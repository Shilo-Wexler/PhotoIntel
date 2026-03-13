"""
Report Generation Module
Handles the conversion of analysis results into web-compatible format.
"""


import json
from pathlib import Path
from dataclasses import asdict

from src.models import CollectionInsights


class ReportGenerator:
    """
    Serializes analysis insights into a web-ready format.
    """
    def __init__(self, insights:CollectionInsights):
        self.insights = insights

    def generate_web_payload(self, output_dir: str | Path) -> Path:
        """
        Serialize the collection insights into a JavaScript data payload.

        Args:
            output_dir: The directory where the report data file will be created.

        Returns:
            Path: The full path to the generated 'report_data.js' file.
        """
        target_dir = Path(output_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        collection_insight = asdict(self.insights)

        json_payload = json.dumps(collection_insight, indent=4, default=str)

        file_content = f"const REPORT_DATA = {json_payload};"

        output_file = target_dir/"report_data.js"
        with output_file.open("w", encoding="utf-8") as f:
            f.write(file_content)

        return output_file

