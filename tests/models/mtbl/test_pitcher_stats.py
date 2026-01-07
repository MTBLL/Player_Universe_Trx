"""Tests for MtblPitcherStatsModel combining ESPN, FanGraphs, and Savant data."""

from player_universe_trx.models.mtbl import MtblPitcherStatsModel


def test_pitcher_stats_model_creation_empty():
    """Test creating an empty pitcher stats model."""
    stats = MtblPitcherStatsModel()
    assert stats is not None
    assert stats.W is None
    assert stats.proj_wins is None
    assert stats.velo is None


def test_pitcher_stats_espn_only():
    """Test pitcher stats with only ESPN current season data."""
    stats = MtblPitcherStatsModel(
        W=12,
        L=8,
        ERA=3.45,
        WHIP=1.15,
        GP=28,
        GS=28,
        K=195,
        P_BB=45,
        P_H=160,
        P_HR=20,
        QS=18,
        WPCT=0.600,
    )

    # ESPN stats should be populated
    assert stats.W == 12
    assert stats.L == 8
    assert stats.ERA == 3.45
    assert stats.WHIP == 1.15
    assert stats.GP == 28
    assert stats.GS == 28
    assert stats.K == 195
    assert stats.P_BB == 45
    assert stats.P_H == 160
    assert stats.P_HR == 20
    assert stats.QS == 18
    assert stats.WPCT == 0.600

    # FanGraphs and Savant should be None
    assert stats.proj_wins is None
    assert stats.velo is None


def test_pitcher_stats_fangraphs_projections_only():
    """Test pitcher stats with only FanGraphs projection data."""
    stats = MtblPitcherStatsModel(
        proj_wins=13,
        proj_losses=7,
        proj_era=3.35,
        proj_whip=1.12,
        proj_innings_pitched=185.0,
        proj_strikeouts=200,
        proj_walks=42,
        proj_hits=155,
        proj_home_runs=18,
        proj_saves=0,
        proj_k_per_9=9.73,
        proj_bb_per_9=2.05,
        proj_hr_per_9=0.88,
        proj_fip=3.25,
        proj_ra9_war=4.2,
    )

    # FanGraphs projections should be populated
    assert stats.proj_wins == 13
    assert stats.proj_losses == 7
    assert stats.proj_era == 3.35
    assert stats.proj_whip == 1.12
    assert stats.proj_innings_pitched == 185.0
    assert stats.proj_strikeouts == 200
    assert stats.proj_walks == 42
    assert stats.proj_hits == 155
    assert stats.proj_home_runs == 18
    assert stats.proj_saves == 0
    assert stats.proj_k_per_9 == 9.73
    assert stats.proj_bb_per_9 == 2.05
    assert stats.proj_hr_per_9 == 0.88
    assert stats.proj_fip == 3.25
    assert stats.proj_ra9_war == 4.2

    # ESPN and Savant should be None
    assert stats.W is None
    assert stats.velo is None


def test_pitcher_stats_savant_sabermetrics_only():
    """Test pitcher stats with only Savant sabermetric data."""
    stats = MtblPitcherStatsModel(
        velo=94.5,
        spin_rate=2450,
        swing_miss_pct=28.5,
        xwoba=0.305,
        xavg=0.235,
        xslg=0.395,
        xwOBA=0.305,
        xAVG=0.235,
        xSLG=0.395,
        exit_velo=88.3,
        release_extension=6.2,
        break_z=18.5,
        break_x_arm_side=12.3,
    )

    # Savant sabermetrics should be populated
    assert stats.velo == 94.5
    assert stats.spin_rate == 2450
    assert stats.swing_miss_pct == 28.5
    assert stats.xwoba == 0.305
    assert stats.xavg == 0.235
    assert stats.xslg == 0.395
    assert stats.xwOBA == 0.305
    assert stats.xAVG == 0.235
    assert stats.xSLG == 0.395
    assert stats.exit_velo == 88.3
    assert stats.release_extension == 6.2
    assert stats.break_z == 18.5
    assert stats.break_x_arm_side == 12.3

    # ESPN and FanGraphs should be None
    assert stats.W is None
    assert stats.proj_wins is None


