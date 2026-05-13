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

    # Check that the new three-slot shape is preserved in export
    assert "projections" in exported
    assert exported["projections"] is not None

    # Check specific fields use uppercase aliases
    assert "PA" in exported["projections"]
    assert "HR" in exported["projections"]
    assert "AVG" in exported["projections"]
    assert "G" in exported["projections"]
    assert "FPTS" in exported["projections"]

    # Check that SBN computed field is exported with alias
    assert "SBN" in exported["projections"]
    assert exported["projections"]["SBN"] is not None

    # Check that python names are NOT in export
    assert "pa" not in exported["projections"]
    assert "hr" not in exported["projections"]
    assert "avg" not in exported["projections"]
    assert "games" not in exported["projections"]
    assert "fpts" not in exported["projections"]
    assert "sbn" not in exported["projections"]


def test_pitcher_model_serialize_by_alias_with_svhd(mason_miller_fangraphs):
    """Test that pitcher model exports using aliases and includes SVHD."""
    pitcher = FangraphsPitcherModel.model_validate(mason_miller_fangraphs)

    # Export to dict
    exported = pitcher.model_dump()

    # Check that the new three-slot shape is preserved in export
    assert "projections" in exported
    assert exported["projections"] is not None

    # Check specific fields use uppercase aliases
    assert "IP" in exported["projections"]
    assert "ERA" in exported["projections"]
    assert "WHIP" in exported["projections"]
    assert "G" in exported["projections"]
    assert "FPTS" in exported["projections"]

    # Check that SVHD field is exported with alias
    assert "SVHD" in exported["projections"]
    assert exported["projections"]["SVHD"] is not None
    assert exported["projections"]["SVHD"] > 0

    # Check that python names are NOT in export
    assert "innings_pitched" not in exported["projections"]
    assert "era" not in exported["projections"]
    assert "whip" not in exported["projections"]
    assert "games" not in exported["projections"]
    assert "fpts" not in exported["projections"]
    assert "svhd" not in exported["projections"]


def test_batter_sbn_with_only_sb():
    """Test that SBN equals SB when CS is missing."""
    data = {
        "name": "Only SB Batter",
        "playerid": "sb-only",
        "projections": {"SB": 7},
    }
    batter = FangraphsBatterModel.model_validate(data)

    assert batter.projections is not None
    assert batter.projections.sbn == 7


def test_batter_sbn_with_only_cs():
    """Test that SBN is negative CS when SB is missing."""
    data = {
        "name": "Only CS Batter",
        "playerid": "cs-only",
        "projections": {"CS": 3},
    }
    batter = FangraphsBatterModel.model_validate(data)

    assert batter.projections is not None
    assert batter.projections.sbn == -3


def test_pitcher_svhd_from_data():
    """Test that SVHD is loaded directly from data when provided."""
    data = {
        "name": "Test Pitcher",
        "playerid": "test-pitcher",
        "projections": {"SV": 4, "HLD": 6, "SVHD": 10},
    }
    pitcher = FangraphsPitcherModel.model_validate(data)

    assert pitcher.projections is not None
    assert pitcher.projections.svhd == 10
    assert pitcher.projections.saves == 4
    assert pitcher.projections.holds == 6


# ========== Three-slot projection shape (projections / projs_updated / ros) ==========


def test_batter_loads_all_three_projection_slots():
    """All three upstream projection slots populate when provided."""
    data = {
        "name": "Three Slot Batter",
        "playerid": "three-slot",
        "projections": {"HR": 40, "RBI": 100, "AVG": 0.290},
        "projs_updated": {"HR": 38, "RBI": 95, "AVG": 0.285},
        "ros": {"HR": 12, "RBI": 30, "AVG": 0.275},
    }
    batter = FangraphsBatterModel.model_validate(data)

    assert batter.projections is not None
    assert batter.projections.hr == 40
    assert batter.projs_updated is not None
    assert batter.projs_updated.hr == 38
    assert batter.ros is not None
    assert batter.ros.hr == 12


