import pytest

from player_universe_trx.matchers.player_matcher import match_player_models_on_fangraphs_data
from player_universe_trx.models.player import PlayerModel


def test_matching_players_with_middle_initial():
    """
    Test matching players with middle initials like 'Michael A. Taylor'.
    
    This test verifies that the matching works correctly when:
    1. There are multiple players with the same first and last name
    2. One player has a middle initial
    3. Team information is used to distinguish between them
    """
    # Create test data for Michael A. Taylor on the Twins
    michael_a_taylor = PlayerModel.model_validate(
        {
            "id": 32219,
            "name": "Michael A. Taylor",
            "firstName": "Michael",
            "lastName": "Taylor",
            "displayName": "Michael A. Taylor",
            "shortName": "M. Taylor",
            "proTeam": "MIN",
        }
    )

    # Create another Michael Taylor (without middle initial) on a different team
    other_michael_taylor = PlayerModel.model_validate(
        {
            "id": 45678,
            "name": "Michael Taylor",
            "firstName": "Michael",
            "lastName": "Taylor",
            "displayName": "Michael Taylor",
            "shortName": "M. Taylor",
            "proTeam": "NYY",
        }
    )

    # FanGraphs data for both players (note: no middle initial in either)
    michael_fg_twins = {
        "name": "Michael Taylor",  # No middle initial in FanGraphs data
        "team": "MIN",
        "playerid": "54321"
    }
    
    michael_fg_yankees = {
        "name": "Michael Taylor",  # Same name in FanGraphs data
        "team": "NYY",
        "playerid": "98765"
    }

    # Test matching with same name but different teams
    result = match_player_models_on_fangraphs_data(
        [michael_a_taylor, other_michael_taylor], 
        [michael_fg_twins, michael_fg_yankees]
    )

    # We should have matched both players correctly based on team
    assert len(result["matched"]) == 2
    assert len(result["multiple_matches"]) == 0
    assert len(result["no_matches"]) == 0
    
    # Verify the correct FanGraphs IDs were assigned
    matched_michael_a = next(p for p in result["matched"] if p.id_espn == 32219)
    matched_other_michael = next(p for p in result["matched"] if p.id_espn == 45678)
    
    assert matched_michael_a.id_fangraphs == "54321"
    assert matched_other_michael.id_fangraphs == "98765"