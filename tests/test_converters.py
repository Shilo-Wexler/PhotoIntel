import unittest
from converters import sanitize_string, to_float, dms_to_decimal, to_int, parse_date

class TestConverters(unittest.TestCase):
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

    def test_dms_to_decimal_edge_values(self):
        self.assertEqual(dms_to_decimal((90, 0, 0), 'N'), 90)
        self.assertEqual(dms_to_decimal((180, 0, 0), 'E'), 180)
        self.assertEqual(dms_to_decimal((90, 0, 0), 'S'), -90)
        self.assertEqual(dms_to_decimal((180, 0, 0), 'W'), -180)

    def test_dms_to_decimal_invalid_ref(self):
        self.assertIsNone(dms_to_decimal((10, 0, 0), 'X'))

    def test_to_float_invalid_strings(self):
        self.assertIsNone(to_float("abc"))
        self.assertIsNone(to_float([1, 2, 3]))

    def test_to_float_weird_object(self):
        class Weird:
            numerator = 5

        self.assertIsNone(to_float(Weird()))

    def test_sanitize_unicode_and_special_chars(self):
        self.assertEqual(sanitize_string("  Café "), "Café")
        self.assertEqual(sanitize_string(" \x00Tab\t "), "Tab")

    def test_parse_date_format1(self):
        dt = parse_date("2023:01:01 10:00:00")
        self.assertIsNotNone(dt)
        self.assertEqual(dt.year, 2023)

    def test_parse_date_format2(self):
        dt = parse_date("2023-01-01 10:00:00")
        self.assertIsNotNone(dt)
        self.assertEqual(dt.month, 1)

    def test_parse_date_invalid(self):
        self.assertIsNone(parse_date("not a date"))

    def test_parse_date_non_string(self):
        self.assertIsNone(parse_date(123))




if __name__ == "__main__":
    unittest.main()