def test_pitcher_loads_all_three_projection_slots():
    """All three upstream projection slots populate for pitchers."""
    data = {
        "name": "Three Slot Pitcher",
        "playerid": "three-slot-p",
        "projections": {"W": 18, "SO": 220, "ERA": 3.10},
        "projs_updated": {"W": 16, "SO": 200, "ERA": 3.25},
        "ros": {"W": 5, "SO": 70, "ERA": 3.40},
    }
    pitcher = FangraphsPitcherModel.model_validate(data)

    assert pitcher.projections is not None
    assert pitcher.projections.wins == 18
    assert pitcher.projs_updated is not None
    assert pitcher.projs_updated.wins == 16
    assert pitcher.ros is not None
    assert pitcher.ros.wins == 5


def test_batter_missing_slots_default_to_none():
    """projs_updated and ros default to None when absent from the payload (pre-draft)."""
    data = {
        "name": "Preseason Only",
        "playerid": "preseason",
        "projections": {"HR": 25},
    }
    batter = FangraphsBatterModel.model_validate(data)

    assert batter.projections is not None
    assert batter.projections.hr == 25
    assert batter.projs_updated is None
    assert batter.ros is None


def test_batter_empty_slot_dicts_round_trip_to_empty():
    """Upstream emits {} for slots with no data; the empty model dumps to {}.

    This is the load-side of the stable-shape contract — pre-draft players have
    projs_updated={} and ros={} on the wire, which we want to keep semantically
    equivalent to "no data" so downstream consumers can ignore empty slots.
    """
    data = {
        "name": "Empty Slots",
        "playerid": "empty",
        "projections": {"HR": 25},
        "projs_updated": {},
        "ros": {},
    }
    batter = FangraphsBatterModel.model_validate(data)

    # Empty dicts validate to non-None model instances with every field None
    assert batter.projs_updated is not None
    assert batter.projs_updated.hr is None
    # ...so model_dump(exclude_none=True) collapses them back to {}, which is
    # how downstream code distinguishes "has data" from "slot exists but empty".
    assert batter.projs_updated.model_dump(exclude_none=True) == {}
    assert batter.ros is not None
    assert batter.ros.model_dump(exclude_none=True) == {}


def test_three_slots_serialize_with_plural_keys(sample_batter):
    """Loaded fixture player serializes back with the new three-slot key shape."""
    batter = FangraphsBatterModel.model_validate(sample_batter)
    exported = batter.model_dump(by_alias=True, exclude_none=True)

    # New plural key replaces the old singular `projection`
    assert "projections" in exported
    assert "projection" not in exported
    # The two new sibling slots are present when upstream emitted them
    assert ("projs_updated" in exported) or (batter.projs_updated is None)
    assert ("ros" in exported) or (batter.ros is None)


def test_only_preseason_slot_carries_percentiles(fangraphs_batter_data):
    """Per upstream contract, q*/tt_q* percentile fields appear only in the
    `projections` slot — they're derived from the steamer-at-weight-0 trick,
    which is exclusive to the preseason mix. projs_updated and ros never have them.
    """
    saw_percentile_in_preseason = False
    for raw in fangraphs_batter_data:
        batter = FangraphsBatterModel.model_validate(raw)

        # Whenever preseason has q10, fine. Whenever any other slot has q10, fail.
        if batter.projections is not None and batter.projections.q10 is not None:
            saw_percentile_in_preseason = True
        if batter.projs_updated is not None:
            assert batter.projs_updated.q10 is None
            assert batter.projs_updated.tt_q50 is None
        if batter.ros is not None:
            assert batter.ros.q10 is None
            assert batter.ros.tt_q50 is None

    # The fixture should at least include some preseason percentiles, otherwise
    # the contract above is unverified.
    assert saw_percentile_in_preseason, (
        "Expected at least one preseason player with q10 percentile in fixture"
    )
