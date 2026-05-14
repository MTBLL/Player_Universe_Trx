import logging
from typing import Any, Dict, List, Optional

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

# Pure player/team identity + loader-added consolidation metadata carried by
# sub-domain wire rows. These are redundant inside a stat sub-object — the
# parent MtblPlayerModel already carries identity — so they're stripped at the
# sub-domain indexing boundary to keep them from leaking through the models'
# extra="allow" config into the serialized output. Note: `year` and `team_id`
# are deliberately NOT here — some sub-domain models (home_runs,
# expected_statistics, swing_take) declare them as real stat-context fields.
_SAVANT_SUBDOMAIN_NOISE_FIELDS = _SAVANT_IDENTITY_FIELDS | {"team"}

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

        # Rows missing `opp_hand` are treated as the `all` split. This keeps
        # backwards-compatibility with legacy one-row-per-player extracts that
        # predate the per-handedness wire format — without this default, those
        # rows would be silently dropped and downstream Savant enrichment would
        # vanish for the whole input.
        raw_opp_hand = row.get("opp_hand")
        opp_hand_key = "all" if raw_opp_hand is None else raw_opp_hand
        slot = _OPP_HAND_TO_SLOT.get(opp_hand_key)
        if slot is None:
            logger.debug(
                f"Skipped Savant row with unknown opp_hand={raw_opp_hand!r} "
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


def _index_savant_subdomain(
    rows: Optional[List[Dict]],
    multi_value: bool = False,
) -> Dict[int, Any]:
    """Build a player_id → row (or list of rows) lookup from a sub-domain file.

    Each row is cleaned before storage:
      - NaN floats are scrubbed so the merged data validates cleanly downstream.
      - Identity / metadata noise (name, slug, player_id, team, ...) is dropped
        so it doesn't leak into the serialized stat sub-object via the models'
        extra="allow" config — the parent player record already carries
        identity. Genuine stat-context fields (`year`, `team_id`) survive.

    Rows without a player_id are dropped with a debug log.

    Args:
        rows: Raw rows from one of the sub-domain JSON files (already
            annotated with player_type/season by the loader).
        multi_value: When True, accumulate a list of rows per player_id
            (pitch_arsenal's pitch_type-keyed multi-row shape). When False,
            keep a single dict per player_id (every other sub-domain).
    """
    out: Dict[int, Any] = {}
    if not rows:
        return out
    for row in rows:
        pid = row.get("player_id")
        if pid is None:
            logger.debug(
                f"Skipped Savant sub-domain row with no player_id: {row.get('name')}"
            )
            continue
        # player_id is captured above for the lookup key; strip it (and the
        # rest of the identity/metadata noise) from the stored stat dict.
        cleaned = {
            k: v
            for k, v in _scrub_nan(row).items()
            if k not in _SAVANT_SUBDOMAIN_NOISE_FIELDS
        }
        if multi_value:
            out.setdefault(pid, []).append(cleaned)
        else:
            out[pid] = cleaned
    return out


def _attach_savant_subdomains(
    entry: Dict[str, Any],
    pid: int,
    *,
    statcast_idx: Dict[int, Any],
    home_runs_idx: Dict[int, Any],
    pitch_arsenal_idx: Dict[int, Any],
    swing_take_idx: Dict[int, Any],
    sprint_speed_idx: Optional[Dict[int, Any]] = None,
    expected_stats_idx: Optional[Dict[int, Any]] = None,
) -> None:
    """In-place: attach sub-domain dicts onto a per-player entry by player_id.

    The entry's keys map 1:1 to the SavantBatterModel/SavantPitcherModel
    fields. Each sub-domain key is only set if upstream has a row for this
    player — missing data leaves the field absent (None) on the model.

    `statcast` / `home_runs` / `pitch_arsenal` / `swing_take` are shared
    across both roles; `sprint_speed` (batter) and `expected_stats` (pitcher)
    are role-only and stay None when their index isn't supplied.
    """
    if pid in statcast_idx:
        entry["statcast"] = statcast_idx[pid]
    if pid in home_runs_idx:
        entry["home_runs"] = home_runs_idx[pid]
    if pid in pitch_arsenal_idx:
        entry["pitch_arsenal"] = pitch_arsenal_idx[pid]
    if pid in swing_take_idx:
        entry["swing_take"] = swing_take_idx[pid]
    if sprint_speed_idx is not None and pid in sprint_speed_idx:
        entry["sprint_speed"] = sprint_speed_idx[pid]
    if expected_stats_idx is not None and pid in expected_stats_idx:
        entry["expected_statistics"] = expected_stats_idx[pid]


def create_savant_batter_models(
    batter_data: List[Dict],
    *,
    statcast_data: Optional[List[Dict]] = None,
    home_runs_data: Optional[List[Dict]] = None,
    pitch_arsenal_data: Optional[List[Dict]] = None,
    sprint_speed_data: Optional[List[Dict]] = None,
    swing_take_data: Optional[List[Dict]] = None,
) -> Sequence[SavantBatterModel]:
    """Consolidate Savant batter rows + sub-domain files into one model per player.

    The Savant extractor emits one row per (player_id, opp_hand) for the
    swing/take base file, plus separate flat-or-multi-row files for each
    sub-domain (statcast / home_runs / pitch_arsenal / sprint_speed /
    swing_take). This function groups by player_id, routes each opp_hand row
    into all/vs_r/vs_l, and merges in matching rows from each sub-domain file
    (when supplied).

    Sub-domain kwargs all default to None — callers that only want the base
    swing/take splits don't need to thread the additional sources through.

    Args:
        batter_data: Swing/take rows (one per opp_hand split).
        statcast_data: Optional rows from savant_statcast_batter_*.json
        home_runs_data: Optional rows from savant_home_runs_batter_*.json
        pitch_arsenal_data: Optional multi-row arsenal data, keyed by pitch_type
        sprint_speed_data: Optional rows from savant_sprint_speed_*.json
        swing_take_data: Optional rows from savant_swing_take_batter_*.json

    Returns:
        Sequence of validated SavantBatterModel instances.
    """
    statcast_idx = _index_savant_subdomain(statcast_data)
    home_runs_idx = _index_savant_subdomain(home_runs_data)
    pitch_arsenal_idx = _index_savant_subdomain(pitch_arsenal_data, multi_value=True)
    sprint_speed_idx = _index_savant_subdomain(sprint_speed_data)
    swing_take_idx = _index_savant_subdomain(swing_take_data)

    valid_batters: List[SavantBatterModel] = []
    skipped_count = 0
    consolidated = _consolidate_savant_rows(batter_data)

    for pid, entry in consolidated.items():
        _attach_savant_subdomains(
            entry,
            pid,
            statcast_idx=statcast_idx,
            home_runs_idx=home_runs_idx,
            pitch_arsenal_idx=pitch_arsenal_idx,
            swing_take_idx=swing_take_idx,
            sprint_speed_idx=sprint_speed_idx,
        )
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
    *,
    statcast_data: Optional[List[Dict]] = None,
    home_runs_data: Optional[List[Dict]] = None,
    pitch_arsenal_data: Optional[List[Dict]] = None,
    expected_statistics_data: Optional[List[Dict]] = None,
    swing_take_data: Optional[List[Dict]] = None,
) -> Sequence[SavantPitcherModel]:
    """Pitcher counterpart of create_savant_batter_models.

    Mirrors the batter signature except `sprint_speed_data` (batter-only)
    is replaced by `expected_statistics_data` (pitcher-only). `swing_take_data`
    is shared — both roles get a swing_take run-value-by-region file.
    """
    statcast_idx = _index_savant_subdomain(statcast_data)
    home_runs_idx = _index_savant_subdomain(home_runs_data)
    pitch_arsenal_idx = _index_savant_subdomain(pitch_arsenal_data, multi_value=True)
    expected_stats_idx = _index_savant_subdomain(expected_statistics_data)
    swing_take_idx = _index_savant_subdomain(swing_take_data)

    valid_pitchers: List[SavantPitcherModel] = []
    skipped_count = 0
    consolidated = _consolidate_savant_rows(pitcher_data)

    for pid, entry in consolidated.items():
        _attach_savant_subdomains(
            entry,
            pid,
            statcast_idx=statcast_idx,
            home_runs_idx=home_runs_idx,
            pitch_arsenal_idx=pitch_arsenal_idx,
            swing_take_idx=swing_take_idx,
            expected_stats_idx=expected_stats_idx,
        )
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
