"""Tests for ESPN stats handling in apply_matches function.

These tests verify that ESPN stats are correctly structured:
- current_season stats live under stats.current_season
- ESPN stats container is nested under espn_stats field
- All ESPN periods are preserved (projections, last_7/15/30_games, previous_season)
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
    assert player.stats.espn.current_season.AB == 500
    assert player.stats.espn.current_season.H == 150
    assert player.stats.espn.current_season.HR == 30
    assert player.stats.espn.current_season.RBI == 85
    assert player.stats.espn.current_season.AVG == 0.300


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
            previous_season=EspnBatterStatsModel(AB=480, H=140, HR=28),
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
    assert player.stats.espn is not None
    assert player.stats.espn.current_season is not None
    assert player.stats.espn.projections is not None
    assert player.stats.espn.last_7_games is not None
    assert player.stats.espn.last_15_games is not None
    assert player.stats.espn.last_30_games is not None
    assert player.stats.espn.previous_season is not None

    # Verify nested data is correct
    assert player.stats.espn.projections.AB == 550
    assert player.stats.espn.projections.HR == 35
    assert player.stats.espn.last_7_games.HR == 3
    assert player.stats.espn.previous_season.AB == 480


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
    assert player.stats.espn.current_season.AB == 500
    assert player.stats.espn.current_season.HR == 30

    # Nested container with projections
    assert player.stats.espn.projections.AB == 550
    assert player.stats.espn.projections.HR == 35

    # Current season also in nested container
    assert player.stats.espn.current_season.AB == 500
    assert player.stats.espn.current_season.HR == 30


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
    assert player.stats.espn.current_season.W == 15
    assert player.stats.espn.current_season.L == 6
    assert player.stats.espn.current_season.ERA == 3.15
    assert player.stats.espn.current_season.WHIP == 1.08
    assert player.stats.espn.current_season.K == 215


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
            previous_season=EspnPitcherStatsModel(W=14, K=200, ERA=3.25),
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
    assert player.stats.espn is not None
    assert player.stats.espn.projections is not None
    assert player.stats.espn.last_7_games is not None
    assert player.stats.espn.previous_season is not None

    # Verify nested data is correct
    assert player.stats.espn.projections.W == 16
    assert player.stats.espn.last_7_games.ERA == 2.50
    assert player.stats.espn.previous_season.K == 200


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
    assert player.stats.espn.current_season.W == 15
    assert player.stats.espn.current_season.ERA == 3.15

    # Nested container with projections
    assert player.stats.espn.projections.W == 16
    assert player.stats.espn.projections.ERA == 3.05


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
    assert player.stats.espn.current_season.AB == 500
    assert player.stats.espn.current_season.HR == 30
    assert player.stats.espn.current_season.RBI == 85

    # FanGraphs projections (nested under projections)
    assert player.stats.fangraphs.projections.ab == 575
    assert player.stats.fangraphs.projections.hr == 38
    assert player.stats.fangraphs.projections.rbi == 100

    # Savant (under its own bundle now — no merge into current_season)
    assert player.stats.savant is not None
    assert player.stats.savant.all is not None
    assert player.stats.savant.all.exit_velo == 95.5
    assert player.stats.savant.all.xwOBA == 0.420

    # ESPN container (nested)
    assert player.stats.espn.projections.HR == 35
    assert player.stats.espn.last_7_games.HR == 3


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
    assert player.stats.espn.current_season.W == 15
    assert player.stats.espn.current_season.K == 215
    assert player.stats.espn.current_season.ERA == 3.15

    # FanGraphs projections (nested under projections)
    assert player.stats.fangraphs.projections.wins == 17
    assert player.stats.fangraphs.projections.strikeouts == 230
    assert player.stats.fangraphs.projections.era == 3.00

    # Savant (under its own bundle now — no merge into current_season)
    assert player.stats.savant is not None
    assert player.stats.savant.all is not None
    assert player.stats.savant.all.velo == 97.2
    assert player.stats.savant.all.swing_miss_pct == 32.5

    # ESPN container (nested)
    assert player.stats.espn.projections.W == 16
    assert player.stats.espn.last_30_games.K == 105


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
    assert player.stats.espn.current_season.AB == 100
    assert player.stats.espn.current_season.HR == 5

    # ESPN container nested
    assert player.stats.espn.projections.AB == 400
    assert player.stats.espn.projections.HR == 20


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
            previous_season=None,
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
    assert player.stats.espn is not None
    assert player.stats.espn.current_season is None
    assert player.stats.espn.projections is None


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
            previous_season=EspnBatterStatsModel(AB=480, AVG=0.285),
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
    assert player.stats.espn.current_season.AVG == 0.300
    assert player.stats.espn.projections.AVG == 0.310
    assert player.stats.espn.last_7_games.AVG == 0.357
    assert player.stats.espn.previous_season.AVG == 0.285

    # Current season should be nested under current_season
    assert player.stats.espn.current_season.AVG == 0.300


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

    assert player.stats.fangraphs.projections is not None
    assert player.stats.fangraphs.projections.hr == 40
    assert player.stats.fangraphs.projs_updated is not None
    assert player.stats.fangraphs.projs_updated.hr == 37
    assert player.stats.fangraphs.ros is not None
    assert player.stats.fangraphs.ros.hr == 12


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

    assert player.stats.fangraphs.projections is not None
    assert player.stats.fangraphs.projections.wins == 18
    assert player.stats.fangraphs.projs_updated is not None
    assert player.stats.fangraphs.projs_updated.wins == 16
    assert player.stats.fangraphs.ros is not None
    assert player.stats.fangraphs.ros.wins == 5


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

    assert player.stats.fangraphs.projections is not None
    assert player.stats.fangraphs.projections.hr == 30
    assert player.stats.fangraphs.projs_updated is None
    assert player.stats.fangraphs.ros is None


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

    assert player.stats.fangraphs.projections is not None
    assert player.stats.fangraphs.projections.hr == 20
    # Empty dicts on the wire → None on the typed MTBL output
    assert player.stats.fangraphs.projs_updated is None
    assert player.stats.fangraphs.ros is None


def test_build_fangraphs_bundle_none_input():
    """The FG bundle builder returns None when there's no FG match."""
    from player_universe_trx.matchers.transformation.apply_matches import (
        _build_fangraphs_bundle,
    )

    assert _build_fangraphs_bundle(None, is_batter=True) is None
    assert _build_fangraphs_bundle(None, is_batter=False) is None


