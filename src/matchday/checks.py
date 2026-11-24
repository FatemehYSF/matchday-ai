from .models import CaptionDraft, CheckResult, Match, Platform
import re

BANNED_WORDS = {"idiot", "stupid", "trash", "useless", "clown", "pathetic"}


def check_score(match: Match, draft: CaptionDraft) -> CheckResult:
    expected = f"{match.home_score}-{match.away_score}"
    found = expected in draft.caption.replace("–", "-")
    return CheckResult(
        name="score_correct",
        passed=found,
        detail="" if found else f"Score must appear as {expected} (home-away)",
    )


def check_teams(match: Match, draft: CaptionDraft) -> CheckResult:
    missing = [t for t in (match.home_team, match.away_team) if t not in draft.caption]
    return CheckResult(
        name="teams_mentioned",
        passed=not missing,
        detail=f"Missing team name(s): {', '.join(missing)}" if missing else "",
    )


def check_players(match: Match, draft: CaptionDraft, known_players: set[str]) -> CheckResult:
    wrong = sorted(p for p in known_players - match.scorers if p in draft.caption)
    return CheckResult(
        name="only_real_scorers",
        passed=not wrong,
        detail=f"Mentions players who did not score: {', '.join(wrong)}" if wrong else "",
    )


def check_length(draft: CaptionDraft, platform: Platform) -> CheckResult:
    text = f"{draft.caption} {' '.join(draft.hashtags)}"
    ok = len(text) <= platform.max_chars
    return CheckResult(
        name="length_ok",
        passed=ok,
        detail="" if ok else f"{len(text)} characters, limit is {platform.max_chars}",
    )


def check_hashtags(draft: CaptionDraft, platform: Platform) -> CheckResult:
    ok = 1 <= len(draft.hashtags) <= platform.max_hashtags
    return CheckResult(
        name="hashtags_ok",
        passed=ok,
        detail="" if ok else f"Use 1 to {platform.max_hashtags} hashtags, got {len(draft.hashtags)}",
    )


def check_safe_language(draft: CaptionDraft) -> CheckResult:
    words = set(re.findall(r"[a-z]+", draft.caption.lower()))
    hits = sorted(words & BANNED_WORDS)
    return CheckResult(
        name="safe_language",
        passed=not hits,
        detail=f"Banned words: {', '.join(hits)}" if hits else "",
    )


def run_all_checks(match: Match, draft: CaptionDraft, platform: Platform, known_players: set[str]) -> list[CheckResult]:
    return [
        check_score(match, draft),
        check_teams(match, draft),
        check_players(match, draft, known_players),
        check_length(draft, platform),
        check_hashtags(draft, platform),
        check_safe_language(draft),
    ]
