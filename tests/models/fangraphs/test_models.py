import pytest

from player_universe_trx.models.fangraphs import (
    FangraphsBatterModel,
    FangraphsPitcherModel,
)


@pytest.fixture
def sample_batter(fangraphs_batter_data):
    """Fixture providing a single FanGraphs batter record."""
    return fangraphs_batter_data[0]


@pytest.fixture
def sample_pitcher(fangraphs_pitcher_data):
    """Fixture providing a single FanGraphs pitcher record."""
    return fangraphs_pitcher_data[0]


def test_batter_model_validation(sample_batter):
    """Test creating FanGraphs batter model from raw data."""
    batter = FangraphsBatterModel.model_validate(sample_batter)

    assert batter.name == sample_batter["name"]
    assert batter.playerid == sample_batter["playerid"]
    assert batter.projection is not None


def test_pitcher_model_validation(sample_pitcher):
    """Test creating FanGraphs pitcher model from raw data."""
    pitcher = FangraphsPitcherModel.model_validate(sample_pitcher)

    assert pitcher.name == sample_pitcher["name"]
    assert pitcher.playerid == sample_pitcher["playerid"]
    assert pitcher.projection is not None


def test_batter_model_with_all_data(fangraphs_batter_data):
    """Test validating all batter records in fixture."""
    for batter_data in fangraphs_batter_data:
        batter = FangraphsBatterModel.model_validate(batter_data)
        assert batter.name is not None
        assert batter.playerid is not None


def test_pitcher_model_with_all_data(fangraphs_pitcher_data):
    """Test validating all pitcher records in fixture."""
    for pitcher_data in fangraphs_pitcher_data:
        pitcher = FangraphsPitcherModel.model_validate(pitcher_data)
        assert pitcher.name is not None
        assert pitcher.playerid is not None


def test_batter_projection_fields(sample_batter):
    """Test that batter projection fields are accessible."""
    batter = FangraphsBatterModel.model_validate(sample_batter)

    if batter.projection:
        # Test common fields
        assert hasattr(batter.projection, "games")
        assert hasattr(batter.projection, "war")
        assert hasattr(batter.projection, "fpts")
        # Test batter-specific fields
        assert hasattr(batter.projection, "pa")
        assert hasattr(batter.projection, "hr")
        assert hasattr(batter.projection, "avg")


def test_pitcher_projection_fields(sample_pitcher):
    """Test that pitcher projection fields are accessible."""
    pitcher = FangraphsPitcherModel.model_validate(sample_pitcher)

    if pitcher.projection:
        # Test common fields
        assert hasattr(pitcher.projection, "games")
        assert hasattr(pitcher.projection, "war")
        assert hasattr(pitcher.projection, "fpts")
        # Test pitcher-specific fields
        assert hasattr(pitcher.projection, "innings_pitched")
        assert hasattr(pitcher.projection, "era")
        assert hasattr(pitcher.projection, "whip")


def test_batter_model_with_invalid_data():
    """Test that invalid batter data raises validation error."""
    invalid_data = {"name": "Test Player"}  # Missing required playerid

    with pytest.raises(Exception):
        FangraphsBatterModel.model_validate(invalid_data)


def test_pitcher_model_with_invalid_data():
    """Test that invalid pitcher data raises validation error."""
    invalid_data = {"name": "Test Player"}  # Missing required playerid

    with pytest.raises(Exception):
        FangraphsPitcherModel.model_validate(invalid_data)
