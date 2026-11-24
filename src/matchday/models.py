from pydantic import BaseModel, Field
from dataclasses import dataclass


class Goal(BaseModel):
    player: str
    team: str
    minute: int = Field(ge=1, le=130)


class Match(BaseModel):
    match_id: str
    competition: str
    home_team: str
    away_team: str
    home_score: int = Field(ge=0)
    away_score: int = Field(ge=0)
    goals: list[Goal] = []

    @property
    def scoreline(self) -> str:
        return f"{self.home_team} {self.home_score}-{self.away_score} {self.away_team}"

    @property
    def scorers(self) -> set[str]:
        return {goal.player for goal in self.goals}


class CaptionDraft(BaseModel):
    """The exact shape the LLM must answer in."""
    caption: str = Field(description="The caption text, without hashtags")
    hashtags: list[str] = Field(description="2 to 4 hashtags, each starting with #")


@dataclass(frozen=True)
class Platform:
    name: str
    max_chars: int
    max_hashtags: int
    style: str

PLATFORMS = {
    "instagram": Platform("instagram", 300, 4, "Energetic, 1-3 short sentences, up to 2 emojis, end with a question to fans."),
    "tiktok": Platform("tiktok", 150, 3, "Very short and punchy. One emoji maximum."),
    "x": Platform("x", 280, 2, "Breaking-news style. Lead with the score. No emojis."),
}


class CheckResult(BaseModel):
    name: str
    passed: bool
    detail: str = ""
