"""
Project Paths & Report Constants Module
---------------------------------------
Defines foundational directories, file output names, and JavaScript
variable bindings used for report generation in the forensic analysis pipeline.
"""

from pathlib import Path

# Resolves to the main project folder (PhotoIntel/)
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]

# The default directory where the reporter generates the JSON/JS payloads
DEFAULT_REPORT_DIR: Path = PROJECT_ROOT / "report"

# The output filename for the generated payload
REPORT_DATA_FILENAME: str = "report_data.js"

# The exact JavaScript const variable name the frontend expects
JS_VARIABLE_NAME: str = "REPORT_DATA"