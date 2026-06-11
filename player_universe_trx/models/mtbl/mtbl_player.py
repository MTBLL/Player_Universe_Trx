import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from player_universe_trx.models.fangraphs import FangraphsPlayerModel

# Configure logging
logger = logging.getLogger("player_universe_trx.models.mtbl")


class BirthPlace(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None


class StatPeriod(BaseModel):
    points: float = 0.0
    projected_points: float = 0.0
    breakdown: Dict[str, Any] = {}
    projected_breakdown: Dict[str, Any] = {}


class MtblPlayerModel(BaseModel):
    """Pydantic model for baseball player data"""

    # Basic player info
    id_espn: Optional[int] = Field(None, alias="id")
    id_fangraphs: Optional[str] = None
    id_xmlbam: Optional[int] = None
    name: Optional[str] = None
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    name_ascii: Optional[str] = None

    # Display information
    slug: Optional[str] = Field(None, alias="slug")
    fangraphs_api_route: Optional[str] = None

    # Position information
    primary_position: Optional[str] = Field(None, alias="primaryPosition")
    eligible_slots: List[str] = Field(default_factory=list, alias="eligibleSlots")

    # Team information
    pro_team: Optional[str] = Field(None, alias="proTeam")
    fantasy_team: Optional[int] = Field(None, alias="fantasyTeam")
    draft_value: Optional[float] = Field(None, alias="draftValue")

    # Status information
    injury_status: Optional[str] = Field(None, alias="injuryStatus")
    status: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def check_not_retired(cls, data: Dict) -> Optional[Dict]:
        """Validate that the player is not retired."""
        if isinstance(data, dict) and data.get("status") == "retired":
            raise ValueError(
                f"Retired players ({data.get('name')}) cannot be serialized"
            )
        return data

    injured: bool = False
    active: bool = False

    # Physical attributes
    weight: Optional[float] = None
    display_weight: Optional[str] = Field(None, alias="displayWeight")
    height: Optional[int] = None
    display_height: Optional[str] = Field(None, alias="displayHeight")

    # Playing characteristics
    bats: Optional[str] = None
    throws: Optional[str] = None

    # Biographical information
    date_of_birth: Optional[str] = Field(None, alias="dateOfBirth")
    birth_place: Optional[BirthPlace] = Field(None, alias="birthPlace")
    debut_year: Optional[int] = Field(None, alias="debutYear")

    # Jersey information
    @field_validator("jersey", mode="before")
    @classmethod
    def normalize_jersey(cls, value: Any) -> Any:
        """Normalize jersey values before type coercion."""
        if value is None or value == "":
            return None
        if isinstance(value, str):
            value = value.strip()
            if value.isdigit():
                value = int(value)
        return value

    jersey: Optional[int] = None

    # Media information
    headshot: Optional[str] = None

    # News items from ESPN Fantasy news API (Rotowire notes)
    news: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = ConfigDict(
        populate_by_name=True, arbitrary_types_allowed=True, str_strip_whitespace=True
    )

    def merge_fangraphs_data(self, data: Optional[FangraphsPlayerModel] = None) -> None:
        """
        Merges data from FanGraphs API into this player model.

        Args:
            data: Dictionary containing FanGraphs player data

        Note:
            This method does not process projections, as those are stored separately.
        """
        self.id_fangraphs = data.playerid if data else None
        self.id_xmlbam = data.xmlbam_id if data else None
        self.name_ascii = data.ascii_name if data else None
        self.fangraphs_api_route = data.stats_api if data else None
