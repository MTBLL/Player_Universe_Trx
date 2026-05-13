from typing import Any, Dict

from player_universe_trx.models.espn import EspnBatterModel, EspnPitcherModel
from player_universe_trx.models.fangraphs import (
    FangraphsBatterModel,
    FangraphsPitcherModel,
)
from player_universe_trx.models.savant import (
    SavantBatterModel,
    SavantPitcherModel,
)
from player_universe_trx.utils.model_utils import (
    create_espn_batter_models,
    create_espn_pitcher_models,
    create_fangraphs_batter_models,
    create_fangraphs_pitcher_models,
    create_savant_batter_models,
    create_savant_pitcher_models,
)


def test_create_espn_batter_models(espn_batter_data):
    """Test creating ESPN batter models from raw data."""
    batter_models = create_espn_batter_models(espn_batter_data)

    assert isinstance(batter_models, list)
    assert len(batter_models) > 0
    assert all(isinstance(model, EspnBatterModel) for model in batter_models)

    for model in batter_models:
        assert model.id is not None
        assert model.name is not None


def test_create_espn_pitcher_models(espn_pitcher_data):
    """Test creating ESPN pitcher models from raw data."""
    pitcher_models = create_espn_pitcher_models(espn_pitcher_data)

    assert isinstance(pitcher_models, list)
    assert len(pitcher_models) > 0
    assert all(isinstance(model, EspnPitcherModel) for model in pitcher_models)

    for model in pitcher_models:
        assert model.id is not None
        assert model.name is not None


def test_create_espn_batter_models_with_empty_input():
    """Test creating batter models with empty input."""
    batter_models = create_espn_batter_models([])

    assert isinstance(batter_models, list)
    assert len(batter_models) == 0


def test_create_espn_pitcher_models_with_empty_input():
    """Test creating pitcher models with empty input."""
    pitcher_models = create_espn_pitcher_models([])

    assert isinstance(pitcher_models, list)
    assert len(pitcher_models) == 0


def test_create_espn_batter_models_with_invalid_data(caplog):
    """Test that invalid batter data is skipped gracefully and exceptions are caught."""
    invalid_data = [
        {"name": "Missing ID"},  # Missing required id field
        {"id": "not_an_int", "name": "Bad ID"},  # Wrong type for id
        {},  # Empty object
        {"invalid": "data"},  # No required fields
    ]

    with caplog.at_level("DEBUG"):
        batter_models = create_espn_batter_models(invalid_data)

    # All invalid records should be skipped
    assert isinstance(batter_models, list)
    assert len(batter_models) == 0

    # Verify that exceptions were caught and logged (4 DEBUG + 1 INFO)
    debug_records = [r for r in caplog.records if r.levelname == "DEBUG"]
    assert len(debug_records) == 4
    for record in debug_records:
        assert "Skipped batter" in record.message


def test_create_espn_pitcher_models_with_invalid_data(caplog):
    """Test that invalid pitcher data is skipped gracefully and exceptions are caught."""
    invalid_data = [
        {"name": "Missing ID"},  # Missing required id field
        {"id": "not_an_int", "name": "Bad ID"},  # Wrong type for id
        {},  # Empty object
        {"invalid": "data"},  # No required fields
    ]

    with caplog.at_level("DEBUG"):
        pitcher_models = create_espn_pitcher_models(invalid_data)

    # All invalid records should be skipped
    assert isinstance(pitcher_models, list)
    assert len(pitcher_models) == 0

    # Verify that exceptions were caught and logged (4 DEBUG + 1 INFO)
    debug_records = [r for r in caplog.records if r.levelname == "DEBUG"]
    assert len(debug_records) == 4
    for record in debug_records:
        assert "Skipped pitcher" in record.message


def test_create_fangraphs_batter_models(fangraphs_batter_data):
    """Test creating FanGraphs batter models from raw data."""
    batter_models = create_fangraphs_batter_models(fangraphs_batter_data)

    assert isinstance(batter_models, list)
    assert len(batter_models) > 0
    assert all(isinstance(model, FangraphsBatterModel) for model in batter_models)

    for model in batter_models:
        assert model.name is not None
        assert model.playerid is not None


