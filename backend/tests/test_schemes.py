import json
import pytest
from schemes import (
    DATA_AS_OF_DATE,
    SCHEMES_DATA,
    evaluate_scheme_eligibility,
    normalize_scheme_name,
)
from agent import Assistant


def test_normalize_scheme_name():
    assert normalize_scheme_name("PMSBY") == "PMSBY"
    assert normalize_scheme_name("pmsby") == "PMSBY"
    assert normalize_scheme_name("suraksha bima") == "PMSBY"
    assert normalize_scheme_name("Atal Pension Yojana") == "APY"
    assert normalize_scheme_name("sukanya samriddhi") == "SSY"
    assert normalize_scheme_name("pm kisan") == "PM-KISAN"
    assert normalize_scheme_name("nonexistent_scheme_xyz") is None


def test_pmsby_eligible():
    result = evaluate_scheme_eligibility(
        scheme_name="PMSBY",
        age=30,
        has_bank_account=True,
    )
    assert result["status"] == "ELIGIBLE"
    assert result["scheme_key"] == "PMSBY"
    assert len(result["documents_required"]) > 0
    assert result["as_of_date"] == DATA_AS_OF_DATE
    assert "Aadhaar Card" in str(result["documents_required"])


def test_apy_ineligible_over_age():
    result = evaluate_scheme_eligibility(
        scheme_name="APY",
        age=45,  # APY max age is 40
        has_bank_account=True,
    )
    assert result["status"] == "INELIGIBLE"
    assert any("अधिकतम स्वीकृत आयु" in reason for reason in result["reasons_ineligible"])


def test_scheme_more_info_needed():
    result = evaluate_scheme_eligibility(
        scheme_name="PMJJBY",
        age=None,  # missing age
        has_bank_account=True,
    )
    assert result["status"] == "MORE_INFO_NEEDED"
    assert len(result["missing_info"]) > 0


def test_ssy_girl_child():
    result = evaluate_scheme_eligibility(
        scheme_name="SSY",
        has_girl_child_under_10=True,
        age=35,
    )
    assert result["status"] == "ELIGIBLE"
    assert "Birth Certificate of the girl child" in str(result["documents_required"])


def test_unknown_scheme():
    result = evaluate_scheme_eligibility(scheme_name="Random Scheme 123")
    assert result["status"] == "UNKNOWN_SCHEME"
    assert " उपलब्ध मुख्य योजनाएं" in result["message"]
    assert result["as_of_date"] == DATA_AS_OF_DATE


@pytest.mark.asyncio
async def test_agent_tool_check_scheme_eligibility():
    assistant = Assistant()
    tool_resp_str = await assistant.check_scheme_eligibility(
        context=None,
        scheme_name="PMSBY",
        age=25,
        has_bank_account=True,
    )
    data = json.loads(tool_resp_str)
    assert data["status"] == "ELIGIBLE"
    assert data["scheme_name"] == "Pradhan Mantri Suraksha Bima Yojana (PMSBY)"
    assert "as_of_date" in data
    assert len(data["documents_required"]) >= 3


@pytest.mark.asyncio
async def test_agent_tool_failure_path_out_loud(monkeypatch):
    assistant = Assistant()

    # Force an exception inside evaluate_scheme_eligibility to simulate service failure / timeout
    def mock_raise(*args, **kwargs):
        raise TimeoutError("Database connection timed out")

    monkeypatch.setattr("agent.evaluate_scheme_eligibility", mock_raise)

    tool_resp_str = await assistant.check_scheme_eligibility(
        context=None,
        scheme_name="PMSBY",
    )
    data = json.loads(tool_resp_str)
    assert data["status"] == "FAILURE_ERROR"
    assert "ALERT: The scheme eligibility service experienced a connection/execution failure." in data["spoken_instruction"]
    assert "as_of_date" in data
