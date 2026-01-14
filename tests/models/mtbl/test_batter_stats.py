"""Tests for MtblBatterStatsModel combining ESPN, FanGraphs, and Savant data."""

import pytest

from player_universe_trx.models.fangraphs.stats import FangraphsBatterStatsModel
from player_universe_trx.models.mtbl import (
    MtblBatterSeasonStatsModel,
    MtblBatterStatsModel,
)


def test_batter_stats_model_creation_empty():
    """Test creating an empty batter stats model."""
    stats = MtblBatterStatsModel()
    assert stats is not None
    assert stats.current_season is None
    assert stats.espn_stats is None


def test_batter_stats_espn_only():
    """Test batter stats with only ESPN current season data."""
    stats = MtblBatterStatsModel(
        current_season=MtblBatterSeasonStatsModel(
            AB=500,
            H=150,
            AVG=0.300,
            HR=30,
            RBI=100,
            R=85,
            SB=15,
            OBP=0.375,
            SLG=0.550,
            OPS=0.925,
        )
    )

    assert stats.current_season is not None

    # ESPN stats should be populated
    assert stats.current_season.AB == 500
    assert stats.current_season.H == 150
    assert stats.current_season.AVG == 0.300
    assert stats.current_season.HR == 30
    assert stats.current_season.RBI == 100
    assert stats.current_season.R == 85
    assert stats.current_season.SB == 15
    assert stats.current_season.OBP == 0.375
    assert stats.current_season.SLG == 0.550
    assert stats.current_season.OPS == 0.925

    # FanGraphs and Savant should be None
    assert stats.projections is None
    assert stats.current_season.exit_velo is None


def test_batter_stats_fangraphs_projections_only():
    """Test batter stats with only FanGraphs projection data."""
    stats = MtblBatterStatsModel(
        projections=FangraphsBatterStatsModel(
            AB=550,
            H=165,
            AVG=0.300,
            HR=32,
            RBI=95,
            R=90,
            SB=12,
            OBP=0.370,
            SLG=0.540,
            OPS=0.910,
            wOBA=0.380,
            wrc_plus=125.5,  # type: ignore [reportCallIssues]
        )
    )

    # FanGraphs projections should be populated
    assert stats.projections is not None
    assert stats.projections.ab == 550
    assert stats.projections.h == 165
    assert stats.projections.avg == 0.300
    assert stats.projections.hr == 32
    assert stats.projections.rbi == 95
    assert stats.projections.r == 90
    assert stats.projections.sb == 12
    assert stats.projections.obp == 0.370
    assert stats.projections.slg == 0.540
    assert stats.projections.ops == 0.910
    assert stats.projections.woba == 0.380
    assert stats.projections.wrc_plus == 125.5

    # ESPN and Savant should be None
    assert stats.current_season is None


def test_batter_stats_savant_sabermetrics_only():
    """Test batter stats with only Savant sabermetric data."""
    stats = MtblBatterStatsModel(
        current_season=MtblBatterSeasonStatsModel(
            exit_velo=92.5,
            launch_angle=15.2,
            barrel_rate=12.5,
            barrels_per_bbe_pct=12.5,
            hard_hit_rate=45.8,
            hardhit_pct=45.8,
            xwoba=0.380,
            xavg=0.295,
            xslg=0.520,
            xwOBA=0.380,
            xAVG=0.295,
            xSLG=0.520,
            swing_miss_pct=24.5,
            bat_speed=72.3,
            attack_angle=14.8,
        )
    )

    assert stats.current_season is not None

    # Savant sabermetrics should be populated
    assert stats.current_season.exit_velo == 92.5
    assert stats.current_season.launch_angle == 15.2
    assert stats.current_season.barrel_rate == 12.5
    assert stats.current_season.barrels_per_bbe_pct == 12.5
    assert stats.current_season.hard_hit_rate == 45.8
    assert stats.current_season.hardhit_pct == 45.8
    assert stats.current_season.xwoba == 0.380
    assert stats.current_season.xavg == 0.295
    assert stats.current_season.xslg == 0.520
    assert stats.current_season.xwOBA == 0.380
    assert stats.current_season.xAVG == 0.295
    assert stats.current_season.xSLG == 0.520
    assert stats.current_season.swing_miss_pct == 24.5
    assert stats.current_season.bat_speed == 72.3
    assert stats.current_season.attack_angle == 14.8

    # ESPN and FanGraphs should be None
    assert stats.current_season.AB is None
    assert stats.projections is None


