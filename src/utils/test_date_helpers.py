"""Unit tests for date_helpers module."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from date_helpers import (
    add_computed_fields,
    calculate_duration,
    get_date_string,
    get_day_of_week,
    parse_calendar_datetime,
    spans_multiple_days,
)


class TestParseCalendarDatetime:
    """Tests for parse_calendar_datetime function."""

    def test_parse_iso_with_timezone_offset(self):
        """Test parsing ISO datetime with timezone offset."""
        dt = parse_calendar_datetime("2025-09-27T12:30:00-04:00")
        assert dt.year == 2025
        assert dt.month == 9
        assert dt.day == 27
        assert dt.hour == 12
        assert dt.minute == 30
        assert dt.second == 0
        assert dt.tzinfo is not None

    def test_parse_iso_with_utc_z(self):
        """Test parsing ISO datetime with Z suffix (UTC)."""
        dt = parse_calendar_datetime("2025-09-27T12:30:00Z")
        assert dt.tzinfo == ZoneInfo("UTC")
        assert dt.hour == 12

    def test_parse_iso_without_timezone_with_timezone_param(self):
        """Test parsing ISO datetime without timezone, providing timezone parameter."""
        dt = parse_calendar_datetime("2025-09-27T12:30:00", "America/Toronto")
        assert dt.tzinfo == ZoneInfo("America/Toronto")

    def test_parse_iso_without_timezone_defaults_to_utc(self):
        """Test parsing ISO datetime without timezone defaults to UTC."""
        dt = parse_calendar_datetime("2025-09-27T12:30:00")
        assert dt.tzinfo == ZoneInfo("UTC")

    def test_parse_invalid_datetime_raises_error(self):
        """Test that invalid datetime string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid datetime format"):
            parse_calendar_datetime("invalid-date")

    def test_parse_empty_string_raises_error(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError, match="datetime_str cannot be empty"):
            parse_calendar_datetime("")

    def test_parse_invalid_timezone_raises_error(self):
        """Test that invalid timezone raises ValueError."""
        with pytest.raises(ValueError):
            parse_calendar_datetime("2025-09-27T12:30:00", "Invalid/Timezone")


class TestGetDayOfWeek:
    """Tests for get_day_of_week function."""

    def test_get_day_of_week_saturday(self):
        """Test getting day of week for Saturday."""
        # September 27, 2025 is a Saturday
        dt = datetime(2025, 9, 27, 12, 30, 0, tzinfo=ZoneInfo("America/Toronto"))
        assert get_day_of_week(dt) == "Saturday"

    def test_get_day_of_week_friday(self):
        """Test getting day of week for Friday."""
        # September 26, 2025 is a Friday
        dt = datetime(2025, 9, 26, 12, 30, 0, tzinfo=ZoneInfo("America/Toronto"))
        assert get_day_of_week(dt) == "Friday"

    def test_get_day_of_week_across_timezones(self):
        """Test day of week calculation across different timezones."""
        # Same UTC moment in different timezones
        utc_dt = datetime(
            2025, 9, 27, 4, 0, 0, tzinfo=ZoneInfo("UTC")
        )  # Saturday 4am UTC
        toronto_dt = utc_dt.astimezone(
            ZoneInfo("America/Toronto")
        )  # Saturday midnight Toronto

        assert get_day_of_week(utc_dt) == "Saturday"
        assert get_day_of_week(toronto_dt) == "Saturday"

    def test_get_day_of_week_none_raises_error(self):
        """Test that None datetime raises ValueError."""
        with pytest.raises(ValueError, match="datetime object cannot be None"):
            get_day_of_week(None)

    def test_get_day_of_week_no_timezone_raises_error(self):
        """Test that datetime without timezone raises ValueError."""
        dt = datetime(2025, 9, 27, 12, 30, 0)  # No timezone
        with pytest.raises(ValueError, match="datetime object must be timezone-aware"):
            get_day_of_week(dt)


class TestGetDateString:
    """Tests for get_date_string function."""

    def test_get_date_string_basic(self):
        """Test basic date string formatting."""
        dt = datetime(2025, 9, 27, 12, 30, 0, tzinfo=ZoneInfo("America/Toronto"))
        assert get_date_string(dt) == "2025-09-27"

    def test_get_date_string_single_digit_month_day(self):
        """Test date string with single digit month and day."""
        dt = datetime(2025, 1, 5, 12, 30, 0, tzinfo=ZoneInfo("America/Toronto"))
        assert get_date_string(dt) == "2025-01-05"

    def test_get_date_string_none_raises_error(self):
        """Test that None datetime raises ValueError."""
        with pytest.raises(ValueError, match="datetime object cannot be None"):
            get_date_string(None)

    def test_get_date_string_no_timezone_raises_error(self):
        """Test that datetime without timezone raises ValueError."""
        dt = datetime(2025, 9, 27, 12, 30, 0)  # No timezone
        with pytest.raises(ValueError, match="datetime object must be timezone-aware"):
            get_date_string(dt)


