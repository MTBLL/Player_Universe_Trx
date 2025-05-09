from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


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
    name_ascii: Optional[str] = None

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

    # Team information
    pro_team: Optional[str] = Field(None, alias="proTeam")

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
    jersey: Optional[int] = None

    # Media information
    headshot: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True, arbitrary_types_allowed=True, str_strip_whitespace=True
    )

    @classmethod
    def model_validate(cls, obj: Dict, **kwargs: Any):
        """
        Custom validation to handle specific data formatting issues.

        - Converts empty string jersey numbers to None
        - Converts string jersey numbers to integers when possible
        - Skip retired players from being serialized
        """
        # Check if player is retired and skip serialization
        if obj.get("status") == "retired":
            # Returning None would not be consistent with Pydantic's behavior
            # so we raise a ValueError to indicate this player should be skipped
            raise ValueError(f"Retired player ({obj.get('name', 'unknown')}) skipped")

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

    def name_contains_first_and_last(self) -> bool:
        """
        Check if full name contains both first and last name components.

        Handles edge cases like middle initials or suffixes:
        - "Michael A. Taylor" contains both "Michael" and "Taylor"
        - "Ken Griffey Jr." contains both "Ken" and "Griffey"

        Returns:
            bool: True if both first and last name are found in the full name
        """
        if not all([self.name, self.first_name, self.last_name]):
            return False

        # Check if both first and last name are contained within the full name
        assert self.name and self.first_name and self.last_name
        return self.first_name in self.name and self.last_name in self.name

    def to_player_dict(self) -> dict:
        """
        Convert PlayerModel to a dictionary ready for Player class initialization.

        Note: Retired players will be filtered out before this method is called.
        """
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

    def _from_json(self, data: Dict) -> NotImplementedError:
        raise NotImplementedError("_from_json method is not implemented yet.")

    def merge_fangraphs_data(self, data: dict) -> None:
        """
        Merges data from FanGraphs API into this player model.

        Args:
            data: Dictionary containing FanGraphs player data

        Note:
            This method does not process projections, as those are stored separately.
        """
        for key, value in data.items():
            match key:
                case "playerid":
                    self.id_fangraphs = value
                case "xmlbam_id":
                    self.id_xmlbam = value
                case "name":
                    if not self.name_nonascii:
                        self.name_nonascii = value
                case "ascii_name":
                    if not self.name_ascii:
                        self.name_ascii = value
                case "slug":
                    self.slug_fangraphs = value
                case "stats_api":
                    self.fangraphs_api_route = value
                case _:
                    pass  # Ignore other fields