# ========== Three-split Savant data flows into MTBL ==========


def test_savant_bundle_carries_all_three_splits_for_batter():
    """All three Savant splits live under the nested MTBL bundle; `all` also folds into current_season."""
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

    # All three splits live under the savant bundle (no merge into ESPN
    # current_season after the source-namespace cleanup).
    assert player.stats.savant is not None
    assert player.stats.savant.all is not None
    assert player.stats.savant.all.xwOBA == 0.420
    assert player.stats.savant.all.exit_velo == 95.5
    assert player.stats.savant.vs_r is not None
    assert player.stats.savant.vs_r.xwOBA == 0.430
    assert player.stats.savant.vs_r.exit_velo == 96.2
    assert player.stats.savant.vs_l is not None
    assert player.stats.savant.vs_l.xwOBA == 0.395


def test_savant_bundle_carries_all_three_splits_for_pitcher():
    """Pitcher counterpart of the batter bundle test."""
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

    # All three splits live under the savant bundle (no merge into ESPN
    # current_season after the source-namespace cleanup).
    assert player.stats.savant is not None
    assert player.stats.savant.all is not None
    assert player.stats.savant.all.velo == 97.0
    assert player.stats.savant.all.xwOBA == 0.260
    assert player.stats.savant.vs_r is not None
    assert player.stats.savant.vs_r.velo == 97.3
    assert player.stats.savant.vs_l is not None
    assert player.stats.savant.vs_l.xwOBA == 0.285


def test_savant_bundle_partial_coverage_only_all_split():
    """Player with only the `all` split: bundle.vs_r and bundle.vs_l stay None."""
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

    # Savant `all` populated; vs_r/vs_l absent → bundle has all set, splits None
    assert player.stats.savant is not None
    assert player.stats.savant.all is not None
    assert player.stats.savant.all.xwOBA == 0.320
    assert player.stats.savant.vs_r is None
    assert player.stats.savant.vs_l is None


def test_build_savant_bundle_none_input():
    """The bundle builder returns None when there's no Savant match."""
    from player_universe_trx.matchers.transformation.apply_matches import (
        _build_savant_bundle,
    )

    assert _build_savant_bundle(None, is_batter=True) is None
    assert _build_savant_bundle(None, is_batter=False) is None


