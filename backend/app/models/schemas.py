from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class CriterionSchema(BaseModel):
    id: Optional[int] = None
    criterion_text: str
    category: str
    is_mandatory: bool = True
    field_name: Optional[str] = None
    operator: Optional[str] = None
    expected_value: Optional[str] = None
    unit: Optional[str] = None
    extraction_confidence: float = 1.0

    class Config:
        from_attributes = True


class TenderResponse(BaseModel):
    id: int
    title: str
    original_filename: Optional[str] = None
    status: str
    criteria: List[CriterionSchema] = []
    created_at: datetime

    class Config:
        from_attributes = True


class BidderResponse(BaseModel):
    id: int
    name: str
    documents: Optional[List[str]] = None
    extracted_data: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class EvaluationResponse(BaseModel):
    id: int
    tender_id: int
    bidder_id: int
    bidder_name: str
    overall_status: str
    overall_confidence: float
    summary: str
    criteria_met: int
    criteria_not_met: int
    criteria_uncertain: int
    total_criteria: int
    created_at: datetime

    class Config:
        from_attributes = True