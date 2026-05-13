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
