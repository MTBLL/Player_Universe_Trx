from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SavantBaseStats(BaseModel):
    """Base statistics common to both batters and pitchers in Savant data."""

    model_config = ConfigDict(populate_by_name=True)

    # Batting statistics
    BABIP: Optional[float] = Field(default=None, description="Batting Average on Balls In Play")
    BB: Optional[int] = Field(default=None, description="Walks")
    BB_pct: Optional[float] = Field(default=None, alias="BB%", description="Walk percentage")
    BBdist: Optional[int] = Field(default=None, description="Walk distance")
    BIP: Optional[int] = Field(default=None, description="Balls In Play")
    ISO: Optional[float] = Field(default=None, description="Isolated Power")
    K: Optional[int] = Field(default=None, description="Strikeouts")
    K_pct: Optional[float] = Field(default=None, alias="K%", description="Strikeout percentage")
    OBP: Optional[float] = Field(default=None, description="On-Base Percentage")
    SLG: Optional[float] = Field(default=None, description="Slugging Percentage")

    # Contact metrics
    adj_exit_velo: Optional[float] = Field(default=None, description="Adjusted exit velocity")
    exit_velo: Optional[float] = Field(default=None, description="Exit velocity")
    launch_angle: Optional[float] = Field(default=None, description="Launch angle")
    percieved_velo: Optional[float] = Field(default=None, description="Perceived velocity")

    # Plate discipline
    swings: Optional[int] = Field(default=None, description="Number of swings")
    takes: Optional[int] = Field(default=None, description="Number of takes")
    whiffs: Optional[int] = Field(default=None, description="Number of whiffs")
    swing_miss_pct: Optional[float] = Field(default=None, description="Swing and miss percentage")

    # Advanced metrics
    barrels_total: Optional[int] = Field(default=None, description="Total barrels")
    run_exp: Optional[float] = Field(default=None, description="Run expectancy")
    rate_ideal_attack_angle: Optional[float] = Field(default=None, description="Rate of ideal attack angle")
    wOBA: Optional[float] = Field(default=None, description="Weighted On-Base Average")
    wOBAdiff: Optional[float] = Field(default=None, description="wOBA differential")
    xAVG: Optional[float] = Field(default=None, description="Expected batting average")
    xAVGdiff: Optional[float] = Field(default=None, description="Expected AVG differential")
    xOBP: Optional[float] = Field(default=None, description="Expected on-base percentage")
    xOBPdiff: Optional[float] = Field(default=None, description="Expected OBP differential")
    xSLG: Optional[float] = Field(default=None, description="Expected slugging percentage")
    xSLGdiff: Optional[float] = Field(default=None, description="Expected SLG differential")
    xwOBA: Optional[float] = Field(default=None, description="Expected weighted on-base average")


class SavantPlayerModel(BaseModel):
    """Base Savant player model with common fields for all player types."""

    model_config = ConfigDict(populate_by_name=True)

    # Player identification
    player_id: int = Field(description="Savant player ID")
    name: str = Field(description="Player name in 'Last, First' format")
    first_name: str
    last_name: str
    name_ascii: str = Field(description="ASCII name in 'First Last' format")
    slug: str

    # Pitch counts
    pitches: int = Field(description="Number of pitches in sample")
    total_pitches: int = Field(description="Total pitches")
    pitch_percent: float = Field(description="Percentage of total pitches")
