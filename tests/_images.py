"""Helpers that build real in-memory images for tests."""

from __future__ import annotations

import io

from PIL import Image

MUDDY = (150, 110, 60)   # floodwater-coloured
BLUE = (40, 90, 160)     # water-coloured
GREEN = (40, 160, 60)    # not water
GRAY = (128, 128, 128)   # not water


def make_image(color=MUDDY, fmt: str = "PNG", size=(64, 64)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, format=fmt)
    return buffer.getvalue()
