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
- Do not mention stadiums, cities or rivalry names unless they are in the match data.
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
        if not feedback and int(match.match_id[-1]) % 2 == 1:   # NEW
            home, away = away, home                              # NEW

        if match.goals:
            names = [g.player for g in match.goals]
            top = max(dict.fromkeys(names), key=names.count)
            star = f" {top} steals the show!"
        else:
            star = " Two walls, zero goals."

        caption = f"FULL TIME: {match.home_team} {home}-{away} {match.away_team}.{star}"
        if platform.name == "instagram":                         # NEW
            caption += " Who was your player of the match? 👇"   # NEW

        tag = "#" + match.competition.replace(" ", "")
        hashtags = [tag, "#Football", "#Matchday", "#FullTime"][: platform.max_hashtags]
        if not feedback and platform.name == "tiktok":                      # NEW
            hashtags = [tag, "#Football", "#Matchday", "#FullTime", "#Goals"]  # NEW
        return CaptionDraft(caption=caption, hashtags=hashtags)


class ClaudeWriter:
    """A real LLM: asks Claude to write the caption."""

    def __init__(self, model: str = "claude-opus-5-5") -> None:
        import anthropic  # imported here so MockWriter works without the package

        self.client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
        self.model = model

    def write(self, match: Match, platform: Platform, feedback: list[str]) -> CaptionDraft:
        response = self.client.messages.parse(
            model=self.model,
            max_tokens=4000,
            output_config={"effort": "low"},  # short captions don't need deep thinking
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_user_prompt(match, platform, feedback)}],
            output_format=CaptionDraft,  # Claude must answer in this exact shape
        )
        if response.stop_reason == "refusal" or response.parsed_output is None:
            raise RuntimeError(f"Claude gave no caption (stop_reason={response.stop_reason})")
        return response.parsed_output
