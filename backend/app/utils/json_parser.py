"""Robust JSON parsing for LLM outputs."""
import json
import re
import logging
from typing import Any, Dict, Optional, Tuple, List

logger = logging.getLogger(__name__)


def extract_json_from_llm_response(text: str, fallback: Dict = None) -> Tuple[Dict, bool, str]:
    """
    Extract JSON from LLM response with markdown/text handling.

    Args:
        text: Raw LLM response that may contain JSON wrapped in markdown or text
        fallback: Default dict to return if parsing fails

    Returns:
        Tuple of (parsed_dict, success_bool, error_message)
    """
    if not text or not text.strip():
        return fallback or {}, False, "Empty response"

    # Strategy 1: Extract from markdown code blocks (```json ... ``` or ``` ... ```)
    for pattern in [r'```json\s*([\s\S]*?)\s*```', r'```\s*([\s\S]*?)\s*```']:
        for match in re.findall(pattern, text, re.IGNORECASE):
            try:
                parsed = json.loads(match.strip())
                if isinstance(parsed, dict):
                    logger.debug(f"JSON extracted from markdown code block")
                    return parsed, True, ""
            except json.JSONDecodeError:
                continue

    # Strategy 2: Balanced brace extraction (handles nested objects correctly)
    try:
        parsed = _extract_balanced_json(text)
        if parsed:
            logger.debug(f"JSON extracted using balanced brace matching")
            return parsed, True, ""
    except json.JSONDecodeError as e:
        logger.debug(f"Balanced brace extraction failed: {e}")

    # Strategy 3: Simple first/last brace (fallback for simple cases)
    json_start = text.find('{')
    json_end = text.rfind('}') + 1
    if json_start >= 0 and json_end > json_start:
        try:
            parsed = json.loads(text[json_start:json_end])
            if isinstance(parsed, dict):
                logger.debug(f"JSON extracted using simple brace matching")
                return parsed, True, ""
        except json.JSONDecodeError as e:
            logger.warning(f"Simple brace JSON parse error: {e}")

    # All strategies failed
    preview = text[:200].replace('\n', ' ') if text else "(empty)"
    return fallback or {}, False, f"Could not extract JSON (len={len(text)}, preview='{preview}...')"


def _extract_balanced_json(text: str) -> Optional[Dict]:
    """
    Extract JSON by finding balanced braces.

    Handles cases where there's text after the JSON object ends.
    """
    start = text.find('{')
    if start == -1:
        return None

    brace_count = 0
    in_string = False
    escape = False

    for i, c in enumerate(text[start:], start):
        if escape:
            escape = False
            continue
        if c == '\\' and in_string:
            escape = True
            continue
        if c == '"' and not escape:
            in_string = not in_string
            continue
        if not in_string:
            if c == '{':
                brace_count += 1
            elif c == '}':
                brace_count -= 1
                if brace_count == 0:
                    # Found the closing brace
                    json_str = text[start:i+1]
                    return json.loads(json_str)

    return None


def validate_judge_response(data: Dict, judge_type: str) -> Tuple[Dict, List[str]]:
    """
    Validate and normalize judge response structure.

    Ensures required fields exist and have valid types.

    Args:
        data: Parsed JSON dict from judge
        judge_type: Type of judge for logging (business, technical, feasibility)

    Returns:
        Tuple of (normalized_data, list_of_warnings)
    """
    warnings = []

    # Ensure scores dict exists
    if "scores" not in data or not isinstance(data.get("scores"), dict):
        warnings.append(f"{judge_type}: Missing or invalid 'scores' field")
        data["scores"] = {}

    # Ensure overall_score exists - calculate from individual scores if missing
    if "overall_score" not in data:
        warnings.append(f"{judge_type}: Missing 'overall_score', calculating from individual scores")
        scores = [v for v in data["scores"].values() if isinstance(v, (int, float))]
        data["overall_score"] = sum(scores) / len(scores) if scores else 5.0

    # Validate overall_score is numeric
    if not isinstance(data.get("overall_score"), (int, float)):
        try:
            data["overall_score"] = float(data["overall_score"])
        except (TypeError, ValueError):
            warnings.append(f"{judge_type}: Invalid overall_score type, defaulting to 5.0")
            data["overall_score"] = 5.0

    # Clamp score to valid range
    if data["overall_score"] < 1.0 or data["overall_score"] > 10.0:
        warnings.append(f"{judge_type}: overall_score {data['overall_score']} out of range, clamping")
        data["overall_score"] = max(1.0, min(10.0, data["overall_score"]))

    # Ensure reasoning exists
    if "reasoning" not in data or not isinstance(data.get("reasoning"), str):
        data.setdefault("reasoning", "")
        if not data["reasoning"]:
            warnings.append(f"{judge_type}: Missing 'reasoning' field")

    # Ensure recommendations exists as list
    if "recommendations" not in data or not isinstance(data.get("recommendations"), list):
        data.setdefault("recommendations", [])
        warnings.append(f"{judge_type}: Missing or invalid 'recommendations' field")

    return data, warnings
