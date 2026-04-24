import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from player_universe_trx.utils.file_utils import load_json_data

logger = logging.getLogger("player_universe_trx.loaders")


class DataLoader:
    """
    Handles loading of all input data files with support for timestamped file discovery.

    File naming conventions:
    - ESPN Batters: espn_batters_{year}_{timestamp}.json
    - ESPN Pitchers: espn_pitchers_{year}_{timestamp}.json
    - ESPN League: espn_league_{league_id}_{year}_{timestamp}.json
    - FanGraphs Batters: fangraph_batters_{year}_{timestamp}.json
    - FanGraphs Pitchers: fangraph_pitchers_{year}_{timestamp}.json
    - Savant Batters: savant_batters_{year}_{MM}_{DD}_{HHMM}.json
    - Savant Pitchers: savant_pitchers_{year}_{MM}_{DD}_{HHMM}.json

    Note: Savant uses a different timestamp format (YYYY_MM_DD_HHMM) vs ESPN/FanGraphs (YYYYMMDD_HHMMSS)
    """

    DEFAULT_RESOURCES_PATH = "/Users/Shared/BaseballHQ/resources/extract"

    def __init__(
        self, resources_path: Optional[str] = None, year: Optional[int] = None
    ):
        """
        Initialize the DataLoader.

        Args:
            resources_path: Path to the directory containing input files.
                          Defaults to /Users/Shared/BaseballHQ/resources/extract
            year: Year to use for file discovery. Defaults to current year.
        """
        self.resources_path = Path(resources_path or self.DEFAULT_RESOURCES_PATH)
        self.year = year or datetime.now().year

        if not self.resources_path.exists():
            raise ValueError(f"Resources path does not exist: {self.resources_path}")

        logger.info(
            f"DataLoader initialized with resources path: {self.resources_path}, year: {self.year}"
        )

    def _find_latest_file(self, pattern: str) -> Optional[Path]:
        """
        Find the most recent file matching the given pattern.

        Args:
            pattern: Regex pattern to match filenames

        Returns:
            Path to the most recent file, or None if no files match
        """
        matching_files = []

        for file in self.resources_path.iterdir():
            if file.is_file() and re.match(pattern, file.name):
                matching_files.append(file)

        if not matching_files:
            logger.warning(f"No files found matching pattern: {pattern}")
            return None

        # Sort by modification time, most recent first
        latest_file = max(matching_files, key=lambda f: f.stat().st_mtime)
        logger.info(f"Found latest file: {latest_file.name}")
        return latest_file

    def _extract_timestamp_from_filename(self, filename: str) -> Optional[datetime]:
        """
        Extract timestamp from filename in format YYYYMMDD_HHMMSS.

        Args:
            filename: Name of the file

        Returns:
            datetime object if timestamp found, None otherwise
        """
        timestamp_pattern = r"(\d{8}_\d{6})"
        match = re.search(timestamp_pattern, filename)

        if match:
            try:
                return datetime.strptime(match.group(1), "%Y%m%d_%H%M%S")
            except ValueError:
                logger.warning(f"Invalid timestamp format in filename: {filename}")
                return None
        return None

    def _extract_savant_season_from_filename(self, filename: str) -> Optional[int]:
        """
        Extract Savant season from filename in format savant_<role>_<season>_<MM>_<DD>_<HHMM>.json.

        Args:
            filename: Name of the Savant file

        Returns:
            Season year if found, None otherwise
        """
        season_pattern = r"^savant_(?:batters|pitchers)_(\d{4})_\d{2}_\d{2}_\d{4}\.json$"
        match = re.match(season_pattern, filename)
        if not match:
            return None

        return int(match.group(1))

    @staticmethod
    def _annotate_savant_rows(
        rows: List[Dict], player_type: str, season: Optional[int]
    ) -> List[Dict]:
        """
        Attach downstream metadata that Savant rows do not include directly.

        The upstream extractor documents player_type as part of the row schema and
        season as ingestion context. Older fixture files may not include
        player_type, so this method fills it from the file role without
        overwriting newer extractor output.
        """
        annotated_rows = []
        for row in rows:
            annotated = dict(row)
            annotated.setdefault("player_type", player_type)
            if season is not None:
                annotated.setdefault("season", season)
            annotated_rows.append(annotated)

        return annotated_rows

    def get_espn_batters_file(self) -> Path:
        """
        Get the most recent ESPN batters file for the configured year.

        Returns:
            Path to the ESPN batters file

        Raises:
            FileNotFoundError: If no matching file is found
        """
        pattern = f"espn_batters_{self.year}_\\d{{8}}_\\d{{6}}\\.json"

        file_path = self._find_latest_file(pattern)
        if not file_path:
            raise FileNotFoundError(
                f"No ESPN batters file found for year {self.year} in {self.resources_path}"
            )

        return file_path

    def get_espn_pitchers_file(self) -> Path:
        """
        Get the most recent ESPN pitchers file for the configured year.

        Returns:
            Path to the ESPN pitchers file

        Raises:
            FileNotFoundError: If no matching file is found
        """
        pattern = f"espn_pitchers_{self.year}_\\d{{8}}_\\d{{6}}\\.json"

        file_path = self._find_latest_file(pattern)
        if not file_path:
            raise FileNotFoundError(
                f"No ESPN pitchers file found for year {self.year} in {self.resources_path}"
            )

        return file_path

    def get_espn_league_file(self, league_id: Optional[int] = None) -> Path:
        """
        Get the most recent ESPN league file for the configured year.

        Args:
            league_id: Optional league ID to filter files

        Returns:
            Path to the ESPN league file

        Raises:
            FileNotFoundError: If no matching file is found
        """
        if league_id:
            pattern = f"espn_league_{league_id}_{self.year}_\\d{{8}}_\\d{{6}}\\.json"
        else:
            pattern = f"espn_league_\\d+_{self.year}_\\d{{8}}_\\d{{6}}\\.json"

        file_path = self._find_latest_file(pattern)
        if not file_path:
            league_info = f"league {league_id} " if league_id else ""
            raise FileNotFoundError(
                f"No ESPN league file found for {league_info}year {self.year} in {self.resources_path}"
            )

        return file_path

    def get_fangraphs_batters_file(self) -> Path:
        """
        Get the most recent FanGraphs batters file for the configured year.

        Returns:
            Path to the FanGraphs batters file

        Raises:
            FileNotFoundError: If no matching file is found
        """
        pattern = f"fangraph_batters_{self.year}_\\d{{8}}_\\d{{6}}\\.json"

        file_path = self._find_latest_file(pattern)
        if not file_path:
            raise FileNotFoundError(
                f"No FanGraphs batters file found for year {self.year} in {self.resources_path}"
            )

        return file_path

    def get_fangraphs_pitchers_file(self) -> Path:
        """
        Get the most recent FanGraphs pitchers file for the configured year.

        Returns:
            Path to the FanGraphs pitchers file

        Raises:
            FileNotFoundError: If no matching file is found
        """
        pattern = f"fangraph_pitchers_{self.year}_\\d{{8}}_\\d{{6}}\\.json"

        file_path = self._find_latest_file(pattern)
        if not file_path:
            raise FileNotFoundError(
                f"No FanGraphs pitchers file found for year {self.year} in {self.resources_path}"
            )

        return file_path

    def load_espn_batters(self) -> List[Dict]:
        """
        Load ESPN batters data for the configured year.

        Returns:
            List of ESPN batter dictionaries
        """
        file_path = self.get_espn_batters_file()
        logger.info(f"Loading ESPN batters from: {file_path}")
        return load_json_data(str(file_path))

    def load_espn_pitchers(self) -> List[Dict]:
        """
        Load ESPN pitchers data for the configured year.

        Returns:
            List of ESPN pitcher dictionaries
        """
        file_path = self.get_espn_pitchers_file()
        logger.info(f"Loading ESPN pitchers from: {file_path}")
        return load_json_data(str(file_path))

    def load_espn_league(self, league_id: Optional[int] = None) -> List[Dict]:
        """
        Load ESPN league data for the configured year.

        Args:
            league_id: Optional league ID to filter files

        Returns:
            List of ESPN league dictionaries
        """
        file_path = self.get_espn_league_file(league_id)
        logger.info(f"Loading ESPN league from: {file_path}")
        return load_json_data(str(file_path))

    def load_fangraphs_batters(self) -> List[Dict]:
        """
        Load FanGraphs batters data for the configured year.

        Returns:
            List of FanGraphs batter dictionaries
        """
        file_path = self.get_fangraphs_batters_file()
        logger.info(f"Loading FanGraphs batters from: {file_path}")
        return load_json_data(str(file_path))

    def load_fangraphs_pitchers(self) -> List[Dict]:
        """
        Load FanGraphs pitchers data for the configured year.

        Returns:
            List of FanGraphs pitcher dictionaries
        """
        file_path = self.get_fangraphs_pitchers_file()
        logger.info(f"Loading FanGraphs pitchers from: {file_path}")
        return load_json_data(str(file_path))

    def get_savant_batters_file(self) -> Path:
        """
        Get the most recent Savant batters file (year-indifferent).

        Returns:
            Path to the Savant batters file

        Raises:
            FileNotFoundError: If no matching file is found
        """
        # Year-indifferent pattern - just find the latest file
        pattern = r"savant_batters_\d{4}_\d{2}_\d{2}_\d{4}\.json"

        file_path = self._find_latest_file(pattern)
        if not file_path:
            raise FileNotFoundError(
                f"No Savant batters file found in {self.resources_path}"
            )

        return file_path

    def get_savant_pitchers_file(self) -> Path:
        """
        Get the most recent Savant pitchers file (year-indifferent).

        Returns:
            Path to the Savant pitchers file

        Raises:
            FileNotFoundError: If no matching file is found
        """
        # Year-indifferent pattern - just find the latest file
        pattern = r"savant_pitchers_\d{4}_\d{2}_\d{2}_\d{4}\.json"

        file_path = self._find_latest_file(pattern)
        if not file_path:
            raise FileNotFoundError(
                f"No Savant pitchers file found in {self.resources_path}"
            )

        return file_path

    def load_savant_batters(self) -> List[Dict]:
        """
        Load Savant batters data for the configured year.

        Returns:
            List of Savant batter dictionaries
        """
        file_path = self.get_savant_batters_file()
        logger.info(f"Loading Savant batters from: {file_path}")
        data = load_json_data(str(file_path))
        season = self._extract_savant_season_from_filename(file_path.name)
        return self._annotate_savant_rows(data, "batter", season)

    def load_savant_pitchers(self) -> List[Dict]:
        """
        Load Savant pitchers data for the configured year.

        Returns:
            List of Savant pitcher dictionaries
        """
        file_path = self.get_savant_pitchers_file()
        logger.info(f"Loading Savant pitchers from: {file_path}")
        data = load_json_data(str(file_path))
        season = self._extract_savant_season_from_filename(file_path.name)
        return self._annotate_savant_rows(data, "pitcher", season)
