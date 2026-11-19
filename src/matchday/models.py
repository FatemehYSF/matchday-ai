from pydantic import BaseModel, Field


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
