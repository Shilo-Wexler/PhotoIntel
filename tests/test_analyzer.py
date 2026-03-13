import pytest
from datetime import datetime
from src.models import ImageMetadata
from src import constants
from src.analyzer import PhotoAnalyzer

# Mock constants to run tests independently
constants.CLUSTER_RADIUS_KM = 1.0
constants.MAX_SPEED_KMH = 1000
constants.MIN_TIME_DIFF_SEC = 10
constants.EARTH_RADIUS_KM = 6371
def make_image(**overrides):
    """Helper to generate a fully populated ImageMetadata object."""
    defaults = dict(
        filename="img.jpg",
        full_path="/images/img.jpg",
        has_exif=True,
        has_gps=True,
        datetime="2026-03-13T12:00:00",
        latitude=0.0,
        longitude=0.0,
        camera_make="Canon",
        camera_model="EOS",
        software="CameraApp",
        modify_date="2026-03-13T12:10:00",
        altitude=100,
        direction=90,
        exposure_time=10,
        f_number=2.8,
        pixel_width=1024,
        pixel_height=768,
        iso=200
    )
    defaults.update(overrides)
    return ImageMetadata(**defaults)


class TestPhotoAnalyzer:

    @pytest.mark.parametrize(
        "make,model,expected_device",
        [
            ("Canon", "EOS", "Canon EOS"),
            (None, None, None),
            ("Canon", "Canon EOS", "Canon EOS"),
            ("", "EOS", "EOS")
        ]
    )
    def test_build_device_name_variants(self, make, model, expected_device):
        """Check device name formatting logic with various inputs."""
        img = make_image(camera_make=make, camera_model=model)
        profile = PhotoAnalyzer.evaluate_image(img)
        assert profile.device == expected_device

    @pytest.mark.parametrize(
        "lat1,lon1,lat2,lon2,expected_nonzero",
        [
            (0,0,0,1, True),
            (0,0,0,0, False),
            (None,0,0,0, False),
            (0,None,0,0, False),
        ]
    )
    def test_calculate_distance_edge_cases(self, lat1, lon1, lat2, lon2, expected_nonzero):
        """Distance calculation should handle missing or identical coordinates."""
        dist = PhotoAnalyzer._calculate_distance(lat1, lon1, lat2, lon2)
        if expected_nonzero:
            assert dist > 0
        else:
            assert dist == 0.0

    @pytest.mark.parametrize(
        "img1_props,img2_props,expect_incident",
        [
            ({"latitude":0,"longitude":0,"datetime":"2026-03-13T12:00:00"},
             {"latitude":50,"longitude":50,"datetime":"2026-03-13T12:01:00"},
             True),  # High speed triggers teleportation
            ({"datetime":"2026-03-13T12:00:00"},
             {"datetime":"2026-03-13T12:00:05"},
             False)  # Too short time -> no incident
        ]
    )
    def test_detect_teleportation_various(self, img1_props, img2_props, expect_incident):
        """Test teleportation detection with normal and edge cases."""
        img1 = make_image(**img1_props)
        img2 = make_image(**img2_props)
        profile1 = PhotoAnalyzer.evaluate_image(img1)
        profile2 = PhotoAnalyzer.evaluate_image(img2)
        analyzer = PhotoAnalyzer([img1, img2])
        incident = analyzer._detect_teleportation(profile1, profile2)
        if expect_incident:
            assert incident is not None
            assert "speed_kmh" in incident
        else:
            assert incident is None

    @pytest.mark.parametrize(
        "images_props,expected_switch_count",
        [
            (  # Normal switch
                [{"camera_model":"A"}, {"camera_model":"B","datetime":"2026-03-13T12:10:00"}],
                1
            ),
            (  # Missing device -> no switch
                [{"camera_make":None,"camera_model":None}, {"camera_model":"B"}],
                0
            )
        ]
    )
    def test_get_device_switches_param(self, images_props, expected_switch_count):
        """Test detection of device switches with normal and missing device names."""
        imgs = [make_image(**p) for p in images_props]
        profiles = [PhotoAnalyzer.evaluate_image(img) for img in imgs]
        switches = PhotoAnalyzer._get_device_switches(profiles)
        assert len(switches) == expected_switch_count

    @pytest.mark.parametrize(
        "images_props,expected_cluster_count",
        [
            ([{"latitude":0,"longitude":0},{"latitude":0.0001,"longitude":0.0001},{"latitude":10,"longitude":10}],
             2),  # Two clusters: close pair + distant
            ([{"latitude":None,"longitude":None},{"latitude":None,"longitude":None}],
             0)   # No GPS -> no clusters
        ]
    )
    def test_compute_location_clusters_param(self, images_props, expected_cluster_count):
        """Test clustering with normal, close, and missing GPS data."""
        imgs = [make_image(**p) for p in images_props]
        profiles = [PhotoAnalyzer.evaluate_image(img) for img in imgs]
        analyzer = PhotoAnalyzer(imgs)
        clusters = analyzer._compute_location_clusters(profiles)
        assert len(clusters) == expected_cluster_count

    @pytest.mark.parametrize(
        "has_exif,datetime_val,modify_val",
        [
            (True,"2026-03-13T12:00:00","2026-03-13T12:10:00"),
            (False,None,None),
            (True,None,None),
            (True,"invalid","2026-03-13T12:10:00")
        ]
    )
    def test_analyzer_various_inputs(self, has_exif, datetime_val, modify_val):
        """Test analyzer handles normal, missing EXIF, and invalid datetime."""
        img = make_image(has_exif=has_exif, datetime=datetime_val, modify_date=modify_val)
        analyzer = PhotoAnalyzer([img])
        insights = analyzer.analyzer()
        assert insights.total_count == 1
        profile = insights.image_profiles[0]
        if has_exif:
            assert profile.has_exif is True
        else:
            assert profile.has_exif is False
        assert profile.timestamp is None or isinstance(profile.timestamp, datetime)


    @pytest.mark.parametrize(
        "make, model, expected",
        [
            ("Canon", "EOS", "Canon EOS"),
            ("Canon", "Canon EOS", "Canon EOS"),
            ("Canon", None, "Canon"),
            (None, "EOS", "EOS"),
            (None, None, None),
            ("", "EOS", "EOS"),
            ("Canon", "", "Canon"),
            ("", "", None),
            ("Nikon", "NIKON Z7", "NIKON Z7"),
            ("sony", "SONY A7", "SONY A7"),
        ]
    )
    def test_build_device_name_variants(self, make, model, expected):
        """Test _build_device_name with all combinations of make and model."""
        img = ImageMetadata(
            filename="img.jpg",
            full_path="/images/img.jpg",
            camera_make=make,
            camera_model=model
        )
        device_name = PhotoAnalyzer._build_device_name(img)
        assert device_name == expected