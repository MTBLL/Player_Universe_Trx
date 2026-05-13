from typing import Optional

from pydantic import BaseModel, Field

from player_universe_trx.models.savant.savant_player import (
    SAVANT_STATS_MODEL_CONFIG,
    SavantBaseStats,
)


class SavantBatterStatsModel(SavantBaseStats):
    """Savant batter statistics including base stats plus batter-specific fields."""

    model_config = SAVANT_STATS_MODEL_CONFIG

    # Swing mechanics
    attack_angle: Optional[float] = Field(default=None, description="Attack angle")
    attack_dir: Optional[float] = Field(default=None, description="Attack direction")
    bat_speed: Optional[float] = Field(default=None, description="Bat speed")
    swing_length: Optional[float] = Field(default=None, description="Swing length")
    swing_path_tilt: Optional[float] = Field(default=None, description="Swing path tilt")

    # Performance metrics
    pitch_velo: Optional[float] = Field(default=None, description="Average pitch velocity faced")
    batter_run_value_per_100: Optional[float] = Field(default=None, description="Batter run value per 100 pitches")


class SavantPitcherStatsModel(SavantBaseStats):
    """Savant pitcher statistics including base stats plus pitcher-specific fields."""

    model_config = SAVANT_STATS_MODEL_CONFIG

    # Pitch characteristics
    velo: Optional[float] = Field(default=None, description="Pitch velocity")
    spin_rate: Optional[float] = Field(default=None, description="Spin rate")
    eff_min_vel: Optional[float] = Field(default=None, description="Effective minimum velocity")

    # Release point
    release_extension: Optional[float] = Field(default=None, description="Release extension")
    release_pos_x: Optional[float] = Field(default=None, description="Release position X")
    release_pos_z: Optional[float] = Field(default=None, description="Release position Z")

    # Pitch movement
    break_z: Optional[float] = Field(default=None, description="Vertical break")
    induced_break_z: Optional[float] = Field(default=None, description="Induced vertical break")
    break_x_arm_side: Optional[float] = Field(default=None, description="Horizontal break (arm side)")
    break_x_batter_in: Optional[float] = Field(default=None, description="Horizontal break (batter in)")

    # Mechanics and performance
    arm_angle: Optional[float] = Field(default=None, description="Arm angle")
    pitcher_run_exp: Optional[float] = Field(default=None, description="Pitcher run expectancy")
    pitcher_run_value_per_100: Optional[float] = Field(default=None, description="Pitcher run value per 100 pitches")


# ====================== Statcast (batted-ball quality) ======================


class SavantStatcastModel(BaseModel):
    """Statcast batted-ball quality summary, shared shape for batters and pitchers.

    Sourced from `savant_statcast_{batter,pitcher}_*.json`. The numeric fields
    are identical between roles — for pitchers, the values describe contact
    allowed rather than contact generated.
    """

    model_config = SAVANT_STATS_MODEL_CONFIG

    bbe: Optional[int] = Field(default=None, description="Batted-ball events")
    avg_launch_angle: Optional[float] = Field(default=None, description="Average launch angle")
    sweetspot_pct: Optional[float] = Field(default=None, description="Sweet-spot %")
    max_ev: Optional[float] = Field(default=None, description="Max exit velocity")
    avg_ev: Optional[float] = Field(default=None, description="Average exit velocity")
    ev50: Optional[float] = Field(default=None, description="50th-percentile exit velocity")
    fbld_ev: Optional[float] = Field(default=None, description="Fly-ball/line-drive exit velocity")
    gb_ev: Optional[float] = Field(default=None, description="Ground-ball exit velocity")
    max_distance: Optional[int] = Field(default=None, description="Max batted-ball distance (ft)")
    avg_distance: Optional[int] = Field(default=None, description="Average batted-ball distance (ft)")
    avg_hr_distance: Optional[float] = Field(default=None, description="Average HR distance (ft)")
    ev95_plus: Optional[int] = Field(default=None, description="Count of batted balls at 95+ EV")
    ev95_pct: Optional[float] = Field(default=None, description="% of batted balls at 95+ EV")
    barrels: Optional[int] = Field(default=None, description="Barrel count")
    barrels_per_bbe_pct: Optional[float] = Field(default=None, description="Barrels per BBE %")
    barrels_per_pa_pct: Optional[float] = Field(default=None, description="Barrels per PA %")


# ====================== Home runs (HR quality) ======================


class SavantHomeRunsModel(BaseModel):
    """Home-run quality metrics from `savant_home_runs_{batter,pitcher}_*.json`.

    Shared shape across both roles. The fields describe HR quality (e.g.,
    "no-doubter" vs. "mostly gone") and an expected-HR projection.
    """

    model_config = SAVANT_STATS_MODEL_CONFIG

    year: Optional[int] = Field(default=None, description="Season")
    hr_type: Optional[str] = Field(default=None, description="HR projection variant identifier (currently 'adj_xhr')")
    HR: Optional[int] = Field(default=None, description="Home runs (actual)")
    xHR: Optional[float] = Field(default=None, description="Expected HR")
    xHRdiff: Optional[float] = Field(default=None, description="HR minus xHR")
    avg_hr_trot: Optional[float] = Field(default=None, description="Average HR trot time (s)")
    doubters: Optional[int] = Field(default=None, description="Borderline HR count (would-be HR in some parks)")
    mostly_gone: Optional[int] = Field(default=None, description="HR count that cleared most parks")
    no_doubters: Optional[int] = Field(default=None, description="HR count cleared in every park")
    no_doubter_pct: Optional[float] = Field(default=None, description="% of HR classed as no-doubters")


