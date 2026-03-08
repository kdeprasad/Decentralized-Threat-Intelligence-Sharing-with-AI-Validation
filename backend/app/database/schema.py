"""
SQLAlchemy ORM table definitions.

Tables:
    threat_submissions  – raw threat indicator submissions
    validation_results  – AI validation outcomes linked to submissions
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class ThreatSubmissionORM(Base):
    """Stores each threat indicator submitted via Google Forms."""

    __tablename__ = "threat_submissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String(45), nullable=True)       # IPv4 or IPv6
    domain = Column(String(255), nullable=True)
    malware_hash = Column(String(128), nullable=True)     # MD5/SHA-256
    threat_type = Column(String(100), nullable=False)     # e.g. phishing, malware
    description = Column(Text, nullable=True)
    submission_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    source_row_hash = Column(String(64), nullable=True, unique=True, index=True)  # SHA-256 dedup hash

    # Relationship
    validation = relationship(
        "ValidationResultORM",
        back_populates="submission",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ThreatSubmission id={self.id} type={self.threat_type}>"


class ValidationResultORM(Base):
    """Stores the AI validation result for a threat submission."""

    __tablename__ = "validation_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    submission_id = Column(
        Integer,
        ForeignKey("threat_submissions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    confidence_score = Column(Float, nullable=False)
    is_valid = Column(Integer, default=0)  # 1 = valid, 0 = invalid
    validated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    submission = relationship("ThreatSubmissionORM", back_populates="validation")

    def __repr__(self) -> str:
        return (
            f"<ValidationResult submission_id={self.submission_id} "
            f"confidence={self.confidence_score}>"
        )
