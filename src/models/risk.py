"""
Forensic Risk Profile Module
----------------------------
Defines the analytical output structure for individual files.

This module represents the state of an image *after* it has been processed 
by the forensic rules engine. It translates raw metadata into actionable 
intelligence and binary risk flags.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.models.raw import ImageMetadata


@dataclass(frozen=True)
class ImageRiskProfile:
    """
    Comprehensive forensic analysis results and risk scoring for a single image.

    This immutable dataclass is the direct output of the Analyzer component. 
    It bridges the raw metadata and the parsed contextual data (like standardizing 
    device names and timestamps), while providing a detailed breakdown of which 
    specific forensic rules the image violated.

    Attributes:
        [File Identification]
        filename (str): The name of the analyzed file.
        full_path (str): The absolute path to the file.

        [Parsed Context]
        device (Optional[str]): A normalized string representing the capturing device.
        timestamp (Optional[datetime]): A fully parsed datetime object representing 
            the verified chronological position of the image.
        latitude (Optional[float]): Verified GPS latitude.
        longitude (Optional[float]): Verified GPS longitude.

        [High-Level Status]
        has_exif (bool): Confirms if the image had a metadata payload to analyze.
        is_suspicious (bool): The master flag. True if ANY of the specific anomaly 
            flags below are triggered.

        [Specific Forensic Flags]
        software_issue (bool): Triggered if the image was saved by known editing 
            software (e.g., Photoshop, Lightroom).
        device_issue (bool): Triggered if the device signature matches virtual 
            environments or emulators.
        temporal_issue (bool): Triggered if the metadata timestamps (e.g., Modify Date 
            vs Original Date) contradict each other chronologically.
        altitude_issue (bool): Triggered if the recorded GPS altitude is physically 
            implausible (e.g., underground or in the stratosphere).
        gps_issue (bool): Triggered if the GPS coordinates are mathematically invalid 
            or suggest crude tampering (e.g., perfectly round numbers).
        optical_issue (bool): Triggered if the camera settings (ISO, Exposure, F-Stop) 
            contradict the time of day the photo was allegedly taken.
        ai_issue (bool): Triggered if the image signature matches known AI generation 
            tools (e.g., Midjourney, Stable Diffusion) or specific aspect ratios.
    """

    # File Identification
    filename: str
    full_path: str
    raw_metadata: ImageMetadata

    # Parsed Context
    device: Optional[str] = None
    timestamp: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # High-Level Status
    has_exif: bool = False
    is_suspicious: bool = False

    # Specific Forensic Flags
    software_issue: bool = False
    device_issue: bool = False
    temporal_issue: bool = False
    altitude_issue: bool = False
    gps_issue: bool = False
    optical_issue: bool = False
    ai_issue: bool = False