"""Tests for ESPN stats handling in apply_matches function.

These tests verify that ESPN stats are correctly structured:
- current_season stats live under stats.current_season
- ESPN stats container is nested under espn_stats field
- All ESPN periods are preserved (projections, last_7/15/30_games, previous_season_24)
"""

from player_universe_trx.matchers.player_matcher import PlayerMatcher
from player_universe_trx.matchers.transformation import apply_matches
from player_universe_trx.models.espn import EspnBatterModel, EspnPitcherModel
from player_universe_trx.models.espn.batter import EspnBatterStatsGroupModel
from player_universe_trx.models.espn.pitcher import EspnPitcherStatsGroupModel
from player_universe_trx.models.espn.stats import (
    EspnBatterStatsModel,
    EspnPitcherStatsModel,
)
from player_universe_trx.models.fangraphs import (
    FangraphsBatterModel,
    FangraphsPitcherModel,
)
from player_universe_trx.models.fangraphs.stats import (
    FangraphsBatterStatsModel,
    FangraphsPitcherStatsModel,
)
from player_universe_trx.models.savant import SavantBatterModel, SavantPitcherModel
from player_universe_trx.models.savant.batter import SavantBatterStatsModel
from player_universe_trx.models.savant.pitcher import SavantPitcherStatsModel

# ========== Basic Tests - Current Season Only ==========


def test_espn_batter_current_season_only():
    """Test that ESPN current_season stats are stored under stats.current_season."""
    espn_player = EspnBatterModel(
        id=1,
        name="Aaron Judge",
        first_name="Aaron",
        last_name="Judge",
        slug="aaron-judge",
        pro_team="NYY",
        stats=EspnBatterStatsGroupModel(
            current_season=EspnBatterStatsModel(AB=500, H=150, HR=30, RBI=85, AVG=0.300)
        ),
    )

    fg_player = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        slug="aaron-judge",
        team="NYY",
    )

    matcher = PlayerMatcher([espn_player], [fg_player])
    results = matcher.match_players()
    mtbl_players = apply_matches(results)

    matched = mtbl_players["matched"]
    assert len(matched) == 1

    player = matched[0]
    # Verify current season stats are nested under current_season
    assert player.stats.current_season.AB == 500
    assert player.stats.current_season.H == 150
    assert player.stats.current_season.HR == 30
    assert player.stats.current_season.RBI == 85
    assert player.stats.current_season.AVG == 0.300


def test_espn_batter_with_nested_container():
    """Test that ESPN stats container is preserved with all periods."""
    espn_player = EspnBatterModel(
        id=1,
        name="Aaron Judge",
        first_name="Aaron",
        last_name="Judge",
        slug="aaron-judge",
        pro_team="NYY",
        stats=EspnBatterStatsGroupModel(
            current_season=EspnBatterStatsModel(AB=500, H=150, HR=30),
            projections=EspnBatterStatsModel(AB=550, H=165, HR=35),
            last_7_games=EspnBatterStatsModel(AB=28, H=10, HR=3),
            last_15_games=EspnBatterStatsModel(AB=60, H=18, HR=5),
            last_30_games=EspnBatterStatsModel(AB=120, H=38, HR=10),
            previous_season_24=EspnBatterStatsModel(AB=480, H=140, HR=28),
        ),
    )

    fg_player = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        slug="aaron-judge",
        team="NYY",
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
    """Test that both current season stats and nested container work together."""
    espn_player = EspnBatterModel(
        id=1,
        name="Aaron Judge",
        first_name="Aaron",
        last_name="Judge",
        slug="aaron-judge",
        pro_team="NYY",
        stats=EspnBatterStatsGroupModel(
            current_season=EspnBatterStatsModel(AB=500, H=150, HR=30),
            projections=EspnBatterStatsModel(AB=550, H=165, HR=35),
        ),
    )

    fg_player = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        slug="aaron-judge",
        team="NYY",
    )

    matcher = PlayerMatcher([espn_player], [fg_player])
    results = matcher.match_players()
    mtbl_players = apply_matches(results)

    matched = mtbl_players["matched"]
    player = matched[0]

    # Current season stats
    assert player.stats.current_season.AB == 500
    assert player.stats.current_season.HR == 30

    # Nested container with projections
    assert player.stats.espn_stats.projections.AB == 550
    assert player.stats.espn_stats.projections.HR == 35

    # Current season also in nested container
    assert player.stats.espn_stats.current_season.AB == 500
    assert player.stats.espn_stats.current_season.HR == 30


