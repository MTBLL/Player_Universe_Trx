import json
import logging
import os
from typing import Dict, List, Tuple

from player_universe_trx.models.mtbl import (
    MtblBatterModel,
    MtblPitcherModel,
    MtblPlayerModel,
)

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
    Save processing results to output files split by batters and pitchers.

    Args:
        matched: List of successfully matched player models
        unmatched: List of players that couldn't be matched
        multiple_matches: List of players with multiple potential matches
        output_dir: Directory to save output files
    """
    os.makedirs(output_dir, exist_ok=True)

    batters_matched = [p for p in matched if isinstance(p, MtblBatterModel)]
    pitchers_matched = [p for p in matched if isinstance(p, MtblPitcherModel)]
    batters_unmatched = [p for p in unmatched if isinstance(p, MtblBatterModel)]
    pitchers_unmatched = [p for p in unmatched if isinstance(p, MtblPitcherModel)]

    # Save matched players
    batters_matched_file = os.path.join(output_dir, "batters_matched.json")
    with open(batters_matched_file, "w") as f:
        json.dump([p.model_dump() for p in batters_matched], f, indent=2)
    logger.info(
        "Saved %s matched batters to %s",
        len(batters_matched),
        batters_matched_file,
    )

    pitchers_matched_file = os.path.join(output_dir, "pitchers_matched.json")
    with open(pitchers_matched_file, "w") as f:
        json.dump([p.model_dump() for p in pitchers_matched], f, indent=2)
    logger.info(
        "Saved %s matched pitchers to %s",
        len(pitchers_matched),
        pitchers_matched_file,
    )

    # Save unmatched players
    batters_unmatched_file = os.path.join(output_dir, "batters_unmatched.json")
    with open(batters_unmatched_file, "w") as f:
        json.dump([p.model_dump() for p in batters_unmatched], f, indent=2)
    logger.info(
        "Saved %s unmatched batters to %s",
        len(batters_unmatched),
        batters_unmatched_file,
    )

    pitchers_unmatched_file = os.path.join(output_dir, "pitchers_unmatched.json")
    with open(pitchers_unmatched_file, "w") as f:
        json.dump([p.model_dump() for p in pitchers_unmatched], f, indent=2)
    logger.info(
        "Saved %s unmatched pitchers to %s",
        len(pitchers_unmatched),
        pitchers_unmatched_file,
    )

    # Save players with multiple matches for manual review
    batters_ambiguous = []
    pitchers_ambiguous = []
    for player, candidates in multiple_matches:
        serialized_candidates = [c.model_dump() for c in candidates]
        payload = {"player": player.model_dump(), "candidates": serialized_candidates}
        if isinstance(player, MtblBatterModel):
            batters_ambiguous.append(payload)
        elif isinstance(player, MtblPitcherModel):
            pitchers_ambiguous.append(payload)

    batters_ambiguous_file = os.path.join(output_dir, "batters_ambiguous.json")
    with open(batters_ambiguous_file, "w") as f:
        json.dump(batters_ambiguous, f, indent=2)
    logger.info(
        "Saved %s ambiguous batters to %s",
        len(batters_ambiguous),
        batters_ambiguous_file,
    )

    pitchers_ambiguous_file = os.path.join(output_dir, "pitchers_ambiguous.json")
    with open(pitchers_ambiguous_file, "w") as f:
        json.dump(pitchers_ambiguous, f, indent=2)
    logger.info(
        "Saved %s ambiguous pitchers to %s",
        len(pitchers_ambiguous),
        pitchers_ambiguous_file,
    )
