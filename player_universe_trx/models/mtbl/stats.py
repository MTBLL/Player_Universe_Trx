"""MTBL player statistics models combining ESPN, FanGraphs, and Savant data."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from player_universe_trx.models.espn.batter import EspnBatterStats
from player_universe_trx.models.espn.pitcher import EspnPitcherStats


class MtblBatterStatsModel(BaseModel):
    """
    MTBL batter statistics combining ESPN current stats, FanGraphs projections, and Savant sabermetrics.

    This model holds all three stat types in a single object since each source provides unique data:
    - ESPN: Current season statistics (actual performance)
    - FanGraphs: Projections (expected future performance)
    - Savant: Sabermetrics (advanced metrics like exit velocity, barrel rate, etc.)
    """

    model_config = ConfigDict(populate_by_name=True)

    # ========== ESPN Current Season Stats ==========
    # Batting statistics
    AB: Optional[float] = Field(default=None, description="At Bats (ESPN)")
    H: Optional[float] = Field(default=None, description="Hits (ESPN)")
    AVG: Optional[float] = Field(default=None, description="Batting Average (ESPN)")
    singles: Optional[float] = Field(default=None, alias="1B", description="Singles (ESPN)")
    doubles: Optional[float] = Field(default=None, alias="2B", description="Doubles (ESPN)")
    triples: Optional[float] = Field(default=None, alias="3B", description="Triples (ESPN)")
    HR: Optional[float] = Field(default=None, description="Home Runs (ESPN)")
    XBH: Optional[float] = Field(default=None, description="Extra Base Hits (ESPN)")
    TB: Optional[float] = Field(default=None, description="Total Bases (ESPN)")
    SLG: Optional[float] = Field(default=None, description="Slugging Percentage (ESPN)")

    # Plate discipline
    B_BB: Optional[float] = Field(default=None, description="Walks (ESPN)")
    B_IBB: Optional[float] = Field(default=None, description="Intentional Walks (ESPN)")
    HBP: Optional[float] = Field(default=None, description="Hit By Pitch (ESPN)")
    SF: Optional[float] = Field(default=None, description="Sacrifice Flies (ESPN)")
    SAC: Optional[float] = Field(default=None, description="Sacrifices (ESPN)")
    PA: Optional[float] = Field(default=None, description="Plate Appearances (ESPN)")
    OBP: Optional[float] = Field(default=None, description="On Base Percentage (ESPN)")
    OPS: Optional[float] = Field(default=None, description="On Base Plus Slugging (ESPN)")

    # Runs and RBIs
    R: Optional[float] = Field(default=None, description="Runs (ESPN)")
    RBI: Optional[float] = Field(default=None, description="Runs Batted In (ESPN)")

    # Stolen bases
    SB: Optional[float] = Field(default=None, description="Stolen Bases (ESPN)")
    CS: Optional[float] = Field(default=None, description="Caught Stealing (ESPN)")
    SBN: Optional[float] = Field(default=None, description="Stolen Base Net (ESPN)")

    # Other
    GDP: Optional[float] = Field(default=None, description="Grounded Into Double Play (ESPN)")
    B_SO: Optional[float] = Field(default=None, description="Strikeouts (ESPN)")
    G: Optional[float] = Field(default=None, description="Games (ESPN)")

    # ========== FanGraphs Projections ==========
    # Counting stats
    proj_pa: Optional[float] = Field(default=None, description="Projected Plate Appearances (FG)")
    proj_ab: Optional[float] = Field(default=None, description="Projected At Bats (FG)")
    proj_h: Optional[float] = Field(default=None, description="Projected Hits (FG)")
    proj_singles: Optional[float] = Field(default=None, description="Projected Singles (FG)")
    proj_doubles: Optional[float] = Field(default=None, description="Projected Doubles (FG)")
    proj_triples: Optional[float] = Field(default=None, description="Projected Triples (FG)")
    proj_hr: Optional[float] = Field(default=None, description="Projected Home Runs (FG)")
    proj_r: Optional[float] = Field(default=None, description="Projected Runs (FG)")
    proj_rbi: Optional[float] = Field(default=None, description="Projected RBIs (FG)")
    proj_bb: Optional[float] = Field(default=None, description="Projected Walks (FG)")
    proj_ibb: Optional[float] = Field(default=None, description="Projected Intentional Walks (FG)")
    proj_so: Optional[float] = Field(default=None, description="Projected Strikeouts (FG)")
    proj_hbp: Optional[float] = Field(default=None, description="Projected Hit By Pitch (FG)")
    proj_sf: Optional[float] = Field(default=None, description="Projected Sacrifice Flies (FG)")
    proj_sh: Optional[float] = Field(default=None, description="Projected Sacrifice Hits (FG)")
    proj_sb: Optional[float] = Field(default=None, description="Projected Stolen Bases (FG)")
    proj_cs: Optional[float] = Field(default=None, description="Projected Caught Stealing (FG)")

    # Rate stats
    proj_avg: Optional[float] = Field(default=None, description="Projected Batting Average (FG)")
    proj_obp: Optional[float] = Field(default=None, description="Projected On-Base Percentage (FG)")
    proj_slg: Optional[float] = Field(default=None, description="Projected Slugging (FG)")
    proj_ops: Optional[float] = Field(default=None, description="Projected OPS (FG)")
    proj_iso: Optional[float] = Field(default=None, description="Projected Isolated Power (FG)")
    proj_woba: Optional[float] = Field(default=None, description="Projected wOBA (FG)")
    proj_wrc_plus: Optional[float] = Field(default=None, description="Projected wRC+ (FG)")
    proj_bb_k: Optional[float] = Field(default=None, description="Projected BB/K (FG)")

    # Advanced metrics
    proj_w_bsr: Optional[float] = Field(default=None, description="Projected Weighted Base Running (FG)")
    proj_spd: Optional[float] = Field(default=None, description="Projected Speed Score (FG)")
    proj_wraa: Optional[float] = Field(default=None, description="Projected wRAA (FG)")
    proj_wrc: Optional[float] = Field(default=None, description="Projected wRC (FG)")
    proj_ubr: Optional[float] = Field(default=None, description="Projected UBR (FG)")
    proj_off: Optional[float] = Field(default=None, description="Projected Offensive Value (FG)")
    proj_def: Optional[float] = Field(default=None, description="Projected Defensive Value (FG)")
    proj_uzr: Optional[float] = Field(default=None, description="Projected UZR (FG)")
    proj_base_running: Optional[float] = Field(default=None, description="Projected Base Running Value (FG)")

    # Fantasy and uncertainty metrics
    proj_fpts_g: Optional[float] = Field(default=None, description="Projected Fantasy Pts/G (FG)")
    proj_spts_g: Optional[float] = Field(default=None, description="Projected Standard Pts/G (FG)")
    proj_woba_sd: Optional[float] = Field(default=None, description="Projected wOBA SD (FG)")
    proj_truetalent_sd: Optional[float] = Field(default=None, description="Projected True Talent SD (FG)")
    proj_woba_sd_book: Optional[float] = Field(default=None, description="Projected wOBA SD Book (FG)")
    proj_woba_se: Optional[float] = Field(default=None, description="Projected wOBA SE (FG)")
    proj_total_se: Optional[float] = Field(default=None, description="Projected Total SE (FG)")

    # ========== Savant Sabermetrics ==========
    # Contact metrics
    exit_velo: Optional[float] = Field(default=None, description="Exit Velocity (Savant)")
    adj_exit_velo: Optional[float] = Field(default=None, description="Adjusted Exit Velocity (Savant)")
    launch_angle: Optional[float] = Field(default=None, description="Launch Angle (Savant)")

    # Swing mechanics
    attack_angle: Optional[float] = Field(default=None, description="Attack Angle (Savant)")
    attack_dir: Optional[float] = Field(default=None, description="Attack Direction (Savant)")
    bat_speed: Optional[float] = Field(default=None, description="Bat Speed (Savant)")
    swing_length: Optional[float] = Field(default=None, description="Swing Length (Savant)")
    swing_path_tilt: Optional[float] = Field(default=None, description="Swing Path Tilt (Savant)")

    # Plate discipline
    swing_miss_pct: Optional[float] = Field(default=None, description="Swing & Miss % (Savant)")
    swings: Optional[int] = Field(default=None, description="Number of Swings (Savant)")
    takes: Optional[int] = Field(default=None, description="Number of Takes (Savant)")
    whiffs: Optional[int] = Field(default=None, description="Number of Whiffs (Savant)")

    # Performance metrics
    barrel_rate: Optional[float] = Field(default=None, description="Barrel Rate (Savant)")
    barrels_per_bbe_pct: Optional[float] = Field(default=None, description="Barrels per BBE % (Savant)")
    barrels_per_pa_pct: Optional[float] = Field(default=None, description="Barrels per PA % (Savant)")
    barrels_total: Optional[int] = Field(default=None, description="Total Barrels (Savant)")
    hard_hit_rate: Optional[float] = Field(default=None, description="Hard Hit % (Savant)")
    hardhit_pct: Optional[float] = Field(default=None, description="Hard Hit Pct (Savant)")
    batter_run_value_per_100: Optional[float] = Field(default=None, description="Run Value per 100 (Savant)")

    # Expected stats
    xwoba: Optional[float] = Field(default=None, description="Expected wOBA (Savant)")
    xavg: Optional[float] = Field(default=None, description="Expected AVG (Savant)")
    xslg: Optional[float] = Field(default=None, description="Expected SLG (Savant)")
    xAVG: Optional[float] = Field(default=None, description="Expected Batting Average (Savant)")
    xAVGdiff: Optional[float] = Field(default=None, description="Expected AVG Differential (Savant)")
    xOBP: Optional[float] = Field(default=None, description="Expected OBP (Savant)")
    xOBPdiff: Optional[float] = Field(default=None, description="Expected OBP Differential (Savant)")
    xSLG: Optional[float] = Field(default=None, description="Expected SLG (Savant)")
    xSLGdiff: Optional[float] = Field(default=None, description="Expected SLG Differential (Savant)")
    xwOBA: Optional[float] = Field(default=None, description="Expected wOBA (Savant)")

    # Other Savant stats
    BABIP: Optional[float] = Field(default=None, description="BABIP (Savant)")
    BB: Optional[int] = Field(default=None, description="Walks (Savant)")
    BB_pct: Optional[float] = Field(default=None, alias="BB%", description="Walk % (Savant)")
    BBdist: Optional[int] = Field(default=None, description="Walk Distance (Savant)")
    BIP: Optional[int] = Field(default=None, description="Balls In Play (Savant)")
    ISO: Optional[float] = Field(default=None, description="Isolated Power (Savant)")
    K: Optional[int] = Field(default=None, description="Strikeouts (Savant)")
    K_pct: Optional[float] = Field(default=None, alias="K%", description="Strikeout % (Savant)")
    wOBA: Optional[float] = Field(default=None, description="wOBA (Savant)")
    wOBAdiff: Optional[float] = Field(default=None, description="wOBA Differential (Savant)")
    run_exp: Optional[float] = Field(default=None, description="Run Expectancy (Savant)")
    rate_ideal_attack_angle: Optional[float] = Field(default=None, description="Rate Ideal Attack Angle (Savant)")
    pitch_velo: Optional[float] = Field(default=None, description="Avg Pitch Velocity Faced (Savant)")

    # ========== ESPN Stats Container ==========
    # Holds all ESPN stat periods: projections, last_7_games, last_15_games, last_30_games, previous_season_24
    espn_stats: Optional[EspnBatterStats] = Field(default=None, description="ESPN stats container with all periods")


class MtblPitcherStatsModel(BaseModel):
    """
    MTBL pitcher statistics combining ESPN current stats, FanGraphs projections, and Savant sabermetrics.

    This model holds all three stat types in a single object since each source provides unique data:
    - ESPN: Current season statistics (actual performance)
    - FanGraphs: Projections (expected future performance)
    - Savant: Sabermetrics (advanced metrics like spin rate, velocity, etc.)
    """

    model_config = ConfigDict(populate_by_name=True)

    # ========== ESPN Current Season Stats ==========
    # Pitching statistics
    GP: Optional[float] = Field(default=None, description="Games Pitched (ESPN)")
    GS: Optional[float] = Field(default=None, description="Games Started (ESPN)")
    OUTS: Optional[float] = Field(default=None, description="Outs Recorded (ESPN)")
    TBF: Optional[float] = Field(default=None, description="Total Batters Faced (ESPN)")
    P_H: Optional[float] = Field(default=None, description="Hits Allowed (ESPN)")
    OBA: Optional[float] = Field(default=None, description="Opponent Batting Average (ESPN)")
    P_BB: Optional[float] = Field(default=None, description="Walks Allowed (ESPN)")
    WHIP: Optional[float] = Field(default=None, description="WHIP (ESPN)")
    OOBP: Optional[float] = Field(default=None, description="Opponent OBP (ESPN)")
    P_R: Optional[float] = Field(default=None, description="Runs Allowed (ESPN)")
    ER: Optional[float] = Field(default=None, description="Earned Runs (ESPN)")
    P_HR: Optional[float] = Field(default=None, description="Home Runs Allowed (ESPN)")
    ERA: Optional[float] = Field(default=None, description="ERA (ESPN)")
    K: Optional[float] = Field(default=None, description="Strikeouts (ESPN)")
    WP: Optional[float] = Field(default=None, description="Wild Pitches (ESPN)")
    W: Optional[float] = Field(default=None, description="Wins (ESPN)")
    L: Optional[float] = Field(default=None, description="Losses (ESPN)")
    WPCT: Optional[float] = Field(default=None, description="Win Percentage (ESPN)")
    QS: Optional[float] = Field(default=None, description="Quality Starts (ESPN)")
    k_bb_ratio: Optional[float] = Field(default=None, alias="K/BB", description="K/BB Ratio (ESPN)")

    # ========== FanGraphs Projections ==========
    # Counting stats
    proj_wins: Optional[float] = Field(default=None, description="Projected Wins (FG)")
    proj_losses: Optional[float] = Field(default=None, description="Projected Losses (FG)")
    proj_games_started: Optional[float] = Field(default=None, description="Projected GS (FG)")
    proj_saves: Optional[float] = Field(default=None, description="Projected Saves (FG)")
    proj_holds: Optional[float] = Field(default=None, description="Projected Holds (FG)")
    proj_innings_pitched: Optional[float] = Field(default=None, description="Projected IP (FG)")
    proj_total_batters_faced: Optional[float] = Field(default=None, description="Projected TBF (FG)")
    proj_hits: Optional[float] = Field(default=None, description="Projected Hits Allowed (FG)")
    proj_runs: Optional[float] = Field(default=None, description="Projected Runs Allowed (FG)")
    proj_earned_runs: Optional[float] = Field(default=None, description="Projected ER (FG)")
    proj_home_runs: Optional[float] = Field(default=None, description="Projected HR Allowed (FG)")
    proj_strikeouts: Optional[float] = Field(default=None, description="Projected Strikeouts (FG)")
    proj_walks: Optional[float] = Field(default=None, description="Projected Walks (FG)")
    proj_intentional_walks: Optional[float] = Field(default=None, description="Projected IBB (FG)")
    proj_hit_by_pitch: Optional[float] = Field(default=None, description="Projected HBP (FG)")
    proj_quality_starts: Optional[float] = Field(default=None, description="Projected QS (FG)")

    # Rate stats
    proj_era: Optional[float] = Field(default=None, description="Projected ERA (FG)")
    proj_whip: Optional[float] = Field(default=None, description="Projected WHIP (FG)")
    proj_k_per_9: Optional[float] = Field(default=None, description="Projected K/9 (FG)")
    proj_bb_per_9: Optional[float] = Field(default=None, description="Projected BB/9 (FG)")
    proj_k_per_bb: Optional[float] = Field(default=None, description="Projected K/BB (FG)")
    proj_hr_per_9: Optional[float] = Field(default=None, description="Projected HR/9 (FG)")
    proj_k_bb_percent: Optional[float] = Field(default=None, description="Projected K-BB% (FG)")
    proj_gb_percent: Optional[float] = Field(default=None, description="Projected GB% (FG)")
    proj_avg_against: Optional[float] = Field(default=None, description="Projected AVG Against (FG)")
    proj_lob_percent: Optional[float] = Field(default=None, description="Projected LOB% (FG)")

    # Advanced metrics
    proj_fip: Optional[float] = Field(default=None, description="Projected FIP (FG)")
    proj_ra9_war: Optional[float] = Field(default=None, description="Projected RA9-WAR (FG)")

    # Fantasy and uncertainty metrics
    proj_fpts_ip: Optional[float] = Field(default=None, description="Projected Fantasy Pts/IP (FG)")
    proj_spts_ip: Optional[float] = Field(default=None, description="Projected Standard Pts/IP (FG)")
    proj_ra_talent_sd: Optional[float] = Field(default=None, description="Projected RA Talent SD (FG)")
    proj_chance_ra_se: Optional[float] = Field(default=None, description="Projected Chance RA SE (FG)")
    proj_total_ra_se: Optional[float] = Field(default=None, description="Projected Total RA SE (FG)")

    # ========== Savant Sabermetrics ==========
    # Pitch characteristics
    velo: Optional[float] = Field(default=None, description="Pitch Velocity (Savant)")
    spin_rate: Optional[float] = Field(default=None, description="Spin Rate (Savant)")
    eff_min_vel: Optional[float] = Field(default=None, description="Effective Min Velocity (Savant)")
    percieved_velo: Optional[float] = Field(default=None, description="Perceived Velocity (Savant)")

    # Release point
    release_extension: Optional[float] = Field(default=None, description="Release Extension (Savant)")
    release_pos_x: Optional[float] = Field(default=None, description="Release Position X (Savant)")
    release_pos_z: Optional[float] = Field(default=None, description="Release Position Z (Savant)")

    # Pitch movement
    break_z: Optional[float] = Field(default=None, description="Vertical Break (Savant)")
    induced_break_z: Optional[float] = Field(default=None, description="Induced Vertical Break (Savant)")
    break_x_arm_side: Optional[float] = Field(default=None, description="Horizontal Break Arm Side (Savant)")
    break_x_batter_in: Optional[float] = Field(default=None, description="Horizontal Break Batter In (Savant)")

    # Mechanics and performance
    arm_angle: Optional[float] = Field(default=None, description="Arm Angle (Savant)")
    pitcher_run_exp: Optional[float] = Field(default=None, description="Pitcher Run Expectancy (Savant)")
    pitcher_run_value_per_100: Optional[float] = Field(default=None, description="Run Value per 100 (Savant)")

    # Contact/Batted ball metrics
    exit_velo: Optional[float] = Field(default=None, description="Exit Velocity Against (Savant)")
    adj_exit_velo: Optional[float] = Field(default=None, description="Adjusted Exit Velo Against (Savant)")
    launch_angle: Optional[float] = Field(default=None, description="Launch Angle Against (Savant)")

    # Plate discipline
    swing_miss_pct: Optional[float] = Field(default=None, description="Swing & Miss % (Savant)")
    swings: Optional[int] = Field(default=None, description="Swings Against (Savant)")
    takes: Optional[int] = Field(default=None, description="Takes (Savant)")
    whiffs: Optional[int] = Field(default=None, description="Whiffs (Savant)")

    # Expected stats
    xwoba: Optional[float] = Field(default=None, description="xwOBA Against (Savant)")
    xavg: Optional[float] = Field(default=None, description="xAVG Against (Savant)")
    xslg: Optional[float] = Field(default=None, description="xSLG Against (Savant)")
    xAVG: Optional[float] = Field(default=None, description="Expected AVG Against (Savant)")
    xAVGdiff: Optional[float] = Field(default=None, description="Expected AVG Diff (Savant)")
    xOBP: Optional[float] = Field(default=None, description="Expected OBP Against (Savant)")
    xOBPdiff: Optional[float] = Field(default=None, description="Expected OBP Diff (Savant)")
    xSLG: Optional[float] = Field(default=None, description="Expected SLG Against (Savant)")
    xSLGdiff: Optional[float] = Field(default=None, description="Expected SLG Diff (Savant)")
    xwOBA: Optional[float] = Field(default=None, description="Expected wOBA Against (Savant)")

    # Other Savant stats
    BABIP: Optional[float] = Field(default=None, description="BABIP Against (Savant)")
    BB: Optional[int] = Field(default=None, description="Walks (Savant)")
    BB_pct: Optional[float] = Field(default=None, alias="BB%", description="Walk % (Savant)")
    BBdist: Optional[int] = Field(default=None, description="Walk Distance (Savant)")
    BIP: Optional[int] = Field(default=None, description="Balls In Play Against (Savant)")
    ISO: Optional[float] = Field(default=None, description="ISO Against (Savant)")
    wOBA: Optional[float] = Field(default=None, description="wOBA Against (Savant)")
    wOBAdiff: Optional[float] = Field(default=None, description="wOBA Differential (Savant)")
    run_exp: Optional[float] = Field(default=None, description="Run Expectancy (Savant)")
    barrels_total: Optional[int] = Field(default=None, description="Barrels Allowed (Savant)")
    rate_ideal_attack_angle: Optional[float] = Field(default=None, description="Rate Ideal Attack Angle (Savant)")

    # ========== ESPN Stats Container ==========
    # Holds all ESPN stat periods: projections, last_7_games, last_15_games, last_30_games, previous_season_24
    espn_stats: Optional[EspnPitcherStats] = Field(default=None, description="ESPN stats container with all periods")