def test_espn_pitcher_current_season_only():
    """Test that ESPN pitcher current_season stats are stored under stats.current_season."""
    espn_player = EspnPitcherModel(
        id=1,
        name="Gerrit Cole",
        first_name="Gerrit",
        last_name="Cole",
        slug="gerrit-cole",
        pro_team="NYY",
        stats=EspnPitcherStatsGroupModel(
            current_season=EspnPitcherStatsModel(W=15, L=6, ERA=3.15, WHIP=1.08, K=215)
        ),
    )

    fg_player = FangraphsPitcherModel(
        playerid="13125",
        name="Gerrit Cole",
        ascii_name="Gerrit Cole",
        slug="gerrit-cole",
        team="NYY",
    )

    matcher = PlayerMatcher([espn_player], [fg_player])
    results = matcher.match_players()
    mtbl_players = apply_matches(results)

    matched = mtbl_players["matched"]
    assert len(matched) == 1

    player = matched[0]
    # Verify current season stats are nested under current_season
    assert player.stats.current_season.W == 15
    assert player.stats.current_season.L == 6
    assert player.stats.current_season.ERA == 3.15
    assert player.stats.current_season.WHIP == 1.08
    assert player.stats.current_season.K == 215


def test_espn_pitcher_with_nested_container():
    """Test that ESPN pitcher stats container is preserved with all periods."""
    espn_player = EspnPitcherModel(
        id=1,
        name="Gerrit Cole",
        first_name="Gerrit",
        last_name="Cole",
        slug="gerrit-cole",
        pro_team="NYY",
        stats=EspnPitcherStatsGroupModel(
            current_season=EspnPitcherStatsModel(W=15, K=215, ERA=3.15),
            projections=EspnPitcherStatsModel(W=16, K=225, ERA=3.05),
            last_7_games=EspnPitcherStatsModel(W=2, K=25, ERA=2.50),
            last_15_games=EspnPitcherStatsModel(W=4, K=50, ERA=2.80),
            last_30_games=EspnPitcherStatsModel(W=7, K=105, ERA=3.00),
            previous_season_24=EspnPitcherStatsModel(W=14, K=200, ERA=3.25),
        ),
    )

    fg_player = FangraphsPitcherModel(
        playerid="13125",
        name="Gerrit Cole",
        ascii_name="Gerrit Cole",
        slug="gerrit-cole",
        team="NYY",
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
    """Test that pitcher current season stats and nested container work together."""
    espn_player = EspnPitcherModel(
        id=1,
        name="Gerrit Cole",
        first_name="Gerrit",
        last_name="Cole",
        slug="gerrit-cole",
        pro_team="NYY",
        stats=EspnPitcherStatsGroupModel(
            current_season=EspnPitcherStatsModel(W=15, ERA=3.15),
            projections=EspnPitcherStatsModel(W=16, ERA=3.05),
        ),
    )

    fg_player = FangraphsPitcherModel(
        playerid="13125",
        name="Gerrit Cole",
        ascii_name="Gerrit Cole",
        slug="gerrit-cole",
        team="NYY",
    )

    matcher = PlayerMatcher([espn_player], [fg_player])
    results = matcher.match_players()
    mtbl_players = apply_matches(results)

    matched = mtbl_players["matched"]
    player = matched[0]

    # Current season stats
    assert player.stats.current_season.W == 15
    assert player.stats.current_season.ERA == 3.15

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
        stats=EspnBatterStatsGroupModel(
            current_season=EspnBatterStatsModel(AB=500, H=150, HR=30, RBI=85),
            projections=EspnBatterStatsModel(AB=550, H=165, HR=35, RBI=95),
            last_7_games=EspnBatterStatsModel(AB=28, HR=3),
        ),
    )

    fg_player = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        slug="aaron-judge",
        team="NYY",
        xmlbam_id=592450,
        projections=FangraphsBatterStatsModel(AB=575, H=170, HR=38, RBI=100, AVG=0.296),
    )

    savant_player = SavantBatterModel(
        player_id=592450,
        name="Judge, Aaron",
        first_name="Aaron",
        last_name="Judge",
        name_ascii="Aaron Judge",
        slug="aaron-judge",
        all=SavantBatterStatsModel(
            pitches=2000,
            total_pitches=2000,
            pitch_percent=100.0,
            exit_velo=95.5,
            xwOBA=0.420,
            xAVG=0.310,
            xSLG=0.625,
        ),
    )

    matcher = PlayerMatcher([espn_player], [fg_player], [savant_player])
    results = matcher.match_players()
    mtbl_players = apply_matches(results)

    matched = mtbl_players["matched"]
    player = matched[0]

    # ESPN current season (nested under current_season)
    assert player.stats.current_season.AB == 500
    assert player.stats.current_season.HR == 30
    assert player.stats.current_season.RBI == 85

    # FanGraphs projections (nested under projections)
    assert player.stats.projections.ab == 575
    assert player.stats.projections.hr == 38
    assert player.stats.projections.rbi == 100

    # Savant (nested under current_season, unprefixed)
    assert player.stats.current_season.exit_velo == 95.5
    assert player.stats.current_season.xwOBA == 0.420

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
        stats=EspnPitcherStatsGroupModel(
            current_season=EspnPitcherStatsModel(W=15, K=215, ERA=3.15),
            projections=EspnPitcherStatsModel(W=16, K=225, ERA=3.05),
            last_30_games=EspnPitcherStatsModel(W=7, K=105),
        ),
    )

    fg_player = FangraphsPitcherModel(
        playerid="13125",
        name="Gerrit Cole",
        ascii_name="Gerrit Cole",
        slug="gerrit-cole",
        team="NYY",
        xmlbam_id=543037,
        projections=FangraphsPitcherStatsModel(W=17, SO=230, ERA=3.00, WHIP=1.05),
    )

    savant_player = SavantPitcherModel(
        player_id=543037,
        name="Cole, Gerrit",
        first_name="Gerrit",
        last_name="Cole",
        name_ascii="Gerrit Cole",
        slug="gerrit-cole",
        all=SavantPitcherStatsModel(
            pitches=3000,
            total_pitches=3000,
            pitch_percent=100.0,
            velo=97.2,
            spin_rate=2550,
            xwOBA=0.285,
            swing_miss_pct=32.5,
        ),
    )

    matcher = PlayerMatcher([espn_player], [fg_player], [savant_player])
    results = matcher.match_players()
    mtbl_players = apply_matches(results)

    matched = mtbl_players["matched"]
    player = matched[0]

    # ESPN current season (nested under current_season)
    assert player.stats.current_season.W == 15
    assert player.stats.current_season.K == 215
    assert player.stats.current_season.ERA == 3.15

    # FanGraphs projections (nested under projections)
    assert player.stats.projections.wins == 17
    assert player.stats.projections.strikeouts == 230
    assert player.stats.projections.era == 3.00

    # Savant (nested under current_season, unprefixed)
    assert player.stats.current_season.velo == 97.2
    assert player.stats.current_season.swing_miss_pct == 32.5

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
        stats=EspnBatterStatsGroupModel(
            current_season=EspnBatterStatsModel(AB=100, H=25, HR=5),
            projections=EspnBatterStatsModel(AB=400, H=100, HR=20),
        ),
    )

    matcher = PlayerMatcher([espn_batter], [], [])
    results = matcher.match_players()
    mtbl_players = apply_matches(results)

    unmatched = mtbl_players["unmatched"]
    assert len(unmatched) == 1

    player = unmatched[0]
    # Current season under current_season
    assert player.stats.current_season.AB == 100
    assert player.stats.current_season.HR == 5

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
        stats=None,
    )

    fg_player = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        slug="aaron-judge",
        team="NYY",
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
        stats=EspnBatterStatsGroupModel(
            current_season=None,
            projections=None,
            last_7_games=None,
            last_15_games=None,
            last_30_games=None,
            previous_season_24=None,
        ),
    )

    fg_player = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        slug="aaron-judge",
        team="NYY",
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
        stats=EspnBatterStatsGroupModel(
            current_season=EspnBatterStatsModel(AB=500, AVG=0.300),
            projections=EspnBatterStatsModel(AB=550, AVG=0.310),
            last_7_games=EspnBatterStatsModel(AB=28, AVG=0.357),
            previous_season_24=EspnBatterStatsModel(AB=480, AVG=0.285),
        ),
    )

    fg_player = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        slug="aaron-judge",
        team="NYY",
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

    # Current season should be nested under current_season
    assert player.stats.current_season.AVG == 0.300


