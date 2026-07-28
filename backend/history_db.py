"""SQLite storage for prediction history (replaces history.json)."""
import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "history.db"

_conn: sqlite3.Connection | None = None


def _get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(str(DB_PATH))
        _conn.row_factory = sqlite3.Row
        _conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                balita_id TEXT NOT NULL,
                usia_bulan INTEGER,
                jenis_kelamin TEXT,
                tinggi_cm REAL,
                prediction TEXT,
                risk_score REAL,
                shap TEXT,
                rekomendasi TEXT,
                created_at TEXT
            )
        """)
        _conn.execute("CREATE INDEX IF NOT EXISTS idx_balita_id ON predictions(balita_id)")
        _conn.commit()
    return _conn


def save_prediction(data: dict) -> None:
    conn = _get_conn()
    conn.execute(
        """INSERT INTO predictions
           (balita_id, usia_bulan, jenis_kelamin, tinggi_cm,
            prediction, risk_score, shap, rekomendasi, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data["balita_id"],
            data.get("usia_bulan"),
            data.get("jenis_kelamin"),
            data.get("tinggi_cm"),
            data.get("prediction"),
            data.get("risk_score"),
            json.dumps(data.get("shap", {}), ensure_ascii=False),
            json.dumps(data.get("rekomendasi", {}), ensure_ascii=False),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()


def get_history(balita_id: str, limit: int = 20) -> list[dict]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM predictions WHERE balita_id = ? ORDER BY created_at DESC LIMIT ?",
        (balita_id, limit),
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


def list_balita() -> list[dict]:
    conn = _get_conn()
    rows = conn.execute(
        """SELECT balita_id, COUNT(*) as total,
                  MAX(created_at) as last_check
           FROM predictions
           GROUP BY balita_id
           ORDER BY last_check DESC"""
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for key in ("shap", "rekomendasi"):
        if key in d and isinstance(d[key], str):
            try:
                d[key] = json.loads(d[key])
            except (json.JSONDecodeError, TypeError):
                pass
    return d