def test_create_fangraphs_pitcher_models(fangraphs_pitcher_data):
    """Test creating FanGraphs pitcher models from raw data."""
    pitcher_models = create_fangraphs_pitcher_models(fangraphs_pitcher_data)

    assert isinstance(pitcher_models, list)
    assert len(pitcher_models) > 0
    assert all(isinstance(model, FangraphsPitcherModel) for model in pitcher_models)

    for model in pitcher_models:
        assert model.name is not None
        assert model.playerid is not None


def test_create_fangraphs_batter_models_with_empty_input():
    """Test creating FanGraphs batter models with empty input."""
    batter_models = create_fangraphs_batter_models([])

    assert isinstance(batter_models, list)
    assert len(batter_models) == 0


def test_create_fangraphs_pitcher_models_with_empty_input():
    """Test creating FanGraphs pitcher models with empty input."""
    pitcher_models = create_fangraphs_pitcher_models([])

    assert isinstance(pitcher_models, list)
    assert len(pitcher_models) == 0


def test_create_fangraphs_batter_models_with_invalid_data(caplog):
    """Test that invalid FanGraphs batter data is skipped gracefully and exceptions are caught."""
    invalid_data = [
        {"name": "Missing ID"},  # Missing required playerid field
        {"playerid": 123, "name": "Bad ID"},  # Wrong type for playerid
        {},  # Empty object
        {"invalid": "data"},  # No required fields
    ]

    with caplog.at_level("DEBUG"):
        batter_models = create_fangraphs_batter_models(invalid_data)

    # All invalid records should be skipped
    assert isinstance(batter_models, list)
    assert len(batter_models) == 0

    # Verify that exceptions were caught and logged
    debug_records = [r for r in caplog.records if r.levelname == "DEBUG"]
    assert len(debug_records) == 4
    for record in debug_records:
        assert "Skipped batter" in record.message


def test_create_fangraphs_pitcher_models_with_invalid_data(caplog):
    """Test that invalid FanGraphs pitcher data is skipped gracefully and exceptions are caught."""
    invalid_data = [
        {"name": "Missing ID"},  # Missing required playerid field
        {"playerid": 123, "name": "Bad ID"},  # Wrong type for playerid
        {},  # Empty object
        {"invalid": "data"},  # No required fields
    ]

    with caplog.at_level("DEBUG"):
        pitcher_models = create_fangraphs_pitcher_models(invalid_data)

    # All invalid records should be skipped
    assert isinstance(pitcher_models, list)
    assert len(pitcher_models) == 0

    # Verify that exceptions were caught and logged
    debug_records = [r for r in caplog.records if r.levelname == "DEBUG"]
    assert len(debug_records) == 4
    for record in debug_records:
        assert "Skipped pitcher" in record.message


def test_create_savant_batter_models(savant_batter_data):
    """Test creating Savant batter models from raw data with flat-to-nested transformation."""
    batter_models = create_savant_batter_models(savant_batter_data)

    assert isinstance(batter_models, list)
    assert len(batter_models) > 0
    assert all(isinstance(model, SavantBatterModel) for model in batter_models)

    for model in batter_models:
        assert model.player_id is not None
        assert model.name is not None
        # Every player has the `all` split after the upstream min_pas fix
        assert model.all is not None


def test_create_savant_pitcher_models(savant_pitcher_data):
    """Test creating Savant pitcher models from raw data with flat-to-nested transformation."""
    pitcher_models = create_savant_pitcher_models(savant_pitcher_data)

    assert isinstance(pitcher_models, list)
    assert len(pitcher_models) > 0
    assert all(isinstance(model, SavantPitcherModel) for model in pitcher_models)

    for model in pitcher_models:
        assert model.player_id is not None
        assert model.name is not None
        # Every player has the `all` split after the upstream min_pas fix
        assert model.all is not None


def test_create_savant_batter_models_with_empty_input():
    """Test creating Savant batter models with empty input."""
    batter_models = create_savant_batter_models([])

    assert isinstance(batter_models, list)
    assert len(batter_models) == 0


def test_create_savant_pitcher_models_with_empty_input():
    """Test creating Savant pitcher models with empty input."""
    pitcher_models = create_savant_pitcher_models([])

    assert isinstance(pitcher_models, list)
    assert len(pitcher_models) == 0


