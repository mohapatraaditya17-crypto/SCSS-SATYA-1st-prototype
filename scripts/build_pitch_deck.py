"""
SCSS SATYA — Official Pitch Deck Builder v2026.3
SEVA FIRST Innovation Challenge 2026 • Maharashtra / Chhattisgarh
Sector 9: Responsible AI, Deepfake Detection & Digital Trust

Generates a professional 16:9 PowerPoint with SCSS Navy (#0F1E36) & Gold (#C5A059) branding.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Pt
from pptx.enum.dml import MSO_THEME_COLOR
import datetime
import os

# ── Branding Constants ──────────────────────────────────────────────────────
NAVY     = RGBColor(0x0F, 0x1E, 0x36)   # SCSS Navy
GOLD     = RGBColor(0xC5, 0xA0, 0x59)   # SCSS Gold
GOLD_LT  = RGBColor(0xEB, 0xCE, 0x8E)   # Light Gold
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
SLATE    = RGBColor(0x47, 0x55, 0x69)
LIGHT    = RGBColor(0xF1, 0xF5, 0xF9)
GREEN    = RGBColor(0x10, 0xB9, 0x81)   # Authentic
RED      = RGBColor(0xEF, 0x44, 0x44)   # Flagged
AMBER    = RGBColor(0xF5, 0x9E, 0x0B)   # Inconclusive

# Slide dimensions — 16:9 Widescreen
W = Inches(13.33)
H = Inches(7.5)

def prs_init():
    prs = Presentation()
    prs.slide_width  = W
    prs.slide_height = H
    return prs


def add_rect(slide, left, top, width, height, fill_rgb=None, fill_alpha=None, line_rgb=None, line_width=None):
    """Add a filled rectangle shape."""
    shape = slide.shapes.add_shape(1, left, top, width, height)  # MSO_SHAPE_TYPE.RECTANGLE = 1
    shape.line.fill.background()  # No line by default
    if fill_rgb:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_rgb
    else:
        shape.fill.background()
    if line_rgb:
        shape.line.color.rgb = line_rgb
        if line_width:
            shape.line.width = line_width
    return shape


def add_textbox(slide, text, left, top, width, height,
                font_size=18, bold=False, color=WHITE,
                align=PP_ALIGN.LEFT, word_wrap=True, italic=False, line_spacing=None):
    """Add a textbox with styled text."""
    txb = slide.shapes.add_textbox(left, top, width, height)
    tf  = txb.text_frame
    tf.word_wrap = word_wrap
    tf.auto_size = None
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    if line_spacing:
        from pptx.oxml.ns import qn
        from lxml import etree
        pPr = p._pPr if p._pPr is not None else p._p.get_or_add_pPr()
    return txb


def add_multi_para(slide, paragraphs, left, top, width, height,
                   font_size=14, color=WHITE, line_spacing=Pt(22)):
    """Add a textbox with multiple paragraphs."""
    txb = slide.shapes.add_textbox(left, top, width, height)
    tf  = txb.text_frame
    tf.word_wrap = True
    for i, (bold, txt) in enumerate(paragraphs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(4)
        run = p.add_run()
        run.text = txt
        run.font.size = Pt(font_size)
        run.font.bold = bold
        run.font.color.rgb = color
    return txb


def slide_1_cover(prs):
    """Slide 1 — Cover / Title"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank

    # Full background
    bg = add_rect(slide, 0, 0, W, H, fill_rgb=NAVY)

    # Gold accent bar at top
    add_rect(slide, 0, 0, W, Inches(0.08), fill_rgb=GOLD)

    # Gold accent bar at bottom
    add_rect(slide, 0, H - Inches(0.08), W, Inches(0.08), fill_rgb=GOLD)

    # Decorative diagonal stripe (right side)
    add_rect(slide, W - Inches(2.8), 0, Inches(2.8), H, fill_rgb=RGBColor(0x17, 0x2B, 0x4E))

    # Logo text (top-left)
    add_textbox(slide, "SCSS", Inches(0.5), Inches(0.2), Inches(2), Inches(0.5),
                font_size=13, bold=True, color=GOLD, align=PP_ALIGN.LEFT)
    add_textbox(slide, "Sure Clue Scientific Solutions", Inches(0.5), Inches(0.5), Inches(5), Inches(0.35),
                font_size=9, color=GOLD_LT, align=PP_ALIGN.LEFT)

    # SEVA FIRST badge (top-right stripe area)
    add_textbox(slide, "SEVA FIRST", W - Inches(2.6), Inches(0.25), Inches(2.4), Inches(0.4),
                font_size=10, bold=True, color=GOLD, align=PP_ALIGN.CENTER)
    add_textbox(slide, "Innovation Challenge 2026", W - Inches(2.6), Inches(0.55), Inches(2.4), Inches(0.3),
                font_size=8, color=GOLD_LT, align=PP_ALIGN.CENTER)
    add_textbox(slide, "Sector 9 • Sub-theme 4", W - Inches(2.6), Inches(0.78), Inches(2.4), Inches(0.3),
                font_size=8, italic=True, color=GOLD_LT, align=PP_ALIGN.CENTER)

    # Main Title
    add_textbox(slide, "SCSS SATYA", Inches(0.5), Inches(1.8), Inches(9), Inches(1.4),
                font_size=54, bold=True, color=WHITE, align=PP_ALIGN.LEFT)

    # Subtitle
    add_textbox(slide, "Digital Media Authenticity Forensics Platform",
                Inches(0.5), Inches(3.1), Inches(9.5), Inches(0.7),
                font_size=22, bold=False, color=GOLD, align=PP_ALIGN.LEFT)

    # Tag line
    add_textbox(slide, "Multi-Layer AI Detection  |  Cryptographic Provenance  |  ISO/IEC 27037 Compliant",
                Inches(0.5), Inches(3.75), Inches(10), Inches(0.45),
                font_size=13, color=LIGHT, align=PP_ALIGN.LEFT)

    # Doctrine
    add_rect(slide, Inches(0.5), Inches(4.4), Inches(8.5), Inches(0.7),
             fill_rgb=RGBColor(0x1A, 0x30, 0x55))
    add_textbox(slide, "\"The tool screens. The expert decides.\"",
                Inches(0.65), Inches(4.45), Inches(8.2), Inches(0.55),
                font_size=16, italic=True, color=GOLD_LT, align=PP_ALIGN.LEFT)

    # Bottom metadata
    add_textbox(slide, "Maharashtra & Chhattisgarh Government  |  Forensic, AI & Cyber Security",
                Inches(0.5), H - Inches(0.7), Inches(10), Inches(0.4),
                font_size=9, color=SLATE, align=PP_ALIGN.LEFT)
    add_textbox(slide, f"October 2026",
                W - Inches(2.6), H - Inches(0.7), Inches(2.4), Inches(0.4),
                font_size=9, color=GOLD_LT, align=PP_ALIGN.RIGHT)


