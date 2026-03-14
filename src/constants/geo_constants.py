"""
Geographical & Navigation Constants Module
------------------------------------------
Defines spatial limits, physical thresholds, and global bounds used
to detect impossible geographic anomalies (e.g., GPS teleportation).

This configuration ensures that spatial-temporal calculations remain
within the realistic boundaries of human travel and Earth's geometry.
"""

# --- Physical & Geographical Thresholds ---
MAX_ALTITUDE: float = 15000.0     # Max altitude in meters (Accounts for commercial flights)
MIN_ALTITUDE: float = -450.0      # Min altitude in meters (Dead Sea level - GPS fails underground)

EARTH_MAX_LAT: float = 90.0
EARTH_MIN_LAT: float = -90.0
EARTH_MAX_LON: float = 180.0
EARTH_MIN_LON: float = -180.0

# --- Geolocation & Navigation ---
EARTH_RADIUS_KM: float = 6371.0
MAX_SPEED_KMH: float = 1000.0      # Max commercial jet speed (Includes tailwind allowance)
MIN_TIME_DIFF_SEC: float = 1.0     # Minimum time to calculate speed between photos safely
CLUSTER_RADIUS_KM: float = 8.0     # Proximity threshold for location grouping