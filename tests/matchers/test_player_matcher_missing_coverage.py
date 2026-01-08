import pytest

from player_universe_trx.matchers.models import MatchConfidence, MatchMethod
from player_universe_trx.matchers.player_matcher import PlayerMatcher
from player_universe_trx.models.espn import EspnBatterModel
from player_universe_trx.models.fangraphs import FangraphsBatterModel
from player_universe_trx.models.savant import SavantBatterModel


def test_try_match_by_slug_returns_none_without_slug():
    player = EspnBatterModel(
        id=1,
        name="No Slug",
        first_name="No",
        last_name="Slug",
    )
    matcher = PlayerMatcher([player], [])

    assert matcher._try_match_by_slug(player) is None


def test_try_match_by_slug_skips_already_matched():
    player = EspnBatterModel(
        id=1,
        name="Slugger",
        first_name="Slug",
        last_name="Ger",
        slug="slugger",
    )
    fg_player = FangraphsBatterModel(
        playerid="fg1",
        name="Slugger",
        slug="slugger",
    )
    matcher = PlayerMatcher([player], [fg_player])
    matcher.matched_fg_ids.add("fg1")

    assert matcher._try_match_by_slug(player) is None


def test_try_match_by_slug_savant_already_matched():
    player = EspnBatterModel(
        id=1,
        name="Savant Slugger",
        first_name="Savant",
        last_name="Slugger",
        slug="savant-slugger",
    )
    fg_player = FangraphsBatterModel(
        playerid="fg2",
        name="Savant Slugger",
        slug="savant-slugger",
        xmlbam_id=123,
    )
    savant_player = SavantBatterModel(
        player_id=123,
        name="Slugger, Savant",
        first_name="Savant",
        last_name="Slugger",
        name_ascii="Savant Slugger",
        slug="savant-slugger",
        pitches=1,
        total_pitches=1,
        pitch_percent=1.0,
    )
    matcher = PlayerMatcher([player], [fg_player], [savant_player])
    matcher.matched_savant_ids.add(123)

    result = matcher._try_match_by_slug(player)

    assert result is not None
    assert result.fangraphs_match == fg_player
    assert result.savant_match is None


def test_find_candidates_by_last_name_whitespace_returns_empty():
    player = EspnBatterModel(
        id=1,
        name="Whitespace Player",
        first_name="White",
        last_name="   ",
    )
    fg_player = FangraphsBatterModel(
        playerid="fg3",
        name="Other Player",
    )
    matcher = PlayerMatcher([player], [fg_player])

    assert matcher._find_candidates_by_last_name(player) == []


def test_get_savant_match_skips_already_matched():
    fg_player = FangraphsBatterModel(
        playerid="fg4",
        name="Matched Savant",
        xmlbam_id=555,
    )
    savant_player = SavantBatterModel(
        player_id=555,
        name="Savant, Matched",
        first_name="Matched",
        last_name="Savant",
        name_ascii="Matched Savant",
        slug="matched-savant",
        pitches=1,
        total_pitches=1,
        pitch_percent=1.0,
    )
    matcher = PlayerMatcher([], [fg_player], [savant_player])
    matcher.matched_savant_ids.add(555)

    assert matcher._get_savant_match(fg_player) is None


def test_prefix_match_ambiguous_without_team_disambiguation():
    player = EspnBatterModel(
        id=1,
        name="Rob Smith",
        first_name="Rob",
        last_name="Smith",
        pro_team="LAD",
    )
    fg_player_one = FangraphsBatterModel(
        playerid="1",
        name="Robert Smith",
        ascii_name="Robert Smith",
        team="NYY",
    )
    fg_player_two = FangraphsBatterModel(
        playerid="2",
        name="Roberto Smith",
        ascii_name="Roberto Smith",
        team="BOS",
    )
    matcher = PlayerMatcher([player], [fg_player_one, fg_player_two])
    result = matcher.match_players()[0]

    assert result.match_method == MatchMethod.PREFIX_NAME
    assert result.confidence == MatchConfidence.AMBIGUOUS
    assert len(result.candidates) == 2


def test_match_player_fallback_when_team_matcher_returns_none(monkeypatch):
    player = EspnBatterModel(
        id=1,
        name="Fallback Player",
        first_name="Fallback",
        last_name="Player",
        pro_team="NYY",
    )
    fg_player = FangraphsBatterModel(
        playerid="fg5",
        name="Other Player",
        ascii_name="Other Player",
        team="BOS",
    )
    matcher = PlayerMatcher([player], [fg_player])

    def _return_none(*args, **kwargs):
        return None

    monkeypatch.setattr(matcher, "_try_match_by_team", _return_none)
    result = matcher._match_player(player)

    assert result.match_method == MatchMethod.NONE
    assert result.notes == "No definitive match found"
