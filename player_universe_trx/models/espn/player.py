from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class BirthPlace(BaseModel):
    """Birth place information."""

    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None


class DraftRank(BaseModel):
    """Draft rank information for a specific ranking type."""

    auctionValue: Optional[float] = None
    rank: Optional[int] = None
    rankSourceId: Optional[int] = None
    rankType: Optional[str] = None
    slotId: Optional[int] = None


class TransactionItem(BaseModel):
    """Individual transaction item."""

    acquisitionBudget: Optional[int] = None
    fromLineupSlotId: Optional[int] = None
    fromTeamId: Optional[int] = None
    isKeeper: Optional[bool] = None
    overallPickNumber: Optional[int] = None
    playerId: Optional[int] = None
    toLineupSlotId: Optional[int] = None
    toTeamId: Optional[int] = None
    type: Optional[str] = None


class Transaction(BaseModel):
    """Player transaction."""

    bidAmount: Optional[float] = None
    executionType: Optional[str] = None
    id: Optional[str] = None
    isActingAsTeamOwner: Optional[bool] = None
    isLeagueManager: Optional[bool] = None
    isPending: Optional[bool] = None
    items: Optional[List[TransactionItem]] = None
    proposedDate: Optional[int] = None
    rating: Optional[int] = None
    scoringPeriodId: Optional[int] = None
    skipTransactionCounters: Optional[bool] = None
    status: Optional[str] = None
    subOrder: Optional[int] = None
    teamId: Optional[int] = None
    type: Optional[str] = None


class EspnPlayerModel(BaseModel):
    """Base ESPN player model with common fields for all player types."""

    # Player identification
    id: int
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    short_name: Optional[str] = None
    nickname: Optional[str] = None
    slug: Optional[str] = None

    # Position information
    primary_position: Optional[str] = None
    eligible_slots: Optional[List[str]] = None
    position_name: Optional[str] = None
    pos: Optional[str] = None

    # Team and status
    pro_team: Optional[str] = None
    injury_status: Optional[str] = None
    status: Optional[str] = None
    injured: Optional[bool] = None
    active: Optional[bool] = None

    # Ownership
    percent_owned: Optional[float] = None

    # Physical attributes
    weight: Optional[float] = None
    display_weight: Optional[str] = None
    height: Optional[int] = None
    display_height: Optional[str] = None

    # Player attributes
    bats: Optional[str] = None
    throws: Optional[str] = None
    date_of_birth: Optional[str] = None
    birth_place: Optional[BirthPlace] = None
    debut_year: Optional[int] = None
    jersey: Optional[str] = None
    headshot: Optional[str] = None

    # Fantasy information
    season_outlook: Optional[str] = None
    draft_auction_value: Optional[float] = None
    on_team_id: Optional[int] = None
    draft_ranks: Optional[Dict[str, DraftRank]] = None
    auction_value_average: Optional[float] = None

    # Game participation
    games_played_by_position: Optional[Dict[str, int]] = None

    # Transactions
    transactions: Optional[List[Transaction]] = None

    model_config = ConfigDict(populate_by_name=True)
