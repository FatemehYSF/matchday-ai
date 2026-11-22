from matchday.checks import check_score
from matchday.models import CaptionDraft, Match


def make_match() -> Match:
    return Match(
        match_id="t1", competition="Eredivisie",
        home_team="Ajax", away_team="PSV",
        home_score=2, away_score=1,
    )


def test_correct_score_passes():
    draft = CaptionDraft(caption="FULL TIME: Ajax 2-1 PSV", hashtags=["#Ajax"])
    assert check_score(make_match(), draft).passed


def test_swapped_score_fails():
    draft = CaptionDraft(caption="FULL TIME: Ajax 1-2 PSV", hashtags=["#Ajax"])
    assert not check_score(make_match(), draft).passed
