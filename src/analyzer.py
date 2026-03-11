from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
import constants

@dataclass
class ImageMetadata:
    filename: str




@dataclass
class ImageRiskProfile:
    filename: str
    has_exif: bool
    timestamp: Optional[datetime]
    lat: Optional[float]
    lon: Optional[float]
    device: str
    total_score: int
    is_suspicious: bool
    software_issue: bool
    device_issue: bool
    temporal_issue: bool
    altitude_issue: bool
    gps_issue: bool
    optical_issue: bool




class PhotoAnalyzer:
    def __init__(self, image_data: list[dict]):
        self.all_photos = image_data
        self.timeline = self._create_timeline()
        self.unique_cameras = self._get_unique_cameras()
        self.date_range = self._get_date_range()
        self.gps_img_count = self._count_gps_images()

    @staticmethod
    def _evaluate_image(image: dict)->ImageRiskProfile:
        """
        Orchestrate multiple forensic
        checks on a single image
        and return a risk profile
        """



    @staticmethod
    def _altitude_anomaly(image: dict)->int:
        """
        Score (0-10) if altitude is
        impossibly high for handheld device
        without appropriate professional
        markers.
        """
        alt = image.get('altitude')

        if not alt:
            return 0

        if alt < constants.MIN_ALTITUDE or alt > constants.MAX_ALTITUDE:
            return 10

        return 0

    @staticmethod
    def _gps_integrity_check(image: dict)->int:
        """
        Check for sings of manually
        injected or impossible
        GPS coordinates.
        """
        if not image.get('has_gps'):
            return 0

        lat = image.get('latitude')
        lon = image.get('longitude')

        if isinstance(lat, float) and lon.is_integer():
            return 10

        return 0

    @staticmethod
    def _temporal_discrepancy(image: dict)->int:
        """
        Score (0-10) for mismatches
        between EXIF capture time and
        file system modification time.
        """
        exif_date = PhotoAnalyzer._parse_date(image.get('datetime'))
        file_date = PhotoAnalyzer._parse_date(image.get('modify_date'))

        if not file_date or not exif_date:
            return 0

        if file_date < exif_date:
            return 10

        return 0


    @staticmethod
    def _is_high_iso_daylight(image: dict, hour:int)->bool:
        """
        True if ISO is suspiciously
        high during peak daylight.
        """
        iso = image.get('iso',0)

        return 11<= hour <= 15 and iso >= constants.HIGH_ISO

    @staticmethod
    def _is_long_exposure_daylight(image: dict, hour:int)->bool:
        """
        True if exposure time is
        impossibly long for daylight.
        """
        exp = image.get('exposure_time',0)

        return 11<= hour <= 15 and exp > constants.LONG_EXPOSURE

    @staticmethod
    def _is_impossible_aperture(image: dict)->bool:
        """
        True if large aperture (f-stop) and
        high ISO suggest dark environment.
        """
        f_stop = image.get('f_number',0)
        iso = image.get('iso', 0)

        return f_stop < constants.IMPOSSIBLE_F_STOP and iso > constants.MIN_HIGH_ISO


    @staticmethod
    def _optical_time_consistency(image: dict)->int:
        """
        Check for physical contradictions
        between optical settings (ISO, Shutter, Aperture)
        and the recorded time of day.
        """
        if not image.get('has_exif'):
            return 0
        date = PhotoAnalyzer._parse_date(image.get('datetime'))

        if not date:
            return 0

        hour = date.hour
        total_score = 0

        if PhotoAnalyzer._is_high_iso_daylight(image, hour):
            total_score += 2
        if PhotoAnalyzer._is_long_exposure_daylight(image, hour):
            total_score += 2
        if PhotoAnalyzer._is_impossible_aperture(image):
            total_score += 6

        return total_score


    @staticmethod
    def _software_footprint(image: dict)->int:
        """
        Score (0-10) based on software
        signatures found in metadata.
        10: Professional editors,
        5: Mobile editing apps.
        """

        software = (image.get('software') or '').lower()

        if not software:
            return 0

        if any(tool in software for tool
               in constants.PRO_SOFTWARE):
            return 10

        if any(app in software for app
               in constants.MOBILE_APP):
            return 5

        return 0


    @staticmethod
    def _device_anomaly(image: dict)->int:
        """
        Score (0-10) for non-physical
        device signatures
        """
        model = PhotoAnalyzer._build_device_name(image).lower()

        if not model:
            return 0

        if any(device in model for device
               in constants.VIRTUAL_DEVICE):
            return 10

        return 0


    @staticmethod
    def _build_device_name(image: dict)->str:
        """
        Return combined camera make and model.
        If make is already in model, only model
        is returned.
        """
        make = image.get("camera_make") or ''
        model = image.get("camera_model") or ''
        make = '' if make.lower() in model.lower() else make
        return f"{make} {model}".strip()


    @staticmethod
    def _parse_date(date: Any)->Optional[datetime]:
        """
        Convert an EXIF date string to a
        datetime object.
        Supports multiple formats; returns None
        on failure.
        """
        if not isinstance(date, str):
            return None

        formats = [
            "%Y:%m:%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S"
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date, fmt)
            except (ValueError, TypeError):
                continue
        return None


    def _count_gps_images(self)->int:
        """
        Count how many images contain GPS
        metadata.
        """
        return sum(1 for img in self.all_photos if img.get('has_gps'))


    def _get_date_range(self)->dict:
        """
        Extract the earliest and latest dates
        from the sorted timeline.
        Returns a dictionary with formatted
        date string.
        """
        if not self.timeline:
            return {
                'start': None,
                'end': None
            }
        return {
            'start': self.timeline[0]['timestamp'].strftime('%Y-%m-%d'),
            'end': self.timeline[-1]['timestamp'].strftime('%Y-%m-%d')
        }


    def _get_unique_cameras(self)->list[str]:
        """
        Extract a unique list of combined
        camera make and model.
        Example: 'Apple iPhone 16 Pro'
        """
        devices = set()
        for img in self.all_photos:
            model = PhotoAnalyzer._build_device_name(img)
            if model:
                devices.add(model)
        return sorted(devices)


    def _create_timeline(self)->list[dict]:
        """
        Filter and sort entries chronologically
        to build a valid analysis sequence.
        """
        dated_images = []

        for img in self.all_photos:
            timestamp = self._parse_date(img.get('datetime'))
            if timestamp:
                dated_images.append({**img, 'timestamp': timestamp})
        return sorted(dated_images, key = lambda x: x['timestamp'])










