"""Tests for ESPN stats handling in apply_matches function.

These tests verify that ESPN stats are correctly structured:
- current_season stats are unprefixed at top level
- ESPN stats container is nested under espn_stats field
- All ESPN periods are preserved (projections, last_7/15/30_games, previous_season_24)
"""

from player_universe_trx.matchers.player_matcher import PlayerMatcher, apply_matches
from player_universe_trx.models.espn import EspnBatterModel, EspnPitcherModel
from player_universe_trx.models.espn.batter import EspnBatterStats
from player_universe_trx.models.espn.pitcher import EspnPitcherStats
from player_universe_trx.models.espn.stats import EspnBatterStatsModel, EspnPitcherStatsModel
from player_universe_trx.models.fangraphs import FangraphsBatterModel, FangraphsPitcherModel
from player_universe_trx.models.fangraphs.stats import FangraphsBatterStatsModel, FangraphsPitcherStatsModel
from player_universe_trx.models.savant import SavantBatterModel, SavantPitcherModel
from player_universe_trx.models.savant.batter import SavantBatterStatsModel
from player_universe_trx.models.savant.pitcher import SavantPitcherStatsModel


# ========== Basic Tests - Current Season Only ==========

def test_espn_batter_current_season_only():
    """Test that ESPN current_season stats are unprefixed at top level."""
    espn_player = EspnBatterModel(
        id=1,
        name="Aaron Judge",
        first_name="Aaron",
        last_name="Judge",
        slug="aaron-judge",
        pro_team="NYY",
        stats=EspnBatterStats(
            current_season=EspnBatterStatsModel(
                AB=500,
                H=150,
                HR=30,
                RBI=85,
                AVG=0.300
            )
        )
    )

    fg_player = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        slug="aaron-judge",
        team="NYY"
    )

    matcher = PlayerMatcher([espn_player], [fg_player])
    results = matcher.match_players()
    mtbl_players = apply_matches(results)

    matched = mtbl_players["matched"]
    assert len(matched) == 1

    player = matched[0]
    # Verify current season stats are at top level (unprefixed)
    assert player.stats.AB == 500
    assert player.stats.H == 150
    assert player.stats.HR == 30
    assert player.stats.RBI == 85
    assert player.stats.AVG == 0.300


def test_espn_batter_with_nested_container():
    """Test that ESPN stats container is preserved with all periods."""
    espn_player = EspnBatterModel(
        id=1,
        name="Aaron Judge",
        first_name="Aaron",
        last_name="Judge",
        slug="aaron-judge",
        pro_team="NYY",
        stats=EspnBatterStats(
            current_season=EspnBatterStatsModel(AB=500, H=150, HR=30),
            projections=EspnBatterStatsModel(AB=550, H=165, HR=35),
            last_7_games=EspnBatterStatsModel(AB=28, H=10, HR=3),
            last_15_games=EspnBatterStatsModel(AB=60, H=18, HR=5),
            last_30_games=EspnBatterStatsModel(AB=120, H=38, HR=10),
            previous_season_24=EspnBatterStatsModel(AB=480, H=140, HR=28)
        )
    )

    fg_player = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        slug="aaron-judge",
        team="NYY"
    )

    matcher = PlayerMatcher([espn_player], [fg_player])
    results = matcher.match_players()
    mtbl_players = apply_matches(results)

    matched = mtbl_players["matched"]
    assert len(matched) == 1

    player = matched[0]
    # Verify ESPN stats container is nested
    assert player.stats.espn_stats is not None
    assert player.stats.espn_stats.current_season is not None
    assert player.stats.espn_stats.projections is not None
    assert player.stats.espn_stats.last_7_games is not None
    assert player.stats.espn_stats.last_15_games is not None
    assert player.stats.espn_stats.last_30_games is not None
    assert player.stats.espn_stats.previous_season_24 is not None

    # Verify nested data is correct
    assert player.stats.espn_stats.projections.AB == 550
    assert player.stats.espn_stats.projections.HR == 35
    assert player.stats.espn_stats.last_7_games.HR == 3
    assert player.stats.espn_stats.previous_season_24.AB == 480


