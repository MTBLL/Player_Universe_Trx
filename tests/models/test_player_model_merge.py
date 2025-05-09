from player_universe_trx.models.player import PlayerModel


def test_merge_fangraphs_data_corbin_carroll(
    corbin_carroll_espn, corbin_carroll_fangraphs
):
    """Test merging FanGraphs data into a PlayerModel for Corbin Carroll."""
    # Create player model from ESPN data
    player = PlayerModel.model_validate(corbin_carroll_espn)

    # Initial assertions
    assert player.id_espn is not None
    assert player.id_fangraphs is None
    assert player.id_xmlbam is None
    assert player.pro_team is not None

    # Store original values
    original_espn_id = player.id_espn
    original_team = player.pro_team

    # Merge FanGraphs data
    player.merge_fangraphs_data(corbin_carroll_fangraphs)

    # Assertions after merging
    assert player.id_espn == original_espn_id  # ESPN ID should not change
    assert player.pro_team == original_team
    assert (
        player.id_fangraphs == corbin_carroll_fangraphs["playerid"]
    )  # FanGraphs ID should be set
    assert (
        player.id_xmlbam == corbin_carroll_fangraphs["xmlbam_id"]
    )  # MLB ID should be set
    assert player.pro_team == corbin_carroll_fangraphs["team"]  # Team should be updated
    assert player.slug_fangraphs == corbin_carroll_fangraphs["slug"]
    assert player.fangraphs_api_route == corbin_carroll_fangraphs["stats_api"]


def test_merge_fangraphs_data_missing_values(corbin_carroll_espn):
    """Test merging FanGraphs data with missing values."""
    player = PlayerModel.model_validate(corbin_carroll_espn)

    # Prepare incomplete FanGraphs data
    incomplete_data = {
        "name": "Corbin Carroll",
        "playerid": "12345",
        # Missing other fields
    }

    # Merge incomplete data
    player.merge_fangraphs_data(incomplete_data)

    # Check that only provided fields were updated
    assert player.id_fangraphs == "12345"
    assert player.id_xmlbam is None  # Should remain None
    assert player.slug_fangraphs is None  # Should remain None


def test_merge_fangraphs_data_with_nonascii_name():
    """Test handling of non-ASCII characters in names."""
    # Create a simple player model
    player = PlayerModel.model_validate({"id": 1, "name": "Test Player"})

    # FanGraphs data with non-ASCII name
    data = {
        "name": "Jos\u00e9 Ram\u00edrez",
        "ascii_name": "Jose Ramirez",
        "playerid": "12345",
    }

    player.merge_fangraphs_data(data)

    # Check that name_nonascii is populated correctly
    assert player.name_nonascii == "Jos\u00e9 Ram\u00edrez"

    # Test with matching ASCII and non-ASCII names
    player = PlayerModel.model_validate({"id": 1, "name": "Test Player"})
    data = {
        "name": "Bobby Witt Jr.",
        "ascii_name": "Bobby Witt Jr.",
        "playerid": "12345",
    }

    player.merge_fangraphs_data(data)
    assert player.name_nonascii == "Bobby Witt Jr."


def test_merge_fangraphs_data_invalid_input():
    """Test merging with invalid input."""
    player = PlayerModel.model_validate({"id": 1, "name": "Test Player"})

    # Try merging with None
    player.merge_fangraphs_data({None: None})
    assert player.id_fangraphs is None  # Should remain unchanged


def test_merge_fangraphs_data_empty_dict():
    """Test merging with an empty dictionary."""
    player = PlayerModel.model_validate({"id": 1, "name": "Test Player"})

    # Try merging with empty dict
    player.merge_fangraphs_data({})
    assert player.id_fangraphs is None  # Should remain unchanged
