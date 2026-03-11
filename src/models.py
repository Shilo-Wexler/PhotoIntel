
"""
Forensic Data Models
--------------------

Defines the core data structure for
image metadata and risk analysis.

Used as the central schema between the
Extractor and Analyzer modules.
"""


from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ImageMetadata:

    """
    Represents the raw evidentiary data
    extracted from an image file.

    This class serves as a Data Transfer
    Object (DTO) between the Ingestion layer
    (Extractor) and the Analysis layer
    (Analyzer).
    """

    filename: str
    full_path: str
    has_exif: bool = False
    has_gps: Optional[bool] = False
    datetime: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    software: Optional[str] = None
    modify_date: Optional[str] = None
    altitude: Optional[float] = None
    direction: Optional[float] = None
    exposure_time: Optional[float] = None
    iso: Optional[int] = None
    f_number: Optional[float] = None


@dataclass
class ImageRiskProfile:

    """
    Forensic analysis results and risk
    scoring.
    """

    filename: str
    full_path: str
    device: str = None
    timestamp: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_score: Optional[int] = 0
    has_exif: bool = False
    is_suspicious: bool = False

    #Forensic Flags
    software_issue: bool = False
    device_issue: bool = False
    temporal_issue: bool = False
    altitude_issue: bool = False
    gps_issue: bool = False
    optical_issue: bool = False
    ai_issue: bool = False
