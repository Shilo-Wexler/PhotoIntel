import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.extractor.extractor import get_image_data, extract_metadata, extract_all, RawImageData


class TestExtractor(unittest.TestCase):
    @patch("src.extractor.extractor.Image.open")
    def test_get_image_data_success(self, mock_open):
        mock_img = MagicMock()
        mock_img.__enter__.return_value = mock_img
        mock_img.width = 100
        mock_img.height = 200
        mock_img._getexif.return_value = {"Make": "Canon"}

        mock_open.return_value = mock_img

        result = get_image_data(Path("test.jpg"))

        self.assertEqual(result.width, 100)
        self.assertEqual(result.height, 200)
        self.assertEqual(result.exif, {"Make": "Canon"})

    @patch("src.extractor.extractor.Image.open")
    def test_get_image_data_failure(self, mock_open):
        mock_open.side_effect = Exception("bad image")

        result = get_image_data(Path("bad.jpg"))

        self.assertIsNone(result.exif)
        self.assertIsNone(result.width)
        self.assertIsNone(result.height)

    @patch("src.extractor.extractor.get_image_data")
    def test_extract_metadata_no_exif(self, mock_data):
        mock_data.return_value = RawImageData(
            exif=None,
            width=100,
            height=200
        )

        metadata = extract_metadata("photo.jpg")

        self.assertEqual(metadata.filename, "photo.jpg")
        self.assertEqual(metadata.pixel_width, 100)
        self.assertEqual(metadata.pixel_height, 200)
        self.assertFalse(metadata.has_exif)

    @patch("src.extractor.extractor.get_image_data")
    def test_extract_metadata_with_exif(self, mock_data):
        mock_data.return_value = RawImageData(
            exif={},
            width=300,
            height=400
        )

        metadata = extract_metadata("image.jpg")

        self.assertEqual(metadata.filename, "image.jpg")
        self.assertFalse(metadata.has_exif)

    def test_extract_all_invalid_folder(self):
        result = extract_all("not_a_folder")

        self.assertEqual(result, [])

    @patch("src.extractor.extractor.extract_metadata")
    @patch("src.extractor.extractor.Path.rglob")
    @patch("src.extractor.extractor.Path.is_dir")
    def test_extract_all_success(self, mock_is_dir, mock_rglob, mock_extract):
        mock_is_dir.return_value = True

        fake_file = MagicMock()
        fake_file.is_file.return_value = True
        fake_file.suffix = ".jpg"

        mock_rglob.return_value = [fake_file]

        mock_extract.return_value = MagicMock()

        result = extract_all("folder")

        self.assertEqual(len(result), 1)