def test_create_savant_batter_models_with_invalid_data(caplog):
    """Test that invalid Savant rows are skipped gracefully.

    The consolidator first filters rows missing a player_id or carrying an
    unknown opp_hand value, then catches per-player validation errors. Any of
    those paths emits a DEBUG log line so callers can see why a row was
    dropped.
    """
    invalid_data = [
        {"name": "Missing ID"},  # No player_id — filtered at row level
        {
            "player_id": 1,
            "name": "Missing opp_hand",
        },  # Has player_id but no opp_hand
        {},  # Empty — no player_id
        {"invalid": "data"},  # No player_id
    ]

    with caplog.at_level("DEBUG"):
        batter_models = create_savant_batter_models(invalid_data)

    assert isinstance(batter_models, list)
    assert len(batter_models) == 0

    debug_records = [r for r in caplog.records if r.levelname == "DEBUG"]
    assert len(debug_records) == 4
    for record in debug_records:
        # Either filtered at row level (no player_id / unknown opp_hand) or
        # caught at model validation — both prefix with "Skipped".
        assert "Skipped" in record.message


def test_create_savant_pitcher_models_with_invalid_data(caplog):
    """Pitcher counterpart of the batter invalid-data test."""
    invalid_data = [
        {"name": "Missing ID"},
        {"player_id": 1, "name": "Missing opp_hand"},
        {},
        {"invalid": "data"},
    ]

    with caplog.at_level("DEBUG"):
        pitcher_models = create_savant_pitcher_models(invalid_data)

    assert isinstance(pitcher_models, list)
    assert len(pitcher_models) == 0

    debug_records = [r for r in caplog.records if r.levelname == "DEBUG"]
    assert len(debug_records) == 4
    for record in debug_records:
        assert "Skipped" in record.message


# ========== Three-split consolidation ==========


def _savant_batter_row(player_id: int, opp_hand: str, **extras: Any) -> Dict[str, Any]:
    """Build a minimum-viable Savant batter wire row for consolidator tests."""
    return {
        "player_id": player_id,
        "name": "Test, Player",
        "first_name": "Test",
        "last_name": "Player",
        "name_ascii": "Test Player",
        "slug": "test-player",
        "player_type": "batter",
        "season": 2026,
        "opp_hand": opp_hand,
        "pitches": 100,
        "total_pitches": 100,
        "pitch_percent": 100.0,
        **extras,
    }


def test_consolidator_groups_three_rows_into_one_batter():
    """Three wire rows (one per opp_hand) collapse to one model with all/vs_r/vs_l."""
    rows = [
        _savant_batter_row(100, "all", xwOBA=0.350, exit_velo=90.0),
        _savant_batter_row(100, "R", xwOBA=0.360, exit_velo=91.0),
        _savant_batter_row(100, "L", xwOBA=0.330, exit_velo=88.0),
    ]
    models = create_savant_batter_models(rows)

    assert len(models) == 1
    m = models[0]
    assert m.player_id == 100
    assert m.all is not None and m.all.xwOBA == 0.350
    assert m.vs_r is not None and m.vs_r.xwOBA == 0.360
    assert m.vs_l is not None and m.vs_l.xwOBA == 0.330


def test_consolidator_partial_coverage_all_plus_r_only():
    """Player with only `all` + `R` split (never faced a lefty): vs_l is None."""
    rows = [
        _savant_batter_row(200, "all", xwOBA=0.300),
        _savant_batter_row(200, "R", xwOBA=0.305),
    ]
    models = create_savant_batter_models(rows)

    assert len(models) == 1
    m = models[0]
    assert m.all is not None
    assert m.vs_r is not None
    assert m.vs_l is None


def test_consolidator_partial_coverage_all_plus_l_only():
    """Mirror of the R-only case: vs_r is None."""
    rows = [
        _savant_batter_row(300, "all", xwOBA=0.280),
        _savant_batter_row(300, "L", xwOBA=0.295),
    ]
    models = create_savant_batter_models(rows)

    assert len(models) == 1
    m = models[0]
    assert m.all is not None
    assert m.vs_r is None
    assert m.vs_l is not None


def test_consolidator_per_split_pitch_counts_preserved():
    """Pitch counts vary per split and must land on the matching slot."""
    rows = [
        _savant_batter_row(400, "all", pitches=200, total_pitches=200),
        _savant_batter_row(400, "R", pitches=150, total_pitches=200),
        _savant_batter_row(400, "L", pitches=50, total_pitches=200),
    ]
    models = create_savant_batter_models(rows)

    m = models[0]
    assert m.all.pitches == 200
    assert m.vs_r.pitches == 150
    assert m.vs_l.pitches == 50


