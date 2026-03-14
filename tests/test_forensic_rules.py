from src.models.raw import ImageMetadata
import src.analyzer.forensic_rules as rules
import src.constants.geo_constants as geo
import src.constants.forensic_constants as fc

fc.AI_SOFTWARE = {"stablediffusion", "midjourney"}
fc.AI_RESOLUTIONS = {512, 1024, 2048}
geo.AI_MODULO = 64
fc.STANDARD_ASPECT_RATIOS = {1.33, 1.5, 1.78}
fc.HIGH_ISO = 3200
fc.LONG_EXPOSURE = 15
fc.LOW_NIGHT_F_STOP = 2.0
fc.MIN_HIGH_ISO = 1600
fc.DAY_START = 7
fc.DAY_END = 19
fc.EDITING_SOFTWARE = {"photoshop", "lightroom"}
fc.VIRTUAL_DEVICE = {"virtualcam", "emulator"}
geo.MAX_ALTITUDE = 8000
geo.MIN_ALTITUDE = -450
geo.EARTH_MIN_LAT = -90
geo.EARTH_MAX_LAT = 90
geo.EARTH_MIN_LON = -180
geo.EARTH_MAX_LON = 180


class TestForensicRules:

    def _make_metadata(self, **overrides):
        """
        Helper to create ImageMetadata.
        """
        defaults = dict(
            filename="test.jpg",
            full_path="/images/test.jpg",
            has_exif=True,
            has_gps=True,
            datetime="2026-03-13T12:00:00",
            latitude=45.1234,
            longitude=45.5678,
            camera_make="Canon",
            camera_model="EOS",
            software="CameraApp",
            modify_date="2026-03-13T12:30:00",
            altitude=100,
            direction=90,
            exposure_time=10,
            f_number=2.8,
            pixel_width=1024,
            pixel_height=1024,
            iso=200
        )
        defaults.update(overrides)
        return ImageMetadata(**defaults)

    # --- is_ai_generated ---
    def test_is_ai_generated_by_signature(self):
        metadata = self._make_metadata(software="StableDiffusion")
        assert rules.is_ai_generated(metadata) is True

    def test_is_ai_generated_by_resolution(self):
        metadata = self._make_metadata(pixel_width=512, pixel_height=512)
        assert rules.is_ai_generated(metadata) is True

    def test_is_ai_generated_by_modulo(self):
        metadata = self._make_metadata(pixel_width=128, pixel_height=192)
        assert rules.is_ai_generated(metadata) is True

    def test_is_ai_generated_by_aspect_ratio(self):
        metadata = self._make_metadata(pixel_width=1234, pixel_height=567, has_exif=False)
        assert rules.is_ai_generated(metadata) is True

    def test_is_ai_generated_normal(self):
        metadata = self._make_metadata(pixel_width=1200, pixel_height=800, has_exif=True)
        assert rules.is_ai_generated(metadata) is False

    # --- is_altitude_anomaly ---
    def test_is_altitude_anomaly_normal(self):
        metadata = self._make_metadata(altitude=100)
        assert rules.is_altitude_anomaly(metadata) is False

    def test_is_altitude_anomaly_high(self):
        metadata = self._make_metadata(altitude=9000)
        assert rules.is_altitude_anomaly(metadata) is True

    def test_is_altitude_anomaly_low(self):
        metadata = self._make_metadata(altitude=-500)
        assert rules.is_altitude_anomaly(metadata) is True

    # --- has_gps_issue ---
    def test_has_gps_issue_valid(self):
        metadata = self._make_metadata(latitude=45.098, longitude=45.01)
        assert rules.has_gps_issue(metadata) is False

    def test_has_gps_issue_invalid_lat(self):
        metadata = self._make_metadata(latitude=100.0)
        assert rules.has_gps_issue(metadata) is True

    def test_has_gps_issue_invalid_lon(self):
        metadata = self._make_metadata(longitude=200.0)
        assert rules.has_gps_issue(metadata) is True

    def test_has_gps_issue_injected(self):
        metadata = self._make_metadata(latitude=45.0, longitude=60.0)
        metadata = metadata.__class__(**{**metadata.__dict__, "latitude": 45.0, "longitude": 60.0})
        assert rules.has_gps_issue(metadata) is True

    # --- has_optical_issue ---
    def test_has_optical_issue_daytime_high_iso(self):
        metadata = self._make_metadata(datetime="2026-03-13T12:00:00", iso=6400)
        assert rules.has_optical_issue(metadata) is True

    def test_has_optical_issue_daytime_long_exposure(self):
        metadata = self._make_metadata(datetime="2026-03-13T12:00:00", exposure_time=30)
        assert rules.has_optical_issue(metadata) is True

    def test_has_optical_issue_daytime_low_fstop_high_iso(self):
        metadata = self._make_metadata(datetime="2026-03-13T12:00:00", f_number=1.8, iso=2000)
        assert rules.has_optical_issue(metadata) is True

    def test_has_optical_issue_nighttime(self):
        metadata = self._make_metadata(datetime="2026-03-13T22:00:00", iso=6400)
        assert rules.has_optical_issue(metadata) is False

    # --- has_software_issue ---
    def test_has_software_issue_true(self):
        metadata = self._make_metadata(software="Photoshop")
        assert rules.has_software_issue(metadata) is True

    def test_has_software_issue_false(self):
        metadata = self._make_metadata(software="CameraApp")
        assert rules.has_software_issue(metadata) is False

    # --- has_virtual_device_issue ---
    def test_has_virtual_device_issue_true(self):
        metadata = self._make_metadata(camera_make="VirtualCam")
        assert rules.has_virtual_device_issue(metadata) is True

    def test_has_virtual_device_issue_false(self):
        metadata = self._make_metadata(camera_make="Canon")
        assert rules.has_virtual_device_issue(metadata) is False

    # --- has_temporal_issue ---
    def test_has_temporal_issue_valid(self):
        metadata = self._make_metadata(datetime="2026-03-13T12:00:00", modify_date="2026-03-13T13:00:00")
        assert rules.has_temporal_issue(metadata) is False

    def test_has_temporal_issue_invalid(self):
        metadata = self._make_metadata(datetime="2026-03-13T12:00:00", modify_date="2026-03-13T11:00:00")
        assert rules.has_temporal_issue(metadata) is True