"""Date utility functions for calendar event processing.

This module provides timezone-aware datetime parsing and computation functions
for enhancing calendar event responses with computed day-of-week and date information.
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


def parse_calendar_datetime(
    datetime_str: str, timezone_str: Optional[str] = None
) -> Optional[datetime]:
    """Parse ISO datetime string with timezone information.

    Args:
        datetime_str: ISO format datetime string (e.g., '2025-09-27T12:30:00-04:00')
        timezone_str: Optional timezone string (e.g., 'America/Toronto')

    Returns:
        Timezone-aware datetime object, or None if parsing fails

    Raises:
        ValueError: If datetime string is invalid or timezone is not recognized
    """
    if not datetime_str:
        raise ValueError("datetime_str cannot be empty")

    try:
        # Handle ISO format with timezone offset (e.g., '2025-09-27T12:30:00-04:00')
        if datetime_str.endswith("Z"):
            # UTC timezone
            dt = datetime.fromisoformat(datetime_str[:-1])
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))
        elif (
            "+" in datetime_str[-6:]
            or datetime_str[-6:-3] == "-"
            and datetime_str[-3] == ":"
        ):
            # Has timezone offset
            dt = datetime.fromisoformat(datetime_str)
        else:
            # No timezone info, use provided timezone or default to UTC
            dt = datetime.fromisoformat(datetime_str)
            if timezone_str:
                dt = dt.replace(tzinfo=ZoneInfo(timezone_str))
            else:
                dt = dt.replace(tzinfo=ZoneInfo("UTC"))

        return dt

    except (ValueError, KeyError) as e:
        logger.error(
            f"Failed to parse datetime '{datetime_str}' with timezone '{timezone_str}': {e}"
        )
        raise ValueError(f"Invalid datetime format: {datetime_str}")


def get_day_of_week(dt: datetime) -> str:
    """Get the day of the week name for a datetime object.

    Args:
        dt: Timezone-aware datetime object

    Returns:
        Day name (e.g., 'Saturday', 'Monday')

    Raises:
        ValueError: If datetime object is None or not timezone-aware
    """
    if dt is None:
        raise ValueError("datetime object cannot be None")

    if dt.tzinfo is None:
        raise ValueError("datetime object must be timezone-aware")

    try:
        return dt.strftime("%A")
    except Exception as e:
        logger.error(f"Failed to get day of week for {dt}: {e}")
        raise ValueError(f"Failed to format day of week: {e}")


def get_date_string(dt: datetime) -> str:
    """Get the date string in YYYY-MM-DD format.

    Args:
        dt: Timezone-aware datetime object

    Returns:
        Date string in YYYY-MM-DD format

    Raises:
        ValueError: If datetime object is None or not timezone-aware
    """
    if dt is None:
        raise ValueError("datetime object cannot be None")

    if dt.tzinfo is None:
        raise ValueError("datetime object must be timezone-aware")

    try:
        return dt.strftime("%Y-%m-%d")
    except Exception as e:
        logger.error(f"Failed to get date string for {dt}: {e}")
        raise ValueError(f"Failed to format date string: {e}")


def calculate_duration(start_dt: datetime, end_dt: datetime) -> str:
    """Calculate human-readable duration between two datetime objects.

    Args:
        start_dt: Start datetime (timezone-aware)
        end_dt: End datetime (timezone-aware)

    Returns:
        Human-readable duration string (e.g., '30 minutes', '2 hours', '1 day 3 hours')

    Raises:
        ValueError: If datetime objects are None, not timezone-aware, or end is before start
    """
    if start_dt is None or end_dt is None:
        raise ValueError("datetime objects cannot be None")

    if start_dt.tzinfo is None or end_dt.tzinfo is None:
        raise ValueError("datetime objects must be timezone-aware")

    if end_dt < start_dt:
        raise ValueError("end_dt must be after start_dt")

    try:
        duration = end_dt - start_dt
        total_seconds = int(duration.total_seconds())

        if total_seconds == 0:
            return "0 minutes"

        days = total_seconds // (24 * 3600)
        hours = (total_seconds % (24 * 3600)) // 3600
        minutes = (total_seconds % 3600) // 60

        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")

        if not parts:
            return "less than 1 minute"

        return " ".join(parts)

    except Exception as e:
        logger.error(
            f"Failed to calculate duration between {start_dt} and {end_dt}: {e}"
        )
        raise ValueError(f"Failed to calculate duration: {e}")


def spans_multiple_days(start_dt: datetime, end_dt: datetime) -> bool:
    """Check if an event spans multiple calendar days.

    Args:
        start_dt: Start datetime (timezone-aware)
        end_dt: End datetime (timezone-aware)

    Returns:
        True if event spans multiple days, False otherwise

    Raises:
        ValueError: If datetime objects are None, not timezone-aware, or end is before start
    """
    if start_dt is None or end_dt is None:
        raise ValueError("datetime objects cannot be None")

    if start_dt.tzinfo is None or end_dt.tzinfo is None:
        raise ValueError("datetime objects must be timezone-aware")

    if end_dt < start_dt:
        raise ValueError("end_dt must be after start_dt")

    try:
        return start_dt.date() != end_dt.date()
    except Exception as e:
        logger.error(f"Failed to check if event spans multiple days: {e}")
        raise ValueError(f"Failed to check multiple days: {e}")


def add_computed_fields(event: Dict[str, Any]) -> Dict[str, Any]:
    """Add computed fields to a calendar event dictionary.

    Args:
        event: Calendar event dictionary with 'start' and 'end' fields

    Returns:
        Event dictionary with added 'computed' field containing:
        - startDay: Day of week for start date
        - endDay: Day of week for end date
        - startDate: Date string for start date (YYYY-MM-DD)
        - endDate: Date string for end date (YYYY-MM-DD)
        - duration: Human-readable duration string
        - spansMultipleDays: Boolean indicating if event spans multiple days

    Raises:
        ValueError: If event structure is invalid or datetime parsing fails
    """
    if not isinstance(event, dict):
        raise ValueError("event must be a dictionary")

    if "start" not in event or "end" not in event:
        raise ValueError("event must have 'start' and 'end' fields")

    try:
        # Extract start datetime info
        start_info = event["start"]
        start_datetime_str = start_info.get("dateTime")
        start_timezone = start_info.get("timeZone")

        # Extract end datetime info
        end_info = event["end"]
        end_datetime_str = end_info.get("dateTime")
        end_timezone = end_info.get("timeZone")

        if not start_datetime_str or not end_datetime_str:
            raise ValueError("start and end must have 'dateTime' fields")

        # Parse datetimes
        start_dt = parse_calendar_datetime(start_datetime_str, start_timezone)
        end_dt = parse_calendar_datetime(end_datetime_str, end_timezone)

        # Calculate computed fields
        computed = {
            "startDay": get_day_of_week(start_dt),
            "endDay": get_day_of_week(end_dt),
            "startDate": get_date_string(start_dt),
            "endDate": get_date_string(end_dt),
            "duration": calculate_duration(start_dt, end_dt),
            "spansMultipleDays": spans_multiple_days(start_dt, end_dt),
        }

        # Add computed fields to event (create copy to avoid mutation)
        enhanced_event = event.copy()
        enhanced_event["computed"] = computed

        return enhanced_event

    except Exception as e:
        logger.error(
            f"Failed to add computed fields to event {event.get('id', 'unknown')}: {e}"
        )
        raise ValueError(f"Failed to add computed fields: {e}")
