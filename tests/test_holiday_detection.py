"""Tests for holiday detection and smart scheduling functionality."""

import sys
from datetime import date
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, "src")

from tools.calendar import GoogleCalendarTools  # noqa: E402
from utils.holiday_helpers import (  # noqa: E402
    find_next_working_day,
    get_holiday_name,
    is_holiday,
    is_working_day,
    parse_date_from_iso,
    suggest_alternative_date,
)


class TestHolidayHelpers:
    """Test holiday detection utility functions."""

    def test_is_holiday_christmas(self):
        """Test that Christmas is detected as a holiday."""
        christmas = date(2025, 12, 25)
        assert is_holiday(christmas) is True

    def test_is_holiday_us_independence_day(self):
        """Test that July 4th is detected as a US holiday."""
        july_4th = date(2025, 7, 4)
        assert is_holiday(july_4th) is True

    def test_is_holiday_canada_day(self):
        """Test that Canada Day is detected as a Canadian holiday."""
        canada_day = date(2025, 7, 1)
        assert is_holiday(canada_day) is True

    def test_is_holiday_regular_weekday(self):
        """Test that a regular weekday is not a holiday."""
        regular_day = date(2025, 10, 15)  # Wednesday
        assert is_holiday(regular_day) is False

    def test_get_holiday_name_christmas(self):
        """Test getting the name of Christmas."""
        christmas = date(2025, 12, 25)
        name = get_holiday_name(christmas)
        assert "Christmas" in name
        assert "US" in name
        assert "Canada" in name  # Observed in both countries

    def test_get_holiday_name_us_only(self):
        """Test getting the name of a US-only holiday."""
        july_4th = date(2025, 7, 4)
        name = get_holiday_name(july_4th)
        assert "Independence Day" in name
        assert "US" in name
        assert "Canada" not in name

    def test_get_holiday_name_canada_only(self):
        """Test getting the name of a Canada-only holiday."""
        canada_day = date(2025, 7, 1)
        name = get_holiday_name(canada_day)
        assert "Canada Day" in name
        assert "Canada" in name
        assert "US" not in name

    def test_get_holiday_name_non_holiday(self):
        """Test that non-holidays return None."""
        regular_day = date(2025, 10, 15)
        assert get_holiday_name(regular_day) is None

    def test_is_working_day_weekday(self):
        """Test that a regular weekday is a working day."""
        wednesday = date(2025, 10, 15)  # Regular Wednesday
        assert is_working_day(wednesday) is True

    def test_is_working_day_saturday(self):
        """Test that Saturday is not a working day."""
        saturday = date(2025, 10, 11)  # Saturday
        assert is_working_day(saturday) is False

    def test_is_working_day_sunday(self):
        """Test that Sunday is not a working day."""
        sunday = date(2025, 10, 12)  # Sunday
        assert is_working_day(sunday) is False

    def test_is_working_day_holiday(self):
        """Test that a holiday is not a working day."""
        christmas = date(2025, 12, 25)
        assert is_working_day(christmas) is False

    def test_find_next_working_day_from_weekday(self):
        """Test finding next working day from a regular weekday."""
        wednesday = date(2025, 10, 15)
        next_day, days_skipped = find_next_working_day(wednesday)
        assert next_day == wednesday
        assert days_skipped == 0

    def test_find_next_working_day_from_friday(self):
        """Test finding next working day from Friday (skips weekend)."""
        friday = date(2025, 10, 10)
        next_day, days_skipped = find_next_working_day(friday)
        assert next_day == friday
        assert days_skipped == 0

    def test_find_next_working_day_from_saturday(self):
        """Test finding next working day from Saturday."""
        saturday = date(2025, 10, 11)
        next_day, days_skipped = find_next_working_day(saturday)
        # Monday Oct 13 is a holiday (Canadian Thanksgiving), so skips to Tuesday
        assert next_day == date(2025, 10, 14)  # Tuesday
        assert days_skipped == 3

    def test_find_next_working_day_from_christmas(self):
        """Test finding next working day from Christmas (Thursday)."""
        christmas = date(2025, 12, 25)  # Thursday
        next_day, days_skipped = find_next_working_day(christmas)
        # Should skip to Monday (skipping Friday, Saturday, Sunday)
        assert next_day == date(2025, 12, 29)
        assert days_skipped == 4

    def test_find_next_working_day_max_days_exceeded(self):
        """Test that ValueError is raised if no working day found within limit."""
        # This would require a very long holiday period
        # For testing, we'll use a small max_days_ahead
        with pytest.raises(ValueError, match="No working day found"):
            find_next_working_day(date(2025, 12, 25), max_days_ahead=2)

    def test_suggest_alternative_date_holiday(self):
        """Test suggesting alternative date for a holiday."""
        christmas = date(2025, 12, 25)
        alternative = suggest_alternative_date(christmas)
        assert alternative is not None
        assert alternative == date(2025, 12, 29)  # Monday
        assert is_working_day(alternative) is True

    def test_suggest_alternative_date_working_day(self):
        """Test that working days return None for alternative."""
        regular_day = date(2025, 10, 15)
        assert suggest_alternative_date(regular_day) is None

    def test_parse_date_from_iso_date_only(self):
        """Test parsing date-only ISO string."""
        date_str = "2025-12-25"
        parsed = parse_date_from_iso(date_str)
        assert parsed == date(2025, 12, 25)

    def test_parse_date_from_iso_datetime(self):
        """Test parsing datetime ISO string."""
        date_str = "2025-12-25T10:00:00"
        parsed = parse_date_from_iso(date_str)
        assert parsed == date(2025, 12, 25)

    def test_parse_date_from_iso_datetime_with_timezone(self):
        """Test parsing datetime ISO string with timezone."""
        date_str = "2025-12-25T10:00:00-05:00"
        parsed = parse_date_from_iso(date_str)
        assert parsed == date(2025, 12, 25)

    def test_parse_date_from_iso_invalid(self):
        """Test that invalid ISO strings raise ValueError."""
        with pytest.raises(ValueError, match="Invalid ISO date string"):
            parse_date_from_iso("not-a-date")


