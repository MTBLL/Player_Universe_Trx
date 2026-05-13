import logging
from typing import Any, Dict, List

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


# Identity fields that stay constant across all (player_id, opp_hand) rows for
# the same player; pulled from the row chosen as identity source during
# consolidation.
_SAVANT_IDENTITY_FIELDS = {
    "player_id",
    "name",
    "first_name",
    "last_name",
    "name_ascii",
    "slug",
    "player_type",
    "season",
}

# Maps Savant's opp_hand wire value to the model field name. The extractor
# emits one row per opp_hand per player.
_OPP_HAND_TO_SLOT = {"all": "all", "R": "vs_r", "L": "vs_l"}


def _scrub_nan(d: Dict[str, Any]) -> Dict[str, Any]:
    """Replace NaN floats with None.

    Upstream Savant rows occasionally surface pandas NaN values for stats like
    BBdist or barrels_total when the sample is too thin to compute them.
    json.load deserializes those as Python float('nan'), which pydantic then
    rejects (finite_number). Treating them as missing is the right semantic.
    """
    out: Dict[str, Any] = {}
    for k, v in d.items():
        if isinstance(v, float) and v != v:  # NaN is the only x where x != x
            continue
        out[k] = v
    return out


def _consolidate_savant_rows(
    rows: List[Dict],
) -> Dict[int, Dict[str, Any]]:
    """Group flat Savant rows by player_id and assemble per-split slots.

    Returns a dict keyed by player_id whose value is a partially-built model
    dict: identity fields at the root plus `all` / `vs_r` / `vs_l` stats dicts
    sourced from each row's opp_hand value. Unrecognized opp_hand values are
    skipped with a debug log (defensive — the extractor's contract is fixed
    at all/R/L).
    """
    by_player: Dict[int, Dict[str, Any]] = {}

    for row in rows:
        pid = row.get("player_id")
        if pid is None:
            logger.debug(f"Skipped Savant row with no player_id: {row.get('name')}")
            continue

        slot = _OPP_HAND_TO_SLOT.get(row.get("opp_hand", ""))
        if slot is None:
            logger.debug(
                f"Skipped Savant row with unknown opp_hand={row.get('opp_hand')!r} "
                f"for player_id={pid}"
            )
            continue

        # Partition: identity stays at root, everything else (minus opp_hand,
        # which is metadata, not a stat) goes into the per-split stats dict.
        # Pitch counts (pitches/total_pitches/pitch_percent) intentionally fall
        # into the stats dict because they're per-split.
        identity = {k: v for k, v in row.items() if k in _SAVANT_IDENTITY_FIELDS}
        stats = _scrub_nan(
            {
                k: v
                for k, v in row.items()
                if k not in _SAVANT_IDENTITY_FIELDS and k != "opp_hand"
            }
        )

        entry = by_player.setdefault(pid, {})
        # Identity merges via "first-wins" — every row for the same player
        # carries the same identity values, so the order doesn't matter.
        for k, v in identity.items():
            entry.setdefault(k, v)
        entry[slot] = stats

    return by_player


def create_savant_batter_models(batter_data: List[Dict]) -> Sequence[SavantBatterModel]:
    """Consolidate flat Savant batter rows into one model per player.

    The Savant extractor emits one row per (player_id, opp_hand) tuple. This
    function groups by player_id and routes each row into the matching
    `all` / `vs_r` / `vs_l` slot on SavantBatterModel.

    Args:
        batter_data: Raw Savant batter rows from JSON (one row per split)

    Returns:
        Sequence of validated SavantBatterModel instances (one per unique
        player_id, with up to three split sub-objects populated).
    """
    valid_batters: List[SavantBatterModel] = []
    skipped_count = 0
    consolidated = _consolidate_savant_rows(batter_data)

    for pid, entry in consolidated.items():
        try:
            valid_batters.append(SavantBatterModel.model_validate(entry))
        except Exception as e:
            logger.debug(f"Skipped batter player_id={pid}: {e}")
            skipped_count += 1

    logger.info(
        f"Created {len(valid_batters)} Savant batter models from {len(batter_data)} "
        f"wire rows ({len(consolidated)} unique player_ids); "
        f"skipped {skipped_count} invalid records"
    )
    return valid_batters


def create_savant_pitcher_models(
    pitcher_data: List[Dict],
) -> Sequence[SavantPitcherModel]:
    """Consolidate flat Savant pitcher rows into one model per player.

    Same pattern as create_savant_batter_models — see that function's docstring
    for the row-grouping contract.

    Args:
        pitcher_data: Raw Savant pitcher rows from JSON (one row per split)

    Returns:
        Sequence of validated SavantPitcherModel instances (one per unique
        player_id, with up to three split sub-objects populated).
    """
    valid_pitchers: List[SavantPitcherModel] = []
    skipped_count = 0
    consolidated = _consolidate_savant_rows(pitcher_data)

    for pid, entry in consolidated.items():
        try:
            valid_pitchers.append(SavantPitcherModel.model_validate(entry))
        except Exception as e:
            logger.debug(f"Skipped pitcher player_id={pid}: {e}")
            skipped_count += 1

    logger.info(
        f"Created {len(valid_pitchers)} Savant pitcher models from {len(pitcher_data)} "
        f"wire rows ({len(consolidated)} unique player_ids); "
        f"skipped {skipped_count} invalid records"
    )
    return valid_pitchers
