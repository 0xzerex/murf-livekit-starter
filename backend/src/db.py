import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("db")

DEFAULT_DB_PATH = Path(__file__).parent.parent / "caller_data.db"

# Sensitive fields that must NOT be stored in caller facts (Financial Services track policy)
SENSITIVE_KEYS = {
    "account_number",
    "account_no",
    "acc_num",
    "bank_account",
    "aadhaar",
    "aadhaar_card",
    "pan",
    "pan_card",
    "pin",
    "upi_pin",
    "otp",
    "card_number",
    "debit_card",
    "credit_card",
    "cvv",
    "id_number",
    "ssn",
}


def get_db_connection(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Connect to SQLite database with row factory for dictionary access."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path | str = DEFAULT_DB_PATH) -> None:
    """Initialize SQLite database schema for storing caller records."""
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS callers (
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    language_preference TEXT DEFAULT 'Hindi',
                    facts TEXT NOT NULL,
                    last_interaction TEXT NOT NULL
                );
                """
            )
        logger.info(f"Database initialized successfully at {db_path}")
    finally:
        conn.close()


def sanitize_facts(facts: dict[str, Any]) -> dict[str, Any]:
    """Filter out any sensitive financial or personal identification data from facts."""
    if not isinstance(facts, dict):
        return {}

    cleaned_facts = {}
    for key, value in facts.items():
        key_lower = str(key).strip().lower()
        if key_lower in SENSITIVE_KEYS or any(
            sens in key_lower
            for sens in ("account", "aadhaar", "pan", "pin", "otp", "card")
        ):
            logger.warning(f"Sanitizing sensitive key '{key}' from facts dictionary.")
            continue
        cleaned_facts[key] = value
    return cleaned_facts


def get_caller(
    user_id: str, db_path: Path | str = DEFAULT_DB_PATH
) -> dict[str, Any] | None:
    """Look up a caller by user_id and return their profile record, or None if not found."""
    if not user_id:
        return None

    init_db(db_path)
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, name, language_preference, facts, last_interaction FROM callers WHERE user_id = ?",
            (str(user_id).strip(),),
        )
        row = cursor.fetchone()
        if not row:
            return None

        try:
            facts_dict = json.loads(row["facts"])
        except Exception:
            facts_dict = {}

        return {
            "user_id": row["user_id"],
            "name": row["name"],
            "language_preference": row["language_preference"],
            "facts": facts_dict,
            "last_interaction": row["last_interaction"],
        }
    finally:
        conn.close()


def upsert_caller(
    user_id: str,
    name: str,
    language_preference: str = "Hindi",
    facts: dict[str, Any] | None = None,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> dict[str, Any]:
    """Save or update caller information with updated ISO timestamp."""
    user_id = str(user_id).strip()
    name = str(name).strip()
    language_preference = (
        str(language_preference).strip() if language_preference else "Hindi"
    )

    # Merge with existing facts if present
    existing = get_caller(user_id, db_path=db_path)
    combined_facts = {}
    if existing and isinstance(existing.get("facts"), dict):
        combined_facts.update(existing["facts"])

    if facts and isinstance(facts, dict):
        cleaned_new_facts = sanitize_facts(facts)
        combined_facts.update(cleaned_new_facts)

    facts_json = json.dumps(combined_facts, ensure_ascii=False)
    now_iso = datetime.now(timezone.utc).isoformat()

    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO callers (user_id, name, language_preference, facts, last_interaction)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    name = excluded.name,
                    language_preference = excluded.language_preference,
                    facts = excluded.facts,
                    last_interaction = excluded.last_interaction;
                """,
                (user_id, name, language_preference, facts_json, now_iso),
            )
    finally:
        conn.close()

    return {
        "user_id": user_id,
        "name": name,
        "language_preference": language_preference,
        "facts": combined_facts,
        "last_interaction": now_iso,
    }
