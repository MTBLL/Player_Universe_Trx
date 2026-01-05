from typing import Optional

from pydantic import ConfigDict, Field

from player_universe_trx.models.savant.savant_player import SavantBaseStats


class SavantBatterStatsModel(SavantBaseStats):
    """Savant batter statistics including base stats plus batter-specific fields."""

    model_config = ConfigDict(populate_by_name=True)

    # Swing mechanics
    attack_angle: Optional[float] = Field(default=None, description="Attack angle")
    attack_dir: Optional[float] = Field(default=None, description="Attack direction")
    bat_speed: Optional[float] = Field(default=None, description="Bat speed")
    swing_length: Optional[float] = Field(default=None, description="Swing length")
    swing_path_tilt: Optional[float] = Field(default=None, description="Swing path tilt")

    # Performance metrics
    pitch_velo: Optional[float] = Field(default=None, description="Average pitch velocity faced")
    barrels_per_bbe_pct: Optional[float] = Field(default=None, description="Barrels per batted ball event percentage")
    barrels_per_pa_pct: Optional[float] = Field(default=None, description="Barrels per plate appearance percentage")
    hardhit_pct: Optional[float] = Field(default=None, description="Hard hit percentage")
    batter_run_value_per_100: Optional[float] = Field(default=None, description="Batter run value per 100 pitches")


class SavantPitcherStatsModel(SavantBaseStats):
    """Savant pitcher statistics including base stats plus pitcher-specific fields."""

    model_config = ConfigDict(populate_by_name=True)

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
