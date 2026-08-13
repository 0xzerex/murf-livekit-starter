import json
import logging
import re
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

# Regex patterns for stripping sensitive financial / personal data from escalation summaries
SENSITIVE_TEXT_PATTERNS = [
    (r"\b\d{16}\b", "[REDACTED_CARD_NUMBER]"),
    (r"\b\d{12}\b", "[REDACTED_AADHAAR_NUMBER]"),
    (r"\b[A-Z]{5}\d{4}[A-Z]{1}\b", "[REDACTED_PAN_NUMBER]"),
    (r"\b\d{10,18}\b", "[REDACTED_ACCOUNT_NUMBER]"),
    (r"\b(pin|otp|password|cvv|code)\s*[:=]?\s*\d{3,8}\b", "[REDACTED_SENSITIVE_CODE]"),
]


def sanitize_text(text: str) -> str:
    """Filter out sensitive credentials, account numbers, PINs, OTPs, Aadhaar, and PAN from free text."""
    if not text:
        return ""
    sanitized = str(text)
    for pattern, replacement in SENSITIVE_TEXT_PATTERNS:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    return sanitized


def get_db_connection(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Connect to SQLite database with row factory for dictionary access."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path | str = DEFAULT_DB_PATH) -> None:
    """Initialize SQLite database schema for storing caller records and escalation requests."""
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
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS escalations (
                    reference_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    caller_name TEXT NOT NULL,
                    reason_category TEXT NOT NULL,
                    what_happened TEXT NOT NULL,
                    agent_checks TEXT NOT NULL,
                    urgency_level TEXT NOT NULL,
                    language_preference TEXT NOT NULL,
                    preferred_followup TEXT NOT NULL,
                    status TEXT DEFAULT 'OPEN',
                    created_at TEXT NOT NULL
                );
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    call_id TEXT UNIQUE NOT NULL,
                    caller_name TEXT DEFAULT 'Citizen',
                    language TEXT DEFAULT 'Hindi',
                    duration_seconds INTEGER DEFAULT 0,
                    status TEXT NOT NULL CHECK(status IN ('success', 'failed')),
                    summary TEXT,
                    created_at TEXT NOT NULL
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


def create_escalation_record(
    user_id: str,
    caller_name: str,
    reason_category: str,
    what_happened: str,
    agent_checks: str,
    urgency_level: str = "High",
    language_preference: str = "Hindi",
    preferred_followup: str = "Phone Call",
    db_path: Path | str = DEFAULT_DB_PATH,
) -> dict[str, Any]:
    """Create a sanitized human-help escalation record in the database."""
    init_db(db_path)

    import random

    ref_num = random.randint(10000, 99999)
    reference_id = f"ESC-2026-{ref_num}"

    clean_what_happened = sanitize_text(what_happened)
    clean_agent_checks = sanitize_text(agent_checks)
    now_iso = datetime.now(timezone.utc).isoformat()

    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO escalations (
                    reference_id, user_id, caller_name, reason_category,
                    what_happened, agent_checks, urgency_level,
                    language_preference, preferred_followup, status, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN', ?);
                """,
                (
                    reference_id,
                    str(user_id).strip(),
                    str(caller_name).strip(),
                    str(reason_category).strip(),
                    clean_what_happened,
                    clean_agent_checks,
                    str(urgency_level).strip(),
                    str(language_preference).strip(),
                    str(preferred_followup).strip(),
                    now_iso,
                ),
            )
    finally:
        conn.close()

    return {
        "reference_id": reference_id,
        "user_id": user_id,
        "caller_name": caller_name,
        "reason_category": reason_category,
        "what_happened": clean_what_happened,
        "agent_checks": clean_agent_checks,
        "urgency_level": urgency_level,
        "language_preference": language_preference,
        "preferred_followup": preferred_followup,
        "status": "OPEN",
        "created_at": now_iso,
    }


def get_all_escalations(
    db_path: Path | str = DEFAULT_DB_PATH,
) -> list[dict[str, Any]]:
    """Retrieve all escalation records ordered by creation date (newest first)."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM escalations ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def update_escalation_status(
    reference_id: str,
    new_status: str = "RESOLVED",
    db_path: Path | str = DEFAULT_DB_PATH,
) -> bool:
    """Update status of an escalation record (e.g. OPEN -> RESOLVED)."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                "UPDATE escalations SET status = ? WHERE reference_id = ?",
                (new_status, reference_id),
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def log_call_outcome(
    call_id: str,
    caller_name: str = "Citizen",
    language: str = "Hindi",
    duration_seconds: int = 0,
    status: str = "failed",
    summary: str = "",
    db_path: Path | str = DEFAULT_DB_PATH,
) -> dict[str, Any]:
    """Log a call outcome ('success' or 'failed') to the calls table with sanitized summary."""
    init_db(db_path)

    clean_summary = sanitize_text(summary)
    valid_status = "success" if str(status).strip().lower() == "success" else "failed"
    now_iso = datetime.now(timezone.utc).isoformat()

    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO calls (call_id, caller_name, language, duration_seconds, status, summary, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(call_id) DO UPDATE SET
                    caller_name = excluded.caller_name,
                    language = excluded.language,
                    duration_seconds = excluded.duration_seconds,
                    status = excluded.status,
                    summary = excluded.summary,
                    created_at = excluded.created_at;
                """,
                (
                    str(call_id).strip(),
                    str(caller_name).strip() or "Citizen",
                    str(language).strip() or "Hindi",
                    int(duration_seconds),
                    valid_status,
                    clean_summary,
                    now_iso,
                ),
            )
    finally:
        conn.close()

    return {
        "call_id": call_id,
        "caller_name": caller_name,
        "language": language,
        "duration_seconds": duration_seconds,
        "status": valid_status,
        "summary": clean_summary,
        "created_at": now_iso,
    }


def get_recent_calls(
    limit: int = 50,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> list[dict[str, Any]]:
    """Retrieve recent call records ordered by creation date (newest first)."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM calls ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_call_stats(
    db_path: Path | str = DEFAULT_DB_PATH,
) -> dict[str, Any]:
    """Retrieve aggregate analytics for total, successful, failed calls, and average duration."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                COUNT(*) as total_calls,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_calls,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_calls,
                ROUND(AVG(duration_seconds), 1) as avg_duration
            FROM calls;
            """
        )
        row = cursor.fetchone()
        if not row or row["total_calls"] == 0:
            return {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "avg_duration": 0.0,
            }
        return {
            "total_calls": row["total_calls"] or 0,
            "successful_calls": row["successful_calls"] or 0,
            "failed_calls": row["failed_calls"] or 0,
            "avg_duration": row["avg_duration"] or 0.0,
        }
    finally:
        conn.close()