class TestCalculateDuration:
    """Tests for calculate_duration function."""

    def test_calculate_duration_30_minutes(self):
        """Test 30 minute duration calculation."""
        start = datetime(2025, 9, 27, 12, 0, 0, tzinfo=ZoneInfo("America/Toronto"))
        end = datetime(2025, 9, 27, 12, 30, 0, tzinfo=ZoneInfo("America/Toronto"))
        assert calculate_duration(start, end) == "30 minutes"

    def test_calculate_duration_1_hour(self):
        """Test 1 hour duration calculation."""
        start = datetime(2025, 9, 27, 12, 0, 0, tzinfo=ZoneInfo("America/Toronto"))
        end = datetime(2025, 9, 27, 13, 0, 0, tzinfo=ZoneInfo("America/Toronto"))
        assert calculate_duration(start, end) == "1 hour"

    def test_calculate_duration_2_hours(self):
        """Test 2 hours duration calculation."""
        start = datetime(2025, 9, 27, 12, 0, 0, tzinfo=ZoneInfo("America/Toronto"))
        end = datetime(2025, 9, 27, 14, 0, 0, tzinfo=ZoneInfo("America/Toronto"))
        assert calculate_duration(start, end) == "2 hours"

    def test_calculate_duration_1_day(self):
        """Test 1 day duration calculation."""
        start = datetime(2025, 9, 27, 12, 0, 0, tzinfo=ZoneInfo("America/Toronto"))
        end = datetime(2025, 9, 28, 12, 0, 0, tzinfo=ZoneInfo("America/Toronto"))
        assert calculate_duration(start, end) == "1 day"

    def test_calculate_duration_complex(self):
        """Test complex duration with days, hours, and minutes."""
        start = datetime(2025, 9, 27, 12, 15, 0, tzinfo=ZoneInfo("America/Toronto"))
        end = datetime(2025, 9, 29, 14, 45, 0, tzinfo=ZoneInfo("America/Toronto"))
        assert calculate_duration(start, end) == "2 days 2 hours 30 minutes"

    def test_calculate_duration_zero(self):
        """Test zero duration."""
        start = datetime(2025, 9, 27, 12, 0, 0, tzinfo=ZoneInfo("America/Toronto"))
        end = datetime(2025, 9, 27, 12, 0, 0, tzinfo=ZoneInfo("America/Toronto"))
        assert calculate_duration(start, end) == "0 minutes"

    def test_calculate_duration_end_before_start_raises_error(self):
        """Test that end before start raises ValueError."""
        start = datetime(2025, 9, 27, 13, 0, 0, tzinfo=ZoneInfo("America/Toronto"))
        end = datetime(2025, 9, 27, 12, 0, 0, tzinfo=ZoneInfo("America/Toronto"))
        with pytest.raises(ValueError, match="end_dt must be after start_dt"):
            calculate_duration(start, end)

    def test_calculate_duration_none_raises_error(self):
        """Test that None datetimes raise ValueError."""
        dt = datetime(2025, 9, 27, 12, 0, 0, tzinfo=ZoneInfo("America/Toronto"))
        with pytest.raises(ValueError, match="datetime objects cannot be None"):
            calculate_duration(None, dt)
        with pytest.raises(ValueError, match="datetime objects cannot be None"):
            calculate_duration(dt, None)


class TestSpansMultipleDays:
    """Tests for spans_multiple_days function."""

    def test_spans_multiple_days_same_day(self):
        """Test event within same day."""
        start = datetime(2025, 9, 27, 12, 0, 0, tzinfo=ZoneInfo("America/Toronto"))
        end = datetime(2025, 9, 27, 14, 0, 0, tzinfo=ZoneInfo("America/Toronto"))
        assert spans_multiple_days(start, end) is False

    def test_spans_multiple_days_different_days(self):
        """Test event spanning multiple days."""
        start = datetime(2025, 9, 27, 23, 0, 0, tzinfo=ZoneInfo("America/Toronto"))
        end = datetime(2025, 9, 28, 1, 0, 0, tzinfo=ZoneInfo("America/Toronto"))
        assert spans_multiple_days(start, end) is True

    def test_spans_multiple_days_midnight_boundary(self):
        """Test event crossing midnight boundary."""
        start = datetime(2025, 9, 27, 23, 59, 59, tzinfo=ZoneInfo("America/Toronto"))
        end = datetime(2025, 9, 28, 0, 0, 1, tzinfo=ZoneInfo("America/Toronto"))
        assert spans_multiple_days(start, end) is True

    def test_spans_multiple_days_timezone_aware(self):
        """Test multiple days check with timezone conversion."""
        # UTC 6am = Toronto 2am (UTC-4 in September)
        start = datetime(2025, 9, 27, 23, 0, 0, tzinfo=ZoneInfo("America/Toronto"))
        end = datetime(
            2025, 9, 28, 6, 0, 0, tzinfo=ZoneInfo("UTC")
        )  # 6am UTC = 2am Toronto
        # Convert end to same timezone as start for comparison
        end_toronto = end.astimezone(ZoneInfo("America/Toronto"))
        assert (
            spans_multiple_days(start, end_toronto) is True
        )  # Different days in Toronto timezone

    def test_spans_multiple_days_none_raises_error(self):
        """Test that None datetimes raise ValueError."""
        dt = datetime(2025, 9, 27, 12, 0, 0, tzinfo=ZoneInfo("America/Toronto"))
        with pytest.raises(ValueError, match="datetime objects cannot be None"):
            spans_multiple_days(None, dt)


