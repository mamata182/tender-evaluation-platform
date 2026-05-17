import re
from app.services.llm_service import call_llm_json


SYSTEM_PROMPT = """You are an expert government procurement analyst for Indian tenders.

Extract ALL eligibility criteria from the tender document.

For each criterion provide:
- criterion_text: The exact requirement text
- category: "technical", "financial", or "compliance"
- is_mandatory: true if mandatory, false if optional/desirable
- field_name: Short name like "minimum_turnover", "iso_certification"
- operator: ">=", "<=", "must_have", "at_least"
- expected_value: The threshold value (e.g., "50 crore", "valid", "10")
- unit: "crore", "lakh", "years", "count", "boolean"

Categories:
- TECHNICAL: experience, projects, equipment, manpower, manufacturing
- FINANCIAL: turnover, net worth, bank guarantees, solvency
- COMPLIANCE: GST, ISO, ARAI, CMVR, certifications, registrations

Return JSON: {"criteria": [...]}"""


USER_PROMPT = """Extract all eligibility criteria from this tender:

---
{tender_text}
---

Return JSON with key "criteria" containing list of criterion objects."""


def extract_criteria_from_text(tender_text):
    """Try Groq AI first, fallback to rule-based if it fails."""
    if not tender_text:
        return []

    print(f"📄 Processing tender text: {len(tender_text)} chars")

    # Try AI first
    try:
        response = call_llm_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=USER_PROMPT.format(tender_text=tender_text[:80000]),
            temperature=0.1
        )

        criteria = response.get("criteria", [])

        validated = []
        for c in criteria:
            if c.get("criterion_text"):
                c.setdefault("category", "technical")
                c.setdefault("is_mandatory", True)
                c.setdefault("field_name", "")
                c.setdefault("operator", "")
                c.setdefault("expected_value", "")
                c.setdefault("unit", "")
                c.setdefault("extraction_confidence", 0.9)
                validated.append(c)

        if validated:
            print(f"✅ AI extracted {len(validated)} criteria")
            return validated

    except Exception as e:
        print(f"⚠️ AI failed, using fallback: {e}")

    # Fallback: rule-based extraction
    return fallback_extract(tender_text)


def fallback_extract(text):
    """Rule-based extraction as backup."""
    criteria = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    for line in lines:
        if len(line) < 20:
            continue
        if any(skip in line.lower() for skip in ["section a", "section b", "section c", "section d", "tender for", "tender reference", "============", "------------"]):
            continue

        lower = line.lower()
        added = False

        if "turnover" in lower:
            value = extract_crore(lower)
            criteria.append(make_c(line, "financial", "minimum_turnover", ">=", value, "crore"))
            added = True
        elif "net worth" in lower:
            value = extract_crore(lower)
            criteria.append(make_c(line, "financial", "net_worth", ">=", value, "crore"))
            added = True
        elif "solvency" in lower:
            value = extract_crore(lower)
            criteria.append(make_c(line, "financial", "bank_solvency", ">=", value, "crore"))
            added = True
        elif ("electric bus" in lower or "buses" in lower) and ("supplied" in lower or "experience" in lower or "commission" in lower):
            value = extract_count(lower)
            criteria.append(make_c(line, "technical", "electric_buses_supplied", "at_least", value, "count"))
            added = True
        elif "service center" in lower or "service centre" in lower:
            value = extract_count(lower)
            criteria.append(make_c(line, "technical", "service_centers", "at_least", value, "count"))
            added = True
        elif "warranty" in lower:
            value = extract_years(lower)
            criteria.append(make_c(line, "technical", "battery_warranty", ">=", value, "years"))
            added = True
        elif "engineer" in lower:
            value = extract_count(lower)
            criteria.append(make_c(line, "technical", "qualified_engineers", "at_least", value, "count"))
            added = True
        elif "gst" in lower:
            criteria.append(make_c(line, "compliance", "gst_registration", "must_have", "valid", "boolean"))
            added = True
        elif "iso" in lower:
            criteria.append(make_c(line, "compliance", "iso_certification", "must_have", "valid", "boolean"))
            added = True
        elif "arai" in lower:
            criteria.append(make_c(line, "compliance", "arai_certification", "must_have", "valid", "boolean"))
            added = True
        elif "cmvr" in lower:
            criteria.append(make_c(line, "compliance", "cmvr_compliance", "must_have", "valid", "boolean"))
            added = True
        elif "environmental clearance" in lower:
            criteria.append(make_c(line, "compliance", "environmental_clearance", "must_have", "valid", "boolean"))
            added = True
        elif "registered in india" in lower or "company must be registered" in lower:
            criteria.append(make_c(line, "compliance", "registered_in_india", "must_have", "yes", "boolean"))
            added = True

    print(f"✅ Fallback extracted {len(criteria)} criteria")
    return criteria


def make_c(text, category, field_name, operator, value, unit):
    mandatory = not any(w in text.lower() for w in ["desirable", "optional", "preferred"])
    return {
        "criterion_text": text,
        "category": category,
        "is_mandatory": mandatory,
        "field_name": field_name,
        "operator": operator,
        "expected_value": value,
        "unit": unit,
        "extraction_confidence": 0.85
    }


def extract_crore(text):
    m = re.search(r"(\d+(?:\.\d+)?)\s*crore", text, re.IGNORECASE)
    return f"{m.group(1)} crore" if m else ""


def extract_years(text):
    m = re.search(r"(\d+)[-\s]*year", text, re.IGNORECASE)
    return m.group(1) if m else ""


def extract_count(text):
    patterns = [
        r"at least\s*(\d+)",
        r"minimum\s*(?:of\s*)?(\d+)",
        r"not less than\s*(\d+)",
        r"(\d+)\s+(?:electric buses|buses|engineers|service centers|cities|projects)"
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1)
    return ""