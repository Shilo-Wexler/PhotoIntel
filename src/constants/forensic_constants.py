"""
Forensic System Constants Module
--------------------------------
Defines static thresholds, heuristic boundaries, and known threat signatures
used by the forensic analysis engine to evaluate image integrity.

This module acts as the central tuning layer for the system, allowing detection
rules and sensitivity levels to be updated without altering the core logic.
"""

# --- Optical & Exposure Analysis ---
HIGH_ISO: int = 1600
MIN_HIGH_ISO: int = 800
LONG_EXPOSURE: float = 0.1         # Seconds
LOW_NIGHT_F_STOP: float = 2.0      # Aperture

# --- Temporal Configuration ---
DAY_START: int = 7                 # 07:00 AM
DAY_END: int = 19                  # 07:00 PM
MAX_TIME_DIFF_SEC: int = 60        # Seconds

# --- Digital Signatures & Artifacts ---
EDITING_SOFTWARE: set[str] = {
    'photoshop', 'lightroom', 'adobe', 'affinity', 'capture one',
    'gimp', 'krita', 'paint.net', 'darktable', 'rawtherapee', 'corel',
    'paintshop', 'preview', 'windows photo', 'apple photos',
    'photoscape', 'fotor', 'photopea', 'pixlr', 'sumopaint', 'lunapic',
    'befunky', 'snapseed', 'picsart', 'canva', 'polarr', 'vsco',
    'facetune', 'remini', 'lightleap', 'instasize', 'photo director'
}

AI_SOFTWARE: set[str] = {
    'midjourney', 'stable diffusion', 'stablediffusion', 'dalle', 'dall-e',
    'automatic1111', 'invokeai', 'comfyui', 'runway', 'leonardo',
    'dreamstudio', 'nightcafe', 'nanobanana', 'sora', 'copilot',
    'firefly', 'adobe firefly', 'bing image', 'flux', 'ideogram',
    'gemini', 'imagen', 'ideogram', 'grok'
}

VIRTUAL_DEVICE: set[str] = {
    'emulator', 'simulator', 'virtual', 'vmware', 'androidid',
    'genymotion', 'bluestacks', 'qemu', 'nox', 'memu', 'vbox', 'virtualbox'
}
# --- AI & Geometry Specific Constants ---
AI_MODULO: int = 64                    # Math signature of Diffusion models
AI_RESOLUTIONS: set[int] = {           # Added 768 & 2048 for broader SD coverage
        512, 640, 768, 896, 1024,
        1152, 1280, 1344, 1536, 2048
}

# Standard aspect ratios in photography (Requires rounding to 2 decimal places before lookup)
STANDARD_ASPECT_RATIOS: set[float] = {
    1.33,   # 4:3 (Most Smartphones)
    0.75,   # 3:4 (Portrait Smartphone)
    1.5,    # 3:2 (DSLR / Mirrorless)
    0.67,   # 2:3 (Portrait Professional)
    1.78,   # 16:9 (Wide / Video)
    0.56    # 9:16 (Story / Social)
}

# --- Supported File Extensions ---
SUPPORTED_EXTENSIONS: set[str] = {
    '.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif', '.avif',
    '.tiff', '.tif', '.raw', '.cr2', '.nef', '.arw', '.dng'
}

# --- Display Defaults ---
UNKNOWN_DEVICE: str = 'Unknown Device'