def test_batter_stats_all_sources_combined():
    """Test batter stats with data from all three sources combined."""
    stats = MtblBatterStatsModel(
        current_season=MtblBatterSeasonStatsModel(
            # ESPN current season
            AB=520,
            H=156,
            AVG=0.300,
            HR=32,
            RBI=98,
            R=88,
            SB=18,
            CS=4,
            OBP=0.378,
            SLG=0.545,
            OPS=0.923,
            # Savant sabermetrics
            exit_velo=93.2,
            launch_angle=14.5,
            barrel_rate=13.2,
            barrels_per_bbe_pct=13.2,
            hard_hit_rate=47.5,
            hardhit_pct=47.5,
            xwoba=0.385,
            xavg=0.298,
            xslg=0.530,
            xwOBA=0.385,
            xAVG=0.298,
            xSLG=0.530,
            swing_miss_pct=23.8,
            bat_speed=73.1,
            attack_angle=15.2,
        ),
        projections=FangraphsBatterStatsModel(
            AB=540,
            H=162,
            AVG=0.300,
            HR=30,
            RBI=95,
            R=90,
            SB=15,
            OBP=0.375,
            SLG=0.540,
            OPS=0.915,
            wOBA=0.375,
            wrc_plus=128.0,  # type: ignore [reportCallIssues]
        ),
    )

    assert stats.current_season is not None

    # Verify ESPN stats
    assert stats.current_season.AB == 520
    assert stats.current_season.AVG == 0.300
    assert stats.current_season.HR == 32
    assert stats.current_season.OPS == 0.923
    assert stats.current_season.SBN == 14

    # Verify FanGraphs projections
    assert stats.projections is not None
    assert stats.projections.ab == 540
    assert stats.projections.avg == 0.300
    assert stats.projections.hr == 30
    assert stats.projections.wrc_plus == 128.0

    # Verify Savant sabermetrics
    assert stats.current_season.exit_velo == 93.2
    assert stats.current_season.barrel_rate == 13.2
    assert stats.current_season.xwOBA == 0.385
    assert stats.current_season.bat_speed == 73.1


def test_batter_stats_partial_data_from_each_source():
    """Test batter stats with partial data from each source."""
    stats = MtblBatterStatsModel(
        current_season=MtblBatterSeasonStatsModel(
            # Partial ESPN
            AB=450,
            HR=25,
            # Partial Savant
            exit_velo=91.0,
            barrel_rate=10.5,
        ),
        projections=FangraphsBatterStatsModel(
            HR=28,
            wOBA=0.360,
        ),
    )

    assert stats.current_season is not None

    # Verify provided ESPN stats
    assert stats.current_season.AB == 450
    assert stats.current_season.HR == 25
    assert stats.current_season.AVG is None  # Not provided

    # Verify provided FanGraphs stats
    assert stats.projections is not None
    assert stats.projections.hr == 28
    assert stats.projections.woba == 0.360
    assert stats.projections.avg is None  # Not provided

    # Verify provided Savant stats
    assert stats.current_season.exit_velo == 91.0
    assert stats.current_season.barrel_rate == 10.5
    assert stats.current_season.xwOBA is None  # Not provided


def test_batter_stats_expected_vs_actual_comparison():
    """Test that we can compare expected (xStats) vs actual performance."""
    stats = MtblBatterStatsModel(
        current_season=MtblBatterSeasonStatsModel(
            # Actual (ESPN)
            AVG=0.275,
            SLG=0.480,
            # Expected (Savant)
            xAVG=0.290,
            xSLG=0.510,
            xAVGdiff=0.015,
            xSLGdiff=0.030,
        )
    )

    assert stats.current_season is not None

    # Verify we can track both actual and expected
    assert stats.current_season.AVG == 0.275
    assert stats.current_season.xAVG == 0.290
    assert stats.current_season.xAVGdiff == 0.015

    assert stats.current_season.SLG == 0.480
    assert stats.current_season.xSLG == 0.510
    assert stats.current_season.xSLGdiff == 0.030


def test_batter_stats_current_vs_projected_comparison():
    """Test that we can compare current performance vs projections."""
    stats = MtblBatterStatsModel(
        current_season=MtblBatterSeasonStatsModel(
            # Current (ESPN)
            HR=15,  # Through half season
            AB=250,
        ),
        projections=FangraphsBatterStatsModel(
            HR=32,  # Full season projection
            AB=520,
        ),
    )

    assert stats.current_season is not None

    # Verify we can track both current and projected
    assert stats.current_season.HR == 15
    assert stats.projections is not None
    assert stats.projections.hr == 32
    assert stats.projections.ab == 520

    # Can calculate pace: (15 / 250) * 520 = 31.2 HR pace
    if stats.current_season.AB and stats.current_season.AB > 0:
        pace = (
            stats.current_season.HR / stats.current_season.AB
        ) * stats.projections.ab
        assert pace == pytest.approx(31.2, abs=0.1)


