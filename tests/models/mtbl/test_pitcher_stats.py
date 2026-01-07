"""Tests for MtblPitcherStatsModel combining ESPN, FanGraphs, and Savant data."""

import pytest

from player_universe_trx.models.fangraphs.stats import FangraphsPitcherStatsModel
from player_universe_trx.models.mtbl import (
    MtblPitcherSeasonStatsModel,
    MtblPitcherStatsModel,
)


def test_pitcher_stats_model_creation_empty():
    """Test creating an empty pitcher stats model."""
    stats = MtblPitcherStatsModel()
    assert stats is not None
    assert stats.current_season is None
    assert stats.espn_stats is None


def test_pitcher_stats_espn_only():
    """Test pitcher stats with only ESPN current season data."""
    stats = MtblPitcherStatsModel(
        current_season=MtblPitcherSeasonStatsModel(
            W=15,
            L=6,
            ERA=3.25,
            WHIP=1.12,
            K=180,
            QS=20,
        )
    )

    assert stats.current_season is not None

    # ESPN stats should be populated
    assert stats.current_season.W == 15
    assert stats.current_season.L == 6
    assert stats.current_season.ERA == 3.25
    assert stats.current_season.WHIP == 1.12
    assert stats.current_season.K == 180
    assert stats.current_season.QS == 20

    # FanGraphs and Savant should be None
    assert stats.projections is None
    assert stats.current_season.velo is None


def test_pitcher_stats_fangraphs_projections_only():
    """Test pitcher stats with only FanGraphs projection data."""
    stats = MtblPitcherStatsModel(
        projections=FangraphsPitcherStatsModel(
            wins=16,
            losses=7,
            era=3.50,
            whip=1.18,
            strikeouts=195,
            k_per_9=9.5,
            bb_per_9=2.8,
            fip=3.60,
            ra9_war=4.2,
        )
    )

    # FanGraphs projections should be populated
    assert stats.projections is not None
    assert stats.projections.wins == 16
    assert stats.projections.losses == 7
    assert stats.projections.era == 3.50
    assert stats.projections.whip == 1.18
    assert stats.projections.strikeouts == 195
    assert stats.projections.k_per_9 == 9.5
    assert stats.projections.bb_per_9 == 2.8
    assert stats.projections.fip == 3.60
    assert stats.projections.ra9_war == 4.2

    # ESPN and Savant should be None
    assert stats.current_season is None


def test_pitcher_stats_savant_sabermetrics_only():
    """Test pitcher stats with only Savant sabermetric data."""
    stats = MtblPitcherStatsModel(
        current_season=MtblPitcherSeasonStatsModel(
            velo=96.5,
            spin_rate=2450,
            release_extension=6.5,
            break_z=15.2,
            break_x_arm_side=6.8,
            swing_miss_pct=30.5,
            xwoba=0.285,
            xavg=0.215,
        )
    )

    assert stats.current_season is not None

    # Savant sabermetrics should be populated
    assert stats.current_season.velo == 96.5
    assert stats.current_season.spin_rate == 2450
    assert stats.current_season.release_extension == 6.5
    assert stats.current_season.break_z == 15.2
    assert stats.current_season.break_x_arm_side == 6.8
    assert stats.current_season.swing_miss_pct == 30.5
    assert stats.current_season.xwoba == 0.285
    assert stats.current_season.xavg == 0.215

    # ESPN and FanGraphs should be None
    assert stats.current_season.W is None
    assert stats.projections is None


def test_pitcher_stats_all_sources_combined():
    """Test pitcher stats with data from all three sources combined."""
    stats = MtblPitcherStatsModel(
        current_season=MtblPitcherSeasonStatsModel(
            # ESPN current season
            W=18,
            L=7,
            ERA=2.95,
            WHIP=1.05,
            K=210,
            QS=22,

            # Savant sabermetrics
            velo=97.2,
            spin_rate=2500,
            release_extension=6.8,
            break_z=16.0,
            swing_miss_pct=32.0,
            xwoba=0.280,
        ),
        projections=FangraphsPitcherStatsModel(
            wins=17,
            era=3.10,
            strikeouts=200,
            whip=1.10,
            fip=3.20,
            ra9_war=5.0,
        ),
    )

    assert stats.current_season is not None

    # Verify ESPN stats
    assert stats.current_season.W == 18
    assert stats.current_season.ERA == 2.95
    assert stats.current_season.K == 210
    assert stats.current_season.QS == 22

    # Verify FanGraphs projections
    assert stats.projections.wins == 17
    assert stats.projections.era == 3.10
    assert stats.projections.strikeouts == 200
    assert stats.projections.ra9_war == 5.0

    # Verify Savant sabermetrics
    assert stats.current_season.velo == 97.2
    assert stats.current_season.spin_rate == 2500
    assert stats.current_season.swing_miss_pct == 32.0
    assert stats.current_season.xwoba == 0.280


