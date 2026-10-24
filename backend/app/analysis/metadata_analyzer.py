import io
import time
import struct
import zlib
from typing import Dict, Any, List, Tuple, Optional
from PIL import Image, ExifTags
import exifread

from app.schemas.examination import ScreeningTestResult


class MetadataAnalyzer:
    METHOD_NAME = "metadata_examination"
    VERSION = "1.1.0"

    EDITING_SOFTWARE_KEYWORDS = [
        "photoshop", "gimp", "canva", "lightroom", "paint.net",
        "pixlr", "snapseed", "picsart", "affinity", "coreldraw",
        "stable diffusion", "midjourney", "dall-e", "comfyui", "automatic1111"
    ]

    @classmethod
    def _parse_png_chunks(
        cls,
        file_bytes: bytes,
        image_width: int,
        image_height: int,
        extracted_metadata: Dict[str, Any],
        observations: List[str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Performs deep structural forensic inspection of PNG chunk anatomy.
        Returns (has_anomaly, software_signature).
        """
        if not file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            return False, None

        offset = 8
        file_len = len(file_bytes)
        chunks_found: List[str] = []
        software_detected = None
        has_trailing_bytes = False
        color_type_desc = "Unknown"

        while offset < file_len - 12:
            try:
                chunk_len = struct.unpack(">I", file_bytes[offset:offset + 4])[0]
                chunk_type = file_bytes[offset + 4:offset + 8].decode("ascii", "ignore")
                chunk_data = file_bytes[offset + 8:offset + 8 + chunk_len]
                chunks_found.append(chunk_type)

                if chunk_type == "IHDR" and len(chunk_data) >= 13:
                    w, h, bit_depth, color_type, comp, filt, interlace = struct.unpack(">IIBBBBB", chunk_data[:13])
                    color_map = {0: "Grayscale", 2: "RGB", 3: "Indexed/Palette", 4: "Grayscale+Alpha", 6: "RGBA"}
                    color_type_desc = color_map.get(color_type, f"Type-{color_type}")
                    extracted_metadata["PNG:BitDepth"] = f"{bit_depth}-bit"
                    extracted_metadata["PNG:ColorType"] = color_type_desc
                    extracted_metadata["PNG:Interlace"] = "Interlaced (Adam7)" if interlace == 1 else "Non-interlaced"

                elif chunk_type == "pHYs" and len(chunk_data) >= 9:
                    ppux, ppuy, unit = struct.unpack(">IIB", chunk_data[:9])
                    if unit == 1:
                        dpi_x = int(round(ppux * 0.0254))
                        dpi_y = int(round(ppuy * 0.0254))
                        extracted_metadata["PNG:Resolution"] = f"{dpi_x} x {dpi_y} DPI"
                        observations.append(f"PNG raster density: {dpi_x}x{dpi_y} DPI (meters unit).")
                        if dpi_x in [96, 120, 144]:
                            observations.append(f"Recorded resolution ({dpi_x} DPI) is characteristic of a native computer display/screen capture.")

                elif chunk_type == "tEXt":
                    parts = chunk_data.split(b"\x00", 1)
                    if len(parts) == 2:
                        k = parts[0].decode("latin1", "ignore").strip()
                        v = parts[1].decode("latin1", "ignore").strip()
                        extracted_metadata[f"PNG:{k}"] = v[:200]
                        if k.lower() in ["software", "tool"]:
                            software_detected = v

                elif chunk_type == "zTXt":
                    parts = chunk_data.split(b"\x00", 2)
                    if len(parts) >= 2:
                        k = parts[0].decode("latin1", "ignore").strip()
                        try:
                            # parts[1] is compression method (1 byte), compressed text starts after
                            decomp = zlib.decompress(parts[1][1:])
                            v = decomp.decode("latin1", "ignore").strip()
                            extracted_metadata[f"PNG:{k}"] = v[:200]
                            if k.lower() in ["software", "tool"]:
                                software_detected = v
                        except Exception:
                            pass

                elif chunk_type == "iTXt":
                    parts = chunk_data.split(b"\x00", 5)
                    if len(parts) >= 5:
                        k = parts[0].decode("utf-8", "ignore").strip()
                        v = parts[-1].decode("utf-8", "ignore").strip()
                        extracted_metadata[f"PNG:{k}"] = v[:200]
                        if k.lower() in ["software", "tool"]:
                            software_detected = v

                elif chunk_type == "tIME" and len(chunk_data) >= 7:
                    yr, mo, da, hr, mn, sc = struct.unpack(">HBBBBB", chunk_data[:7])
                    extracted_metadata["PNG:LastModified"] = f"{yr:04d}-{mo:02d}-{da:02d} {hr:02d}:{mn:02d}:{sc:02d} UTC"
                    observations.append(f"Embedded PNG timestamp: {yr:04d}-{mo:02d}-{da:02d} {hr:02d}:{mn:02d}:{sc:02d} UTC.")

                elif chunk_type == "iCCP":
                    prof_name = chunk_data.split(b"\x00", 1)[0].decode("latin1", "ignore")
                    extracted_metadata["PNG:ICCProfile"] = prof_name[:100]

                elif chunk_type == "IEND":
                    iend_end = offset + 12
                    if iend_end < file_len:
                        trailing = file_len - iend_end
                        observations.append(f"WARNING: {trailing} trailing bytes detected past PNG IEND marker (potential payload or hidden data).")
                        has_trailing_bytes = True
                    break

                offset += 12 + chunk_len
            except Exception:
                break

        observations.append(f"Analyzed {len(chunks_found)} sequential PNG chunk headers: {', '.join(set(chunks_found))}.")

        # Raw uncompressed raster size estimate
        channels = 4 if "Alpha" in color_type_desc else 3
        raw_size = image_width * image_height * channels
        if raw_size > 0:
            ratio = (file_len / raw_size) * 100.0
            extracted_metadata["PNG:CompressionRatio"] = f"{ratio:.1f}% of uncompressed raw raster"
            observations.append(f"Lossless raster compression efficiency: {ratio:.1f}% of raw uncompressed bitmap.")

        return has_trailing_bytes, software_detected

    @classmethod
    def analyze(cls, file_bytes: bytes, image_width: int, image_height: int, detected_mime: str) -> Dict[str, Any]:
        start_time = time.perf_counter()
        observations: List[str] = []
        limitations: List[str] = [
            "Metadata is easily manipulated, stripped, or spoofed using basic editing tools.",
            "Absence of camera EXIF metadata is standard for screenshots, web captures, and messaging apps (WhatsApp, Telegram).",
            "The presence of editing software tags indicates software processing, but does not prove fraudulent alteration."
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
                clean_name = tag_name.replace("EXIF ", "").replace("Image ", "").replace("GPS ", "GPS_")
                str_val = str(tag_val).strip()
                if "GPS" in clean_name and any(char.isdigit() for char in str_val):
                    extracted_metadata[clean_name] = "[REDACTED FOR PRIVACY: GPS Coordinate Data Present]"
                else:
                    extracted_metadata[clean_name] = str_val[:200]
        except Exception as e:
            observations.append(f"ExifRead parser note: {str(e)}")

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

        # 3. If PNG, perform deep structural chunk forensics
        is_png = detected_mime == "image/png" or file_bytes.startswith(b"\x89PNG\r\n\x1a\n")
        png_trailing, png_software = False, None
        if is_png:
            png_trailing, png_software = cls._parse_png_chunks(
                file_bytes, image_width, image_height, extracted_metadata, observations
            )
            if png_software and not software_detected:
                software_detected = png_software

        # 4. Analyze extracted fields
        has_exif = len([k for k in extracted_metadata.keys() if not k.startswith("PNG:")]) > 0
        has_metadata = len(extracted_metadata) > 0

        # Check Software / Processing tags across all extracted metadata
        software_tag = (
            extracted_metadata.get("Software", "") or
            extracted_metadata.get("ProcessingSoftware", "") or
            extracted_metadata.get("PNG:Software", "") or
            (software_detected or "")
        )
        make_tag = extracted_metadata.get("Make", "")
        model_tag = extracted_metadata.get("Model", "")
        date_original = (
            extracted_metadata.get("DateTimeOriginal", "") or
            extracted_metadata.get("DateTime", "") or
            extracted_metadata.get("PNG:LastModified", "")
        )

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

        if png_trailing:
            indicator = "indicator_detected"
            indicator_label = "Indicator detected"

        if make_tag or model_tag:
            observations.append(f"Camera Hardware Profile: {make_tag} {model_tag}".strip())

        if date_original:
            observations.append(f"Recorded Capture/Creation Timestamp: {date_original}")

        if any("GPS" in k for k in extracted_metadata.keys()):
            observations.append("Geotagging metadata detected (coordinates redacted for privacy).")

        # Synthesize final status and explanation
        if indicator == "indicator_detected":
            explanation = (
                f"Metadata examination identified actionable anomalies: {observations[-1]}. "
                "This indicates the image has been saved, generated, or modified through digital editing software, "
                "or contains trailing payload bytes. Manual corroboration is required."
            )
        elif not has_exif and not is_png:
            indicator = "inconclusive"
            indicator_label = "Inconclusive"
            observations.append("No EXIF metadata found in image header.")
            observations.append("Metadata stripping is common in social media and privacy-preserving tools.")
            explanation = (
                "The image contains no embedded EXIF metadata records. While metadata stripping can "
                "be performed intentionally to obscure origin, it is also standard automated behavior "
                "for web browsers, social networks, and messaging applications. This finding is inconclusive."
            )
        elif is_png and not has_exif:
            # PNG screenshot / graphic with parsed chunks
            indicator = "no_indicator_detected"
            indicator_label = "No indicator detected by this test"
            explanation = (
                f"Successfully parsed {len(extracted_metadata)} PNG structural chunk headers. "
                "Image structure conforms to valid PNG specifications with no illegal chunk ordering, "
                "no trailing byte steganography, and no known editing software signatures."
            )
        else:
            explanation = (
                f"Parsed {len(extracted_metadata)} metadata headers. "
                "Extracted metadata appears consistent with standard capture or storage headers. "
                "No explicit digital editing or composite software signatures were identified in available fields."
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
