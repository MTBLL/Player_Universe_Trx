import re
import logging
from typing import Dict, List, Optional, Set, Tuple

from player_universe_trx.models.player import PlayerModel

# Configure logging
logger = logging.getLogger("player_universe_trx.matchers")

# Team code mapping from ESPN to FanGraphs
ESPN_TO_FG_TEAM_MAPPING = {
    "KC": "KCR",
    "SD": "SDP",
    "TB": "TBR",
    "SF": "SFG",
}


class PlayerMatcher:
    """
    Match player data between ESPN and FanGraphs sources.
    
    This class implements an efficient matching algorithm that progressively
    tries different matching strategies and tracks matched/unmatched players
    to improve performance.
    """
    
    def __init__(self, espn_players: List[PlayerModel], fangraphs_data: List[Dict]):
        """
        Initialize the matcher with ESPN players and FanGraphs data.
        
        Args:
            espn_players: List of PlayerModel instances from ESPN
            fangraphs_data: List of FanGraphs player data dictionaries
        """
        self.espn_players = espn_players.copy()  # Work with a copy to preserve original
        self.fg_data = fangraphs_data
        
        # Results containers
        self.matched_players: List[PlayerModel] = []
        self.ambiguous_matches: List[Tuple[PlayerModel, List[Dict]]] = []
        self.unmatched_players: List[PlayerModel] = []
        
        # Track matched FanGraphs players by ID
        self.matched_fg_ids: Set[str] = set()
        
        # Organize FanGraphs data for efficient lookup
        self.fg_by_last_name = self._organize_fg_data_by_last_name()
        
    def _organize_fg_data_by_last_name(self) -> Dict[str, List[Dict]]:
        """
        Organize FanGraphs data by player last name for efficient lookup.
        
        Returns:
            Dictionary mapping last names to lists of FanGraphs player data
        """
        fg_by_last_name: Dict[str, List[Dict]] = {}
        
        for fg_player in self.fg_data:
            # Use ascii_name instead of name to handle accented characters
            name_field = "ascii_name" if "ascii_name" in fg_player else "name"
            
            if name_field not in fg_player:
                continue

            # Extract last name, removing suffixes
            last_name = self._extract_last_name(fg_player[name_field])
            if not last_name:
                continue

            if last_name not in fg_by_last_name:
                fg_by_last_name[last_name] = []
            fg_by_last_name[last_name].append(fg_player)
            
        return fg_by_last_name
    
    def _find_candidates_by_last_name(self, player: PlayerModel) -> List[Dict]:
        """
        Find FanGraphs candidates with matching last name for a player.
        
        Args:
            player: PlayerModel instance
            
        Returns:
            List of candidate FanGraphs players (filtered by already matched)
        """
        if not player.last_name:
            return []

        # Extract clean last name
        last_name = self._extract_last_name(player.last_name)
        if not last_name:
            return []

        # Get all candidates with matching last name
        all_candidates = self.fg_by_last_name.get(last_name, [])
        
        
        # Filter out already matched players
        return [c for c in all_candidates if c.get("playerid") not in self.matched_fg_ids]
    
    def _find_exact_first_name_matches(self, player: PlayerModel, candidates: List[Dict]) -> List[Dict]:
        """
        Find candidates with exact matching first name.
        
        Args:
            player: PlayerModel instance
            candidates: List of FanGraphs player data
            
        Returns:
            List of candidates with matching first name
        """
        exact_matches: List[Dict] = []
        if not player.first_name:
            return exact_matches
            
        for candidate in candidates:
            # Use ascii_name instead of name to handle accented characters
            name_field = "ascii_name" if "ascii_name" in candidate else "name"
            fg_first_name = self._extract_first_name(candidate.get(name_field, ""))
            if fg_first_name and fg_first_name == player.first_name:
                exact_matches.append(candidate)
        
        return exact_matches
    
    def _find_prefix_first_name_matches(self, player: PlayerModel, candidates: List[Dict]) -> List[Dict]:
        """
        Find candidates with first name prefix matching.
        
        Args:
            player: PlayerModel instance
            candidates: List of FanGraphs player data
            
        Returns:
            List of candidates with prefix-matching first name
        """
        prefix_matches: List[Dict] = []
        if not player.first_name:
            return prefix_matches
            
        for candidate in candidates:
            # Use ascii_name instead of name to handle accented characters
            name_field = "ascii_name" if "ascii_name" in candidate else "name"
            fg_first_name = self._extract_first_name(candidate.get(name_field, ""))
            if fg_first_name and (
                fg_first_name.startswith(player.first_name)
                or player.first_name.startswith(fg_first_name)
            ):
                prefix_matches.append(candidate)
        
        return prefix_matches
    
    def _filter_by_team(self, candidates: List[Dict], team_code: Optional[str]) -> List[Dict]:
        """
        Filter candidates by matching team codes.

        Args:
            candidates: List of candidate FanGraphs player data
            team_code: ESPN team code

        Returns:
            List of candidates with matching team codes
        """
        if not team_code:
            return []

        results = []
        fg_team_code = ESPN_TO_FG_TEAM_MAPPING.get(team_code, team_code)

        for candidate in candidates:
            if candidate.get("team") == fg_team_code:
                results.append(candidate)

        return results
    
    def _process_match(self, player: PlayerModel, match: Dict) -> None:
        """
        Process a matched player by merging data and updating tracking.
        
        Args:
            player: PlayerModel instance
            match: Matching FanGraphs player data
        """
        # Merge FanGraphs data into player model
        player.merge_fangraphs_data(match)
        
        # Add to matched players list
        self.matched_players.append(player)
        
        # Mark FanGraphs player as matched
        if "playerid" in match:
            fg_id = match["playerid"]
            self.matched_fg_ids.add(fg_id)
            
        # Log the match
        logger.debug(f"Matched player {player.name} with FanGraphs player {match.get('name')}")
    
    def _try_match_exact_first_name(self, player: PlayerModel, candidates: List[Dict]) -> bool:
        """
        Try to match a player using exact first name match.
        
        Args:
            player: PlayerModel instance
            candidates: List of candidate FanGraphs players
            
        Returns:
            True if matched, False otherwise
        """
        exact_matches = self._find_exact_first_name_matches(player, candidates)
        
        if len(exact_matches) == 1:
            # Single exact match found
            self._process_match(player, exact_matches[0])
            return True
        elif len(exact_matches) > 1:
            # Multiple exact matches, try team matching
            team_matches = self._filter_by_team(exact_matches, player.pro_team)
            if len(team_matches) == 1:
                self._process_match(player, team_matches[0])
                return True
            else:
                self.ambiguous_matches.append((player, exact_matches))
                return True
                
        return False
    
    def _try_match_prefix_first_name(self, player: PlayerModel, candidates: List[Dict]) -> bool:
        """
        Try to match a player using prefix first name match.
        
        Args:
            player: PlayerModel instance
            candidates: List of candidate FanGraphs players
            
        Returns:
            True if matched or ambiguous, False otherwise
        """
        prefix_matches = self._find_prefix_first_name_matches(player, candidates)
        
        if len(prefix_matches) == 1:
            # Single prefix match found
            self._process_match(player, prefix_matches[0])
            return True
        elif len(prefix_matches) > 1:
            # Multiple prefix matches, try team matching
            team_matches = self._filter_by_team(prefix_matches, player.pro_team)
            if len(team_matches) == 1:
                self._process_match(player, team_matches[0])
                return True
            else:
                self.ambiguous_matches.append((player, prefix_matches))
                return True
                
        return False
    
    def _try_match_by_team(self, player: PlayerModel, candidates: List[Dict]) -> bool:
        """
        Try to match a player using team code.
        
        Args:
            player: PlayerModel instance
            candidates: List of candidate FanGraphs players
            
        Returns:
            True if handled, False otherwise
        """
        team_matches = self._filter_by_team(candidates, player.pro_team)
        
        if len(team_matches) == 1:
            self._process_match(player, team_matches[0])
            return True
        elif team_matches:
            self.ambiguous_matches.append((player, team_matches))
            return True
        else:
            self.ambiguous_matches.append((player, candidates))
            return True
    
    def _match_player(self, player: PlayerModel) -> None:
        """
        Try to match a single player using progressive matching strategies.
        
        Args:
            player: PlayerModel instance to match
        """
        # Find candidates with matching last name
        candidates = self._find_candidates_by_last_name(player)
        if not candidates:
            self.unmatched_players.append(player)
            return
            
        # Try matching strategies in order of strictness
        # 1. Exact first name match
        if self._try_match_exact_first_name(player, candidates):
            return
            
        # 2. Prefix first name match
        if self._try_match_prefix_first_name(player, candidates):
            return
            
        # 3. Team match (last resort)
        if self._try_match_by_team(player, candidates):
            return
            
        # If we get here, we couldn't match or classify the player
        self.unmatched_players.append(player)
    
    def match_players(self) -> Dict[str, List]:
        """
        Match all players using progressive matching strategies.
        
        Returns:
            Dictionary with keys:
                - 'matched': List of PlayerModel instances that were successfully matched
                - 'multiple_matches': List of (player, candidates) tuples for manual review
                - 'no_matches': List of PlayerModel instances with no potential matches
        """
        # Reset the results
        self.matched_players = []
        self.ambiguous_matches = []
        self.unmatched_players = []
        self.matched_fg_ids = set()
        
        # Make a copy since we'll be modifying the list as we go
        players_to_match = self.espn_players.copy()
        
        # Perform specific player pre-matching first
        # This helps with players who have common last names
        special_players = ["Gary Sanchez", "Jose Ramirez", "Luis Garcia", "Eugenio Suarez"]
        
        # Process players in a strategic order to improve matching
        # 1. First process special players (manually identified as having common names)
        special_player_models = [p for p in players_to_match if p.name in special_players]
        
        # 2. Then process players who are on a team (more likely to be correctly matched)
        remaining_players = [p for p in players_to_match if p.name not in special_players]
        team_players = [p for p in remaining_players if p.pro_team is not None and p.pro_team != ""]
        no_team_players = [p for p in remaining_players if p.pro_team is None or p.pro_team == ""]
        
        # 3. Further prioritize active players
        active_team_players = [p for p in team_players if p.status == "active" or p.status == "injured"]
        inactive_team_players = [p for p in team_players if p.status != "active" and p.status != "injured"]
        
        # 4. Process in priority order
        for player in special_player_models:
            self._match_player(player)
            
        for player in active_team_players:
            self._match_player(player)
            
        for player in inactive_team_players:
            self._match_player(player)
            
        for player in no_team_players:
            self._match_player(player)
            
        return {
            "matched": self.matched_players,
            "multiple_matches": self.ambiguous_matches,
            "no_matches": self.unmatched_players,
        }
    
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


