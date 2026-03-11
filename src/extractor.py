"""
Metadata Extraction Engine
--------------------------
This module serves as the Ingestion Layer of the forensic system.
It is responsible for:
1. Orchestrating recursive directory scans for image assets.
2. Filtering files based on supported forensic formats.
3. Extracting and normalizing raw EXIF data into structured DTOs (ImageMetadata).

The engine leverages 'extractor_utils.py' for granular data parsing and
sanitization, ensuring that only clean, type-safe data reaches the Analysis Layer.
"""

import logging
from pathlib import Path
from typing import Optional

from PIL import Image
from PIL.ExifTags import TAGS

import constants
import extractor_utils as utils
from models import ImageMetadata



logger = logging.getLogger(__name__)


def get_raw_exif(image_path: Path) -> Optional[dict]:
    """
    Safely opens an image file and retrieves its raw EXIF data.

    Args:
        image_path (Path): The pathlib.Path object pointing to the image.

    Returns:
        Optional[dict]: A dictionary of raw EXIF tags if found,
                        None if the file is not an image or is corrupted.
    """

    try:
        with Image.open(image_path) as img:
            # noinspection PyProtectedMember
            exif = img._getexif()
            return exif
    except Exception as e:
        logger.error(f"Failed to process {image_path}: {e}")
        return None


def extract_metadata(image_path: str) -> ImageMetadata:
    """
    Extracts and normalizes metadata from a single image file.

    Performs validation, raw EXIF extraction, and maps sanitized values
    into a structured ImageMetadata DTO.

    Args:
        image_path (str): Absolute or relative path to the image.

    Returns:
        ImageMetadata: Structured metadata object
    """

    path = Path(image_path)
    exif = get_raw_exif(path)


    if not exif:
        return ImageMetadata(filename=path.name, full_path=str(path.resolve()))


    raw_tags = {TAGS.get(tag_id, tag_id): value for tag_id, value in exif.items()}

    text_mapping = {
        "datetime": utils.extract_timestamp,
        "camera_make": utils.camera_make,
        "camera_model": utils.camera_model,
        "software": utils.software_info,
        "modify_date": utils.modification_date,
    }

    extract_fields = {field: utils.sanitize_string(func(raw_tags))
                      for field, func in text_mapping.items()}

    exp = utils.exposure_stats(raw_tags)

    extract_fields.update({
        "latitude": utils.latitude(raw_tags),
        "longitude": utils.longitude(raw_tags),
        "has_gps": utils.has_gps(raw_tags),
        "altitude": utils.to_float(utils.altitude(raw_tags)),
        "direction": utils.to_float(utils.direction(raw_tags)),
        "exposure_time": utils.to_float(exp.get('exposure_time')),
        "iso": utils.to_int(exp.get('iso')),
        "f_number": utils.to_float(exp.get('f_number'))
    })

    return ImageMetadata(
        filename=path.name,
        full_path=str(path.resolve()),
        has_exif=True,
        **extract_fields
    )


def extract_all(folder_path: str) -> list[ImageMetadata]:
    """
    Recursively scans a directory for supported image files and extracts their metadata.

    Only files with extensions listed in 'constants.SUPPORTED_EXTENSIONS' are processed,
    ensuring type-safe, clean data for downstream analysis.

    Args:
        folder_path (str): Root directory to start the recursive scan.

    Returns:
        list[ImageMetadata]: Metadata objects for all successfully processed images.
                             Returns an empty list if the path is invalid or no supported files are found.
    """

    results = []
    base_path = Path(folder_path)

    if not base_path.is_dir():
        return results

    supported = constants.SUPPORTED_EXTENSIONS

    for file_path in base_path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in supported:
            try:
                metadata = extract_metadata(str(file_path))
                results.append(metadata)
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
    return results
