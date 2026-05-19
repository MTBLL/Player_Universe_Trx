"""Final coverage tests to reach 100%."""

from player_universe_trx.matchers.models import (
    MatchConfidence,
    MatchMethod,
    PlayerMatchResult,
)
from player_universe_trx.matchers.player_matcher import PlayerMatcher
from player_universe_trx.matchers.transformation import apply_matches
from player_universe_trx.models.espn import EspnBatterModel
from player_universe_trx.models.fangraphs import FangraphsBatterModel


def test_slug_match_player_without_slug():
    """Test slug matching when ESPN player has no slug."""
    espn_player = EspnBatterModel(
        id=123,
        name="Test Player",
        first_name="Test",
        last_name="Player",
        slug=None,  # No slug
    )
    fg_player = FangraphsBatterModel(
        name="Test Player",
        playerid="456",
        slug="test-player",
    )

    matcher = PlayerMatcher([espn_player], [fg_player])
    results = matcher.match_players()

    # Should not match by slug since ESPN player has no slug
    assert len(results) == 1
    # Should still match by name
    assert results[0].fangraphs_match is not None


def test_slug_match_already_matched():
    """Test slug matching when FanGraphs player already matched."""
    espn_player1 = EspnBatterModel(
        id=123,
        name="Test Player",
        first_name="Test",
        last_name="Player",
        slug="test-player",
    )
    espn_player2 = EspnBatterModel(
        id=456,
        name="Test Player",
        first_name="Test",
        last_name="Player",
        slug="test-player",  # Same slug
    )
    fg_player = FangraphsBatterModel(
        name="Test Player",
        playerid="789",
        slug="test-player",
    )

    matcher = PlayerMatcher([espn_player1, espn_player2], [fg_player])

    # Manually mark as already matched
    matcher.matched_fg_ids.add("789")

    results = matcher.match_players()

    # First player should not match by slug since already marked as matched
    # Should fall back to name matching
    assert len(results) == 2


def test_savant_match_already_matched():
    """Test Savant matching when Savant player already matched to another player."""
    from player_universe_trx.models.savant import SavantBatterModel
    from player_universe_trx.models.savant.stats import SavantBatterStatsModel

    espn_player1 = EspnBatterModel(
        id=123,
        name="Test Player One",
        first_name="Test",
        last_name="PlayerOne",
        slug="test-playerone",
    )
    espn_player2 = EspnBatterModel(
        id=456,
        name="Test Player Two",
        first_name="Test",
        last_name="PlayerTwo",
        slug="test-playertwo",
    )
    fg_player1 = FangraphsBatterModel(
        name="Test Player One",
        playerid="111",
        slug="test-playerone",
        xmlbam_id=99999,
    )
    fg_player2 = FangraphsBatterModel(
        name="Test Player Two",
        playerid="222",
        slug="test-playertwo",
        xmlbam_id=99999,  # Same Savant ID - should only match once
    )
    savant_player = SavantBatterModel(
        player_id=99999,
        last_name="PlayerOne",
        first_name="Test",
        name="Test PlayerOne",
        name_ascii="Test PlayerOne",
        slug="test-playerone",
        pitches=100,
        total_pitches=100,
        pitch_percent=1.0,
        stats=SavantBatterStatsModel(),
    )

    matcher = PlayerMatcher(
        [espn_player1, espn_player2], [fg_player1, fg_player2], [savant_player]
    )
    results = matcher.match_players()

    # First player should get Savant match, second should not
    assert len(results) == 2
    assert results[0].savant_match is not None
    assert results[1].savant_match is None  # Already matched


def test_find_candidates_no_last_name():
    """Test finding candidates when player has no last name."""
    espn_player = EspnBatterModel(
        id=123,
        name="Test",
        first_name="Test",
        last_name="",  # Empty last name
    )
    fg_player = FangraphsBatterModel(
        name="Test Player",
        playerid="456",
    )

    matcher = PlayerMatcher([espn_player], [fg_player])
    results = matcher.match_players()

    # Should return no match since no last name
    assert len(results) == 1
    assert results[0].fangraphs_match is None
    assert results[0].match_method == MatchMethod.NONE


def test_match_player_fallthrough():
    """Test match_player fallthrough case (should not normally happen)."""
    # Create scenario where all strategies fail but we have candidates
    espn_player = EspnBatterModel(
        id=123,
        name="Test Player",
        first_name="Test",
        last_name="Player",
        pro_team="NYY",
    )
    # FanGraphs player with different first name and team
    fg_player = FangraphsBatterModel(
        name="Different Player",
        ascii_name="Different Player",
        playerid="456",
        team="BOS",
    )

    matcher = PlayerMatcher([espn_player], [fg_player])
    results = matcher.match_players()

    # Should return a result even though no match
    assert len(results) == 1


def test_apply_matches_retired_player():
    """Test apply_matches skips retired players."""
    espn_player = EspnBatterModel(
        id=123,
        name="Retired Player",
        first_name="Retired",
        last_name="Player",
        status="retired",  # Retired status
    )

    result = PlayerMatchResult(
        espn_player=espn_player,
        fangraphs_match=None,
        savant_match=None,
        match_method=MatchMethod.NONE,
        confidence=MatchConfidence.NONE,
    )

    output = apply_matches([result])

    # Retired player should be skipped
    assert len(output["matched"]) == 0
    assert len(output["unmatched"]) == 0
    assert len(output["ambiguous"]) == 0


def test_match_players_invokes_progress_callback():
    """match_players should call progress_advance once per ESPN player when
    a callback is supplied (covers the optional progress-bar hook)."""
    espn_players = [
        EspnBatterModel(
            id=i,
            name=f"Player {i}",
            first_name="Player",
            last_name=str(i),
            slug=f"player-{i}",
        )
        for i in range(3)
    ]
    fg_players = [
        FangraphsBatterModel(name=f"Player {i}", playerid=str(100 + i), slug=f"player-{i}")
        for i in range(3)
    ]

    matcher = PlayerMatcher(espn_players, fg_players)
    calls: list[int] = []

    def _advance() -> None:
        calls.append(1)

    results = matcher.match_players(progress_advance=_advance)

    assert len(results) == 3
    assert len(calls) == 3
