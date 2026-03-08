"""
Validation service — runs AI validation on a threat submission.

Phase 2: returns a *placeholder* confidence score (random 0.5-1.0).
Phase 3: will load a trained scikit-learn model from ml/model.pkl.
"""

import random
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.schema import ValidationResultORM
from app.services.threat_service import get_threat_by_id
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Confidence threshold — scores above this are considered "valid"
CONFIDENCE_THRESHOLD = 0.7


async def validate_threat(
    db: AsyncSession,
    submission_id: int,
) -> ValidationResultORM | None:
    """
    Validate a threat submission by its ID.

    Currently uses a placeholder scoring function. In Phase 3 this will be
    replaced with a real ML model prediction.

    Returns:
        A ValidationResultORM instance persisted to the database,
        or None if the submission was not found.
    """
    submission = await get_threat_by_id(db, submission_id)
    if submission is None:
        logger.warning("Submission id=%d not found — cannot validate.", submission_id)
        return None

    # ── Placeholder AI scoring ──────────────────────────
    confidence = _placeholder_confidence_score(submission)

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
        "Validated submission id=%d → confidence=%.4f, is_valid=%s",
        submission_id,
        confidence,
        bool(is_valid),
    )
    return validation


def _placeholder_confidence_score(submission) -> float:
    """
    Placeholder scoring logic.

    Returns a pseudo-random confidence score between 0.5 and 1.0.
    Slightly biases toward higher confidence when more fields are filled in.

    This function will be replaced by a real ML prediction in Phase 3.
    """
    filled_fields = sum(
        1
        for field in [
            submission.ip_address,
            submission.domain,
            submission.malware_hash,
            submission.description,
        ]
        if field
    )
    # Base confidence + bonus per filled field + small random jitter
    base = 0.5
    field_bonus = filled_fields * 0.05
    jitter = random.uniform(0.0, 0.2)
    return min(base + field_bonus + jitter, 1.0)