def test_consolidator_treats_missing_opp_hand_as_all_split():
    """Legacy one-row-per-player extracts (pre-opp_hand) load as the `all` split.

    Without this backwards-compat default, every row in a legacy file would
    be silently dropped (opp_hand=None → unknown slot), wiping all Savant
    enrichment downstream for backfills or reruns against older fixtures.
    """
    # Legacy row — note the absence of opp_hand
    legacy_row = {
        "player_id": 999,
        "name": "Legacy, Player",
        "first_name": "Legacy",
        "last_name": "Player",
        "name_ascii": "Legacy Player",
        "slug": "legacy-player",
        "player_type": "batter",
        "season": 2024,
        "pitches": 500,
        "total_pitches": 500,
        "pitch_percent": 100.0,
        "xwOBA": 0.345,
        "exit_velo": 89.0,
    }
    models = create_savant_batter_models([legacy_row])

    assert len(models) == 1
    m = models[0]
    assert m.player_id == 999
    # Missing opp_hand maps to the `all` slot
    assert m.all is not None
    assert m.all.xwOBA == 0.345
    assert m.all.pitches == 500
    assert m.vs_r is None
    assert m.vs_l is None


def test_consolidator_unknown_opp_hand_is_skipped(caplog):
    """opp_hand values outside the {all,R,L} contract are filtered with a debug log."""
    rows = [
        _savant_batter_row(500, "all", xwOBA=0.310),
        _savant_batter_row(500, "S", xwOBA=0.999),  # bogus
    ]
    with caplog.at_level("DEBUG"):
        models = create_savant_batter_models(rows)

    m = models[0]
    assert m.all is not None and m.all.xwOBA == 0.310
    assert m.vs_r is None and m.vs_l is None
    assert any("unknown opp_hand" in r.message for r in caplog.records)


def test_consolidator_scrubs_nan_floats():
    """NaN values from upstream pandas serialization are dropped, not propagated.

    Upstream emits float('nan') for stats that couldn't be computed for the
    sample (typical for thin-sample BBdist / barrels_total fields). Pydantic
    rejects non-finite floats by default; the consolidator converts them to
    missing data instead so the row still validates.
    """
    nan = float("nan")
    rows = [
        _savant_batter_row(
            600, "all", xwOBA=0.295, BBdist=nan, barrels_total=nan
        ),
    ]
    models = create_savant_batter_models(rows)

    assert len(models) == 1
    m = models[0]
    assert m.all.xwOBA == 0.295
    assert m.all.BBdist is None
    assert m.all.barrels_total is None


def test_consolidator_every_player_has_all_slot(savant_batter_data, savant_pitcher_data):
    """Post-min_pas-filter contract: every player must have an `all` slot.

    The conftest fixtures slice to first 10 wire rows (so this is a thin
    smoke test, not a full-fixture audit), but the contract is firm enough
    that even on a 10-row slice no row should be missing the all-split
    after consolidation.
    """
    batters = create_savant_batter_models(savant_batter_data)
    pitchers = create_savant_pitcher_models(savant_pitcher_data)
    for m in batters:
        assert m.all is not None, f"batter {m.player_id} ({m.name}) missing 'all' split"
    for m in pitchers:
        assert m.all is not None, f"pitcher {m.player_id} ({m.name}) missing 'all' split"


# ========== Sub-domain merge into Savant models ==========


def _savant_subdomain_row(player_id: int, **extras: Any) -> Dict[str, Any]:
    """Build a minimal sub-domain row keyed by player_id."""
    return {"player_id": player_id, "name": "Test", **extras}


def test_subdomain_merge_attaches_statcast_to_matching_player():
    """A statcast row keyed by player_id lands on the matching SavantBatterModel."""
    base = [_savant_batter_row(100, "all", xwOBA=0.300)]
    statcast = [_savant_subdomain_row(100, bbe=42, avg_ev=89.0, ev50=95.0)]
    models = create_savant_batter_models(base, statcast_data=statcast)
    assert len(models) == 1
    m = models[0]
    assert m.statcast is not None
    assert m.statcast.bbe == 42
    assert m.statcast.avg_ev == 89.0


