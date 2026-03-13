import unittest
from extractor.extractor_utils import (
    has_gps, latitude, longitude, altitude,
    extract_timestamp, camera_make, camera_model,
    software_info, modification_date, exposure_stats, direction
)


class TestExtractorUtils(unittest.TestCase):

    def test_has_gps(self):
        self.assertTrue(has_gps({"GPSInfo": {}}))
        self.assertFalse(has_gps({}))

    def test_latitude_longitude_altitude(self):
        exif = {"GPSInfo": {1: 'N', 2: (10, 0, 0), 3: 'E', 4: (20, 0, 0), 6: 100, 17: 45}}
        self.assertAlmostEqual(latitude(exif), 10.0)
        self.assertAlmostEqual(longitude(exif), 20.0)
        self.assertEqual(altitude(exif), 100.0)
        self.assertEqual(direction(exif), 45.0)

    def test_extract_timestamp_and_camera_info(self):
        exif = {"DateTimeOriginal": "2026:03:13 10:00:00", "Make": "Canon", "Model": "R5"}
        self.assertEqual(extract_timestamp(exif), "2026:03:13 10:00:00")
        self.assertEqual(camera_make(exif), "Canon")
        self.assertEqual(camera_model(exif), "R5")

    def test_software_and_modification_date(self):
        exif = {"Software": "Photoshop", "DateTime": "2026:03:13 12:00:00"}
        self.assertEqual(software_info(exif), "Photoshop")
        self.assertEqual(modification_date(exif), "2026:03:13 12:00:00")

    def test_exposure_stats(self):
        exif = {"ExposureTime": 0.01, "ISOSpeedRatings": 100, "FNumber": 2.8}
        stats = exposure_stats(exif)
        self.assertEqual(stats["exposure_time"], 0.01)
        self.assertEqual(stats["iso"], 100)
        self.assertEqual(stats["f_number"], 2.8)

    def test_latitude_longitude_none(self):
        self.assertIsNone(latitude({}))
        self.assertIsNone(longitude({}))
        self.assertIsNone(altitude({}))
        self.assertIsNone(direction({}))

    def test_latitude_longitude_invalid(self):
        exif = {"GPSInfo": {1: 'N', 2: None, 3: 'E', 4: "abc", 6: "abc", 17: "xxx"}}
        self.assertIsNone(latitude(exif))
        self.assertIsNone(longitude(exif))
        self.assertIsNone(altitude(exif))
        self.assertIsNone(direction(exif))

    def test_timestamp_camera_none(self):
        exif = {}
        self.assertIsNone(extract_timestamp(exif))
        self.assertIsNone(camera_make(exif))
        self.assertIsNone(camera_model(exif))
        self.assertIsNone(software_info(exif))
        self.assertIsNone(modification_date(exif))

    def test_exposure_stats_invalid(self):
        exif = {"ExposureTime": "abc", "ISOSpeedRatings": "NaN", "FNumber": None}
        stats = exposure_stats(exif)
        self.assertIsNone(stats["exposure_time"])
        self.assertIsNone(stats["iso"])
        self.assertIsNone(stats["f_number"])