def test_pitcher_stats_partial_data_from_each_source():
    """Test pitcher stats with partial data from each source."""
    stats = MtblPitcherStatsModel(
        current_season=MtblPitcherSeasonStatsModel(
            # Partial ESPN
            W=12,
            ERA=3.75,

            # Partial Savant
            velo=95.0,
            spin_rate=2400,
        ),
        projections=FangraphsPitcherStatsModel(
            era=3.60,
            fip=3.70,
        ),
    )

    assert stats.current_season is not None

    # Verify provided ESPN stats
    assert stats.current_season.W == 12
    assert stats.current_season.ERA == 3.75
    assert stats.current_season.WHIP is None  # Not provided

    # Verify provided FanGraphs stats
    assert stats.projections.era == 3.60
    assert stats.projections.fip == 3.70
    assert stats.projections.wins is None  # Not provided

    # Verify provided Savant stats
    assert stats.current_season.velo == 95.0
    assert stats.current_season.spin_rate == 2400
    assert stats.current_season.swing_miss_pct is None  # Not provided


def test_pitcher_stats_expected_vs_actual_comparison():
    """Test that we can compare expected (xStats) vs actual performance."""
    stats = MtblPitcherStatsModel(
        current_season=MtblPitcherSeasonStatsModel(
            # Actual (ESPN)
            ERA=3.50,
            WHIP=1.15,

            # Expected (Savant)
            xAVG=0.230,
            xSLG=0.380,
            xAVGdiff=0.010,
            xSLGdiff=0.020,
        )
    )

    assert stats.current_season is not None

    # Verify we can track both actual and expected
    assert stats.current_season.ERA == 3.50
    assert stats.current_season.xAVG == 0.230
    assert stats.current_season.xAVGdiff == 0.010

    assert stats.current_season.WHIP == 1.15
    assert stats.current_season.xSLG == 0.380
    assert stats.current_season.xSLGdiff == 0.020


def test_pitcher_stats_current_vs_projected_comparison():
    """Test that we can compare current performance vs projections."""
    stats = MtblPitcherStatsModel(
        current_season=MtblPitcherSeasonStatsModel(
            # Current (ESPN)
            K=90,  # Through half season
            OUTS=480,  # 160 IP (3 outs per inning)
        ),
        projections=FangraphsPitcherStatsModel(
            strikeouts=180,  # Full season projection
            innings_pitched=190,
        ),
    )

    assert stats.current_season is not None

    # Verify we can track both current and projected
    assert stats.current_season.K == 90
    assert stats.projections.strikeouts == 180

    # Can calculate K/9 pace
    if stats.current_season.OUTS and stats.current_season.OUTS > 0:
        innings = stats.current_season.OUTS / 3
        k_per_9 = (stats.current_season.K / innings) * 9
        assert k_per_9 == pytest.approx(5.06, abs=0.1)


def test_pitcher_stats_model_dump():
    """Test that model_dump works correctly with all stats."""
    stats = MtblPitcherStatsModel(
        current_season=MtblPitcherSeasonStatsModel(
            W=15,
            ERA=3.25,
            velo=96.0,
        ),
        projections=FangraphsPitcherStatsModel(
            era=3.10,
        ),
    )

    dumped = stats.model_dump(exclude_none=True)

    assert dumped["current_season"]["W"] == 15
    assert dumped["current_season"]["ERA"] == 3.25
    assert dumped["current_season"]["velo"] == 96.0
    assert dumped["projections"]["era"] == 3.10

    # None values should be excluded
    assert "WHIP" not in dumped["current_season"]
    assert "proj_whip" not in dumped["current_season"]
    assert "spin_rate" not in dumped["current_season"]


def test_pitcher_stats_plate_discipline_metrics():
    """Test plate discipline metrics from all sources."""
    stats = MtblPitcherStatsModel(
        current_season=MtblPitcherSeasonStatsModel(
            # ESPN plate discipline
            P_BB=45,
            K=190,
            TBF=750,

            # Savant plate discipline
            swing_miss_pct=31.0,
            swings=520,
            whiffs=160,
            takes=180,
        ),
        projections=FangraphsPitcherStatsModel(
            walks=50,
            strikeouts=185,
            k_per_bb=3.8,
        ),
    )

    assert stats.current_season is not None

    # ESPN
    assert stats.current_season.P_BB == 45
    assert stats.current_season.K == 190
    assert stats.current_season.TBF == 750

    # FanGraphs
    assert stats.projections.walks == 50
    assert stats.projections.strikeouts == 185
    assert stats.projections.k_per_bb == 3.8

    # Savant
    assert stats.current_season.swing_miss_pct == 31.0
    assert stats.current_season.swings == 520
    assert stats.current_season.whiffs == 160
    assert stats.current_season.takes == 180


