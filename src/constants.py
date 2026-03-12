"""
Forensic System Constants.

Contains threshold values, signature sets, and configuration constants
used across the forensic analysis pipeline.
"""

# --- Physical & Geographical Thresholds ---
MAX_ALTITUDE = 8000.0       # Max altitude in meters (approx. Everest)
MIN_ALTITUDE = -450.0       # Min altitude in meters (approx. Dead Sea)

EARTH_MAX_LAT = 90.0
EARTH_MIN_LAT = -90.0
EARTH_MAX_LON = 180.0
EARTH_MIN_LON = -180.0

# --- Optical & Exposure Analysis ---
HIGH_ISO = 1600
MIN_HIGH_ISO = 800
LONG_EXPOSURE = 0.1         # Seconds
LOW_NIGHT_F_STOP = 2.0      # Aperture

# --- Temporal Configuration ---
DAY_START = 7               # 07:00 AM
DAY_END = 19                # 07:00 PM
MAX_TIME_DIFF_SEC = 60      # Seconds

# --- Digital Signatures & Artifacts ---

EDITING_SOFTWARE = {
    'photoshop', 'lightroom', 'adobe', 'affinity', 'capture one',
    'gimp', 'krita', 'paint.net', 'darktable', 'rawtherapee', 'corel',
    'paintshop', 'preview', 'windows photo', 'apple photos',
    'photoscape', 'fotor', 'photopea', 'pixlr', 'sumopaint', 'lunapic',
    'befunky', 'snapseed', 'picsart', 'canva', 'polarr', 'vsco',
    'facetune', 'remini', 'lightleap', 'instasize', 'photo director'
}

AI_SOFTWARE = {
    'midjourney', 'stable diffusion', 'stablediffusion', 'dalle', 'dall-e',
    'automatic1111', 'invokeai', 'comfyui', 'runway', 'leonardo',
    'dreamstudio', 'nightcafe', 'nanobanana'
}

VIRTUAL_DEVICE = {
    'emulator', 'simulator', 'virtual', 'vmware', 'androidid',
    'genymotion', 'bluestacks', 'qemu', 'nox', 'memu', 'vbox', 'virtualbox'
}

# --- AI Specific Constants ---
AI_MODULO = 64                    # Math signature of Diffusion models
AI_RESOLUTIONS = {512, 1024}      # Common AI square output sizes

# --- Supported File Extensions --
SUPPORTED_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif', '.avif',
    '.tiff', '.tif', '.raw', '.cr2', '.nef', '.arw', '.dng'
}

# --- Geolocation & Navigation ---
EARTH_RADIUS_KM = 6371.0
MAX_SPEED_KMH = 900.0        # Cruising speed of a commercial jet
MIN_TIME_DIFF_SEC = 1.0      # Minimum time to calculate speed between photos
CLUSTER_RADIUS_KM = 8.0      # Proximity threshold for location grouping

# --- Display Defaults ---
UNKNOWN_DEVICE = 'Unknown Device'


