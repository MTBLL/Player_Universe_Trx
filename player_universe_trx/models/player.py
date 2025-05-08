from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field



class BirthPlace(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None


class StatPeriod(BaseModel):
    points: float = 0.0
    projected_points: float = 0.0
    breakdown: Dict[str, Any] = {}
    projected_breakdown: Dict[str, Any] = {}


class PlayerModel(BaseModel):
    """Pydantic model for baseball player data"""

    # Basic player info
    id_espn: Optional[int] = Field(None, alias="id")
    id_fangraphs: Optional[str] = None
    id_xmlbam: Optional[int] = None
    name: Optional[str] = None
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    name_nonascii: Optional[str] = None

    # Display information
    display_name: Optional[str] = Field(None, alias="displayName")
    short_name: Optional[str] = Field(None, alias="shortName")
    nickname: Optional[str] = None
    slug_espn: Optional[str] = Field(None, alias="slug")
    slug_fangraphs: Optional[str] = None
    fangraphs_api_route: Optional[str] = None

    # Position information
    primary_position: Optional[str] = Field(None, alias="primaryPosition")
    eligible_slots: List[str] = Field(default_factory=list, alias="eligibleSlots")
    position_name: Optional[str] = Field(None, alias="positionName")
    pos: Optional[str] = None

    # Team information
    pro_team: Optional[str] = Field(None, alias="proTeam")

    # Status information
    injury_status: Optional[str] = Field(None, alias="injuryStatus")
    status: Optional[str] = None
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
    jersey: Optional[int] = None

    # Media information
    headshot: Optional[str] = None

    # Statistics
    stats: Dict[Union[int, str], StatPeriod] = Field(default_factory=dict)

    model_config = ConfigDict(
        populate_by_name=True, arbitrary_types_allowed=True, str_strip_whitespace=True
    )
    
    @classmethod
    def model_validate(cls, obj, **kwargs):
        """
        Custom validation to handle specific data formatting issues.
        
        - Converts empty string jersey numbers to None
        - Converts string jersey numbers to integers when possible
        """
        if isinstance(obj, dict):
            obj_copy = obj.copy()
            
            # Handle jersey number conversion
            if "jersey" in obj_copy:
                jersey = obj_copy["jersey"]
                if jersey == "":
                    obj_copy["jersey"] = None
                elif isinstance(jersey, str) and jersey.isdigit():
                    obj_copy["jersey"] = int(jersey)
            
            # Use the standard validation with our modified data
            return super().model_validate(obj_copy, **kwargs)
        
        return super().model_validate(obj, **kwargs)

    def to_player_dict(self) -> dict:
        """Convert PlayerModel to a dictionary ready for Player class initialization"""
        # Convert to dict with all fields - use snake_case
        data = self.model_dump(exclude_none=True)

        # Add a few fields that are necessary for Player initialization
        if self.name:
            data["fullName"] = self.name

        # Process stats into the format expected by Player
        if "stats" in data:
            processed_stats = {}
            for period, stats in data["stats"].items():
                period_stats = {}
                for key, value in stats.items():
                    if isinstance(value, dict):
                        period_stats[key] = value
                    else:
                        period_stats[key] = value
                processed_stats[period] = period_stats
            data["stats"] = processed_stats

        return data

    def _from_json(self, data):
        pass
        
    def merge_fangraphs_data(self, data: dict) -> None:
        """
        Merges data from FanGraphs API into this player model.
        
        Args:
            data: Dictionary containing FanGraphs player data
        
        Note:
            This method does not process projections, as those are stored separately.
        """
        if not isinstance(data, dict):
            return
            
        # Use match/case for better readability and lower complexity
        for key, value in data.items():
            match key:
                case "playerid":
                    self.id_fangraphs = value
                case "xmlbam_id":
                    self.id_xmlbam = value
                case "name":
                    if not self.name:
                        self.name = value
                case "ascii_name":
                    if "name" in data and data["name"] != value:
                        self.name_nonascii = data["name"]
                case "slug":
                    self.slug_fangraphs = value
                case "stats_api":
                    self.fangraphs_api_route = value
                case "team":
                    self.pro_team = value
                # We ignore projections as requested - they'll be stored separately
                case _:
                    pass  # Ignore other fields
