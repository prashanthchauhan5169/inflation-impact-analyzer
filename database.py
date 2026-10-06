"""
database.py – SQLite helpers for the Inflation Impact Analyzer.
"""

from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("inflation_survey.db")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the responses table if it does not exist."""
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                id                     INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at             TEXT    NOT NULL,
                age_band               TEXT    NOT NULL,
                income_range           TEXT    NOT NULL,
                family_size            INTEGER NOT NULL,
                spend_food             REAL    NOT NULL DEFAULT 0,
                spend_transport        REAL    NOT NULL DEFAULT 0,
                spend_housing          REAL    NOT NULL DEFAULT 0,
                spend_education        REAL    NOT NULL DEFAULT 0,
                spend_healthcare       REAL    NOT NULL DEFAULT 0,
                spend_entertainment    REAL    NOT NULL DEFAULT 0,
                spend_other            REAL    NOT NULL DEFAULT 0,
                coping_cheaper_brands       INTEGER NOT NULL DEFAULT 0,
                coping_cut_non_essentials   INTEGER NOT NULL DEFAULT 0,
                coping_fewer_shopping_trips INTEGER NOT NULL DEFAULT 0,
                coping_delayed_big_purchases INTEGER NOT NULL DEFAULT 0,
                personal_rate          REAL,
                penalty                REAL,
                adjusted_rate          REAL,
                headline_rate          REAL,
                impact_label           TEXT,
                breakdown_json         TEXT
            )
        """)
        conn.commit()


def insert_response(
    age_band: str,
    income_range: str,
    family_size: int,
    spend: dict[str, float],
    behaviours: list[str],
    score: dict,
) -> int:
    """Insert a survey response and return the new row id."""
    now = datetime.utcnow().isoformat(timespec="seconds")
    with _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO responses (
                created_at, age_band, income_range, family_size,
                spend_food, spend_transport, spend_housing,
                spend_education, spend_healthcare, spend_entertainment, spend_other,
                coping_cheaper_brands, coping_cut_non_essentials,
                coping_fewer_shopping_trips, coping_delayed_big_purchases,
                personal_rate, penalty, adjusted_rate, headline_rate,
                impact_label, breakdown_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                now, age_band, income_range, family_size,
                spend.get("food", 0),
                spend.get("transport", 0),
                spend.get("housing", 0),
                spend.get("education", 0),
                spend.get("healthcare", 0),
                spend.get("entertainment", 0),
                spend.get("other", 0),
                int("cheaper_brands" in behaviours),
                int("cut_non_essentials" in behaviours),
                int("fewer_shopping_trips" in behaviours),
                int("delayed_big_purchases" in behaviours),
                score.get("personal_rate"),
                score.get("penalty"),
                score.get("adjusted_rate"),
                score.get("headline_rate"),
                score.get("label"),
                json.dumps(score.get("breakdown", {})),
            ),
        )
        conn.commit()
        return cur.lastrowid


def get_response(response_id: int) -> dict | None:
    """Fetch a single response as a plain dict."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM responses WHERE id = ?", (response_id,)
        ).fetchone()
    return dict(row) if row else None


def get_all_responses() -> list[dict]:
    """Return all responses as a list of dicts, newest first."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM responses ORDER BY created_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def response_count() -> int:
    with _connect() as conn:
        return conn.execute("SELECT COUNT(*) FROM responses").fetchone()[0]
