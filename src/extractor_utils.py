"""
Extractor Utilities Module
--------------------------
This module provide helper functions for
the EXIF metadata extraction process.
It includes functions for data cleaning
(sanitization), coordinates conversion,
and specific field extraction from raw
EXIF tags.

Functions:
    - to_float: Safe conversion of EXIF
Rationals to float numbers.
    - sanitize_string: Cleaning and
stripping whitespace from text fields.
"""
from typing import Optional, Any

def sanitize_string(val: Any)->Any:
    """
    Remove null bytes and whitespace
    from string values.

    Args:
        val: The value to clean.
    Returns:
        The cleaned string or the original value if not a string.
    """
    if isinstance(val, str):
        return val.strip(' \x00\t\n\r')
    return val


def to_float(value: Any)->Optional[float]:
    """
    Convert EXIF numeric or Rational
    values to float, returning None on failure.
    """
    try:
        if hasattr(value, 'numerator') and hasattr(value, 'denominator'):
            return float(value.numerator) / float(value.denominator)
        return float(value)
    except (TypeError, ZeroDivisionError, AttributeError):
        return None


def to_int(value: Any)->Optional[int]:
    """
    Safely convert a value to an integer.
    Returns None if the value is invalid or a string that cannot be converted.
    """
    try:
        if value is None:
            return None
        return int(value)
    except (ValueError, TypeError):
        return None


def dms_to_decimal(dms_tuple: tuple, ref: Any)->Optional[float]:
    """
    Converts coordinates from DMS (Degrees, Minutes, and Seconds) format to decimal degrees.

    Args:
        dms_tuple (tuple): A tuple containing Degrees, Minutes, and Seconds.
        ref (str): Geographic reference direction (N, S, E, W).

    Returns:
        float: The decimal degree value (negative for S/W references), or None if invalid.
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


def has_gps(exif_data: dict):
    """
    Checks if GPS information is
    present in the metadata dictionary.
    """
    return "GPSInfo" in exif_data


def latitude(exif_data: dict):
    """
    Extract latitude from the EXIF
    data dictionary.
    """
    gps_info = exif_data.get("GPSInfo")
    if isinstance(gps_info, dict) and 2 in gps_info:
        return dms_to_decimal(gps_info[2], gps_info.get(1))
    return None


def longitude(exif_data: dict):
    """
    Extract longitude from the EXIF
    data dictionary.
    """
    gps_info = exif_data.get("GPSInfo")
    if isinstance(gps_info, dict) and 4 in gps_info:
        return dms_to_decimal(gps_info[4], gps_info.get(3))
    return None


def altitude(exif_data: dict):
    """
    Extract altitude from GPSInfo safely.
    """
    gps_info = exif_data.get("GPSInfo")
    if isinstance(gps_info, dict):
        return gps_info.get(6)
    return None


def extract_timestamp(exif_data: dict):
    """
    Extract the best available
    timestamp from the metadata.
    """
    dt = exif_data.get("DateTimeOriginal")
    return str(dt) if dt else None


def camera_make(exif_data: dict):
    """
    Retrieves the camera manufacturer
    from EXIF data.
    """
    return exif_data.get("Make")


def camera_model(exif_data: dict):
    """
    Retrieves the camera model name
    from EXIF data.
    """
    return exif_data.get("Model")


def software_info(exif_data: dict):
    """
    Extract the software name used to
    create or edit the image.
    """
    software = exif_data.get("Software")
    return str(software) if software else None


def modification_date(exif_data: dict):
    """
    Extracts the last modification
    date from EXIF.
    """
    mod_date = exif_data.get("DateTime")
    return str(mod_date) if mod_date else None


def exposure_stats(exif_data: dict):
    """
    Extract technical exposure
    settings (ISO, Shutter Speed,
    Aperture).
    """
    return {
        "exposure_time": exif_data.get("ExposureTime"),
        "iso": exif_data.get("ISOSpeedRatings"),
        "f_number": exif_data.get("FNumber")
    }


def direction(exif_data: dict):
    """
    Extract image direction from
    GPSInfo safely.
    """
    gps_info = exif_data.get("GPSInfo")
    if isinstance(gps_info, dict):
        return gps_info.get(17)
    return None

