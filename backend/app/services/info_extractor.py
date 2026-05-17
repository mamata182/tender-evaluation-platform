import json
from app.services.llm_service import call_llm_json

SYSTEM_PROMPT = """You extract information from bidder documents for Indian government tenders.

You will receive:
1. Text from bidder documents
2. List of criteria fields to check

For each field provide:
- field_name: The criterion field
- found: true/false
- extracted_value: The actual value found
- source_text: Exact text from document
- confidence: 0.0-1.0
- notes: Any observations

Be honest. If unclear, set confidence low.
Normalize values (Rs. 5,00,00,000 = "5 crore").

Return JSON with key "extracted_fields"."""


USER_PROMPT = """CRITERIA TO CHECK:
{criteria_fields}

BIDDER DOCUMENTS:
---
{bidder_text}
---

Return JSON with "extracted_fields"."""


def extract_bidder_info(bidder_text, criteria, bidder_name=""):
    criteria_fields = []
    for c in criteria:
        criteria_fields.append({
            "field_name": c.get("field_name", ""),
            "criterion_text": c.get("criterion_text", ""),
            "expected_value": c.get("expected_value", ""),
            "operator": c.get("operator", "")
        })

    max_chars = 60000
    if len(bidder_text) > max_chars:
        bidder_text = bidder_text[:max_chars]

    try:
        response = call_llm_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=USER_PROMPT.format(
                criteria_fields=json.dumps(criteria_fields, indent=2),
                bidder_text=bidder_text
            ),
            temperature=0.1
        )

        extracted = response.get("extracted_fields", [])

        result = {}
        for field in extracted:
            field_name = field.get("field_name", "")
            if field_name:
                result[field_name] = {
                    "found": field.get("found", False),
                    "extracted_value": field.get("extracted_value", ""),
                    "source_text": field.get("source_text", ""),
                    "confidence": field.get("confidence", 0.0),
                    "notes": field.get("notes", "")
                }

        return result

    except Exception as e:
        print(f"Bidder extraction failed: {e}")
        return {}


def normalize_financial_value(value_str):
    if not value_str:
        return None

    value_str = str(value_str).lower().strip()

    for prefix in ['rs.', 'rs', '₹', 'inr', 'rupees']:
        value_str = value_str.replace(prefix, '')

    value_str = value_str.replace(',', '').strip()

    try:
        if 'crore' in value_str or 'cr' in value_str:
            num = float(value_str.replace('crore', '').replace('cr', '').strip())
            return num * 10000000
        elif 'lakh' in value_str or 'lac' in value_str:
            num = float(value_str.replace('lakh', '').replace('lac', '').strip())
            return num * 100000
        else:
            return float(value_str)
    except ValueError:
        return None