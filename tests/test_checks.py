from matchday.checks import (
    check_hashtags,
    check_length,
    check_players,
    check_safe_language,
    check_score,
    check_teams,
)
from matchday.models import PLATFORMS, CaptionDraft, Match


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


def test_missing_team_fails():
    draft = CaptionDraft(caption="Ajax win 2-1!", hashtags=["#Ajax"])
    result = check_teams(make_match(), draft)
    assert not result.passed
    assert "PSV" in result.detail


def test_player_who_did_not_score_fails():
    draft = CaptionDraft(caption="Ajax 2-1 PSV, Kylian Mbappé watching", hashtags=["#Ajax"])
    assert not check_players(make_match(), draft, {"Kylian Mbappé"}).passed


def test_too_many_hashtags_fails():
    draft = CaptionDraft(caption="x", hashtags=["#a", "#b", "#c"])
    assert not check_hashtags(draft, PLATFORMS["x"]).passed


def test_banned_word_fails():
    draft = CaptionDraft(caption="What a useless defence", hashtags=["#Ajax"])
    assert not check_safe_language(draft).passed


def test_short_caption_passes():
    draft = CaptionDraft(caption="Ajax 2-1 PSV", hashtags=["#Ajax"])   # 1. put in: a SHORT caption
    assert check_length(draft, PLATFORMS["tiktok"]).passed            # 3. check: it must PASS


def test_long_caption_fails():
    draft = CaptionDraft(caption="A" * 200, hashtags=["#Ajax"])
    assert not check_length(draft, PLATFORMS["tiktok"]).passed