def test_pitcher_stats_all_sources_combined():
    """Test pitcher stats with data from all three sources combined."""
    stats = MtblPitcherStatsModel(
        # ESPN current season
        W=15,
        L=6,
        ERA=3.15,
        WHIP=1.08,
        GP=30,
        GS=30,
        K=215,
        P_BB=38,
        P_H=165,
        P_HR=18,
        QS=22,
        # FanGraphs projections
        proj_wins=14,
        proj_losses=7,
        proj_era=3.25,
        proj_whip=1.10,
        proj_innings_pitched=190.0,
        proj_strikeouts=210,
        proj_walks=40,
        proj_fip=3.10,
        proj_ra9_war=4.5,
        # Savant sabermetrics
        velo=95.2,
        spin_rate=2485,
        swing_miss_pct=29.8,
        xwoba=0.298,
        xavg=0.228,
        xslg=0.385,
        xwOBA=0.298,
        xAVG=0.228,
        xSLG=0.385,
        exit_velo=87.8,
        release_extension=6.3,
    )

    # Verify ESPN stats
    assert stats.W == 15
    assert stats.ERA == 3.15
    assert stats.K == 215
    assert stats.WHIP == 1.08

    # Verify FanGraphs projections
    assert stats.proj_wins == 14
    assert stats.proj_era == 3.25
    assert stats.proj_strikeouts == 210
    assert stats.proj_ra9_war == 4.5

    # Verify Savant sabermetrics
    assert stats.velo == 95.2
    assert stats.swing_miss_pct == 29.8
    assert stats.xwOBA == 0.298
    assert stats.exit_velo == 87.8


def test_pitcher_stats_partial_data_from_each_source():
    """Test pitcher stats with partial data from each source."""
    stats = MtblPitcherStatsModel(
        # Partial ESPN
        W=10,
        ERA=3.50,
        # Partial FanGraphs
        proj_wins=12,
        proj_fip=3.25,
        # Partial Savant
        velo=93.5,
        swing_miss_pct=27.5,
    )

    # Verify provided ESPN stats
    assert stats.W == 10
    assert stats.ERA == 3.50
    assert stats.K is None  # Not provided

    # Verify provided FanGraphs stats
    assert stats.proj_wins == 12
    assert stats.proj_fip == 3.25
    assert stats.proj_era is None  # Not provided

    # Verify provided Savant stats
    assert stats.velo == 93.5
    assert stats.swing_miss_pct == 27.5
    assert stats.xwOBA is None  # Not provided


def test_pitcher_stats_expected_vs_actual_comparison():
    """Test that we can compare expected (xStats) vs actual performance."""
    stats = MtblPitcherStatsModel(
        # Actual (ESPN)
        ERA=3.80,
        OBA=0.265,  # Opponent batting average
        # Expected (Savant)
        xwOBA=0.310,
        xAVG=0.240,
        xSLG=0.395,
        xAVGdiff=0.025,
        xSLGdiff=0.030,
    )

    # Verify we can track both actual and expected
    assert stats.ERA == 3.80
    assert stats.OBA == 0.265

    assert stats.xAVG == 0.240
    assert stats.xSLG == 0.395
    assert stats.xAVGdiff == 0.025
    assert stats.xSLGdiff == 0.030


def test_pitcher_stats_current_vs_projected_comparison():
    """Test that we can compare current performance vs projections."""
    stats = MtblPitcherStatsModel(
        # Current (ESPN) - through half season
        W=8,
        K=105,
        # Projected (FanGraphs) - full season
        proj_wins=15,
        proj_strikeouts=210,
        proj_innings_pitched=190.0,
    )

    # Verify we can track both current and projected
    assert stats.W == 8
    assert stats.proj_wins == 15
    assert stats.K == 105
    assert stats.proj_strikeouts == 210


