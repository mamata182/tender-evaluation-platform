from app.database import SessionLocal
from app.models.db_models import Tender, Criterion
from app.services.criteria_extractor import extract_criteria_from_text

db = SessionLocal()

tender = db.query(Tender).get(1)

if not tender or not tender.extracted_text:
    print("❌ No tender or text found")
    exit()

print(f"Tender: {tender.title}")
print(f"Text length: {len(tender.extracted_text)} chars")
print("\n🔄 Extracting criteria...\n")

try:
    criteria_data = extract_criteria_from_text(tender.extracted_text)
    
    if not criteria_data:
        print("❌ No criteria returned from LLM")
    else:
        print(f"✅ Got {len(criteria_data)} criteria\n")
        
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
            print(f"  {c_data['category']}: {c_data['criterion_text'][:60]}...")
        
        db.commit()
        print(f"\n✅ Saved {len(criteria_data)} criteria to database!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

db.close()