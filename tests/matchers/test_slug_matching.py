"""Tests for slug-based player matching with period normalization."""

from player_universe_trx.matchers.player_matcher import (
    MatchConfidence,
    MatchMethod,
    PlayerMatcher,
)
from player_universe_trx.models.espn import EspnBatterModel
from player_universe_trx.models.fangraphs import FangraphsBatterModel


def test_slug_exact_match():
    """Test that slug matching works with exact slug match."""
    # ESPN player with slug
    espn_player = EspnBatterModel(
        id=12345,
        name="Bobby Witt",
        first_name="Bobby",
        last_name="Witt",
        slug="bobby-witt-jr",
        pro_team="KCR",
    )

    # FanGraphs player with matching slug (no period)
    fg_player = FangraphsBatterModel(
        playerid="54321",
        name="Bobby Witt",
        ascii_name="Bobby Witt",
        slug="bobby-witt-jr",
        team="KCR",
        xmlbam_id=677951,
    )

    matcher = PlayerMatcher([espn_player], [fg_player])
    results = matcher.match_players()

    assert len(results) == 1
    result = results[0]
    assert result.match_method == MatchMethod.SLUG
    assert result.confidence == MatchConfidence.HIGH
    assert result.fangraphs_match == fg_player


def test_slug_period_normalization():
    """Test that slug matching handles period differences (bobby-witt-jr vs bobby-witt-jr.)."""
    # ESPN player with slug (no period)
    espn_player = EspnBatterModel(
        id=12345,
        name="Bobby Witt Jr.",
        first_name="Bobby",
        last_name="Witt",
        slug="bobby-witt-jr",  # No period
        pro_team="KCR",
    )

    # FanGraphs player with slug (with period)
    fg_player = FangraphsBatterModel(
        playerid="54321",
        name="Bobby Witt",
        ascii_name="Bobby Witt",
        slug="bobby-witt-jr.",  # With period
        team="KCR",
        xmlbam_id=677951,
    )

    matcher = PlayerMatcher([espn_player], [fg_player])
    results = matcher.match_players()

    assert len(results) == 1
    result = results[0]
    assert result.match_method == MatchMethod.SLUG
    assert result.confidence == MatchConfidence.HIGH
    assert result.fangraphs_match == fg_player


def test_slug_no_match_falls_back_to_name():
    """Test that when slug doesn't match, it falls back to name matching."""
    # ESPN player with slug
    espn_player = EspnBatterModel(
        id=12345,
        name="Aaron Judge",
        first_name="Aaron",
        last_name="Judge",
        slug="aaron-judge-different",  # Different slug
        pro_team="NYY",
    )

    # FanGraphs player with different slug
    fg_player = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        slug="aaron-judge",  # Different slug
        team="NYY",
        xmlbam_id=592450,
    )

    matcher = PlayerMatcher([espn_player], [fg_player])
    results = matcher.match_players()

    assert len(results) == 1
    result = results[0]
    # Should fall back to name matching
    assert result.match_method == MatchMethod.EXACT_NAME
    assert result.fangraphs_match == fg_player


def test_slug_missing_in_espn():
    """Test that matching works when ESPN player has no slug."""
    # ESPN player without slug
    espn_player = EspnBatterModel(
        id=12345,
        name="Aaron Judge",
        first_name="Aaron",
        last_name="Judge",
        slug=None,  # No slug
        pro_team="NYY",
    )

    # FanGraphs player with slug
    fg_player = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        slug="aaron-judge",
        team="NYY",
        xmlbam_id=592450,
    )

    matcher = PlayerMatcher([espn_player], [fg_player])
    results = matcher.match_players()

    assert len(results) == 1
    result = results[0]
    # Should use name matching instead
    assert result.match_method == MatchMethod.EXACT_NAME
    assert result.fangraphs_match == fg_player


def test_slug_match_faster_than_name():
    """Test that slug matching is tried before name matching (performance test)."""
    # Create a player that would match by both slug and name
    espn_player = EspnBatterModel(
        id=12345,
        name="Shohei Ohtani",
        first_name="Shohei",
        last_name="Ohtani",
        slug="shohei-ohtani",
        pro_team="LAA",
    )

    # Multiple FanGraphs players with same last name (would slow down name matching)
    fg_players = [
        FangraphsBatterModel(
            playerid="19755",
            name="Shohei Ohtani",
            ascii_name="Shohei Ohtani",
            slug="shohei-ohtani",
            team="LAA",
            xmlbam_id=660271,
        ),
        # Other "Ohtani" players (fictional)
        FangraphsBatterModel(
            playerid="99999",
            name="Other Ohtani",
            ascii_name="Other Ohtani",
            slug="other-ohtani",
            team="SEA",
            xmlbam_id=111111,
        ),
    ]

    matcher = PlayerMatcher([espn_player], fg_players)
    results = matcher.match_players()

    assert len(results) == 1
    result = results[0]
    # Should match by slug (faster than checking all "Ohtani" candidates)
    assert result.match_method == MatchMethod.SLUG
    assert result.confidence == MatchConfidence.HIGH
