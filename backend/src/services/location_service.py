"""Location validation service for job compatibility checking."""

import re
from dataclasses import dataclass


# US state abbreviations
US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC",
}

# State name to abbreviation mapping
STATE_NAMES = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
    "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
    "vermont": "VT", "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY", "district of columbia": "DC",
}

# User's location - hardcoded for now, matches resume_service.py
USER_LOCATION = "Alpharetta, GA"
USER_STATE = "GA"


@dataclass
class LocationValidationResult:
    """Result of location validation."""

    is_compatible: bool
    allowed_states: list[str] | None  # None means no restrictions (all US)
    user_state: str
    reason: str | None  # Explanation if incompatible


def extract_user_state() -> str:
    """Extract user's state from profile location."""
    # For now, hardcoded. Could be enhanced to read from resume_service.
    return USER_STATE


def extract_states_from_text(text: str) -> list[str]:
    """Extract state abbreviations from a text string."""
    states = []

    # Split by common separators
    parts = re.split(r"[,\s/]+", text)

    for part in parts:
        # Clean up the part
        clean = part.strip().upper()
        # Skip common words (but note "OR" is Oregon)
        if clean in ["AND", "ONLY", "THE", "IN", "US", "USA"]:
            continue
        # "OR" could be Oregon or conjunction - check context
        if clean == "OR" and len(parts) > 2:
            # Likely a conjunction in a list
            continue
        if clean in US_STATES:
            states.append(clean)
            continue
        # Check full state names
        lower = part.strip().lower()
        if lower in STATE_NAMES:
            states.append(STATE_NAMES[lower])

    return list(set(states))  # Remove duplicates


def parse_allowed_states(location_string: str) -> list[str] | None:
    """
    Parse location string to extract allowed states for remote positions.

    Patterns handled:
    - "Remote US (CT, MA, NH, NJ, NY)" -> ["CT", "MA", "NH", "NJ", "NY"]
    - "Remote - CT, MA, or NY only" -> ["CT", "MA", "NY"]
    - "United States (CA, TX, NY)" -> ["CA", "TX", "NY"]
    - "Remote US" or "Remote" or "United States" -> None (all states allowed)
    - "Remote (US)" -> None (all states allowed)

    Returns None if all US states are allowed, otherwise list of allowed states.
    """
    if not location_string:
        return None

    location_lower = location_string.lower()

    # Check if this is a US remote role
    us_indicators = ["remote", "united states", "usa", "u.s."]
    is_us_remote = any(ind in location_lower for ind in us_indicators)

    if not is_us_remote:
        # Not explicitly a US remote role - could be specific city/state
        # For non-remote-explicit locations, assume no restrictions
        return None

    # Look for state restrictions in parentheses
    # Pattern: "Remote US (CT, MA, NH, NJ, NY)"
    paren_match = re.search(r"\(([^)]+)\)", location_string)
    if paren_match:
        states_text = paren_match.group(1)
        # Check if it's just "(US)" or similar
        if states_text.strip().upper() in ["US", "USA", "U.S.", "UNITED STATES"]:
            return None
        states = extract_states_from_text(states_text)
        if states:
            return states

    # Look for "only" patterns: "Remote - CT, MA, or NY only"
    only_match = re.search(r"[-:]\s*([^-:]+?)\s*only", location_string, re.IGNORECASE)
    if only_match:
        states_text = only_match.group(1)
        states = extract_states_from_text(states_text)
        if states:
            return states

    # Look for explicit state lists after "Remote"
    # Pattern: "Remote: CA, NY, TX" or "Remote - West Coast"
    after_remote = re.search(r"remote\s*[-:]\s*(.+)", location_string, re.IGNORECASE)
    if after_remote:
        states_text = after_remote.group(1)
        # Skip if it's just descriptive text without states
        states = extract_states_from_text(states_text)
        if states:
            return states

    # No restrictions found - all US states allowed
    return None


def validate_location_compatibility(
    location: str | None,
    work_location_type: str | None,
) -> LocationValidationResult:
    """
    Validate if user's location is compatible with job.

    Args:
        location: Job location string (e.g., "Remote US (CT, MA, NH, NJ, NY)")
        work_location_type: WorkLocationType value ("remote", "hybrid", "on_site")

    Returns:
        LocationValidationResult with compatibility status and explanation
    """
    user_state = extract_user_state()

    # For HYBRID and ON_SITE: user is willing to travel anywhere in US
    if work_location_type in ("hybrid", "on_site", None):
        return LocationValidationResult(
            is_compatible=True,
            allowed_states=None,
            user_state=user_state,
            reason=None,
        )

    # For REMOTE: check if user's state is in allowed states
    if work_location_type == "remote":
        allowed_states = parse_allowed_states(location or "")

        if allowed_states is None:
            # No restrictions - all US states allowed
            return LocationValidationResult(
                is_compatible=True,
                allowed_states=None,
                user_state=user_state,
                reason=None,
            )

        if user_state in allowed_states:
            return LocationValidationResult(
                is_compatible=True,
                allowed_states=allowed_states,
                user_state=user_state,
                reason=None,
            )
        else:
            return LocationValidationResult(
                is_compatible=False,
                allowed_states=allowed_states,
                user_state=user_state,
                reason=f"Remote position restricted to {', '.join(sorted(allowed_states))}. User is in {user_state}.",
            )

    # Unknown work location type - assume compatible
    return LocationValidationResult(
        is_compatible=True,
        allowed_states=None,
        user_state=user_state,
        reason=None,
    )


# Convenience alias
location_service = validate_location_compatibility