# Legacy function that uses the new class-based implementation
def match_player_models_on_fangraphs_data(
    players: List[PlayerModel], data: List[Dict]
) -> Dict[str, List]:
    """
    Match PlayerModel instances with FanGraphs data.

    Args:
        players: List of PlayerModel instances from ESPN
        data: List of FanGraphs player data dictionaries

    Returns:
        Dictionary with keys:
            - 'matched': List of PlayerModel instances that were successfully matched
            - 'multiple_matches': List of (player, candidates) tuples for manual review
            - 'no_matches': List of PlayerModel instances with no potential matches
    """
    matcher = PlayerMatcher(players, data)
    return matcher.match_players()


# For backwards compatibility, keep the standalone functions
def extract_last_name(full_name: str) -> str:
    """
    Extract the last name from a full name, removing suffixes.

    Args:
        full_name: Full player name

    Returns:
        Last name without suffixes
    """
    return PlayerMatcher._extract_last_name(full_name)


def extract_first_name(full_name: str) -> str:
    """
    Extract the first name from a full name.

    Args:
        full_name: Full player name

    Returns:
        First name
    """
    return PlayerMatcher._extract_first_name(full_name)


def filter_by_team(
    candidates: List[Dict],
    team_code: Optional[str],
) -> List[Dict]:
    """
    Filter candidates by matching team codes.

    Args:
        candidates: List of candidate FanGraphs player data
        team_code: ESPN team code

    Returns:
        List of candidates with matching team codes
    """
    if not team_code:
        return []

    results = []
    fg_team_code = ESPN_TO_FG_TEAM_MAPPING.get(team_code, team_code)

    for candidate in candidates:
        if candidate.get("team") == fg_team_code:
            results.append(candidate)

    return results