def test_batter_stats_model_dump():
    """Test that model_dump works correctly with all stats."""
    stats = MtblBatterStatsModel(
        current_season=MtblBatterSeasonStatsModel(
            AB=500,
            HR=30,
            exit_velo=92.0,
        ),
        projections=FangraphsBatterStatsModel(
            HR=28,
        ),
    )

    dumped = stats.model_dump(exclude_none=True)

    assert dumped["current_season"]["AB"] == 500
    assert dumped["current_season"]["HR"] == 30
    assert dumped["current_season"]["exit_velo"] == 92.0
    assert dumped["projections"]["HR"] == 28

    # None values should be excluded
    assert "AVG" not in dumped["current_season"]
    assert "proj_avg" not in dumped["current_season"]
    assert "barrel_rate" not in dumped["current_season"]


def test_batter_stats_plate_discipline_metrics():
    """Test plate discipline metrics from all sources."""
    stats = MtblBatterStatsModel(
        current_season=MtblBatterSeasonStatsModel(
            # ESPN plate discipline
            B_BB=65,
            B_SO=120,
            PA=550,
            # Savant plate discipline
            swing_miss_pct=24.5,
            swings=450,
            whiffs=110,
            takes=100,
        ),
        projections=FangraphsBatterStatsModel(
            BB=68,
            SO=115,
            bb_k=0.59,  # type: ignore [reportCallIssues]
        ),
    )

    assert stats.current_season is not None

    # ESPN
    assert stats.current_season.B_BB == 65
    assert stats.current_season.B_SO == 120
    assert stats.current_season.PA == 550

    # FanGraphs
    assert stats.projections is not None
    assert stats.projections.bb == 68
    assert stats.projections.so == 115
    assert stats.projections.bb_k == 0.59

    # Savant
    assert stats.current_season.swing_miss_pct == 24.5
    assert stats.current_season.swings == 450
    assert stats.current_season.whiffs == 110
    assert stats.current_season.takes == 100


def test_batter_stats_contact_quality_metrics():
    """Test contact quality metrics from Savant."""
    stats = MtblBatterStatsModel(
        current_season=MtblBatterSeasonStatsModel(
            exit_velo=94.5,
            adj_exit_velo=95.2,
            launch_angle=16.2,
            barrel_rate=15.8,
            barrels_per_bbe_pct=15.8,
            barrels_per_pa_pct=8.2,
            barrels_total=42,
            hard_hit_rate=48.9,
            hardhit_pct=48.9,
        )
    )

    assert stats.current_season is not None
    assert stats.current_season.exit_velo == 94.5
    assert stats.current_season.adj_exit_velo == 95.2
    assert stats.current_season.launch_angle == 16.2
    assert stats.current_season.barrel_rate == 15.8
    assert stats.current_season.barrels_per_bbe_pct == 15.8
    assert stats.current_season.barrels_per_pa_pct == 8.2
    assert stats.current_season.barrels_total == 42
    assert stats.current_season.hard_hit_rate == 48.9
    assert stats.current_season.hardhit_pct == 48.9


def test_batter_stats_swing_mechanics():
    """Test swing mechanics from Savant."""
    stats = MtblBatterStatsModel(
        current_season=MtblBatterSeasonStatsModel(
            attack_angle=16.5,
            attack_dir=2.3,
            bat_speed=74.2,
            swing_length=7.1,
            swing_path_tilt=18.2,
        )
    )

    assert stats.current_season is not None
    assert stats.current_season.attack_angle == 16.5
    assert stats.current_season.attack_dir == 2.3
    assert stats.current_season.bat_speed == 74.2
    assert stats.current_season.swing_length == 7.1
    assert stats.current_season.swing_path_tilt == 18.2


def test_batter_stats_sbn_with_only_sb():
    """Test SBN when only SB is provided."""
    stats = MtblBatterSeasonStatsModel(SB=11)

    assert stats.SBN == 11


def test_batter_stats_sbn_with_only_cs():
    """Test SBN when only CS is provided."""
    stats = MtblBatterSeasonStatsModel(CS=5)

    assert stats.SBN == -5


def test_batter_stats_sbn_provided_by_espn():
    """Test that ESPN-provided SBN is preserved (not overwritten by computation)."""
    # This simulates a league that only tracks SBN, not individual SB/CS
    stats = MtblBatterSeasonStatsModel(SBN=15)

    # ESPN's SBN should be preserved
    assert stats.SBN == 15
    assert stats.SB is None
    assert stats.CS is None


def test_batter_stats_sbn_espn_overrides_computation():
    """Test that ESPN-provided SBN takes precedence over computed value."""
    # Even if SB and CS are present, if ESPN provides SBN, use ESPN's value
    # (This handles edge cases where ESPN may have special SBN calculation logic)
    stats = MtblBatterSeasonStatsModel(SB=20, CS=8, SBN=10)

    # Should use ESPN's SBN value, not compute from SB-CS
    assert stats.SBN == 10