def test_build_savant_bundle_empty_match_returns_none():
    """An identity-only Savant match with every field None coerces to None — both roles."""
    from player_universe_trx.matchers.transformation.apply_matches import (
        _build_savant_bundle,
    )

    empty_batter = SavantBatterModel(
        player_id=1,
        name="Empty, Match",
        first_name="Empty",
        last_name="Match",
        name_ascii="Empty Match",
        slug="empty-match",
        # all/vs_r/vs_l/statcast/home_runs/pitch_arsenal/sprint_speed all default
    )
    assert _build_savant_bundle(empty_batter, is_batter=True) is None

    empty_pitcher = SavantPitcherModel(
        player_id=2,
        name="Empty, Pitcher",
        first_name="Empty",
        last_name="Pitcher",
        name_ascii="Empty Pitcher",
        slug="empty-pitcher",
    )
    assert _build_savant_bundle(empty_pitcher, is_batter=False) is None


def test_savant_bundle_isolates_each_split():
    """Regression guard: bundle.all, bundle.vs_r, bundle.vs_l are independent objects.

    Replaces the old `_extract_savant_stats reads from .all` regression — that
    function was deleted in the source-namespace cleanup (no more merge into
    current_season). The equivalent guard now is that `bundle.all` carries the
    overall numbers and `bundle.vs_r` / `bundle.vs_l` carry distinct per-split
    numbers — they don't bleed into each other.
    """
    from player_universe_trx.matchers.transformation.apply_matches import (
        _build_savant_bundle,
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
        vs_r=SavantBatterStatsModel(xwOBA=0.999),
        vs_l=SavantBatterStatsModel(xwOBA=0.250),
    )

    bundle = _build_savant_bundle(sm, is_batter=True)
    assert bundle is not None
    assert bundle.all is not None and bundle.all.xwOBA == 0.350
    assert bundle.vs_r is not None and bundle.vs_r.xwOBA == 0.999
    assert bundle.vs_l is not None and bundle.vs_l.xwOBA == 0.250


# ========== Savant bundle sub-domains end-to-end ==========


def test_savant_bundle_carries_batter_sub_domains():
    """All five batter sub-domains (statcast, home_runs, pitch_arsenal, sprint_speed, swing_take) reach the bundle."""
    from player_universe_trx.models.savant import (
        SavantHomeRunsModel,
        SavantPitchArsenalEntryModel,
        SavantSprintSpeedModel,
        SavantStatcastModel,
        SavantSwingTakeModel,
    )

    espn_player = EspnBatterModel(
        id=10,
        name="Mike Trout",
        first_name="Mike",
        last_name="Trout",
        slug="mike-trout",
        pro_team="LAA",
        stats=EspnBatterStatsGroupModel(
            current_season=EspnBatterStatsModel(AB=500, HR=20)
        ),
    )
    fg_player = FangraphsBatterModel(
        playerid="10155",
        name="Mike Trout",
        ascii_name="Mike Trout",
        slug="mike-trout",
        team="LAA",
        xmlbam_id=545361,
    )
    savant_player = SavantBatterModel(
        player_id=545361,
        name="Trout, Mike",
        first_name="Mike",
        last_name="Trout",
        name_ascii="Mike Trout",
        slug="mike-trout",
        season=2026,
        all=SavantBatterStatsModel(xwOBA=0.380),
        statcast=SavantStatcastModel(bbe=120, avg_ev=91.7, ev50=98.0, barrels=12),
        home_runs=SavantHomeRunsModel(
            year=2026, hr_type="adj_xhr", HR=11, xHR=12.5, no_doubters=4
        ),
        pitch_arsenal=[
            SavantPitchArsenalEntryModel(pitch_type="FF", pitches=371, xwOBA=0.46),
            SavantPitchArsenalEntryModel(pitch_type="SL", pitches=78, xwOBA=0.369),
        ],
        sprint_speed=SavantSprintSpeedModel(position="CF", sprint_speed=28.7, age=33),
        swing_take=SavantSwingTakeModel(
            runs_all=15.2, runs_heart=3.1, runs_shadow=7.8, runs_chase=2.9, runs_waste=1.4
        ),
    )

    results = PlayerMatcher(
        [espn_player], [fg_player], [savant_player]
    ).match_players()
    player = apply_matches(results)["matched"][0]

    b = player.stats.savant
    assert b is not None
    assert b.statcast is not None and b.statcast.avg_ev == 91.7
    assert b.home_runs is not None and b.home_runs.HR == 11 and b.home_runs.xHR == 12.5
    assert len(b.pitch_arsenal) == 2
    assert {e.pitch_type for e in b.pitch_arsenal} == {"FF", "SL"}
    assert b.sprint_speed is not None and b.sprint_speed.sprint_speed == 28.7
    assert b.swing_take is not None
    assert b.swing_take.runs_all == 15.2
    assert b.swing_take.runs_shadow == 7.8