def test_pitcher_stats_model_dump():
    """Test that model_dump works correctly with all stats."""
    stats = MtblPitcherStatsModel(
        W=12, ERA=3.45, proj_wins=13, proj_fip=3.25, velo=94.5
    )

    dumped = stats.model_dump(exclude_none=True)

    assert dumped["W"] == 12
    assert dumped["ERA"] == 3.45
    assert dumped["proj_wins"] == 13
    assert dumped["proj_fip"] == 3.25
    assert dumped["velo"] == 94.5

    # None values should be excluded
    assert "L" not in dumped
    assert "proj_era" not in dumped
    assert "spin_rate" not in dumped


def test_pitcher_stats_starter_metrics():
    """Test metrics specific to starting pitchers."""
    stats = MtblPitcherStatsModel(
        # ESPN starter metrics
        W=14,
        L=7,
        QS=20,
        GS=28,
        GP=28,
        # FanGraphs starter projections
        proj_wins=13,
        proj_quality_starts=18,
        proj_games_started=30,
        proj_innings_pitched=190.0,
        # Savant pitch characteristics
        velo=93.5,
        spin_rate=2425,
        release_extension=6.1,
    )

    # ESPN
    assert stats.W == 14
    assert stats.QS == 20
    assert stats.GS == 28

    # FanGraphs
    assert stats.proj_wins == 13
    assert stats.proj_quality_starts == 18
    assert stats.proj_games_started == 30

    # Savant
    assert stats.velo == 93.5
    assert stats.spin_rate == 2425
    assert stats.release_extension == 6.1


def test_pitcher_stats_command_control_metrics():
    """Test command and control metrics from all sources."""
    stats = MtblPitcherStatsModel(
        # ESPN command metrics
        P_BB=42,
        K=195,
        WHIP=1.15,
        # FanGraphs command projections
        proj_walks=38,
        proj_strikeouts=205,
        proj_bb_per_9=1.90,
        proj_k_per_9=10.25,
        proj_k_per_bb=5.39,
        # Savant discipline metrics
        swing_miss_pct=29.2,
        BB_pct=6.8,
        whiffs=450,
        swings=1550,
        takes=850,
    )

    # ESPN
    assert stats.P_BB == 42
    assert stats.K == 195
    assert stats.WHIP == 1.15

    # FanGraphs
    assert stats.proj_walks == 38
    assert stats.proj_strikeouts == 205
    assert stats.proj_bb_per_9 == 1.90
    assert stats.proj_k_per_9 == 10.25
    assert stats.proj_k_per_bb == 5.39

    # Savant
    assert stats.swing_miss_pct == 29.2
    assert stats.BB_pct == 6.8
    assert stats.whiffs == 450
    assert stats.swings == 1550
    assert stats.takes == 850


def test_pitcher_stats_contact_quality_allowed():
    """Test contact quality metrics allowed from Savant."""
    stats = MtblPitcherStatsModel(
        exit_velo=87.5,
        adj_exit_velo=87.8,
        launch_angle=12.5,
        xavg=0.235,
        xslg=0.395,
        xwoba=0.305,
        BABIP=0.285,
        ISO=0.160,
    )

    assert stats.exit_velo == 87.5
    assert stats.adj_exit_velo == 87.8
    assert stats.launch_angle == 12.5
    assert stats.xavg == 0.235
    assert stats.xslg == 0.395
    assert stats.xwoba == 0.305
    assert stats.BABIP == 0.285
    assert stats.ISO == 0.160


def test_pitcher_stats_pitch_arsenal():
    """Test pitch arsenal metrics from Savant."""
    stats = MtblPitcherStatsModel(
        velo=94.2,
        spin_rate=2425,
        release_extension=6.3,
        break_z=18.5,
        break_x_arm_side=-8.2,
        induced_break_z=16.8,
        arm_angle=42.5,
        release_pos_x=-2.1,
        release_pos_z=5.8,
    )

    assert stats.velo == 94.2
    assert stats.spin_rate == 2425
    assert stats.release_extension == 6.3
    assert stats.break_z == 18.5
    assert stats.break_x_arm_side == -8.2
    assert stats.induced_break_z == 16.8
    assert stats.arm_angle == 42.5
    assert stats.release_pos_x == -2.1
    assert stats.release_pos_z == 5.8
