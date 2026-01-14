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
    assert batter.projections is not None
    assert batter.projections.ab is not None


def test_pitcher_model_validation(sample_pitcher):
    """Test creating FanGraphs pitcher model from raw data."""
    pitcher = FangraphsPitcherModel.model_validate(sample_pitcher)

    assert pitcher.name == sample_pitcher["name"]
    assert pitcher.playerid == sample_pitcher["playerid"]
    assert pitcher.projections is not None


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
    """Test that batter projection fields are properly mapped and have values."""
    batter = FangraphsBatterModel.model_validate(sample_batter)

    assert batter.projections is not None, "Projections should not be None"

    # Test common fields from base projection
    assert batter.projections.games is not None
    assert batter.projections.fpts is not None
    assert batter.projections.spts is not None

    # Test quantile projections (wOBA for batters)
    assert batter.projections.q10 is not None
    assert batter.projections.q50 is not None
    assert batter.projections.q90 is not None

    # Test counting stats
    assert batter.projections.pa is not None
    assert batter.projections.ab is not None
    assert batter.projections.h is not None
    assert batter.projections.hr is not None
    assert batter.projections.r is not None
    assert batter.projections.rbi is not None
    assert batter.projections.bb is not None
    assert batter.projections.so is not None
    assert batter.projections.sb is not None

    # Test rate stats
    assert batter.projections.avg is not None
    assert batter.projections.obp is not None
    assert batter.projections.slg is not None


def test_pitcher_projection_fields(sample_pitcher):
    """Test that pitcher projection fields are properly mapped and have values."""
    pitcher = FangraphsPitcherModel.model_validate(sample_pitcher)

    assert pitcher.projections is not None, "Projections should not be None"

    # Test common fields from base projection
    assert pitcher.projections.games is not None
    assert pitcher.projections.fpts is not None
    assert pitcher.projections.spts is not None

    # Test quantile projections (ERA for pitchers)
    assert pitcher.projections.q10 is not None
    assert pitcher.projections.q50 is not None
    assert pitcher.projections.q90 is not None

    # Test counting stats
    assert pitcher.projections.wins is not None
    assert pitcher.projections.losses is not None
    assert pitcher.projections.games_started is not None
    assert pitcher.projections.innings_pitched is not None
    assert pitcher.projections.strikeouts is not None
    assert pitcher.projections.walks is not None
    assert pitcher.projections.hits is not None

    # Test rate stats
    assert pitcher.projections.era is not None
    assert pitcher.projections.whip is not None

    # Test fantasy metrics
    assert pitcher.projections.fpts_ip is not None
    assert pitcher.projections.spts_ip is not None


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


def test_pitcher_svhd_field(mason_miller_fangraphs):
    """Test that SVHD field is correctly loaded from data."""
    pitcher = FangraphsPitcherModel.model_validate(mason_miller_fangraphs)

    # Test that SVHD is loaded from the data
    assert pitcher.projections is not None
    assert pitcher.projections.svhd is not None
    assert pitcher.projections.saves is not None
    assert pitcher.projections.holds is not None
    # SVHD should be provided by upstream data (FanGraphs now includes it)
    assert pitcher.projections.svhd > 0


def test_batter_sbn_computed_field(sample_batter):
    """Test that SBN is correctly computed from stolen bases and caught stealing."""
    batter = FangraphsBatterModel.model_validate(sample_batter)

    # Test that SBN is computed
    assert batter.projections is not None
    assert batter.projections.sbn is not None
    assert batter.projections.sb is not None
    assert batter.projections.cs is not None
    assert batter.projections.sbn == (
        batter.projections.sb - batter.projections.cs
    )


def test_batter_model_serialize_by_alias(sample_batter):
    """Test that batter model exports using aliases and includes SBN."""
    batter = FangraphsBatterModel.model_validate(sample_batter)

    # Export to dict
    exported = batter.model_dump()

    # Check that aliases are used in export
    assert "projection" in exported
    assert exported["projection"] is not None

    # Check specific fields use uppercase aliases
    assert "PA" in exported["projection"]
    assert "HR" in exported["projection"]
    assert "AVG" in exported["projection"]
    assert "G" in exported["projection"]
    assert "FPTS" in exported["projection"]

    # Check that SBN computed field is exported with alias
    assert "SBN" in exported["projection"]
    assert exported["projection"]["SBN"] is not None

    # Check that python names are NOT in export
    assert "pa" not in exported["projection"]
    assert "hr" not in exported["projection"]
    assert "avg" not in exported["projection"]
    assert "games" not in exported["projection"]
    assert "fpts" not in exported["projection"]
    assert "sbn" not in exported["projection"]


def test_pitcher_model_serialize_by_alias_with_svhd(mason_miller_fangraphs):
    """Test that pitcher model exports using aliases and includes SVHD."""
    pitcher = FangraphsPitcherModel.model_validate(mason_miller_fangraphs)

    # Export to dict
    exported = pitcher.model_dump()

    # Check that aliases are used in export
    assert "projection" in exported
    assert exported["projection"] is not None

    # Check specific fields use uppercase aliases
    assert "IP" in exported["projection"]
    assert "ERA" in exported["projection"]
    assert "WHIP" in exported["projection"]
    assert "G" in exported["projection"]
    assert "FPTS" in exported["projection"]

    # Check that SVHD field is exported with alias
    assert "SVHD" in exported["projection"]
    assert exported["projection"]["SVHD"] is not None
    assert exported["projection"]["SVHD"] > 0

    # Check that python names are NOT in export
    assert "innings_pitched" not in exported["projection"]
    assert "era" not in exported["projection"]
    assert "whip" not in exported["projection"]
    assert "games" not in exported["projection"]
    assert "fpts" not in exported["projection"]
    assert "svhd" not in exported["projection"]


def test_batter_sbn_with_only_sb():
    """Test that SBN equals SB when CS is missing."""
    data = {
        "name": "Only SB Batter",
        "playerid": "sb-only",
        "projection": {"SB": 7},
    }
    batter = FangraphsBatterModel.model_validate(data)

    assert batter.projections is not None
    assert batter.projections.sbn == 7


def test_batter_sbn_with_only_cs():
    """Test that SBN is negative CS when SB is missing."""
    data = {
        "name": "Only CS Batter",
        "playerid": "cs-only",
        "projection": {"CS": 3},
    }
    batter = FangraphsBatterModel.model_validate(data)

    assert batter.projections is not None
    assert batter.projections.sbn == -3


def test_pitcher_svhd_from_data():
    """Test that SVHD is loaded directly from data when provided."""
    data = {
        "name": "Test Pitcher",
        "playerid": "test-pitcher",
        "projection": {"SV": 4, "HLD": 6, "SVHD": 10},
    }
    pitcher = FangraphsPitcherModel.model_validate(data)

    assert pitcher.projections is not None
    assert pitcher.projections.svhd == 10
    assert pitcher.projections.saves == 4
    assert pitcher.projections.holds == 6
