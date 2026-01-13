from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FangraphsBaseProjection(BaseModel):
    """Base projection fields common to both batters and pitchers."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    # Quantile projections (context-specific: wOBA for batters, ERA for pitchers)
    q10: Optional[float] = Field(default=None, description="10th percentile projection")
    q20: Optional[float] = Field(default=None, description="20th percentile projection")
    q30: Optional[float] = Field(default=None, description="30th percentile projection")
    q40: Optional[float] = Field(default=None, description="40th percentile projection")
    q50: Optional[float] = Field(default=None, description="50th percentile projection (median)")
    q60: Optional[float] = Field(default=None, description="60th percentile projection")
    q70: Optional[float] = Field(default=None, description="70th percentile projection")
    q80: Optional[float] = Field(default=None, description="80th percentile projection")
    q90: Optional[float] = Field(default=None, description="90th percentile projection")

    # True talent quantile projections
    tt_q10: Optional[float] = Field(default=None, description="True talent 10th percentile")
    tt_q20: Optional[float] = Field(default=None, description="True talent 20th percentile")
    tt_q30: Optional[float] = Field(default=None, description="True talent 30th percentile")
    tt_q40: Optional[float] = Field(default=None, description="True talent 40th percentile")
    tt_q50: Optional[float] = Field(default=None, description="True talent 50th percentile")
    tt_q60: Optional[float] = Field(default=None, description="True talent 60th percentile")
    tt_q70: Optional[float] = Field(default=None, description="True talent 70th percentile")
    tt_q80: Optional[float] = Field(default=None, description="True talent 80th percentile")
    tt_q90: Optional[float] = Field(default=None, description="True talent 90th percentile")

    # Common statistics
    games: Optional[float] = Field(default=None, alias="G", description="Games played")
    fpts: Optional[float] = Field(default=None, alias="FPTS", description="Fantasy points")
    spts: Optional[float] = Field(default=None, alias="SPTS", description="Standard points")


class FangraphsPlayerModel(BaseModel):
    """Base FanGraphs player model with common fields for all player types."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    # Player identification
    name: str
    ascii_name: Optional[str] = None
    playerid: str = Field(description="FanGraphs player ID")
    xmlbam_id: Optional[int] = Field(default=None, description="MLB official player ID")
    slug: Optional[str] = None
    stats_api: Optional[str] = None

    # Team information
    team: Optional[str] = None
