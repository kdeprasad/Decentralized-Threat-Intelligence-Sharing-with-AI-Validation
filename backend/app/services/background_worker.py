"""
Background worker — automatically fetches new Google Form responses,
stores them in PostgreSQL, and runs AI validation on each new submission.

The worker runs as an asyncio background task inside the FastAPI process.
It polls Google Sheets every POLL_INTERVAL_SECONDS (configured in .env).
"""

import asyncio
import hashlib
import json

from app.config import settings
from app.database.db import async_session
from app.models.threat_model import ThreatSubmissionCreate
from app.services import sheets_service, threat_service, validation_service
from app.utils.logger import get_logger

logger = get_logger("background_worker")

# Handle to the running task so we can cancel it on shutdown
_worker_task: asyncio.Task | None = None


def _row_hash(row: dict) -> str:
    """
    Create a deterministic SHA-256 hash of a sheet row for deduplication.

    Uses all relevant fields so that two identical form responses produce
    the same hash, but any change results in a different hash.
    """
    canonical = json.dumps(row, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


async def _process_single_row(row: dict) -> None:
    """
    Process one Google Sheet row:
        1. Compute a hash for deduplication
        2. Skip if already stored
        3. Create a ThreatSubmission record
        4. Run AI validation and store the result
    """
    row_hash = _row_hash(row)

    async with async_session() as db:
        try:
            # ── Deduplication check ──────────────────────────
            already_exists = await threat_service.submission_exists_by_hash(db, row_hash)
            if already_exists:
                return  # silently skip duplicates

            # ── Create submission ────────────────────────────
            data = ThreatSubmissionCreate(
                ip_address=row.get("IP Address") or None,
                domain=row.get("Domain") or None,
                malware_hash=row.get("Malware Hash") or None,
                threat_type=row.get("Threat Type", "unknown"),
                description=row.get("Description") or None,
            )
            submission = await threat_service.create_threat(db, data, source_row_hash=row_hash)
            logger.info(
                "[NEW] Stored submission id=%d  type=%s  hash=%s",
                submission.id,
                submission.threat_type,
                row_hash[:12],
            )

            # ── Auto-validate ────────────────────────────────
            result = await validation_service.validate_threat(db, submission.id)
            if result:
                logger.info(
                    "[VALIDATED] submission id=%d  confidence=%.4f  is_valid=%s",
                    submission.id,
                    result.confidence_score,
                    bool(result.is_valid),
                )

            await db.commit()

        except Exception:
            await db.rollback()
            logger.exception("Error processing row hash=%s", row_hash[:12])


async def poll_once() -> int:
    """
    Run a single poll cycle:
        1. Fetch all rows from Google Sheets
        2. Process each row (dedup → store → validate)

    Returns the number of *new* submissions created.
    """
    logger.info("Polling Google Sheets for new form responses…")
    rows = sheets_service.fetch_form_responses()
    if not rows:
        logger.info("No rows returned from Google Sheets.")
        return 0

    new_count = 0
    for row in rows:
        row_hash = _row_hash(row)
        # Quick pre-check before opening a session
        async with async_session() as db:
            exists = await threat_service.submission_exists_by_hash(db, row_hash)
        if exists:
            continue

        await _process_single_row(row)
        new_count += 1

    logger.info(
        "Poll complete — %d new submission(s) out of %d total row(s).",
        new_count,
        len(rows),
    )
    return new_count


async def _run_loop() -> None:
    """Infinite loop that calls poll_once() every POLL_INTERVAL_SECONDS."""
    interval = settings.POLL_INTERVAL_SECONDS
    logger.info(
        "Background worker started — polling every %d seconds.", interval
    )
    while True:
        try:
            await poll_once()
        except Exception:
            logger.exception("Unhandled error in background poll cycle.")
        await asyncio.sleep(interval)


def start(loop: asyncio.AbstractEventLoop | None = None) -> asyncio.Task:
    """
    Schedule the background polling loop as an asyncio Task.

    Call this from the FastAPI lifespan *after* the event loop is running.
    """
    global _worker_task
    _worker_task = asyncio.create_task(_run_loop())
    logger.info("Background worker task created.")
    return _worker_task


def stop() -> None:
    """Cancel the background polling task (called on shutdown)."""
    global _worker_task
    if _worker_task and not _worker_task.done():
        _worker_task.cancel()
        logger.info("Background worker task cancelled.")
    _worker_task = None
