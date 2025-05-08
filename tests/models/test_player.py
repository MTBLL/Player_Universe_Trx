from typing import List

import pytest

from player_universe_trx.models.player import BirthPlace, PlayerModel, StatPeriod


@pytest.mark.parametrize(
    "player_name",
    ["Corbin Carroll", "Gunnar Henderson"],
)
def test_player_model_from_espn_json(espn_player_data, player_name):
    """Test loading PlayerModel from ESPN JSON data."""
    # Take the first player from the data
    player_data = next(
        (player for player in espn_player_data if player["name"] == player_name)
    )

    # Create a PlayerModel from the data
    player = PlayerModel.model_validate(player_data)

    # Test basic properties
    assert player.id_espn == player_data["id"]
    assert player.name == player_data["name"]
    assert player.name == player_name
    assert player.first_name == player_data["first_name"]
    assert player.last_name == player_data["last_name"]
    assert (
        player.slug_espn == "corbin-carroll"
        if player_name == "Corbin Carroll"
        else "gunnar-henderson"
    )
    assert player.slug_fangraphs is None  # hasn't been readin yet

    # Test nested properties
    if player_data.get("birth_place"):
        assert player.birth_place is not None
        assert isinstance(player.birth_place, BirthPlace)
        assert player.birth_place.city == player_data["birth_place"]["city"]
        assert player.birth_place.country == player_data["birth_place"]["country"]

    # Test stats conversion if the player has stats
    if player_data.get("stats") and player_data["stats"]:
        # Convert string keys to appropriate types if needed
        for period, stats in player_data["stats"].items():
            # For period keys that should be integers (like years)
            try:
                period_key = int(period)
            except ValueError:
                period_key = period

            assert period_key in player.stats
            assert isinstance(player.stats[period_key], StatPeriod)

            # Verify stats data was properly loaded
            if isinstance(stats, dict) and "points" in stats:
                assert player.stats[period_key].points == stats["points"]


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


def test_player_data_consistency(player_models: List[PlayerModel]):
    """Test that player data is consistent with the expected format."""
    for player in player_models:
        # Test that name matches first/last name when both are present
        if player.first_name and player.last_name and player.name:
            assert f"{player.first_name} {player.last_name}" == player.name

        # Test that birth_place is properly populated when present
        if player.birth_place:
            assert hasattr(player.birth_place, "city")
            assert hasattr(player.birth_place, "country")
