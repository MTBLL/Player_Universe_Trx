from typing import List

from player_universe_trx.models import PlayerModel


def test_player_list_creation(player_models: List[PlayerModel]):
    """Test that we can create multiple player models from a list of player data."""
    # Check that we have players in our list
    assert len(player_models) > 0

    # Check that each item is a PlayerModel
    for player in player_models:
        assert isinstance(player, PlayerModel)


def test_player_list_attributes(player_models: List[PlayerModel]):
    """Test that player models in the list have the expected attributes."""
    for player in player_models:
        # Check that essential attributes are present
        assert hasattr(player, "id_espn")
        assert hasattr(player, "name")
        assert hasattr(player, "first_name")
        assert hasattr(player, "last_name")

        # Check that team information is present
        assert hasattr(player, "pro_team")

        # Check status information
        assert hasattr(player, "status")
        assert isinstance(player.active, bool)
        assert isinstance(player.injured, bool)
