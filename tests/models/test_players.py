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


def test_player_list_stats(player_models: List[PlayerModel]):
    """Test that player stats are correctly loaded when present."""
    # Check stats for players that have them
    for player in player_models:
        if player.stats:
            # Validate that stats periods exist
            for period, stat_period in player.stats.items():
                # Check that the stat period has the expected attributes
                assert hasattr(stat_period, "points")
                assert hasattr(stat_period, "projected_points")
                assert hasattr(stat_period, "breakdown")
                assert hasattr(stat_period, "projected_breakdown")
