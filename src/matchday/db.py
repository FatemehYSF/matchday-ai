import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS captions (
    caption_id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id   TEXT NOT NULL,
    platform   TEXT NOT NULL,
    attempt    INTEGER NOT NULL,
    caption    TEXT NOT NULL,
    passed     INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS checks (
    caption_id INTEGER NOT NULL,
    name       TEXT NOT NULL,
    passed     INTEGER NOT NULL,
    detail     TEXT
);
"""


def connect(path: str = "output/matchday.db") -> sqlite3.Connection:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    return conn


def save_caption(conn, match_id, platform, attempt, draft, results) -> None:
    passed = all(r.passed for r in results)
    cur = conn.execute(
        "INSERT INTO captions (match_id, platform, attempt, caption, passed) VALUES (?, ?, ?, ?, ?)",
        (match_id, platform, attempt, draft.caption, passed),
    )
    conn.executemany(
        "INSERT INTO checks (caption_id, name, passed, detail) VALUES (?, ?, ?, ?)",
        [(cur.lastrowid, r.name, r.passed, r.detail) for r in results],
    )
    conn.commit()