def test_subdomain_merge_skips_unmatched_player_id():
    """A statcast row for a player_id not in the base file is ignored."""
    base = [_savant_batter_row(100, "all", xwOBA=0.300)]
    statcast = [
        _savant_subdomain_row(100, bbe=42),
        _savant_subdomain_row(999, bbe=99),  # No matching base row
    ]
    models = create_savant_batter_models(base, statcast_data=statcast)
    assert len(models) == 1
    assert models[0].statcast.bbe == 42  # The 999-keyed row is silently dropped


def test_subdomain_merge_pitch_arsenal_groups_multiple_rows():
    """Multiple pitch_arsenal rows for the same player_id collect into a list."""
    base = [_savant_batter_row(100, "all", xwOBA=0.300)]
    arsenal = [
        _savant_subdomain_row(100, pitch_type="FF", pitches=200, xwOBA=0.310),
        _savant_subdomain_row(100, pitch_type="SL", pitches=100, xwOBA=0.260),
        _savant_subdomain_row(100, pitch_type="CH", pitches=80, xwOBA=0.270),
    ]
    models = create_savant_batter_models(base, pitch_arsenal_data=arsenal)
    m = models[0]
    assert len(m.pitch_arsenal) == 3
    assert {e.pitch_type for e in m.pitch_arsenal} == {"FF", "SL", "CH"}


def test_subdomain_merge_missing_sub_domain_yields_default_values():
    """When a sub-domain kwarg is omitted, fields stay None / empty list."""
    base = [_savant_batter_row(100, "all", xwOBA=0.300)]
    models = create_savant_batter_models(base)  # No sub-domain kwargs
    m = models[0]
    assert m.statcast is None
    assert m.home_runs is None
    assert m.pitch_arsenal == []
    assert m.sprint_speed is None


def test_subdomain_merge_handles_nan_in_sub_domain_rows():
    """NaN floats in sub-domain rows are scrubbed like the base rows."""
    base = [_savant_batter_row(100, "all", xwOBA=0.300)]
    sprint = [
        _savant_subdomain_row(
            100, position=float("nan"), sprint_speed=29.0, age=30
        ),
    ]
    models = create_savant_batter_models(base, sprint_speed_data=sprint)
    m = models[0]
    assert m.sprint_speed is not None
    assert m.sprint_speed.sprint_speed == 29.0
    assert m.sprint_speed.position is None  # NaN scrubbed to absent → None


def test_subdomain_merge_skips_subdomain_row_with_no_player_id(caplog):
    """A sub-domain row missing player_id is filtered with a debug log, not propagated."""
    base = [_savant_batter_row(100, "all", xwOBA=0.300)]
    statcast = [{"name": "Orphan", "bbe": 50}]  # no player_id

    with caplog.at_level("DEBUG"):
        models = create_savant_batter_models(base, statcast_data=statcast)

    assert models[0].statcast is None  # orphan didn't attach
    assert any("no player_id" in r.message for r in caplog.records)


def test_consolidator_full_fixture_end_to_end():
    """End-to-end: load all 10 wire files through the loader+consolidator pipeline."""
    from player_universe_trx.loaders import DataLoader

    loader = DataLoader(resources_path="tests/fixtures", year=2026)
    batters = create_savant_batter_models(
        loader.load_savant_batters(),
        statcast_data=loader.load_savant_statcast_batters(),
        home_runs_data=loader.load_savant_home_runs_batters(),
        pitch_arsenal_data=loader.load_savant_pitch_arsenal_batters(),
        sprint_speed_data=loader.load_savant_sprint_speed(),
    )
    pitchers = create_savant_pitcher_models(
        loader.load_savant_pitchers(),
        statcast_data=loader.load_savant_statcast_pitchers(),
        home_runs_data=loader.load_savant_home_runs_pitchers(),
        pitch_arsenal_data=loader.load_savant_pitch_arsenal_pitchers(),
        expected_statistics_data=loader.load_savant_expected_statistics_pitchers(),
    )

    # Coverage sanity — exact counts taken from raw fixture analysis
    assert len(batters) == 486
    assert len(pitchers) == 597
    assert sum(1 for b in batters if b.statcast) == 269
    assert sum(1 for b in batters if b.home_runs) == 399
    assert sum(1 for b in batters if b.pitch_arsenal) == 349
    assert sum(1 for b in batters if b.sprint_speed) == 401
    assert sum(1 for p in pitchers if p.expected_statistics) == 367