class TestCalendarHolidayIntegration:
    """Test holiday detection integration with calendar event creation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_auth = Mock()
        self.calendar_tools = GoogleCalendarTools(self.mock_auth)

    @patch("tools.calendar.build")
    def test_create_event_blocks_holiday_by_default(self, mock_build):
        """Test that creating an event on a holiday is blocked by default."""
        params = {
            "summary": "Holiday Meeting",
            "start_time": "2025-12-25T10:00:00",  # Christmas
            "end_time": "2025-12-25T11:00:00",
        }

        with pytest.raises(ValueError) as exc_info:
            self.calendar_tools.create_event(params)

        error_msg = str(exc_info.value)
        assert "holiday" in error_msg.lower()
        assert "Christmas" in error_msg
        assert "2025-12-25" in error_msg
        assert "force_holiday_booking" in error_msg

    @patch("tools.calendar.build")
    def test_create_event_suggests_alternative_date(self, mock_build):
        """Test that error message suggests alternative date."""
        params = {
            "summary": "Holiday Meeting",
            "start_time": "2025-12-25T10:00:00",  # Christmas (Thursday)
            "end_time": "2025-12-25T11:00:00",
        }

        with pytest.raises(ValueError) as exc_info:
            self.calendar_tools.create_event(params)

        error_msg = str(exc_info.value)
        assert "2025-12-29" in error_msg  # Next Monday
        assert "Monday" in error_msg

    @patch("tools.calendar.build")
    def test_create_event_allows_force_holiday_booking(self, mock_build):
        """Test that force_holiday_booking bypasses holiday check."""
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock the event creation
        mock_event = {
            "id": "test_event_id",
            "summary": "Holiday Meeting",
            "htmlLink": "https://calendar.google.com/event/test",
            "start": {"dateTime": "2025-12-25T10:00:00"},
            "end": {"dateTime": "2025-12-25T11:00:00"},
            "status": "confirmed",
            "created": "2025-10-18T12:00:00Z",
        }
        mock_service.events().insert().execute.return_value = mock_event

        params = {
            "summary": "Holiday Meeting",
            "start_time": "2025-12-25T10:00:00",  # Christmas
            "end_time": "2025-12-25T11:00:00",
            "force_holiday_booking": True,  # Force booking
        }

        # Should NOT raise ValueError
        result = self.calendar_tools.create_event(params)

        assert result["id"] == "test_event_id"
        assert result["summary"] == "Holiday Meeting"

    @patch("tools.calendar.build")
    def test_create_event_allows_regular_weekday(self, mock_build):
        """Test that regular weekdays are allowed without force flag."""
        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_event = {
            "id": "test_event_id",
            "summary": "Regular Meeting",
            "htmlLink": "https://calendar.google.com/event/test",
            "start": {"dateTime": "2025-10-15T10:00:00"},
            "end": {"dateTime": "2025-10-15T11:00:00"},
            "status": "confirmed",
            "created": "2025-10-18T12:00:00Z",
        }
        mock_service.events().insert().execute.return_value = mock_event

        params = {
            "summary": "Regular Meeting",
            "start_time": "2025-10-15T10:00:00",  # Regular Wednesday
            "end_time": "2025-10-15T11:00:00",
        }

        # Should NOT raise ValueError
        result = self.calendar_tools.create_event(params)

        assert result["id"] == "test_event_id"

    @patch("tools.calendar.build")
    def test_create_event_blocks_us_independence_day(self, mock_build):
        """Test that US Independence Day is blocked."""
        params = {
            "summary": "July 4th Meeting",
            "start_time": "2025-07-04T10:00:00",
            "end_time": "2025-07-04T11:00:00",
        }

        with pytest.raises(ValueError) as exc_info:
            self.calendar_tools.create_event(params)

        error_msg = str(exc_info.value)
        assert "Independence Day" in error_msg

    @patch("tools.calendar.build")
    def test_create_event_blocks_canada_day(self, mock_build):
        """Test that Canada Day is blocked."""
        params = {
            "summary": "Canada Day Meeting",
            "start_time": "2025-07-01T10:00:00",
            "end_time": "2025-07-01T11:00:00",
        }

        with pytest.raises(ValueError) as exc_info:
            self.calendar_tools.create_event(params)

        error_msg = str(exc_info.value)
        assert "Canada Day" in error_msg