def slide_2_problem(prs):
    """Slide 2 — Problem Statement"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    add_rect(slide, 0, 0, W, H, fill_rgb=NAVY)
    add_rect(slide, 0, 0, W, Inches(0.06), fill_rgb=GOLD)
    add_rect(slide, 0, H - Inches(0.06), W, Inches(0.06), fill_rgb=GOLD)

    # Slide heading strip
    add_rect(slide, 0, Inches(0.06), W, Inches(0.9), fill_rgb=RGBColor(0x17, 0x2B, 0x4E))
    add_textbox(slide, "THE PROBLEM", Inches(0.5), Inches(0.1), Inches(4), Inches(0.55),
                font_size=11, bold=True, color=GOLD, align=PP_ALIGN.LEFT)
    add_textbox(slide, "The Digital Trust Crisis in India's Governance Ecosystem",
                Inches(0.5), Inches(0.45), Inches(12), Inches(0.5),
                font_size=20, bold=True, color=WHITE, align=PP_ALIGN.LEFT)

    # Stats row
    stats = [
        ("78%", "of legal exhibits in select courts\ncannot be verified for AI origin"),
        ("₹2,300 Cr+", "estimated annual loss from\nfake document fraud in India"),
        ("12 Seconds", "to generate a photorealistic deepfake\nindistinguishable to the naked eye"),
        ("0", "unified forensic screening APIs in\nGovernment sector workflows"),
    ]
    colors_stat = [RED, AMBER, GOLD, GREEN]
    for i, (stat, desc) in enumerate(stats):
        left = Inches(0.4 + i * 3.18)
        add_rect(slide, left, Inches(1.2), Inches(2.9), Inches(1.6), fill_rgb=RGBColor(0x17, 0x2B, 0x4E))
        add_textbox(slide, stat, left + Inches(0.1), Inches(1.25), Inches(2.7), Inches(0.65),
                    font_size=28, bold=True, color=colors_stat[i], align=PP_ALIGN.CENTER)
        add_textbox(slide, desc, left + Inches(0.1), Inches(1.88), Inches(2.7), Inches(0.8),
                    font_size=10, color=LIGHT, align=PP_ALIGN.CENTER)

    # Challenge bullets
    challenges = [
        ("AI-generated content", "DALL-E 3, Midjourney v6, Stable Diffusion produce images indistinguishable from authentic photographs — with zero embedded watermarks or provenance."),
        ("Deepfake proliferation", "Face-swap and voice-clone technologies are weaponised in electoral disinformation, insurance fraud, KYC bypass, and court evidence fabrication."),
        ("Document tampering", "Financial certificates, government orders, and medical reports are altered with commercially available tools in under 3 minutes."),
        ("Institutional gap", "Law enforcement, judiciary, and e-governance wings have no standardised, explainable, court-admissible automated screening mechanism."),
    ]
    for i, (title, body) in enumerate(challenges):
        top = Inches(2.95 + i * 0.99)
        add_rect(slide, Inches(0.4), top, Inches(0.08), Inches(0.72), fill_rgb=GOLD)
        add_textbox(slide, title, Inches(0.65), top, Inches(3.5), Inches(0.32),
                    font_size=12, bold=True, color=GOLD_LT, align=PP_ALIGN.LEFT)
        add_textbox(slide, body, Inches(0.65), top + Inches(0.32), Inches(12.2), Inches(0.55),
                    font_size=10.5, color=LIGHT, align=PP_ALIGN.LEFT)

    add_textbox(slide, "SCSS SATYA — Slide 2 of 7", Inches(0.4), H - Inches(0.35), Inches(6), Inches(0.3),
                font_size=8, color=SLATE, align=PP_ALIGN.LEFT)


def slide_3_solution(prs):
    """Slide 3 — Solution & 4-Layer Architecture"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    add_rect(slide, 0, 0, W, H, fill_rgb=NAVY)
    add_rect(slide, 0, 0, W, Inches(0.06), fill_rgb=GOLD)
    add_rect(slide, 0, H - Inches(0.06), W, Inches(0.06), fill_rgb=GOLD)

    add_rect(slide, 0, Inches(0.06), W, Inches(0.9), fill_rgb=RGBColor(0x17, 0x2B, 0x4E))
    add_textbox(slide, "OUR SOLUTION", Inches(0.5), Inches(0.1), Inches(4), Inches(0.55),
                font_size=11, bold=True, color=GOLD, align=PP_ALIGN.LEFT)
    add_textbox(slide, "4-Layer Multi-Dimensional Forensics Architecture",
                Inches(0.5), Inches(0.45), Inches(12), Inches(0.5),
                font_size=20, bold=True, color=WHITE, align=PP_ALIGN.LEFT)

    # Four pillars / layers
    layers = [
        ("LAYER 1", "Cryptographic\n& Provenance", ["SHA-256 + BLAKE3", "C2PA Manifest (ISO 19566-5)", "Perceptual Hashing", "Vault Bitstream Seal"], GOLD),
        ("LAYER 2", "Classical Image\nForensics", ["Error Level Analysis", "JPEG DQT Quantization", "Noise Residual Map", "FFT Frequency Lattice"], GREEN),
        ("LAYER 3", "AI & Deepfake\nDetection", ["Spectral Decay Slope (α)", "GAN / Diffusion Traces", "AI Synthetic Heatmap", "Cross-Channel Correlation"], RED),
        ("LAYER 4", "Document &\nStructural Forensics", ["PDF Revision Tracking", "Typography Alignment", "Copy-Move Detection", "Office XML Metadata"], AMBER),
    ]
    for i, (label, title, bullets, accent) in enumerate(layers):
        left = Inches(0.35 + i * 3.24)
        # Card background
        add_rect(slide, left, Inches(1.15), Inches(3.0), Inches(5.85), fill_rgb=RGBColor(0x12, 0x24, 0x40))
        # Accent top bar
        add_rect(slide, left, Inches(1.15), Inches(3.0), Inches(0.09), fill_rgb=accent)
        # Layer badge
        add_textbox(slide, label, left + Inches(0.1), Inches(1.22), Inches(2.8), Inches(0.32),
                    font_size=9, bold=True, color=accent, align=PP_ALIGN.LEFT)
        # Layer title
        add_textbox(slide, title, left + Inches(0.1), Inches(1.52), Inches(2.8), Inches(0.72),
                    font_size=15, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
        # Bullets
        for j, b in enumerate(bullets):
            btop = Inches(2.28 + j * 0.78)
            add_rect(slide, left + Inches(0.15), btop + Inches(0.12), Inches(0.08), Inches(0.08), fill_rgb=accent)
            add_textbox(slide, b, left + Inches(0.32), btop, Inches(2.55), Inches(0.6),
                        font_size=11, color=LIGHT, align=PP_ALIGN.LEFT)

    # Evidence Fusion banner at bottom
    add_rect(slide, Inches(0.35), Inches(6.88), W - Inches(0.7), Inches(0.45), fill_rgb=RGBColor(0x1A, 0x30, 0x55))
    add_textbox(slide, "⟶  Evidence Fusion Engine answers 4 forensic questions: Origin | Integrity | Generation | Transformation",
                Inches(0.55), Inches(6.9), W - Inches(1.0), Inches(0.38),
                font_size=11, bold=True, color=GOLD_LT, align=PP_ALIGN.CENTER)

    add_textbox(slide, "SCSS SATYA — Slide 3 of 7", Inches(0.4), H - Inches(0.35), Inches(6), Inches(0.3),
                font_size=8, color=SLATE, align=PP_ALIGN.LEFT)


def slide_4_technology(prs):
    """Slide 4 — Technology Stack & AI Engine"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    add_rect(slide, 0, 0, W, H, fill_rgb=NAVY)
    add_rect(slide, 0, 0, W, Inches(0.06), fill_rgb=GOLD)
    add_rect(slide, 0, H - Inches(0.06), W, Inches(0.06), fill_rgb=GOLD)

    add_rect(slide, 0, Inches(0.06), W, Inches(0.9), fill_rgb=RGBColor(0x17, 0x2B, 0x4E))
    add_textbox(slide, "TECHNOLOGY", Inches(0.5), Inches(0.1), Inches(4), Inches(0.55),
                font_size=11, bold=True, color=GOLD, align=PP_ALIGN.LEFT)
    add_textbox(slide, "Production-Grade Technology Stack",
                Inches(0.5), Inches(0.45), Inches(12), Inches(0.5),
                font_size=20, bold=True, color=WHITE, align=PP_ALIGN.LEFT)

    # Left column — Backend
    add_textbox(slide, "⚙  BACKEND & AI ENGINE", Inches(0.4), Inches(1.15), Inches(6), Inches(0.4),
                font_size=12, bold=True, color=GOLD, align=PP_ALIGN.LEFT)

    backend_items = [
        ("FastAPI + Python 3.12", "Async REST API, OpenAPI 3.1, ISO/IEC 27037 chain of custody"),
        ("SQLAlchemy + SQLite", "Immutable evidence vault with audit activity log"),
        ("OpenCV + NumPy + SciPy", "ELA, noise residuals, FFT, ORB feature matching, copy-move"),
        ("ONNX Runtime", "Production-ready neural inference; DIRE / CNNDetection adapter"),
        ("BLAKE3 + SHA-256 + SHA-512", "Dual cryptographic sealing + perceptual fingerprinting"),
        ("imagehash (pHash/dHash/wHash)", "Visual similarity matching across recompressed variants"),
        ("pypdf + python-docx", "PDF revision tracking, Office XML metadata & revision forensics"),
        ("ReportLab (ISO PDF/A)", "Court-quality PDF forensic report generation"),
    ]
    for i, (title, desc) in enumerate(backend_items):
        top = Inches(1.6 + i * 0.68)
        add_rect(slide, Inches(0.4), top, Inches(0.06), Inches(0.5), fill_rgb=GOLD)
        add_textbox(slide, title, Inches(0.58), top, Inches(5.7), Inches(0.25),
                    font_size=11, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
        add_textbox(slide, desc, Inches(0.58), top + Inches(0.24), Inches(5.9), Inches(0.3),
                    font_size=9, color=LIGHT, align=PP_ALIGN.LEFT)

    # Divider
    add_rect(slide, Inches(6.85), Inches(1.1), Inches(0.04), Inches(6.0), fill_rgb=RGBColor(0x2D, 0x45, 0x65))

    # Right column — Frontend & Compliance
    add_textbox(slide, "🖥  FRONTEND & DELIVERY", W / 2 + Inches(0.2), Inches(1.15), Inches(6), Inches(0.4),
                font_size=12, bold=True, color=GOLD, align=PP_ALIGN.LEFT)

    frontend_items = [
        ("React 19 + TypeScript + Vite", "Responsive examiner dashboard with live forensic results"),
        ("Component Evidence Cards", "Per-test indicator badges (Detected / Clean / Inconclusive)"),
        ("Evidence Heatmaps", "Noise residual, ELA, copy-move, AI synthetic, typography maps"),
        ("4-Pillar Display", "Origin | Integrity | Generation | Transformation panels"),
        ("Calibrated Confidence Dials", "Multi-dimensional probability scores with explainability"),
    ]
    for i, (title, desc) in enumerate(frontend_items):
        top = Inches(1.6 + i * 0.76)
        add_rect(slide, W / 2 + Inches(0.2), top, Inches(0.06), Inches(0.5), fill_rgb=GREEN)
        add_textbox(slide, title, W / 2 + Inches(0.38), top, Inches(5.9), Inches(0.28),
                    font_size=11, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
        add_textbox(slide, desc, W / 2 + Inches(0.38), top + Inches(0.26), Inches(5.9), Inches(0.3),
                    font_size=9, color=LIGHT, align=PP_ALIGN.LEFT)

    add_textbox(slide, "🏛  STANDARDS & COMPLIANCE", W / 2 + Inches(0.2), Inches(5.5), Inches(6), Inches(0.4),
                font_size=12, bold=True, color=GOLD, align=PP_ALIGN.LEFT)
    compliance_items = ["ISO/IEC 27037 — Digital Evidence Handling",
                        "NIST OpenMFC — Media Forensics Challenge",
                        "C2PA Specification 2.x — Content Provenance",
                        "ISO/IEC 19566-5 — JUMBF Manifest Format"]
    for i, c in enumerate(compliance_items):
        add_textbox(slide, f"✓  {c}", W / 2 + Inches(0.38), Inches(5.9 + i * 0.32), Inches(6.0), Inches(0.3),
                    font_size=10.5, color=GREEN, align=PP_ALIGN.LEFT)

    add_textbox(slide, "SCSS SATYA — Slide 4 of 7", Inches(0.4), H - Inches(0.35), Inches(6), Inches(0.3),
                font_size=8, color=SLATE, align=PP_ALIGN.LEFT)


def slide_5_forensic_tests(prs):
    """Slide 5 — 12 Forensic Tests"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    add_rect(slide, 0, 0, W, H, fill_rgb=NAVY)
    add_rect(slide, 0, 0, W, Inches(0.06), fill_rgb=GOLD)
    add_rect(slide, 0, H - Inches(0.06), W, Inches(0.06), fill_rgb=GOLD)

    add_rect(slide, 0, Inches(0.06), W, Inches(0.9), fill_rgb=RGBColor(0x17, 0x2B, 0x4E))
    add_textbox(slide, "FORENSIC TESTS", Inches(0.5), Inches(0.1), Inches(4), Inches(0.55),
                font_size=11, bold=True, color=GOLD, align=PP_ALIGN.LEFT)
    add_textbox(slide, "12 Automated Screening Tests — Each Explainable, Each Court-Documented",
                Inches(0.5), Inches(0.45), Inches(12), Inches(0.5),
                font_size=20, bold=True, color=WHITE, align=PP_ALIGN.LEFT)

    tests_data = [
        ("T-01", "Metadata & Structural Chunk Forensics", "EXIF, PNG IHDR/pHYs/tEXt, screen-density, trailing bytes"),
        ("T-02", "Dual Cryptographic & Perceptual Hashing", "SHA-256, BLAKE3, SHA-512 | pHash, dHash, aHash, wHash"),
        ("T-03", "C2PA & Content Credentials Provenance", "JUMBF Manifest, APP11 markers, AI-declared generative origin"),
        ("T-04", "Document & Container Structural Forensics", "PDF revisions, JavaScript detection, Office XML metadata"),
        ("T-05", "JPEG Quantization & Double-Compression", "DQT extraction, IJG quality estimation, recompression ghosting"),
        ("T-06", "Error Level Analysis (ELA)", "DCT compression grid resave differential analysis (JPEG)"),
        ("T-07", "Image Consistency & Channel Analytics", "RGB divergence, quadrant variance, global luminance map"),
        ("T-08", "Multi-Scale Noise Residual Analysis", "High-pass median filter residual, SNR, kurtosis, inhomogeneity"),
        ("T-09", "2D Fourier Spectral Analysis (FFT)", "Periodic lattice peaks, spectral decay slope, GAN frequency grid"),
        ("T-10", "Copy-Move / Clone Forgery Detection", "ORB descriptor matching, spatial clustering, translation map"),
        ("T-11", "AI Generative Classifier", "Synthetic Likelihood Index (%), spectral decay α, patch heatmap"),
        ("T-12", "Document Typography & Character Alignment", "Baseline deviation, kerning variance, glyph edge sharpness"),
    ]

    # Two columns, 6 rows
    for i, (code, name, detail) in enumerate(tests_data):
        col  = i % 2
        row  = i // 2
        left = Inches(0.35 + col * 6.55)
        top  = Inches(1.18 + row * 1.02)
        # Card
        add_rect(slide, left, top, Inches(6.2), Inches(0.93), fill_rgb=RGBColor(0x12, 0x24, 0x40))
        # Code badge
        add_rect(slide, left, top, Inches(0.55), Inches(0.93), fill_rgb=GOLD)
        add_textbox(slide, code, left + Inches(0.01), top + Inches(0.28), Inches(0.52), Inches(0.35),
                    font_size=9, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
        # Name
        add_textbox(slide, name, left + Inches(0.65), top + Inches(0.04), Inches(5.4), Inches(0.32),
                    font_size=11, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
        # Detail
        add_textbox(slide, detail, left + Inches(0.65), top + Inches(0.38), Inches(5.4), Inches(0.48),
                    font_size=9, color=LIGHT, align=PP_ALIGN.LEFT)

    add_textbox(slide, "SCSS SATYA — Slide 5 of 7", Inches(0.4), H - Inches(0.35), Inches(6), Inches(0.3),
                font_size=8, color=SLATE, align=PP_ALIGN.LEFT)


def slide_6_compliance(prs):
    """Slide 6 — Compliance, Identity & Use Cases"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    add_rect(slide, 0, 0, W, H, fill_rgb=NAVY)
    add_rect(slide, 0, 0, W, Inches(0.06), fill_rgb=GOLD)
    add_rect(slide, 0, H - Inches(0.06), W, Inches(0.06), fill_rgb=GOLD)

    add_rect(slide, 0, Inches(0.06), W, Inches(0.9), fill_rgb=RGBColor(0x17, 0x2B, 0x4E))
    add_textbox(slide, "COMPLIANCE & IMPACT", Inches(0.5), Inches(0.1), Inches(5), Inches(0.55),
                font_size=11, bold=True, color=GOLD, align=PP_ALIGN.LEFT)
    add_textbox(slide, "Institutional Identity, Compliance Standards & Use Cases",
                Inches(0.5), Inches(0.45), Inches(12), Inches(0.5),
                font_size=20, bold=True, color=WHITE, align=PP_ALIGN.LEFT)

    # Standards block (left)
    add_textbox(slide, "STANDARDS WE CONFORM TO", Inches(0.4), Inches(1.15), Inches(6.0), Inches(0.4),
                font_size=12, bold=True, color=GOLD, align=PP_ALIGN.LEFT)

    standards = [
        ("ISO/IEC 27037:2012", "Digital Evidence Identification, Collection, Acquisition & Preservation — Chain of custody embedded in every examination record."),
        ("NIST OpenMFC", "NIST Open Media Forensics Challenge taxonomy: Manipulation Detection, Localisation, Deepfake Detection, Steganography — treated as independent forensic problems."),
        ("C2PA Specification 2.x", "Coalition for Content Provenance and Authenticity — JUMBF manifest parsing, claim generator extraction, signing trust chain evaluation."),
        ("ISO/IEC 19566-5", "JPEG Universal Metadata Box Format (JUMBF) for digital asset provenance containers."),
        ("ISO/IEC 10918-1 (JPEG)", "Discrete Cosine Transform baseline quantization table analysis and double-compression detection."),
        ("ISO/IEC 29500 (OOXML)", "Office Open XML container integrity, metadata revision and document structural anomaly forensics."),
    ]
    for i, (std_title, std_body) in enumerate(standards):
        top = Inches(1.6 + i * 0.84)
        add_rect(slide, Inches(0.4), top + Inches(0.05), Inches(0.07), Inches(0.58), fill_rgb=GREEN)
        add_textbox(slide, std_title, Inches(0.6), top, Inches(5.8), Inches(0.28),
                    font_size=11, bold=True, color=GREEN, align=PP_ALIGN.LEFT)
        add_textbox(slide, std_body, Inches(0.6), top + Inches(0.28), Inches(6.0), Inches(0.48),
                    font_size=9, color=LIGHT, align=PP_ALIGN.LEFT)

    # Divider
    add_rect(slide, Inches(6.85), Inches(1.1), Inches(0.04), Inches(6.0), fill_rgb=RGBColor(0x2D, 0x45, 0x65))

    # Right — Use Cases
    add_textbox(slide, "INSTITUTIONAL USE CASES", W / 2 + Inches(0.2), Inches(1.15), Inches(6.0), Inches(0.4),
                font_size=12, bold=True, color=GOLD, align=PP_ALIGN.LEFT)

    use_cases = [
        ("🏛  Judiciary & Courts", "Rapid preliminary screening of digital exhibits — photographs, screenshots, audio spectrograms, and PDF documents."),
        ("🚓  Law Enforcement", "First-response field screening of forwarded WhatsApp messages, social media posts, and CCTV screenshots."),
        ("🏦  Banking & Insurance", "KYC document authenticity: Aadhaar, PAN, Property Papers, Medical certificates — before loan or claim approval."),
        ("🏫  Examination Boards", "Certificate and result tampering detection for state-level merit lists, admit cards, and marksheets."),
        ("🗳️  Electoral Commission", "Electoral deepfake and fabricated candidate imagery screening before publication clearance."),
        ("📡  Defence & Intelligence", "Intelligence media evidence authentication and adversarial synthetic media identification."),
    ]
    for i, (uc_title, uc_body) in enumerate(use_cases):
        top = Inches(1.6 + i * 0.87)
        add_rect(slide, W / 2 + Inches(0.2), top + Inches(0.04), Inches(0.07), Inches(0.6), fill_rgb=GOLD)
        add_textbox(slide, uc_title, W / 2 + Inches(0.38), top, Inches(6.0), Inches(0.3),
                    font_size=11, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
        add_textbox(slide, uc_body, W / 2 + Inches(0.38), top + Inches(0.3), Inches(6.0), Inches(0.5),
                    font_size=9, color=LIGHT, align=PP_ALIGN.LEFT)

    add_textbox(slide, "SCSS SATYA — Slide 6 of 7", Inches(0.4), H - Inches(0.35), Inches(6), Inches(0.3),
                font_size=8, color=SLATE, align=PP_ALIGN.LEFT)


def slide_7_roadmap_cta(prs):
    """Slide 7 — Roadmap & Call to Action"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    add_rect(slide, 0, 0, W, H, fill_rgb=NAVY)
    add_rect(slide, 0, 0, W, Inches(0.06), fill_rgb=GOLD)
    add_rect(slide, 0, H - Inches(0.06), W, Inches(0.06), fill_rgb=GOLD)

    add_rect(slide, 0, Inches(0.06), W, Inches(0.9), fill_rgb=RGBColor(0x17, 0x2B, 0x4E))
    add_textbox(slide, "ROADMAP & NEXT STEPS", Inches(0.5), Inches(0.1), Inches(5), Inches(0.55),
                font_size=11, bold=True, color=GOLD, align=PP_ALIGN.LEFT)
    add_textbox(slide, "Deployment Roadmap & SEVA FIRST Pilot Plan",
                Inches(0.5), Inches(0.45), Inches(12), Inches(0.5),
                font_size=20, bold=True, color=WHITE, align=PP_ALIGN.LEFT)

    # Roadmap phases
    phases = [
        ("Q4 2026\nPrototype", "✓ 12-module pipeline\n✓ React dashboard\n✓ ISO/IEC 27037 PDF reports\n✓ C2PA provenance", GOLD),
        ("Q1 2027\nPilot", "→ Maharashtra Police Digital Cell\n→ NASCA Chhattisgarh tie-up\n→ 500 test cases, blind evaluation\n→ ONNX DIRE model integration", AMBER),
        ("Q2 2027\nSWAS API", "→ REST API for court e-filing systems\n→ Aadhaar / DigiLocker integration\n→ SLA: 95% accuracy target\n→ Load-tested: 500 RPM", GREEN),
        ("Q3-Q4 2027\nScale", "→ National rollout: 28 states\n→ NIC cloud deployment\n→ Hardware SynthID chip pipeline\n→ CERT-In approved audit trail", RGBColor(0x60, 0xA5, 0xFA)),
    ]

    for i, (phase, items, color) in enumerate(phases):
        left = Inches(0.35 + i * 3.22)
        # Phase card
        add_rect(slide, left, Inches(1.2), Inches(3.0), Inches(3.0), fill_rgb=RGBColor(0x12, 0x24, 0x40))
        add_rect(slide, left, Inches(1.2), Inches(3.0), Inches(0.08), fill_rgb=color)
        add_textbox(slide, phase, left + Inches(0.1), Inches(1.26), Inches(2.8), Inches(0.6),
                    font_size=13, bold=True, color=color, align=PP_ALIGN.CENTER)
        add_textbox(slide, items, left + Inches(0.12), Inches(1.88), Inches(2.76), Inches(2.2),
                    font_size=10, color=LIGHT, align=PP_ALIGN.LEFT)

    # Key differentiators
    add_textbox(slide, "WHY SCSS SATYA WINS", Inches(0.4), Inches(4.4), Inches(12.5), Inches(0.4),
                font_size=13, bold=True, color=GOLD, align=PP_ALIGN.LEFT)

    differentiators = [
        ("No Black Box", "Every test result carries a structured observations list, an explanation, and known limitations — auditable in court."),
        ("Format-Agnostic", "JPEG, PNG, WebP, PDF, DOCX — single platform handles all evidence types from police FIRs to insurance claims."),
        ("Open Standards", "NIST, ISO, C2PA — not proprietary APIs. Independent re-verification by any accredited lab is architecturally guaranteed."),
        ("Government-Ready", "SQLite evidence vault, chain-of-custody audit log, human review workflow, and PDF/A report — built for e-court integration."),
    ]
    for i, (d_title, d_body) in enumerate(differentiators):
        col = i % 2
        row = i // 2
        left = Inches(0.35 + col * 6.55)
        top  = Inches(4.86 + row * 0.82)
        add_rect(slide, left, top, Inches(6.2), Inches(0.74), fill_rgb=RGBColor(0x17, 0x2B, 0x4E))
        add_textbox(slide, f"◆  {d_title}", left + Inches(0.15), top + Inches(0.04), Inches(6.0), Inches(0.28),
                    font_size=11, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
        add_textbox(slide, d_body, left + Inches(0.15), top + Inches(0.3), Inches(5.9), Inches(0.38),
                    font_size=9, color=LIGHT, align=PP_ALIGN.LEFT)

    # CTA box
    add_rect(slide, Inches(1.5), Inches(6.7), Inches(10.35), Inches(0.6), fill_rgb=RGBColor(0x1A, 0x30, 0x55))
    add_textbox(slide, "Contact SCSS: animesh0112@gmail.com  |  github.com/animesh0112/SCSS-SATYA  |  SEVA FIRST Sector 9, Sub-theme 4",
                Inches(1.6), Inches(6.74), Inches(10.15), Inches(0.5),
                font_size=10.5, bold=True, color=GOLD_LT, align=PP_ALIGN.CENTER)

    add_textbox(slide, "SCSS SATYA — Slide 7 of 7", Inches(0.4), H - Inches(0.35), Inches(6), Inches(0.3),
                font_size=8, color=SLATE, align=PP_ALIGN.LEFT)


def build_pitch_deck(output_path: str):
    prs = prs_init()
    slide_1_cover(prs)
    slide_2_problem(prs)
    slide_3_solution(prs)
    slide_4_technology(prs)
    slide_5_forensic_tests(prs)
    slide_6_compliance(prs)
    slide_7_roadmap_cta(prs)
    prs.save(output_path)
    print(f"[OK] Pitch deck saved: {output_path}  ({prs.slides.__len__()} slides)")


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "SCSS_SATYA_SEVA_FIRST_2026_Pitch_Deck.pptx"
    build_pitch_deck(out)
