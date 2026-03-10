import unittest
import unittest.mock as mock
from src.extractor_utils import sanitize_string, to_float, dms_to_decimal, to_int
from src.extractor import get_empty_metadata, extract_metadata
from pathlib import Path

class TestPhotoIntel(unittest.TestCase):
    def test_sanitize_basic(self):
        dirty_name = "   Canon "
        clean_name = sanitize_string(dirty_name)
        self.assertEqual(clean_name, "Canon")
    def test_sanitize_null_bytes(self):
        dirty_input = "Nikon\x00"
        result = sanitize_string(dirty_input)
        self.assertEqual(result, "Nikon")
    def test_sanitize_none_and_nums(self):
        self.assertIsNone(sanitize_string(None))
        self.assertEqual(sanitize_string(123),123)
    def test_sanitize_complex_garbage(self):
        self.assertEqual(sanitize_string("\x00Sony\x00"),"Sony")
        self.assertEqual(sanitize_string(" \x00Nikon \x00 "),"Nikon")
    def test_to_float_standard(self):
        self.assertEqual(to_float(10),10.0)
        self.assertEqual(to_float("5.5"), 5.5)
        self.assertEqual(to_float("6"), 6.0)
    def test_to_float_rational(self):
        class MockRational:
            def __init__(self, n, d):
                self.numerator = n
                self.denominator = d
        self.assertEqual(to_float(MockRational(10,2)), 5.0)
    def test_to_float_division_by_zero(self):
        class BadRational:
            def __init__(self, n, d):
                self.numerator = n
                self.denominator = d
        result = to_float(BadRational(10,0))
        self.assertIsNone(result)
    def test_dms_to_decimal_success(self):
        dms_tuple = (32,4,33.6)
        ref = 'N'
        # 32 + 4 /60 + 33.6/3600 = 32.076
        result = dms_to_decimal(dms_tuple, ref)
        self.assertAlmostEqual(result, 32.076, places=3)

    def test_dms_to_decimal_to_negative_ref(self):
        result_west = dms_to_decimal((10,0,0), 'W')
        result_south = dms_to_decimal((10,0,0), 'S')
        self.assertEqual(result_west, -10)
        self.assertEqual(result_south, -10)
    def test_dms_to_decimal_invalid_input(self):
        self.assertIsNone(dms_to_decimal(None,'N'))
        self.assertIsNone(dms_to_decimal((32,4),'N'))
        self.assertIsNone(dms_to_decimal((1,-20,0),9))
    def test_dms_to_decimal_boundaries(self):
        class MockRat:
            numerator = 60
            denominator = 2
        self.assertEqual(dms_to_decimal((MockRat(),0,0),'N'),30.0)
        self.assertEqual(dms_to_decimal((10,0,0),b'N'),10.0)
        self.assertIsNone(dms_to_decimal((32,None,0),'N'))
    def test_to_int_standard(self):
        self.assertEqual(to_int("100"),100)
        self.assertEqual(to_int(800.0),800)
        self.assertIsNone(to_int(None))
    def test_to_int_garbage(self):
        self.assertIsNone(to_int("ISO100"))
        self.assertIsNone(to_int("ABC"))
    def test_empty_metadata(self):
        empty = get_empty_metadata(Path("images_copy/sample_data/20230118_070716.jpg"))
        expected_keys = {
            "filename", "full_path", "datetime", "latitude", "longitude",
            "camera_make", "camera_model", "has_gps", "software",
            "modify_date", "altitude", "direction", "exposure_time",
            "iso", "f_number"
        }
        self.assertTrue(expected_keys.issubset(empty.keys()))
        self.assertIsNone(empty["iso"])
        self.assertFalse(empty["has_gps"])

    def test_extract_metadata_integration(self):
        with mock.patch('src.extractor.get_raw_exif') as mocked_exif:
            mocked_exif.return_value = {
                271: "Apple", #make
                272: "iPhone 13 ", #model
                305: "Adobe Photoshop", #software
                34855: "800" #ISO
            }
            result = extract_metadata("dummy.jpg")
            self.assertEqual(result["camera_make"], "Apple")
            self.assertEqual(result["software"], "Adobe Photoshop")
            self.assertEqual(result["iso"], 800)
            self.assertIsInstance(result["iso"], int)











if __name__ == "__main__":
    unittest.main()



