"""
Threat service — CRUD operations for threat submissions in PostgreSQL.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database.schema import ThreatSubmissionORM, ValidationResultORM
from app.models.threat_model import ThreatSubmissionCreate
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def create_threat(
    db: AsyncSession,
    data: ThreatSubmissionCreate,
) -> ThreatSubmissionORM:
    """Insert a new threat submission and return the ORM instance."""
    submission = ThreatSubmissionORM(
        ip_address=data.ip_address,
        domain=data.domain,
        malware_hash=data.malware_hash,
        threat_type=data.threat_type,
        description=data.description,
        submission_time=datetime.utcnow(),
    )
    db.add(submission)
    await db.flush()          # populate submission.id without committing
    await db.refresh(submission)
    logger.info("Created threat submission id=%d", submission.id)
    return submission


async def get_threat_by_id(
    db: AsyncSession,
    submission_id: int,
) -> Optional[ThreatSubmissionORM]:
    """Return a single threat submission by primary key, or None."""
    result = await db.execute(
        select(ThreatSubmissionORM)
        .options(joinedload(ThreatSubmissionORM.validation))
        .where(ThreatSubmissionORM.id == submission_id)
    )
    return result.scalars().first()


async def get_all_validated_threats(
    db: AsyncSession,
) -> list[ThreatSubmissionORM]:
    """
    Return all threat submissions that have been validated
    (i.e. have a linked ValidationResult with is_valid = 1).
    """
    result = await db.execute(
        select(ThreatSubmissionORM)
        .join(ValidationResultORM)
        .options(joinedload(ThreatSubmissionORM.validation))
        .where(ValidationResultORM.is_valid == 1)
        .order_by(ThreatSubmissionORM.submission_time.desc())
    )
    return list(result.scalars().unique().all())


async def get_all_threats(
    db: AsyncSession,
) -> list[ThreatSubmissionORM]:
    """Return every threat submission (validated or not), newest first."""
    result = await db.execute(
        select(ThreatSubmissionORM)
        .options(joinedload(ThreatSubmissionORM.validation))
        .order_by(ThreatSubmissionORM.submission_time.desc())
    )
    return list(result.scalars().unique().all())
