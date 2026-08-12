import pytest
import json
from unittest.mock import MagicMock

from db import (
    init_db,
    create_escalation_record,
    get_all_escalations,
    update_escalation_status,
    sanitize_text,
)
from agent import Assistant


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_escalations.db"
    init_db(db_file)
    return db_file


def test_sanitize_text_pii_filtering():
    raw_text = (
        "Caller reported suspicious transaction on card 4111222233334444. "
        "Account 9876543210123 was debited. Aadhaar is 999988887777 and PAN is ABCDE1234F. "
        "Caller mentioned OTP 654321 and PIN 1234."
    )

    cleaned = sanitize_text(raw_text)

    assert "4111222233334444" not in cleaned
    assert "[REDACTED_CARD_NUMBER]" in cleaned
    assert "9876543210123" not in cleaned
    assert "[REDACTED_ACCOUNT_NUMBER]" in cleaned
    assert "999988887777" not in cleaned
    assert "[REDACTED_AADHAAR_NUMBER]" in cleaned
    assert "ABCDE1234F" not in cleaned
    assert "[REDACTED_PAN_NUMBER]" in cleaned


def test_create_and_fetch_escalation(temp_db):
    user_id = "9876543210"
    caller_name = "Ramesh Sharma"
    reason_category = "fraud_report"
    what_happened = "Caller reported fake UPI call asking for card 1234567812345678."
    agent_checks = "Verified user identity and active bank account link."

    record = create_escalation_record(
        user_id=user_id,
        caller_name=caller_name,
        reason_category=reason_category,
        what_happened=what_happened,
        agent_checks=agent_checks,
        urgency_level="High",
        language_preference="Hindi",
        preferred_followup="Phone Call",
        db_path=temp_db,
    )

    assert record["reference_id"].startswith("ESC-2026-")
    assert record["user_id"] == user_id
    assert record["caller_name"] == caller_name
    assert record["reason_category"] == reason_category
    assert record["status"] == "OPEN"
    assert "1234567812345678" not in record["what_happened"]

    # Retrieve all
    escalations = get_all_escalations(db_path=temp_db)
    assert len(escalations) == 1
    assert escalations[0]["reference_id"] == record["reference_id"]


def test_update_escalation_status(temp_db):
    record = create_escalation_record(
        user_id="user_999",
        caller_name="Sita Devi",
        reason_category="unauthorized_decision",
        what_happened="Requesting manual loan approval override above limit",
        agent_checks="Checked PM-MUDRA eligibility criteria",
        urgency_level="Medium",
        db_path=temp_db,
    )

    ref_id = record["reference_id"]
    success = update_escalation_status(ref_id, "RESOLVED", db_path=temp_db)
    assert success is True

    escalations = get_all_escalations(db_path=temp_db)
    assert escalations[0]["status"] == "RESOLVED"


@pytest.mark.asyncio
async def test_agent_create_escalation_tool(temp_db, monkeypatch):
    # Patch DEFAULT_DB_PATH so agent tool writes to temp_db
    monkeypatch.setattr("db.DEFAULT_DB_PATH", temp_db)

    assistant = Assistant()
    mock_context = MagicMock()

    res_json_str = await assistant.create_escalation(
        context=mock_context,
        user_id="9988776655",
        caller_name="Vikram Singh",
        reason_category="fraud_report",
        what_happened="Received phishing link claiming account suspension",
        agent_checks_performed="Advised on cyber crime portal 1930 and checked account safety checklist",
        urgency_level="High",
        caller_language="Hindi",
        preferred_followup_method="Phone Call",
    )

    res = json.loads(res_json_str)
    assert res["status"] == "SUCCESS"
    assert "reference_id" in res
    assert res["reference_id"].startswith("ESC-2026-")
    assert "spoken_instruction" in res
