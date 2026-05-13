from typing import Any, Dict, List, Optional, Sequence, Tuple

from typing_extensions import TYPE_CHECKING

from player_universe_trx.matchers.models import MatchConfidence, PlayerMatchResult
from player_universe_trx.models.espn import (
    EspnBatterModel,
    EspnBatterStatsGroupModel,
    EspnPitcherStatsGroupModel,
)
from player_universe_trx.models.fangraphs import (
    FangraphsBatterModel,
    FangraphsPitcherModel,
    FangraphsPlayerModel,
)
from player_universe_trx.models.fangraphs.stats import (
    FangraphsBatterStatsModel,
    FangraphsPitcherStatsModel,
)
from player_universe_trx.models.mtbl import (
    MtblBatterModel,
    MtblBatterSeasonStatsModel,
    MtblBatterStatsModel,
    MtblPitcherModel,
    MtblPitcherSeasonStatsModel,
    MtblPitcherStatsModel,
    MtblPlayerModel,
)
from player_universe_trx.models.savant import SavantBatterModel, SavantPitcherModel
from player_universe_trx.models.savant.stats import (
    SavantBatterStatsModel,
    SavantPitcherStatsModel,
)

if TYPE_CHECKING:  # pragma: no cover
    from player_universe_trx.models.espn import (
        EspnBatterModel,
        EspnPitcherModel,
    )
    from player_universe_trx.models.fangraphs import (
        FangraphsBatterModel,
        FangraphsPitcherModel,
    )
    from player_universe_trx.models.savant import SavantBatterModel, SavantPitcherModel


def _extract_espn_current_season_stats(
    espn_player: "EspnBatterModel | EspnPitcherModel",
) -> Dict[str, Any]:
    """Extract ESPN current season stats as unprefixed dictionary.

    Args:
        espn_player: ESPN player model with stats container

    Returns:
        Dictionary of current season stats (unprefixed)
    """
    if espn_player.stats and espn_player.stats.current_season:
        return espn_player.stats.current_season.model_dump(exclude_none=True)
    return {}


_FANGRAPHS_PROJECTION_SLOTS: Tuple[str, ...] = ("projections", "projs_updated", "ros")


def _extract_fangraphs_projections(
    fg_match: Optional["FangraphsBatterModel | FangraphsPitcherModel"],
) -> Dict[str, Dict[str, Any]]:
    """Extract FanGraphs projection stats for all three upstream slots.

    Upstream emits three sibling slots per player — `projections` (preseason),
    `projs_updated` (in-season full-year refit), and `ros` (rest-of-season).
    Each slot is rendered as `{}` upstream when Fangraphs hasn't published the
    underlying endpoints yet, which round-trips here to a model whose
    model_dump(exclude_none=True) is `{}`. We propagate empty dicts unchanged
    so downstream consumers see the same stable shape.

    Returns:
        Dict keyed by slot name with the per-slot stats dict as value.
    """
    out: Dict[str, Dict[str, Any]] = {slot: {} for slot in _FANGRAPHS_PROJECTION_SLOTS}
    if not fg_match:
        return out

    for slot in _FANGRAPHS_PROJECTION_SLOTS:
        model = getattr(fg_match, slot, None)
        if model is None:
            continue
        out[slot] = model.model_dump(exclude_none=True)
    return out


_SAVANT_SPLIT_FIELDS: Tuple[str, ...] = ("vs_r", "vs_l")


def _extract_savant_stats(
    savant_match: Optional["SavantBatterModel | SavantPitcherModel"],
) -> Dict[str, Any]:
    """Extract Savant sabermetric stats for the `all` (overall) split.

    This feeds `MtblBatterSeasonStatsModel.current_season` / its pitcher
    counterpart — the overall-Savant-numbers-merged-into-the-current-season
    contract that downstream code already depends on. Per-handedness splits
    are routed separately via `_extract_savant_splits`.

    Args:
        savant_match: Savant player model with per-split stats

    Returns:
        Dictionary of Savant `all` split stats (unprefixed), or {} if absent.
    """
    if savant_match and savant_match.all:
        stats = savant_match.all.model_dump(exclude_none=True)
        stats["savant_player_id"] = savant_match.player_id
        stats["savant_player_type"] = savant_match.player_type
        if savant_match.season is not None:
            stats["savant_season"] = savant_match.season
        return stats
    return {}


def _extract_savant_splits(
    savant_match: Optional["SavantBatterModel | SavantPitcherModel"],
) -> Dict[str, Dict[str, Any]]:
    """Extract Savant per-handedness splits (vs_r, vs_l).

    The `all` split is handled by _extract_savant_stats — it flows into
    current_season. The other two splits are returned here so they can be
    routed into dedicated savant_vs_r / savant_vs_l fields on the MTBL
    stats container.

    Returns:
        Dict keyed by slot name ("vs_r" / "vs_l") with per-slot stats dict as
        value. Empty dict per slot when the player has no sample for that
        handedness.
    """
    out: Dict[str, Dict[str, Any]] = {slot: {} for slot in _SAVANT_SPLIT_FIELDS}
    if not savant_match:
        return out
    for slot in _SAVANT_SPLIT_FIELDS:
        model = getattr(savant_match, slot, None)
        if model is None:
            continue
        out[slot] = model.model_dump(exclude_none=True)
    return out


