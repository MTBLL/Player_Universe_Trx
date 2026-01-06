import json
from unittest.mock import mock_open, patch

import pytest

from player_universe_trx.utils import file_utils


@pytest.fixture
def test_file_path():
    return "path/to/test/file.txt"


@pytest.fixture
def test_file_content():
    return "This is a test file."


def test_load_json_data(espn_fixture_path):
    result = file_utils.load_json_data(espn_fixture_path)
    assert result is not None


def test_load_json_data_file_not_found(test_file_path):
    with pytest.raises(FileNotFoundError) as exc_info:
        file_utils.load_json_data(test_file_path)
        assert exc_info.type is FileNotFoundError


def test_load_json_data_invalid_json(test_file_path, test_file_content):
    mocked_open = mock_open(read_data=test_file_content)
    decode_error = json.JSONDecodeError("Expecting value", test_file_content, 0)

    with patch("builtins.open", mocked_open), patch(
        "player_universe_trx.utils.file_utils.json.load",
        side_effect=decode_error,
    ):
        with pytest.raises(json.JSONDecodeError) as exc_info:
            file_utils.load_json_data(test_file_path)

    assert exc_info.type is json.JSONDecodeError
