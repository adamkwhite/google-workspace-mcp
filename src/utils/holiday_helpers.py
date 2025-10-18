"""Holiday detection and smart scheduling utilities.

Provides holiday detection for US and Canadian calendars to support
smart event scheduling that respects regional holidays.
"""

from datetime import date, datetime, timedelta
from typing import Optional, Tuple

from workalendar.america import Ontario
from workalendar.usa import UnitedStates

# Initialize calendar instances
_us_calendar = UnitedStates()
_ca_calendar = Ontario()  # Using Ontario as representative Canadian calendar


def is_holiday(check_date: date) -> bool:
    """Check if a date is a holiday in either US or Canada.

    Args:
        check_date: Date to check

    Returns:
        True if the date is a holiday in US or Canada, False otherwise
    """
    return _us_calendar.is_holiday(check_date) or _ca_calendar.is_holiday(check_date)


def get_holiday_name(check_date: date) -> Optional[str]:
    """Get the name of a holiday if the date is a holiday.

    Args:
        check_date: Date to check

    Returns:
        Holiday name if the date is a holiday, None otherwise.
        If the date is a holiday in both US and Canada, returns both names.
    """
    us_holidays = [
        name for d, name in _us_calendar.holidays(check_date.year) if d == check_date
    ]
    ca_holidays = [
        name for d, name in _ca_calendar.holidays(check_date.year) if d == check_date
    ]

    if us_holidays and ca_holidays:
        return f"{us_holidays[0]} (US), {ca_holidays[0]} (Canada)"
    elif us_holidays:
        return f"{us_holidays[0]} (US)"
    elif ca_holidays:
        return f"{ca_holidays[0]} (Canada)"
    return None


def is_working_day(check_date: date) -> bool:
    """Check if a date is a working day (not weekend or holiday).

    Args:
        check_date: Date to check

    Returns:
        True if the date is a working day, False if weekend or holiday
    """
    # Check if it's a weekend (Saturday=5, Sunday=6)
    if check_date.weekday() in (5, 6):
        return False

    # Check if it's a holiday
    return not is_holiday(check_date)


def find_next_working_day(
    start_date: date, max_days_ahead: int = 14
) -> Tuple[date, int]:
    """Find the next working day (skipping weekends and holidays).

    Args:
        start_date: Date to start searching from
        max_days_ahead: Maximum number of days to search ahead (default: 14)

    Returns:
        Tuple of (next_working_day, days_skipped)

    Raises:
        ValueError: If no working day found within max_days_ahead
    """
    current_date = start_date
    days_checked = 0

    while days_checked <= max_days_ahead:
        if is_working_day(current_date):
            return current_date, days_checked

        current_date += timedelta(days=1)
        days_checked += 1

    raise ValueError(
        f"No working day found within {max_days_ahead} days of {start_date}"
    )


def suggest_alternative_date(requested_date: date) -> Optional[date]:
    """Suggest an alternative date if the requested date is a holiday.

    Args:
        requested_date: The date requested by the user

    Returns:
        Alternative working day if requested date is a holiday, None otherwise
    """
    if not is_holiday(requested_date):
        return None

    try:
        next_working_day, _ = find_next_working_day(requested_date)
        return next_working_day
    except ValueError:
        return None


def parse_date_from_iso(iso_string: str) -> date:
    """Parse a date from ISO format string (YYYY-MM-DD).

    Args:
        iso_string: ISO format date string

    Returns:
        Parsed date object

    Raises:
        ValueError: If the string cannot be parsed
    """
    try:
        # Handle datetime strings (ISO 8601 with time)
        if "T" in iso_string:
            dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
            return dt.date()
        # Handle date-only strings
        return datetime.strptime(iso_string[:10], "%Y-%m-%d").date()
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid ISO date string: {iso_string}") from e