def _build_stats_dict(
    result: PlayerMatchResult,
    is_matched: bool,
) -> Dict[str, Any]:
    """Build combined current-season stats dictionary from all sources.

    Args:
        result: Player match result containing ESPN, FanGraphs, and Savant data
        is_matched: Whether player has FanGraphs/Savant matches

    Returns:
        Dictionary combining current-season stats from ESPN and Savant
    """
    stats_dict: Dict[str, Any] = {}

    # 1. ESPN current season stats (unprefixed)
    espn_current: Dict[str, Any] = _extract_espn_current_season_stats(
        result.espn_player
    )
    stats_dict.update(espn_current)

    if is_matched:
        # 2. Savant sabermetrics (unprefixed), keep ESPN values on collision
        savant_stats: Dict[str, Any] = _extract_savant_stats(result.savant_match)
        for key, value in savant_stats.items():
            if key not in stats_dict:
                stats_dict[key] = value

    return stats_dict


def _create_player_model(
    base_player: MtblPlayerModel,
    stats_dict: Dict[str, Any],
    projections_dict: Dict[str, Dict[str, Any]],
    savant_splits_dict: Dict[str, Dict[str, Any]],
    espn_stats_container: Optional[
        EspnBatterStatsGroupModel | EspnPitcherStatsGroupModel
    ],
    is_batter: bool,
) -> MtblPlayerModel:
    """Create typed player model (batter or pitcher) with stats.

    Args:
        base_player: Base MTBL player model
        stats_dict: Combined current season stats dictionary
        projections_dict: FanGraphs projections by slot — keys are
            "projections", "projs_updated", "ros"; each value is the per-slot
            stats dict (possibly empty).
        savant_splits_dict: Savant per-handedness splits — keys are
            "vs_r", "vs_l"; each value is the per-slot stats dict (possibly
            empty). The `all` split is already folded into stats_dict.
        espn_stats_container: ESPN stats container with all periods
        is_batter: True for batter, False for pitcher

    Returns:
        MtblBatterModel or MtblPitcherModel with merged stats
    """
    base_data: Dict[str, Any] = base_player.model_dump()

    # Pull per-slot dicts out for clarity; empty dicts mean "upstream had no data"
    # and we leave the corresponding field as None on the MTBL stats container.
    preseason = projections_dict.get("projections", {})
    updated = projections_dict.get("projs_updated", {})
    ros = projections_dict.get("ros", {})
    has_any_projection = bool(preseason or updated or ros)

    vs_r = savant_splits_dict.get("vs_r", {})
    vs_l = savant_splits_dict.get("vs_l", {})
    has_any_savant_split = bool(vs_r or vs_l)

    if is_batter:
        batter_stats: Optional[MtblBatterStatsModel] = None
        if (
            stats_dict
            or has_any_projection
            or has_any_savant_split
            or espn_stats_container
        ):
            # Type narrow the container for batters
            batter_container: Optional[EspnBatterStatsGroupModel] = (
                espn_stats_container
                if isinstance(espn_stats_container, EspnBatterStatsGroupModel)
                else None
            )
            batter_current_season: Optional[MtblBatterSeasonStatsModel] = (
                MtblBatterSeasonStatsModel(**stats_dict) if stats_dict else None
            )
            batter_stats = MtblBatterStatsModel(
                current_season=batter_current_season,
                projections=(
                    FangraphsBatterStatsModel(**preseason) if preseason else None
                ),
                projs_updated=(
                    FangraphsBatterStatsModel(**updated) if updated else None
                ),
                ros=(FangraphsBatterStatsModel(**ros) if ros else None),
                savant_vs_r=(SavantBatterStatsModel(**vs_r) if vs_r else None),
                savant_vs_l=(SavantBatterStatsModel(**vs_l) if vs_l else None),
                espn_stats=batter_container,
            )
        return MtblBatterModel(**base_data, stats=batter_stats)
    else:
        pitcher_stats: Optional[MtblPitcherStatsModel] = None
        if (
            stats_dict
            or has_any_projection
            or has_any_savant_split
            or espn_stats_container
        ):
            # Type narrow the container for pitchers
            pitcher_container: Optional[EspnPitcherStatsGroupModel] = (
                espn_stats_container
                if isinstance(espn_stats_container, EspnPitcherStatsGroupModel)
                else None
            )
            pitcher_current_season: Optional[MtblPitcherSeasonStatsModel] = (
                MtblPitcherSeasonStatsModel(**stats_dict) if stats_dict else None
            )
            pitcher_stats = MtblPitcherStatsModel(
                current_season=pitcher_current_season,
                projections=(
                    FangraphsPitcherStatsModel(**preseason) if preseason else None
                ),
                projs_updated=(
                    FangraphsPitcherStatsModel(**updated) if updated else None
                ),
                ros=(FangraphsPitcherStatsModel(**ros) if ros else None),
                savant_vs_r=(SavantPitcherStatsModel(**vs_r) if vs_r else None),
                savant_vs_l=(SavantPitcherStatsModel(**vs_l) if vs_l else None),
                espn_stats=pitcher_container,
            )
        return MtblPitcherModel(**base_data, stats=pitcher_stats)


