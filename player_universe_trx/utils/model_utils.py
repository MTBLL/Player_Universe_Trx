import logging
from typing import Dict, List

from player_universe_trx.models.espn import EspnBatterModel, EspnPitcherModel
from player_universe_trx.models.fangraphs import (
    FangraphsBatterModel,
    FangraphsPitcherModel,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("player_universe_trx.utils")


def create_espn_batter_models(batter_data: List[Dict]) -> List[EspnBatterModel]:
    """
    Create EspnBatterModel instances from raw ESPN batter data.

    Args:
        batter_data: Raw ESPN batter data from JSON

    Returns:
        List of validated EspnBatterModel instances
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

    logger.info(f"Created {len(valid_batters)} ESPN batter models, skipped {skipped_count} invalid records")
    return valid_batters


def create_espn_pitcher_models(pitcher_data: List[Dict]) -> List[EspnPitcherModel]:
    """
    Create EspnPitcherModel instances from raw ESPN pitcher data.

    Args:
        pitcher_data: Raw ESPN pitcher data from JSON

    Returns:
        List of validated EspnPitcherModel instances
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

    logger.info(f"Created {len(valid_pitchers)} ESPN pitcher models, skipped {skipped_count} invalid records")
    return valid_pitchers


def create_fangraphs_batter_models(batter_data: List[Dict]) -> List[FangraphsBatterModel]:
    """
    Create FangraphsBatterModel instances from raw FanGraphs batter data.

    Args:
        batter_data: Raw FanGraphs batter data from JSON

    Returns:
        List of validated FangraphsBatterModel instances
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

    logger.info(f"Created {len(valid_batters)} FanGraphs batter models, skipped {skipped_count} invalid records")
    return valid_batters


def create_fangraphs_pitcher_models(pitcher_data: List[Dict]) -> List[FangraphsPitcherModel]:
    """
    Create FangraphsPitcherModel instances from raw FanGraphs pitcher data.

    Args:
        pitcher_data: Raw FanGraphs pitcher data from JSON

    Returns:
        List of validated FangraphsPitcherModel instances
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

    logger.info(f"Created {len(valid_pitchers)} FanGraphs pitcher models, skipped {skipped_count} invalid records")
    return valid_pitchers