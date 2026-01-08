"""League data loader for ESPN fantasy baseball leagues."""

import logging
import re
from pathlib import Path
from typing import Optional

from player_universe_trx.models.espn import EspnLeagueModel
from player_universe_trx.utils.file_utils import load_json_data

logger = logging.getLogger(__name__)


class LeagueLoader:
    """
    Loader for ESPN fantasy baseball league data.

    Loads league JSON files and validates them against ESPN league models.
    """

    DEFAULT_RESOURCES_PATH = Path("/Users/Shared/BaseballHQ/resources/extract")

    def __init__(
        self, resources_path: Optional[str] = None, year: Optional[int] = None
    ):
        """
        Initialize the league loader.

        Args:
            resources_path: Path to directory containing league files
            year: Year for data files (defaults to current year if not specified)
        """
        if resources_path:
            self.resources_path = Path(resources_path)
        else:
            self.resources_path = self.DEFAULT_RESOURCES_PATH

        self.year = year
        logger.info(
            f"LeagueLoader initialized with resources path: {self.resources_path}, year: {self.year}"
        )

    def _find_latest_file(self, pattern: str) -> Optional[Path]:
        """
        Find the most recent file matching the given pattern.

        Args:
            pattern: Regex pattern to match files

        Returns:
            Path to the most recent matching file, or None if no match found
        """
        matching_files = []
        for file_path in self.resources_path.glob("*.json"):
            if re.match(pattern, file_path.name):
                matching_files.append(file_path)

        if not matching_files:
            logger.warning(f"No files found matching pattern: {pattern}")
            return None

        # Sort by modification time, most recent first
        matching_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        latest_file = matching_files[0]
        logger.info(f"Found latest file: {latest_file.name}")
        return latest_file

    def get_league_file(self, league_id: int) -> Path:
        """
        Get the most recent league file for a specific league ID and year.

        Args:
            league_id: ESPN league ID

        Returns:
            Path to the league file

        Raises:
            FileNotFoundError: If no matching file is found
        """
        if self.year:
            pattern = f"espn_league_{league_id}_{self.year}_\\d{{8}}_\\d{{6}}\\.json"
        else:
            pattern = f"espn_league_{league_id}_\\d{{4}}_\\d{{8}}_\\d{{6}}\\.json"

        file_path = self._find_latest_file(pattern)
        if not file_path:
            raise FileNotFoundError(
                f"No league file found for league {league_id}, year {self.year} in {self.resources_path}"
            )

        return file_path

    def load_league(self, league_id: int) -> EspnLeagueModel:
        """
        Load and validate ESPN league data.

        Args:
            league_id: ESPN league ID

        Returns:
            Validated EspnLeagueModel instance

        Raises:
            FileNotFoundError: If league file not found
            ValueError: If league data validation fails
        """
        file_path = self.get_league_file(league_id)
        logger.info(f"Loading league {league_id} from: {file_path}")

        # Load raw JSON data
        data = load_json_data(str(file_path))

        # Validate against model
        try:
            league = EspnLeagueModel.model_validate(data)
            logger.info(
                f"Successfully loaded league {league.id} with {len(league.teams)} teams"
            )
            return league
        except Exception as e:
            logger.error(f"Failed to validate league data: {e}")
            raise ValueError(f"Invalid league data in {file_path}: {e}")
