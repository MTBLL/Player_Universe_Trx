from enum import Enum


class MatchMethod(Enum):
    """Method used to match a player between data sources."""

    SLUG = "slug"
    EXACT_NAME = "exact_name"
    PREFIX_NAME = "prefix_name"
    TEAM = "team"
    NONE = "none"
