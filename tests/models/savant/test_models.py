import pytest

from player_universe_trx.models.savant import SavantBatterModel, SavantPitcherModel
from player_universe_trx.utils.model_utils import (
    create_savant_batter_models,
    create_savant_pitcher_models,
)


@pytest.fixture
def sample_batter(savant_batter_data):
    """Fixture providing a single Savant batter record."""
    return savant_batter_data[0]


@pytest.fixture
def sample_pitcher(savant_pitcher_data):
    """Fixture providing a single Savant pitcher record."""
    return savant_pitcher_data[0]


def test_batter_model_validation(sample_batter):
    """Test creating Savant batter model from raw data using transformation."""
    # Use the utility function that handles flat-to-nested transformation
    batters = create_savant_batter_models([sample_batter])

    assert len(batters) == 1
    batter = batters[0]
    assert batter.player_id == sample_batter["player_id"]
    assert batter.name == sample_batter["name"]
    assert batter.all is not None


def test_pitcher_model_validation(sample_pitcher):
    """Test creating Savant pitcher model from raw data using transformation."""
    # Use the utility function that handles flat-to-nested transformation
    pitchers = create_savant_pitcher_models([sample_pitcher])

    assert len(pitchers) == 1
    pitcher = pitchers[0]
    assert pitcher.player_id == sample_pitcher["player_id"]
    assert pitcher.name == sample_pitcher["name"]
    assert pitcher.all is not None


def test_batter_model_with_all_data(savant_batter_data):
    """Test validating all batter records in fixture."""
    batters = create_savant_batter_models(savant_batter_data)

    assert len(batters) > 0
    for batter in batters:
        assert batter.player_id is not None
        assert batter.name is not None


def test_pitcher_model_with_all_data(savant_pitcher_data):
    """Test validating all pitcher records in fixture."""
    pitchers = create_savant_pitcher_models(savant_pitcher_data)

    assert len(pitchers) > 0
    for pitcher in pitchers:
        assert pitcher.player_id is not None
        assert pitcher.name is not None


def test_batter_stats_fields(sample_batter):
    """Test that batter stats fields are accessible."""
    batters = create_savant_batter_models([sample_batter])
    batter = batters[0]

    if batter.all:
        # Test base stats fields
        assert hasattr(batter.all, "BABIP")
        assert hasattr(batter.all, "wOBA")
        assert hasattr(batter.all, "exit_velo")
        # Test batter-specific fields
        assert hasattr(batter.all, "bat_speed")
        assert hasattr(batter.all, "attack_angle")
        assert hasattr(batter.all, "barrels_per_pa_pct")


def test_batter_preserves_new_role_metadata_and_percentile_fields(sample_batter):
    """Test new Savant role metadata and percentile ranks are preserved."""
    sample = {
        **sample_batter,
        "player_type": "batter",
        "season": 2026,
        "hardhit_pct_pct_rnk": 86.4,
        "barrels_per_bbe_pct_pct_rnk": 97.6,
        "barrels_per_pa_pct_pct_rnk": 96.9,
        "barrels_total_pct_rnk": 98.6,
    }

    batter = create_savant_batter_models([sample])[0]

    assert batter.player_type == "batter"
    assert batter.season == 2026
    assert batter.all is not None
    assert batter.all.hardhit_pct_pct_rnk == 86.4
    assert batter.all.barrels_per_bbe_pct_pct_rnk == 97.6
    assert batter.all.model_dump()["barrels_total_pct_rnk"] == 98.6


def test_pitcher_stats_fields(sample_pitcher):
    """Test that pitcher stats fields are accessible."""
    pitchers = create_savant_pitcher_models([sample_pitcher])
    pitcher = pitchers[0]

    if pitcher.all:
        # Test base stats fields
        assert hasattr(pitcher.all, "BABIP")
        assert hasattr(pitcher.all, "wOBA")
        assert hasattr(pitcher.all, "exit_velo")
        # Test pitcher-specific fields
        assert hasattr(pitcher.all, "velo")
        assert hasattr(pitcher.all, "spin_rate")
        assert hasattr(pitcher.all, "release_extension")


def test_pitcher_preserves_contact_quality_fields(sample_pitcher):
    """Test pitcher exports keep the contact-quality fields shared with batters."""
    sample = {
        **sample_pitcher,
        "player_type": "pitcher",
        "hardhit_pct": 31.0,
        "hardhit_pct_pct_rnk": 44.4,
        "barrels_per_bbe_pct": 3.4,
        "barrels_per_bbe_pct_pct_rnk": 12.1,
        "barrels_per_pa_pct": 2.1,
        "barrels_per_pa_pct_pct_rnk": 9.8,
    }

    pitcher = create_savant_pitcher_models([sample])[0]

    assert pitcher.player_type == "pitcher"
    assert pitcher.all is not None
    assert pitcher.all.hardhit_pct == 31.0
    assert pitcher.all.hardhit_pct_pct_rnk == 44.4
    assert pitcher.all.barrels_per_bbe_pct == 3.4
    assert pitcher.all.barrels_per_pa_pct_pct_rnk == 9.8


def test_batter_model_with_invalid_data():
    """Test that invalid batter data raises validation error."""
    invalid_data = [{"name": "Test Player"}]  # Missing required player_id

    batters = create_savant_batter_models(invalid_data)
    assert len(batters) == 0  # Should skip invalid records


def test_pitcher_model_with_invalid_data():
    """Test that invalid pitcher data raises validation error."""
    invalid_data = [{"name": "Test Player"}]  # Missing required player_id

    pitchers = create_savant_pitcher_models(invalid_data)
    assert len(pitchers) == 0  # Should skip invalid records


def test_role_mismatch_is_invalid(sample_batter):
    """Test role-specific models reject rows carrying the opposite player_type."""
    invalid_role_data = {**sample_batter, "player_type": "pitcher"}

    batters = create_savant_batter_models([invalid_role_data])

    assert len(batters) == 0
