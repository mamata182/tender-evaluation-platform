from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, Field
from datetime import datetime

from app.database import get_db
from app.models.db_models import (
    Tender,
    Criterion,
    Bidder,
    Evaluation,
    CriterionEvaluation
)
from app.services.evaluation_engine import evaluate_bidder

router = APIRouter(prefix="/api/evaluation", tags=["Evaluation"])


class EvaluationRequest(BaseModel):
    tender_id: int
    bidder_ids: List[int] = Field(default_factory=list)


@router.post("/evaluate")
async def run_evaluation(
    request: EvaluationRequest,
    db: Session = Depends(get_db)
):
    tender_id = request.tender_id
    bidder_ids = request.bidder_ids

    print("=" * 80)
    print("Starting evaluation")
    print(f"Tender ID: {tender_id}")
    print(f"Bidder IDs received: {bidder_ids}")
    print("=" * 80)

    # Get tender
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    # Get criteria
    criteria = db.query(Criterion).filter(
        Criterion.tender_id == tender_id
    ).all()

    if not criteria:
        raise HTTPException(
            status_code=400,
            detail="No criteria found for this tender"
        )

    print(f"Criteria found: {len(criteria)}")

    # If frontend accidentally sends empty bidder_ids,
    # evaluate all uploaded bidders instead of returning 0 results.
    if not bidder_ids:
        bidders = db.query(Bidder).all()
        bidder_ids = [b.id for b in bidders]
        print(f"No bidder IDs received. Using all bidders: {bidder_ids}")

    if not bidder_ids:
        raise HTTPException(
            status_code=400,
            detail="No bidders found. Please upload bidders before evaluation."
        )

    # Delete old evaluations for this tender to avoid duplicate saved results
    old_evaluations = db.query(Evaluation).filter(
        Evaluation.tender_id == tender_id
    ).all()

    old_eval_ids = [e.id for e in old_evaluations]

    if old_eval_ids:
        db.query(CriterionEvaluation).filter(
            CriterionEvaluation.evaluation_id.in_(old_eval_ids)
        ).delete(synchronize_session=False)

        db.query(Evaluation).filter(
            Evaluation.tender_id == tender_id
        ).delete(synchronize_session=False)

        db.commit()
        print(f"Deleted old evaluations: {len(old_eval_ids)}")

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
            print(f"Bidder {bidder_id} not found. Skipping.")
            continue

        print("-" * 80)
        print(f"Evaluating bidder {bidder.id}: {bidder.name}")
        print(f"Bidder status: {bidder.status}")
        print(f"Has extracted data: {bool(bidder.extracted_data)}")

        # IMPORTANT:
        # Do NOT skip bidder even if extracted_data is empty.
        # If extraction failed, evaluation engine marks criteria as uncertain.
        bidder_extraction = bidder.extracted_data or {}

        eval_result = evaluate_bidder(
            criteria=criteria_list,
            bidder_extraction=bidder_extraction,
            bidder_name=bidder.name
        )

        print(f"Result: {eval_result['overall_status']}")
        print(
            f"Met: {eval_result['criteria_met']}, "
            f"Not met: {eval_result['criteria_not_met']}, "
            f"Uncertain: {eval_result['criteria_uncertain']}"
        )

        # Save evaluation summary
        evaluation = Evaluation(
            tender_id=tender_id,
            bidder_id=bidder.id,
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

        # Save criterion-level evaluation details
        for ce_data in eval_result["criterion_evaluations"]:
            ce = CriterionEvaluation(
                evaluation_id=evaluation.id,
                criterion_id=ce_data.get("criterion_id"),
                status=ce_data.get("status", "uncertain"),
                confidence=ce_data.get("confidence", 0.0),
                extracted_value=ce_data.get("extracted_value", ""),
                source_text=ce_data.get("source_text", ""),
                reasoning=ce_data.get("reasoning", ""),
                evidence=ce_data.get("evidence", "")
            )
            db.add(ce)

        db.commit()

        eval_result["evaluation_id"] = evaluation.id
        eval_result["bidder_id"] = bidder.id
        results.append(eval_result)

    print("=" * 80)
    print(f"Evaluation complete. Total evaluated: {len(results)}")
    print("=" * 80)

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
                "reasoning": ce.reasoning,
                "evidence": ce.evidence
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

    return {
        "tender_id": tender_id,
        "evaluations": results
    }


@router.get("/debug/{tender_id}")
async def debug_evaluation_data(tender_id: int, db: Session = Depends(get_db)):
    """
    Debug endpoint to check tender, criteria, bidders, and evaluations.
    Useful when deployed output shows 0 results.
    """

    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    criteria = db.query(Criterion).filter(Criterion.tender_id == tender_id).all()
    bidders = db.query(Bidder).all()
    evaluations = db.query(Evaluation).filter(Evaluation.tender_id == tender_id).all()

    return {
        "tender_exists": bool(tender),
        "tender_id": tender_id,
        "tender_title": tender.title if tender else None,
        "criteria_count": len(criteria),
        "bidders_count": len(bidders),
        "bidders": [
            {
                "id": b.id,
                "name": b.name,
                "status": b.status,
                "has_extracted_data": bool(b.extracted_data),
                "extracted_fields": list(b.extracted_data.keys()) if b.extracted_data else []
            }
            for b in bidders
        ],
        "evaluations_count": len(evaluations)
    }


@router.get("/report/{tender_id}/download")
async def download_evaluation_report(tender_id: int, db: Session = Depends(get_db)):
    """
    Download consolidated evaluation report as a text file.
    """

    tender = db.query(Tender).filter(Tender.id == tender_id).first()

    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    evaluations = db.query(Evaluation).filter(
        Evaluation.tender_id == tender_id
    ).all()

    if not evaluations:
        raise HTTPException(
            status_code=404,
            detail="No evaluations found for this tender. Please run evaluation first."
        )

    report_lines = []

    report_lines.append("=" * 95)
    report_lines.append("AI-BASED TENDER EVALUATION & ELIGIBILITY ANALYSIS REPORT")
    report_lines.append("=" * 95)
    report_lines.append("")
    report_lines.append(f"Tender ID      : {tender.id}")
    report_lines.append(f"Tender Title   : {tender.title}")
    report_lines.append(f"Generated On   : {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report_lines.append("")
    report_lines.append("-" * 95)

    total_bidders = len(evaluations)
    eligible_count = sum(1 for e in evaluations if e.overall_status == "eligible")
    not_eligible_count = sum(1 for e in evaluations if e.overall_status == "not_eligible")
    review_count = sum(1 for e in evaluations if e.overall_status == "needs_review")

    report_lines.append("SUMMARY")
    report_lines.append("-" * 95)
    report_lines.append(f"Total Bidders Evaluated : {total_bidders}")
    report_lines.append(f"Eligible                : {eligible_count}")
    report_lines.append(f"Not Eligible            : {not_eligible_count}")
    report_lines.append(f"Needs Manual Review     : {review_count}")
    report_lines.append("")
    report_lines.append("=" * 95)
    report_lines.append("DETAILED BIDDER-WISE EVALUATION")
    report_lines.append("=" * 95)
    report_lines.append("")

    for evaluation in evaluations:
        bidder = db.query(Bidder).filter(Bidder.id == evaluation.bidder_id).first()
        bidder_name = bidder.name if bidder else "Unknown Bidder"

        report_lines.append("-" * 95)
        report_lines.append(f"BIDDER NAME      : {bidder_name}")
        report_lines.append(f"OVERALL STATUS   : {evaluation.overall_status.upper().replace('_', ' ')}")
        report_lines.append(f"CONFIDENCE       : {round((evaluation.overall_confidence or 0) * 100, 2)}%")
        report_lines.append(f"CRITERIA MET     : {evaluation.criteria_met}/{evaluation.total_criteria}")
        report_lines.append(f"NOT MET          : {evaluation.criteria_not_met}")
        report_lines.append(f"UNCERTAIN        : {evaluation.criteria_uncertain}")
        report_lines.append("")
        report_lines.append("SUMMARY:")
        report_lines.append(evaluation.summary or "No summary available.")
        report_lines.append("")
        report_lines.append("CRITERION LEVEL DETAILS:")
        report_lines.append("-" * 95)

        criterion_evals = db.query(CriterionEvaluation).filter(
            CriterionEvaluation.evaluation_id == evaluation.id
        ).all()

        for index, ce in enumerate(criterion_evals, start=1):
            criterion = db.query(Criterion).filter(Criterion.id == ce.criterion_id).first()

            criterion_text = criterion.criterion_text if criterion else "Unknown criterion"
            category = criterion.category if criterion else "unknown"
            mandatory = criterion.is_mandatory if criterion else True

            report_lines.append("")
            report_lines.append(f"{index}. Criterion")
            report_lines.append(f"   Text            : {criterion_text}")
            report_lines.append(f"   Category        : {category}")
            report_lines.append(f"   Mandatory       : {'Yes' if mandatory else 'No'}")
            report_lines.append(f"   Status          : {ce.status}")
            report_lines.append(f"   Confidence      : {round((ce.confidence or 0) * 100, 2)}%")
            report_lines.append(f"   Extracted Value : {ce.extracted_value or 'N/A'}")
            report_lines.append(f"   Reasoning       : {ce.reasoning or 'N/A'}")

            if ce.source_text:
                report_lines.append(f"   Source Text     : {ce.source_text[:300]}")

            if ce.evidence:
                report_lines.append(f"   Evidence        : {ce.evidence[:300]}")

        report_lines.append("")
        report_lines.append("=" * 95)
        report_lines.append("")

    report_lines.append("")
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 95)

    report_content = "\n".join(report_lines)

    filename = f"tender_evaluation_report_{tender_id}.txt"

    return Response(
        content=report_content,
        media_type="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )