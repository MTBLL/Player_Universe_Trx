from enum import Enum


class MatchConfidence(Enum):
    """Confidence level of a player match."""

    HIGH = 90  # Slug or exact name + team
    MEDIUM = 70  # Exact name or prefix + team
    LOW = 40  # Prefix name or team only
    AMBIGUOUS = 0  # Multiple candidates
    NONE = -1  # No match
