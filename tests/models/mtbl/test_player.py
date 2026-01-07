from typing import Dict

import pytest

from player_universe_trx.models.espn.batter import EspnBatterModel
from player_universe_trx.models.mtbl import MtblPlayerModel
from player_universe_trx.utils.model_utils import create_espn_batter_models


class TestPlayerModel:
    def test_skip_retired_players(self):
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

        espn_player = create_espn_batter_models([retired_player])[0]

        # Test that validation fails for retired players
        with pytest.raises(ValueError, match="Retired player") as exc_info:
            espn_raw = EspnBatterModel.model_dump(espn_player)
            MtblPlayerModel.model_validate(espn_raw)
            assert exc_info.value.args[0] == "Retired player"
