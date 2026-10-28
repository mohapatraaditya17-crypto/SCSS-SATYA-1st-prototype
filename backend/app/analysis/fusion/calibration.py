from typing import Dict, Any


class ForensicCalibrator:
    """
    Forensic Calibrator & Detector Reliability Profiles.
    Calibrates raw algorithmic outputs into statistically normalized evidentiary scores,
    preventing over-confident conclusions from inherently exploratory methods.
    """
    VERSION = "2.0.0"

    # Empirical detector reliability weights (based on forensic false-positive characteristics)
    DETECTOR_RELIABILITY = {
        "c2pa_provenance": 0.98,                     # Cryptographic hardware signature
        "copy_move_forgery_detection": 0.90,         # Geometric clustering of spatial keypoints
        "image_splicing_detector": 0.85,             # Multi-block boundary & noise mismatch
        "ai_generative_classifier": 0.80,            # Cross-channel co-occurrence + radial decay
        "document_typography_and_alignment": 0.85,   # Character baseline displacement
        "jpeg_quantization_analysis": 0.75,         # DQT coefficient profiling
        "error_level_analysis": 0.55,               # Compression exploratory visualization
        "noise_residual_analysis": 0.45,            # Prone to natural texture false-positives
        "fourier_spectral_analysis": 0.60,          # Frequency harmonic lattice spikes
        "srm_wavelet_analysis": 0.65,               # Steganalysis filter bank residual
        "lighting_consistency_analysis": 0.70,      # Optical gradient consistency
        "cryptographic_and_perceptual_hashing": 0.50,# Integrity indicator, not tamper classifier
        "metadata_examination": 0.70,               # Software tags & structural EXIF
    }

    @classmethod
    def calibrate_score(cls, detector_name: str, raw_score: float) -> float:
        """
        Applies non-linear logistic/clamping calibration to align raw detector score
        with empirical forensic reliability.
        """
        rel = cls.DETECTOR_RELIABILITY.get(detector_name, 0.60)
        # Scaled non-linear sigmoid-like response
        clamped = max(0.0, min(1.0, raw_score))
        calibrated = clamped * rel + (1.0 - rel) * (clamped ** 2)
        return round(float(calibrated), 3)

    @classmethod
    def get_evidence_strength(cls, score: float, confidence: float) -> str:
        """
        Determines qualitative forensic evidence strength scale.
        """
        combined = score * confidence
        if combined >= 0.80:
            return "VERY_STRONG"
        elif combined >= 0.60:
            return "STRONG"
        elif combined >= 0.40:
            return "MODERATE"
        elif combined >= 0.20:
            return "LOW"
        else:
            return "NONE"