def test_espn_batter_both_current_and_nested():
    """Test that both top-level current stats and nested container work together."""
    espn_player = EspnBatterModel(
        id=1,
        name="Aaron Judge",
        first_name="Aaron",
        last_name="Judge",
        slug="aaron-judge",
        pro_team="NYY",
        stats=EspnBatterStats(
            current_season=EspnBatterStatsModel(AB=500, H=150, HR=30),
            projections=EspnBatterStatsModel(AB=550, H=165, HR=35)
        )
    )

    fg_player = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        slug="aaron-judge",
        team="NYY"
    )

    matcher = PlayerMatcher([espn_player], [fg_player])
    results = matcher.match_players()
    mtbl_players = apply_matches(results)

    matched = mtbl_players["matched"]
    player = matched[0]

    # Top-level current season stats
    assert player.stats.AB == 500
    assert player.stats.HR == 30

    # Nested container with projections
    assert player.stats.espn_stats.projections.AB == 550
    assert player.stats.espn_stats.projections.HR == 35

    # Current season also in nested container
    assert player.stats.espn_stats.current_season.AB == 500
    assert player.stats.espn_stats.current_season.HR == 30


def test_espn_pitcher_current_season_only():
    """Test that ESPN pitcher current_season stats are unprefixed at top level."""
    espn_player = EspnPitcherModel(
        id=1,
        name="Gerrit Cole",
        first_name="Gerrit",
        last_name="Cole",
        slug="gerrit-cole",
        pro_team="NYY",
        stats=EspnPitcherStats(
            current_season=EspnPitcherStatsModel(
                W=15,
                L=6,
                ERA=3.15,
                WHIP=1.08,
                K=215
            )
        )
    )

    fg_player = FangraphsPitcherModel(
        playerid="13125",
        name="Gerrit Cole",
        ascii_name="Gerrit Cole",
        slug="gerrit-cole",
        team="NYY"
    )

    matcher = PlayerMatcher([espn_player], [fg_player])
    results = matcher.match_players()
    mtbl_players = apply_matches(results)

    matched = mtbl_players["matched"]
    assert len(matched) == 1

    player = matched[0]
    # Verify current season stats are at top level (unprefixed)
    assert player.stats.W == 15
    assert player.stats.L == 6
    assert player.stats.ERA == 3.15
    assert player.stats.WHIP == 1.08
    assert player.stats.K == 215


def test_espn_pitcher_with_nested_container():
    """Test that ESPN pitcher stats container is preserved with all periods."""
    espn_player = EspnPitcherModel(
        id=1,
        name="Gerrit Cole",
        first_name="Gerrit",
        last_name="Cole",
        slug="gerrit-cole",
        pro_team="NYY",
        stats=EspnPitcherStats(
            current_season=EspnPitcherStatsModel(W=15, K=215, ERA=3.15),
            projections=EspnPitcherStatsModel(W=16, K=225, ERA=3.05),
            last_7_games=EspnPitcherStatsModel(W=2, K=25, ERA=2.50),
            last_15_games=EspnPitcherStatsModel(W=4, K=50, ERA=2.80),
            last_30_games=EspnPitcherStatsModel(W=7, K=105, ERA=3.00),
            previous_season_24=EspnPitcherStatsModel(W=14, K=200, ERA=3.25)
        )
    )

    fg_player = FangraphsPitcherModel(
        playerid="13125",
        name="Gerrit Cole",
        ascii_name="Gerrit Cole",
        slug="gerrit-cole",
        team="NYY"
    )

    matcher = PlayerMatcher([espn_player], [fg_player])
    results = matcher.match_players()
    mtbl_players = apply_matches(results)

    matched = mtbl_players["matched"]
    player = matched[0]

    # Verify ESPN stats container is nested
    assert player.stats.espn_stats is not None
    assert player.stats.espn_stats.projections is not None
    assert player.stats.espn_stats.last_7_games is not None
    assert player.stats.espn_stats.previous_season_24 is not None

    # Verify nested data is correct
    assert player.stats.espn_stats.projections.W == 16
    assert player.stats.espn_stats.last_7_games.ERA == 2.50
    assert player.stats.espn_stats.previous_season_24.K == 200


def test_espn_pitcher_both_current_and_nested():
    """Test that pitcher top-level current stats and nested container work together."""
    espn_player = EspnPitcherModel(
        id=1,
        name="Gerrit Cole",
        first_name="Gerrit",
        last_name="Cole",
        slug="gerrit-cole",
        pro_team="NYY",
        stats=EspnPitcherStats(
            current_season=EspnPitcherStatsModel(W=15, ERA=3.15),
            projections=EspnPitcherStatsModel(W=16, ERA=3.05)
        )
    )

    fg_player = FangraphsPitcherModel(
        playerid="13125",
        name="Gerrit Cole",
        ascii_name="Gerrit Cole",
        slug="gerrit-cole",
        team="NYY"
    )

    matcher = PlayerMatcher([espn_player], [fg_player])
    results = matcher.match_players()
    mtbl_players = apply_matches(results)

    matched = mtbl_players["matched"]
    player = matched[0]

    # Top-level current season stats
    assert player.stats.W == 15
    assert player.stats.ERA == 3.15

    # Nested container with projections
    assert player.stats.espn_stats.projections.W == 16
    assert player.stats.espn_stats.projections.ERA == 3.05


