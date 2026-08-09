import pytest

from db import get_caller, init_db, sanitize_facts, upsert_caller


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_caller_data.db"
    init_db(db_file)
    return db_file


def test_init_and_empty_lookup(temp_db):
    record = get_caller("user_123", db_path=temp_db)
    assert record is None


def test_upsert_and_get_caller(temp_db):
    user_id = "user_001"
    name = "Ramesh Kumar"
    language_preference = "Hinglish"
    facts = {
        "schemes_checked": ["PMJDY", "PMSBY"],
        "eligibility_status": "Eligible for PMSBY",
        "occupation": "Farmer",
    }

    result = upsert_caller(
        user_id=user_id,
        name=name,
        language_preference=language_preference,
        facts=facts,
        db_path=temp_db,
    )

    assert result["user_id"] == user_id
    assert result["name"] == name
    assert result["language_preference"] == language_preference
    assert result["facts"]["occupation"] == "Farmer"
    assert "PMJDY" in result["facts"]["schemes_checked"]

    # Retrieve from DB
    fetched = get_caller(user_id, db_path=temp_db)
    assert fetched is not None
    assert fetched["user_id"] == user_id
    assert fetched["name"] == name
    assert fetched["language_preference"] == language_preference
    assert fetched["facts"]["schemes_checked"] == ["PMJDY", "PMSBY"]
    assert "last_interaction" in fetched


def test_sensitive_facts_sanitization(temp_db):
    raw_facts = {
        "schemes_checked": ["PMJJBY"],
        "account_number": "123456789012",
        "aadhaar": "999988887777",
        "pan_card": "ABCDE1234F",
        "pin": "1234",
        "otp": "567890",
        "annual_income": "Under 2 Lakhs",
    }

    cleaned = sanitize_facts(raw_facts)
    assert "schemes_checked" in cleaned
    assert "annual_income" in cleaned
    assert "account_number" not in cleaned
    assert "aadhaar" not in cleaned
    assert "pan_card" not in cleaned
    assert "pin" not in cleaned
    assert "otp" not in cleaned

    # Verify when saving caller info
    saved = upsert_caller(
        user_id="user_priv",
        name="Sita Devi",
        facts=raw_facts,
        db_path=temp_db,
    )
    assert "account_number" not in saved["facts"]
    assert "aadhaar" not in saved["facts"]
    assert saved["facts"]["annual_income"] == "Under 2 Lakhs"


def test_update_caller_facts_merging(temp_db):
    user_id = "user_002"
    upsert_caller(
        user_id=user_id,
        name="Anita",
        facts={"schemes_checked": ["PMJDY"]},
        db_path=temp_db,
    )

    upsert_caller(
        user_id=user_id,
        name="Anita",
        facts={"occupation": "Teacher", "eligibility_answers": "Qualified for APY"},
        db_path=temp_db,
    )

    fetched = get_caller(user_id, db_path=temp_db)
    assert fetched["facts"]["schemes_checked"] == ["PMJDY"]
    assert fetched["facts"]["occupation"] == "Teacher"
    assert fetched["facts"]["eligibility_answers"] == "Qualified for APY"
