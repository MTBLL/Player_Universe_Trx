"""ESPN league models for parsing ESPN Fantasy Baseball league data."""

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class EspnPlayerMinimalModel(BaseModel):
    """Minimal player information from ESPN player pool entry."""

    id: int
    fullName: str = Field(..., alias="fullName")
    proTeamId: int = Field(..., alias="proTeamId")
    defaultPositionId: int = Field(..., alias="defaultPositionId")
    eligibleSlots: List[int] = Field(default_factory=list, alias="eligibleSlots")
    injuryStatus: Optional[str] = Field(None, alias="injuryStatus")
    active: bool = True

    model_config = ConfigDict(populate_by_name=True)


class EspnPlayerPoolEntryModel(BaseModel):
    """Player pool entry containing player data and ownership info."""

    id: int
    onTeamId: int = Field(..., alias="onTeamId")
    keeperValue: Optional[int] = Field(None, alias="keeperValue")
    keeperValueFuture: Optional[int] = Field(None, alias="keeperValueFuture")
    player: EspnPlayerMinimalModel

    model_config = ConfigDict(populate_by_name=True)


class EspnRosterEntryModel(BaseModel):
    """Individual roster entry for a player on a team."""

    playerId: int = Field(..., alias="playerId")
    lineupSlotId: int = Field(..., alias="lineupSlotId")
    acquisitionDate: Optional[int] = Field(None, alias="acquisitionDate")
    acquisitionType: Optional[str] = Field(None, alias="acquisitionType")
    injuryStatus: Optional[str] = Field(None, alias="injuryStatus")
    playerPoolEntry: EspnPlayerPoolEntryModel = Field(..., alias="playerPoolEntry")

    model_config = ConfigDict(populate_by_name=True)


class EspnRosterModel(BaseModel):
    """Team roster containing all roster entries."""

    entries: List[EspnRosterEntryModel]

    model_config = ConfigDict(populate_by_name=True)


class EspnRecordDetailModel(BaseModel):
    """Detailed record information (overall, home, away, division)."""

    wins: int = 0
    losses: int = 0
    ties: int = 0
    percentage: float = 0.0
    gamesBack: float = Field(0.0, alias="gamesBack")
    pointsFor: Optional[float] = Field(None, alias="pointsFor")
    pointsAgainst: Optional[float] = Field(None, alias="pointsAgainst")
    streakLength: Optional[int] = Field(None, alias="streakLength")
    streakType: Optional[str] = Field(None, alias="streakType")

    model_config = ConfigDict(populate_by_name=True)


class EspnRecordModel(BaseModel):
    """Team record with overall, home, away, and division splits."""

    overall: EspnRecordDetailModel
    home: Optional[EspnRecordDetailModel] = None
    away: Optional[EspnRecordDetailModel] = None
    division: Optional[EspnRecordDetailModel] = None

    model_config = ConfigDict(populate_by_name=True)


class EspnScoringCategoryModel(BaseModel):
    """Individual scoring category."""

    statId: int = Field(..., alias="statId")
    name: str
    isReverseItem: bool = Field(False, alias="isReverseItem")

    model_config = ConfigDict(populate_by_name=True)


class EspnScoringCategoriesModel(BaseModel):
    """Scoring categories for batting and pitching."""

    batting: List[EspnScoringCategoryModel] = Field(default_factory=list)
    pitching: List[EspnScoringCategoryModel] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


class EspnScoringSettingsModel(BaseModel):
    """League scoring settings."""

    categories: EspnScoringCategoriesModel
    scoringType: Optional[str] = Field(None, alias="scoringType")

    model_config = ConfigDict(populate_by_name=True)


class EspnAcquisitionSettingsModel(BaseModel):
    """League acquisition settings."""

    acquisitionBudget: Optional[int] = Field(None, alias="acquisitionBudget")

    model_config = ConfigDict(populate_by_name=True)


class EspnDraftSettingsModel(BaseModel):
    """League draft settings."""

    auctionBudget: Optional[int] = Field(None, alias="auctionBudget")
    type: Optional[str] = None  # "AUCTION", "SNAKE", etc.

    model_config = ConfigDict(populate_by_name=True)


