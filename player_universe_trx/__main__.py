import logging
from typing import Dict, Optional

from player_universe_trx.loaders import DataLoader
from player_universe_trx.matchers.player_matcher import (
    match_player_models_on_fangraphs_data,
)
from player_universe_trx.utils.model_utils import create_espn_batter_models
from player_universe_trx.utils.output_utils import save_results

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("player_universe_trx")


def main(
    resources_path: Optional[str] = None,
    year: Optional[int] = None,
    output_dir: Optional[str] = None,
) -> Dict:
    """
    Main entry point for the player universe transformation pipeline.

    Args:
        resources_path: Path to directory containing input files (defaults to DataLoader.DEFAULT_RESOURCES_PATH)
        year: Year for data files (defaults to current year)
        output_dir: Directory to save output files (defaults to './output')

    Returns:
        Dictionary with counts of matched, unmatched, and ambiguous players
    """
    output_dir = output_dir or "./output"

    logger.info("Starting player universe transformation")

    # Initialize data loader
    loader = DataLoader(resources_path=resources_path, year=year)

    # Load ESPN batter data
    logger.info("Loading ESPN batter data...")
    espn_batter_data = loader.load_espn_batters()

    # Create ESPN batter models
    logger.info("Creating ESPN batter models...")
    espn_batter_models = create_espn_batter_models(espn_batter_data)

    # Load FanGraphs player data
    logger.info("Loading FanGraphs player data...")
    fangraphs_data = loader.load_fangraphs_batters()

    # Match players
    logger.info("Matching players between ESPN and FanGraphs data...")
    result = match_player_models_on_fangraphs_data(espn_batter_models, fangraphs_data)

    matched_players = result["matched"]
    unmatched_players = result["no_matches"]
    multiple_matches = result["multiple_matches"]

    logger.info("Matching complete:")
    logger.info(f"  - {len(matched_players)} players matched successfully")
    logger.info(f"  - {len(unmatched_players)} players couldn't be matched")
    logger.info(f"  - {len(multiple_matches)} players have multiple potential matches")

    # Save results
    logger.info("Saving results...")
    save_results(matched_players, unmatched_players, multiple_matches, output_dir)

    logger.info("Player universe transformation complete")
    return {
        "matched": len(matched_players),
        "unmatched": len(unmatched_players),
        "ambiguous": len(multiple_matches),
    }


if __name__ == "__main__":
    # Default to 2025 for now since that's the latest data we have
    main(year=2025)
