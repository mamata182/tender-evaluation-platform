from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.db_models import Tender, Criterion
from app.models.schemas import TenderResponse, CriterionSchema
from app.services.document_processor import process_document, save_uploaded_file
from app.services.criteria_extractor import extract_criteria_from_text

router = APIRouter(prefix="/api/tender", tags=["Tender"])


@router.post("/upload", response_model=TenderResponse)
async def upload_tender(
    file: UploadFile = File(...),
    title: str = Form("Untitled Tender"),
    db: Session = Depends(get_db)
):
    allowed = ['pdf', 'docx', 'doc', 'png', 'jpg', 'jpeg', 'tiff']
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in allowed:
        raise HTTPException(400, f"Unsupported file type: .{ext}")

    content = await file.read()
    file_path = save_uploaded_file(content, file.filename, "tenders")

    tender = Tender(
        title=title,
        file_path=file_path,
        original_filename=file.filename,
        status="processing"
    )
    db.add(tender)
    db.commit()
    db.refresh(tender)

    try:
        doc_result = process_document(file_path)
        tender.extracted_text = doc_result["text"]

        if not doc_result["text"]:
            tender.status = "error"
            db.commit()
            raise HTTPException(422, "Could not extract text")

        criteria_data = extract_criteria_from_text(doc_result["text"])

        for c_data in criteria_data:
            criterion = Criterion(
                tender_id=tender.id,
                criterion_text=c_data.get("criterion_text", ""),
                category=c_data.get("category", "technical"),
                is_mandatory=c_data.get("is_mandatory", True),
                field_name=c_data.get("field_name", ""),
                operator=c_data.get("operator", ""),
                expected_value=c_data.get("expected_value", ""),
                unit=c_data.get("unit", ""),
                extraction_confidence=c_data.get("extraction_confidence", 0.9)
            )
            db.add(criterion)

        tender.status = "processed"
        db.commit()
        db.refresh(tender)

    except HTTPException:
        raise
    except Exception as e:
        tender.status = "error"
        db.commit()
        raise HTTPException(500, f"Processing failed: {str(e)}")

    return tender


@router.get("/{tender_id}", response_model=TenderResponse)
async def get_tender(tender_id: int, db: Session = Depends(get_db)):
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(404, "Tender not found")
    return tender


@router.get("/", response_model=List[TenderResponse])
async def list_tenders(db: Session = Depends(get_db)):
    return db.query(Tender).order_by(Tender.created_at.desc()).all()


@router.delete("/{tender_id}")
async def delete_tender(tender_id: int, db: Session = Depends(get_db)):
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(404, "Tender not found")
    db.delete(tender)
    db.commit()
    return {"message": "Tender deleted"}