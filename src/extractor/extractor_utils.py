"""
Extractor Utilities Module
--------------------------
Provides helper functions for mapping raw EXIF tags to structured data.
This module bridges the gap between raw metadata and typed values,
utilizing 'converters.py' for low-level parsing and casting.

Designed to fail gracefully by returning None on missing or malformed data.
"""

from typing import Optional

from src.converters import dms_to_decimal, sanitize_string, to_float, to_int



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
        return to_float(gps_info.get(6))

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
    return sanitize_string(str(dt)) if dt else None


def camera_make(exif_data: dict) -> Optional[str]:
    """
    Retrieves the camera manufacturer name.

    Args:
        exif_data (dict): The dictionary containing raw EXIF tags.

    Returns:
        Optional[str]: The manufacturer (e.g., 'Apple', 'Canon') or None.
    """

    return sanitize_string(exif_data.get("Make"))


def camera_model(exif_data: dict) -> Optional[str]:
    """
    Retrieves the specific camera or device model name.

    Args:
        exif_data (dict): The dictionary containing raw EXIF tags.

    Returns:
        Optional[str]: The model name (e.g., 'iPhone 15 Pro') or None.
    """

    return sanitize_string(exif_data.get("Model"))


def software_info(exif_data: dict) -> Optional[str]:
    """
    Extract the name and version of the software used to process the image.

    Args:
        exif_data (dict): The dictionary containing raw EXIF tags.

    Returns:
        Optional[str]: The software information, or None.
    """

    software = exif_data.get("Software")
    return sanitize_string(str(software)) if software else None


def modification_date(exif_data: dict) -> Optional[str]:
    """
    Extracts the last modification date stored in the EXIF header.

    Args:
        exif_data (dict): The dictionary containing raw EXIF tags.

    Returns:
        Optional[str]: The 'DateTime' (Tag 306) value or None.
    """

    mod_date = exif_data.get("DateTime")
    return sanitize_string(str(mod_date)) if mod_date else None


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
        "exposure_time": to_float(exif_data.get("ExposureTime")),
        "iso": to_int(exif_data.get("ISOSpeedRatings")),
        "f_number": to_float(exif_data.get("FNumber"))
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
        return to_float(gps_info.get(17))

    return None
