import json
from datetime import datetime
from pathlib import Path

import pytest

from player_universe_trx.loaders.file_loader import DataLoader


@pytest.fixture
def fixtures_dir():
    """Fixture providing the path to the test fixtures directory."""
    return Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def temp_dir_with_files(tmp_path):
    """Fixture creating a temporary directory with test files."""
    import time

    test_data = [{"id": 1, "name": "Test Player"}]

    files_ordered = [
        ("espn_batters_2025_20260102_090000.json", test_data),
        ("espn_batters_2025_20260103_103120.json", test_data),
        ("espn_league_10998_2025_20260102_143242.json", test_data),
    ]

    for filename, data in files_ordered:
        file_path = tmp_path / filename
        with open(file_path, "w") as f:
            json.dump(data, f)
        time.sleep(0.01)

    return tmp_path


def test_init_and_default_path(fixtures_dir):
    """Test initialization with custom and default paths."""
    loader = DataLoader(resources_path=str(fixtures_dir), year=2024)
    assert loader.resources_path == fixtures_dir
    assert loader.year == 2024

    loader_default_year = DataLoader(resources_path=str(fixtures_dir))
    assert loader_default_year.year == datetime.now().year

    assert (
        DataLoader.DEFAULT_RESOURCES_PATH
        == "/Users/Shared/BaseballHQ/resources/extract"
    )

    with pytest.raises(ValueError, match="Resources path does not exist"):
        DataLoader(resources_path="/nonexistent/path")


def test_find_latest_file(temp_dir_with_files):
    """Test finding latest file by modification time."""
    loader = DataLoader(resources_path=str(temp_dir_with_files), year=2025)

    result = loader._find_latest_file(r"espn_batters_2025_\d{8}_\d{6}\.json")
    assert isinstance(result, Path)
    assert result.name == "espn_batters_2025_20260103_103120.json"

    assert loader._find_latest_file(r"nonexistent_\d{8}_\d{6}\.json") is None


def test_extract_timestamp(fixtures_dir):
    """Test timestamp extraction from filenames."""
    loader = DataLoader(resources_path=str(fixtures_dir), year=2025)

    timestamp = loader._extract_timestamp_from_filename(
        "espn_batters_2025_20260103_103120.json"
    )
    assert timestamp == datetime(2026, 1, 3, 10, 31, 20)

    assert loader._extract_timestamp_from_filename("invalid_filename.json") is None
    assert (
        loader._extract_timestamp_from_filename(
            "espn_batters_2025_20269903_103120.json"
        )
        is None
    )


def test_get_file_methods(fixtures_dir):
    """Test all get_*_file methods for success and error cases."""
    loader = DataLoader(resources_path=str(fixtures_dir), year=2025)

    assert (
        loader.get_espn_batters_file().name == "espn_batters_2025_20260103_103120.json"
    )
    assert (
        loader.get_espn_pitchers_file().name
        == "espn_pitchers_2025_20260103_103120.json"
    )
    assert (
        loader.get_espn_league_file(league_id=10998).name
        == "espn_league_10998_2025_20260102_143242.json"
    )
    assert "espn_league_" in loader.get_espn_league_file().name
    assert (
        loader.get_fangraphs_batters_file().name
        == "fangraph_batters_2025_20260103_135002.json"
    )
    assert (
        loader.get_fangraphs_pitchers_file().name
        == "fangraph_pitchers_2025_20260103_135002.json"
    )

    # Test Savant file methods (year 2026 for Savant fixtures)
    loader_2026 = DataLoader(resources_path=str(fixtures_dir), year=2026)
    assert (
        loader_2026.get_savant_batters_file().name
        == "savant_batters_2026_01_03_1444.json"
    )
    assert (
        loader_2026.get_savant_pitchers_file().name
        == "savant_pitchers_2026_01_03_1444.json"
    )

    loader_no_files = DataLoader(resources_path=str(fixtures_dir), year=2099)
    with pytest.raises(
        FileNotFoundError, match="No ESPN batters file found for year 2099"
    ):
        loader_no_files.get_espn_batters_file()
    with pytest.raises(
        FileNotFoundError, match="No ESPN pitchers file found for year 2099"
    ):
        loader_no_files.get_espn_pitchers_file()
    with pytest.raises(FileNotFoundError, match="No ESPN league file found"):
        loader_no_files.get_espn_league_file()
    with pytest.raises(FileNotFoundError, match="league 12345"):
        loader_no_files.get_espn_league_file(league_id=12345)
    with pytest.raises(
        FileNotFoundError, match="No FanGraphs batters file found for year 2099"
    ):
        loader_no_files.get_fangraphs_batters_file()
    with pytest.raises(
        FileNotFoundError, match="No FanGraphs pitchers file found for year 2099"
    ):
        loader_no_files.get_fangraphs_pitchers_file()
    with pytest.raises(
        FileNotFoundError, match="No Savant batters file found for year 2099"
    ):
        loader_no_files.get_savant_batters_file()
    with pytest.raises(
        FileNotFoundError, match="No Savant pitchers file found for year 2099"
    ):
        loader_no_files.get_savant_pitchers_file()


def test_load_methods(fixtures_dir):
    """Test all load_* methods."""
    loader = DataLoader(resources_path=str(fixtures_dir), year=2025)

    batters = loader.load_espn_batters()
    assert isinstance(batters, list) and len(batters) > 0

    pitchers = loader.load_espn_pitchers()
    assert isinstance(pitchers, list) and len(pitchers) > 0

    league = loader.load_espn_league(league_id=10998)
    assert isinstance(league, (dict, list))

    league_no_id = loader.load_espn_league()
    assert isinstance(league_no_id, (dict, list))

    fg_batters = loader.load_fangraphs_batters()
    assert isinstance(fg_batters, list) and len(fg_batters) > 0

    fg_pitchers = loader.load_fangraphs_pitchers()
    assert isinstance(fg_pitchers, list) and len(fg_pitchers) > 0

    # Test Savant load methods (year 2026 for Savant fixtures)
    loader_2026 = DataLoader(resources_path=str(fixtures_dir), year=2026)

    sv_batters = loader_2026.load_savant_batters()
    assert isinstance(sv_batters, list) and len(sv_batters) > 0

    sv_pitchers = loader_2026.load_savant_pitchers()
    assert isinstance(sv_pitchers, list) and len(sv_pitchers) > 0
