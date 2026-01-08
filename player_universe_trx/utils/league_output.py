"""Output utilities for league transformation results."""

import json
import logging
from pathlib import Path
from typing import List, Optional

from player_universe_trx.models.mtbl import (
    MtblLeagueModel,
    MtblScheduleModel,
    MtblTeamRosterModel,
)

logger = logging.getLogger(__name__)


def save_team_roster(team_roster: MtblTeamRosterModel, output_dir: str) -> Path:
    """
    Save a team roster to a JSON file.

    Args:
        team_roster: MTBL team roster model
        output_dir: Directory to save the file

    Returns:
        Path to the saved file
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filename = f"team_{team_roster.team_id}_roster.json"
    file_path = output_path / filename

    # Convert to dict and save as JSON
    data = team_roster.model_dump(exclude_none=True)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info(f"Saved team {team_roster.team_id} roster to {file_path}")
    return file_path


def save_all_team_rosters(
    team_rosters: List[MtblTeamRosterModel], output_dir: str
) -> List[Path]:
    """
    Save all team rosters to individual JSON files.

    Args:
        team_rosters: List of MTBL team roster models
        output_dir: Directory to save the files

    Returns:
        List of paths to saved files
    """
    saved_files = []
    for team_roster in team_rosters:
        file_path = save_team_roster(team_roster, output_dir)
        saved_files.append(file_path)

    logger.info(f"Saved {len(saved_files)} team roster files to {output_dir}")
    return saved_files


def save_league_summary(league_summary: MtblLeagueModel, output_dir: str) -> Path:
    """
    Save league summary to a JSON file.

    Args:
        league_summary: MTBL league summary model
        output_dir: Directory to save the file

    Returns:
        Path to the saved file
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filename = f"league_{league_summary.league_id}_summary.json"
    file_path = output_path / filename

    # Convert to dict and save as JSON
    data = league_summary.model_dump(exclude_none=True)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info(f"Saved league {league_summary.league_id} summary to {file_path}")
    return file_path


def save_schedule(schedule: MtblScheduleModel, output_dir: str) -> Path:
    """
    Save league schedule to a JSON file.

    Args:
        schedule: MTBL schedule model
        output_dir: Directory to save the file

    Returns:
        Path to the saved file
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filename = f"league_{schedule.league_id}_schedule.json"
    file_path = output_path / filename

    # Convert to dict and save as JSON
    data = schedule.model_dump(exclude_none=True)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info(f"Saved league {schedule.league_id} schedule to {file_path}")
    return file_path


def save_league_results(
    league_summary: MtblLeagueModel,
    team_rosters: List[MtblTeamRosterModel],
    output_dir: str,
    schedule: Optional[MtblScheduleModel] = None,
) -> dict:
    """
    Save all league transformation results.

    Args:
        league_summary: MTBL league summary model
        team_rosters: List of MTBL team roster models
        output_dir: Directory to save the files
        schedule: Optional MTBL schedule model

    Returns:
        Dictionary with file paths and summary info
    """
    # Save league summary
    league_file = save_league_summary(league_summary, output_dir)

    # Save all team rosters
    team_files = save_all_team_rosters(team_rosters, output_dir)

    # Save schedule if provided
    schedule_file = None
    if schedule:
        schedule_file = save_schedule(schedule, output_dir)

    logger.info(
        f"League transformation complete: "
        f"1 league summary, {len(team_files)} team rosters"
        f"{', 1 schedule' if schedule_file else ''} saved to {output_dir}"
    )

    result = {
        "league_file": str(league_file),
        "team_files": [str(f) for f in team_files],
        "num_teams": len(team_files),
    }
    if schedule_file:
        result["schedule_file"] = str(schedule_file)

    return result
