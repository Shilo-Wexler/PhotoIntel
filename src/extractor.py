"""
PhotoIntel - Core Extraction Module 
Engine for extracting EXIF metadata and
geographic information from images.

This module is part of the PhotoIntel
visual information system.
Supports GPS coordinates, devices 
metadata, and timestamp extraction.
"""
from PIL import Image
from PIL.ExifTags import TAGS
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

#---Utility Functions ---


def sanitize_string(val):
    """
    Remove null bytes and whitespace
    from string values.

    Args:
        val: The value to clean.
    Returns:
        The cleaned string or the original value if not a string.
    """
    if isinstance(val, str):
        return val.strip('\x00').strip()
    return val


def to_float(value):
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


def dms_to_decimal(dms_tuple, ref):
    """
    Converts coordinates from DMS (Degrees, Minutes, and Seconds) format to decimal degrees.

    Args:
        dms_tuple (tuple): A tuple containing Degrees, Minutes, and Seconds.
        ref (str): Geographic reference direction (N, S, E, W).

    Returns:
        float: The decimal degree value (negative for S/W references), or None if invalid.
    """
    if not dms_tuple or len(dms_tuple) < 3 or not ref:
        return None

    degrees = to_float(dms_tuple[0])
    minutes = to_float(dms_tuple[1])
    seconds = to_float(dms_tuple[2])

    if None in {degrees, minutes, seconds}:
        return None

    decimal = degrees + (minutes / 60) + (seconds / 3600)

    if ref in [b'S', b'W', 'S', 'W']:
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


def extract_timestamp(exif_data: dict):
    """
    Extract the best available
    timestamp from the metadata.
    """
    dt = exif_data.get("DateTimeOriginal") or exif_data.get("DateTime")
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


def extract_metadata(image_path):
    """
    Extracts EXIF metadata from a single
    image and organizes it into a dictionary.
        Args:
             image_path(str): The full path to
             the image file.
        Returns:
            dict: A dictionary containing
            filename, datetime, GPS, and device info.
    """
    path = Path(image_path)

    try:
        with Image.open(image_path) as img:
            # noinspection PyProtectedMember
            exif = img._getexif()
    # noinspection PyBroadException
    except Exception as e:
        logger.error(f"Failed to process {image_path}: {e}")
        exif = None

    if exif is None:
        return {
        "filename": path.name,
        "datetime": None,
        "latitude": None,
        "longitude": None,
        "camera_make": None,
        "camera_model": None,
        "has_gps": False
        }

    data = {}
    for tag_id, value in exif.items():
        tag = TAGS.get(tag_id, tag_id)
        data[tag] = value


    exif_dict = {
        "filename": path.name,
        "datetime": sanitize_string(extract_timestamp(data)),
        "latitude": latitude(data),
        "longitude": longitude(data),
        "camera_make": sanitize_string(camera_make(data)),
        "camera_model": sanitize_string(camera_model(data)),
        "has_gps": has_gps(data)
    }
    return exif_dict


def extract_all(folder_path):
    """
    Recursively scans a directory and
    extracting metadata from all supported
    images.
        Args:
            folder_path (str): Path to the
    source directory for analysis.
        Returns:
            list: A list of dictionaries, one
    for each successfully processed image.
    """
    results = []
    base_path = Path(folder_path)
    supported_extensions = {
        '.jpg', '.jpeg', '.png', '.gif', '.webp',
        '.bmp', '.svg', '.tiff', '.tif', '.ico',
        '.heif', '.avif', '.apng', '.jfif'
    }
    if not base_path.is_dir():
        return results
    for file_path in base_path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            try:
                metadata = extract_metadata(str(file_path))
                results.append(metadata)
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                continue
    return results
