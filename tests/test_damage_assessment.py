"""Tests for image validation and the colour-coverage damage heuristic."""

from fastapi.testclient import TestClient

from app.main import app
from app.models.damage_assessment import DamageLevel
from app.services.damage_assessment import assess_image_damage, sanitize_filename
from tests._images import BLUE, GRAY, GREEN, MUDDY, make_image


def _post(client, name, content, mime="image/png"):
    return client.post("/api/v1/assess-damage", files={"file": (name, content, mime)})


def test_valid_png_and_jpeg_are_assessed_without_fake_confidence():
    with TestClient(app) as client:
        for name, fmt, mime in (("incident1.jpg", "JPEG", "image/jpeg"), ("incident2.png", "PNG", "image/png")):
            response = _post(client, name, make_image(MUDDY, fmt), mime)
            assert response.status_code == 200
            data = response.json()
            assert data["filename"] == name
            assert data["damage_level"] in [level.value for level in DamageLevel]
            assert data["confidence"] is None  # no fabricated statistical confidence
            assert data["method"] == "heuristic_water_color_coverage"
            assert "disclaimer" in data


def test_result_depends_on_image_content_not_on_bytes_hash():
    wet = assess_image_damage(make_image(MUDDY), "a.png")
    blue = assess_image_damage(make_image(BLUE), "b.png")
    dry_green = assess_image_damage(make_image(GREEN), "c.png")
    dry_gray = assess_image_damage(make_image(GRAY), "d.png")
    assert wet.damage_level == DamageLevel.CATASTROPHIC and wet.water_coverage_pct == 100.0
    assert blue.damage_level == DamageLevel.CATASTROPHIC
    assert dry_green.damage_level == DamageLevel.NONE and dry_gray.damage_level == DamageLevel.NONE
    # Same content re-encoded differently gives the same verdict (a byte hash would not).
    assert assess_image_damage(make_image(MUDDY, "PNG"), "x.png").damage_level == \
        assess_image_damage(make_image(MUDDY, "JPEG"), "x.jpg").damage_level


def test_non_images_are_rejected_even_with_image_extension_or_magic_bytes():
    with TestClient(app) as client:
        assert _post(client, "evil.jpg", b"this is plain text, not an image", "image/jpeg").status_code == 400
        assert _post(client, "x.exe", b"\xff\xd8 fake jpeg magic bytes only").status_code == 400
        assert _post(client, "document.txt", b"This is not an image file.", "text/plain").status_code == 400


def test_empty_file_is_rejected():
    with TestClient(app) as client:
        response = _post(client, "empty.jpg", b"", "image/jpeg")
        assert response.status_code == 400
        assert "Empty file uploaded" in response.json()["detail"]


def test_oversized_upload_is_rejected_with_413():
    with TestClient(app) as client:
        response = _post(client, "big.jpg", b"\xff\xd8" + b"0" * (9 * 1024 * 1024), "image/jpeg")
        assert response.status_code == 413


def test_filename_is_sanitized_before_being_echoed():
    assert sanitize_filename("../../etc/passwd") == "passwd"
    cleaned = sanitize_filename("<script>alert(1)</script>.png")
    assert "<" not in cleaned and ">" not in cleaned and "(" not in cleaned
