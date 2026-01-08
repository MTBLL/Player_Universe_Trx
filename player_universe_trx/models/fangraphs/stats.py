from typing import Optional

from pydantic import ConfigDict, Field

from player_universe_trx.models.fangraphs.fangraphs_player import (
    FangraphsBaseProjection,
)


class FangraphsBatterStatsModel(FangraphsBaseProjection):
    """FanGraphs batter projection statistics."""

    model_config = ConfigDict(populate_by_name=True)

    # Counting stats
    pa: Optional[float] = Field(default=None, description="Plate appearances")
    ab: Optional[float] = Field(default=None, description="At bats")
    h: Optional[float] = Field(default=None, description="Hits")
    singles: Optional[float] = Field(default=None, description="Singles")
    doubles: Optional[float] = Field(default=None, description="Doubles")
    triples: Optional[float] = Field(default=None, description="Triples")
    hr: Optional[float] = Field(default=None, description="Home runs")
    r: Optional[float] = Field(default=None, description="Runs")
    rbi: Optional[float] = Field(default=None, description="Runs batted in")
    bb: Optional[float] = Field(default=None, description="Walks")
    ibb: Optional[float] = Field(default=None, description="Intentional walks")
    so: Optional[float] = Field(default=None, description="Strikeouts")
    hbp: Optional[float] = Field(default=None, description="Hit by pitch")
    sf: Optional[float] = Field(default=None, description="Sacrifice flies")
    sh: Optional[float] = Field(default=None, description="Sacrifice hits")
    sb: Optional[float] = Field(default=None, description="Stolen bases")
    cs: Optional[float] = Field(default=None, description="Caught stealing")

    # Rate stats
    avg: Optional[float] = Field(default=None, description="Batting average")
    obp: Optional[float] = Field(default=None, description="On-base percentage")
    slg: Optional[float] = Field(default=None, description="Slugging percentage")
    ops: Optional[float] = Field(default=None, description="On-base plus slugging")
    iso: Optional[float] = Field(default=None, description="Isolated power")
    woba: Optional[float] = Field(default=None, description="Weighted on-base average")
    wrc_plus: Optional[float] = Field(default=None, description="Weighted runs created plus")
    bb_k: Optional[float] = Field(default=None, description="Walk to strikeout ratio")

    # Advanced metrics
    w_bsr: Optional[float] = Field(default=None, description="Weighted base running")
    spd: Optional[float] = Field(default=None, description="Speed score")
    wraa: Optional[float] = Field(default=None, description="Weighted runs above average")
    wrc: Optional[float] = Field(default=None, description="Weighted runs created")
    ubr: Optional[float] = Field(default=None, description="Ultimate base running")
    off: Optional[float] = Field(default=None, description="Offensive value")
    def_: Optional[float] = Field(default=None, description="Defensive value")
    uzr: Optional[float] = Field(default=None, description="Ultimate zone rating")
    base_running: Optional[float] = Field(default=None, description="Base running value")

    # Fantasy and uncertainty metrics
    fpts_g: Optional[float] = Field(default=None, description="Fantasy points per game")
    spts_g: Optional[float] = Field(default=None, description="Standard points per game")
    woba_sd: Optional[float] = Field(default=None, description="wOBA standard deviation")
    truetalent_sd: Optional[float] = Field(default=None, description="True talent standard deviation")
    woba_sd_book: Optional[float] = Field(default=None, description="wOBA SD book value")
    woba_se: Optional[float] = Field(default=None, description="wOBA standard error")
    total_se: Optional[float] = Field(default=None, description="Total standard error")


class FangraphsPitcherStatsModel(FangraphsBaseProjection):
    """FanGraphs pitcher projection statistics."""

    model_config = ConfigDict(populate_by_name=True)

    # Counting stats
    wins: Optional[float] = Field(default=None, description="Wins")
    losses: Optional[float] = Field(default=None, description="Losses")
    games_started: Optional[float] = Field(default=None, description="Games started")
    saves: Optional[float] = Field(default=None, description="Saves")
    holds: Optional[float] = Field(default=None, description="Holds")
    innings_pitched: Optional[float] = Field(default=None, description="Innings pitched")
    total_batters_faced: Optional[float] = Field(default=None, description="Total batters faced")
    hits: Optional[float] = Field(default=None, description="Hits allowed")
    runs: Optional[float] = Field(default=None, description="Runs allowed")
    earned_runs: Optional[float] = Field(default=None, description="Earned runs")
    home_runs: Optional[float] = Field(default=None, description="Home runs allowed")
    strikeouts: Optional[float] = Field(default=None, description="Strikeouts")
    walks: Optional[float] = Field(default=None, description="Walks allowed")
    intentional_walks: Optional[float] = Field(default=None, description="Intentional walks")
    hit_by_pitch: Optional[float] = Field(default=None, description="Hit batters")
    quality_starts: Optional[float] = Field(default=None, description="Quality starts")

    # Rate stats
    era: Optional[float] = Field(default=None, description="Earned run average")
    whip: Optional[float] = Field(default=None, description="Walks + hits per inning pitched")
    k_per_9: Optional[float] = Field(default=None, description="Strikeouts per 9 innings")
    bb_per_9: Optional[float] = Field(default=None, description="Walks per 9 innings")
    k_per_bb: Optional[float] = Field(default=None, description="Strikeout to walk ratio")
    hr_per_9: Optional[float] = Field(default=None, description="Home runs per 9 innings")
    k_bb_percent: Optional[float] = Field(default=None, description="K-BB percentage")
    gb_percent: Optional[float] = Field(default=None, description="Ground ball percentage")
    avg_against: Optional[float] = Field(default=None, description="Batting average against")
    lob_percent: Optional[float] = Field(default=None, description="Left on base percentage")

    # Advanced metrics
    fip: Optional[float] = Field(default=None, description="Fielding independent pitching")
    ra9_war: Optional[float] = Field(default=None, description="RA9 wins above replacement")

    # Fantasy and uncertainty metrics
    fpts_ip: Optional[float] = Field(default=None, description="Fantasy points per inning pitched")
    spts_ip: Optional[float] = Field(default=None, description="Standard points per inning pitched")
    ra_talent_sd: Optional[float] = Field(default=None, description="Run average talent standard deviation")
    chance_ra_se: Optional[float] = Field(default=None, description="Chance run average standard error")
    total_ra_se: Optional[float] = Field(default=None, description="Total run average standard error")
