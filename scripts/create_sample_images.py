import io
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import piexif

sample_dir = Path(__file__).resolve().parent.parent / "storage" / "samples"
sample_dir.mkdir(parents=True, exist_ok=True)


def create_authentic_sample():
    """Generates a clean synthetic camera sample with standard EXIF metadata."""
    img = Image.new("RGB", (640, 480), color=(135, 206, 235))  # Sky blue
    draw = ImageDraw.Draw(img)
    # Add natural landscape elements
    draw.rectangle([0, 300, 640, 480], fill=(34, 139, 34))  # Green ground
    draw.ellipse([450, 60, 550, 160], fill=(255, 215, 0))  # Sun

    # Synthesize standard camera EXIF
    zeroth_ifd = {
        piexif.ImageIFD.Make: b"Nikon Corporation",
        piexif.ImageIFD.Model: b"NIKON D850",
        piexif.ImageIFD.Software: b"Ver.1.20",
        piexif.ImageIFD.DateTime: b"2026:08:15 10:24:30",
    }
    exif_ifd = {
        piexif.ExifIFD.DateTimeOriginal: b"2026:08:15 10:24:30",
        piexif.ExifIFD.ExposureTime: (1, 500),
        piexif.ExifIFD.FNumber: (28, 10),
        piexif.ExifIFD.ISOSpeedRatings: 100,
    }
    exif_dict = {"0th": zeroth_ifd, "Exif": exif_ifd}
    exif_bytes = piexif.dump(exif_dict)

    file_path = sample_dir / "sample_authentic_camera.jpg"
    img.save(file_path, "JPEG", quality=95, exif=exif_bytes)
    print(f"Created: {file_path}")


def create_tampered_sample():
    """Generates a synthetic composite image with Adobe Photoshop EXIF metadata and spliced patch."""
    base = Image.new("RGB", (640, 480), color=(240, 240, 240))
    draw = ImageDraw.Draw(base)
    draw.rectangle([50, 50, 590, 430], fill=(200, 220, 240))

    # Save and re-compress at quality 65
    buf = io.BytesIO()
    base.save(buf, "JPEG", quality=65)
    buf.seek(0)
    base_recompressed = Image.open(buf)

    # Insert a foreign patch saved at quality 98 (creating sharp ELA residual variance)
    patch = Image.new("RGB", (180, 180), color=(180, 40, 40))
    patch_draw = ImageDraw.Draw(patch)
    patch_draw.rectangle([20, 20, 160, 160], fill=(255, 200, 0))
    patch_draw.text((30, 80), "SPLICED OBJECT", fill=(0, 0, 0))

    composite = base_recompressed.copy()
    composite.paste(patch, (220, 150))

    # Add Adobe Photoshop EXIF
    zeroth_ifd = {
        piexif.ImageIFD.Make: b"Canon",
        piexif.ImageIFD.Model: b"Canon EOS 5D Mark IV",
        piexif.ImageIFD.Software: b"Adobe Photoshop 2026 (Windows)",
        piexif.ImageIFD.DateTime: b"2026:09:01 14:12:00",
    }
    exif_dict = {"0th": zeroth_ifd}
    exif_bytes = piexif.dump(exif_dict)

    file_path = sample_dir / "sample_tampered_composite.jpg"
    composite.save(file_path, "JPEG", quality=92, exif=exif_bytes)
    print(f"Created: {file_path}")


def create_png_sample():
    """Generates a lossless PNG sample without EXIF."""
    img = Image.new("RGB", (400, 400), color=(50, 50, 70))
    draw = ImageDraw.Draw(img)
    draw.ellipse([100, 100, 300, 300], fill=(100, 200, 150))
    draw.text((120, 190), "LOSSLESS PNG", fill=(255, 255, 255))

    file_path = sample_dir / "sample_lossless.png"
    img.save(file_path, "PNG")
    print(f"Created: {file_path}")


if __name__ == "__main__":
    create_authentic_sample()
    create_tampered_sample()
    create_png_sample()
