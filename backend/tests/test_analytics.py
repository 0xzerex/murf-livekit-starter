import pytest
from db import (
    init_db,
    log_call_outcome,
    get_recent_calls,
    get_call_stats,
    sanitize_text,
)


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_analytics_caller_data.db"
    init_db(db_file)
    return db_file


def test_log_call_outcome_success(temp_db):
    res = log_call_outcome(
        call_id="call-001",
        caller_name="Ramesh Sharma",
        language="Hindi",
        duration_seconds=45,
        status="success",
        summary="Checked scheme eligibility for PMSBY",
        db_path=temp_db,
    )

    assert res["call_id"] == "call-001"
    assert res["status"] == "success"
    assert res["duration_seconds"] == 45
    assert "PMSBY" in res["summary"]

    calls = get_recent_calls(limit=10, db_path=temp_db)
    assert len(calls) == 1
    assert calls[0]["call_id"] == "call-001"
    assert calls[0]["status"] == "success"


def test_log_call_outcome_failed(temp_db):
    res = log_call_outcome(
        call_id="call-002",
        caller_name="Sita Devi",
        language="Hindi",
        duration_seconds=12,
        status="failed",
        summary="Caller disconnected early or did not complete an inquiry",
        db_path=temp_db,
    )

    assert res["status"] == "failed"

    stats = get_call_stats(db_path=temp_db)
    assert stats["total_calls"] == 1
    assert stats["failed_calls"] == 1
    assert stats["successful_calls"] == 0
    assert stats["avg_duration"] == 12.0


def test_call_stats_aggregate(temp_db):
    log_call_outcome(
        call_id="call-101",
        caller_name="Aman",
        duration_seconds=30,
        status="success",
        summary="Checked PMSBY",
        db_path=temp_db,
    )
    log_call_outcome(
        call_id="call-102",
        caller_name="Bina",
        duration_seconds=60,
        status="success",
        summary="Created escalation ticket",
        db_path=temp_db,
    )
    log_call_outcome(
        call_id="call-103",
        caller_name="Chiran",
        duration_seconds=15,
        status="failed",
        summary="Disconnected early",
        db_path=temp_db,
    )

    stats = get_call_stats(db_path=temp_db)
    assert stats["total_calls"] == 3
    assert stats["successful_calls"] == 2
    assert stats["failed_calls"] == 1
    assert stats["avg_duration"] == 35.0


def test_log_call_privacy_sanitization(temp_db):
    raw_summary = (
        "Checked scheme PMJDY. Caller provided Aadhaar 999988887777 and card 4111222233334444 with OTP 123456."
    )
    res = log_call_outcome(
        call_id="call-priv-1",
        caller_name="Test Citizen",
        status="success",
        summary=raw_summary,
        db_path=temp_db,
    )

    assert "999988887777" not in res["summary"]
    assert "4111222233334444" not in res["summary"]
    assert "[REDACTED_AADHAAR_NUMBER]" in res["summary"]
    assert "[REDACTED_CARD_NUMBER]" in res["summary"]
