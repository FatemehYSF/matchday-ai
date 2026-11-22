import json
from pathlib import Path

from .models import Match


def load_matches(path: str) -> list[Match]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Match.model_validate(item) for item in raw]
