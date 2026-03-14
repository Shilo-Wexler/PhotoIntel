"""
Forensic Report Generation Module
---------------------------------
Handles the serialization of forensic analysis results into a web-compatible
JavaScript payload.

This module acts as the final stage of the pipeline, transforming structured
Python data models into the 'report_data.js' file consumed by the frontend UI.
"""

import json
from pathlib import Path
from dataclasses import asdict

from src.constants import report_constants as rc
from src.models.collection import CollectionInsights


class ReportGenerator:
    """
    Orchestrates the conversion of analysis insights into a web-ready format.
    """

    def __init__(self, insights: CollectionInsights):
        """
        Initializes the generator with a completed collection analysis.

        Args:
            insights (CollectionInsights): The aggregated result of the forensic analysis.
        """
        self.insights = insights

    def generate_web_payload(self, output_dir: str | Path = rc.DEFAULT_REPORT_DIR) -> Path:
        """
        Serializes the collection insights into a JavaScript data payload.

        Wraps the JSON-encoded analysis data in a JS constant, making it
        immediately accessible via a <script> tag in the frontend.

        Args:
            output_dir (str | Path): The directory where the JS file will be saved.
                                     Defaults to the project's report/app folder.

        Returns:
            Path: The full path to the generated 'report_data.js' file.
        """
        target_dir = Path(output_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        collection_insights = asdict(self.insights)

        json_payload = json.dumps(collection_insights, indent=4, default=str)

        file_content = f"const {rc.JS_VARIABLE_NAME} = {json_payload};"

        output_file = target_dir / rc.REPORT_DATA_FILENAME
        output_file.write_text(file_content, encoding="utf-8")

        return output_file