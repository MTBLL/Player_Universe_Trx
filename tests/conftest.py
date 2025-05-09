import json
from pathlib import Path
from typing import Any, Dict, List

import pytest

from player_universe_trx.models.player import PlayerModel


@pytest.fixture
def espn_fixture_path():
    """Fixture providing the path to the ESPN player universe fixture file."""
    return Path(__file__).parent / "fixtures" / "espn_player_universe.json"


@pytest.fixture
def fangraphs_fixture_path():
    """Fixture providing the path to the FanGraphs players fixture file."""
    return Path(__file__).parent / "fixtures" / "fangraph_players.json"


@pytest.fixture
def espn_player_data(espn_fixture_path) -> List[Dict]:
    """Fixture providing the loaded ESPN player data."""
    with open(espn_fixture_path, "r") as f:
        return json.load(f)


@pytest.fixture
def fangraphs_player_data(fangraphs_fixture_path):
    """Fixture providing the loaded FanGraphs player data."""
    with open(fangraphs_fixture_path, "r") as f:
        return json.load(f)


@pytest.fixture
def player_models(espn_player_data) -> List[PlayerModel]:
    """Fixture providing PlayerModel objects created from ESPN data."""
    # Load the first 10 players to keep the test fast
    validated_models = []
    for obj in espn_player_data:
        try:
            model = PlayerModel.model_validate(obj)
            validated_models.append(model)
        except ValueError:
            continue
    return validated_models


@pytest.fixture
def corbin_carroll_espn(espn_player_data) -> Dict[str, Any]:
    """Fixture providing Corbin Carroll's ESPN data."""
    for player in espn_player_data:
        if player.get("name") == "Corbin Carroll":
            return player
    raise ValueError("Corbin Carroll not found in ESPN data")


@pytest.fixture
def corbin_carroll_fangraphs(fangraphs_player_data) -> Dict[str, Any]:
    """Fixture providing Corbin Carroll's FanGraphs data."""
    for player in fangraphs_player_data:
        if player.get("name") == "Corbin Carroll":
            return player
    raise ValueError("Corbin Carroll not found in FanGraphs data")
