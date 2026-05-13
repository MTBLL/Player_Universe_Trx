"""Tests for MtblPitcherStatsModel — three source-by-source bundles (espn / fangraphs / savant)."""

from player_universe_trx.models.espn.pitcher import EspnPitcherStatsGroupModel
from player_universe_trx.models.espn.stats import EspnPitcherStatsModel
from player_universe_trx.models.fangraphs.stats import FangraphsPitcherStatsModel
from player_universe_trx.models.mtbl import (
    MtblPitcherFangraphsBundle,
    MtblPitcherSavantBundle,
    MtblPitcherStatsModel,
)
from player_universe_trx.models.savant.stats import (
    SavantHomeRunsModel,
    SavantPitcherExpectedStatsModel,
    SavantPitcherStatsModel,
    SavantPitchArsenalEntryModel,
    SavantStatcastModel,
)


def test_pitcher_stats_model_empty():
    """An empty stats model has all three namespaces as None."""
    stats = MtblPitcherStatsModel()
    assert stats.espn is None
    assert stats.fangraphs is None
    assert stats.savant is None


def test_pitcher_stats_espn_namespace_only():
    """ESPN data lives under stats.espn — current_season + periods."""
    stats = MtblPitcherStatsModel(
        espn=EspnPitcherStatsGroupModel(
            current_season=EspnPitcherStatsModel(W=15, L=6, ERA=3.25, K=180),
            projections=EspnPitcherStatsModel(W=18, ERA=3.10, K=210),
        )
    )

    assert stats.espn is not None
    assert stats.espn.current_season is not None
    assert stats.espn.current_season.W == 15
    assert stats.espn.current_season.ERA == 3.25
    assert stats.espn.projections is not None
    assert stats.espn.projections.W == 18
    assert stats.fangraphs is None
    assert stats.savant is None


def test_pitcher_stats_fangraphs_namespace_only():
    """FanGraphs projections live under stats.fangraphs.{projections,projs_updated,ros}."""
    stats = MtblPitcherStatsModel(
        fangraphs=MtblPitcherFangraphsBundle(
            projections=FangraphsPitcherStatsModel(W=18, SO=230, ERA=2.95),
            projs_updated=FangraphsPitcherStatsModel(W=16, SO=200, ERA=3.05),
            ros=FangraphsPitcherStatsModel(W=6, SO=80, ERA=3.20),
        )
    )

    assert stats.fangraphs is not None
    assert stats.fangraphs.projections is not None
    assert stats.fangraphs.projections.wins == 18
    assert stats.fangraphs.projs_updated is not None
    assert stats.fangraphs.projs_updated.wins == 16
    assert stats.fangraphs.ros is not None
    assert stats.fangraphs.ros.wins == 6


def test_pitcher_stats_savant_namespace_only():
    """Savant data lives under stats.savant — splits + sub-domains (expected_statistics for pitchers)."""
    stats = MtblPitcherStatsModel(
        savant=MtblPitcherSavantBundle(
            all=SavantPitcherStatsModel(xwOBA=0.270, velo=96.8),
            vs_r=SavantPitcherStatsModel(xwOBA=0.260),
            vs_l=SavantPitcherStatsModel(xwOBA=0.290),
            statcast=SavantStatcastModel(bbe=180, avg_ev=86.5),
            home_runs=SavantHomeRunsModel(HR=12, xHR=14.0),
            pitch_arsenal=[SavantPitchArsenalEntryModel(pitch_type="FF", pitches=500)],
            expected_statistics=SavantPitcherExpectedStatsModel(xERA=3.45, xwOBA=0.270),
        )
    )

    assert stats.savant is not None
    assert stats.savant.all is not None and stats.savant.all.xwOBA == 0.270
    assert stats.savant.vs_r is not None and stats.savant.vs_r.xwOBA == 0.260
    assert stats.savant.vs_l is not None and stats.savant.vs_l.xwOBA == 0.290
    assert stats.savant.statcast is not None and stats.savant.statcast.bbe == 180
    assert stats.savant.home_runs is not None and stats.savant.home_runs.xHR == 14.0
    assert len(stats.savant.pitch_arsenal) == 1
    # Pitcher bundle has expected_statistics (instead of batter's sprint_speed)
    assert stats.savant.expected_statistics is not None
    assert stats.savant.expected_statistics.xERA == 3.45


def test_pitcher_stats_three_namespaces_combined():
    """All three sources populated independently."""
    stats = MtblPitcherStatsModel(
        espn=EspnPitcherStatsGroupModel(
            current_season=EspnPitcherStatsModel(W=10, ERA=3.50, K=150)
        ),
        fangraphs=MtblPitcherFangraphsBundle(
            projections=FangraphsPitcherStatsModel(W=18, ERA=3.00, SO=220)
        ),
        savant=MtblPitcherSavantBundle(
            all=SavantPitcherStatsModel(xwOBA=0.280, velo=96.5)
        ),
    )

    assert stats.espn.current_season.W == 10
    assert stats.fangraphs.projections.wins == 18
    assert stats.savant.all.xwOBA == 0.280


def test_pitcher_stats_model_dump_preserves_three_namespaces():
    """model_dump emits the three top-level namespace keys."""
    stats = MtblPitcherStatsModel(
        espn=EspnPitcherStatsGroupModel(
            current_season=EspnPitcherStatsModel(W=15)
        ),
        fangraphs=MtblPitcherFangraphsBundle(
            projections=FangraphsPitcherStatsModel(W=18)
        ),
        savant=MtblPitcherSavantBundle(
            all=SavantPitcherStatsModel(xwOBA=0.270)
        ),
    )

    dumped = stats.model_dump(exclude_none=True)
    assert set(dumped.keys()) == {"espn", "fangraphs", "savant"}
    assert dumped["espn"]["current_season"]["W"] == 15
    assert dumped["fangraphs"]["projections"]["W"] == 18
    assert dumped["savant"]["all"]["xwOBA"] == 0.270
