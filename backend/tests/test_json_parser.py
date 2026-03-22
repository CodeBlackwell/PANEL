"""Test JSON parsing utilities."""

from app.utils.json_parser import extract_json_from_llm_response, validate_judge_response


class TestExtractJson:
    def test_plain_json(self):
        text = '{"questions": [], "is_complete": true}'
        result, success, error = extract_json_from_llm_response(text)
        assert success
        assert result["is_complete"] is True

    def test_markdown_code_block(self):
        text = 'Here is the response:\n```json\n{"score": 8.5}\n```\nDone.'
        result, success, error = extract_json_from_llm_response(text)
        assert success
        assert result["score"] == 8.5

    def test_generic_code_block(self):
        text = '```\n{"key": "value"}\n```'
        result, success, error = extract_json_from_llm_response(text)
        assert success
        assert result["key"] == "value"

    def test_json_with_surrounding_text(self):
        text = 'Sure, here is the evaluation: {"overall_score": 7.0, "reasoning": "Good"} Hope this helps!'
        result, success, error = extract_json_from_llm_response(text)
        assert success
        assert result["overall_score"] == 7.0

    def test_nested_json(self):
        text = '{"scores": {"design": 8, "security": 7}, "overall_score": 7.5}'
        result, success, error = extract_json_from_llm_response(text)
        assert success
        assert result["scores"]["design"] == 8

    def test_empty_string(self):
        result, success, error = extract_json_from_llm_response("")
        assert not success
        assert result == {}

    def test_no_json(self):
        result, success, error = extract_json_from_llm_response("This has no JSON at all")
        assert not success

    def test_fallback_returned(self):
        fallback = {"default": True}
        result, success, error = extract_json_from_llm_response("no json", fallback)
        assert not success
        assert result == fallback


class TestValidateJudgeResponse:
    def test_valid_response(self):
        data = {
            "scores": {"design": 8, "security": 7},
            "overall_score": 7.5,
            "reasoning": "Well designed",
            "recommendations": ["Add caching"],
        }
        result, warnings = validate_judge_response(data, "technical")
        assert len(warnings) == 0
        assert result["overall_score"] == 7.5

    def test_missing_overall_score_calculated(self):
        data = {"scores": {"a": 8, "b": 6}, "reasoning": "ok", "recommendations": []}
        result, warnings = validate_judge_response(data, "business")
        assert result["overall_score"] == 7.0
        assert any("Missing 'overall_score'" in w for w in warnings)

    def test_score_clamped(self):
        data = {"scores": {}, "overall_score": 15.0, "reasoning": "", "recommendations": []}
        result, warnings = validate_judge_response(data, "feasibility")
        assert result["overall_score"] == 10.0

    def test_missing_scores_field(self):
        data = {"overall_score": 5.0}
        result, warnings = validate_judge_response(data, "technical")
        assert result["scores"] == {}
        assert any("Missing or invalid 'scores'" in w for w in warnings)

    def test_string_overall_score_converted(self):
        data = {"scores": {}, "overall_score": "8.0", "reasoning": "", "recommendations": []}
        result, warnings = validate_judge_response(data, "business")
        assert result["overall_score"] == 8.0
