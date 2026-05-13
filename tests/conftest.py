import json
from pathlib import Path
from typing import Any, Dict, List

import pytest

from player_universe_trx.models.espn import EspnPlayerModel
from player_universe_trx.models.mtbl import MtblPlayerModel

espn_batters_fixture_file = "espn_batters_2025_20260108_095403.json"
espn_pitchers_fixture_file = "espn_pitchers_2025_20260108_095403.json"
fangraphs_batters_fixture_file = "fangraph_batters_2026_20260512_131824.json"
fangraphs_pitchers_fixture_file = "fangraph_pitchers_2026_20260512_131824.json"


@pytest.fixture
def espn_fixture_path():
    """Fixture providing the path to the ESPN player universe fixture file."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    # Use the actual batter file (most complete for testing)
    return fixtures_dir / espn_batters_fixture_file


@pytest.fixture
def fangraphs_fixture_path():
    """Fixture providing the path to the FanGraphs players fixture file."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    # Use the actual batter file (most complete for testing)
    return fixtures_dir / fangraphs_batters_fixture_file


@pytest.fixture
def savant_fixture_path():
    """Fixture providing the path to the Savant players fixture file."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    return fixtures_dir / "savant_batters_2026_01_03_1444.json"


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
def savant_player_data(savant_fixture_path):
    """Fixture providing the loaded Savant player data."""
    with open(savant_fixture_path, "r") as f:
        return json.load(f)


@pytest.fixture
def player_models(espn_player_data) -> List[MtblPlayerModel]:
    """Fixture providing PlayerModel objects created from ESPN data."""
    # Load the first 10 players to keep the test fast
    validated_models = []
    for obj in espn_player_data:
        try:
            model = MtblPlayerModel.model_validate(obj)
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
        if player.get("slug") == "corbin-carroll":
            return player
    raise ValueError("Corbin Carroll not found in FanGraphs data")


@pytest.fixture
def corbin_carroll_savant(savant_player_data) -> Dict[str, Any]:
    """Fixture providing Corbin Carroll's Savant data."""
    for player in savant_player_data:
        if player.get("slug") == "corbin-carroll":
            return player
    raise ValueError("Corbin Carroll not found in Savant data")


@pytest.fixture
def espn_batter_data(espn_fixture_path) -> List[Dict]:
    """Fixture providing ESPN batter data."""
    with open(espn_fixture_path, "r") as f:
        data = json.load(f)
    return data[:10]


@pytest.fixture
def espn_pitcher_data() -> List[Dict]:
    """Fixture providing ESPN pitcher data."""
    fixtures_path = Path(__file__).parent / "fixtures"
    with open(fixtures_path / espn_pitchers_fixture_file) as f:
        data = json.load(f)
    return data[:10]


@pytest.fixture
def fangraphs_batter_data() -> List[Dict]:
    """Fixture providing FanGraphs batter data."""
    fixtures_path = Path(__file__).parent / "fixtures"
    with open(fixtures_path / fangraphs_batters_fixture_file) as f:
        data = json.load(f)
    return data[:10]


@pytest.fixture
def fangraphs_pitcher_data() -> List[Dict]:
    """Fixture providing FanGraphs pitcher data."""
    fixtures_path = Path(__file__).parent / "fixtures"
    with open(fixtures_path / fangraphs_pitchers_fixture_file) as f:
        data = json.load(f)
    return data[:10]


@pytest.fixture
def savant_batter_data() -> List[Dict]:
    """Fixture providing Savant batter data."""
    fixtures_path = Path(__file__).parent / "fixtures"
    with open(fixtures_path / "savant_batters_2026_01_03_1444.json") as f:
        data = json.load(f)
    return data[:10]


@pytest.fixture
def savant_pitcher_data() -> List[Dict]:
    """Fixture providing Savant pitcher data."""
    fixtures_path = Path(__file__).parent / "fixtures"
    with open(fixtures_path / "savant_pitchers_2026_01_03_1444.json") as f:
        data = json.load(f)
    return data[:10]


@pytest.fixture
def mason_miller_fangraphs() -> Dict[str, Any]:
    """Fixture providing Mason Miller's FanGraphs data (relief pitcher with saves/holds)."""
    fixtures_path = Path(__file__).parent / "fixtures"
    with open(fixtures_path / fangraphs_pitchers_fixture_file) as f:
        data = json.load(f)

    for player in data:
        if player.get("slug") == "mason-miller":
            return player

    # If Mason Miller not found, return any relief pitcher with saves and holds
    for player in data:
        proj = player.get("projections", {})
        if proj.get("SV", 0) > 0 and proj.get("HLD", 0) > 0:
            return player

    raise ValueError("No relief pitcher with saves and holds found in FanGraphs data")


@pytest.fixture
def mason_miller_savant() -> Dict[str, Any]:
    """Fixture providing Mason Miller's Savant data."""
    fixtures_path = Path(__file__).parent / "fixtures"
    with open(fixtures_path / "savant_pitchers_2026_01_03_1444.json") as f:
        data = json.load(f)

    for player in data:
        if player.get("name") == "Mason Miller":
            return player

    raise ValueError("No player named Mason Miller found in Savant data")


@pytest.fixture
def mason_miller_espn(player_models) -> EspnPlayerModel:
    """Fixture providing Mason Miller's ESPN data."""
    for player in player_models:
        if player.slug == "mason-miller":
            return player

    raise ValueError("No player named Mason Miller found in ESPN data")
