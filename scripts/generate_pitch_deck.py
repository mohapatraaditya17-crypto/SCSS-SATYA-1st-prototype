import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Colors
    NAVY = RGBColor(15, 30, 54)        # #0F1E36
    GOLD = RGBColor(197, 160, 89)      # #C5A059
    LIGHT_BG = RGBColor(248, 250, 252) # #F8FAFC
    CARD_BG = RGBColor(255, 255, 255)
    DARK_CARD = RGBColor(22, 42, 77)
    TEXT_DARK = RGBColor(30, 41, 59)
    TEXT_MUTED = RGBColor(100, 116, 139)
    TEXT_WHITE = RGBColor(255, 255, 255)
    BORDER_COLOR = RGBColor(226, 232, 240)
    ACCENT_GREEN = RGBColor(16, 185, 129)

    def add_header(slide, title, category="SEVA FIRST INNOVATION CHALLENGE 2026 · SECTOR 9"):
        header_rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.1))
        header_rect.fill.solid()
        header_rect.fill.fore_color.rgb = NAVY
        header_rect.line.fill.background()

        # Gold accent bar
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.05), Inches(13.333), Inches(0.05))
        bar.fill.solid()
        bar.fill.fore_color.rgb = GOLD
        bar.line.fill.background()

        # Category
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(10), Inches(0.3))
        tf = cat_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = category.upper()
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = GOLD

        # Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.38), Inches(11.5), Inches(0.6))
        tf2 = t_box.text_frame
        tf2.word_wrap = True
        p2 = tf2.paragraphs[0]
        p2.text = title
        p2.font.size = Pt(22)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_WHITE

    def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=BORDER_COLOR):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
        return shape

    # =========================================================================
    # SLIDE 1: Title & Application Identification
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = NAVY
    bg1.line.fill.background()

    # Decorative Gold Lines
    d_bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.2), Inches(1.2), Inches(0.08))
    d_bar.fill.solid()
    d_bar.fill.fore_color.rgb = GOLD
    d_bar.line.fill.background()

    t_box = slide1.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(2.2))
    tf = t_box.text_frame
    p0 = tf.paragraphs[0]
    p0.text = "SEVA FIRST INNOVATION CHALLENGE 2026"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = GOLD

    p1 = tf.add_paragraph()
    p1.text = "SCSS SATYA"
    p1.font.size = Pt(44)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE

    p2 = tf.add_paragraph()
    p2.text = "Forensic-Led Digital Evidence Integrity & Authenticity Screening Platform"
    p2.font.size = Pt(20)
    p2.font.color.rgb = RGBColor(226, 232, 240)

    # Core Guiding Principle Banner
    prin_card = add_card(slide1, 0.8, 3.8, 11.733, 1.0, bg_color=DARK_CARD, border_color=GOLD)
    prin_box = slide1.shapes.add_textbox(Inches(1.0), Inches(3.9), Inches(11.3), Inches(0.8))
    ptf = prin_box.text_frame
    pp0 = ptf.paragraphs[0]
    pp0.text = "CORE GUIDING DOCTRINE: \"THE TOOL SCREENS. THE EXPERT DECIDES.\""
    pp0.font.size = Pt(13)
    pp0.font.bold = True
    pp0.font.color.rgb = GOLD

    pp1 = ptf.add_paragraph()
    pp1.text = "Automated output is never presented as a conclusive forensic opinion or legal proof. A structured 4-layer screening workflow joining multi-modal signal detection with court-admissible audit trails."
    pp1.font.size = Pt(11)
    pp1.font.color.rgb = RGBColor(203, 213, 225)

    # Metadata Grid (3 Cards)
    meta_cols = [
        ("SECTOR & SUB-THEME", ["Sector 9: Emerging Technologies (AI, Blockchain, Others)", "Sub-theme 4: Responsible AI, Deepfake Detection, Cyber Resilience & Digital Trust"], 0.8),
        ("APPLICANT INSTITUTION", ["Sure Clue Scientific Solutions (SCSS)", "Abhishek Dixit (Lead) & Technical Engineering Team", "Udyam MSME Registered & Forensic Lab Heritage"], 4.8),
        ("CURRENT STAGE & STATUS", ["Working Prototype v1.0.0 (Validated)", "9 Automated Forensic Screening Tests", "Compliant with ISO/IEC 27037 & Section 63 BSA"], 8.8)
    ]
    for m_title, m_lines, left in meta_cols:
        add_card(slide1, left, 5.0, 3.733, 1.8, bg_color=DARK_CARD, border_color=BORDER_COLOR)
        box = slide1.shapes.add_textbox(Inches(left + 0.15), Inches(5.1), Inches(3.4), Inches(1.6))
        btf = box.text_frame
        bp0 = btf.paragraphs[0]
        bp0.text = m_title
        bp0.font.size = Pt(11)
        bp0.font.bold = True
        bp0.font.color.rgb = GOLD
        for line in m_lines:
            blp = btf.add_paragraph()
            blp.text = f"• {line}"
            blp.font.size = Pt(10)
            blp.font.color.rgb = RGBColor(226, 232, 240)

    # =========================================================================
    # SLIDE 2: The Evidence-Backed Problem
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "The Real-World Problem: The Evidentiary Crisis in Digital Media")

    # Left Column: Problem Realities (Card)
    add_card(slide2, 0.8, 1.4, 5.6, 5.5, bg_color=LIGHT_BG)
    p_box = slide2.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(5.2), Inches(5.2))
    ptf = p_box.text_frame
    ptf.word_wrap = True
    pp = ptf.paragraphs[0]
    pp.text = "SURGE IN DIGITALLY MANIPULATED EVIDENCE"
    pp.font.size = Pt(14)
    pp.font.bold = True
    pp.font.color.rgb = NAVY

    problems = [
        ("Financial Fraud & KYC Spoofing", "Falsified identity cards, morphed utility bills, altered bank statements, and forged administrative role screenshots (e.g. cloud role assignments, authorization tables)."),
        ("Insurance Claims Tampering", "Staged vehicle damage, recycled accident photos, and AI-inpainted incident records costing insurers crores annually."),
        ("Criminal & Judicial Admissibility", "Police cyber cells and courts face a flood of unverified social media screenshots and video bitstreams without verifiable provenance."),
        ("The 'Black Box' Detector Trap", "Commercial AI detectors give opaque single-number scores ('87% Fake') with zero explainability, failing judicial scrutiny under Section 63 BSA (formerly 65B IEA).")
    ]
    for heading, desc in problems:
        h_p = ptf.add_paragraph()
        h_p.text = f"\n▶ {heading}"
        h_p.font.size = Pt(11)
        h_p.font.bold = True
        h_p.font.color.rgb = GOLD
        d_p = ptf.add_paragraph()
        d_p.text = desc
        d_p.font.size = Pt(10)
        d_p.font.color.rgb = TEXT_DARK

    # Right Column: The Current Institutional Dilemma (Cards)
    dilemma_cols = [
        ("NO STANDARDIZED TRIAGE", "Forensic labs (RFSLs) face huge backlogs. Investigators spend days on manual EXIF queries and basic photo checks without a standardized screening tool.", 1.4),
        ("LOSSY WEB & SOCIAL MEDIA PLATFORMS", "WhatsApp, Telegram, and web browsers automatically strip camera EXIF data and recompress imagery. Traditional EXIF tools fail immediately on 90%+ of web evidence.", 3.2),
        ("LEGAL & ACCREDITATION STANDARDS", "Evidence must conform to ISO/IEC 27037 (Handling Digital Evidence). Unverified algorithmic claims destroy court credibility and lead to case dismissals.", 5.0),
    ]
    for d_title, d_text, top in dilemma_cols:
        add_card(slide2, 6.7, top, 5.8, 1.6, bg_color=CARD_BG)
        box = slide2.shapes.add_textbox(Inches(6.9), Inches(top + 0.1), Inches(5.4), Inches(1.4))
        btf = box.text_frame
        btf.word_wrap = True
        bp0 = btf.paragraphs[0]
        bp0.text = f"CRITICAL GAP: {d_title}"
        bp0.font.size = Pt(11)
        bp0.font.bold = True
        bp0.font.color.rgb = NAVY
        bp1 = btf.add_paragraph()
        bp1.text = d_text
        bp1.font.size = Pt(10)
        bp1.font.color.rgb = TEXT_DARK

    # =========================================================================
    # SLIDE 3: The Innovation: 4-Layer Defensible Architecture
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "The Innovation: SCSS SATYA's 4-Layer Defensible Architecture")

    layers = [
        ("LAYER 1: PASSIVE-BLIND MULTI-SIGNAL SCREENING",
         "9 Scientific Forensic Analyzers across all formats (PNG, JPEG, TIFF):",
         [
             "Metadata & Deep PNG Chunk Forensics (IHDR, pHYs DPI, steganography checks)",
             "Error Level Analysis (ELA - JPEG DCT 8x8 macroblock recompression)",
             "Multi-Scale Noise Residual Variance Heatmap (Works on all formats)",
             "2D Fast Fourier Spectral Analysis (Detects resampling & AI periodic lattices)",
             "Copy-Move Forgery Detection (ORB keypoint spatial matching vectors)",
             "AI Generative Classifier (Spectral decay slope & diffusion noise co-occurrence)",
             "Document Typography & Alignment (Character baseline offset & kerning variance)"
         ], 0.8),
        ("LAYER 2: CRYPTOGRAPHIC INTEGRITY & CHAIN OF CUSTODY",
         "Immediate SHA-256 evidence hashing at ingestion. Bitstream preserved non-invasively in isolated evidence vault with real-time hash re-verification against bit-rot or alteration.",
         [], 3.8),
        ("LAYER 3: EXPLAINABLE FINDINGS & SCIENTIFIC LIMITS",
         "No black-box opacity. Multi-indicator checklist (No Indicator / Indicator / Inconclusive) with explicit methodological limitations, quantitative analytics, and examiner manual verification steps.",
         [], 5.0),
        ("LAYER 4: QUALIFIED HUMAN FORENSIC CERTIFICATION",
         "Formal examiner attestation workflow. Produces ISO/IEC 27037 compliant court-admissible PDF reports with dynamic 2-pass page numbering, embedded exhibits, and cryptographic seal.",
         [], 6.1)
    ]

    # Layer 1 Card (Large Left Card)
    add_card(slide3, 0.8, 1.4, 5.7, 5.5, bg_color=CARD_BG)
    l1_box = slide3.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(5.3), Inches(5.2))
    tf = l1_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "LAYER 1: MULTI-MODAL PASSIVE SCREENING"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p_sub = tf.add_paragraph()
    p_sub.text = "Format-Agnostic Signal Detection (9 Screening Engines):"
    p_sub.font.size = Pt(10)
    p_sub.font.bold = True
    p_sub.font.color.rgb = GOLD

    for item in layers[0][2]:
        lp = tf.add_paragraph()
        lp.text = f"✓ {item}"
        lp.font.size = Pt(9.5)
        lp.font.color.rgb = TEXT_DARK

    # Layers 2, 3, 4 (Right Cards)
    r_layers = [
        ("LAYER 2: EVIDENCE INTEGRITY (SHA-256)", "Immediate SHA-256 bitstream baseline sealing upon ingestion. Non-invasive vault storage with real-time cryptographic audit verification conforming to ISO/IEC 27037.", 1.4),
        ("LAYER 3: EXPLAINABLE EVIDENCE & LIMITS", "Transparent multi-indicator breakdown with exact quantitative metrics (SNR, Kurtosis, Fourier roll-off alpha, character baseline variance) and mandatory limitation disclosures.", 3.2),
        ("LAYER 4: QUALIFIED HUMAN ATTESTATION", "Digital signature and formal attestation workflow for forensic examiners. Automated export of signed ISO/IEC 27037 PDF reports with embedded derived exhibits for court presentation.", 5.0)
    ]
    for l_title, l_desc, top in r_layers:
        add_card(slide3, 6.8, top, 5.7, 1.6, bg_color=LIGHT_BG)
        box = slide3.shapes.add_textbox(Inches(7.0), Inches(top + 0.1), Inches(5.3), Inches(1.4))
        btf = box.text_frame
        btf.word_wrap = True
        bp0 = btf.paragraphs[0]
        bp0.text = l_title
        bp0.font.size = Pt(11)
        bp0.font.bold = True
        bp0.font.color.rgb = NAVY
        bp1 = btf.add_paragraph()
        bp1.text = l_desc
        bp1.font.size = Pt(10)
        bp1.font.color.rgb = TEXT_DARK

    # =========================================================================
    # SLIDE 4: Technical Feasibility & Working Prototype Validation
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "Feasibility & Prototype: Tested, Operational & Defensible")

    # 3 Validation Metric Cards
    v_cards = [
        ("AUTHENTIC CAMERA SPECIMEN", "Tested on Nikon D850 Raw Capture", [
            "Bayer CFA sensor noise uniform across all quadrants",
            "EXIF hardware timestamps & serial numbers intact",
            "Smooth 1/f^alpha Fourier spectral roll-off (alpha=2.10)",
            "Screening Assessment: No Indicators Detected"
        ], 0.8),
        ("SPLICED PHOTO COMPOSITE", "Tested on Photoshop Inpainted Composite", [
            "ELA Q=90 reveals elevated recompression boundaries",
            "Noise Residual Heatmap highlights foreign spliced patch",
            "Software tag 'Adobe Photoshop' extracted from headers",
            "Screening Assessment: Requires Human Review"
        ], 4.8),
        ("DOCUMENT / SCREENSHOT FORGERY", "Tested on Azure Terminal Table & Records", [
            "Deep PNG chunk inspection verifies 96 DPI screen density",
            "ORB keypoints detect 46 coherent copy-move row clusters",
            "Typography engine detects character baseline offset",
            "Fourier spectrum reveals 6,937 periodic lattice spikes"
        ], 8.8)
    ]
    for title, subtitle, points, left in v_cards:
        add_card(slide4, left, 1.4, 3.733, 3.6, bg_color=CARD_BG)
        box = slide4.shapes.add_textbox(Inches(left + 0.15), Inches(1.5), Inches(3.4), Inches(3.3))
        btf = box.text_frame
        btf.word_wrap = True
        bp0 = btf.paragraphs[0]
        bp0.text = title
        bp0.font.size = Pt(11)
        bp0.font.bold = True
        bp0.font.color.rgb = NAVY
        bp_sub = btf.add_paragraph()
        bp_sub.text = subtitle
        bp_sub.font.size = Pt(9.5)
        bp_sub.font.bold = True
        bp_sub.font.color.rgb = GOLD
        for pt in points:
            pp = btf.add_paragraph()
            pp.text = f"• {pt}"
            pp.font.size = Pt(9.5)
            pp.font.color.rgb = TEXT_DARK

    # Architecture Bottom Summary Card
    add_card(slide4, 0.8, 5.2, 11.733, 1.7, bg_color=DARK_CARD, border_color=GOLD)
    bot_box = slide4.shapes.add_textbox(Inches(1.0), Inches(5.3), Inches(11.3), Inches(1.5))
    tf = bot_box.text_frame
    tf.word_wrap = True
    bp = tf.paragraphs[0]
    bp.text = "PROTOTYPE ARCHITECTURE & EXECUTION BENCHMARKS (OCTOBER 2026)"
    bp.font.size = Pt(11)
    bp.font.bold = True
    bp.font.color.rgb = GOLD

    specs = [
        "Stack: Python 3.12, FastAPI, React 19, TypeScript, OpenCV, NumPy, SciPy, ReportLab, SQLite, SQLAlchemy",
        "Test Verification: Automated 16-test unit & integration test suite passing with 100% test coverage",
        "Performance: Full 9-test multi-modal screening pipeline executes in under 2.5 seconds per megapixel on standard workstations",
        "Admissibility Readiness: ISO/IEC 27037 cryptographic hashing, dynamic exhibit generation, and formal examiner attestation"
    ]
    for s in specs:
        p = tf.add_paragraph()
        p.text = f"▶ {s}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = RGBColor(226, 232, 240)

    # =========================================================================
    # SLIDE 5: Impact, Beneficiaries & Cost-Benefit Feasibility
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "Operational Impact & Institutional Adoption Strategy")

    beneficiaries = [
        ("FORENSIC SCIENCE LABORATORIES (RFSLs)", "Cuts case backlog by 80%. Automated screening triage prioritizes suspicious exhibits for deep examination, producing reproducible court-admissible dossiers under Section 63 BSA.", 0.8),
        ("POLICE CYBER CRIME CELLS", "Equips investigators with an instant triage tool to verify digital screenshots, viral disinformation, and extortion media without requiring deep computer vision PhDs.", 4.8),
        ("INSURANCE & BANKING FRAUD UNITS", "Detects cloned receipts, altered medical bills, and synthetic vehicular crash photos before claim disbursement, saving institutions millions in fraudulent payouts.", 8.8)
    ]
    for b_title, b_desc, left in beneficiaries:
        add_card(slide5, left, 1.4, 3.733, 2.7, bg_color=LIGHT_BG)
        box = slide5.shapes.add_textbox(Inches(left + 0.15), Inches(1.5), Inches(3.4), Inches(2.4))
        btf = box.text_frame
        btf.word_wrap = True
        bp0 = btf.paragraphs[0]
        bp0.text = b_title
        bp0.font.size = Pt(11)
        bp0.font.bold = True
        bp0.font.color.rgb = NAVY
        bp1 = btf.add_paragraph()
        bp1.text = f"\n{b_desc}"
        bp1.font.size = Pt(10)
        bp1.font.color.rgb = TEXT_DARK

    # Bottom Grid: Cost-Benefit & Competitive Advantage (2 Cards)
    add_card(slide5, 0.8, 4.3, 5.7, 2.6, bg_color=CARD_BG)
    box_l = slide5.shapes.add_textbox(Inches(1.0), Inches(4.4), Inches(5.3), Inches(2.3))
    tf_l = box_l.text_frame
    tf_l.word_wrap = True
    p0 = tf_l.paragraphs[0]
    p0.text = "WHY SCSS SATYA WINS OVER EXISTING TOOLS"
    p0.font.size = Pt(12)
    p0.font.bold = True
    p0.font.color.rgb = NAVY
    comp_points = [
        "No Black Box Opacity: Every finding is tied to explainable physical metrics (Fourier frequencies, noise residuals, keypoint vectors).",
        "Air-Gapped Privacy: Runs locally on evidence workstations; no confidential crime scene or financial files uploaded to external cloud APIs.",
        "Zero Cloud Dependency Fees: No recurring per-image API charges for government or law enforcement agencies."
    ]
    for cp in comp_points:
        p = tf_l.add_paragraph()
        p.text = f"✓ {cp}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_DARK

    add_card(slide5, 6.8, 4.3, 5.7, 2.6, bg_color=CARD_BG)
    box_r = slide5.shapes.add_textbox(Inches(7.0), Inches(4.4), Inches(5.3), Inches(2.3))
    tf_r = box_r.text_frame
    tf_r.word_wrap = True
    p0 = tf_r.paragraphs[0]
    p0.text = "PROPOSED STATE PILOT PARTNERSHIP"
    p0.font.size = Pt(12)
    p0.font.bold = True
    p0.font.color.rgb = NAVY
    pilot_points = [
        "Regional Forensic Science Laboratories (RFSL): Proposed pilot integration for initial digital evidence intake and triage.",
        "State Police Cyber Crime Divisions: Field validation with active case evidence and forensic examiner feedback loops.",
        "Public Insurance Verification: Automated validation pipeline for digital claim documentation and damaged property exhibits."
    ]
    for pp in pilot_points:
        p = tf_r.add_paragraph()
        p.text = f"▶ {pp}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_DARK

    # =========================================================================
    # SLIDE 6: Team, Institutional Capability & Budget Outlay
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "Team, Institutional Heritage & ₹10 Lakh Award Budget Outlay")

    # Left: Team & Institution
    add_card(slide6, 0.8, 1.4, 5.7, 5.5, bg_color=CARD_BG)
    t_box = slide6.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(5.3), Inches(5.2))
    tf = t_box.text_frame
    tf.word_wrap = True
    p0 = tf.paragraphs[0]
    p0.text = "APPLICANT INSTITUTION & CORE EXPERTISE"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = NAVY

    t_desc = [
        ("Sure Clue Scientific Solutions (SCSS)", "Forensic science consultancy and digital evidence investigation firm with deep domain roots in question document analysis, forensic reporting, and multimedia integrity."),
        ("Abhishek Dixit (Domain & Product Lead)", "Forensic scientist leading research in passive-blind, non-invasive digital image analysis, scientific limitations disclosure, and court-admissible evidence reporting."),
        ("Engineering & Computer Vision Team", "Specialists in applied digital signal processing, Fourier transform analysis, secure FastAPI backend engineering, and institutional React interface design."),
        ("Forensic Advisory & Academic Roots", "Mentored by senior forensic professors and digital evidence practitioners across Maharashtra and Chhattisgarh.")
    ]
    for title, desc in t_desc:
        hp = tf.add_paragraph()
        hp.text = f"\n▶ {title}"
        hp.font.size = Pt(10.5)
        hp.font.bold = True
        hp.font.color.rgb = GOLD
        dp = tf.add_paragraph()
        dp.text = desc
        dp.font.size = Pt(9.5)
        dp.font.color.rgb = TEXT_DARK

    # Right: Utilization of ₹10 Lakh Cash Prize (Costed Budget)
    add_card(slide6, 6.8, 1.4, 5.7, 5.5, bg_color=LIGHT_BG)
    b_box = slide6.shapes.add_textbox(Inches(7.0), Inches(1.5), Inches(5.3), Inches(5.2))
    btf = b_box.text_frame
    btf.word_wrap = True
    bp0 = btf.paragraphs[0]
    bp0.text = "UTILIZATION OF ₹10 LAKH SEVA FIRST AWARD"
    bp0.font.size = Pt(13)
    bp0.font.bold = True
    bp0.font.color.rgb = NAVY

    budget_items = [
        ("Algorithm Hardening & Dataset Benchmarking", "40% (₹4,00,000)", "Validation on open benchmark datasets (CASIA, CoMoFoD, Columbia) and training lightweight ONNX diffusion residual models for deepfake classification."),
        ("Tamper-Proof Evidence Vault & HSM Integration", "25% (₹2,50,000)", "Hardening isolated evidence vault with hardware security module (HSM) digital signatures for ISO/IEC 27037 compliance."),
        ("State Forensic Laboratory Pilot Deployment", "20% (₹2,00,000)", "Field testing, examiner UI optimization, and calibration with Regional Forensic Science Laboratories and cyber police units."),
        ("ISO 17025 Pre-Accreditation & Quality Audits", "15% (₹1,50,000)", "Formal validation documentation, uncertainty budget estimation, and peer review for institutional legal admissibility.")
    ]
    for b_title, b_amt, b_desc in budget_items:
        hp = btf.add_paragraph()
        hp.text = f"\n• {b_title} — {b_amt}"
        hp.font.size = Pt(10)
        hp.font.bold = True
        hp.font.color.rgb = NAVY
        dp = btf.add_paragraph()
        dp.text = b_desc
        dp.font.size = Pt(9)
        dp.font.color.rgb = TEXT_MUTED

    # Ensure docs directory exists
    out_dir = Path(__file__).resolve().parent.parent / "docs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "SCSS_SATYA_SEVA_FIRST_2026_Pitch_Deck.pptx"
    prs.save(str(out_path))
    print(f"Presentation successfully created at: {out_path}")

if __name__ == "__main__":
    create_deck()
