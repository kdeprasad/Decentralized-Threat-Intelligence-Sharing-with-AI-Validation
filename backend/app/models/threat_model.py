"""
Pydantic models (schemas) for request/response validation.

These are separate from the SQLAlchemy ORM models in database/schema.py.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Request / Input schemas ─────────────────────────────

class ThreatSubmissionCreate(BaseModel):
    """Payload used when creating a new threat submission."""

    ip_address: Optional[str] = Field(None, max_length=45, examples=["192.168.1.100"])
    domain: Optional[str] = Field(None, max_length=255, examples=["malicious-site.com"])
    malware_hash: Optional[str] = Field(None, max_length=128, examples=["d41d8cd98f00b204e9800998ecf8427e"])
    threat_type: str = Field(..., max_length=100, examples=["phishing"])
    description: Optional[str] = Field(None, examples=["Phishing email targeting employees"])


# ── Response / Output schemas ───────────────────────────

class ThreatSubmissionResponse(BaseModel):
    """Returned when reading a stored threat submission."""

    id: int
    ip_address: Optional[str] = None
    domain: Optional[str] = None
    malware_hash: Optional[str] = None
    threat_type: str
    description: Optional[str] = None
    submission_time: datetime

    model_config = {"from_attributes": True}


class ValidationRequest(BaseModel):
    """Payload sent to the /validate endpoint."""

    submission_id: int = Field(..., description="ID of the threat submission to validate")


class ValidationResponse(BaseModel):
    """Returned after running AI validation on a submission."""

    submission_id: int
    confidence_score: float
    is_valid: bool
    validated_at: datetime

    model_config = {"from_attributes": True}
