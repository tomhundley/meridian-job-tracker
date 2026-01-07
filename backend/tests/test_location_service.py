"""Tests for location validation service."""

import pytest

from src.services.location_service import (
    extract_states_from_text,
    parse_allowed_states,
    validate_location_compatibility,
    extract_user_state,
)


class TestExtractStatesFromText:
    """Tests for extract_states_from_text function."""

    def test_comma_separated_states(self):
        result = extract_states_from_text("CT, MA, NH, NJ, NY")
        assert set(result) == {"CT", "MA", "NH", "NJ", "NY"}

    def test_single_state(self):
        result = extract_states_from_text("CA")
        assert result == ["CA"]

    def test_state_names(self):
        # Single-word state names work, multi-word names like "New York" don't
        result = extract_states_from_text("California, Texas, Florida")
        assert set(result) == {"CA", "TX", "FL"}

    def test_mixed_case(self):
        result = extract_states_from_text("ca, TX, florida")
        assert set(result) == {"CA", "TX", "FL"}

    def test_with_or_conjunction(self):
        result = extract_states_from_text("CA, NY, or TX")
        assert set(result) == {"CA", "NY", "TX"}

    def test_empty_string(self):
        result = extract_states_from_text("")
        assert result == []

    def test_invalid_states_ignored(self):
        result = extract_states_from_text("CA, XX, NY, ZZ")
        assert set(result) == {"CA", "NY"}


class TestParseAllowedStates:
    """Tests for parse_allowed_states function."""

    def test_remote_with_state_list_in_parentheses(self):
        result = parse_allowed_states("Remote US (CT, MA, NH, NJ, NY)")
        assert set(result) == {"CT", "MA", "NH", "NJ", "NY"}

    def test_remote_no_restrictions(self):
        assert parse_allowed_states("Remote US") is None
        assert parse_allowed_states("Remote") is None
        assert parse_allowed_states("United States") is None

    def test_remote_us_parentheses_only_us(self):
        assert parse_allowed_states("Remote (US)") is None
        assert parse_allowed_states("Remote (USA)") is None

    def test_remote_only_pattern(self):
        result = parse_allowed_states("Remote - CA, NY only")
        assert set(result) == {"CA", "NY"}

    def test_remote_colon_pattern(self):
        result = parse_allowed_states("Remote: CA, TX, NY")
        assert set(result) == {"CA", "TX", "NY"}

    def test_empty_location(self):
        assert parse_allowed_states("") is None
        assert parse_allowed_states(None) is None

    def test_specific_city_state(self):
        # Non-remote explicit locations should return None (no restrictions parsed)
        assert parse_allowed_states("San Francisco, CA") is None
        assert parse_allowed_states("New York, NY") is None


class TestValidateLocationCompatibility:
    """Tests for validate_location_compatibility function."""

    def test_hybrid_always_compatible(self):
        result = validate_location_compatibility("San Francisco, CA", "hybrid")
        assert result.is_compatible is True
        assert result.reason is None

    def test_on_site_always_compatible(self):
        result = validate_location_compatibility("New York, NY", "on_site")
        assert result.is_compatible is True
        assert result.reason is None

    def test_no_work_type_always_compatible(self):
        result = validate_location_compatibility("San Francisco, CA", None)
        assert result.is_compatible is True

    def test_remote_with_ga_allowed(self):
        result = validate_location_compatibility("Remote US (GA, FL, TX)", "remote")
        assert result.is_compatible is True
        assert result.user_state == "GA"

    def test_remote_without_ga_incompatible(self):
        result = validate_location_compatibility(
            "Remote US (CT, MA, NH, NJ, NY)", "remote"
        )
        assert result.is_compatible is False
        assert result.user_state == "GA"
        assert "GA" in result.reason
        assert result.allowed_states is not None
        assert set(result.allowed_states) == {"CT", "MA", "NH", "NJ", "NY"}

    def test_remote_no_restrictions_compatible(self):
        result = validate_location_compatibility("Remote US", "remote")
        assert result.is_compatible is True
        assert result.allowed_states is None

    def test_remote_empty_location_compatible(self):
        result = validate_location_compatibility("", "remote")
        assert result.is_compatible is True

    def test_remote_none_location_compatible(self):
        result = validate_location_compatibility(None, "remote")
        assert result.is_compatible is True


class TestExtractUserState:
    """Tests for extract_user_state function."""

    def test_returns_ga(self):
        # Currently hardcoded to GA
        assert extract_user_state() == "GA"


class TestRealWorldLocations:
    """Test with real-world location strings from job postings."""

    def test_foley_location(self):
        """Test the actual Foley job location that caused the issue."""
        result = validate_location_compatibility(
            "Remote US (CT, MA, NH, NJ, NY)", "remote"
        )
        assert result.is_compatible is False
        assert "CT, MA, NH, NJ, NY" in result.reason or all(
            s in str(result.allowed_states) for s in ["CT", "MA", "NH", "NJ", "NY"]
        )

    def test_typical_remote_us(self):
        result = validate_location_compatibility("Remote, United States", "remote")
        assert result.is_compatible is True

    def test_usa_remote(self):
        result = validate_location_compatibility("USA (Remote)", "remote")
        assert result.is_compatible is True
