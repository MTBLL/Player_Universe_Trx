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


def _extract_fangraphs_projections(
    fg_match: Optional["FangraphsBatterModel | FangraphsPitcherModel"],
) -> Dict[str, Any]:
    """Extract FanGraphs projection stats.

    Args:
        fg_match: FanGraphs player model with projections

    Returns:
        Dictionary of projection stats
    """
    if not fg_match or not fg_match.projections:
        return {}

    return fg_match.projections.model_dump(exclude_none=True)


def _extract_savant_stats(
    savant_match: Optional["SavantBatterModel | SavantPitcherModel"],
) -> Dict[str, Any]:
    """Extract Savant sabermetric stats as unprefixed dictionary.

    Args:
        savant_match: Savant player model with stats

    Returns:
        Dictionary of Savant stats (unprefixed)
    """
    if savant_match and savant_match.stats:
        return savant_match.stats.model_dump(exclude_none=True)
    return {}


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
    projections_dict: Dict[str, Any],
    espn_stats_container: Optional[
        EspnBatterStatsGroupModel | EspnPitcherStatsGroupModel
    ],
    is_batter: bool,
) -> MtblPlayerModel:
    """Create typed player model (batter or pitcher) with stats.

    Args:
        base_player: Base MTBL player model
        stats_dict: Combined current season stats dictionary
        projections_dict: FanGraphs projections dictionary
        espn_stats_container: ESPN stats container with all periods
        is_batter: True for batter, False for pitcher

    Returns:
        MtblBatterModel or MtblPitcherModel with merged stats
    """
    base_data: Dict[str, Any] = base_player.model_dump()

    if is_batter:
        batter_stats: Optional[MtblBatterStatsModel] = None
        if stats_dict or projections_dict or espn_stats_container:
            # Type narrow the container for batters
            batter_container: Optional[EspnBatterStatsGroupModel] = (
                espn_stats_container
                if isinstance(espn_stats_container, EspnBatterStatsGroupModel)
                else None
            )
            batter_current_season: Optional[MtblBatterSeasonStatsModel] = (
                MtblBatterSeasonStatsModel(**stats_dict) if stats_dict else None
            )
            batter_projections: Optional[FangraphsBatterStatsModel] = (
                FangraphsBatterStatsModel(**projections_dict)
                if projections_dict
                else None
            )
            batter_stats = MtblBatterStatsModel(
                current_season=batter_current_season,
                projections=batter_projections,
                espn_stats=batter_container,
            )
        return MtblBatterModel(**base_data, stats=batter_stats)
    else:
        pitcher_stats: Optional[MtblPitcherStatsModel] = None
        if stats_dict or projections_dict or espn_stats_container:
            # Type narrow the container for pitchers
            pitcher_container: Optional[EspnPitcherStatsGroupModel] = (
                espn_stats_container
                if isinstance(espn_stats_container, EspnPitcherStatsGroupModel)
                else None
            )
            pitcher_current_season: Optional[MtblPitcherSeasonStatsModel] = (
                MtblPitcherSeasonStatsModel(**stats_dict) if stats_dict else None
            )
            pitcher_projections: Optional[FangraphsPitcherStatsModel] = (
                FangraphsPitcherStatsModel(**projections_dict)
                if projections_dict
                else None
            )
            pitcher_stats = MtblPitcherStatsModel(
                current_season=pitcher_current_season,
                projections=pitcher_projections,
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
            ambiguous_projections_dict: Dict[str, Any] = {}
            ambiguous_espn_stats_container: Optional[Any] = (
                result.espn_player.stats if result.espn_player.stats else None
            )
            ambiguous_player: MtblPlayerModel = _create_player_model(
                base_player=base_player,
                stats_dict=ambiguous_stats_dict,
                projections_dict=ambiguous_projections_dict,
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

        projections_dict: Dict[str, Any] = (
            _extract_fangraphs_projections(result.fangraphs_match) if is_matched else {}
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
            espn_stats_container=espn_stats_container,
            is_batter=is_batter,
        )

        # Categorize result
        if is_matched:
            matched.append(player_model)
        else:
            unmatched.append(player_model)

    return {"matched": matched, "ambiguous": ambiguous, "unmatched": unmatched}
