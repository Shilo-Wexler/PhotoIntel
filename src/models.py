
"""
Forensic Data Models
--------------------

Defines the core data structure for image metadata and risk analysis.

Used as the central schema between the Extractor and Analyzer modules.
"""


from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ImageMetadata:

    """
    Represents the raw evidentiary data extracted from an image file.

    This class serves as a Data Transfer Object (DTO)
    between the Ingestion layer (Extractor) and the Analysis layer
    (Analyzer).
    """

    filename: str
    full_path: str
    has_exif: bool = False
    has_gps: bool = False
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
    f_number: Optional[float] = None
    pixel_width: Optional[int] = None
    pixel_height: Optional[int] = None
    iso: Optional[int] = None


@dataclass(frozen=True)
class ImageRiskProfile:

    """
    Forensic analysis results and risk scoring.
    """

    filename: str
    full_path: str
    device: Optional[str] = None
    timestamp: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    has_exif: bool = False
    is_suspicious: bool = False

    software_issue: bool = False
    device_issue: bool = False
    temporal_issue: bool = False
    altitude_issue: bool = False
    gps_issue: bool = False
    optical_issue: bool = False
    ai_issue: bool = False


@dataclass
class CollectionInsights:
    """
    Represents the high-level analysis of an entire image collection.
    """

    image_profiles: list[ImageRiskProfile]

    total_count: int = 0
    suspicious_images: int = 0
    images_with_exif: int = 0
    images_with_gps: int = 0

    ai_count: int = 0
    software_edit_count: int = 0
    gps_tampering_count: int = 0
    device_anomaly_count: int = 0

    unique_device_models: list[str] = field(default_factory=list)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    location_clusters: list[dict] = field(default_factory=list)
    teleportation_incidents: list[dict] = field(default_factory=list)

