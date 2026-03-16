"""
PhotoIntel — main.py
---------------------
FastAPI application entry point.

Exposes two API endpoints:
  - POST /analyze  — Forensic analysis pipeline for uploaded images.
  - POST /ask      — AI assistant powered by Gemini for forensic Q&A.

The frontend (app/) is served as static files mounted at the root path,
making the entire application accessible from a single server process.
"""

import logging
import os
import shutil
import tempfile
from dataclasses import asdict
from typing import List

import google.generativeai as genai
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.analyzer.analyzer import PhotoAnalyzer
from src.extractor.extractor import extract_all

# ─────────────────────────────────────────
# API Keys
# ─────────────────────────────────────────

try:
    from config import GEMINI_API_KEY as _LOCAL_GEMINI_KEY
except ImportError:
    _LOCAL_GEMINI_KEY = None

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or _LOCAL_GEMINI_KEY

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

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
    temp_dir = tempfile.mkdtemp()
    logger.info(f"Received {len(files)} file(s) for analysis.")

    try:
        for file in files:
            safe_name = (
                os.path.basename(file.filename)
                .replace(":", "_")
                .replace(" ", "_")
            )
            file_path = os.path.join(temp_dir, safe_name)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        metadata_list = extract_all(temp_dir)
        if not metadata_list:
            raise HTTPException(
                status_code=400,
                detail="No metadata could be extracted from the uploaded files."
            )

        logger.info(f"Extracted metadata from {len(metadata_list)} file(s).")

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


@app.post("/ask", summary="Ask the AI forensic assistant about an image")
async def ask_ai(request: dict):
    """
    Accepts a user question alongside a forensic profile,
    and returns a concise Gemini response.
    """
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API Key not configured.")

    try:
        question = request.get("question", "")
        profile  = request.get("profile", {})
        raw      = profile.get("raw_metadata", {}) or {}

        prompt = f"""You are PhotoIntel's forensic analysis assistant.
        You help users understand why specific images were flagged as suspicious.

        Be direct, technical, and concise. Answer in a maximum of 60–80 words.
        Answer in plain text only. No markdown, no asterisks, no bold, no numbered lists. Write in flowing sentences.

        System developer is Shilo Wexler.


        FORENSIC RULES CONTEXT

        AI Detection:
        resolution divisible by 64, known AI software signatures in EXIF, AI tool names in filename, or unusual aspect ratios typical of generative models.

        GPS Tampering:
        integer coordinates, coordinates outside physical Earth boundaries, or clearly artificial GPS precision patterns.

        Software Editing:
        known editing software detected in EXIF software field (Photoshop, Lightroom, GIMP, etc.).

        Temporal Inconsistency:
        modification date occurs earlier than the original capture date.

        Optical Mismatch:
        camera settings inconsistent with environmental conditions, such as high ISO or long exposure recorded during daytime.

        Altitude Anomaly:
        GPS altitude outside physically plausible range.

        Metadata Absence:
        missing EXIF metadata in images where modern smartphones or cameras normally embed it.

        Device Inconsistency:
        camera make and model combinations that are technically impossible or inconsistent.


        ANALYSIS GUIDELINES

        Base conclusions strictly on the provided metadata and forensic flags.

        Reference specific metadata fields when explaining the reason for suspicion.

        Consider correlations between multiple anomalies. Multiple anomalies strengthen suspicion while a single anomaly may not be conclusive.

        If evidence is insufficient, clearly state that the metadata does not provide conclusive proof of manipulation.

        Never speculate beyond the provided metadata.


        IMAGE FORENSIC PROFILE

        Filename:    {profile.get('filename', 'N/A')}
        Device:      {profile.get('device', 'N/A')}
        Timestamp:   {profile.get('timestamp', 'N/A')}
        Has EXIF:    {profile.get('has_exif', False)}
        Coordinates: {profile.get('latitude', 'N/A')}, {profile.get('longitude', 'N/A')}


        RAW METADATA

        Software:     {raw.get('software', 'N/A')}
        Camera Make:  {raw.get('camera_make', 'N/A')}
        Camera Model: {raw.get('camera_model', 'N/A')}
        ISO:          {raw.get('iso', 'N/A')}
        F-Number:     {raw.get('f_number', 'N/A')}
        Exposure:     {raw.get('exposure_time', 'N/A')}
        Dimensions:   {raw.get('pixel_width', 'N/A')}x{raw.get('pixel_height', 'N/A')}


        TRIGGERED FORENSIC FLAGS

        AI Generated:      {profile.get('ai_issue', False)}
        GPS Tampering:     {profile.get('gps_issue', False)}
        Software Edited:   {profile.get('software_issue', False)}
        Temporal Issue:    {profile.get('temporal_issue', False)}
        Optical Mismatch:  {profile.get('optical_issue', False)}
        Altitude Anomaly:  {profile.get('altitude_issue', False)}
        Virtual Device:    {profile.get('device_issue', False)}


        User question: {question}
        """
        
        model = genai.GenerativeModel("gemini-3-flash-preview")
        response = model.generate_content(prompt)

        logger.info(f"Gemini response for: {profile.get('filename', 'unknown')}")
        return {"answer": response.text}

    except Exception as e:
        logger.exception("Gemini API error.")
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────
# Config.js — inject Cesium token at startup
# ─────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR  = os.path.join(BASE_DIR, "app")

cesium_token = os.environ.get("CESIUM_TOKEN", "")
if cesium_token and os.path.exists(WEB_DIR):
    config_path = os.path.join(WEB_DIR, "config.js")
    with open(config_path, "w") as f:
        f.write(f'const CONFIG = {{ CESIUM_TOKEN: "{cesium_token}" }};')
    logger.info("config.js written with Cesium token.")


# ─────────────────────────────────────────
# Static Frontend
# ─────────────────────────────────────────

if os.path.exists(WEB_DIR):
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="ui")
    logger.info(f"Serving frontend from: {WEB_DIR}")
else:
    logger.warning(f"Frontend directory not found: {WEB_DIR}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)