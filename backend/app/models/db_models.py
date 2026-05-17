from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean,
    DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class Tender(Base):
    __tablename__ = "tenders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    original_filename = Column(String(500))
    extracted_text = Column(Text)
    status = Column(String(50), default="uploaded")
    created_at = Column(DateTime, default=datetime.utcnow)

    criteria = relationship(
        "Criterion", back_populates="tender",
        cascade="all, delete-orphan"
    )
    evaluations = relationship(
        "Evaluation", back_populates="tender",
        cascade="all, delete-orphan"
    )


class Criterion(Base):
    __tablename__ = "criteria"

    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(Integer, ForeignKey("tenders.id"), nullable=False)
    criterion_text = Column(Text, nullable=False)
    category = Column(String(50))
    is_mandatory = Column(Boolean, default=True)
    field_name = Column(String(200))
    operator = Column(String(50))
    expected_value = Column(String(500))
    unit = Column(String(100))
    extraction_confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    tender = relationship("Tender", back_populates="criteria")


class Bidder(Base):
    __tablename__ = "bidders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False)
    documents = Column(JSON)
    extracted_data = Column(JSON)
    raw_text = Column(Text)
    status = Column(String(50), default="uploaded")
    created_at = Column(DateTime, default=datetime.utcnow)

    evaluations = relationship(
        "Evaluation", back_populates="bidder",
        cascade="all, delete-orphan"
    )


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(Integer, ForeignKey("tenders.id"), nullable=False)
    bidder_id = Column(Integer, ForeignKey("bidders.id"), nullable=False)
    overall_status = Column(String(50))
    overall_confidence = Column(Float)
    summary = Column(Text)
    criteria_met = Column(Integer, default=0)
    criteria_not_met = Column(Integer, default=0)
    criteria_uncertain = Column(Integer, default=0)
    total_criteria = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    tender = relationship("Tender", back_populates="evaluations")
    bidder = relationship("Bidder", back_populates="evaluations")
    criterion_evaluations = relationship(
        "CriterionEvaluation", back_populates="evaluation",
        cascade="all, delete-orphan"
    )


class CriterionEvaluation(Base):
    __tablename__ = "criterion_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"), nullable=False)
    criterion_id = Column(Integer, ForeignKey("criteria.id"), nullable=False)
    status = Column(String(50))
    confidence = Column(Float)
    extracted_value = Column(String(500))
    source_text = Column(Text)
    reasoning = Column(Text)
    evidence = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    evaluation = relationship("Evaluation", back_populates="criterion_evaluations")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(200), nullable=False)
    entity_type = Column(String(100))
    entity_id = Column(Integer)
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)