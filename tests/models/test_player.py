from typing import Dict

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
    if player_name == "Corbin Carroll":
        assert player.slug_espn == "corbin-carroll"
    if player_name == "Gunnar Henderson":
        assert player.slug_espn == "gunnar-henderson"

    assert player.slug_fangraphs is None  # hasn't been read yet

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


def test_skip_retired_players():
    retired_player: Dict = {
        "id": 32286,
        "name": "Danry Vasquez",
        "first_name": "Danry",
        "last_name": "Vasquez",
        "display_name": "Danry Vasquez",
        "short_name": "D. Vasquez",
        "nickname": "",
        "slug": "danry-vasquez",
        "primary_position": "CF",
        "eligible_slots": ["CF", "OF", "UTIL"],
        "position_name": "Right Field",
        "pos": "RF",
        "pro_team": "HOU",
        "injury_status": None,
        "status": "retired",
        "injured": False,
        "active": False,
        "percent_owned": 0.0,
        "weight": 189.0,
        "display_weight": "189 lbs",
        "height": 75,
        "display_height": "6' 3\"",
        "bats": "Left",
        "throws": "Right",
        "date_of_birth": "1994-01-08",
        "birth_place": {"city": "Ocumare Del Tuy", "country": "Venezuela"},
        "debut_year": None,
        "jersey": "",
        "headshot": None,
        "stats": {},
    }

    # Test that validation fails for retired players
    with pytest.raises(ValueError, match="Retired player"):
        PlayerModel.model_validate(retired_player)

    # Test that active players process normally
    active_player_data = retired_player.copy()
    active_player_data["status"] = "active"
    active_result = PlayerModel.model_validate(active_player_data)
    assert isinstance(active_result, PlayerModel)
