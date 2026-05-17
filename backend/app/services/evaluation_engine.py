from app.services.info_extractor import normalize_financial_value
from app.services.llm_service import call_llm_json
import json


def evaluate_bidder(criteria, bidder_extraction, bidder_name=""):
    """Main function to evaluate a bidder against tender criteria."""
    criterion_evaluations = []
    met = 0
    not_met = 0
    uncertain = 0

    for criterion in criteria:
        field_name = criterion.get("field_name", "")
        bidder_data = bidder_extraction.get(field_name, {})

        eval_result = _evaluate_single(criterion, bidder_data)
        criterion_evaluations.append(eval_result)

        if eval_result["status"] == "met":
            met += 1
        elif eval_result["status"] == "not_met":
            not_met += 1
        else:
            uncertain += 1

    overall_status, overall_confidence = _determine_overall(criterion_evaluations)

    summary = _generate_summary(
        bidder_name, overall_status, met, not_met,
        uncertain, len(criteria), criterion_evaluations
    )

    return {
        "bidder_name": bidder_name,
        "overall_status": overall_status,
        "overall_confidence": overall_confidence,
        "summary": summary,
        "criteria_met": met,
        "criteria_not_met": not_met,
        "criteria_uncertain": uncertain,
        "total_criteria": len(criteria),
        "criterion_evaluations": criterion_evaluations
    }


def _evaluate_single(criterion, bidder_data):
    """Evaluate a single criterion for one bidder."""
    result = {
        "criterion_id": criterion.get("id"),
        "criterion_text": criterion.get("criterion_text", ""),
        "category": criterion.get("category", ""),
        "is_mandatory": criterion.get("is_mandatory", True),
        "field_name": criterion.get("field_name", ""),
        "status": "uncertain",
        "confidence": 0.0,
        "extracted_value": "",
        "source_text": "",
        "reasoning": "",
        "evidence": ""
    }

    # No data found in bidder docs
    if not bidder_data or not bidder_data.get("found", False):
        result["confidence"] = 0.3
        result["reasoning"] = f"No information found in bidder documents for: {criterion.get('criterion_text', '')[:80]}"
        result["evidence"] = "Field not present in submitted documents"
        return result

    extracted_value = bidder_data.get("extracted_value", "")
    source_text = bidder_data.get("source_text", "")
    extraction_conf = bidder_data.get("confidence", 0.5)
    notes = bidder_data.get("notes", "")

    result["extracted_value"] = str(extracted_value)
    result["source_text"] = source_text

    # If extraction confidence is very low, mark as uncertain
    if extraction_conf < 0.5:
        result["status"] = "uncertain"
        result["confidence"] = extraction_conf
        result["reasoning"] = f"Bidder data is ambiguous or unclear. {notes}"
        result["evidence"] = f"Source: {source_text[:200]}"
        return result

    # Try rule-based evaluation
    rule_result = _rule_based_eval(
        criterion.get("operator", ""),
        criterion.get("expected_value", ""),
        extracted_value
    )

    if rule_result:
        status, confidence, reasoning = rule_result
        result["status"] = status
        result["confidence"] = min(confidence, extraction_conf)
        result["reasoning"] = reasoning
        result["evidence"] = f"Source: {source_text[:200]}"

        # If extraction confidence is medium, downgrade decisive answers to uncertain
        if extraction_conf < 0.7 and status == "not_met":
            result["status"] = "uncertain"
            result["reasoning"] = f"Possible mismatch but data unclear. {reasoning}"

        return result

    # Fallback to LLM evaluation
    return _llm_evaluate(criterion, bidder_data, result)


def _rule_based_eval(operator, expected_value, extracted_value):
    """Rule-based comparison logic."""
    if not operator or not expected_value or not extracted_value:
        return None

    extracted_str = str(extracted_value).lower().strip()

    # Handle ambiguous bidder responses
    ambiguous_signals = [
        "pending", "provisional", "unclear", "illegible",
        "under audit", "review", "expired", "renewal",
        "approx", "approximately", "tbd", "to be confirmed"
    ]
    if any(sig in extracted_str for sig in ambiguous_signals):
        return ("uncertain", 0.5, f"Bidder data appears ambiguous: '{extracted_value}'")

    # Numeric comparisons
    if operator in [">=", ">", "minimum", "at_least"]:
        expected_num = normalize_financial_value(str(expected_value))
        extracted_num = normalize_financial_value(str(extracted_value))

        # If extracted is also a plain count
        if extracted_num is None:
            try:
                extracted_num = float(extracted_str.split()[0])
            except (ValueError, IndexError):
                pass

        if expected_num is None:
            try:
                expected_num = float(str(expected_value).split()[0])
            except (ValueError, IndexError):
                pass

        if expected_num is not None and extracted_num is not None:
            if extracted_num >= expected_num:
                return (
                    "met", 0.9,
                    f"Bidder value ({extracted_value}) meets requirement ({expected_value})"
                )
            else:
                return (
                    "not_met", 0.9,
                    f"Bidder value ({extracted_value}) is below requirement ({expected_value})"
                )

    # Less-than comparisons
    if operator in ["<=", "<", "maximum"]:
        expected_num = normalize_financial_value(str(expected_value))
        extracted_num = normalize_financial_value(str(extracted_value))

        if expected_num is not None and extracted_num is not None:
            if extracted_num <= expected_num:
                return (
                    "met", 0.9,
                    f"Bidder value ({extracted_value}) is within limit ({expected_value})"
                )
            else:
                return (
                    "not_met", 0.9,
                    f"Bidder value ({extracted_value}) exceeds limit ({expected_value})"
                )

    # Boolean / must_have
    if operator in ["must_have", "required", "mandatory"]:
        valid_words = ["yes", "true", "valid", "available", "present", "submitted", "active"]
        invalid_words = ["no", "false", "invalid", "expired", "not available", "missing", "not found"]

        if any(w in extracted_str for w in valid_words):
            return ("met", 0.85, f"Required item is present: {extracted_value}")

        if any(w in extracted_str for w in invalid_words):
            return ("not_met", 0.85, f"Required item is missing or invalid: {extracted_value}")

        # Default: uncertain
        return ("uncertain", 0.5, f"Cannot clearly verify presence: {extracted_value}")

    return None


