"""
Validation service — runs AI validation on a threat submission.

Phase 3: loads a trained scikit-learn model from ml/model.pkl and uses
feature engineering to score incoming submissions. Falls back to a
heuristic placeholder if the model file is not available.
"""

import os
import pickle
import random
from datetime import datetime
from pathlib import Path

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.schema import ValidationResultORM
from app.services.threat_service import get_threat_by_id
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Confidence threshold — scores above this are considered "valid"
CONFIDENCE_THRESHOLD = 0.7

# ── ML model loading ───────────────────────────────────
_model = None
_model_loaded = False


def _load_model():
    """
    Attempt to load the trained ML model from disk.
    Called once at first prediction; result is cached in _model.
    """
    global _model, _model_loaded
    _model_loaded = True

    model_path = Path(settings.ML_MODEL_PATH)
    if not model_path.exists():
        logger.warning(
            "ML model not found at %s — falling back to placeholder scoring.",
            model_path,
        )
        _model = None
        return

    try:
        with open(model_path, "rb") as f:
            _model = pickle.load(f)
        logger.info("ML model loaded from %s", model_path)
    except Exception as exc:
        logger.exception("Failed to load ML model: %s", exc)
        _model = None


# ── Feature extraction (mirrors ml/feature_engineering.py) ──
# Duplicated here to keep the backend self-contained without importing
# from the ml/ package at runtime.

THREAT_TYPE_MAP = {
    "phishing": 0,
    "malware": 1,
    "ransomware": 2,
    "command_and_control": 3,
    "data_exfiltration": 4,
    "denial_of_service": 5,
    "brute_force": 6,
    "other": 7,
}

SUSPICIOUS_TLDS = {".xyz", ".tk", ".top", ".buzz", ".ru", ".cn", ".cc", ".pw", ".gq", ".ml"}


def _extract_features(submission) -> np.ndarray:
    """
    Extract the same 12-feature vector used during training.

    Returns np.ndarray of shape (1, 12) ready for model.predict_proba().
    """
    ip = submission.ip_address or ""
    dom = submission.domain or ""
    h = submission.malware_hash or ""
    desc = submission.description or ""
    tt = (submission.threat_type or "other").lower()

    has_ip = int(bool(ip.strip()))
    has_domain = int(bool(dom.strip()))
    has_hash = int(bool(h.strip()))
    has_desc = int(bool(desc.strip()))

    features = np.array([[
        has_ip,
        has_domain,
        has_hash,
        has_desc,
        has_ip + has_domain + has_hash + has_desc,   # filled_count
        len(desc),                                     # description_len
        len(desc.split()) if desc.strip() else 0,      # desc_word_count
        len(h.strip()),                                 # hash_len
        len(dom.strip()),                               # domain_len
        dom.count("."),                                  # domain_dot_count
        THREAT_TYPE_MAP.get(tt, 7),                     # threat_type_enc
        int(any(dom.lower().endswith(tld) for tld in SUSPICIOUS_TLDS)),  # is_suspicious_tld
    ]], dtype=np.float64)

    return features


# ── Scoring functions ──────────────────────────────────

def _ml_confidence_score(submission) -> float:
    """
    Use the trained ML model to predict the probability that a submission
    is a valid (legitimate) threat indicator.
    """
    features = _extract_features(submission)
    proba = _model.predict_proba(features)[0]  # [prob_invalid, prob_valid]
    confidence = float(proba[1])  # probability of class 1 (valid)
    return confidence


def _placeholder_confidence_score(submission) -> float:
    """
    Heuristic fallback when no ML model is available.
    Returns a pseudo-random confidence score biased by filled fields.
    """
    filled = sum(
        1 for field in [
            submission.ip_address,
            submission.domain,
            submission.malware_hash,
            submission.description,
        ] if field
    )
    base = 0.5
    bonus = filled * 0.05
    jitter = random.uniform(0.0, 0.2)
    return min(base + bonus + jitter, 1.0)


# ── Main validation entry point ────────────────────────

async def validate_threat(
    db: AsyncSession,
    submission_id: int,
) -> ValidationResultORM | None:
    """
    Validate a threat submission by its ID.

    Uses the trained ML model if available, otherwise falls back to the
    heuristic placeholder.

    Returns:
        A ValidationResultORM instance persisted to the database,
        or None if the submission was not found.
    """
    # Lazy-load the model on first call
    if not _model_loaded:
        _load_model()

    submission = await get_threat_by_id(db, submission_id)
    if submission is None:
        logger.warning("Submission id=%d not found — cannot validate.", submission_id)
        return None

    # ── Score the submission ─────────────────────────────
    if _model is not None:
        confidence = _ml_confidence_score(submission)
        scoring_method = "ml_model"
    else:
        confidence = _placeholder_confidence_score(submission)
        scoring_method = "placeholder"

    is_valid = 1 if confidence >= CONFIDENCE_THRESHOLD else 0

    validation = ValidationResultORM(
        submission_id=submission_id,
        confidence_score=round(confidence, 4),
        is_valid=is_valid,
        validated_at=datetime.utcnow(),
    )
    db.add(validation)
    await db.flush()
    await db.refresh(validation)

    logger.info(
        "Validated submission id=%d → confidence=%.4f, is_valid=%s [%s]",
        submission_id,
        confidence,
        bool(is_valid),
        scoring_method,
    )
    return validation
