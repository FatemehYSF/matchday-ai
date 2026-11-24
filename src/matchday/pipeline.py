import json
from pathlib import Path

from .checks import run_all_checks
from .models import PLATFORMS, Match
from .writers import MockWriter

from . import db
from .graphics import render_match_card

MAX_ATTEMPTS = 3


def load_matches(path: str) -> list[Match]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Match.model_validate(item) for item in raw]


def caption_with_retries(conn, writer, match, platform, known_players):
    feedback: list[str] = []
    for attempt in range(1, MAX_ATTEMPTS + 1):
        draft = writer.write(match, platform, feedback)
        results = run_all_checks(match, draft, platform, known_players)
        db.save_caption(conn, match.match_id, platform.name, attempt, draft, results)

        if all(r.passed for r in results):
            break
        feedback = [f"{r.name}: {r.detail}" for r in results if not r.passed]
        print(f"  feedback: {feedback}")

    return draft, results, attempt


def run_pipeline(matches_path: str = "data/matches.json") -> None:
    Path("output/matchday.db").unlink(missing_ok=True)
    conn = db.connect()
    matches = load_matches(matches_path)
    known_players = {g.player for m in matches for g in m.goals}
    writer = MockWriter()

    for match in matches:
        for platform in PLATFORMS.values():
            draft, results, attempts = caption_with_retries(conn, writer, match, platform, known_players)
            if platform.name == "instagram" and all(r.passed for r in results):
                render_match_card(match, draft.caption, f"output/{match.match_id}.png")
            status = "PASS" if all(r.passed for r in results) else "FAIL"
            print(f"[{status}] {match.match_id} {platform.name:<9} (attempts: {attempts}) {draft.caption}")
    db.print_report(conn)
    conn.close()
