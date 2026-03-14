"""
Data Conversion & Normalization Utility.
Standardizes raw EXIF data into typed Python objects while
providing a safety layer against malformed or corrupt metadata.
"""

import logging
from datetime import datetime
from typing import Any, Optional


logger = logging.getLogger(__name__)


def sanitize_string(val: Any) -> Any:
    """
    Clean string values by removing null bytes, tabs.

    Args:
        val (Any): The raw value to clean.

    Returns:
        Any: Cleaned string if input was string , otherwise returns the original value.
    """
    if isinstance(val, bytes):
        try:
            return val.decode('utf-8', errors='replace').strip(' \x00\t\n\r')
        except UnicodeDecodeError:
            return val
        except Exception as e:
            logger.warning(f"Failed to decode bytes metadata: {e}")

    if isinstance(val, str):
        return val.strip(' \x00\t\n\r')

    return val


def to_float(value: Any) -> Optional[float]:
    """
    Safely converts EXIF numeric or Rational values to a float.
    Handles 'IFDRational' types by calculating numerator/denominator.

    Args:
        value (Any): The raw numeric or Rational value.

    Returns:
        Optional[float]: Float value or None if conversion fails
         or division by zero occurs.
    """

    try:
        if hasattr(value, 'numerator') and hasattr(value, 'denominator'):
            return float(value.numerator) / float(value.denominator)

        return float(value)
    except (TypeError, ZeroDivisionError, AttributeError, ValueError):
        return None


def to_int(value: Any) -> Optional[int]:
    """
    Safely converts a value to an integer.

    Args:
        value (Any): The raw value to convert.

    Returns:
        Optional[int]: Integer value or None if conversion is not possible.
    """

    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def dms_to_decimal(dms_tuple: tuple, ref: Any) -> Optional[float]:
    """
    Converts Degrees, Minutes, Seconds (DMS) coordinates to Decimal Degrees.

    Args:
        dms_tuple (tuple): A tuple DNS in Rational format.

        ref (str/bytes): Geographic reference directions.

    Returns:
        Optional[float]: Decimal coordinates, or None if invalid.
    """

    negative_refs = {'S', b'S', 'W', b'W'}
    positive_refs = {'N', b'N', 'E', b'E'}
    refs = negative_refs | positive_refs

    if None in {dms_tuple, ref} or len(dms_tuple) < 3 or ref not in refs:
        return None

    degrees = to_float(dms_tuple[0])
    minutes = to_float(dms_tuple[1])
    seconds = to_float(dms_tuple[2])

    if None in {degrees, minutes, seconds}:
        return None

    decimal = degrees + (minutes / 60) + (seconds / 3600)

    if ref in negative_refs:
        decimal = -decimal
    return decimal


def parse_date(date: Any)->Optional[datetime]:
    """
    Safely parses a raw EXIF date string into a Python datetime object.

    Args:
        date (Any): The raw string value from times tags.

    Returns:
        Optional[datetime]: A datetime object if parsing succeed, None otherwise.
    """

    if not isinstance(date, str):
        return None

    formats = [
        "%Y:%m:%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%d.%m.%Y %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date, fmt)
        except (ValueError, TypeError):
            continue

    try:
        return datetime.fromisoformat(date)
    except ValueError:
        return None
