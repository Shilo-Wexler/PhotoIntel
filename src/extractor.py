"""
Metadata Extractor Module
-------------------------
Main engine for scanning directories and
extracting organized EXIF metadata.
Utilizes 'extractor_utils.py' for low-level
data processing and sanitization.
"""

from PIL import Image
from PIL.ExifTags import TAGS
from pathlib import Path
import logging
import extractor_utils as utils

logger = logging.getLogger(__name__)


def get_empty_metadata(path: Path):
    return {
        "filename": path.name,
        "full_path": path,
        "datetime": None,
        "latitude": None,
        "longitude": None,
        "camera_make": None,
        "camera_model": None,
        "has_gps": False,
        "software": None,
        "modify_date": None,
        "altitude": None,
        "direction": None,
        "exposure_time": None,
        "iso": None,
        "f_number": None
    }


def get_raw_exif(image_path: Path):
    try:
        with Image.open(image_path) as img:
            # noinspection PyProtectedMember
            exif = img._getexif()
            return exif
    except (Image.UnidentifiedImageError, IOError, PermissionError):
        return False
    except Exception as e:
        logger.error(f"Failed to process {image_path}: {e}")
        return None


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
    metadata = get_empty_metadata(path)
    exif  = get_raw_exif(path)

    if not exif:
        return None if exif is False else metadata

    raw_tags = {TAGS.get(tag_id, tag_id): value for tag_id, value in exif.items()}

    text_mapping = {
        "datetime": utils.extract_timestamp,
        "camera_make": utils.camera_make,
        "camera_model": utils.camera_model,
        "software": utils.software_info,
        "modify_date": utils.modification_date,
    }
    for key, func in text_mapping.items():
        metadata[key] = utils.sanitize_string(func(raw_tags))

    exp = utils.exposure_stats(raw_tags)

    metadata.update({
        "latitude": utils.latitude(raw_tags),
        "longitude": utils.longitude(raw_tags),
        "has_gps": utils.has_gps(raw_tags),
        "altitude": utils.to_float(utils.altitude(raw_tags)),
        "direction": utils.to_float(utils.direction(raw_tags)),
        "exposure_time": utils.to_float(exp["exposure_time"]),
        "iso": utils.to_int(exp["iso"]),
        "f_number": utils.to_float(exp["f_number"])
    })

    return metadata


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

    if not base_path.is_dir():
        return results
    for file_path in base_path.rglob("*"):
        if file_path.is_file():
            try:
                metadata = extract_metadata(str(file_path.resolve()))
                if metadata:
                    results.append(metadata)
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                continue
    return results
