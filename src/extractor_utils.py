"""
Extractor Utilities Module
--------------------------
Provides low-level helper functions for EXIF metadata processing.
This module handles data sanitization, coordinate conversion (DMS to Decimal),
and safe type casting (Rational to Float).

It is designed to fail gracefully by returning None instead of raising
exceptions during data parsing.
"""


from typing import Optional, Any



def sanitize_string(val: Any) -> Any:
    """
    Clean string values by removing null bytes, tabs.

    Args:
        val (Any): The raw value to clean.

    Returns:
        Any: Cleaned string if input was string , otherwise returns the original value.
    """

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


def has_gps(exif_data: dict) -> bool:
    """
    Checks if the 'GPSInfo' tag is present in the EXIF dictionary.

    Args:
        exif_data (dict): The dictionary containing raw EXIF tags.

    Returns:
        bool: True if 'GPSInfo' tag exists, False otherwise.
    """

    return "GPSInfo" in exif_data


def latitude(exif_data: dict) -> Optional[float]:
    """
    Extract and converts latitude from GPSInfo to decimal degrees.

    Args:
        exif_data (dict): The dictionary containing raw EXIF tags.

    Returns:
         Optional[float]: Latitude in decimal degrees, or None if tag 2 is missing.
    """

    gps_info = exif_data.get("GPSInfo")

    if isinstance(gps_info, dict) and 2 in gps_info:
        return dms_to_decimal(gps_info[2], gps_info.get(1))

    return None


def longitude(exif_data: dict) -> Optional[float]:
    """
    Extract and converts longitude from GPSInfo to decimal degrees.

    Args:
        exif_data (dict): The dictionary containing raw EXIF tags.

    Returns:
        Optional[float]: Longitude in decimal degrees, or None if tag 4 is missing.
    """
    gps_info = exif_data.get("GPSInfo")

    if isinstance(gps_info, dict) and 4 in gps_info:
        return dms_to_decimal(gps_info[4], gps_info.get(3))

    return None


def altitude(exif_data: dict) -> Optional[float]:
    """
    Extract altitude (height above sea level) from GPSInfo.

    Args:
        exif_data (dict): The dictionary containing raw EXIF tags.

    Returns:
       Optional[float]: Altitude value from tag 6, or None if unavailable.
    """

    gps_info = exif_data.get("GPSInfo")

    if isinstance(gps_info, dict):
        return gps_info.get(6)

    return None


def extract_timestamp(exif_data: dict) -> Optional[str]:
    """
    Retrieves the original capture timestamp from the metadata.

    Args:
        exif_data (dict): The dictionary containing raw EXIF tags.

    Returns:
        Optional[str]: The 'DateTimeOriginal' as a string, or None if missing.
    """

    dt = exif_data.get("DateTimeOriginal")
    return str(dt) if dt else None


def camera_make(exif_data: dict) -> Optional[str]:
    """
    Retrieves the camera manufacturer name.

    Args:
        exif_data (dict): The dictionary containing raw EXIF tags.

    Returns:
        Optional[str]: The manufacturer (e.g., 'Apple', 'Canon') or None.
    """

    return exif_data.get("Make")


def camera_model(exif_data: dict) -> Optional[str]:
    """
    Retrieves the specific camera or device model name.

    Args:
        exif_data (dict): The dictionary containing raw EXIF tags.

    Returns:
        Optional[str]: The model name (e.g., 'iPhone 15 Pro') or None.
    """

    return exif_data.get("Model")


def software_info(exif_data: dict) -> Optional[str]:
    """
    Extract the name and version of the software used to process the image.

    Args:
        exif_data (dict): The dictionary containing raw EXIF tags.

    Returns:
        Optional[str]: The software information, or None.
    """

    software = exif_data.get("Software")
    return str(software) if software else None


def modification_date(exif_data: dict) -> Optional[str]:
    """
    Extracts the last modification date stored in the EXIF header.

    Args:
        exif_data (dict): The dictionary containing raw EXIF tags.

    Returns:
        Optional[str]: The 'DateTime' (Tag 306) value or None.
    """

    mod_date = exif_data.get("DateTime")
    return str(mod_date) if mod_date else None


def exposure_stats(exif_data: dict) -> dict:
    """
    Extract the core technical exposure settings for optical analysis.

    Args:
        exif_data (dict): The dictionary containing raw EXIF tags.

    Returns:
        dict: A dictionary containing:
        - 'exposure_time': The shutter speed.
        - 'iso': The sensor sensitivity.
        - 'f_number': The lens aperture
    """

    return {
        "exposure_time": exif_data.get("ExposureTime"),
        "iso": exif_data.get("ISOSpeedRatings"),
        "f_number": exif_data.get("FNumber")
    }


def direction(exif_data: dict) -> Optional[float]:
    """
    Extract the image direction (compass heading) from GPSInfo.

    Args:
        exif_data (dict): The dictionary containing raw EXIF tags.

    Returns:
        Optional[float]: The direction value from GPS tag 17, or None
         if the tag is invalid.
    """
    gps_info = exif_data.get("GPSInfo")

    if isinstance(gps_info, dict):
        return gps_info.get(17)

    return None