class EspnRosterSettingsModel(BaseModel):
    """League roster settings including lineup slot counts."""

    lineupSlotCounts: Dict[str, int] = Field(
        default_factory=dict, alias="lineupSlotCounts"
    )
    rosterSize: Optional[int] = Field(None, alias="rosterSize")

    model_config = ConfigDict(populate_by_name=True)


class EspnLeagueSettingsModel(BaseModel):
    """League settings."""

    name: Optional[str] = None
    rosterSettings: Optional[EspnRosterSettingsModel] = Field(
        None, alias="rosterSettings"
    )
    scoringSettings: Optional[EspnScoringSettingsModel] = Field(
        None, alias="scoringSettings"
    )
    acquisitionSettings: Optional[EspnAcquisitionSettingsModel] = Field(
        None, alias="acquisitionSettings"
    )
    draftSettings: Optional[EspnDraftSettingsModel] = Field(
        None, alias="draftSettings"
    )

    model_config = ConfigDict(populate_by_name=True)


class EspnTransactionCounterModel(BaseModel):
    """Team transaction counter tracking acquisitions and budget."""

    acquisitionBudgetSpent: int = Field(0, alias="acquisitionBudgetSpent")
    acquisitions: int = 0
    drops: int = 0
    trades: int = 0

    model_config = ConfigDict(populate_by_name=True)


class EspnTeamModel(BaseModel):
    """ESPN fantasy team with roster and metadata."""

    id: int
    name: str
    abbrev: str
    logo: Optional[str] = None
    logoType: Optional[str] = Field(None, alias="logoType")
    owners: List[str] = Field(default_factory=list)
    primaryOwner: str = Field(..., alias="primaryOwner")
    roster: EspnRosterModel
    record: Optional[EspnRecordModel] = None
    playoffSeed: Optional[int] = Field(None, alias="playoffSeed")
    rankFinal: Optional[int] = Field(None, alias="rankFinal")
    rankCalculatedFinal: Optional[int] = Field(None, alias="rankCalculatedFinal")
    points: Optional[float] = None
    pointsAdjusted: Optional[float] = Field(None, alias="pointsAdjusted")
    transactionCounter: Optional[EspnTransactionCounterModel] = Field(
        None, alias="transactionCounter"
    )
    waiverRank: Optional[int] = Field(None, alias="waiverRank")

    model_config = ConfigDict(populate_by_name=True)


class EspnCategoryResultModel(BaseModel):
    """A single scoring category's outcome within a matchup."""

    value: Optional[float] = None
    result: Optional[str] = None  # WIN / LOSS / TIE

    model_config = ConfigDict(populate_by_name=True)


class EspnScheduleMatchupModel(BaseModel):
    """Individual schedule matchup."""

    id: int
    matchupPeriodId: int = Field(..., alias="matchupPeriodId")
    playoffTierType: Optional[str] = Field(None, alias="playoffTierType")
    winner: Optional[int | str] = None  # Can be team_id (int) or "BYE WEEK" (str)
    teams: Dict[str, str] = Field(default_factory=dict)  # team_id -> score string
    # Per-category breakdown for H2H category leagues: team_id -> {category ->
    # result}. Absent for points/roster-limit leagues (no scoreByStat upstream).
    categoryResults: Optional[Dict[str, Dict[str, EspnCategoryResultModel]]] = Field(
        None, alias="categoryResults"
    )

    model_config = ConfigDict(populate_by_name=True)


class EspnLeagueModel(BaseModel):
    """ESPN fantasy baseball league."""

    id: int
    seasonId: int = Field(..., alias="seasonId")
    scoringPeriodId: Optional[int] = Field(None, alias="scoringPeriodId")
    teams: List[EspnTeamModel]
    settings: Optional[EspnLeagueSettingsModel] = None
    status: Optional[Dict] = None
    schedule: List[EspnScheduleMatchupModel] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)
