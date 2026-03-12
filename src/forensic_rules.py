
"""
Forensic Rules Engine.

This module provides a suite of analysis rules to detect anomalies,
physical inconsistencies, and synthetic signatures in image metadata.
"""


from typing import Optional

import src.constants as constants
from src.converters import parse_date
from src.models import ImageMetadata


def is_ai_generated(metadata: ImageMetadata) -> bool:
    """
    Identifies digital signatures of Generative AI tools.

    Args:
        metadata (ImageMetadata): The object containing image metadata.

    Returns:
        bool: True if AI-generation evidence is found, False otherwise.
    """

    ai_in_fields = _check_text_signatures(
        metadata, constants.AI_SOFTWARE
    )

    if ai_in_fields:
        return True

    w, h = metadata.pixel_width, metadata.pixel_height

    if w and h:
       return ((w == h and w in constants.AI_RESOLUTIONS)
            or (w % constants.AI_MODULO == 0 and h % constants.AI_MODULO == 0))

    return False


def is_altitude_anomaly(metadata: ImageMetadata) -> bool:
    """
    Detects suspicious altitude values that are physically improbable.

    Args:
        metadata (ImageMetadata): The object containing image metadata.

    Returns:
        bool: True if altitude is outside plausible bounds, False otherwise.
    """

    if metadata.altitude is None:
        return False

    too_high = metadata.altitude > constants.MAX_ALTITUDE
    too_low = metadata.altitude < constants.MIN_ALTITUDE

    return too_high or too_low


def has_gps_issue(metadata: ImageMetadata) -> bool:
    """
    Performs a comprehensive integrity check on GPS data.

    Checks for multiple anomalies:
    1. Out-of-bounds coordinates (physically impossible locations).
    2. Manual injection (coordinates lacking standard sensor precision).

    Args:
        metadata (ImageMetadata): The extracted image metadata.

    Returns:
        bool: True if ANY GPS anomaly is detected, False otherwise.
    """

    if not metadata.has_gps or None in (
            metadata.longitude, metadata.latitude
    ):
        return False

    is_lat_valid = (
            constants.EARTH_MIN_LAT <=
            metadata.latitude <=
            constants.EARTH_MAX_LAT
    )

    if not is_lat_valid:
        return True

    is_lon_valid = (
            constants.EARTH_MIN_LON <=
            metadata.longitude <=
            constants.EARTH_MAX_LON
    )

    if not is_lon_valid:
        return True

    is_injected = (
            metadata.latitude.is_integer() or
            metadata.longitude.is_integer()
    )

    if is_injected:
        return True

    return False


def has_optical_issue(metadata: ImageMetadata) -> bool:
    """
    Checks for exposure parameter inconsistencies based on basic optical rules.

    Args:
        metadata (ImageMetadata): Image metadata.

    Returns:
        bool: True if ISO, aperture, and exposure settings appear physically inconsistent.
    """

    is_day = _is_daytime(metadata.datetime)
    iso = metadata.iso
    f_num = metadata.f_number
    exp_t = metadata.exposure_time

    if not is_day:
        return False

    high_iso_check = (
                      iso is not None
                      and iso >= constants.HIGH_ISO
                      )

    long_exp_check = (
                      exp_t is not None
                      and exp_t > constants.LONG_EXPOSURE
                     )

    f_num_iso_check = (
                      f_num is not None
                      and f_num < constants.LOW_NIGHT_F_STOP
                      and iso is not None
                      and iso >= constants.MIN_HIGH_ISO
                       )

    return any([
        high_iso_check,
        long_exp_check,
        f_num_iso_check
    ])


def has_software_issue(metadata: ImageMetadata) -> bool:
    """
    Detects traces of known image editing software in metadata.

    Args:
        metadata (ImageMetadata): Image metadata.

    Returns:
        bool: True if a known editing tool is found, False otherwise
    """

    return _check_text_signatures(
        metadata, constants.EDITING_SOFTWARE
    )


def has_virtual_device_issue(metadata: ImageMetadata) -> bool:
    """
    Detects signatures of emulators or virtual devices in the hardware metadata.

    Args:
        metadata (ImageMetadata): Image metadata.

    Returns:
        bool: True if virtual device traces are found in make, model, or software fields.
    """

    return _check_text_signatures(
        metadata, constants.VIRTUAL_DEVICE
    )


def has_temporal_issue(metadata: ImageMetadata) -> bool:
    """
    Detects chronological contradictions between capture time and modification time.

    Args:
        metadata (ImageMetadata): Image metadata.

    Returns:
        bool: True if the modification date is earlier than the capture date.
    """

    capture_date = parse_date(metadata.datetime)
    modify_date = parse_date(metadata.modify_date)

    if None in {capture_date, modify_date}:
        return False

    return modify_date < capture_date


def _is_daytime(date: Optional[str]) -> bool:
    """
    Helper to determine if the hour is within daytime limits.

    Args:
        date (Optional[str]): The raw date string to evaluate.

    Returns:
        True if the time falls between 07:00 and 19:00, False otherwise.
    """

    dt_obj = parse_date(date)

    if not dt_obj:
        return False

    return constants.DAY_START <= dt_obj.hour <= constants.DAY_END


def _check_text_signatures(metadata: ImageMetadata, signatures: set) -> bool:
    """
    Helper function to scan metadata text fields for specific signatures.

    Args:
        metadata (ImageMetadata): Image metadata.
        signatures (set): A set of lowercase signature strings to search for.

    Returns:
          bool: True if any of the signatures are found, False otherwise.
    """

    make = (metadata.camera_make or '').lower()
    model = (metadata.camera_model or '').lower()
    software = (metadata.software or '').lower()

    hardware_info = f"{make} {model} {software}".strip()

    if not hardware_info:
        return False

    return any(sig in hardware_info for
               sig in signatures if sig)