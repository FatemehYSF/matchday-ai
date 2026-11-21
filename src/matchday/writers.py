from .models import CaptionDraft, Match, Platform

SYSTEM_PROMPT = """You write social media captions for a football media brand \
with millions of young fans.

Brand voice:
- Hype, fun and fan-first, but never insulting players, clubs or fans.
- Short sentences. Plain English.

Hard rules:
- Use ONLY facts from the match data. Never invent players, minutes or scores.
- The score must appear exactly as given, in the form HOME_SCORE-AWAY_SCORE.
- Mention both team names exactly as written in the data.
- Only mention players who scored in this match.
- Hashtags go in the hashtags list, not in the caption text."""


def build_user_prompt(match: Match, platform: Platform, feedback: list[str]) -> str:
    prompt = (
        f"Platform: {platform.name}\n"
        f"Style: {platform.style}\n"
        f"Limit: {platform.max_chars} characters in total, "
        f"at most {platform.max_hashtags} hashtags.\n\n"
        f"Match data (JSON):\n{match.model_dump_json(indent=2)}"
    )
    if feedback:
        prompt += "\n\nYour previous caption failed these checks. Fix them:\n"
        prompt += "\n".join(f"- {item}" for item in feedback)
    return prompt


class MockWriter:
    """A fake LLM: free, offline, same answer every time."""

    def write(self, match: Match, platform: Platform, feedback: list[str]) -> CaptionDraft:
        home, away = match.home_score, match.away_score

        if match.goals:
            names = [g.player for g in match.goals]
            top = max(dict.fromkeys(names), key=names.count)
            star = f" {top} steals the show!"
        else:
            star = " Two walls, zero goals."

        caption = f"FULL TIME: {match.home_team} {home}-{away} {match.away_team}.{star}"

        tag = "#" + match.competition.replace(" ", "")
        hashtags = [tag, "#Football", "#Matchday", "#FullTime"][: platform.max_hashtags]
        return CaptionDraft(caption=caption, hashtags=hashtags)
    