import re


def extract_last_name(full_name: str) -> str:
    """
    Extract the last name from a full name, removing suffixes.

    Args:
        full_name: Full player name

    Returns:
        Last name without suffixes
    """
    if not full_name:
        return ""

    # Split the name
    parts = full_name.split()
    if not parts:
        return ""

    # Remove suffix if present
    suffix_pattern = r"^(Jr\.?|Sr\.?|I{2,3}|IV)$"
    if len(parts) > 1 and re.match(suffix_pattern, parts[-1], re.IGNORECASE):
        last_name = parts[-2]
    else:
        last_name = parts[-1]

    return last_name


def extract_first_name(full_name: str) -> str:
    """
    Extract the first name from a full name.

    Args:
        full_name: Full player name

    Returns:
        First name
    """
    if not full_name:
        return ""

    parts = full_name.split()
    if not parts:
        return ""

    return parts[0]
