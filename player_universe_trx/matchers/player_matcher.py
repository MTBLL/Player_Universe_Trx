import logging
from typing import Dict, List, Optional, Sequence, Set, Tuple

from typing_extensions import TYPE_CHECKING

from player_universe_trx.matchers.config import (
    ESPN_TO_FG_TEAM_MAPPING,
)
from player_universe_trx.matchers.indexing import PlayerIndex
from player_universe_trx.matchers.models import (
    MatchConfidence,
    MatchMethod,
    PlayerMatchResult,
)
from player_universe_trx.matchers.utils import extract_first_name, extract_last_name
from player_universe_trx.models.espn import (
    EspnBatterModel,
    EspnPitcherModel,
    EspnPlayerModel,
)
from player_universe_trx.models.fangraphs import (
    FangraphsBatterModel,
    FangraphsPitcherModel,
)
from player_universe_trx.models.mtbl import (
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

        # Results containers (deprecated - kept for backward compatibility)
        self.matched_players: List[MtblPlayerModel] = []
        self.ambiguous_matches: List[Tuple[MtblPlayerModel, List[Dict]]] = []
        self.unmatched_players: List[MtblPlayerModel] = []

        # Track matched players by ID
        self.matched_fg_ids: Set[str] = set()
        self.matched_savant_ids: Set[int] = set()

        # Build player indexes for efficient lookup
        self.index = PlayerIndex(fangraphs_data, savant_data)

    def _try_match_by_slug(
        self, player: EspnPlayerModel
    ) -> Optional[PlayerMatchResult]:
        """
        Try to match a player using slug with team disambiguation for duplicates.

        Args:
            player: PlayerModel instance with ESPN data

        Returns:
            PlayerMatchResult if match found, None otherwise
        """
        if not player.slug:
            return None

        # Get all players with matching slug
        fg_matches = self.index.find_by_slug(player.slug)

        # Filter out already matched players
        fg_matches = [p for p in fg_matches if p.playerid not in self.matched_fg_ids]

        if not fg_matches:
            return None

        # Handle single match (most common case)
        if len(fg_matches) == 1:
            fg_match = fg_matches[0]
            savant_match = self._get_savant_match(fg_match)

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

        # Handle duplicate slugs - use team to disambiguate
        assert isinstance(player, EspnBatterModel | EspnPitcherModel)
        team_matches = self._filter_by_team(fg_matches, player.pro_team)

        if len(team_matches) == 1:
            # Team disambiguation successful
            fg_match = team_matches[0]
            savant_match = self._get_savant_match(fg_match)

            return PlayerMatchResult(
                espn_player=player,
                fangraphs_match=fg_match,
                savant_match=savant_match,
                match_method=MatchMethod.SLUG,
                confidence=MatchConfidence.HIGH,  # Slug + team = HIGH confidence
                candidates=[fg_match],
                notes=f"Matched on slug + team (duplicate slug resolved): {player.slug}",
            )

        # Ambiguous - multiple players with same slug, couldn't disambiguate by team
        return PlayerMatchResult(
            espn_player=player,
            fangraphs_match=None,
            savant_match=None,
            match_method=MatchMethod.SLUG,
            confidence=MatchConfidence.AMBIGUOUS,
            candidates=fg_matches,
            notes=f"Duplicate slug, ambiguous match: {player.slug} ({len(fg_matches)} candidates)",
        )

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
        last_name = extract_last_name(player.last_name)
        if not last_name:
            return []

        # Get all candidates with matching last name
        # Matched players are already removed from index, no filtering needed
        return self.index.find_by_last_name(last_name)

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
            fg_first_name = extract_first_name(name)
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
            fg_first_name = extract_first_name(name)
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
        if not xmlbam_id or not self.index.savant_by_mlb_id:
            return None

        savant_match = self.index.find_savant_by_mlb_id(xmlbam_id)
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
                    self.index.remove_matched(result.fangraphs_match)

            if result.savant_match:
                savant_id = result.savant_match.player_id
                if savant_id:
                    self.matched_savant_ids.add(savant_id)

            results.append(result)

        return results