# ========== Three-slot FG projections flow into MTBL stats ==========


def test_all_three_fg_projection_slots_land_on_mtbl_batter():
    """The three upstream FG slots end up as siblings under MtblBatterStatsModel."""
    espn_player = EspnBatterModel(
        id=1,
        name="Aaron Judge",
        first_name="Aaron",
        last_name="Judge",
        slug="aaron-judge",
        pro_team="NYY",
        stats=EspnBatterStatsGroupModel(
            current_season=EspnBatterStatsModel(AB=500, HR=30)
        ),
    )

    fg_player = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        slug="aaron-judge",
        team="NYY",
        xmlbam_id=592450,
        projections=FangraphsBatterStatsModel(HR=40, RBI=110, AVG=0.295),
        projs_updated=FangraphsBatterStatsModel(HR=37, RBI=100, AVG=0.288),
        ros=FangraphsBatterStatsModel(HR=12, RBI=32, AVG=0.272),
    )

    results = PlayerMatcher([espn_player], [fg_player]).match_players()
    player = apply_matches(results)["matched"][0]

    assert player.stats.projections is not None
    assert player.stats.projections.hr == 40
    assert player.stats.projs_updated is not None
    assert player.stats.projs_updated.hr == 37
    assert player.stats.ros is not None
    assert player.stats.ros.hr == 12