# ========== Integration Tests - All Sources ==========

def test_all_sources_batters_matched():
    """Test combining ESPN current + ESPN container + FG projections + Savant."""
    espn_player = EspnBatterModel(
        id=1,
        name="Aaron Judge",
        first_name="Aaron",
        last_name="Judge",
        slug="aaron-judge",
        pro_team="NYY",
        stats=EspnBatterStats(
            current_season=EspnBatterStatsModel(AB=500, H=150, HR=30, RBI=85),
            projections=EspnBatterStatsModel(AB=550, H=165, HR=35, RBI=95),
            last_7_games=EspnBatterStatsModel(AB=28, HR=3)
        )
    )

    fg_player = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        slug="aaron-judge",
        team="NYY",
        xmlbam_id=592450,
        projection=FangraphsBatterStatsModel(
            ab=575,
            h=170,
            hr=38,
            rbi=100,
            avg=0.296
        )
    )

    savant_player = SavantBatterModel(
        player_id=592450,
        name="Judge, Aaron",
        first_name="Aaron",
        last_name="Judge",
        name_ascii="Aaron Judge",
        slug="aaron-judge",
        pitches=2000,
        total_pitches=2000,
        pitch_percent=100.0,
        stats=SavantBatterStatsModel(
            exit_velo=95.5,
            xwOBA=0.420,
            xAVG=0.310,
            xSLG=0.625
        )
    )

    matcher = PlayerMatcher([espn_player], [fg_player], [savant_player])
    results = matcher.match_players()
    mtbl_players = apply_matches(results)

    matched = mtbl_players["matched"]
    player = matched[0]

    # ESPN current season (top level, unprefixed)
    assert player.stats.AB == 500
    assert player.stats.HR == 30
    assert player.stats.RBI == 85

    # FanGraphs projections (top level, proj_ prefix)
    assert player.stats.proj_ab == 575
    assert player.stats.proj_hr == 38
    assert player.stats.proj_rbi == 100

    # Savant (top level, unprefixed)
    assert player.stats.exit_velo == 95.5
    assert player.stats.xwOBA == 0.420

    # ESPN container (nested)
    assert player.stats.espn_stats.projections.HR == 35
    assert player.stats.espn_stats.last_7_games.HR == 3


def test_all_sources_pitchers_matched():
    """Test combining ESPN current + ESPN container + FG projections + Savant for pitchers."""
    espn_player = EspnPitcherModel(
        id=1,
        name="Gerrit Cole",
        first_name="Gerrit",
        last_name="Cole",
        slug="gerrit-cole",
        pro_team="NYY",
        stats=EspnPitcherStats(
            current_season=EspnPitcherStatsModel(W=15, K=215, ERA=3.15),
            projections=EspnPitcherStatsModel(W=16, K=225, ERA=3.05),
            last_30_games=EspnPitcherStatsModel(W=7, K=105)
        )
    )

    fg_player = FangraphsPitcherModel(
        playerid="13125",
        name="Gerrit Cole",
        ascii_name="Gerrit Cole",
        slug="gerrit-cole",
        team="NYY",
        xmlbam_id=543037,
        projection=FangraphsPitcherStatsModel(
            wins=17,
            strikeouts=230,
            era=3.00,
            whip=1.05
        )
    )

    savant_player = SavantPitcherModel(
        player_id=543037,
        name="Cole, Gerrit",
        first_name="Gerrit",
        last_name="Cole",
        name_ascii="Gerrit Cole",
        slug="gerrit-cole",
        pitches=3000,
        total_pitches=3000,
        pitch_percent=100.0,
        stats=SavantPitcherStatsModel(
            velo=97.2,
            spin_rate=2550,
            xwoba=0.285,
            swing_miss_pct=32.5
        )
    )

    matcher = PlayerMatcher([espn_player], [fg_player], [savant_player])
    results = matcher.match_players()
    mtbl_players = apply_matches(results)

    matched = mtbl_players["matched"]
    player = matched[0]

    # ESPN current season (top level, unprefixed)
    assert player.stats.W == 15
    assert player.stats.K == 215
    assert player.stats.ERA == 3.15

    # FanGraphs projections (top level, proj_ prefix)
    assert player.stats.proj_wins == 17
    assert player.stats.proj_strikeouts == 230
    assert player.stats.proj_era == 3.00

    # Savant (top level, unprefixed)
    assert player.stats.velo == 97.2
    assert player.stats.swing_miss_pct == 32.5

    # ESPN container (nested)
    assert player.stats.espn_stats.projections.W == 16
    assert player.stats.espn_stats.last_30_games.K == 105


