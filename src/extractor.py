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
from dataclasses import dataclass

from PIL import Image
from PIL.ExifTags import TAGS

import constants
import extractor_utils as utils
from models import ImageMetadata



logger = logging.getLogger(__name__)



@dataclass
class RawImageData:
    exif: Optional[dict] = None
    width: Optional[int] = None
    height: Optional[int] = None


def get_image_data(image_path: Path) -> RawImageData:
    """
    Safely opens an image file and retrieves its raw EXIF data and dimensions.

    Args:
        image_path (Path): The pathlib.Path object pointing to the image.

    Returns:
        RawImageData: A data object containing the raw EXIF dictionary, width, and height.
                      If extraction fails, returns an empty RawImageData instance
                      with all fields set to None.
    """

    try:
        with Image.open(image_path) as img:
            return RawImageData(
                # noinspection PyProtectedMember
                exif = img._getexif(),
                width = img.width,
                height= img.height
            )
    except Exception as e:
        logger.error(f"Failed to process {image_path}: {e}")

        return RawImageData()


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
    raw_data = get_image_data(path)

    if not raw_data.exif:
        return ImageMetadata(
            filename=path.name,
            full_path=str(path.resolve()),
            pixel_width=raw_data.width,
            pixel_height=raw_data.height
        )

    raw_tags = {TAGS.get(tag_id, tag_id): value for tag_id, value in exif.items()}

    exp = utils.exposure_stats(raw_tags)

    return ImageMetadata(
    filename = path.name,
    full_path = str(path.resolve()),
    has_exif = True,
    has_gps = utils.has_gps(raw_tags),
    datetime = utils.extract_timestamp(raw_tags),
    latitude = utils.latitude(raw_tags),
    longitude = utils.longitude(raw_tags),
    camera_make = utils.camera_make(raw_tags),
    camera_model = utils.camera_model(raw_tags),
    software = utils.software_info(raw_tags),
    modify_date = utils.modification_date(raw_tags),
    altitude = utils.altitude(raw_tags),
    direction = utils.direction(raw_tags),
    exposure_time = exp.get('exposure_time'),
    iso = exp.get('iso'),
    f_number = exp.get('f_number'),
    pixel_width=width,
    pixel_height=height



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
