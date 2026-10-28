import io
from pathlib import Path
from PIL import Image
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_v2_pipeline_end_to_end(tmp_path):
    # Create test JPEG
    img = Image.new("RGB", (400, 300), color=(80, 120, 160))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=90)
    raw_bytes = buf.getvalue()

    response = client.post(
        "/api/examinations",
        files={"file": ("v2_specimen.jpg", raw_bytes, "image/jpeg")}
    )
    assert response.status_code == 201
    data = response.json()

    # Verify SATYA v2 Top-Level Fields
    assert "decision_assessment" in data
    assert data["decision_assessment"] in ["LIKELY_AUTHENTIC", "LIKELY_TAMPERED", "INCONCLUSIVE"]
    assert "evidence_strength" in data
    assert "image_characterization" in data
    assert data["image_characterization"]["format"] == "JPEG"
    assert "detector_results" in data
    assert len(data["detector_results"]) >= 12

    # Check detector result structure
    for d_res in data["detector_results"]:
        assert "detector_name" in d_res
        assert "status" in d_res
        assert d_res["status"] in ["POSITIVE", "NEGATIVE", "INCONCLUSIVE", "NOT_APPLICABLE", "ERROR"]
        assert "evidence_strength" in d_res
        assert "technical_reason" in d_res

    # Check Composite Heatmap in artifacts
    assert "composite_evidence_map" in data["artifacts"] or "noise_residual_map" in data["artifacts"]

    # Verify JSON Report Endpoint (endpoint is /report, returns JSON by default)
    exam_id = data["examination_id"]
    json_res = client.get(f"/api/examinations/{exam_id}/report")
    assert json_res.status_code == 200
    report = json_res.json()
    assert "technical_assessment" in report
    assert report["technical_assessment"]["decision_assessment"] == data["decision_assessment"]
    assert report["technical_assessment"]["human_review_required"] is True

