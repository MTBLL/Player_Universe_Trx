import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from typing_extensions import TYPE_CHECKING

from player_universe_trx.models.espn import (
    EspnBatterModel,
    EspnBatterStatsGroupModel,
    EspnPitcherModel,
    EspnPitcherStatsGroupModel,
    EspnPlayerModel,
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
from player_universe_trx.models.savant import (
    SavantBatterModel,
    SavantPitcherModel,
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

# Configure logging
logger = logging.getLogger("player_universe_trx.matchers")


class MatchMethod(Enum):
    """Method used to match a player between data sources."""

    SLUG = "slug"
    EXACT_NAME = "exact_name"
    PREFIX_NAME = "prefix_name"
    TEAM = "team"
    NONE = "none"


class MatchConfidence(Enum):
    """Confidence level of a player match."""

    HIGH = 90  # Slug or exact name + team
    MEDIUM = 70  # Exact name or prefix + team
    LOW = 40  # Prefix name or team only
    AMBIGUOUS = 0  # Multiple candidates
    NONE = -1  # No match


@dataclass
class PlayerMatchResult:
    """
    Result of matching a player across data sources.

    This is a transient object used for auditing and debugging the matching process.
    It is not stored in the PlayerModel, but can be inspected to understand how
    matches were made.
    """

    espn_player: EspnBatterModel | EspnPitcherModel
    fangraphs_match: Optional[FangraphsBatterModel | FangraphsPitcherModel]
    savant_match: Optional[SavantBatterModel | SavantPitcherModel]
    match_method: MatchMethod
    confidence: MatchConfidence
    candidates: List[FangraphsBatterModel | FangraphsPitcherModel] = field(
        default_factory=list
    )
    notes: str = ""


# Team code mapping from ESPN to FanGraphs
ESPN_TO_FG_TEAM_MAPPING = {
    "KC": "KCR",
    "SD": "SDP",
    "TB": "TBR",
    "SF": "SFG",
}
# Team code mapping from FanGraphs to ESPN
FG_TO_ESPN_TEAM_MAPPING = {
    "KCR": "KC",
    "SDP": "SD",
    "TBR": "TB",
    "SFG": "SF",
}


class PlayerMatcher:
    """
    Match player data between ESPN and FanGraphs sources.

    This class implements an efficient matching algorithm that progressively
    tries different matching strategies and tracks matched/unmatched players
    to improve performance.
    """

    def __init__(
        self,
        espn_players: Sequence[EspnBatterModel | EspnPitcherModel],
        fangraphs_data: Optional[
            Sequence[FangraphsBatterModel | FangraphsPitcherModel]
        ],
        savant_data: Optional[Sequence[SavantBatterModel | SavantPitcherModel]] = None,
    ):
        """
        Initialize the matcher with ESPN players, FanGraphs data, and optional Savant data.

        Args:
            espn_players: Sequence of PlayerModel instances from ESPN
            fangraphs_data: Sequence of FanGraphs player data dictionaries
            savant_data: Optional sequence of Savant player data dictionaries
        """
        self.espn_players = list(
            espn_players
        )  # Convert to list and copy to preserve original
        self.fg_data = list(fangraphs_data) if fangraphs_data else []
        self.savant_data = list(savant_data) if savant_data else []

        # Results containers (deprecated - kept for backward compatibility)
        self.matched_players: List[MtblPlayerModel] = []
        self.ambiguous_matches: List[Tuple[MtblPlayerModel, List[Dict]]] = []
        self.unmatched_players: List[MtblPlayerModel] = []

        # Track matched players by ID
        self.matched_fg_ids: Set[str] = set()
        self.matched_savant_ids: Set[int] = set()

        # FanGraphs indexes for efficient lookup
        self.fg_by_last_name: Dict[
            str, List[FangraphsBatterModel | FangraphsPitcherModel]
        ] = {}
        self.fg_by_slug: Dict[str, FangraphsBatterModel | FangraphsPitcherModel] = {}
        self.fg_by_team: Dict[
            str, List[FangraphsBatterModel | FangraphsPitcherModel]
        ] = {}
        self.fg_by_id: Dict[str, FangraphsBatterModel | FangraphsPitcherModel] = {}

        # Savant indexes
        self.savant_by_mlb_id: Dict[int, SavantBatterModel | SavantPitcherModel] = {}

        # Build all indexes
        self._build_indexes()

    def _build_indexes(self) -> None:
        """
        Build all indexes for fast lookups in a single pass.

        This method indexes FanGraphs data by:
        - Last name (for name-based matching)
        - Slug (exact and normalized for slug-based matching)
        - Team (for team-based disambiguation)
        - Player ID (for quick lookup)

        Also indexes Savant data by MLB ID (player_id).
        """
        # Index FanGraphs data
        for fg_player in self.fg_data:
            playerid = fg_player.playerid
            slug = fg_player.slug
            team = fg_player.team

            # Use ascii_name instead of name to handle accented characters
            name = fg_player.ascii_name if fg_player.ascii_name else fg_player.name
            last_name = self._extract_last_name(name)

            # Index by player ID
            if playerid:
                self.fg_by_id[playerid] = fg_player

            # Index by slug (exact and normalized)
            if slug:
                # Also index normalized version (no periods)
                normalized = slug.replace(".", "")
                self.fg_by_slug[normalized] = fg_player

            # Index by team, normalized for ESPN team names
            if team:
                normalized_team = FG_TO_ESPN_TEAM_MAPPING.get(team, team)
                if normalized_team not in self.fg_by_team:
                    self.fg_by_team[normalized_team] = []
                self.fg_by_team[normalized_team].append(fg_player)

            # Index by last name
            if last_name:
                if last_name not in self.fg_by_last_name:
                    self.fg_by_last_name[last_name] = []
                self.fg_by_last_name[last_name].append(fg_player)

        # Index Savant data by MLB ID (player_id)
        for savant_player in self.savant_data:
            player_id = savant_player.player_id
            if player_id:
                self.savant_by_mlb_id[player_id] = savant_player

    def _remove_from_indexes(
        self, fg_player: FangraphsBatterModel | FangraphsPitcherModel
    ) -> None:
        """
        Remove a matched player from all indexes to improve performance.

        This shrinks the indexes as matches are found, reducing the number of
        candidates to check for subsequent matches.

        Args:
            fg_player: FanGraphs player model to remove from indexes
        """
        playerid = fg_player.playerid
        slug = fg_player.slug
        team = fg_player.team
        mlbid = fg_player.xmlbam_id

        # Use ascii_name for consistency with indexing
        name = fg_player.ascii_name if fg_player.ascii_name else fg_player.name
        last_name = self._extract_last_name(name)

        # Remove from last name index
        if last_name and last_name in self.fg_by_last_name:
            self.fg_by_last_name[last_name] = [
                p for p in self.fg_by_last_name[last_name] if p.playerid != playerid
            ]
            # Clean up empty entries
            if not self.fg_by_last_name[last_name]:
                del self.fg_by_last_name[last_name]

        # Remove from team index
        if team and team in self.fg_by_team:
            self.fg_by_team[team] = [
                p for p in self.fg_by_team[team] if p.playerid != playerid
            ]
            if not self.fg_by_team[team]:
                del self.fg_by_team[team]

        # Remove from slug indexes (fast - O(1))
        if slug:
            self.fg_by_slug.pop(slug, None)

        # Remove from ID index
        if playerid:
            self.fg_by_id.pop(playerid, None)

        # Remove from Savant MLB ID index
        if mlbid:
            self.savant_by_mlb_id.pop(mlbid, None)

    def _try_match_by_slug(
        self, player: EspnPlayerModel
    ) -> Optional[PlayerMatchResult]:
        """
        Try to match a player using slug (fastest, highest confidence).

        Args:
            player: PlayerModel instance with ESPN data

        Returns:
            PlayerMatchResult if match found, None otherwise
        """
        if not player.slug:
            return None

        # Try exact match first
        fg_match = self.fg_by_slug.get(player.slug)

        if fg_match:
            # Check if already matched (shouldn't happen with index shrinking, but be safe)
            if fg_match.playerid in self.matched_fg_ids:
                return None

            # Get Savant data using xmlbam_id from FanGraphs match
            savant_match = None
            xmlbam_id = fg_match.xmlbam_id
            if xmlbam_id and self.savant_by_mlb_id:
                savant_match = self.savant_by_mlb_id.get(xmlbam_id)
                if savant_match and savant_match.player_id in self.matched_savant_ids:
                    savant_match = None  # Already matched to another player

            assert isinstance(player, EspnBatterModel | EspnPitcherModel)
            return PlayerMatchResult(
                espn_player=player,
                fangraphs_match=fg_match,
                savant_match=savant_match,
                match_method=MatchMethod.SLUG,
                confidence=MatchConfidence.HIGH,
                candidates=[fg_match],
                notes=f"Matched on slug: {player.slug}",
            )

        return None

    def _find_candidates_by_last_name(
        self, player: EspnBatterModel | EspnPitcherModel
    ) -> List[FangraphsBatterModel | FangraphsPitcherModel]:
        """
        Find FanGraphs candidates with matching last name for a player.

        Args:
            player: PlayerModel instance

        Returns:
            List of candidate FanGraphs player models

        Note:
            With index shrinking enabled, matched players are already removed
            from indexes, so no filtering is needed.
        """
        if not player.last_name:
            return []

        # Extract clean last name
        last_name = self._extract_last_name(player.last_name)
        if not last_name:
            return []

        # Get all candidates with matching last name
        # Matched players are already removed from index, no filtering needed
        return self.fg_by_last_name.get(last_name, [])

    def _find_exact_first_name_matches(
        self,
        player: EspnBatterModel | EspnPitcherModel,
        candidates: List[FangraphsBatterModel | FangraphsPitcherModel],
    ) -> List[FangraphsBatterModel | FangraphsPitcherModel]:
        """
        Find candidates with exact matching first name.

        Args:
            player: PlayerModel instance
            candidates: List of FanGraphs player models

        Returns:
            List of candidates with matching first name
        """
        exact_matches: List[FangraphsBatterModel | FangraphsPitcherModel] = []
        if not player.first_name:
            return exact_matches

        for candidate in candidates:
            # Use ascii_name instead of name to handle accented characters
            name = candidate.ascii_name if candidate.ascii_name else candidate.name
            fg_first_name = self._extract_first_name(name)
            if fg_first_name and fg_first_name == player.first_name:
                exact_matches.append(candidate)

        return exact_matches

    def _find_prefix_first_name_matches(
        self,
        player: EspnBatterModel | EspnPitcherModel,
        candidates: List[FangraphsBatterModel | FangraphsPitcherModel],
    ) -> List[FangraphsBatterModel | FangraphsPitcherModel]:
        """
        Find candidates with first name prefix matching.

        Args:
            player: PlayerModel instance
            candidates: List of FanGraphs player models

        Returns:
            List of candidates with prefix-matching first name
        """
        prefix_matches: List[FangraphsBatterModel | FangraphsPitcherModel] = []
        if not player.first_name:
            return prefix_matches

        for candidate in candidates:
            # Use ascii_name instead of name to handle accented characters
            name = candidate.ascii_name if candidate.ascii_name else candidate.name
            fg_first_name = self._extract_first_name(name)
            if fg_first_name and (
                fg_first_name.startswith(player.first_name)
                or player.first_name.startswith(fg_first_name)
            ):
                prefix_matches.append(candidate)

        return prefix_matches

    def _filter_by_team(
        self,
        candidates: List[FangraphsBatterModel | FangraphsPitcherModel],
        team_code: Optional[str],
    ) -> List[FangraphsBatterModel | FangraphsPitcherModel]:
        """
        Filter candidates by matching team codes.

        Args:
            candidates: List of candidate FanGraphs player models
            team_code: ESPN team code

        Returns:
            List of candidates with matching team codes
        """
        if not team_code:
            return []

        results = []
        fg_team_code = ESPN_TO_FG_TEAM_MAPPING.get(team_code, team_code)

        for candidate in candidates:
            if candidate.team == fg_team_code:
                results.append(candidate)

        return results

    def _get_savant_match(
        self, fg_match: FangraphsBatterModel | FangraphsPitcherModel
    ) -> Optional[SavantBatterModel | SavantPitcherModel]:
        """
        Get Savant data for a FanGraphs match using xmlbam_id.

        Args:
            fg_match: FanGraphs player model

        Returns:
            Savant player model if found and not already matched, None otherwise
        """
        xmlbam_id = fg_match.xmlbam_id
        if not xmlbam_id or not self.savant_by_mlb_id:
            return None

        savant_match = self.savant_by_mlb_id.get(xmlbam_id)
        if savant_match and savant_match.player_id in self.matched_savant_ids:
            return None  # Already matched to another player

        return savant_match

    def _try_match_exact_first_name(
        self,
        player: EspnBatterModel | EspnPitcherModel,
        candidates: List[FangraphsBatterModel | FangraphsPitcherModel],
    ) -> Optional[PlayerMatchResult]:
        """
        Try to match a player using exact first name match.

        Args:
            player: PlayerModel instance
            candidates: List of candidate FanGraphs players

        Returns:
            PlayerMatchResult if match found or ambiguous, None otherwise
        """
        exact_matches = self._find_exact_first_name_matches(player, candidates)

        if len(exact_matches) == 1:
            # Single exact match found
            match = exact_matches[0]
            savant_match = self._get_savant_match(match)

            return PlayerMatchResult(
                espn_player=player,
                fangraphs_match=match,
                savant_match=savant_match,
                match_method=MatchMethod.EXACT_NAME,
                confidence=MatchConfidence.MEDIUM,
                candidates=[match],
                notes="Single exact first name match",
            )

        elif len(exact_matches) > 1:
            # Multiple exact matches, try team disambiguation
            team_matches = self._filter_by_team(exact_matches, player.pro_team)

            if len(team_matches) == 1:
                match = team_matches[0]
                savant_match = self._get_savant_match(match)

                return PlayerMatchResult(
                    espn_player=player,
                    fangraphs_match=match,
                    savant_match=savant_match,
                    match_method=MatchMethod.EXACT_NAME,
                    confidence=MatchConfidence.HIGH,  # Name + team
                    candidates=[match],
                    notes="Exact name + team disambiguation",
                )
            else:
                # Ambiguous - multiple matches even after team filter
                return PlayerMatchResult(
                    espn_player=player,
                    fangraphs_match=None,
                    savant_match=None,
                    match_method=MatchMethod.EXACT_NAME,
                    confidence=MatchConfidence.AMBIGUOUS,
                    candidates=exact_matches,
                    notes=f"Multiple exact matches: {len(exact_matches)}",
                )

        return None

    def _try_match_prefix_first_name(
        self,
        player: EspnBatterModel | EspnPitcherModel,
        candidates: List[FangraphsBatterModel | FangraphsPitcherModel],
    ) -> Optional[PlayerMatchResult]:
        """
        Try to match a player using prefix first name match.

        Args:
            player: PlayerModel instance
            candidates: List of candidate FanGraphs players

        Returns:
            PlayerMatchResult if match found or ambiguous, False otherwise
        """
        prefix_matches = self._find_prefix_first_name_matches(player, candidates)

        if len(prefix_matches) == 1:
            # Single prefix match found
            match = prefix_matches[0]
            savant_match = self._get_savant_match(match)

            return PlayerMatchResult(
                espn_player=player,
                fangraphs_match=match,
                savant_match=savant_match,
                match_method=MatchMethod.PREFIX_NAME,
                confidence=MatchConfidence.LOW,
                candidates=[match],
                notes="Single prefix first name match",
            )

        elif len(prefix_matches) > 1:
            # Multiple prefix matches, try team disambiguation
            team_matches = self._filter_by_team(prefix_matches, player.pro_team)

            if len(team_matches) == 1:
                match = team_matches[0]
                savant_match = self._get_savant_match(match)

                return PlayerMatchResult(
                    espn_player=player,
                    fangraphs_match=match,
                    savant_match=savant_match,
                    match_method=MatchMethod.PREFIX_NAME,
                    confidence=MatchConfidence.MEDIUM,  # Prefix + team
                    candidates=[match],
                    notes="Prefix name + team disambiguation",
                )
            else:
                # Ambiguous
                return PlayerMatchResult(
                    espn_player=player,
                    fangraphs_match=None,
                    savant_match=None,
                    match_method=MatchMethod.PREFIX_NAME,
                    confidence=MatchConfidence.AMBIGUOUS,
                    candidates=prefix_matches,
                    notes=f"Multiple prefix matches: {len(prefix_matches)}",
                )

        return None

    def _try_match_by_team(
        self,
        player: EspnBatterModel | EspnPitcherModel,
        candidates: List[FangraphsBatterModel | FangraphsPitcherModel],
    ) -> Optional[PlayerMatchResult]:
        """
        Try to match a player using team code (last resort).

        Args:
            player: PlayerModel instance
            candidates: List of candidate FanGraphs players

        Returns:
            PlayerMatchResult - always returns a result (match or ambiguous)
        """
        team_matches = self._filter_by_team(candidates, player.pro_team)

        if len(team_matches) == 1:
            # Single team match
            match = team_matches[0]
            savant_match = self._get_savant_match(match)

            return PlayerMatchResult(
                espn_player=player,
                fangraphs_match=match,
                savant_match=savant_match,
                match_method=MatchMethod.TEAM,
                confidence=MatchConfidence.LOW,
                candidates=[match],
                notes="Team-only match (last resort)",
            )

        elif team_matches:
            # Multiple team matches - ambiguous
            return PlayerMatchResult(
                espn_player=player,
                fangraphs_match=None,
                savant_match=None,
                match_method=MatchMethod.TEAM,
                confidence=MatchConfidence.AMBIGUOUS,
                candidates=team_matches,
                notes=f"Multiple team matches: {len(team_matches)}",
            )

        else:
            # No team matches, but we have candidates
            return PlayerMatchResult(
                espn_player=player,
                fangraphs_match=None,
                savant_match=None,
                match_method=MatchMethod.NONE,
                confidence=MatchConfidence.AMBIGUOUS,
                candidates=candidates,
                notes=f"Candidates exist but no definitive match: {len(candidates)}",
            )

    def _match_player(self, player: EspnPlayerModel) -> PlayerMatchResult:
        """
        Try to match a single player using progressive matching strategies.

        Args:
            player: PlayerModel instance to match

        Returns:
            PlayerMatchResult with match information
        """
        # STRATEGY 1: Slug matching (FASTEST, HIGHEST CONFIDENCE)
        if player.slug:
            result = self._try_match_by_slug(player)
            if result:
                return result

        assert isinstance(player, EspnBatterModel | EspnPitcherModel)
        # STRATEGY 2: Find candidates by last name
        candidates = self._find_candidates_by_last_name(player)
        if not candidates:
            return PlayerMatchResult(
                espn_player=player,
                fangraphs_match=None,
                savant_match=None,
                match_method=MatchMethod.NONE,
                confidence=MatchConfidence.NONE,
                candidates=[],
                notes="No candidates with matching last name",
            )

        # STRATEGY 3: Exact first name match
        result = self._try_match_exact_first_name(player, candidates)
        if result:
            return result

        # STRATEGY 4: Prefix first name match
        result = self._try_match_prefix_first_name(player, candidates)
        if result:
            return result

        # STRATEGY 5: Team-only match (last resort)
        result = self._try_match_by_team(player, candidates)
        if result:
            return result

        # Should not reach here, but just in case
        return PlayerMatchResult(
            espn_player=player,
            fangraphs_match=None,
            savant_match=None,
            match_method=MatchMethod.NONE,
            confidence=MatchConfidence.NONE,
            candidates=candidates,
            notes="No definitive match found",
        )

    def match_players(self) -> List[PlayerMatchResult]:
        """
        Match all ESPN players against FanGraphs and Savant data.

        Returns:
            List of PlayerMatchResult objects (one per ESPN player)

        Note:
            This method shrinks indexes as matches are found to improve performance.
            Players are processed in their natural order since slug-first matching
            and index shrinking handle edge cases effectively.
        """
        # Reset tracking
        self.matched_fg_ids = set()
        self.matched_savant_ids = set()

        results = []

        # Process players in natural order (slug-first matching + index shrinking handles edge cases)
        for player in self.espn_players:
            result = self._match_player(player)

            # Track matched IDs and shrink indexes
            if result.fangraphs_match:
                fg_id = result.fangraphs_match.playerid
                if fg_id:
                    self.matched_fg_ids.add(fg_id)
                    self._remove_from_indexes(result.fangraphs_match)

            if result.savant_match:
                savant_id = result.savant_match.player_id
                if savant_id:
                    self.matched_savant_ids.add(savant_id)

            results.append(result)

        return results

    @staticmethod
    def _extract_last_name(full_name: str) -> str:
        """
        Extract the last name from a full name, removing suffixes.

        Args:
            full_name: Full player name

        Returns:
            Last name without suffixes
        """
        if not full_name:
            return ""

        # Split the name
        parts = full_name.split()
        if not parts:
            return ""

        # Remove suffix if present
        suffix_pattern = r"^(Jr\.?|Sr\.?|I{2,3}|IV)$"
        if len(parts) > 1 and re.match(suffix_pattern, parts[-1], re.IGNORECASE):
            last_name = parts[-2]
        else:
            last_name = parts[-1]

        return last_name

    @staticmethod
    def _extract_first_name(full_name: str) -> str:
        """
        Extract the first name from a full name.

        Args:
            full_name: Full player name

        Returns:
            First name
        """
        if not full_name:
            return ""

        parts = full_name.split()
        if not parts:
            return ""

        return parts[0]


# Helper functions for apply_matches
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
    if not fg_match or not fg_match.projection:
        return {}

    return fg_match.projection.model_dump(exclude_none=True)


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
    espn_stats_container: Optional[EspnBatterStatsGroupModel | EspnPitcherStatsGroupModel],
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


# Standalone function for applying matches
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