def test_espn_stats_unmatched_players():
    """Test that unmatched players preserve ESPN stats correctly."""
    espn_batter = EspnBatterModel(
        id=1,
        name="Unknown Player",
        first_name="Unknown",
        last_name="Player",
        slug="unknown-player",
        pro_team="NYY",
        stats=EspnBatterStats(
            current_season=EspnBatterStatsModel(AB=100, H=25, HR=5),
            projections=EspnBatterStatsModel(AB=400, H=100, HR=20)
        )
    )

    matcher = PlayerMatcher([espn_batter], [], [])
    results = matcher.match_players()
    mtbl_players = apply_matches(results)

    unmatched = mtbl_players["unmatched"]
    assert len(unmatched) == 1

    player = unmatched[0]
    # Current season at top level
    assert player.stats.AB == 100
    assert player.stats.HR == 5

    # ESPN container nested
    assert player.stats.espn_stats.projections.AB == 400
    assert player.stats.espn_stats.projections.HR == 20


# ========== Edge Cases ==========

def test_espn_stats_container_none():
    """Test handling when ESPN stats container is None."""
    espn_player = EspnBatterModel(
        id=1,
        name="Aaron Judge",
        first_name="Aaron",
        last_name="Judge",
        slug="aaron-judge",
        pro_team="NYY",
        stats=None
    )

    fg_player = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        slug="aaron-judge",
        team="NYY"
    )

    matcher = PlayerMatcher([espn_player], [fg_player])
    results = matcher.match_players()
    mtbl_players = apply_matches(results)

    matched = mtbl_players["matched"]
    player = matched[0]

    # Stats should be None when no data from any source
    assert player.stats is None


def test_espn_stats_empty_container():
    """Test handling when ESPN stats container has all fields as None."""
    espn_player = EspnBatterModel(
        id=1,
        name="Aaron Judge",
        first_name="Aaron",
        last_name="Judge",
        slug="aaron-judge",
        pro_team="NYY",
        stats=EspnBatterStats(
            current_season=None,
            projections=None,
            last_7_games=None,
            last_15_games=None,
            last_30_games=None,
            previous_season_24=None
        )
    )

    fg_player = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        slug="aaron-judge",
        team="NYY"
    )

    matcher = PlayerMatcher([espn_player], [fg_player])
    results = matcher.match_players()
    mtbl_players = apply_matches(results)

    matched = mtbl_players["matched"]
    player = matched[0]

    # Should have espn_stats container even if all periods are None
    assert player.stats is not None
    assert player.stats.espn_stats is not None
    assert player.stats.espn_stats.current_season is None
    assert player.stats.espn_stats.projections is None


def test_access_nested_espn_projections():
    """Test that we can access nested ESPN projections through the container."""
    espn_player = EspnBatterModel(
        id=1,
        name="Aaron Judge",
        first_name="Aaron",
        last_name="Judge",
        slug="aaron-judge",
        pro_team="NYY",
        stats=EspnBatterStats(
            current_season=EspnBatterStatsModel(AB=500, AVG=0.300),
            projections=EspnBatterStatsModel(AB=550, AVG=0.310),
            last_7_games=EspnBatterStatsModel(AB=28, AVG=0.357),
            previous_season_24=EspnBatterStatsModel(AB=480, AVG=0.285)
        )
    )

    fg_player = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        slug="aaron-judge",
        team="NYY"
    )

    matcher = PlayerMatcher([espn_player], [fg_player])
    results = matcher.match_players()
    mtbl_players = apply_matches(results)

    matched = mtbl_players["matched"]
    player = matched[0]

    # Access all nested periods
    assert player.stats.espn_stats.current_season.AVG == 0.300
    assert player.stats.espn_stats.projections.AVG == 0.310
    assert player.stats.espn_stats.last_7_games.AVG == 0.357
    assert player.stats.espn_stats.previous_season_24.AVG == 0.285

    # Top level should have current season
    assert player.stats.AVG == 0.300
