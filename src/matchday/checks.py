from .models import CaptionDraft, CheckResult, Match


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