def _llm_evaluate(criterion, bidder_data, result):
    """Use LLM as fallback for complex cases."""
    try:
        system_prompt = (
            "You are an expert tender evaluator. Decide if the bidder meets the criterion. "
            "Be cautious — flag uncertain cases as 'uncertain' instead of rejecting. "
            "Return JSON with: status ('met'/'not_met'/'uncertain'), "
            "confidence (0.0-1.0), reasoning, evidence."
        )

        user_prompt = f"""CRITERION: {json.dumps(criterion, indent=2)}
BIDDER DATA: {json.dumps(bidder_data, indent=2)}

Return JSON only."""

        response = call_llm_json(system_prompt, user_prompt, temperature=0.1)

        result["status"] = response.get("status", "uncertain")
        result["confidence"] = float(response.get("confidence", 0.5))
        result["reasoning"] = response.get("reasoning", "")
        result["evidence"] = response.get("evidence", "")

    except Exception as e:
        print(f"LLM evaluation failed: {e}")
        result["status"] = "uncertain"
        result["confidence"] = 0.3
        result["reasoning"] = "Evaluation could not be completed automatically. Needs manual review."
        result["evidence"] = "Auto-evaluation unavailable"

    return result


def _determine_overall(evaluations):
    """Determine overall eligibility status with smart logic."""
    if not evaluations:
        return "needs_review", 0.0

    mandatory_not_met_high_conf = False
    mandatory_uncertain = False
    mandatory_not_met_low_conf = False

    for e in evaluations:
        if e.get("is_mandatory", True):
            if e["status"] == "uncertain":
                mandatory_uncertain = True
            elif e["status"] == "not_met":
                # Strict rejection only if confidence is high
                if e.get("confidence", 0) >= 0.8:
                    mandatory_not_met_high_conf = True
                else:
                    mandatory_not_met_low_conf = True

    # Strong rejection - clear failure on mandatory criteria
    if mandatory_not_met_high_conf:
        return "not_eligible", 0.9

    # Uncertain mandatory criteria → human review
    if mandatory_uncertain or mandatory_not_met_low_conf:
        return "needs_review", 0.65

    # Count overall results
    not_met_count = sum(1 for e in evaluations if e["status"] == "not_met")
    uncertain_count = sum(1 for e in evaluations if e["status"] == "uncertain")

    # All clear - eligible
    if not_met_count == 0 and uncertain_count == 0:
        return "eligible", 0.92

    # Some uncertainty in non-mandatory → still needs review
    if uncertain_count > 0:
        return "needs_review", 0.7

    # Failed only on optional → still eligible
    return "eligible", 0.8


def _generate_summary(bidder_name, status, met, not_met,
                      uncertain, total, evaluations):
    """Generate human-readable summary."""
    status_text = {
        "eligible": "ELIGIBLE",
        "not_eligible": "NOT ELIGIBLE",
        "needs_review": "NEEDS MANUAL REVIEW"
    }

    summary = f"Bidder '{bidder_name}' is {status_text.get(status, 'UNKNOWN')}.\n\n"
    summary += f"Result: {met}/{total} criteria met, "
    summary += f"{not_met} not met, {uncertain} uncertain.\n\n"

    if not_met > 0:
        summary += "FAILED CRITERIA:\n"
        for e in evaluations:
            if e["status"] == "not_met":
                tag = "[MANDATORY]" if e.get("is_mandatory") else "[OPTIONAL]"
                summary += f"  X {tag} {e['criterion_text']}\n"
                summary += f"     Reason: {e['reasoning']}\n"

    if uncertain > 0:
        summary += "\nUNCERTAIN CRITERIA (Needs Review):\n"
        for e in evaluations:
            if e["status"] == "uncertain":
                tag = "[MANDATORY]" if e.get("is_mandatory") else "[OPTIONAL]"
                summary += f"  ? {tag} {e['criterion_text']}\n"
                summary += f"     Note: {e['reasoning']}\n"

    if met > 0 and not_met == 0 and uncertain == 0:
        summary += "All mandatory criteria are satisfied.\n"

    return summary