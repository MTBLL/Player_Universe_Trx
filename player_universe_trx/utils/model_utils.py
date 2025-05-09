import logging
from typing import Dict, List

from player_universe_trx.models.player import PlayerModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("player_universe_trx.utils")


def create_player_models(player_data: List[Dict]) -> List[PlayerModel]:
    """
    Create PlayerModel instances from raw player data.
    
    Args:
        player_data: Raw player data from JSON
        
    Returns:
        List of validated PlayerModel instances (retired players are filtered out)
    """
    valid_players = []
    skipped_count = 0
    
    for player in player_data:
        try:
            model = PlayerModel.model_validate(player)
            valid_players.append(model)
        except ValueError:
            # This is expected for retired players
            skipped_count += 1
    
    logger.info(f"Created {len(valid_players)} player models, skipped {skipped_count} invalid records")
    return valid_players