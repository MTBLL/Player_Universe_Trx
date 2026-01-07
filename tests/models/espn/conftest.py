import json
from pathlib import Path
from typing import Dict, List

import pytest

from tests.conftest import espn_batters_fixture_file, espn_pitchers_fixture_file


@pytest.fixture
def fixtures_dir():
    """Path to test fixtures directory."""
    return Path(__file__).parent.parent.parent / "fixtures"


@pytest.fixture
def espn_batter_data(fixtures_dir) -> List[Dict]:
    """Load first 3 ESPN batter records from fixture."""
    with open(fixtures_dir / espn_batters_fixture_file) as f:
        data = json.load(f)
    return data[:3]


@pytest.fixture
def espn_pitcher_data(fixtures_dir) -> List[Dict]:
    """Load first 3 ESPN pitcher records from fixture."""
    with open(fixtures_dir / espn_pitchers_fixture_file) as f:
        data = json.load(f)
    return data[:3]


@pytest.fixture
def sample_batter(espn_batter_data) -> Dict:
    """Single batter record."""
    return espn_batter_data[0]


@pytest.fixture
def sample_pitcher(espn_pitcher_data) -> Dict:
    """Single pitcher record."""
    return espn_pitcher_data[0]
