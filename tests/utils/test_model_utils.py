import pytest

from player_universe_trx.models.espn import EspnBatterModel, EspnPitcherModel
from player_universe_trx.utils.model_utils import (
    create_espn_batter_models,
    create_espn_pitcher_models,
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