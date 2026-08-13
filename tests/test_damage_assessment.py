"""Tests for the image-based damage assessment fallback classifier."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.damage_assessment import DamageLevel


def test_assess_image_damage_valid_jpeg():
    """Verify that uploading a valid dummy JPEG returns a deterministic valid response."""
    # Create a minimal valid JPEG header
    dummy_jpeg = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    
    with TestClient(app) as client:
        files = {"file": ("incident1.jpg", dummy_jpeg, "image/jpeg")}
        response = client.post("/api/v1/assess-damage", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["filename"] == "incident1.jpg"
        assert data["damage_level"] in [level.value for level in DamageLevel]
        assert 72.0 <= data["confidence"] <= 100.0
        assert len(data["rationale"]) > 0


def test_assess_image_damage_valid_png():
    """Verify that uploading a valid dummy PNG returns a deterministic valid response."""
    # Minimal valid PNG header
    dummy_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    
    with TestClient(app) as client:
        files = {"file": ("incident2.png", dummy_png, "image/png")}
        response = client.post("/api/v1/assess-damage", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["filename"] == "incident2.png"
        assert data["damage_level"] in [level.value for level in DamageLevel]


def test_assess_image_damage_unsupported_input():
    """Verify that uploading a non-image file results in a 400 Bad Request."""
    dummy_text = b"This is not an image file. It is a text file."
    
    with TestClient(app) as client:
        files = {"file": ("document.txt", dummy_text, "text/plain")}
        response = client.post("/api/v1/assess-damage", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "Unsupported file format" in data["detail"]


def test_assess_image_damage_empty_file():
    """Verify that uploading an empty file results in a 400 Bad Request."""
    dummy_empty = b""
    
    with TestClient(app) as client:
        files = {"file": ("empty.jpg", dummy_empty, "image/jpeg")}
        response = client.post("/api/v1/assess-damage", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "Empty file uploaded" in data["detail"]