def test_all_three_fg_projection_slots_land_on_mtbl_pitcher():
    """Same three-slot wiring for pitchers."""
    espn_player = EspnPitcherModel(
        id=1,
        name="Tarik Skubal",
        first_name="Tarik",
        last_name="Skubal",
        slug="tarik-skubal",
        pro_team="DET",
        stats=EspnPitcherStatsGroupModel(
            current_season=EspnPitcherStatsModel(W=15, K=220, ERA=2.80)
        ),
    )

    fg_player = FangraphsPitcherModel(
        playerid="29597",
        name="Tarik Skubal",
        ascii_name="Tarik Skubal",
        slug="tarik-skubal",
        team="DET",
        xmlbam_id=669373,
        projections=FangraphsPitcherStatsModel(W=18, SO=240, ERA=2.95),
        projs_updated=FangraphsPitcherStatsModel(W=16, SO=200, ERA=3.05),
        ros=FangraphsPitcherStatsModel(W=5, SO=70, ERA=3.10),
    )

    results = PlayerMatcher([espn_player], [fg_player]).match_players()
    player = apply_matches(results)["matched"][0]

    assert player.stats.projections is not None
    assert player.stats.projections.wins == 18
    assert player.stats.projs_updated is not None
    assert player.stats.projs_updated.wins == 16
    assert player.stats.ros is not None
    assert player.stats.ros.wins == 5


def test_pre_draft_only_preseason_slot_populated():
    """Pre-draft / pre-publication shape: only `projections` has data; the other
    two FG slots are None on MTBL output. Matches the upstream contract where
    projs_updated and ros serialize as {} until Fangraphs publishes them.
    """
    espn_player = EspnBatterModel(
        id=2,
        name="Corbin Carroll",
        first_name="Corbin",
        last_name="Carroll",
        slug="corbin-carroll",
        pro_team="ARI",
        stats=EspnBatterStatsGroupModel(
            current_season=EspnBatterStatsModel(AB=550, HR=25)
        ),
    )

    fg_player = FangraphsBatterModel(
        playerid="25878",
        name="Corbin Carroll",
        ascii_name="Corbin Carroll",
        slug="corbin-carroll",
        team="ARI",
        xmlbam_id=682998,
        # Only preseason populated; projs_updated/ros omitted (pre-draft)
        projections=FangraphsBatterStatsModel(HR=30, SB=40, AVG=0.285),
    )

    results = PlayerMatcher([espn_player], [fg_player]).match_players()
    player = apply_matches(results)["matched"][0]

    assert player.stats.projections is not None
    assert player.stats.projections.hr == 30
    assert player.stats.projs_updated is None
    assert player.stats.ros is None


