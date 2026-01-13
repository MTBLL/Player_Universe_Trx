from typing import Optional

from pydantic import ConfigDict, Field, computed_field

from player_universe_trx.models.fangraphs.fangraphs_player import (
    FangraphsBaseProjection,
)


class FangraphsBatterStatsModel(FangraphsBaseProjection):
    """FanGraphs batter projection statistics."""

    model_config = ConfigDict(populate_by_name=True, ser_json_bytes="utf8", serialize_by_alias=True)

    # Counting stats
    pa: Optional[float] = Field(default=None, alias="PA", description="Plate appearances")
    ab: Optional[float] = Field(default=None, alias="AB", description="At bats")
    h: Optional[float] = Field(default=None, alias="H", description="Hits")
    singles: Optional[float] = Field(default=None, alias="1B", description="Singles")
    doubles: Optional[float] = Field(default=None, alias="2B", description="Doubles")
    triples: Optional[float] = Field(default=None, alias="3B", description="Triples")
    hr: Optional[float] = Field(default=None, alias="HR", description="Home runs")
    r: Optional[float] = Field(default=None, alias="R", description="Runs")
    rbi: Optional[float] = Field(default=None, alias="RBI", description="Runs batted in")
    bb: Optional[float] = Field(default=None, alias="BB", description="Walks")
    ibb: Optional[float] = Field(default=None, alias="IBB", description="Intentional walks")
    so: Optional[float] = Field(default=None, alias="SO", description="Strikeouts")
    hbp: Optional[float] = Field(default=None, alias="HBP", description="Hit by pitch")
    sf: Optional[float] = Field(default=None, alias="SF", description="Sacrifice flies")
    sh: Optional[float] = Field(default=None, alias="SH", description="Sacrifice hits")
    gdp: Optional[float] = Field(default=None, alias="GDP", description="Ground into double play")
    sb: Optional[float] = Field(default=None, alias="SB", description="Stolen bases")
    cs: Optional[float] = Field(default=None, alias="CS", description="Caught stealing")

    # Rate stats
    avg: Optional[float] = Field(default=None, alias="AVG", description="Batting average")
    obp: Optional[float] = Field(default=None, alias="OBP", description="On-base percentage")
    slg: Optional[float] = Field(default=None, alias="SLG", description="Slugging percentage")
    ops: Optional[float] = Field(default=None, alias="OPS", description="On-base plus slugging")
    iso: Optional[float] = Field(default=None, alias="ISO", description="Isolated power")
    woba: Optional[float] = Field(default=None, alias="wOBA", description="Weighted on-base average")
    wrc_plus: Optional[float] = Field(default=None, alias="wRC+", description="Weighted runs created plus")
    bb_k: Optional[float] = Field(default=None, alias="BB/K", description="Walk to strikeout ratio")
    babip: Optional[float] = Field(default=None, alias="BABIP", description="Batting average on balls in play")
    k_percent: Optional[float] = Field(default=None, alias="K%", description="Strikeout percentage")
    bb_percent: Optional[float] = Field(default=None, alias="BB%", description="Walk percentage")

    # Advanced metrics
    spd: Optional[float] = Field(default=None, alias="Spd", description="Speed score")
    wraa: Optional[float] = Field(default=None, alias="wRAA", description="Weighted runs above average")
    wrc: Optional[float] = Field(default=None, alias="wRC", description="Weighted runs created")
    wbsr: Optional[float] = Field(default=None, alias="wBsR", description="Weighted base running")
    ubr: Optional[float] = Field(default=None, alias="UBR", description="Ultimate base running")
    base_running: Optional[float] = Field(default=None, alias="BaseRunning", description="Base running runs")
    off: Optional[float] = Field(default=None, alias="Off", description="Offensive value")
    def_: Optional[float] = Field(default=None, alias="Def", description="Defensive value")
    uzr: Optional[float] = Field(default=None, alias="UZR", description="Ultimate zone rating")
    war: Optional[float] = Field(default=None, alias="WAR", description="Wins above replacement")

    # Fantasy metrics
    fpts_g: Optional[float] = Field(default=None, alias="FPTS_G", description="Fantasy points per game")
    spts_g: Optional[float] = Field(default=None, alias="SPTS_G", description="Standard points per game")

    @computed_field(alias="SBN")  # type: ignore[prop-decorator]
    @property
    def sbn(self) -> Optional[float]:
        """Net stolen bases (SB - CS)."""
        if self.sb is not None and self.cs is not None:
            return self.sb - self.cs
        elif self.sb is not None:
            return self.sb
        elif self.cs is not None:
            return -self.cs
        return None


