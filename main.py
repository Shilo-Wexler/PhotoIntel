"""
PhotoIntel — main.py
---------------------
FastAPI application entry point.

Exposes a single POST /analyze endpoint that accepts image files,
runs them through the forensic extraction and analysis pipeline,
and returns a structured CollectionInsights report as JSON.

The frontend (app/) is served as static files mounted at the root path,
making the entire application accessible from a single server process.

Usage:
    python main.py
    uvicorn main:app --host 0.0.0.0 --port 8080 --reload
"""

import logging
import os
import shutil
import tempfile
from dataclasses import asdict
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.analyzer.analyzer import PhotoAnalyzer
from src.extractor.extractor import extract_all

# ─────────────────────────────────────────
# Logging
# ─────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("photointel")

# ─────────────────────────────────────────
# Application
# ─────────────────────────────────────────

app = FastAPI(
    title="PhotoIntel",
    description="Forensic image metadata analysis and geospatial auditing API.",
    version="1.0.0",
)

# ─────────────────────────────────────────
# Middleware
# ─────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────
# Routes
# ─────────────────────────────────────────

@app.post("/analyze", summary="Analyze uploaded image files")
async def analyze_images(files: List[UploadFile] = File(...)):
    """
    Accepts one or more image files, runs the full forensic pipeline,
    and returns a CollectionInsights report serialized as JSON.

    Pipeline:
        1. Save uploaded files to a temporary directory.
        2. Extract raw EXIF metadata via the Extractor engine.
        3. Analyze metadata with seven forensic rule engines.
        4. Return the aggregated CollectionInsights as a JSON dict.

    Raises:
        400 — No extractable metadata found in the uploaded files.
        500 — Internal server error during extraction or analysis.
    """
    temp_dir = tempfile.mkdtemp()
    logger.info(f"Received {len(files)} file(s) for analysis.")

    try:
        # Save files with sanitized names to avoid OS-level path issues
        for file in files:
            safe_name = (
                os.path.basename(file.filename)
                .replace(":", "_")
                .replace(" ", "_")
            )
            file_path = os.path.join(temp_dir, safe_name)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        # Stage 1 — Metadata extraction
        metadata_list = extract_all(temp_dir)
        if not metadata_list:
            raise HTTPException(
                status_code=400,
                detail="No metadata could be extracted from the uploaded files."
            )

        logger.info(f"Extracted metadata from {len(metadata_list)} file(s).")

        # Stage 2 — Forensic analysis
        insights = PhotoAnalyzer(metadata_list).analyzer()
        logger.info(
            f"Analysis complete — {insights.total_count} files, "
            f"{insights.suspicious_images} suspicious."
        )

        return asdict(insights)

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Unexpected error during analysis.")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


# ─────────────────────────────────────────
# Static Frontend
# ─────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "app")

if os.path.exists(WEB_DIR):
    # Mount the frontend at root — must be registered after all API routes
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="ui")
    logger.info(f"Serving frontend from: {WEB_DIR}")
else:
    logger.warning(f"Frontend directory not found: {WEB_DIR}")

# ─────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
