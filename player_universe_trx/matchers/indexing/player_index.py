from typing import Dict, List, Optional, Sequence, Tuple

from player_universe_trx.matchers.config import FG_TO_ESPN_TEAM_MAPPING
from player_universe_trx.matchers.utils import extract_last_name
from player_universe_trx.models.fangraphs import (
    FangraphsBatterModel,
    FangraphsPitcherModel,
)
from player_universe_trx.models.savant import SavantBatterModel, SavantPitcherModel


class PlayerIndex:
    """Manages indexes for efficient player lookups."""

    def __init__(
        self,
        fangraphs_data: Optional[
            Sequence[FangraphsBatterModel | FangraphsPitcherModel]
        ],
        savant_data: Optional[Sequence[SavantBatterModel | SavantPitcherModel]] = None,
    ):
        """
        Build all indexes from data.

        Args:
            fangraphs_data: Sequence of FanGraphs player data
            savant_data: Optional sequence of Savant player data
        """
        self.fg_data = list(fangraphs_data) if fangraphs_data else []
        self.savant_data = list(savant_data) if savant_data else []

        # FanGraphs indexes for efficient lookup
        self.fg_by_last_name: Dict[
            str, List[FangraphsBatterModel | FangraphsPitcherModel]
        ] = {}
        self.fg_by_slug: Dict[
            str, List[FangraphsBatterModel | FangraphsPitcherModel]
        ] = {}
        self.fg_by_team: Dict[
            str, List[FangraphsBatterModel | FangraphsPitcherModel]
        ] = {}
        self.fg_by_id: Dict[str, FangraphsBatterModel | FangraphsPitcherModel] = {}

        # Savant indexes
        self.savant_by_mlb_id: Dict[
            int, List[SavantBatterModel | SavantPitcherModel]
        ] = {}
        self.savant_by_mlb_id_and_type: Dict[
            Tuple[int, str], SavantBatterModel | SavantPitcherModel
        ] = {}

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

        Also indexes Savant data by MLB ID (player_id) and role. The role-aware
        index prevents two-way player batter and pitcher rows from overwriting
        each other.
        """
        # Index FanGraphs data
        for fg_player in self.fg_data:
            playerid = fg_player.playerid
            slug = fg_player.slug
            team = fg_player.team

            # Use ascii_name instead of name to handle accented characters
            name = fg_player.ascii_name if fg_player.ascii_name else fg_player.name
            last_name = extract_last_name(name)

            # Index by player ID
            if playerid:
                self.fg_by_id[playerid] = fg_player

            # Index by slug (exact and normalized) - store as list to handle duplicates
            if slug:
                # Also index normalized version (no periods)
                normalized = slug.replace(".", "")
                if normalized not in self.fg_by_slug:
                    self.fg_by_slug[normalized] = []
                self.fg_by_slug[normalized].append(fg_player)

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

        # Index Savant data by MLB ID (player_id) and player_type
        for savant_player in self.savant_data:
            player_id = savant_player.player_id
            if player_id:
                self.savant_by_mlb_id.setdefault(player_id, []).append(savant_player)
                if savant_player.player_type:
                    self.savant_by_mlb_id_and_type[
                        (player_id, savant_player.player_type)
                    ] = savant_player

    def find_by_slug(
        self, slug: str
    ) -> List[FangraphsBatterModel | FangraphsPitcherModel]:
        """
        Find players by slug. Returns a list to handle duplicate slugs.

        Args:
            slug: Player slug to search for

        Returns:
            List of FanGraphs players with matching slug (may be empty, or contain multiple players)
        """
        if not slug:
            return []

        # Try exact match first
        fg_matches = self.fg_by_slug.get(slug)
        if fg_matches:
            return fg_matches

        # Try normalized (no periods)
        normalized = slug.replace(".", "")
        return self.fg_by_slug.get(normalized, [])

    def find_by_last_name(
        self, last_name: str
    ) -> List[FangraphsBatterModel | FangraphsPitcherModel]:
        """
        Find candidates by last name.

        Args:
            last_name: Last name to search for

        Returns:
            List of FanGraphs players with matching last name
        """
        if not last_name:
            return []

        # Get all candidates with matching last name
        # Matched players are already removed from index, no filtering needed
        return self.fg_by_last_name.get(last_name, [])

    def find_by_team(
        self, team: str
    ) -> List[FangraphsBatterModel | FangraphsPitcherModel]:
        """
        Find players by team.

        Args:
            team: Team code to search for

        Returns:
            List of FanGraphs players on the specified team
        """
        if not team:
            return []

        return self.fg_by_team.get(team, [])

    def find_savant_by_mlb_id(
        self, mlb_id: Optional[int], player_type: Optional[str] = None
    ) -> Optional[SavantBatterModel | SavantPitcherModel]:
        """
        Find Savant player by MLB ID.

        Args:
            mlb_id: MLB player ID
            player_type: Optional Savant role ("batter" or "pitcher")

        Returns:
            Savant player if found, None otherwise
        """
        if not mlb_id:
            return None

        if player_type:
            match = self.savant_by_mlb_id_and_type.get((mlb_id, player_type))
            if match:
                return match

        matches = self.savant_by_mlb_id.get(mlb_id, [])
        if len(matches) == 1:
            return matches[0]

        return None

    def remove_matched(
        self, fg_player: FangraphsBatterModel | FangraphsPitcherModel
    ) -> None:
        """
        Remove matched player from all indexes.

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
        last_name = extract_last_name(name)

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

        # Remove from slug indexes
        if slug:
            normalized = slug.replace(".", "")
            if normalized in self.fg_by_slug:
                self.fg_by_slug[normalized] = [
                    p for p in self.fg_by_slug[normalized] if p.playerid != playerid
                ]
                # Clean up empty entries
                if not self.fg_by_slug[normalized]:
                    del self.fg_by_slug[normalized]

        # Remove from ID index
        if playerid:
            self.fg_by_id.pop(playerid, None)

        # Remove from Savant MLB ID index for this role only. Two-way players may
        # still have a valid row in the opposite role.
        if mlbid:
            player_type = "batter" if isinstance(fg_player, FangraphsBatterModel) else "pitcher"
            self.savant_by_mlb_id_and_type.pop((mlbid, player_type), None)

            if mlbid in self.savant_by_mlb_id:
                self.savant_by_mlb_id[mlbid] = [
                    p
                    for p in self.savant_by_mlb_id[mlbid]
                    if p.player_type != player_type
                ]
                if not self.savant_by_mlb_id[mlbid]:
                    del self.savant_by_mlb_id[mlbid]