def apply_matches(results: List[PlayerMatchResult]) -> Dict[str, List]:
    """
    Apply matches by merging FanGraphs and Savant data into ESPN players.

    This function takes the match results from PlayerMatcher.match_players()
    and performs the actual data merging into MtblBatterModel or MtblPitcherModel instances.

    Args:
        results: List of PlayerMatchResult objects from match_players()

    Returns:
        Dictionary with categorized results:
        - 'matched': List of MtblBatterModel/MtblPitcherModel instances with successful matches
        - 'ambiguous': List of (MtblPlayerModel, candidates) tuples for manual review
        - 'unmatched': List of MtblBatterModel/MtblPitcherModel instances with no matches
    """
    matched: List[MtblPlayerModel] = []
    ambiguous: List[Tuple[MtblPlayerModel, Sequence[FangraphsPlayerModel]]] = []
    unmatched: List[MtblPlayerModel] = []

    for result in results:
        # Skip retired players (they cannot be serialized to MtblPlayerModel)
        if result.espn_player.status == "retired":
            continue

        # Determine player type
        is_batter: bool = isinstance(result.espn_player, EspnBatterModel)

        # Convert ESPN player to base MtblPlayerModel
        espn_data: Dict[str, Any] = result.espn_player.model_dump(exclude_none=True)

        # Map ESPN fields to MTBL fields
        if "on_team_id" in espn_data:
            espn_data["fantasy_team"] = espn_data.pop("on_team_id")
        if "draft_auction_value" in espn_data:
            espn_data["draft_value"] = espn_data.pop("draft_auction_value")

        base_player: MtblPlayerModel = MtblPlayerModel.model_validate(espn_data)

        # Handle ambiguous matches
        if result.confidence == MatchConfidence.AMBIGUOUS:
            ambiguous_stats_dict = _build_stats_dict(result, is_matched=False)
            ambiguous_projections_dict: Dict[str, Dict[str, Any]] = {
                slot: {} for slot in _FANGRAPHS_PROJECTION_SLOTS
            }
            ambiguous_savant_splits_dict: Dict[str, Dict[str, Any]] = {
                slot: {} for slot in _SAVANT_SPLIT_FIELDS
            }
            ambiguous_espn_stats_container: Optional[Any] = (
                result.espn_player.stats if result.espn_player.stats else None
            )
            ambiguous_player: MtblPlayerModel = _create_player_model(
                base_player=base_player,
                stats_dict=ambiguous_stats_dict,
                projections_dict=ambiguous_projections_dict,
                savant_splits_dict=ambiguous_savant_splits_dict,
                espn_stats_container=ambiguous_espn_stats_container,
                is_batter=is_batter,
            )
            ambiguous.append((ambiguous_player, result.candidates))
            continue

        # Determine if this is a matched or unmatched player
        is_matched: bool = result.fangraphs_match is not None

        # Merge FanGraphs data if matched
        if is_matched:
            base_player.merge_fangraphs_data(result.fangraphs_match)

        # Build combined current-season stats dictionary
        stats_dict: Dict[str, Any] = _build_stats_dict(result, is_matched)

        projections_dict: Dict[str, Dict[str, Any]] = (
            _extract_fangraphs_projections(result.fangraphs_match)
            if is_matched
            else {slot: {} for slot in _FANGRAPHS_PROJECTION_SLOTS}
        )

        savant_splits_dict: Dict[str, Dict[str, Any]] = (
            _extract_savant_splits(result.savant_match)
            if is_matched
            else {slot: {} for slot in _SAVANT_SPLIT_FIELDS}
        )

        # Extract ESPN stats container
        espn_stats_container: Optional[Any] = (
            result.espn_player.stats if result.espn_player.stats else None
        )

        # Create typed player model
        player_model: MtblPlayerModel = _create_player_model(
            base_player=base_player,
            stats_dict=stats_dict,
            projections_dict=projections_dict,
            savant_splits_dict=savant_splits_dict,
            espn_stats_container=espn_stats_container,
            is_batter=is_batter,
        )

        # Categorize result
        if is_matched:
            matched.append(player_model)
        else:
            unmatched.append(player_model)

    return {"matched": matched, "ambiguous": ambiguous, "unmatched": unmatched}
