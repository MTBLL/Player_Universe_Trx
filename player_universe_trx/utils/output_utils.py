import json
import logging
import os
from typing import Dict, List, Tuple

from player_universe_trx.models.mtbl import MtblPlayerModel

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("player_universe_trx.utils")


def save_results(
    matched: List[MtblPlayerModel],
    unmatched: List[MtblPlayerModel],
    multiple_matches: List[Tuple[MtblPlayerModel, List[MtblPlayerModel]]],
    output_dir: str,
):
    """
    Save processing results to output files.

    Args:
        matched: List of successfully matched player models
        unmatched: List of players that couldn't be matched
        multiple_matches: List of players with multiple potential matches
        output_dir: Directory to save output files
    """
    os.makedirs(output_dir, exist_ok=True)

    # Save matched players
    matched_file = os.path.join(output_dir, "matched_players.json")
    with open(matched_file, "w") as f:
        json.dump([p.model_dump() for p in matched], f, indent=2)
    logger.info(f"Saved {len(matched)} matched players to {matched_file}")

    # Save unmatched players
    unmatched_file = os.path.join(output_dir, "unmatched_players.json")
    with open(unmatched_file, "w") as f:
        json.dump([p.model_dump() for p in unmatched], f, indent=2)
    logger.info(f"Saved {len(unmatched)} unmatched players to {unmatched_file}")

    # Save players with multiple matches for manual review
    ambiguous_data = []
    for player, candidates in multiple_matches:
        # Serialize candidates (they are Pydantic models)
        serialized_candidates = [c.model_dump() for c in candidates]
        ambiguous_data.append({"player": player.model_dump(), "candidates": serialized_candidates})

    ambiguous_file = os.path.join(output_dir, "ambiguous_matches.json")
    with open(ambiguous_file, "w") as f:
        json.dump(ambiguous_data, f, indent=2)
    logger.info(f"Saved {len(multiple_matches)} ambiguous matches to {ambiguous_file}")
