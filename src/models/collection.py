"""
Collection Insights Module
--------------------------
Defines the data structures responsible for aggregating and summarizing 
forensic analysis results across an entire collection of images.

This module acts as the definitive "source of truth" for the macro-level 
analysis, bridging the gap between individual image profiles and the final 
report generated for the user interface.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from src.models.risk import ImageRiskProfile


@dataclass
class CollectionInsights:
    """
    Aggregated forensic analysis report for an image collection.

    This dataclass serves as the final output payload from the PhotoAnalyzer. 
    It encapsulates both the individual risk profiles of each image and 
    the macroscopic insights derived from cross-referencing the entire dataset.

    Attributes:
        image_profiles (list[ImageRiskProfile]): The detailed forensic profiles 
            for every individual image processed in the collection.

        [General Statistics]
        total_count (int): Total number of images successfully processed.
        suspicious_images (int): Count of images flagged with at least one anomaly.
        images_with_exif (int): Count of images containing embedded EXIF metadata.
        images_with_gps (int): Count of images with valid geographic coordinates.

        [Anomaly Metrics]
        ai_count (int): Number of images suspected to be AI-generated.
        software_edit_count (int): Number of images edited by external software.
        gps_tampering_count (int): Number of images with illogical or spoofed GPS data.
        device_anomaly_count (int): Number of images originating from virtual/emulator devices.

        [Temporal & Device Data]
        unique_device_models (list[str]): A deduplicated list of all camera/phone models found.
        start_date (Optional[datetime]): The earliest chronological timestamp in the collection.
        end_date (Optional[datetime]): The latest chronological timestamp in the collection.

        [Spatial-Temporal Incidents]
        location_clusters (list[dict]): Groupings of photos taken in close physical proximity.
        teleportation_incidents (list[dict]): Events where travel speed between consecutive 
            photos exceeds logical physical limits.
        device_timeline_switches (list[dict]): Points in the chronological timeline where 
            the capturing device changed.
    """

    # Core Data
    image_profiles: list[ImageRiskProfile]

    # General Statistics
    total_count: int = 0
    suspicious_images: int = 0
    images_with_exif: int = 0
    images_with_gps: int = 0

    # Anomaly Metrics
    ai_count: int = 0
    software_edit_count: int = 0
    gps_tampering_count: int = 0
    device_anomaly_count: int = 0

    # Temporal & Device Data
    unique_device_models: list[str] = field(default_factory=list)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    # Spatial-Temporal Incidents
    location_clusters: list[dict] = field(default_factory=list)
    teleportation_incidents: list[dict] = field(default_factory=list)
    device_timeline_switches: list[dict] = field(default_factory=list)