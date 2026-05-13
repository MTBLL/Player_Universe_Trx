"""Tests for MtblBatterStatsModel — three source-by-source bundles (espn / fangraphs / savant)."""

from player_universe_trx.models.espn.batter import EspnBatterStatsGroupModel
from player_universe_trx.models.espn.stats import EspnBatterStatsModel
from player_universe_trx.models.fangraphs.stats import FangraphsBatterStatsModel
from player_universe_trx.models.mtbl import (
    MtblBatterFangraphsBundle,
    MtblBatterSavantBundle,
    MtblBatterStatsModel,
)
from player_universe_trx.models.savant.stats import (
    SavantBatterStatsModel,
    SavantHomeRunsModel,
    SavantPitchArsenalEntryModel,
    SavantSprintSpeedModel,
    SavantStatcastModel,
)


def test_batter_stats_model_empty():
    """An empty stats model has all three namespaces as None."""
    stats = MtblBatterStatsModel()
    assert stats.espn is None
    assert stats.fangraphs is None
    assert stats.savant is None


def test_batter_stats_espn_namespace_only():
    """ESPN data lives under stats.espn — current_season + periods."""
    stats = MtblBatterStatsModel(
        espn=EspnBatterStatsGroupModel(
            current_season=EspnBatterStatsModel(
                AB=500, H=150, AVG=0.300, HR=30, RBI=100, R=85, SB=15
            ),
            projections=EspnBatterStatsModel(AB=550, HR=35, RBI=110),
        )
    )

    assert stats.espn is not None
    assert stats.espn.current_season is not None
    assert stats.espn.current_season.AB == 500
    assert stats.espn.current_season.HR == 30
    assert stats.espn.projections is not None
    assert stats.espn.projections.HR == 35
    # The other source namespaces stay None
    assert stats.fangraphs is None
    assert stats.savant is None


def test_batter_stats_fangraphs_namespace_only():
    """FanGraphs projections live under stats.fangraphs.{projections,projs_updated,ros}."""
    stats = MtblBatterStatsModel(
        fangraphs=MtblBatterFangraphsBundle(
            projections=FangraphsBatterStatsModel(HR=32, RBI=95, AVG=0.300),
            projs_updated=FangraphsBatterStatsModel(HR=30, RBI=90),
            ros=FangraphsBatterStatsModel(HR=10, RBI=30),
        )
    )

    assert stats.fangraphs is not None
    assert stats.fangraphs.projections is not None
    assert stats.fangraphs.projections.hr == 32
    assert stats.fangraphs.projs_updated is not None
    assert stats.fangraphs.projs_updated.hr == 30
    assert stats.fangraphs.ros is not None
    assert stats.fangraphs.ros.hr == 10


def test_batter_stats_savant_namespace_only():
    """Savant data lives under stats.savant — splits + sub-domains."""
    stats = MtblBatterStatsModel(
        savant=MtblBatterSavantBundle(
            all=SavantBatterStatsModel(xwOBA=0.380, exit_velo=92.5),
            vs_r=SavantBatterStatsModel(xwOBA=0.390),
            vs_l=SavantBatterStatsModel(xwOBA=0.355),
            statcast=SavantStatcastModel(bbe=120, avg_ev=92.0),
            home_runs=SavantHomeRunsModel(HR=25, xHR=27.5),
            pitch_arsenal=[SavantPitchArsenalEntryModel(pitch_type="FF", pitches=300)],
            sprint_speed=SavantSprintSpeedModel(sprint_speed=28.5),
        )
    )

    assert stats.savant is not None
    assert stats.savant.all is not None and stats.savant.all.xwOBA == 0.380
    assert stats.savant.vs_r is not None and stats.savant.vs_r.xwOBA == 0.390
    assert stats.savant.vs_l is not None and stats.savant.vs_l.xwOBA == 0.355
    assert stats.savant.statcast is not None and stats.savant.statcast.avg_ev == 92.0
    assert stats.savant.home_runs is not None and stats.savant.home_runs.xHR == 27.5
    assert len(stats.savant.pitch_arsenal) == 1
    assert stats.savant.sprint_speed is not None
    assert stats.savant.sprint_speed.sprint_speed == 28.5


def test_batter_stats_three_namespaces_combined():
    """All three sources populated independently — no cross-source coupling."""
    stats = MtblBatterStatsModel(
        espn=EspnBatterStatsGroupModel(
            current_season=EspnBatterStatsModel(AB=520, HR=32, AVG=0.300)
        ),
        fangraphs=MtblBatterFangraphsBundle(
            projections=FangraphsBatterStatsModel(HR=30, AVG=0.300)
        ),
        savant=MtblBatterSavantBundle(
            all=SavantBatterStatsModel(xwOBA=0.385, exit_velo=93.2)
        ),
    )

    # Each namespace remains independent — actuals in ESPN, projections in FG,
    # sabermetrics in Savant. No merged "current_season" bag any more.
    assert stats.espn.current_season.HR == 32
    assert stats.fangraphs.projections.hr == 30
    assert stats.savant.all.xwOBA == 0.385


def test_batter_stats_model_dump_preserves_three_namespaces():
    """model_dump emits the three top-level namespace keys."""
    stats = MtblBatterStatsModel(
        espn=EspnBatterStatsGroupModel(
            current_season=EspnBatterStatsModel(HR=30)
        ),
        fangraphs=MtblBatterFangraphsBundle(
            projections=FangraphsBatterStatsModel(HR=28)
        ),
        savant=MtblBatterSavantBundle(
            all=SavantBatterStatsModel(xwOBA=0.380)
        ),
    )

    dumped = stats.model_dump(exclude_none=True)
    assert set(dumped.keys()) == {"espn", "fangraphs", "savant"}
    assert dumped["espn"]["current_season"]["HR"] == 30
    assert dumped["fangraphs"]["projections"]["HR"] == 28
    assert dumped["savant"]["all"]["xwOBA"] == 0.380


# ========== SBN compute (now lives on EspnBatterStatsModel) ==========


def test_espn_batter_sbn_computed_from_sb_and_cs():
    """SBN auto-fills from SB - CS when ESPN's payload omits it."""
    m = EspnBatterStatsModel(SB=20, CS=6)
    assert m.SBN == 14


def test_espn_batter_sbn_only_sb():
    """SBN equals SB when CS is absent."""
    m = EspnBatterStatsModel(SB=11)
    assert m.SBN == 11


def test_espn_batter_sbn_only_cs():
    """SBN equals -CS when SB is absent."""
    m = EspnBatterStatsModel(CS=5)
    assert m.SBN == -5


def test_espn_batter_sbn_explicit_value_preserved():
    """ESPN-supplied SBN is not recomputed."""
    m = EspnBatterStatsModel(SB=20, CS=8, SBN=10)
    assert m.SBN == 10  # explicit value wins over compute