def test_savant_bundle_carries_pitcher_sub_domains():
    """All five pitcher sub-domains reach the bundle (expected_statistics replaces sprint_speed; swing_take is shared)."""
    from player_universe_trx.models.savant import (
        SavantHomeRunsModel,
        SavantPitcherExpectedStatsModel,
        SavantPitchArsenalEntryModel,
        SavantStatcastModel,
        SavantSwingTakeModel,
    )

    espn_player = EspnPitcherModel(
        id=11,
        name="Sandy Alcantara",
        first_name="Sandy",
        last_name="Alcantara",
        slug="sandy-alcantara",
        pro_team="MIA",
        stats=EspnPitcherStatsGroupModel(
            current_season=EspnPitcherStatsModel(W=10, K=150, ERA=3.50)
        ),
    )
    fg_player = FangraphsPitcherModel(
        playerid="22182",
        name="Sandy Alcantara",
        ascii_name="Sandy Alcantara",
        slug="sandy-alcantara",
        team="MIA",
        xmlbam_id=645261,
    )
    savant_player = SavantPitcherModel(
        player_id=645261,
        name="Alcantara, Sandy",
        first_name="Sandy",
        last_name="Alcantara",
        name_ascii="Sandy Alcantara",
        slug="sandy-alcantara",
        season=2026,
        all=SavantPitcherStatsModel(xwOBA=0.297),
        statcast=SavantStatcastModel(bbe=182, avg_ev=88.5),
        home_runs=SavantHomeRunsModel(year=2026, HR=9, xHR=11.4),
        pitch_arsenal=[
            SavantPitchArsenalEntryModel(pitch_type="FF", pitches=400),
            SavantPitchArsenalEntryModel(pitch_type="CH", pitches=180),
            SavantPitchArsenalEntryModel(pitch_type="SL", pitches=120),
        ],
        expected_statistics=SavantPitcherExpectedStatsModel(
            year=2026, PA=242, xAVG=0.243, xSLG=0.356, xwOBA=0.297, xERA=3.48
        ),
        swing_take=SavantSwingTakeModel(
            runs_all=0.3, runs_heart=-4.4, runs_shadow=8.5, runs_chase=-1.0, runs_waste=-2.8
        ),
    )

    results = PlayerMatcher(
        [espn_player], [fg_player], [savant_player]
    ).match_players()
    player = apply_matches(results)["matched"][0]

    p = player.stats.savant
    assert p is not None
    assert p.statcast is not None and p.statcast.bbe == 182
    assert p.home_runs is not None and p.home_runs.xHR == 11.4
    assert len(p.pitch_arsenal) == 3
    # Pitcher bundle has expected_statistics, not sprint_speed
    assert p.expected_statistics is not None
    assert p.expected_statistics.xERA == 3.48
    assert not hasattr(p, "sprint_speed")
    # swing_take is shared across both roles
    assert p.swing_take is not None
    assert p.swing_take.runs_shadow == 8.5


def test_savant_bundle_sub_domains_default_when_absent():
    """When upstream omits sub-domain data, the bundle fields stay None or empty list."""
    espn_player = EspnBatterModel(
        id=20,
        name="No Subdomain",
        first_name="No",
        last_name="Subdomain",
        slug="no-subdomain",
        pro_team="FA",
        stats=EspnBatterStatsGroupModel(
            current_season=EspnBatterStatsModel(AB=100)
        ),
    )
    fg_player = FangraphsBatterModel(
        playerid="ns-1",
        name="No Subdomain",
        ascii_name="No Subdomain",
        slug="no-subdomain",
        team="FA",
        xmlbam_id=910001,
    )
    savant_player = SavantBatterModel(
        player_id=910001,
        name="Subdomain, No",
        first_name="No",
        last_name="Subdomain",
        name_ascii="No Subdomain",
        slug="no-subdomain",
        season=2026,
        all=SavantBatterStatsModel(xwOBA=0.300),
        # No statcast / home_runs / pitch_arsenal / sprint_speed / swing_take supplied
    )

    results = PlayerMatcher(
        [espn_player], [fg_player], [savant_player]
    ).match_players()
    player = apply_matches(results)["matched"][0]

    b = player.stats.savant
    assert b is not None
    assert b.statcast is None
    assert b.home_runs is None
    assert b.pitch_arsenal == []
    assert b.sprint_speed is None
    assert b.swing_take is None
