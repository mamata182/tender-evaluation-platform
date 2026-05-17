from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.database import get_db
from app.models.db_models import (
    Tender, Criterion, Bidder, Evaluation, CriterionEvaluation
)
from app.services.evaluation_engine import evaluate_bidder

router = APIRouter(prefix="/api/evaluation", tags=["Evaluation"])


class EvaluationRequest(BaseModel):
    tender_id: int
    bidder_ids: List[int]


@router.post("/evaluate")
async def run_evaluation(
    request: EvaluationRequest,
    db: Session = Depends(get_db)
):
    tender_id = request.tender_id
    bidder_ids = request.bidder_ids

    print(f"Starting evaluation: tender={tender_id}, bidders={bidder_ids}")

    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(404, "Tender not found")

    criteria = db.query(Criterion).filter(
        Criterion.tender_id == tender_id
    ).all()

    if not criteria:
        raise HTTPException(400, "No criteria found for this tender")

    print(f"Found {len(criteria)} criteria")

    criteria_list = [
        {
            "id": c.id,
            "criterion_text": c.criterion_text,
            "category": c.category,
            "is_mandatory": c.is_mandatory,
            "field_name": c.field_name,
            "operator": c.operator,
            "expected_value": c.expected_value,
            "unit": c.unit
        }
        for c in criteria
    ]

    results = []

    for bidder_id in bidder_ids:
        bidder = db.query(Bidder).filter(Bidder.id == bidder_id).first()

        if not bidder:
            print(f"Bidder {bidder_id} not found, skipping")
            continue

        if not bidder.extracted_data:
            print(f"Bidder {bidder_id} has no extracted data, skipping")
            continue

        print(f"Evaluating bidder {bidder_id}: {bidder.name}")

        eval_result = evaluate_bidder(
            criteria=criteria_list,
            bidder_extraction=bidder.extracted_data,
            bidder_name=bidder.name
        )

        print(f"  Result: {eval_result['overall_status']}")
        print(f"  Met: {eval_result['criteria_met']}, Not met: {eval_result['criteria_not_met']}, Uncertain: {eval_result['criteria_uncertain']}")

        evaluation = Evaluation(
            tender_id=tender_id,
            bidder_id=bidder_id,
            overall_status=eval_result["overall_status"],
            overall_confidence=eval_result["overall_confidence"],
            summary=eval_result["summary"],
            criteria_met=eval_result["criteria_met"],
            criteria_not_met=eval_result["criteria_not_met"],
            criteria_uncertain=eval_result["criteria_uncertain"],
            total_criteria=eval_result["total_criteria"]
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)

        for ce_data in eval_result["criterion_evaluations"]:
            ce = CriterionEvaluation(
                evaluation_id=evaluation.id,
                criterion_id=ce_data.get("criterion_id"),
                status=ce_data["status"],
                confidence=ce_data["confidence"],
                extracted_value=ce_data.get("extracted_value", ""),
                source_text=ce_data.get("source_text", ""),
                reasoning=ce_data.get("reasoning", ""),
                evidence=ce_data.get("evidence", "")
            )
            db.add(ce)

        db.commit()

        eval_result["evaluation_id"] = evaluation.id
        eval_result["bidder_id"] = bidder_id
        results.append(eval_result)

    print(f"Evaluation complete: {len(results)} bidders evaluated")

    return {
        "tender_id": tender_id,
        "tender_title": tender.title,
        "total_evaluated": len(results),
        "results": results
    }


@router.get("/results/{tender_id}")
async def get_results(tender_id: int, db: Session = Depends(get_db)):
    evaluations = db.query(Evaluation).filter(
        Evaluation.tender_id == tender_id
    ).all()

    results = []
    for evaluation in evaluations:
        bidder = db.query(Bidder).filter(
            Bidder.id == evaluation.bidder_id
        ).first()

        ce_list = db.query(CriterionEvaluation).filter(
            CriterionEvaluation.evaluation_id == evaluation.id
        ).all()

        ce_data = []
        for ce in ce_list:
            criterion = db.query(Criterion).filter(
                Criterion.id == ce.criterion_id
            ).first()
            ce_data.append({
                "criterion_text": criterion.criterion_text if criterion else "",
                "category": criterion.category if criterion else "",
                "is_mandatory": criterion.is_mandatory if criterion else True,
                "status": ce.status,
                "confidence": ce.confidence,
                "extracted_value": ce.extracted_value,
                "source_text": ce.source_text,
                "reasoning": ce.reasoning
            })

        results.append({
            "evaluation_id": evaluation.id,
            "bidder_id": evaluation.bidder_id,
            "bidder_name": bidder.name if bidder else "Unknown",
            "overall_status": evaluation.overall_status,
            "overall_confidence": evaluation.overall_confidence,
            "summary": evaluation.summary,
            "criteria_met": evaluation.criteria_met,
            "criteria_not_met": evaluation.criteria_not_met,
            "criteria_uncertain": evaluation.criteria_uncertain,
            "total_criteria": evaluation.total_criteria,
            "criterion_evaluations": ce_data
        })

    return {"tender_id": tender_id, "evaluations": results}