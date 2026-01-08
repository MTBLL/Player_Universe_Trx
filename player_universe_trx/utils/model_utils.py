import logging
from typing import Dict, List

from typing_extensions import Sequence

from player_universe_trx.models.espn import EspnBatterModel, EspnPitcherModel
from player_universe_trx.models.fangraphs import (
    FangraphsBatterModel,
    FangraphsPitcherModel,
)
from player_universe_trx.models.savant import (
    SavantBatterModel,
    SavantPitcherModel,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("player_universe_trx.utils")


def create_espn_batter_models(batter_data: List[Dict]) -> Sequence[EspnBatterModel]:
    """
    Create EspnBatterModel instances from raw ESPN batter data.

    Args:
        batter_data: Raw ESPN batter data from JSON

    Returns:
        Sequence of validated EspnBatterModel instances
    """
    valid_batters = []
    skipped_count = 0

    for batter in batter_data:
        try:
            model = EspnBatterModel.model_validate(batter)
            valid_batters.append(model)
        except Exception as e:
            logger.debug(f"Skipped batter {batter.get('name', 'unknown')}: {e}")
            skipped_count += 1

    logger.info(
        f"Created {len(valid_batters)} ESPN batter models, skipped {skipped_count} invalid records"
    )
    return valid_batters


def create_espn_pitcher_models(pitcher_data: List[Dict]) -> Sequence[EspnPitcherModel]:
    """
    Create EspnPitcherModel instances from raw ESPN pitcher data.

    Args:
        pitcher_data: Raw ESPN pitcher data from JSON

    Returns:
        Sequence of validated EspnPitcherModel instances
    """
    valid_pitchers = []
    skipped_count = 0

    for pitcher in pitcher_data:
        try:
            model = EspnPitcherModel.model_validate(pitcher)
            valid_pitchers.append(model)
        except Exception as e:
            logger.debug(f"Skipped pitcher {pitcher.get('name', 'unknown')}: {e}")
            skipped_count += 1

    logger.info(
        f"Created {len(valid_pitchers)} ESPN pitcher models, skipped {skipped_count} invalid records"
    )
    return valid_pitchers


def create_fangraphs_batter_models(
    batter_data: List[Dict],
) -> Sequence[FangraphsBatterModel]:
    """
    Create FangraphsBatterModel instances from raw FanGraphs batter data.

    Args:
        batter_data: Raw FanGraphs batter data from JSON

    Returns:
        Sequence of validated FangraphsBatterModel instances
    """
    valid_batters = []
    skipped_count = 0

    for batter in batter_data:
        try:
            model = FangraphsBatterModel.model_validate(batter)
            valid_batters.append(model)
        except Exception as e:
            logger.debug(f"Skipped batter {batter.get('name', 'unknown')}: {e}")
            skipped_count += 1

    logger.info(
        f"Created {len(valid_batters)} FanGraphs batter models, skipped {skipped_count} invalid records"
    )
    return valid_batters


def create_fangraphs_pitcher_models(
    pitcher_data: List[Dict],
) -> Sequence[FangraphsPitcherModel]:
    """
    Create FangraphsPitcherModel instances from raw FanGraphs pitcher data.

    Args:
        pitcher_data: Raw FanGraphs pitcher data from JSON

    Returns:
        Sequence of validated FangraphsPitcherModel instances
    """
    valid_pitchers = []
    skipped_count = 0

    for pitcher in pitcher_data:
        try:
            model = FangraphsPitcherModel.model_validate(pitcher)
            valid_pitchers.append(model)
        except Exception as e:
            logger.debug(f"Skipped pitcher {pitcher.get('name', 'unknown')}: {e}")
            skipped_count += 1

    logger.info(
        f"Created {len(valid_pitchers)} FanGraphs pitcher models, skipped {skipped_count} invalid records"
    )
    return valid_pitchers


def create_savant_batter_models(batter_data: List[Dict]) -> Sequence[SavantBatterModel]:
    """
    Create SavantBatterModel instances from raw Savant batter data.

    Transforms flat Savant data structure into nested model with stats object.
    Separates player identity/pitch count fields from statistical fields.

    Args:
        batter_data: Raw Savant batter data from JSON (flat structure)

    Returns:
        Sequence of validated SavantBatterModel instances (nested structure)
    """
    valid_batters = []
    skipped_count = 0

    # Identity and pitch count fields that stay at root level
    identity_fields = {
        "player_id",
        "name",
        "first_name",
        "last_name",
        "name_ascii",
        "slug",
    }
    pitch_count_fields = {"pitches", "total_pitches", "pitch_percent"}
    root_fields = identity_fields | pitch_count_fields

    for batter in batter_data:
        try:
            # Separate root-level fields from stats fields
            player_data = {k: v for k, v in batter.items() if k in root_fields}
            stats_data = {k: v for k, v in batter.items() if k not in root_fields}

            # Create nested structure
            nested_data = {**player_data, "stats": stats_data if stats_data else None}

            # Validate with Pydantic
            model = SavantBatterModel.model_validate(nested_data)
            valid_batters.append(model)
        except Exception as e:
            logger.debug(f"Skipped batter {batter.get('name', 'unknown')}: {e}")
            skipped_count += 1

    logger.info(
        f"Created {len(valid_batters)} Savant batter models, skipped {skipped_count} invalid records"
    )
    return valid_batters


def create_savant_pitcher_models(
    pitcher_data: List[Dict],
) -> Sequence[SavantPitcherModel]:
    """
    Create SavantPitcherModel instances from raw Savant pitcher data.

    Transforms flat Savant data structure into nested model with stats object.
    Separates player identity/pitch count fields from statistical fields.

    Args:
        pitcher_data: Raw Savant pitcher data from JSON (flat structure)

    Returns:
        Sequence of validated SavantPitcherModel instances (nested structure)
    """
    valid_pitchers = []
    skipped_count = 0

    # Identity and pitch count fields that stay at root level
    identity_fields = {
        "player_id",
        "name",
        "first_name",
        "last_name",
        "name_ascii",
        "slug",
    }
    pitch_count_fields = {"pitches", "total_pitches", "pitch_percent"}
    root_fields = identity_fields | pitch_count_fields

    for pitcher in pitcher_data:
        try:
            # Separate root-level fields from stats fields
            player_data = {k: v for k, v in pitcher.items() if k in root_fields}
            stats_data = {k: v for k, v in pitcher.items() if k not in root_fields}

            # Create nested structure
            nested_data = {**player_data, "stats": stats_data if stats_data else None}

            # Validate with Pydantic
            model = SavantPitcherModel.model_validate(nested_data)
            valid_pitchers.append(model)
        except Exception as e:
            logger.debug(f"Skipped pitcher {pitcher.get('name', 'unknown')}: {e}")
            skipped_count += 1

    logger.info(
        f"Created {len(valid_pitchers)} Savant pitcher models, skipped {skipped_count} invalid records"
    )
    return valid_pitchers
