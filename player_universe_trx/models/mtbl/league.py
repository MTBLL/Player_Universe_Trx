"""MTBL league models for database and JSON export."""

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class RosterSlotPlayer(BaseModel):
    """
    Minimal player data for roster slots.

    Contains only identification and basic info, no stats.
    The player_id links to the full player universe for detailed stats.
    """

    # Core identification - links to player universe
    player_id: int

    # Basic info (no stats)
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    # Team/Position info
    pro_team: str  # MLB team abbreviation (e.g., "NYY", "LAD")
    primary_position: str  # Position name (e.g., "SS", "OF", "SP")
    eligible_positions: List[str] = Field(
        default_factory=list
    )  # Position names (e.g., ["SS", "2B", "UTIL"])

    # Roster info
    lineup_slot: str  # Position slot name (e.g., "C", "OF", "SP", "BENCH")
    acquisition_type: Optional[str] = None  # "DRAFT", "ADD", "TRADE"
    acquisition_date: Optional[str] = None  # ISO format date string

    # Status
    injury_status: Optional[str] = None
    active: bool = True

    # Keeper value
    keeper_value: Optional[int] = None

    # Uniform number (e.g. "27")
    jersey: Optional[str] = None
    # Position name -> ISO date the player became eligible at that position
    eligible_date_by_position: Optional[Dict[str, str]] = None

    model_config = ConfigDict(populate_by_name=True)


class TeamRecordModel(BaseModel):
    """Team record summary."""

    wins: int = 0
    losses: int = 0
    ties: int = 0
    percentage: float = 0.0
    games_back: float = 0.0

    model_config = ConfigDict(populate_by_name=True)


class ScoringCategoryModel(BaseModel):
    """Individual scoring category."""

    stat_id: int
    name: str
    is_reverse: bool = False  # True for ERA, WHIP (lower is better)

    model_config = ConfigDict(populate_by_name=True)


class ScoringCategoriesModel(BaseModel):
    """Scoring categories for batting and pitching."""

    batting: List[ScoringCategoryModel] = Field(default_factory=list)
    pitching: List[ScoringCategoryModel] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


class GamesStartedLimitsModel(BaseModel):
    """League games-started limits for pitchers (start-cap rule)."""

    stat_id: int
    min: Optional[float] = None
    max_per_scoring_period: Optional[float] = None
    max_per_matchup: Optional[float] = None

    model_config = ConfigDict(populate_by_name=True)


class RosterSettingsModel(BaseModel):
    """League roster settings."""

    lineup_slot_counts: Dict[str, int] = Field(default_factory=dict)
    roster_size: Optional[int] = None

    model_config = ConfigDict(populate_by_name=True)


class TransactionSummaryModel(BaseModel):
    """Team transaction summary."""

    budget_spent: int = 0
    budget_remaining: Optional[int] = None
    acquisitions: int = 0
    drops: int = 0
    trades: int = 0
    waiver_rank: Optional[int] = None

    model_config = ConfigDict(populate_by_name=True)


class MtblTeamRosterModel(BaseModel):
    """
    MTBL team roster model for database and JSON export.

    Represents a complete team roster with explicit fields for each position type.
    Each field contains minimal player data (no stats) that can be exported to JSON
    or stored in database with player_id as foreign key to player universe.
    """

    # Team identification
    league_id: int
    season_id: int
    team_id: int
    team_name: str
    team_abbrev: str
    team_logo: Optional[str] = None
    owners: List[str] = Field(default_factory=list)
    primary_owner: str

    # Team record (optional)
    record: Optional[TeamRecordModel] = None

    # Transaction summary
    transactions: Optional[TransactionSummaryModel] = None

    # Roster slots - explicit fields for each position
    # Single-player positions
    c: Optional[RosterSlotPlayer] = None  # Catcher
    first_base: Optional[RosterSlotPlayer] = None  # 1B
    second_base: Optional[RosterSlotPlayer] = None  # 2B
    third_base: Optional[RosterSlotPlayer] = None  # 3B
    shortstop: Optional[RosterSlotPlayer] = None  # SS
    util: Optional[RosterSlotPlayer] = None  # UTIL

    # Multi-player positions (arrays)
    outfield: List[RosterSlotPlayer] = Field(default_factory=list)  # OF (typically 3)
    sp: List[RosterSlotPlayer] = Field(
        default_factory=list
    )  # Starting Pitchers (typically 5)
    rp: List[RosterSlotPlayer] = Field(
        default_factory=list
    )  # Relief Pitchers (typically 2)
    bench: List[RosterSlotPlayer] = Field(default_factory=list)  # Bench slots
    injured_list: List[RosterSlotPlayer] = Field(
        default_factory=list
    )  # Injured List (IL)

    model_config = ConfigDict(populate_by_name=True)


class MtblLeagueModel(BaseModel):
    """MTBL league summary model."""

    league_id: int
    league_name: Optional[str] = None
    season_id: int
    scoring_period_id: Optional[int] = None
    num_teams: int
    roster_settings: Optional[RosterSettingsModel] = None
    scoring_categories: Optional[ScoringCategoriesModel] = None
    games_started_limits: Optional[GamesStartedLimitsModel] = None
    acquisition_budget: Optional[int] = None
    draft_auction_budget: Optional[int] = None

    model_config = ConfigDict(populate_by_name=True)


class CategoryResultModel(BaseModel):
    """A single scoring category's outcome for a team within a matchup."""

    category: str
    value: Optional[float] = None
    result: Optional[str] = None  # WIN / LOSS / TIE

    model_config = ConfigDict(populate_by_name=True)


class GamesStartedModel(BaseModel):
    """A team's games-started tally within a matchup (pitcher start cap)."""

    value: float = 0.0
    limit_exceeded: bool = False
    exceeded_on_scoring_period: int = 0

    model_config = ConfigDict(populate_by_name=True)


class ScheduleMatchupModel(BaseModel):
    """Schedule matchup for a specific period."""

    matchup_id: int
    period_id: int
    is_playoff: bool = False
    team1_id: Optional[int] = None
    team1_score: Optional[str] = None
    team2_id: Optional[int] = None
    team2_score: Optional[str] = None
    winner_id: Optional[int] = None
    is_bye_week: bool = False
    # Per-category breakdown, populated only for H2H category leagues.
    team1_categories: Optional[List[CategoryResultModel]] = None
    team2_categories: Optional[List[CategoryResultModel]] = None
    # Games-started tally, populated only for leagues with a pitcher start cap.
    team1_games_started: Optional[GamesStartedModel] = None
    team2_games_started: Optional[GamesStartedModel] = None

    model_config = ConfigDict(populate_by_name=True)


class MtblScheduleModel(BaseModel):
    """League schedule model."""

    league_id: int
    season_id: int
    matchups: List[ScheduleMatchupModel] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)
