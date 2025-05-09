from typing import List

from player_universe_trx.models.player import PlayerModel


def test_player_name_consistency(player_models: List[PlayerModel]):
    """
    Test that player data has consistent name fields.

    Handles edge cases like middle initials, suffixes, etc.
    Example: 'Michael A. Taylor' contains both 'Michael' (first_name) and 'Taylor' (last_name)
    """
    for player in player_models:
        # Only test if all name components are present
        if player.first_name and player.last_name and player.name:
            # Use the name_contains_first_and_last helper method to check name consistency
            assert player.name_contains_first_and_last(), (
                f"Name '{player.name}' should contain both first name '{player.first_name}' "
                f"and last name '{player.last_name}'"
            )

            # Alternatively, if name_contains_first_and_last() isn't available:
            # assert player.first_name in player.name, f"First name '{player.first_name}' not found in full name '{player.name}'"
            # assert player.last_name in player.name, f"Last name '{player.last_name}' not found in full name '{player.name}'"


def test_display_name_consistency(player_models: List[PlayerModel]):
    """Test that display_name is consistent with name when both are present."""
    for player in player_models:
        if player.name and player.display_name:
            # In many cases these should be identical, but we allow flexibility
            # Some data sources might format display_name differently
            assert (
                player.name in player.display_name or player.display_name in player.name
            ), (
                f"Name '{player.name}' and display name '{player.display_name}' should be related"
            )


def test_short_name_format(player_models: List[PlayerModel]):
    """Test that short_name follows expected format like 'M. Taylor'."""
    for player in player_models:
        if player.short_name and player.last_name:
            # Short name should contain the last name
            assert player.last_name in player.short_name, (
                f"Short name '{player.short_name}' should contain last name '{player.last_name}'"
            )

            # Most short names have format "X. Lastname" but we don't require this
            # as formatting might vary by data source
