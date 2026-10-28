import io
from pathlib import Path
from PIL import Image
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_path_traversal_filename_sanitization():
    # Attempt directory traversal attack via filename
    img = Image.new("RGB", (100, 100), color=(50, 100, 150))
    buf = io.BytesIO()
    img.save(buf, "JPEG")
    raw_bytes = buf.getvalue()

    malicious_filenames = [
        "../../../../etc/shadow.jpg",
        "..\\..\\..\\windows\\system32\\calc.jpg",
        "....//....//traversal.jpg",
        "\x00hidden.jpg",
    ]

    for fname in malicious_filenames:
        res = client.post(
            "/api/examinations",
            files={"file": (fname, raw_bytes, "image/jpeg")}
        )
        assert res.status_code == 201
        data = res.json()
        stored_name = data["original_filename"]
        # Ensure path traversal components are completely stripped
        assert "/" not in stored_name
        assert "\\" not in stored_name
        assert ".." not in stored_name
        assert "\x00" not in stored_name


def test_polyglot_executable_rejection():
    # Simulate executable polyglot (PE header) disguised as JPEG
    polyglot_bytes = b"MZ\x90\x00" + b"\xFF\xD8\xFF\xE0" + b"\x00" * 50
    res = client.post(
        "/api/examinations",
        files={"file": ("malicious.jpg", polyglot_bytes, "image/jpeg")}
    )
    assert res.status_code == 400
    assert "rejected" in res.json()["detail"].lower() or "unsupported" in res.json()["detail"].lower()


def test_decompression_bomb_dimension_limit(monkeypatch):
    # Set limit to 1,000,000 pixels for testing
    monkeypatch.setattr(settings, "MAX_IMAGE_PIXELS", 500_000)

    # Image with 600,000 pixels (1000x600)
    large_img = Image.new("RGB", (1000, 600), color=(100, 100, 100))
    buf = io.BytesIO()
    large_img.save(buf, "JPEG")
    large_bytes = buf.getvalue()

    res = client.post(
        "/api/examinations",
        files={"file": ("bomb.jpg", large_bytes, "image/jpeg")}
    )
    assert res.status_code == 400
    assert "exceeds maximum permitted limit" in res.json()["detail"].lower() or "pixel" in res.json()["detail"].lower()

