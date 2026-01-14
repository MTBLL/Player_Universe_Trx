from player_universe_trx.models.fangraphs import FangraphsPlayerModel
from player_universe_trx.models.mtbl import MtblPlayerModel


def test_merge_fangraphs_data_corbin_carroll(
    corbin_carroll_espn, corbin_carroll_fangraphs
):
    """Test merging FanGraphs data into a PlayerModel for Corbin Carroll."""
    # Create player model from ESPN data
    player = MtblPlayerModel.model_validate(corbin_carroll_espn)

    # Initial assertions
    assert isinstance(player.id_espn, int)
    assert player.id_fangraphs is None
    assert player.id_xmlbam is None
    assert isinstance(player.pro_team, str)

    # Store original values
    original_espn_id = player.id_espn
    original_team = player.pro_team

    corbin_carroll_fangraphs = FangraphsPlayerModel.model_validate(
        corbin_carroll_fangraphs
    )
    # Merge FanGraphs data
    player.merge_fangraphs_data(corbin_carroll_fangraphs)

    # Assertions after merging
    assert player.id_espn == original_espn_id  # ESPN ID should not change
    assert player.pro_team == original_team
    assert (
        player.id_fangraphs == corbin_carroll_fangraphs.playerid
    )  # FanGraphs ID should be set
    assert (
        player.id_xmlbam == corbin_carroll_fangraphs.xmlbam_id
    )  # MLB ID should be set
    assert player.pro_team == corbin_carroll_fangraphs.team  # Team should be updated
    assert player.fangraphs_api_route == corbin_carroll_fangraphs.stats_api


def test_merge_fangraphs_data_missing_values(corbin_carroll_espn):
    """Test merging FanGraphs data with missing values."""
    player = MtblPlayerModel.model_validate(corbin_carroll_espn)

    # Prepare incomplete FanGraphs data
    incomplete_data = FangraphsPlayerModel(name="Corbin Carroll", playerid="12345")

    # Merge incomplete data
    player.merge_fangraphs_data(incomplete_data)

    # Check that only provided fields were updated
    assert player.id_fangraphs == "12345"
    assert player.id_xmlbam is None  # Should remain None


def test_merge_fangraphs_data_invalid_input():
    """Test merging with invalid input."""
    player = MtblPlayerModel.model_validate({"id": 1, "name": "Test Player"})

    # Try merging with None
    player.merge_fangraphs_data()
    assert player.id_fangraphs is None  # Should remain unchanged


def test_merge_fangraphs_data_empty_dict():
    """Test merging with an empty dictionary."""
    player = MtblPlayerModel.model_validate({"id": 1, "name": "Test Player"})

    # Try merging with empty dict
    player.merge_fangraphs_data(FangraphsPlayerModel(name="Test Player", playerid="1"))
    assert player.id_fangraphs == "1"  # Should remain unchanged


def test_merge_mason_miller():
    pass
