"""MTBL player statistics models.

The MTBL stats container is a source-by-source bundle: ESPN data lives under
`espn`, FanGraphs projections under `fangraphs`, and Savant Statcast data
under `savant`. This keeps the data shape parallel across sources — each
namespace is a self-contained reflection of what that upstream emits, and no
cross-source merging happens in this layer (each consumer reaches for the
source it cares about).
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from player_universe_trx.models.espn.batter import EspnBatterStatsGroupModel
from player_universe_trx.models.espn.pitcher import EspnPitcherStatsGroupModel
from player_universe_trx.models.fangraphs.stats import (
    FangraphsBatterStatsModel,
    FangraphsPitcherStatsModel,
)
from player_universe_trx.models.savant.stats import (
    SavantBatterStatsModel,
    SavantHomeRunsModel,
    SavantPitcherExpectedStatsModel,
    SavantPitcherStatsModel,
    SavantPitchArsenalEntryModel,
    SavantSprintSpeedModel,
    SavantStatcastModel,
)


# ============================================================
# FanGraphs bundles — three projection slots under one namespace
# ============================================================


class MtblBatterFangraphsBundle(BaseModel):
    """All FanGraphs-derived data for a batter — three projection slots."""

    model_config = ConfigDict(populate_by_name=True)

    projections: Optional[FangraphsBatterStatsModel] = Field(
        default=None,
        description="FanGraphs preseason projection (canonical mix; carries q*/tt_q* percentiles)",
    )
    projs_updated: Optional[FangraphsBatterStatsModel] = Field(
        default=None,
        description="FanGraphs in-season updated full-year projection (None pre-draft)",
    )
    ros: Optional[FangraphsBatterStatsModel] = Field(
        default=None,
        description="FanGraphs rest-of-season projection (None pre-draft)",
    )


class MtblPitcherFangraphsBundle(BaseModel):
    """All FanGraphs-derived data for a pitcher — three projection slots."""

    model_config = ConfigDict(populate_by_name=True)

    projections: Optional[FangraphsPitcherStatsModel] = Field(
        default=None,
        description="FanGraphs preseason projection (canonical mix; carries q*/tt_q* percentiles)",
    )
    projs_updated: Optional[FangraphsPitcherStatsModel] = Field(
        default=None,
        description="FanGraphs in-season updated full-year projection (None pre-draft)",
    )
    ros: Optional[FangraphsPitcherStatsModel] = Field(
        default=None,
        description="FanGraphs rest-of-season projection (None pre-draft)",
    )


# ============================================================
# Savant bundles — splits + sub-domain stats under one namespace
# ============================================================


class MtblBatterSavantBundle(BaseModel):
    """All Savant-derived data for a batter."""

    model_config = ConfigDict(populate_by_name=True)

    all: Optional[SavantBatterStatsModel] = Field(
        default=None, description="Overall (swing/take) stats"
    )
    vs_r: Optional[SavantBatterStatsModel] = Field(
        default=None,
        description="Swing/take stats facing right-handed pitchers (None if no sample)",
    )
    vs_l: Optional[SavantBatterStatsModel] = Field(
        default=None,
        description="Swing/take stats facing left-handed pitchers (None if no sample)",
    )
    statcast: Optional[SavantStatcastModel] = Field(
        default=None, description="Batted-ball quality summary (ev50, barrels, ...)"
    )
    home_runs: Optional[SavantHomeRunsModel] = Field(
        default=None,
        description="HR-quality metrics (xHR, doubters, mostly_gone, ...)",
    )
    pitch_arsenal: List[SavantPitchArsenalEntryModel] = Field(
        default_factory=list,
        description="Performance per pitch_type (FF/SI/SL/CH/...) the batter faced",
    )
    sprint_speed: Optional[SavantSprintSpeedModel] = Field(
        default=None,
        description="Baserunning sprint-speed metrics (batter-only domain)",
    )


class MtblPitcherSavantBundle(BaseModel):
    """All Savant-derived data for a pitcher."""

    model_config = ConfigDict(populate_by_name=True)

    all: Optional[SavantPitcherStatsModel] = Field(
        default=None, description="Overall (per-pitch) stats"
    )
    vs_r: Optional[SavantPitcherStatsModel] = Field(
        default=None,
        description="Per-pitch stats facing right-handed batters (None if no sample)",
    )
    vs_l: Optional[SavantPitcherStatsModel] = Field(
        default=None,
        description="Per-pitch stats facing left-handed batters (None if no sample)",
    )
    statcast: Optional[SavantStatcastModel] = Field(
        default=None,
        description="Contact-allowed quality summary (ev50, barrels, ...)",
    )
    home_runs: Optional[SavantHomeRunsModel] = Field(
        default=None, description="HR-allowed quality metrics (xHR, doubters, ...)"
    )
    pitch_arsenal: List[SavantPitchArsenalEntryModel] = Field(
        default_factory=list,
        description="Performance per pitch_type (FF/SI/SL/...) the pitcher throws",
    )
    expected_statistics: Optional[SavantPitcherExpectedStatsModel] = Field(
        default=None,
        description="xAVG/xSLG/xwOBA/xERA summary (pitcher-only domain)",
    )


# ============================================================
# Top-level MTBL stats containers — three-namespace layout
# ============================================================


class MtblBatterStatsModel(BaseModel):
    """MTBL batter statistics — three source-by-source namespaces.

    No cross-source merging happens here. Each consumer reaches for the source
    namespace they care about (e.g., `stats.espn.current_season.HR` for
    actuals, `stats.fangraphs.projections.HR` for preseason projection,
    `stats.savant.all.xwOBA` for sabermetrics).
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    espn: Optional[EspnBatterStatsGroupModel] = Field(
        default=None,
        description="ESPN bundle: current_season + projections + last_*_games + previous_season",
    )
    fangraphs: Optional[MtblBatterFangraphsBundle] = Field(
        default=None,
        description="FanGraphs bundle: preseason / projs_updated / ros projections",
    )
    savant: Optional[MtblBatterSavantBundle] = Field(
        default=None,
        description="Savant bundle: all/vs_r/vs_l splits + statcast / home_runs / pitch_arsenal / sprint_speed",
    )


class MtblPitcherStatsModel(BaseModel):
    """MTBL pitcher statistics — three source-by-source namespaces."""

    model_config = ConfigDict(populate_by_name=True)

    espn: Optional[EspnPitcherStatsGroupModel] = Field(
        default=None,
        description="ESPN bundle: current_season + projections + last_*_games + previous_season",
    )
    fangraphs: Optional[MtblPitcherFangraphsBundle] = Field(
        default=None,
        description="FanGraphs bundle: preseason / projs_updated / ros projections",
    )
    savant: Optional[MtblPitcherSavantBundle] = Field(
        default=None,
        description="Savant bundle: all/vs_r/vs_l splits + statcast / home_runs / pitch_arsenal / expected_statistics",
    )
