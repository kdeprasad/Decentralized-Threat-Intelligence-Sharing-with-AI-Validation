"""
API routes for AI validation.

    POST /validate  → run AI validation on an existing threat submission
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.models.threat_model import ValidationRequest, ValidationResponse
from app.services import validation_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "",
    response_model=ValidationResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate a threat submission",
)
async def validate_submission(
    payload: ValidationRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Run AI validation on the threat submission identified by `submission_id`.

    Returns the confidence score and whether the submission is considered valid.
    """
    result = await validation_service.validate_threat(db, payload.submission_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Threat submission {payload.submission_id} not found.",
        )

    return ValidationResponse(
        submission_id=result.submission_id,
        confidence_score=result.confidence_score,
        is_valid=bool(result.is_valid),
        validated_at=result.validated_at,
    )