def test_fg_match_with_empty_slot_dicts_yields_none_on_mtbl():
    """An FG match where projs_updated/ros are non-None but model_dump to {}
    (the round-tripped pre-draft shape) should still produce None for those
    slots on the MTBL container — empty data is not data.
    """
    espn_player = EspnBatterModel(
        id=3,
        name="Empty Slots Hitter",
        first_name="Empty",
        last_name="Slots",
        slug="empty-slots",
        pro_team="FA",
        stats=EspnBatterStatsGroupModel(
            current_season=EspnBatterStatsModel(AB=400)
        ),
    )

    # Build the FG model via dict load — mimics what happens when reading
    # upstream JSON with literal `{}` for the two empty slots.
    fg_player = FangraphsBatterModel.model_validate(
        {
            "playerid": "empty-1",
            "name": "Empty Slots Hitter",
            "ascii_name": "Empty Slots Hitter",
            "slug": "empty-slots",
            "team": "FA",
            "projections": {"HR": 20},
            "projs_updated": {},
            "ros": {},
        }
    )

    results = PlayerMatcher([espn_player], [fg_player]).match_players()
    player = apply_matches(results)["matched"][0]

    assert player.stats.projections is not None
    assert player.stats.projections.hr == 20
    # Empty dicts on the wire → None on the typed MTBL output
    assert player.stats.projs_updated is None
    assert player.stats.ros is None


def test_ambiguous_match_zero_projection_slots():
    """An ambiguous match contributes none of the three FG slots."""
    from player_universe_trx.matchers.transformation.apply_matches import (
        _extract_fangraphs_projections,
    )

    # Direct extractor check: None input → all three slots empty
    result = _extract_fangraphs_projections(None)
    assert result == {"projections": {}, "projs_updated": {}, "ros": {}}


# ========== Three-split Savant data flows into MTBL ==========


def test_savant_vs_r_and_vs_l_land_on_mtbl_batter():
    """Savant vs_r/vs_l splits flow into typed MTBL fields; `all` still feeds current_season."""
    espn_player = EspnBatterModel(
        id=1,
        name="Aaron Judge",
        first_name="Aaron",
        last_name="Judge",
        slug="aaron-judge",
        pro_team="NYY",
        stats=EspnBatterStatsGroupModel(
            current_season=EspnBatterStatsModel(AB=500, HR=30)
        ),
    )

    fg_player = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        slug="aaron-judge",
        team="NYY",
        xmlbam_id=592450,
    )

    savant_player = SavantBatterModel(
        player_id=592450,
        name="Judge, Aaron",
        first_name="Aaron",
        last_name="Judge",
        name_ascii="Aaron Judge",
        slug="aaron-judge",
        season=2026,
        all=SavantBatterStatsModel(xwOBA=0.420, exit_velo=95.5),
        vs_r=SavantBatterStatsModel(xwOBA=0.430, exit_velo=96.2),
        vs_l=SavantBatterStatsModel(xwOBA=0.395, exit_velo=93.8),
    )

    results = PlayerMatcher(
        [espn_player], [fg_player], [savant_player]
    ).match_players()
    player = apply_matches(results)["matched"][0]

    # `all` continues to fold into current_season (preserves prior contract)
    assert player.stats.current_season.xwOBA == 0.420
    assert player.stats.current_season.exit_velo == 95.5

    # vs_r / vs_l land on new typed fields
    assert player.stats.savant_vs_r is not None
    assert player.stats.savant_vs_r.xwOBA == 0.430
    assert player.stats.savant_vs_r.exit_velo == 96.2
    assert player.stats.savant_vs_l is not None
    assert player.stats.savant_vs_l.xwOBA == 0.395
    assert player.stats.savant_vs_l.exit_velo == 93.8