def test_pitcher_stats_pitch_characteristics_metrics():
    """Test pitch characteristics metrics from Savant."""
    stats = MtblPitcherStatsModel(
        current_season=MtblPitcherSeasonStatsModel(
            velo=98.1,
            spin_rate=2550,
            eff_min_vel=95.3,
            percieved_velo=97.0,
            release_extension=7.0,
            release_pos_x=1.2,
            release_pos_z=5.8,
        )
    )

    assert stats.current_season is not None
    assert stats.current_season.velo == 98.1
    assert stats.current_season.spin_rate == 2550
    assert stats.current_season.eff_min_vel == 95.3
    assert stats.current_season.percieved_velo == 97.0
    assert stats.current_season.release_extension == 7.0
    assert stats.current_season.release_pos_x == 1.2
    assert stats.current_season.release_pos_z == 5.8


def test_pitcher_stats_movement_metrics():
    """Test pitch movement metrics from Savant."""
    stats = MtblPitcherStatsModel(
        current_season=MtblPitcherSeasonStatsModel(
            break_z=15.8,
            induced_break_z=12.4,
            break_x_arm_side=7.2,
            break_x_batter_in=5.5,
        )
    )

    assert stats.current_season is not None
    assert stats.current_season.break_z == 15.8
    assert stats.current_season.induced_break_z == 12.4
    assert stats.current_season.break_x_arm_side == 7.2
    assert stats.current_season.break_x_batter_in == 5.5


def test_pitcher_stats_mechanics_and_performance_metrics():
    """Test mechanics and performance metrics from Savant."""
    stats = MtblPitcherStatsModel(
        current_season=MtblPitcherSeasonStatsModel(
            arm_angle=45.5,
            pitcher_run_exp=1.2,
            pitcher_run_value_per_100=5.8,
        )
    )

    assert stats.current_season is not None
    assert stats.current_season.arm_angle == 45.5
    assert stats.current_season.pitcher_run_exp == 1.2
    assert stats.current_season.pitcher_run_value_per_100 == 5.8


def test_pitcher_stats_contact_metrics():
    """Test contact/batted ball metrics from Savant."""
    stats = MtblPitcherStatsModel(
        current_season=MtblPitcherSeasonStatsModel(
            exit_velo=88.5,
            adj_exit_velo=89.2,
            launch_angle=12.8,
        )
    )

    assert stats.current_season is not None
    assert stats.current_season.exit_velo == 88.5
    assert stats.current_season.adj_exit_velo == 89.2
    assert stats.current_season.launch_angle == 12.8


def test_pitcher_stats_expected_stats():
    """Test expected stats from Savant."""
    stats = MtblPitcherStatsModel(
        current_season=MtblPitcherSeasonStatsModel(
            xwoba=0.290,
            xavg=0.225,
            xslg=0.375,
            xAVG=0.225,
            xSLG=0.375,
            xSLGdiff=0.015,
        )
    )

    assert stats.current_season is not None
    assert stats.current_season.xwoba == 0.290
    assert stats.current_season.xavg == 0.225
    assert stats.current_season.xslg == 0.375
    assert stats.current_season.xAVG == 0.225
    assert stats.current_season.xSLG == 0.375
    assert stats.current_season.xSLGdiff == 0.015


def test_pitcher_stats_other_savant_stats():
    """Test other Savant stats for pitchers."""
    stats = MtblPitcherStatsModel(
        current_season=MtblPitcherSeasonStatsModel(
            BABIP=0.290,
            BB=45,
            BB_pct=8.5,
            BBdist=32,
            BIP=420,
            ISO=0.165,
            wOBA=0.315,
            wOBAdiff=0.010,
            run_exp=1.5,
            barrels_total=18,
            rate_ideal_attack_angle=12.5,
        )
    )

    assert stats.current_season is not None
    assert stats.current_season.BABIP == 0.290
    assert stats.current_season.BB == 45
    assert stats.current_season.BB_pct == 8.5
    assert stats.current_season.BBdist == 32
    assert stats.current_season.BIP == 420
    assert stats.current_season.ISO == 0.165
    assert stats.current_season.wOBA == 0.315
    assert stats.current_season.wOBAdiff == 0.010
    assert stats.current_season.run_exp == 1.5
    assert stats.current_season.barrels_total == 18
    assert stats.current_season.rate_ideal_attack_angle == 12.5
