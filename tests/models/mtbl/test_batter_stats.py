"""Tests for MtblBatterStatsModel combining ESPN, FanGraphs, and Savant data."""

import pytest

from player_universe_trx.models.mtbl import MtblBatterStatsModel


def test_batter_stats_model_creation_empty():
    """Test creating an empty batter stats model."""
    stats = MtblBatterStatsModel()
    assert stats is not None
    assert stats.AB is None
    assert stats.proj_hr is None
    assert stats.exit_velo is None


def test_batter_stats_espn_only():
    """Test batter stats with only ESPN current season data."""
    stats = MtblBatterStatsModel(
        AB=500,
        H=150,
        AVG=0.300,
        HR=30,
        RBI=100,
        R=85,
        SB=15,
        OBP=0.375,
        SLG=0.550,
        OPS=0.925
    )

    # ESPN stats should be populated
    assert stats.AB == 500
    assert stats.H == 150
    assert stats.AVG == 0.300
    assert stats.HR == 30
    assert stats.RBI == 100
    assert stats.R == 85
    assert stats.SB == 15
    assert stats.OBP == 0.375
    assert stats.SLG == 0.550
    assert stats.OPS == 0.925

    # FanGraphs and Savant should be None
    assert stats.proj_hr is None
    assert stats.exit_velo is None


def test_batter_stats_fangraphs_projections_only():
    """Test batter stats with only FanGraphs projection data."""
    stats = MtblBatterStatsModel(
        proj_ab=550,
        proj_h=165,
        proj_avg=0.300,
        proj_hr=32,
        proj_rbi=95,
        proj_r=90,
        proj_sb=12,
        proj_obp=0.370,
        proj_slg=0.540,
        proj_ops=0.910,
        proj_woba=0.380,
        proj_wrc_plus=125.5
    )

    # FanGraphs projections should be populated
    assert stats.proj_ab == 550
    assert stats.proj_h == 165
    assert stats.proj_avg == 0.300
    assert stats.proj_hr == 32
    assert stats.proj_rbi == 95
    assert stats.proj_r == 90
    assert stats.proj_sb == 12
    assert stats.proj_obp == 0.370
    assert stats.proj_slg == 0.540
    assert stats.proj_ops == 0.910
    assert stats.proj_woba == 0.380
    assert stats.proj_wrc_plus == 125.5

    # ESPN and Savant should be None
    assert stats.AB is None
    assert stats.exit_velo is None


def test_batter_stats_savant_sabermetrics_only():
    """Test batter stats with only Savant sabermetric data."""
    stats = MtblBatterStatsModel(
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
        attack_angle=14.8
    )

    # Savant sabermetrics should be populated
    assert stats.exit_velo == 92.5
    assert stats.launch_angle == 15.2
    assert stats.barrel_rate == 12.5
    assert stats.barrels_per_bbe_pct == 12.5
    assert stats.hard_hit_rate == 45.8
    assert stats.hardhit_pct == 45.8
    assert stats.xwoba == 0.380
    assert stats.xavg == 0.295
    assert stats.xslg == 0.520
    assert stats.xwOBA == 0.380
    assert stats.xAVG == 0.295
    assert stats.xSLG == 0.520
    assert stats.swing_miss_pct == 24.5
    assert stats.bat_speed == 72.3
    assert stats.attack_angle == 14.8

    # ESPN and FanGraphs should be None
    assert stats.AB is None
    assert stats.proj_hr is None


def test_batter_stats_all_sources_combined():
    """Test batter stats with data from all three sources combined."""
    stats = MtblBatterStatsModel(
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

        # FanGraphs projections
        proj_ab=540,
        proj_h=162,
        proj_avg=0.300,
        proj_hr=30,
        proj_rbi=95,
        proj_r=90,
        proj_sb=15,
        proj_obp=0.375,
        proj_slg=0.540,
        proj_ops=0.915,
        proj_woba=0.375,
        proj_wrc_plus=128.0,

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
        attack_angle=15.2
    )

    # Verify ESPN stats
    assert stats.AB == 520
    assert stats.AVG == 0.300
    assert stats.HR == 32
    assert stats.OPS == 0.923

    # Verify FanGraphs projections
    assert stats.proj_ab == 540
    assert stats.proj_avg == 0.300
    assert stats.proj_hr == 30
    assert stats.proj_wrc_plus == 128.0

    # Verify Savant sabermetrics
    assert stats.exit_velo == 93.2
    assert stats.barrel_rate == 13.2
    assert stats.xwOBA == 0.385
    assert stats.bat_speed == 73.1