def test_savant_vs_r_and_vs_l_land_on_mtbl_pitcher():
    """Pitcher counterpart: vs_r/vs_l splits flow into MtblPitcherStatsModel."""
    espn_player = EspnPitcherModel(
        id=1,
        name="Tarik Skubal",
        first_name="Tarik",
        last_name="Skubal",
        slug="tarik-skubal",
        pro_team="DET",
        stats=EspnPitcherStatsGroupModel(
            current_season=EspnPitcherStatsModel(W=15, K=220, ERA=2.80)
        ),
    )

    fg_player = FangraphsPitcherModel(
        playerid="29597",
        name="Tarik Skubal",
        ascii_name="Tarik Skubal",
        slug="tarik-skubal",
        team="DET",
        xmlbam_id=669373,
    )

    savant_player = SavantPitcherModel(
        player_id=669373,
        name="Skubal, Tarik",
        first_name="Tarik",
        last_name="Skubal",
        name_ascii="Tarik Skubal",
        slug="tarik-skubal",
        season=2026,
        all=SavantPitcherStatsModel(velo=97.0, spin_rate=2500, xwOBA=0.260),
        vs_r=SavantPitcherStatsModel(velo=97.3, spin_rate=2510, xwOBA=0.250),
        vs_l=SavantPitcherStatsModel(velo=96.4, spin_rate=2480, xwOBA=0.285),
    )

    results = PlayerMatcher(
        [espn_player], [fg_player], [savant_player]
    ).match_players()
    player = apply_matches(results)["matched"][0]

    # `all` still feeds current_season
    assert player.stats.current_season.velo == 97.0
    assert player.stats.current_season.xwOBA == 0.260

    # New split fields populated
    assert player.stats.savant_vs_r is not None
    assert player.stats.savant_vs_r.velo == 97.3
    assert player.stats.savant_vs_l is not None
    assert player.stats.savant_vs_l.xwOBA == 0.285


def test_savant_partial_coverage_only_all_split_yields_none_split_fields():
    """Player with only the `all` Savant split: savant_vs_r/savant_vs_l are None."""
    espn_player = EspnBatterModel(
        id=2,
        name="Lefty-Free Hitter",
        first_name="Lefty-Free",
        last_name="Hitter",
        slug="lefty-free-hitter",
        pro_team="FA",
        stats=EspnBatterStatsGroupModel(
            current_season=EspnBatterStatsModel(AB=300, HR=10)
        ),
    )

    fg_player = FangraphsBatterModel(
        playerid="lfh-1",
        name="Lefty-Free Hitter",
        ascii_name="Lefty-Free Hitter",
        slug="lefty-free-hitter",
        team="FA",
        xmlbam_id=900001,
    )

    savant_player = SavantBatterModel(
        player_id=900001,
        name="Hitter, Lefty-Free",
        first_name="Lefty-Free",
        last_name="Hitter",
        name_ascii="Lefty-Free Hitter",
        slug="lefty-free-hitter",
        season=2026,
        all=SavantBatterStatsModel(xwOBA=0.320),
        # vs_r/vs_l intentionally omitted
    )

    results = PlayerMatcher(
        [espn_player], [fg_player], [savant_player]
    ).match_players()
    player = apply_matches(results)["matched"][0]

    assert player.stats.current_season.xwOBA == 0.320
    assert player.stats.savant_vs_r is None
    assert player.stats.savant_vs_l is None


def test_extract_savant_splits_none_input():
    """The extractor returns empty slot dicts when there is no Savant match."""
    from player_universe_trx.matchers.transformation.apply_matches import (
        _extract_savant_splits,
    )

    assert _extract_savant_splits(None) == {"vs_r": {}, "vs_l": {}}


def test_extract_savant_stats_reads_all_split():
    """Regression guard: _extract_savant_stats sources `current_season` from `all`."""
    from player_universe_trx.matchers.transformation.apply_matches import (
        _extract_savant_stats,
    )

    sm = SavantBatterModel(
        player_id=42,
        name="A, B",
        first_name="A",
        last_name="B",
        name_ascii="A B",
        slug="a-b",
        season=2026,
        all=SavantBatterStatsModel(xwOBA=0.350),
        vs_r=SavantBatterStatsModel(xwOBA=0.999),  # would be wrong if read
    )

    out = _extract_savant_stats(sm)
    assert out["xwOBA"] == 0.350  # from `all`, not `vs_r`
    assert out["savant_player_id"] == 42
    assert out["savant_player_type"] == "batter"
    assert out["savant_season"] == 2026
