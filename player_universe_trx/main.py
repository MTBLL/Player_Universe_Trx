import os
import logging
from typing import Dict, Optional

from player_universe_trx.matchers.player_matcher import match_player_models_on_fangraphs_data
from player_universe_trx.utils.file_utils import load_json_data
from player_universe_trx.utils.model_utils import create_player_models
from player_universe_trx.utils.output_utils import save_results

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("player_universe_trx")

# Configuration
RESOURCES_PATH = "/Users/Shared/BaseballHQ/resources/extract"
ESPN_PLAYERS = "espn_player_universe.json"
FANGRAPHS_PLAYERS = "fangraph_players.json"


def main(
    espn_file: Optional[str] = None,
    fangraphs_file: Optional[str] = None,
    output_dir: Optional[str] = None
) -> Dict:
    """
    Main entry point for the player universe transformation pipeline.
    
    Args:
        espn_file: Path to ESPN player data (defaults to RESOURCES_PATH/ESPN_PLAYERS)
        fangraphs_file: Path to FanGraphs player data (defaults to RESOURCES_PATH/FANGRAPHS_PLAYERS)
        output_dir: Directory to save output files (defaults to './output')
        
    Returns:
        Dictionary with counts of matched, unmatched, and ambiguous players
    """
    # Set default file paths if not provided
    espn_file = espn_file or os.path.join(RESOURCES_PATH, ESPN_PLAYERS)
    fangraphs_file = fangraphs_file or os.path.join(RESOURCES_PATH, FANGRAPHS_PLAYERS)
    output_dir = output_dir or "./output"
    
    logger.info("Starting player universe transformation")
    logger.info(f"ESPN data: {espn_file}")
    logger.info(f"FanGraphs data: {fangraphs_file}")
    
    # Load ESPN player data
    logger.info("Loading ESPN player data...")
    espn_data = load_json_data(espn_file)
    
    # Create player models from ESPN data
    logger.info("Creating player models from ESPN data...")
    player_models = create_player_models(espn_data)
    
    # Load FanGraphs player data
    logger.info("Loading FanGraphs player data...")
    fangraphs_data = load_json_data(fangraphs_file)
    
    # Match players
    logger.info("Matching players between ESPN and FanGraphs data...")
    result = match_player_models_on_fangraphs_data(player_models, fangraphs_data)
    
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
        "ambiguous": len(multiple_matches)
    }


if __name__ == "__main__":
    main()