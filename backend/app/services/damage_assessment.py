"""Image-based flood-coverage estimate (prototype colour heuristic).

This decodes and validates the image for real, then estimates how much of the
frame is floodwater-coloured (muddy brown or blue-grey).  It is deliberately
labelled as an *indicative heuristic*: it does not claim a statistical
confidence and is not a structural assessment.
"""

from __future__ import annotations

import io
import os
import re

import numpy as np
from PIL import Image, UnidentifiedImageError

from app.models.damage_assessment import DamageAssessmentResponse, DamageLevel

MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_IMAGE_PIXELS = 40_000_000
_ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP", "GIF", "BMP"}
_ANALYSIS_SIZE = (96, 96)

# (upper bound of water-coloured coverage in %, level)
_LEVEL_BANDS = (
    (5.0, DamageLevel.NONE),
    (15.0, DamageLevel.MINOR),
    (35.0, DamageLevel.MODERATE),
    (60.0, DamageLevel.SEVERE),
)

_RATIONALES = {
    DamageLevel.NONE: "Little floodwater-coloured area detected in the image.",
    DamageLevel.MINOR: "A small share of the image looks like standing water.",
    DamageLevel.MODERATE: "A substantial share of the image looks like floodwater.",
    DamageLevel.SEVERE: "Most of the visible area looks like floodwater.",
    DamageLevel.CATASTROPHIC: "Nearly the whole visible area looks like floodwater.",
}


def sanitize_filename(filename: str) -> str:
    """Strip any path and unsafe characters so the name is safe to echo into reports."""

    base = os.path.basename(filename.replace("\\", "/")).strip()
    cleaned = re.sub(r"[^\w.\- ]", "_", base)[:80].strip()
    return cleaned or "upload"


def _decode(file_bytes: bytes) -> Image.Image:
    if len(file_bytes) > MAX_IMAGE_BYTES:
        raise ValueError(f"Image is larger than the {MAX_IMAGE_BYTES // (1024 * 1024)} MB limit.")
    Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS
    try:
        with Image.open(io.BytesIO(file_bytes)) as probe:
            image_format = probe.format
            probe.verify()
        if image_format not in _ALLOWED_FORMATS:
            raise ValueError(f"Unsupported image format: {image_format}.")
        image = Image.open(io.BytesIO(file_bytes))
        image.load()
        return image.convert("RGB")
    except ValueError:
        raise
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, SyntaxError) as exc:
        raise ValueError("File is not a valid, readable image (JPEG, PNG, WEBP, GIF or BMP).") from exc


def _water_coverage_pct(image: Image.Image) -> float:
    small = image.resize(_ANALYSIS_SIZE)
    hsv = np.asarray(small.convert("HSV"), dtype=float)
    hue = hsv[..., 0] * 360.0 / 255.0
    sat = hsv[..., 1] / 255.0
    val = hsv[..., 2] / 255.0
    muddy = (hue >= 15) & (hue <= 50) & (sat >= 0.25) & (sat <= 0.75) & (val >= 0.2) & (val <= 0.75)
    blue = (hue >= 180) & (hue <= 260) & (sat >= 0.15) & (val >= 0.2)
    return float(np.mean(muddy | blue) * 100.0)


def assess_image_damage(file_bytes: bytes, filename: str) -> DamageAssessmentResponse:
    """Validate and analyse an incident image."""

    if not file_bytes:
        raise ValueError("Empty file uploaded.")
    coverage = round(_water_coverage_pct(_decode(file_bytes)), 1)
    level = next((lvl for bound, lvl in _LEVEL_BANDS if coverage < bound), DamageLevel.CATASTROPHIC)
    return DamageAssessmentResponse(
        filename=sanitize_filename(filename),
        damage_level=level,
        confidence=None,
        rationale=f"{_RATIONALES[level]} Estimated floodwater-coloured coverage: {coverage}%.",
        water_coverage_pct=coverage,
    )