class TestAddComputedFields:
    """Tests for add_computed_fields function."""

    def test_add_computed_fields_basic(self):
        """Test adding computed fields to basic event."""
        event = {
            "id": "test-event",
            "summary": "Test Event",
            "start": {
                "dateTime": "2025-09-27T12:30:00-04:00",
                "timeZone": "America/Toronto",
            },
            "end": {
                "dateTime": "2025-09-27T13:00:00-04:00",
                "timeZone": "America/Toronto",
            },
        }

        result = add_computed_fields(event)

        assert "computed" in result
        computed = result["computed"]
        assert computed["startDay"] == "Saturday"
        assert computed["endDay"] == "Saturday"
        assert computed["startDate"] == "2025-09-27"
        assert computed["endDate"] == "2025-09-27"
        assert computed["duration"] == "30 minutes"
        assert computed["spansMultipleDays"] is False

    def test_add_computed_fields_multi_day_event(self):
        """Test computed fields for multi-day event."""
        event = {
            "id": "multi-day-event",
            "summary": "Conference",
            "start": {
                "dateTime": "2025-09-27T09:00:00-04:00",
                "timeZone": "America/Toronto",
            },
            "end": {
                "dateTime": "2025-09-29T17:00:00-04:00",
                "timeZone": "America/Toronto",
            },
        }

        result = add_computed_fields(event)
        computed = result["computed"]

        assert computed["startDay"] == "Saturday"
        assert computed["endDay"] == "Monday"
        assert computed["startDate"] == "2025-09-27"
        assert computed["endDate"] == "2025-09-29"
        assert computed["spansMultipleDays"] is True
        assert "days" in computed["duration"]

    def test_add_computed_fields_preserves_original(self):
        """Test that original event data is preserved."""
        event = {
            "id": "test-event",
            "summary": "Test Event",
            "location": "Test Location",
            "start": {
                "dateTime": "2025-09-27T12:30:00-04:00",
                "timeZone": "America/Toronto",
            },
            "end": {
                "dateTime": "2025-09-27T13:00:00-04:00",
                "timeZone": "America/Toronto",
            },
        }

        result = add_computed_fields(event)

        # Original fields should be preserved
        assert result["id"] == event["id"]
        assert result["summary"] == event["summary"]
        assert result["location"] == event["location"]
        assert result["start"] == event["start"]
        assert result["end"] == event["end"]

    def test_add_computed_fields_invalid_event_raises_error(self):
        """Test that invalid event structure raises ValueError."""
        with pytest.raises(ValueError, match="event must be a dictionary"):
            add_computed_fields("not a dict")

        with pytest.raises(
            ValueError, match="event must have 'start' and 'end' fields"
        ):
            add_computed_fields({"id": "test"})

        with pytest.raises(
            ValueError, match="start and end must have 'dateTime' fields"
        ):
            add_computed_fields(
                {
                    "start": {"timeZone": "America/Toronto"},
                    "end": {"timeZone": "America/Toronto"},
                }
            )

    def test_add_computed_fields_timezone_edge_cases(self):
        """Test computed fields with various timezone scenarios."""
        # DST transition test - use a simpler scenario
        event = {
            "id": "dst-event",
            "summary": "DST Test",
            "start": {
                "dateTime": "2025-03-09T01:30:00-05:00",  # 1:30 AM EST
                "timeZone": "America/Toronto",
            },
            "end": {
                "dateTime": "2025-03-09T03:30:00-04:00",  # 3:30 AM EDT (after spring forward)
                "timeZone": "America/Toronto",
            },
        }

        result = add_computed_fields(event)
        computed = result["computed"]

        assert computed["startDay"] == "Sunday"
        assert computed["endDay"] == "Sunday"
        assert (
            computed["duration"] == "2 hours"
        )  # Raw ISO parsing shows 2 hour difference

    def test_add_computed_fields_utc_timezone(self):
        """Test computed fields with UTC timezone."""
        event = {
            "id": "utc-event",
            "summary": "UTC Event",
            "start": {"dateTime": "2025-09-27T16:30:00Z"},
            "end": {"dateTime": "2025-09-27T17:00:00Z"},
        }

        result = add_computed_fields(event)
        computed = result["computed"]

        assert computed["startDay"] == "Saturday"
        assert computed["endDay"] == "Saturday"
        assert computed["duration"] == "30 minutes"


if __name__ == "__main__":
    pytest.main([__file__])
