import pytest

from player_universe_trx.utils.model_utils import create_player_models
from player_universe_trx.models.player import PlayerModel


def test_create_player_models(espn_player_data):
    """
    Test creating player models from ESPN player data.
    
    This test verifies that:
    1. Active players are correctly converted to PlayerModel instances
    2. Retired players are filtered out
    3. The correct number of player models are created
    4. The created models have the correct attributes
    """
    # Create player models from the ESPN fixture data
    player_models = create_player_models(espn_player_data)
    
    # Verify that player models were created
    assert player_models is not None
    assert isinstance(player_models, list)
    assert len(player_models) > 0
    
    # Verify all models are PlayerModel instances
    assert all(isinstance(model, PlayerModel) for model in player_models)
    
    # Verify no retired players were included (status == "retired")
    assert all(model.status != "retired" for model in player_models)
    
    # Verify that key fields were correctly populated in the models
    for model in player_models:
        # Required fields
        assert model.id_espn is not None
        
        # Check name-related fields when available
        if model.name:
            if model.first_name and model.last_name:
                assert model.name_contains_first_and_last()
            
            # Double-check display name when available
            if model.display_name:
                assert model.name in model.display_name or model.display_name in model.name


def test_create_player_models_with_specific_players(espn_player_data):
    """
    Test creating player models with focus on specific players.
    
    This test verifies that specific players from the fixture data
    are correctly processed.
    """
    player_models = create_player_models(espn_player_data)
    
    # Find specific players we want to test
    # For example, testing a well-known player like Corbin Carroll
    corbin_carroll = None
    for model in player_models:
        if model.name == "Corbin Carroll":
            corbin_carroll = model
            break
    
    # Verify that we found Corbin Carroll
    assert corbin_carroll is not None
    
    # Verify specific attributes
    assert corbin_carroll.first_name == "Corbin"
    assert corbin_carroll.last_name == "Carroll"
    assert corbin_carroll.pro_team is not None
    
    # Verify data type conversions for specific fields
    # For example, jersey number should be an integer
    if corbin_carroll.jersey is not None:
        assert isinstance(corbin_carroll.jersey, int)


def test_retired_players_are_filtered(espn_player_data):
    """
    Test that retired players are filtered out during model creation.
    
    This test verifies that players with status="retired" are not included
    in the output from create_player_models.
    """
    # First count the total number of players and retired players in the raw data
    total_players = len(espn_player_data)
    retired_players = sum(1 for player in espn_player_data if player.get("status") == "retired")
    
    # Create player models
    player_models = create_player_models(espn_player_data)
    
    # Verify that the number of player models equals total_players - retired_players
    assert len(player_models) == total_players - retired_players
    
    # Double-check by verifying that none of the models have status="retired"
    assert all(model.status != "retired" for model in player_models)


def test_create_player_models_with_empty_input():
    """Test creating player models with empty input."""
    player_models = create_player_models([])
    
    assert player_models is not None
    assert isinstance(player_models, list)
    assert len(player_models) == 0