"""
API routes for threat submissions.

    GET  /threats          → list all validated threats
    GET  /threats/all      → list all threats (validated + unvalidated)
    GET  /threats/{id}     → get a single threat by ID
    POST /threats          → create a new threat submission
    POST /threats/fetch    → import submissions from Google Sheets
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.models.threat_model import ThreatSubmissionCreate, ThreatSubmissionResponse
from app.services import threat_service, sheets_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get(
    "",
    response_model=list[ThreatSubmissionResponse],
    summary="Get validated threats",
)
async def list_validated_threats(db: AsyncSession = Depends(get_db)):
    """Return only threats that passed AI validation."""
    threats = await threat_service.get_all_validated_threats(db)
    return threats


@router.get(
    "/all",
    response_model=list[ThreatSubmissionResponse],
    summary="Get all threats",
)
async def list_all_threats(db: AsyncSession = Depends(get_db)):
    """Return every stored threat (validated and unvalidated)."""
    threats = await threat_service.get_all_threats(db)
    return threats


@router.get(
    "/{submission_id}",
    response_model=ThreatSubmissionResponse,
    summary="Get threat by ID",
)
async def get_threat(submission_id: int, db: AsyncSession = Depends(get_db)):
    """Return a single threat submission by its ID."""
    threat = await threat_service.get_threat_by_id(db, submission_id)
    if threat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Threat submission {submission_id} not found.",
        )
    return threat


@router.post(
    "",
    response_model=ThreatSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a threat submission",
)
async def create_threat(
    payload: ThreatSubmissionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Manually create a new threat submission."""
    threat = await threat_service.create_threat(db, payload)
    return threat


@router.post(
    "/fetch",
    response_model=list[ThreatSubmissionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Import threats from Google Sheets",
)
async def fetch_from_sheets(db: AsyncSession = Depends(get_db)):
    """
    Fetch the latest responses from the linked Google Sheet and store them
    as new threat submissions.
    """
    records = sheets_service.fetch_form_responses()
    if not records:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No records returned from Google Sheets (check credentials and sheet config).",
        )

    created = []
    for row in records:
        data = ThreatSubmissionCreate(
            ip_address=row.get("IP Address") or None,
            domain=row.get("Domain") or None,
            malware_hash=row.get("Malware Hash") or None,
            threat_type=row.get("Threat Type", "unknown"),
            description=row.get("Description") or None,
        )
        threat = await threat_service.create_threat(db, data)
        created.append(threat)

    logger.info("Imported %d submissions from Google Sheets.", len(created))
    return created
