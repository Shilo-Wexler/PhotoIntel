"""
Raw Metadata Extraction Module
------------------------------
Defines the foundational data structures for the ingestion phase.

This module acts as the first layer of data representation, capturing 
the unadulterated EXIF and metadata values exactly as they were 
extracted from the source files, prior to any forensic evaluation.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ImageMetadata:
    """
    Immutable representation of raw evidentiary data extracted from a file.

    This class serves as a strict Data Transfer Object (DTO) moving from 
    the Extraction layer to the Analysis layer. By being 'frozen', it 
    guarantees the integrity of the raw data, ensuring no downstream 
    processes can accidentally mutate the original evidence.

    Attributes:
        [File Information]
        filename (str): The name of the file (e.g., 'image_01.jpg').
        full_path (str): The absolute path to the file on disk.

        [Integrity Flags]
        has_exif (bool): Indicates whether any EXIF metadata was found.
        has_gps (bool): Indicates whether geographic coordinates were successfully parsed.

        [Temporal & Spatial Data]
        datetime (Optional[str]): The original capture timestamp as an unparsed string.
        modify_date (Optional[str]): The timestamp indicating when the file was last altered.
        latitude (Optional[float]): GPS latitude in decimal degrees.
        longitude (Optional[float]): GPS longitude in decimal degrees.
        altitude (Optional[float]): GPS altitude in meters relative to sea level.
        direction (Optional[float]): GPS image direction (bearing) in degrees.

        [Device & Software]
        camera_make (Optional[str]): The manufacturer of the capturing device.
        camera_model (Optional[str]): The specific model of the capturing device.
        software (Optional[str]): The firmware or editing software that last saved the file.

        [Optical & Technical Specifications]
        exposure_time (Optional[float]): The exposure time in seconds.
        f_number (Optional[float]): The focal ratio (aperture) of the lens.
        iso (Optional[int]): The ISO speed rating (light sensitivity).
        pixel_width (Optional[int]): The image width in pixels.
        pixel_height (Optional[int]): The image height in pixels.
    """

    # File Information
    filename: str
    full_path: str

    # Integrity Flags
    has_exif: bool = False
    has_gps: bool = False

    # Temporal & Spatial Data
    datetime: Optional[str] = None
    modify_date: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    direction: Optional[float] = None

    # Device & Software
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    software: Optional[str] = None

    # Optical & Technical Specifications
    exposure_time: Optional[float] = None
    f_number: Optional[float] = None
    iso: Optional[int] = None
    pixel_width: Optional[int] = None
    pixel_height: Optional[int] = None