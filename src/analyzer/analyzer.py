"""
Forensic Photo Analyzer Module
------------------------------
The central analytical engine of the system, engineered to transform raw
image metadata into high-fidelity forensic insights.

Key Capabilities:
    1. Individual Risk Assessment: Cross-references metadata against forensic rules
       (AI, GPS, Software, Device, and Altitude anomalies) to evaluate evidentiary integrity.
    2. Temporal Alignment: Sorts and aligns profiles on a chronological baseline
       to reconstruct the collection's timeline.
    3. Spatial-Temporal Auditing: Detects physically impossible travel and identifies
       geographic hotspots through clustering.
    4. Device Chain-of-Custody Mapping: Tracks device transitions across the
       timeline to identify multi-source origins and facilitate trajectory visualization.

This module serves as the primary intelligence layer between raw ingestion
and comprehensive forensic reporting.
"""

import datetime
import math
from datetime import datetime
from typing import Optional

from src.analyzer import forensic_rules as rules
from src.constants import geo_constants as geo
from src.converters import parse_date
from src.models.collection import CollectionInsights
from src.models.raw import ImageMetadata
from src.models.risk import ImageRiskProfile


class PhotoAnalyzer:
    """
    Core engine for multi-layered forensic analysis of image collections.

    Aggregates individual image assessments with cross-file relational
    analysis to detect anomalies, verify data integrity, and generate
    comprehensive collection insights.
    """
    def __init__(self, images_data: list[ImageMetadata]):
        self.images_data = images_data

    def analyzer(self) -> CollectionInsights:
        """
        Executes a multistaged forensic analysis pipeline on the image collection.

        The process follows a strictly ordered workflow:
            1. Extraction & Assessment: Transforms raw metadata into detailed risk profiles.
            2. Chronological Alignment: Sorts profiles by timestamp to establish a baseline for
               relational analysis.
            3. Statistical Aggregation: Computes collection-wide metrics using declarative
               summation (AI flags, EXIF integrity, device distribution).
            4. Spatial-Temporal Analysis: Detects physical impossibilities (teleportation) and
               identifies geographic hotspots (clustering).

        Returns:
            CollectionInsights: A comprehensive forensic report containing statistical totals,
                risk distributions, and detected anomalies across the entire dataset.
        """
        profiles = [self.evaluate_image(img) for img
                    in self.images_data]

        profiles.sort(key=lambda p: p.timestamp or datetime.min)

        insights = CollectionInsights(profiles)

        insights.image_profiles = profiles

        insights.total_count = len(profiles)
        insights.suspicious_images = sum(profile.is_suspicious for profile in profiles)
        insights.images_with_exif = sum(profile.has_exif for profile in profiles)
        insights.images_with_gps = sum(1 for profile in profiles if None not in {profile.latitude, profile.longitude})

        insights.ai_count = sum(profile.ai_issue for profile in profiles)
        insights.software_edit_count = sum(profile.software_issue for profile in profiles)
        insights.gps_tampering_count = sum(profile.gps_issue for profile in profiles)
        insights.device_anomaly_count = sum(profile.device_issue for profile in profiles)

        insights.unique_device_models = sorted({img.device for img in profiles if img.device})
        insights.start_date = next((p.timestamp for p in profiles if p.timestamp), None)
        insights.end_date = next((p.timestamp for p in reversed(profiles) if p.timestamp), None)

        insights.location_clusters = self._compute_location_clusters(profiles)
        insights.teleportation_incidents = self._get_teleportation_incidents(profiles)
        insights.device_timeline_switches = self._get_device_switches(profiles)

        return insights

    def _get_teleportation_incidents(self, profiles: list[ImageRiskProfile]) -> list[dict]:
        """
        Analyzes consecutive image pairs to detect physically impossible travel speeds.

        Args:
            profiles: Chronologically sorted list of assessed images.

        Returns:
            List of dictionaries containing detected velocity anomalies and spatial data.
        """
        incidents = []

        valid_profiles = [p for p in profiles
            if None not in {p.latitude, p.longitude, p.timestamp}
        ]

        for i in range(1, len(valid_profiles)):
            prev, curr = valid_profiles[i - 1], valid_profiles[i]

            result = self._detect_teleportation(prev, curr)
            if result:
                incidents.append(result)

        return incidents

    @staticmethod
    def _get_device_switches(profiles: list[ImageRiskProfile]) -> list[dict]:
        """
        Identifies device transition points across the sorted image timeline.

        Detects consecutive image pairs captured by different devices and maps
        the spatial-temporal bridge between them, providing a baseline for
        multi-source collection mapping.

        Returns:
            List[dict]: Events containing source/target filenames, device names,
                       and coordinate pairs for trajectory visualization.
        """

        switches = []

        for i in range(1, len(profiles)):
            prev, curr = profiles[i-1], profiles[i]

            if None in {prev.device, curr.device}:
                continue

            if None in {
                prev.latitude, prev.longitude,
                curr.latitude, curr.longitude
            }:
                continue

            if prev.device != curr.device:
                switches.append({
                        "from_file": prev.filename,
                        "to_file": curr.filename,
                        "from_device": prev.device,
                        "to_device": curr.device,
                        "coords": [
                            (prev.latitude, prev.longitude),
                            (curr.latitude, curr.longitude)
                            ]
                })

        return switches

    def _compute_location_clusters(self, profiles: list[ImageRiskProfile]) -> list[dict]:
        """
        Groups images into geographic hotspots based on spatial proximity.

        Uses a greedy clustering approach to aggregate photos within a defined
        radius, identifying primary areas of activity in the collection.

        Returns:
            A list of clusters sorted by image density (descending).
        """
        clusters = []

        gps_data = [profile for profile in profiles
                    if profile.latitude is not None
                    and profile.longitude is not None]

        for profile in gps_data:
            added_to_clusters = False

            for cluster in clusters:
                distance = self._calculate_distance(
                    profile.latitude, profile.longitude,
                    cluster['lat'], cluster['lon']
                )

                if distance <= geo.CLUSTER_RADIUS_KM:
                    cluster['count'] += 1
                    added_to_clusters = True

            if not added_to_clusters:
                clusters.append({
                    'lat': profile.latitude,
                    'lon': profile.longitude,
                    'count': 1
                })

        return sorted(clusters,
                      key=lambda x: x['count'], reverse=True)

    @staticmethod
    def evaluate_image(image: ImageMetadata) -> ImageRiskProfile:
        """
        Analyzes a single image for forensic anomalies and integrity issues.

        If the image lacks EXIF data, a basic profile is returned immediately.
        Otherwise, it cross-references multiple forensic rules (AI, GPS, Time, etc.)
        to determine the overall suspicion status.

        Args:
            image (ImageMetadata): The raw metadata extracted from the image.

        Returns:
            ImageRiskProfile: A structured profile containing risk flags and
                processed data for report generation.
        """
        if not image.has_exif:
            return ImageRiskProfile(
                filename=image.filename,
                full_path=image.full_path
            )

        ai_status = rules.is_ai_generated(image)
        gps_status = rules.has_gps_issue(image)
        temporal_status = rules.has_temporal_issue(image)
        software_status = rules.has_software_issue(image)
        device_status = rules.has_virtual_device_issue(image)
        altitude_status = rules.is_altitude_anomaly(image)
        optical_status = rules.has_optical_issue(image)

        is_suspicious = any([
            ai_status, gps_status, temporal_status, software_status,
            device_status, altitude_status, optical_status
        ])

        device_name = PhotoAnalyzer._build_device_name(image)
        timestamp = parse_date(image.datetime)

        return ImageRiskProfile(
            filename=image.filename,
            full_path=image.full_path,
            device=device_name,
            timestamp=timestamp,
            latitude=image.latitude,
            longitude=image.longitude,

            is_suspicious=is_suspicious,
            has_exif=image.has_exif,

            software_issue = software_status,
            device_issue = device_status,
            temporal_issue =temporal_status,
            altitude_issue = altitude_status,
            gps_issue = gps_status,
            optical_issue = optical_status,
            ai_issue = ai_status
            )

    def _detect_teleportation(self, prev: ImageRiskProfile, curr: ImageRiskProfile) -> Optional[dict]:
        """
        Calculates travel velocity between two points to flag integrity violations.

        Validates if the geographic distance covered within the time delta
        exceeds physical thresholds (constants.MAX_SPEED_KMH).

        Returns:
            A dictionary of incident details if a violation is detected, else None.
        """
        if None in {
            prev.timestamp, curr.timestamp,
            prev.latitude, curr.latitude,
            prev.longitude, curr.longitude
        }:
            return None

        dist_km = self._calculate_distance(
            prev.latitude, prev.longitude,
            curr.latitude, curr.longitude
        )

        time_diff_sec = (
            (curr.timestamp - prev.timestamp).total_seconds()
        )

        if time_diff_sec < geo.MIN_TIME_DIFF_SEC:
            return None

        time_diff_hours = time_diff_sec / 3600

        if time_diff_hours == 0:
            return None

        speed_km = dist_km / time_diff_hours

        if speed_km > geo.MAX_SPEED_KMH:
            return {
                "from_file": prev.filename,
                "to_file": curr.filename,

                "distance_km": round(dist_km, 2),
                "speed_kmh": round(speed_km, 2),
                "time_gap_minutes": round(time_diff_sec / 60, 2),
                "coords": [
                    (prev.latitude, prev.longitude),
                    (curr.latitude, curr.longitude)
                ]
            }

        return None

    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculates the great-circle distance between two GPS points.

        Uses the Haversine formula to account for the Earth's curvature.
        This is a pure mathematical function and does not depend on class state.

        Args:
            lat1, lon1: Coordinates of the first point.
            lat2, lon2: Coordinates of the second point.

        Returns:
            float: Distance in kilometers. Returns 0.0 if any coordinate is missing.
        """
        if None in {lat1, lon1, lat2, lon2}:
            return 0.0

        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(phi1) * math.cos(phi2) * math.sin(delta_lon / 2) ** 2)

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return geo.EARTH_RADIUS_KM * c

    @staticmethod
    def _build_device_name(image: ImageMetadata) -> Optional[str]:
        """
        Generates a clean, unified device identifier.

        Prevents redundant naming by checking if the manufacturer (make)
        is already included in the model string.

        Args:
            image (ImageMetadata): The image metadata object containing
                camera_make and camera_model fields.

        Returns:
            str: A formatted string combining make and model, or None
                if no data is available.
        """
        make = image.camera_make
        model = image.camera_model

        if make is None and model is None:
            return None

        if make and model:
            return (model if make.lower() in model.lower()
                    else f"{make} {model}".strip())

        device_name = make or model

        return device_name if device_name else None