class FangraphsPitcherStatsModel(FangraphsBaseProjection):
    """FanGraphs pitcher projection statistics."""

    model_config = ConfigDict(populate_by_name=True, ser_json_bytes="utf8", serialize_by_alias=True)

    # Counting stats
    wins: Optional[float] = Field(default=None, alias="W", description="Wins")
    losses: Optional[float] = Field(default=None, alias="L", description="Losses")
    games_started: Optional[float] = Field(default=None, alias="GS", description="Games started")
    saves: Optional[float] = Field(default=None, alias="SV", description="Saves")
    holds: Optional[float] = Field(default=None, alias="HLD", description="Holds")
    innings_pitched: Optional[float] = Field(default=None, alias="IP", description="Innings pitched")
    total_batters_faced: Optional[float] = Field(default=None, alias="TBF", description="Total batters faced")
    hits: Optional[float] = Field(default=None, alias="H", description="Hits allowed")
    runs: Optional[float] = Field(default=None, alias="R", description="Runs allowed")
    earned_runs: Optional[float] = Field(default=None, alias="ER", description="Earned runs")
    home_runs: Optional[float] = Field(default=None, alias="HR", description="Home runs allowed")
    strikeouts: Optional[float] = Field(default=None, alias="SO", description="Strikeouts")
    walks: Optional[float] = Field(default=None, alias="BB", description="Walks allowed")
    intentional_walks: Optional[float] = Field(default=None, alias="IBB", description="Intentional walks")
    hit_by_pitch: Optional[float] = Field(default=None, alias="HBP", description="Hit batters")

    # Rate stats
    era: Optional[float] = Field(default=None, alias="ERA", description="Earned run average")
    whip: Optional[float] = Field(default=None, alias="WHIP", description="Walks + hits per inning pitched")
    k_per_9: Optional[float] = Field(default=None, alias="K/9", description="Strikeouts per 9 innings")
    bb_per_9: Optional[float] = Field(default=None, alias="BB/9", description="Walks per 9 innings")
    k_per_bb: Optional[float] = Field(default=None, alias="K/BB", description="Strikeout to walk ratio")
    hr_per_9: Optional[float] = Field(default=None, alias="HR/9", description="Home runs per 9 innings")
    k_percent: Optional[float] = Field(default=None, alias="K%", description="Strikeout percentage")
    bb_percent: Optional[float] = Field(default=None, alias="BB%", description="Walk percentage")
    k_bb_percent: Optional[float] = Field(default=None, alias="K-BB%", description="K-BB percentage")
    avg_against: Optional[float] = Field(default=None, alias="AVG", description="Batting average against")
    babip: Optional[float] = Field(default=None, alias="BABIP", description="Batting average on balls in play")
    lob_percent: Optional[float] = Field(default=None, alias="LOB%", description="Left on base percentage")
    gb_percent: Optional[float] = Field(default=None, alias="GB%", description="Ground ball percentage")

    # Advanced metrics
    fip: Optional[float] = Field(default=None, alias="FIP", description="Fielding independent pitching")
    xfip: Optional[float] = Field(default=None, alias="xFIP", description="Expected fielding independent pitching")
    war: Optional[float] = Field(default=None, alias="WAR", description="Wins above replacement")
    ra9_war: Optional[float] = Field(default=None, alias="RA9-WAR", description="RA9 wins above replacement")
    qs: Optional[float] = Field(default=None, alias="QS", description="Quality starts")

    # Fantasy metrics
    fpts_ip: Optional[float] = Field(default=None, alias="FPTS_IP", description="Fantasy points per inning pitched")
    spts_ip: Optional[float] = Field(default=None, alias="SPTS_IP", description="Standard points per inning pitched")

    @computed_field(alias="SVHD")  # type: ignore[prop-decorator]
    @property
    def svhd(self) -> Optional[float]:
        """Combined saves and holds metric."""
        if self.saves is not None and self.holds is not None:
            return self.saves + self.holds
        elif self.saves is not None:
            return self.saves
        elif self.holds is not None:
            return self.holds
        return None
