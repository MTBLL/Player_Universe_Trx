import pytest
from typing import Dict, List

from player_universe_trx.models.player import PlayerModel
from player_universe_trx.matchers.player_matcher import match_player_models_on_fangraphs_data


def test_matching_players_with_accents():
    """Test matching players when FanGraphs data contains accented characters."""
    # Create an ESPN player with regular ASCII characters
    espn_player = PlayerModel(
        id_espn=32367,
        name="Eugenio Suarez",
        first_name="Eugenio",
        last_name="Suarez",
        display_name="Eugenio Suarez",
        short_name="E. Suarez",
        pro_team="ARI",
        primary_position="3B",
        eligible_slots=["3B", "1B/3B", "IF", "UTIL"],
        status="active",
    )

    # Create FanGraphs data with accented characters
    fangraphs_data: List[Dict] = [
        {
            "name": "Eugenio Su\u00e1rez",  # This is "Eugenio Suárez" with an acute accent on the a
            "ascii_name": "Eugenio Suarez",  # ASCII-normalized version
            "team": "ARI",
            "playerid": "12552",
            "xmlbam_id": 553993,
            "slug": "eugenio-suarez",
            "stats_api": "/players/eugenio-suarez/12552/stats.json?position=3B",
        },
        {
            "name": "José Ramírez",  # Another player with accents
            "ascii_name": "Jose Ramirez",
            "team": "CLE",
            "playerid": "14836",
            "xmlbam_id": 542432,
            "slug": "jose-ramirez",
            "stats_api": "/players/jose-ramirez/14836/stats.json?position=3B",
        }
    ]

    # Match the player against FanGraphs data
    result = match_player_models_on_fangraphs_data([espn_player], fangraphs_data)

    # Verify results
    assert len(result["matched"]) == 1, "Expected one matched player"
    assert len(result["no_matches"]) == 0, "Expected no unmatched players"
    assert len(result["multiple_matches"]) == 0, "Expected no ambiguous matches"

    # Verify the correct match was made
    matched_player = result["matched"][0]
    assert matched_player.id_espn == 32367, "Expected to match Eugenio Suarez"
    assert matched_player.id_fangraphs == "12552", "Expected to match with correct FanGraphs ID"
    assert matched_player.pro_team == "ARI", "Expected to match with correct team"


def test_matching_players_with_multiple_accented_candidates():
    """Test matching players when multiple candidates have accented characters."""
    # Create an ESPN player with regular ASCII characters
    espn_player = PlayerModel(
        id_espn=31062,
        name="Jose Ramirez",
        first_name="Jose",
        last_name="Ramirez",
        display_name="Jose Ramirez",
        short_name="J. Ramirez",
        pro_team="CLE",
        primary_position="3B",
        eligible_slots=["3B", "1B/3B", "IF", "UTIL"],
        status="active",
    )

    # Create FanGraphs data with multiple players having the same ASCII name
    fangraphs_data: List[Dict] = [
        {
            "name": "José Ramírez",  # With accents
            "ascii_name": "Jose Ramirez",
            "team": "CLE",
            "playerid": "14836",
            "xmlbam_id": 542432,
            "slug": "jose-ramirez",
            "stats_api": "/players/jose-ramirez/14836/stats.json?position=3B",
        },
        {
            "name": "Jose Ramirez",  # No accents
            "ascii_name": "Jose Ramirez",
            "team": "LAD",
            "playerid": "24556",
            "xmlbam_id": 665856,
            "slug": "jose-ramirez-2",
            "stats_api": "/players/jose-ramirez-2/24556/stats.json?position=OF",
        }
    ]

    # Match the player against FanGraphs data
    result = match_player_models_on_fangraphs_data([espn_player], fangraphs_data)

    # Verify results - should be matched to the CLE player based on team
    assert len(result["matched"]) == 1, "Expected one matched player"
    assert len(result["no_matches"]) == 0, "Expected no unmatched players"
    assert len(result["multiple_matches"]) == 0, "Expected no ambiguous matches"

    # Verify the correct match was made
    matched_player = result["matched"][0]
    assert matched_player.id_espn == 31062, "Expected to match Jose Ramirez"
    assert matched_player.id_fangraphs == "14836", "Expected to match with correct FanGraphs ID"
    assert matched_player.pro_team == "CLE", "Expected to match with correct team"