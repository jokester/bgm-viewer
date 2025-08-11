from typing import Optional
import re
from datetime import datetime, timedelta

import logging

logger = logging.getLogger(__name__)


def launder_date(date: Optional[str], warning=True) -> Optional[str]:
    if date is None:
        return None

    # Strip whitespace
    cleaned = date.strip()

    # Return None if empty or only whitespace
    if not cleaned:
        return None

    # Month name mapping
    month_names = {
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12',
        'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
        'jun': '06', 'jul': '07', 'aug': '08', 'sep': '09',
        'oct': '10', 'nov': '11', 'dec': '12'
    }

    # Pattern for YYYY-M-D or YYYY-MM-D or YYYY-M-DD formats (with hyphens)
    dash_pattern = r'^(\d{4})-(\d{1,2})-(\d{1,2})$'
    dash_match = re.match(dash_pattern, cleaned)

    # Pattern for YYYY/MM/DD format (with slashes)
    slash_pattern = r'^(\d{4})/(\d{1,2})/(\d{1,2})$'
    slash_match = re.match(slash_pattern, cleaned)

    # Pattern for CJK date format (YYYY年MM月DD日)
    cjk_pattern = r'^(\d{4})年(\d{1,2})月(\d{1,2})日$'
    cjk_match = re.match(cjk_pattern, cleaned)

    # Pattern for European date format (DD.MM.YYYY)
    dot_pattern = r'^(\d{1,2})\.(\d{1,2})\.(\d{4})$'
    dot_match = re.match(dot_pattern, cleaned)

    # Pattern for YYYY.M.D format (with dots)
    dot_ymd_pattern = r'^(\d{4})\.(\d{1,2})\.(\d{1,2})$'
    dot_ymd_match = re.match(dot_ymd_pattern, cleaned)

    # Pattern for English date format (Month DD, YYYY)
    english_pattern = r'^([a-zA-Z]+)\s+(\d{1,2}),\s+(\d{4})$'
    english_match = re.match(english_pattern, cleaned)

    # Pattern for malformed date-like strings that should return None
    # YYYY-DDD format (day number too large)
    malformed_dash = r'^(\d{4})-(\d+)$'
    malformed_dash_match = re.match(malformed_dash, cleaned)

    if malformed_dash_match:
        # If it looks like YYYY-DDD but DDD is too large, return None
        logger.warning(f"Malformed date detected: {cleaned}")
        return None
    elif dash_match:
        year, month, day = dash_match.groups()
        apply_year_offset = False
    elif slash_match:
        year, month, day = slash_match.groups()
        apply_year_offset = False
    elif cjk_match:
        year, month, day = cjk_match.groups()
        apply_year_offset = True  # Add 20 years for CJK format
    elif dot_match:
        month, day, year = dot_match.groups()  # Note: MM.DD.YYYY order
        apply_year_offset = False
    elif dot_ymd_match:
        year, month, day = dot_ymd_match.groups()  # Note: YYYY.MM.DD order
        apply_year_offset = False
    elif english_match:
        month_name, day, year = english_match.groups()
        month_name_lower = month_name.lower()
        if month_name_lower in month_names:
            month = month_names[month_name_lower]
        else:
            # If month name not recognized, return as-is
            return cleaned
        apply_year_offset = False
    else:
        # Return as-is if it doesn't match any expected pattern
        return cleaned

    # Convert to integers for validation
    year_int = int(year)
    month_int = int(month)
    day_int = int(day)

    # Check if values are beyond salvation
    if year_int < 1 or year_int > 9999:  # Invalid year range
        return None
    if month_int < 0 or month_int > 13:  # Too far out of month range
        return None
    # Too far out of day range (max possible days in a year)
    if day_int < 0 or day_int > 366:
        return None

    # Apply year offset for CJK format
    if apply_year_offset:
        year_int += 20

    # Clip month to valid range (1-12)
    if month_int < 1:
        month_int = 1
    elif month_int > 12:
        month_int = 12

    # Clip day to valid range and handle invalid dates
    try:
        # Try to create a valid date
        datetime(year_int, month_int, day_int)
        return f"{year_int:04d}-{month_int:02d}-{day_int:02d}"
    except ValueError:
        # If the date is invalid (e.g., Feb 29 in non-leap year),
        # find the next valid date
        if day_int > 28:  # Potential issue with day being too large
            # Try decreasing day until we find a valid date
            for test_day in range(day_int, 0, -1):
                try:
                    datetime(year_int, month_int, test_day)
                    # If we found a valid date but it's different from requested,
                    # move to next month/year as needed
                    if test_day != day_int:
                        # Move to first day of next month
                        if month_int == 12:
                            return f"{year_int + 1:04d}-01-01"
                        else:
                            return f"{year_int:04d}-{month_int + 1:02d}-01"
                    return f"{year_int:04d}-{month_int:02d}-{test_day:02d}"
                except ValueError:
                    continue

        # If we still can't create a valid date, move to next month
        if month_int == 12:
            return f"{year_int + 1:04d}-01-01"
        else:
            return f"{year_int:04d}-{month_int + 1:02d}-01"
