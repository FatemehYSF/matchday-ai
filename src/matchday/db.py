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


def print_report(conn) -> None:
    print("\n=== First-try pass rate ===")
    rows = conn.execute(
        "SELECT platform, COUNT(*), SUM(passed) FROM captions WHERE attempt = 1 GROUP BY platform"
    ).fetchall()
    for platform, total, passed in rows:
        print(f"{platform:<10} {passed}/{total} = {100 * passed / total:.0f}%")

    print("\n=== Failed checks ===")
    rows = conn.execute(
        "SELECT name, COUNT(*) FROM checks WHERE passed = 0 GROUP BY name ORDER BY COUNT(*) DESC"
    ).fetchall()
    for name, failures in rows:
        print(f"{name:<15} {failures}")
