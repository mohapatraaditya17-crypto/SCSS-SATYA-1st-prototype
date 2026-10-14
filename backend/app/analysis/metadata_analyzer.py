import io
import time
from typing import Dict, Any, List
from PIL import Image, ExifTags
import exifread

from app.schemas.examination import ScreeningTestResult


class MetadataAnalyzer:
    METHOD_NAME = "metadata_examination"
    VERSION = "1.0.0"

    EDITING_SOFTWARE_KEYWORDS = [
        "photoshop", "gimp", "canva", "lightroom", "paint.net",
        "pixlr", "snapseed", "picsart", "affinity", "coreldraw",
        "stable diffusion", "midjourney", "dall-e", "comfyui", "automatic1111"
    ]

    @classmethod
    def analyze(cls, file_bytes: bytes, image_width: int, image_height: int, detected_mime: str) -> Dict[str, Any]:
        start_time = time.perf_counter()
        observations: List[str] = []
        limitations: List[str] = [
            "Metadata is easily manipulated, stripped, or spoofed using basic editing tools.",
            "Absence of EXIF metadata is standard across messaging platforms (WhatsApp, Telegram) and does not establish tampering.",
            "The presence of editing software tags indicates software processing, but does not prove fraudulent or substantive alteration."
        ]
        extracted_metadata: Dict[str, Any] = {}
        indicator = "no_indicator_detected"
        indicator_label = "No indicator detected by this test"
        software_detected = None

        # 1. Extract EXIF via exifread
        try:
            tags = exifread.process_file(io.BytesIO(file_bytes), details=False)
            for tag_name, tag_val in tags.items():
                if tag_name.startswith("JPEGThumbnail"):
                    continue
                # Sanitize tag name
                clean_name = tag_name.replace("EXIF ", "").replace("Image ", "").replace("GPS ", "GPS_")
                str_val = str(tag_val).strip()
                if "GPS" in clean_name and any(char.isdigit() for char in str_val):
                    # Redact GPS exact coordinates for privacy compliance
                    extracted_metadata[clean_name] = "[REDACTED FOR PRIVACY: GPS Coordinate Data Present]"
                else:
                    extracted_metadata[clean_name] = str_val[:200]
        except Exception as e:
            observations.append(f"ExifRead parser warning: {str(e)}")

        # 2. Extract standard PIL EXIF if available
        try:
            with Image.open(io.BytesIO(file_bytes)) as img:
                exif_data = img.getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                        if tag_name not in extracted_metadata and not isinstance(value, bytes):
                            extracted_metadata[tag_name] = str(value)[:200]
        except Exception:
            pass

        # 3. Analyze extracted fields
        has_exif = len(extracted_metadata) > 0
        if not has_exif:
            indicator = "inconclusive"
            indicator_label = "Inconclusive"
            observations.append("No EXIF metadata found in image header.")
            observations.append("Metadata stripping is common in social media and privacy-preserving tools.")
            explanation = (
                "The image contains no embedded EXIF metadata records. While metadata stripping can "
                "be performed intentionally to obscure origin, it is also standard automated behavior "
                "for web browsers, social networks, and messaging applications. This finding is inconclusive."
            )
        else:
            observations.append(f"Successfully parsed {len(extracted_metadata)} metadata headers.")

            # Check Software / Processing tags
            software_tag = extracted_metadata.get("Software", "") or extracted_metadata.get("ProcessingSoftware", "")
            make_tag = extracted_metadata.get("Make", "")
            model_tag = extracted_metadata.get("Model", "")
            date_original = extracted_metadata.get("DateTimeOriginal", "") or extracted_metadata.get("DateTime", "")

            if software_tag:
                observations.append(f"Recorded Software/Tool: '{software_tag}'.")
                lower_soft = software_tag.lower()
                for keyword in cls.EDITING_SOFTWARE_KEYWORDS:
                    if keyword in lower_soft:
                        software_detected = software_tag
                        indicator = "indicator_detected"
                        indicator_label = "Indicator detected"
                        observations.append(f"Editing software signature identified: '{software_tag}'.")
                        break

            if make_tag or model_tag:
                observations.append(f"Camera Hardware Profile: {make_tag} {model_tag}".strip())

            if date_original:
                observations.append(f"Recorded Capture Timestamp: {date_original}")

            if any("GPS" in k for k in extracted_metadata.keys()):
                observations.append("Geotagging metadata detected (coordinates redacted for privacy).")

            if indicator == "indicator_detected":
                explanation = (
                    f"Metadata examination identified software signatures associated with post-processing "
                    f"or synthetic generation software ('{software_detected}'). This indicates the image has "
                    f"been saved or exported through digital editing software. However, this observation alone "
                    f"does not establish malicious alteration, as routine format conversion and resizing "
                    f"also produce editing signatures."
                )
            else:
                explanation = (
                    "Extracted metadata appears consistent with standard capture or storage headers. "
                    "No explicit digital editing or composite software signatures were identified in the "
                    "available EXIF fields. Note that missing or manipulated fields cannot be ruled out "
                    "from metadata analysis alone."
                )

        exec_time = round((time.perf_counter() - start_time) * 1000, 2)

        test_result = ScreeningTestResult(
            method=cls.METHOD_NAME,
            version=cls.VERSION,
            status="completed",
            indicator=indicator,
            indicator_label=indicator_label,
            observations=observations,
            explanation=explanation,
            limitations=limitations,
            execution_time_ms=exec_time,
        )

        return {
            "test_result": test_result,
            "extracted_metadata": extracted_metadata,
        }
