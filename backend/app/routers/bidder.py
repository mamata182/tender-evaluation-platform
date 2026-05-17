from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.db_models import Bidder, Tender, Criterion
from app.models.schemas import BidderResponse
from app.services.document_processor import process_document, save_uploaded_file
from app.services.info_extractor import extract_bidder_info

router = APIRouter(prefix="/api/bidder", tags=["Bidder"])


@router.post("/upload", response_model=BidderResponse)
async def upload_bidder(
    files: List[UploadFile] = File(...),
    bidder_name: str = Form(...),
    tender_id: int = Form(...),
    db: Session = Depends(get_db)
):
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(404, "Tender not found")
    if tender.status != "processed":
        raise HTTPException(400, "Tender not yet processed")

    criteria = db.query(Criterion).filter(
        Criterion.tender_id == tender_id
    ).all()

    criteria_list = [
        {
            "id": c.id,
            "criterion_text": c.criterion_text,
            "field_name": c.field_name,
            "operator": c.operator,
            "expected_value": c.expected_value,
            "category": c.category
        }
        for c in criteria
    ]

    document_paths = []
    all_text = []

    for file in files:
        content = await file.read()
        file_path = save_uploaded_file(
            content, file.filename,
            f"bidders/{bidder_name.replace(' ', '_')}"
        )
        document_paths.append(file_path)

        doc_result = process_document(file_path)
        if doc_result["text"]:
            all_text.append(
                f"[Document: {file.filename}]\n{doc_result['text']}"
            )

    combined_text = "\n\n---\n\n".join(all_text)

    if not combined_text:
        raise HTTPException(422, "Could not extract text from documents")

    bidder = Bidder(
        name=bidder_name,
        documents=document_paths,
        raw_text=combined_text,
        status="processing"
    )
    db.add(bidder)
    db.commit()
    db.refresh(bidder)

    try:
        extracted_data = extract_bidder_info(
            combined_text, criteria_list, bidder_name
        )
        bidder.extracted_data = extracted_data
        bidder.status = "processed"
        db.commit()
        db.refresh(bidder)

    except Exception as e:
        bidder.status = "error"
        db.commit()
        raise HTTPException(500, f"Processing failed: {str(e)}")

    return bidder


@router.get("/{bidder_id}", response_model=BidderResponse)
async def get_bidder(bidder_id: int, db: Session = Depends(get_db)):
    bidder = db.query(Bidder).filter(Bidder.id == bidder_id).first()
    if not bidder:
        raise HTTPException(404, "Bidder not found")
    return bidder


@router.get("/", response_model=List[BidderResponse])
async def list_bidders(db: Session = Depends(get_db)):
    return db.query(Bidder).order_by(Bidder.created_at.desc()).all()