def test_batter_stats_partial_data_from_each_source():
    """Test batter stats with partial data from each source."""
    stats = MtblBatterStatsModel(
        # Partial ESPN
        AB=450,
        HR=25,

        # Partial FanGraphs
        proj_hr=28,
        proj_woba=0.360,

        # Partial Savant
        exit_velo=91.0,
        barrel_rate=10.5
    )

    # Verify provided ESPN stats
    assert stats.AB == 450
    assert stats.HR == 25
    assert stats.AVG is None  # Not provided

    # Verify provided FanGraphs stats
    assert stats.proj_hr == 28
    assert stats.proj_woba == 0.360
    assert stats.proj_avg is None  # Not provided

    # Verify provided Savant stats
    assert stats.exit_velo == 91.0
    assert stats.barrel_rate == 10.5
    assert stats.xwOBA is None  # Not provided


def test_batter_stats_expected_vs_actual_comparison():
    """Test that we can compare expected (xStats) vs actual performance."""
    stats = MtblBatterStatsModel(
        # Actual (ESPN)
        AVG=0.275,
        SLG=0.480,

        # Expected (Savant)
        xAVG=0.290,
        xSLG=0.510,
        xAVGdiff=0.015,
        xSLGdiff=0.030
    )

    # Verify we can track both actual and expected
    assert stats.AVG == 0.275
    assert stats.xAVG == 0.290
    assert stats.xAVGdiff == 0.015

    assert stats.SLG == 0.480
    assert stats.xSLG == 0.510
    assert stats.xSLGdiff == 0.030


def test_batter_stats_current_vs_projected_comparison():
    """Test that we can compare current performance vs projections."""
    stats = MtblBatterStatsModel(
        # Current (ESPN)
        HR=15,  # Through half season
        AB=250,

        # Projected (FanGraphs)
        proj_hr=32,  # Full season projection
        proj_ab=520
    )

    # Verify we can track both current and projected
    assert stats.HR == 15
    assert stats.proj_hr == 32

    # Can calculate pace: (15 / 250) * 520 = 31.2 HR pace
    if stats.AB and stats.AB > 0:
        pace = (stats.HR / stats.AB) * stats.proj_ab
        assert pace == pytest.approx(31.2, abs=0.1)


def test_batter_stats_model_dump():
    """Test that model_dump works correctly with all stats."""
    stats = MtblBatterStatsModel(
        AB=500,
        HR=30,
        proj_hr=28,
        exit_velo=92.0
    )

    dumped = stats.model_dump(exclude_none=True)

    assert dumped["AB"] == 500
    assert dumped["HR"] == 30
    assert dumped["proj_hr"] == 28
    assert dumped["exit_velo"] == 92.0

    # None values should be excluded
    assert "AVG" not in dumped
    assert "proj_avg" not in dumped
    assert "barrel_rate" not in dumped


def test_batter_stats_plate_discipline_metrics():
    """Test plate discipline metrics from all sources."""
    stats = MtblBatterStatsModel(
        # ESPN plate discipline
        B_BB=65,
        B_SO=120,
        PA=550,

        # FanGraphs plate discipline
        proj_bb=68,
        proj_so=115,
        proj_bb_k=0.59,

        # Savant plate discipline
        swing_miss_pct=24.5,
        swings=450,
        whiffs=110,
        takes=100
    )

    # ESPN
    assert stats.B_BB == 65
    assert stats.B_SO == 120
    assert stats.PA == 550

    # FanGraphs
    assert stats.proj_bb == 68
    assert stats.proj_so == 115
    assert stats.proj_bb_k == 0.59

    # Savant
    assert stats.swing_miss_pct == 24.5
    assert stats.swings == 450
    assert stats.whiffs == 110
    assert stats.takes == 100


def test_batter_stats_contact_quality_metrics():
    """Test contact quality metrics from Savant."""
    stats = MtblBatterStatsModel(
        exit_velo=94.5,
        adj_exit_velo=95.2,
        launch_angle=16.2,
        barrel_rate=15.8,
        barrels_per_bbe_pct=15.8,
        barrels_per_pa_pct=8.2,
        barrels_total=42,
        hard_hit_rate=48.9,
        hardhit_pct=48.9
    )

    assert stats.exit_velo == 94.5
    assert stats.adj_exit_velo == 95.2
    assert stats.launch_angle == 16.2
    assert stats.barrel_rate == 15.8
    assert stats.barrels_per_bbe_pct == 15.8
    assert stats.barrels_per_pa_pct == 8.2
    assert stats.barrels_total == 42
    assert stats.hard_hit_rate == 48.9
    assert stats.hardhit_pct == 48.9


def test_batter_stats_swing_mechanics():
    """Test swing mechanics from Savant."""
    stats = MtblBatterStatsModel(
        attack_angle=16.5,
        attack_dir=2.3,
        bat_speed=74.2,
        swing_length=7.1,
        swing_path_tilt=18.2
    )

    assert stats.attack_angle == 16.5
    assert stats.attack_dir == 2.3
    assert stats.bat_speed == 74.2
    assert stats.swing_length == 7.1
    assert stats.swing_path_tilt == 18.2