# ====================== Pitch arsenal (per pitch_type) ======================


class SavantPitchArsenalEntryModel(BaseModel):
    """One per-pitch-type entry from `savant_pitch_arsenal_stats_{batter,pitcher}_*.json`.

    The wire emits one row per (player_id, pitch_type), so a player carries a
    list of these. For batters: stats describe the player's performance
    against that pitch type. For pitchers: stats describe the player's
    own pitch.
    """

    model_config = SAVANT_STATS_MODEL_CONFIG

    pitch_type: Optional[str] = Field(default=None, description="Pitch-type code (e.g. FF, SI, SL)")
    pitch_name: Optional[str] = Field(default=None, description="Human-readable pitch name")
    pitches: Optional[int] = Field(default=None, description="Pitches in sample for this pitch type")
    pitch_usage_pct: Optional[float] = Field(default=None, description="% of total pitches that are this type")
    PA: Optional[int] = Field(default=None, description="Plate appearances ending on this pitch type")
    AVG: Optional[float] = Field(default=None, description="Batting average on this pitch type")
    SLG: Optional[float] = Field(default=None, description="SLG on this pitch type")
    wOBA: Optional[float] = Field(default=None, description="wOBA on this pitch type")
    xAVG: Optional[float] = Field(default=None, description="xAVG on this pitch type")
    xSLG: Optional[float] = Field(default=None, description="xSLG on this pitch type")
    xwOBA: Optional[float] = Field(default=None, description="xwOBA on this pitch type")
    K_pct: Optional[float] = Field(default=None, alias="K%", description="K% on this pitch type")
    whiff_pct: Optional[float] = Field(default=None, description="Whiff % on this pitch type")
    put_away_pct: Optional[float] = Field(default=None, description="Put-away % on this pitch type")
    hardhit_pct: Optional[float] = Field(default=None, description="Hard-hit % on this pitch type")
    run_value: Optional[int] = Field(default=None, description="Run value on this pitch type")
    run_value_per_100: Optional[float] = Field(default=None, description="Run value per 100 pitches on this type")


# ====================== Sprint speed (batter only) ======================


class SavantSprintSpeedModel(BaseModel):
    """Baserunning sprint-speed metrics from `savant_sprint_speed_*.json`.

    Batter-only in practice — the wire file mixes non-pitcher positions
    only (no `P` in `position`).
    """

    model_config = SAVANT_STATS_MODEL_CONFIG

    age: Optional[int] = Field(default=None, description="Player age")
    position: Optional[str] = Field(default=None, description="Primary defensive position")
    sprint_speed: Optional[float] = Field(default=None, description="Sprint speed (ft/s, 30 = MLB avg)")
    hp_to_1b: Optional[float] = Field(default=None, description="Home-plate-to-first time (s)")
    bolts: Optional[float] = Field(default=None, description="Count of 30+ ft/s runs ('bolts')")
    competitive_runs: Optional[int] = Field(default=None, description="Qualified competitive runs in sample")


# ====================== Expected statistics (pitcher only) ======================


class SavantPitcherExpectedStatsModel(BaseModel):
    """Pitcher-only expected-stats summary from `savant_expected_statistics_pitcher_*.json`.

    Mirrors `xAVG / xSLG / xwOBA / xERA` plus their actual/diff counterparts.
    """

    model_config = SAVANT_STATS_MODEL_CONFIG

    year: Optional[int] = Field(default=None, description="Season")
    PA: Optional[int] = Field(default=None, description="Plate appearances")
    BIP: Optional[int] = Field(default=None, description="Balls in play")
    AVG: Optional[float] = Field(default=None, description="Batting average against")
    xAVG: Optional[float] = Field(default=None, description="Expected batting average against")
    xAVGdiff: Optional[float] = Field(default=None, description="AVG minus xAVG")
    SLG: Optional[float] = Field(default=None, description="SLG against")
    xSLG: Optional[float] = Field(default=None, description="Expected SLG against")
    xSLGdiff: Optional[float] = Field(default=None, description="SLG minus xSLG")
    wOBA: Optional[float] = Field(default=None, description="wOBA against")
    xwOBA: Optional[float] = Field(default=None, description="Expected wOBA against")
    wOBAdiff: Optional[float] = Field(default=None, description="wOBA minus xwOBA")
    ERA: Optional[float] = Field(default=None, description="ERA")
    xERA: Optional[float] = Field(default=None, description="Expected ERA")
    xERAdiff: Optional[float] = Field(default=None, description="ERA minus xERA")
