
import json
from datetime import datetime
from dataclasses import dataclass
import pytest

from src.reporter.generator import ReportGenerator



@dataclass
class DummyPhoto:
    name: str
    created: datetime


@dataclass
class DummyCollectionInsights:
    photos: list
    total_count: int
    suspicious_count: int


# --- Tests ---


def test_generate_report_creates_directory_and_file(tmp_path):
    insights = DummyCollectionInsights([], 0, 0)

    generator = ReportGenerator(insights)

    output_dir = tmp_path / "nested" / "reports"

    output_file = generator.generate_web_payload(output_dir)

    assert output_file.exists()
    assert output_file.name == "report_data.js"
    assert output_file.parent == output_dir


def test_generate_report_accepts_string_path(tmp_path):
    insights = DummyCollectionInsights([], 1, 0)

    generator = ReportGenerator(insights)

    output_file = generator.generate_web_payload(str(tmp_path))

    assert output_file.exists()


def test_output_starts_with_js_constant(tmp_path):
    insights = DummyCollectionInsights([], 2, 1)

    generator = ReportGenerator(insights)

    output_file = generator.generate_web_payload(tmp_path)

    content = output_file.read_text()

    assert content.startswith("const REPORT_DATA =")


def test_json_payload_is_valid(tmp_path):
    insights = DummyCollectionInsights([], 3, 1)

    generator = ReportGenerator(insights)

    output_file = generator.generate_web_payload(tmp_path)

    content = output_file.read_text()

    json_part = content.replace("const REPORT_DATA =", "").strip().rstrip(";")

    parsed = json.loads(json_part)

    assert parsed["total_count"] == 3
    assert parsed["suspicious_count"] == 1


def test_datetime_serialization(tmp_path):
    photo = DummyPhoto("test.jpg", datetime(2025, 1, 1))

    insights = DummyCollectionInsights([photo], 1, 0)

    generator = ReportGenerator(insights)

    output_file = generator.generate_web_payload(tmp_path)

    content = output_file.read_text()

    assert "2025-01-01" in content


def test_overwrites_existing_file(tmp_path):
    insights = DummyCollectionInsights([], 5, 2)

    generator = ReportGenerator(insights)

    output_file = tmp_path / "report_data.js"

    output_file.write_text("OLD DATA")

    new_file = generator.generate_web_payload(tmp_path)

    content = new_file.read_text()

    assert "OLD DATA" not in content
    assert "REPORT_DATA" in content


def test_large_payload(tmp_path):
    photos = [DummyPhoto(f"img_{i}.jpg", datetime.now()) for i in range(1000)]

    insights = DummyCollectionInsights(photos, 1000, 100)

    generator = ReportGenerator(insights)

    output_file = generator.generate_web_payload(tmp_path)

    content = output_file.read_text()

    assert "img_999.jpg" in content

def test_payload_matches_dataclass(tmp_path):
    insights = DummyCollectionInsights([], 7, 3)

    generator = ReportGenerator(insights)

    output_file = generator.generate_web_payload(tmp_path)

    content = output_file.read_text()

    json_part = content.replace("const REPORT_DATA =", "").strip().rstrip(";")

    parsed = json.loads(json_part)

    assert parsed == {
        "photos": [],
        "total_count": 7,
        "suspicious_count": 3
    }

def test_utf8_encoding(tmp_path):
    insights = DummyCollectionInsights([], 1, 0)

    generator = ReportGenerator(insights)

    output_file = generator.generate_web_payload(tmp_path)

    with open(output_file, "rb") as f:
        raw = f.read()

    raw.decode("utf-8")

def test_output_dir_is_file(tmp_path):
    fake_file = tmp_path / "not_a_dir"
    fake_file.write_text("hello")

    insights = DummyCollectionInsights([], 1, 0)
    generator = ReportGenerator(insights)

    with pytest.raises(Exception):
        generator.generate_web_payload(fake_file)