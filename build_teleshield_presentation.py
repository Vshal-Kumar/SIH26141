import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    output_path = "TeleShield_SIH2026_Idea_Presentation.pptx"
    prs = pptx.Presentation("SIH2026-IDEA-Presentation-Format.pptx")
    print(f"Loaded presentation with {len(prs.slides)} slides.")

    # Remove Slide 7 if present (Instruction slide)
    if len(prs.slides) > 6:
        rId = prs.slides._sldIdLst[6].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[6]
        print("Removed Slide 7 (instructions). Slide count:", len(prs.slides))

    # Color Palette definitions matching PPT Theme
    C_BLUE = RGBColor(0, 112, 192)        # SIH Brand Blue #0070C0
    C_DARK_BLUE = RGBColor(0, 32, 96)     # Deep Navy #002060
    C_SLATE = RGBColor(15, 23, 42)        # Dark slate #0F172A
    C_BODY = RGBColor(30, 41, 59)         # Body text #1E293B
    C_MUTED = RGBColor(100, 116, 139)     # Muted gray #64748B
    C_BG_CARD = RGBColor(248, 250, 252)   # Light Card Fill #F8FAFC
    C_BORDER = RGBColor(203, 213, 225)    # Card Border #CBD5E1
    C_GREEN = RGBColor(16, 149, 93)       # Verified Green #10955D
    C_RED = RGBColor(220, 38, 38)         # Threat Red #DC2626
    C_CYAN = RGBColor(2, 132, 199)        # Accent Cyan #0284C7
    C_AMBER = RGBColor(217, 119, 6)       # Warning Amber #D97706
    C_WHITE = RGBColor(255, 255, 255)     # White
    C_ACCENT_BG = RGBColor(238, 246, 255) # Light blue card tint

    # Helper: add card
    def add_card(slide, left, top, width, height, bg_color=C_BG_CARD, border_color=C_BORDER, border_width=1.0):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(border_width)
        return shape

    # Helper: add text box
    def add_textbox(slide, left, top, width, height):
        tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.08)
        tf.margin_right = Inches(0.08)
        tf.margin_top = Inches(0.06)
        tf.margin_bottom = Inches(0.06)
        return tf

    # Clean non-base shapes from slide 2 to 6
    def clean_slide_body(slide):
        to_remove = []
        for shp in slide.shapes:
            is_base = (
                shp.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.PICTURE or
                "Title 1" in shp.name or shp.name == "Title 1" or
                "Slide Number" in shp.name or
                "Footer" in shp.name or
                "Oval" in shp.name or
                (shp.name.startswith("Rectangle") and shp.top > 6000000)
            )
            if not is_base:
                to_remove.append(shp)
        for shp in to_remove:
            sp = shp._element
            sp.getparent().remove(sp)

    # Configure slide header (Title 1)
    def setup_header(slide, title_text, subtitle_text):
        for shp in slide.shapes:
            if "Title 1" in shp.name or shp.name == "Title 1":
                shp.left = Inches(1.95)
                shp.top = Inches(0.12)
                shp.width = Inches(8.60)
                shp.height = Inches(0.95)
                tf = shp.text_frame
                tf.clear()
                tf.word_wrap = True
                tf.margin_left = Inches(0.05)
                tf.margin_top = Inches(0.02)
                tf.margin_bottom = Inches(0.02)
                
                # Title
                p0 = tf.paragraphs[0]
                p0.text = title_text
                p0.font.name = "Arial"
                p0.font.size = Pt(20)
                p0.font.bold = True
                p0.font.color.rgb = C_DARK_BLUE
                p0.alignment = PP_ALIGN.LEFT
                p0.space_after = Pt(2)

                # Subtitle
                p1 = tf.add_paragraph()
                p1.text = subtitle_text
                p1.font.name = "Arial"
                p1.font.size = Pt(10.5)
                p1.font.bold = True
                p1.font.color.rgb = C_BLUE
                p1.alignment = PP_ALIGN.LEFT
                break

    # Style team oval
    def setup_team_oval(slide):
        for shp in slide.shapes:
            if "Oval" in shp.name and shp.has_text_frame:
                shp.left = Inches(0.36)
                shp.top = Inches(0.18)
                shp.width = Inches(1.45)
                shp.height = Inches(0.85)
                tf = shp.text_frame
                tf.text = "TeleShield"
                for p in tf.paragraphs:
                    p.alignment = PP_ALIGN.CENTER
                    p.font.name = "Arial"
                    p.font.size = Pt(11)
                    p.font.bold = True
                    p.font.color.rgb = C_WHITE
                shp.fill.solid()
                shp.fill.fore_color.rgb = C_BLUE
                shp.line.color.rgb = C_WHITE
                shp.line.width = Pt(1.5)

    # =========================================================================
    # SLIDE 1: TITLE PAGE
    # =========================================================================
    print("Formatting Slide 1 (TITLE PAGE)...")
    s1 = prs.slides[0]

    # Clean Slide 1: remove any non-base elements
    to_remove = []
    for shp in s1.shapes:
        if shp.name not in ["Picture 1", "Title 7", "Subtitle 3", "TextBox 9"]:
            to_remove.append(shp)
    for shp in to_remove:
        sp = shp._element
        sp.getparent().remove(sp)

    # Configure Title 7
    for shp in s1.shapes:
        if shp.name == "Title 7":
            shp.left = Inches(0.40)
            shp.top = Inches(0.20)
            shp.width = Inches(10.0)
            shp.height = Inches(0.90)
            tf = shp.text_frame
            tf.clear()
            p = tf.paragraphs[0]
            p.text = "SMART INDIA HACKATHON 2026"
            p.font.name = "Garamond"
            p.font.size = Pt(36)
            p.font.bold = True
            p.font.color.rgb = C_DARK_BLUE

    # Configure Subtitle 3
    for shp in s1.shapes:
        if shp.name == "Subtitle 3":
            shp.left = Inches(0.40)
            shp.top = Inches(1.15)
            shp.width = Inches(5.8)
            shp.height = Inches(0.45)
            tf = shp.text_frame
            tf.clear()
            p = tf.paragraphs[0]
            p.text = "TITLE PAGE • INNOVATION PITCH"
            p.font.name = "Arial"
            p.font.size = Pt(12)
            p.font.bold = True
            p.font.color.rgb = C_BLUE

    # Configure TextBox 9 (metadata fields)
    for shp in s1.shapes:
        if shp.name == "TextBox 9":
            shp.left = Inches(0.40)
            shp.top = Inches(1.70)
            shp.width = Inches(5.85)
            shp.height = Inches(4.90)
            tf = shp.text_frame
            tf.clear()
            
            fields = [
                ("Problem Statement ID", "26141"),
                ("Problem Statement Title", "Quantum-Inspired Cyber Threat Detection Framework for Teleportation-Based Quantum Digital Signatures"),
                ("Theme", "Blockchain & Cybersecurity (Quantum Security)"),
                ("PS Category", "Software"),
                ("Team ID", "[INSERT TEAM ID]"),
                ("Team Name", "TeleShield / HexaCore (Registered on portal)"),
            ]

            for idx, (label, val) in enumerate(fields):
                p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
                p.space_after = Pt(5)
                r_lbl = p.add_run()
                r_lbl.text = f"{label} – "
                r_lbl.font.name = "Arial"
                r_lbl.font.size = Pt(10.5)
                r_lbl.font.bold = True
                r_lbl.font.color.rgb = C_DARK_BLUE

                r_val = p.add_run()
                r_val.text = val
                r_val.font.name = "Arial"
                r_val.font.size = Pt(10.5)
                r_val.font.bold = (label in ["Problem Statement ID", "PS Category"])
                r_val.font.color.rgb = C_BODY

            p_pitch = tf.add_paragraph()
            p_pitch.space_before = Pt(8)
            r_pitch = p_pitch.add_run()
            r_pitch.text = "Solution Pitch: "
            r_pitch.font.name = "Arial"
            r_pitch.font.size = Pt(10.5)
            r_pitch.font.bold = True
            r_pitch.font.color.rgb = C_BLUE

            r_pitch_text = p_pitch.add_run()
            r_pitch_text.text = "Full-stack teleportation QDS framework with deterministic Q-STAT threat engine, Hoeffding/Chernoff statistical bounds, 10 attack classes & dual hardware profiles (0% AI/ML)."
            r_pitch_text.font.name = "Arial"
            r_pitch_text.font.size = Pt(9.5)
            r_pitch_text.font.italic = True
            r_pitch_text.font.color.rgb = C_SLATE

    # Add diagram on Slide 1
    s1.shapes.add_picture("slide1_teleshield_pipeline.png", Inches(6.45), Inches(1.25), Inches(6.35), Inches(5.35))
    print("  Slide 1 complete.")

    # =========================================================================
    # SLIDE 2: IDEA TITLE
    # =========================================================================
    print("Formatting Slide 2 (IDEA TITLE)...")
    s2 = prs.slides[1]
    clean_slide_body(s2)
    setup_team_oval(s2)
    setup_header(s2, "IDEA TITLE: TELESHIELD", "Quantum-Inspired Cyber Threat Detection for Teleportation-Based QDS")

    # 1. Top Story Flow (Problem to Solution)
    add_card(s2, 0.6, 1.15, 12.13, 0.55, bg_color=C_ACCENT_BG, border_color=C_BLUE, border_width=1.2)
    tf_flow = add_textbox(s2, 0.65, 1.15, 12.03, 0.55)
    p = tf_flow.paragraphs[0]
    p.text = "PROBLEM-TO-SOLUTION TRAJECTORY: "
    p.font.name = "Arial"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = C_DARK_BLUE
    
    steps = [
        ("RSA/ECC Cryptosystems", "Shor's Threat"),
        ("Active Adversarial Tampering", "Forgery & Replay"),
        ("Teleportation-Based QDS", "Information-Theoretic Security"),
        ("TeleShield Q-STAT Engine", "Deterministic Detection"),
        ("Tamper-Proof Verdict", "0% AI/ML • Provable Safety")
    ]
    for i, (head, sub) in enumerate(steps):
        r = p.add_run()
        r.text = f"[{head}]"
        r.font.name = "Arial"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = C_BLUE if i < 3 else C_GREEN
        if i < len(steps) - 1:
            r_arr = p.add_run()
            r_arr.text = " ➔ "
            r_arr.font.bold = True
            r_arr.font.color.rgb = C_MUTED

    # 2. Left Column: PROPOSED SOLUTION & THREAT ENGINE (Pointers 1, 2, 3)
    add_card(s2, 0.6, 1.80, 5.95, 2.65, bg_color=C_WHITE, border_color=C_BORDER, border_width=1.0)
    add_card(s2, 0.6, 1.80, 5.95, 0.38, bg_color=C_DARK_BLUE, border_color=C_DARK_BLUE)
    tf_hl = add_textbox(s2, 0.7, 1.82, 5.75, 0.35)
    p = tf_hl.paragraphs[0]
    p.text = "PROPOSED SOLUTION & HOW IT ADDRESSES THE PROBLEM (THREAT TAXONOMY)"
    p.font.name = "Arial"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    tf_threats = add_textbox(s2, 0.7, 2.22, 5.75, 2.15)
    threats_data = [
        ("FORGERY ATTACKS", "Random state injection & splice tampering detected via non-orthogonal projection mismatch exceeding Chernoff threshold s_a; random guessing bound P_FA ≤ exp(-2L(p_f - s_a)^2).", C_RED),
        ("IMPERSONATION", "Man-in-the-Middle spoofing signer identity blocked without pre-shared Bell pairs; orthogonal basis collapse prevents authentic verification.", C_RED),
        ("REPLAY & FRESHNESS", "Stale quantum signatures intercepted and replayed rejected via sequential nonces, session timestamps, and quantum state collapse.", C_RED),
        ("CHANNEL MANIPULATION", "Bit-flip (X), dephasing (Z), depolarizing noise & intercept-resend detected via Bell-state fidelity decay and CHSH violation tracking (S = 2√2V).", C_RED)
    ]
    for i, (title, desc, col) in enumerate(threats_data):
        p = tf_threats.paragraphs[0] if i == 0 else tf_threats.add_paragraph()
        p.space_after = Pt(3)
        r_t = p.add_run()
        r_t.text = f"• {title}: "
        r_t.font.name = "Arial"
        r_t.font.size = Pt(8.5)
        r_t.font.bold = True
        r_t.font.color.rgb = col
        r_d = p.add_run()
        r_d.text = desc
        r_d.font.name = "Arial"
        r_d.font.size = Pt(8)
        r_d.font.color.rgb = C_BODY

    # 3. Right Column: INNOVATION & UNIQUENESS (Pointer 4)
    add_card(s2, 6.78, 1.80, 5.95, 2.65, bg_color=C_WHITE, border_color=C_BORDER, border_width=1.0)
    add_card(s2, 6.78, 1.80, 5.95, 0.38, bg_color=C_BLUE, border_color=C_BLUE)
    tf_hr = add_textbox(s2, 6.88, 1.82, 5.75, 0.35)
    p = tf_hr.paragraphs[0]
    p.text = "INNOVATION & UNIQUENESS OF THE SOLUTION (4 CORE PILLARS)"
    p.font.name = "Arial"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    tf_innov = add_textbox(s2, 6.88, 2.22, 5.75, 2.15)
    innov_data = [
        ("Quantum-Native Measurement Analysis", "Direct Pauli projective statistics (X/Z, extended X/Y/Z) without full state tomography. O(1) state complexity vs O(2^n) tomography overhead.", C_CYAN),
        ("Zero AI / Zero ML (100% Deterministic)", "No opaque black-box neural networks, no training bias, no false confidence, and zero hallucination risk. 100% explainable mathematical proof.", C_GREEN),
        ("Mathematically Derived Statistical Thresholds", "Analytical acceptance threshold s_a from Hoeffding/Chernoff bounds: P_FR ≤ exp(-2L(s_a - ε)^2), P_FA ≤ exp(-2L(p_f - s_a)^2). Zero hardcoded cutoffs.", C_BLUE),
        ("Hardware-Aware Dual-Profile Architecture", "Calibrated simulation profiles for Ion-Trap (Qiskit Aer depolarizing/dephasing) and Rydberg/Neutral-Atom (Pulser Hamiltonian) with Clifford scaling via Stim.", C_SLATE)
    ]
    for i, (title, desc, col) in enumerate(innov_data):
        p = tf_innov.paragraphs[0] if i == 0 else tf_innov.add_paragraph()
        p.space_after = Pt(3)
        r_t = p.add_run()
        r_t.text = f"{i+1}. {title}: "
        r_t.font.name = "Arial"
        r_t.font.size = Pt(8.5)
        r_t.font.bold = True
        r_t.font.color.rgb = col
        r_d = p.add_run()
        r_d.text = desc
        r_d.font.name = "Arial"
        r_d.font.size = Pt(8)
        r_d.font.color.rgb = C_BODY

    # 4. Bottom Card: DETAILED EXPLANATION & PIPELINE ARCHITECTURE (Pointer 2)
    add_card(s2, 0.6, 4.55, 12.13, 2.20, bg_color=C_BG_CARD, border_color=C_BLUE, border_width=1.2)
    tf_pipe_hdr = add_textbox(s2, 0.7, 4.58, 11.9, 0.32)
    p = tf_pipe_hdr.paragraphs[0]
    p.text = "DETAILED EXPLANATION: END-TO-END TELEPORTATION QDS ARCHITECTURE & WORKING MECHANISM"
    p.font.name = "Arial"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = C_DARK_BLUE

    pipe_steps = [
        ("1. MESSAGE", "M ∈ {0,1}^k\nClassical text", C_DARK_BLUE),
        ("2. QDS STATES", "Pauli eigenstates\nX, Z (ext. Y)", C_CYAN),
        ("3. EPR SOURCE", "|Φ⁺⟩ = (|00⟩+|11⟩)/√2\nBell distribution", C_CYAN),
        ("4. TELEPORT", "CNOT + H\nBell measurement", C_BLUE),
        ("5. CORRECTION", "Pauli feed-forward\nX^{m1} Z^{m0}", C_AMBER),
        ("6. VERIFIER", "Quantum memory\nStorage of states", C_SLATE),
        ("7. READOUT", "Projective basis\nΠ_Z, Π_X readout", C_SLATE),
        ("8. Q-STAT", "Statistical triage\nBinomial / SPRT", C_GREEN),
        ("9. VERDICT", "ACCEPT / REJECT\nHash-chained log", C_GREEN)
    ]
    b_w = 1.25
    b_gap = 0.08
    b_left_start = 0.72
    for i, (b_title, b_sub, b_col) in enumerate(pipe_steps):
        x = b_left_start + i * (b_w + b_gap)
        add_card(s2, x, 4.92, b_w, 1.25, bg_color=C_WHITE, border_color=b_col, border_width=1.2)
        tf_b = add_textbox(s2, x + 0.02, 4.95, b_w - 0.04, 1.15)
        p1 = tf_b.paragraphs[0]
        p1.alignment = PP_ALIGN.CENTER
        p1.text = b_title
        p1.font.name = "Arial"
        p1.font.size = Pt(8.5)
        p1.font.bold = True
        p1.font.color.rgb = b_col

        p2 = tf_b.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        p2.text = b_sub
        p2.font.name = "Arial"
        p2.font.size = Pt(7.5)
        p2.font.color.rgb = C_BODY
        p2.space_before = Pt(3)

    tf_fnote = add_textbox(s2, 0.7, 6.30, 11.9, 0.35)
    p = tf_fnote.paragraphs[0]
    p.text = "Configurable Demo Baseline: n = 64 tag bits, L = 222 states/bit, 10,000 shots (simulation parameters, not claimed hardware limits). Strict 0% AI/ML statistical decision."
    p.font.name = "Arial"
    p.font.size = Pt(8)
    p.font.italic = True
    p.font.color.rgb = C_MUTED
    print("  Slide 2 complete.")

    # =========================================================================
    # SLIDE 3: TECHNICAL APPROACH
    # =========================================================================
    print("Formatting Slide 3 (TECHNICAL APPROACH)...")
    s3 = prs.slides[2]
    clean_slide_body(s3)
    setup_team_oval(s3)
    setup_header(s3, "TECHNICAL APPROACH", "Technology Stack, Mathematical Model & 9-Stage Q-STAT Detection Pipeline")

    # 1. Top Left: TECHNOLOGIES TO BE USED (Pointer 1)
    add_card(s3, 0.6, 1.15, 5.95, 2.50, bg_color=C_WHITE, border_color=C_BORDER, border_width=1.0)
    add_card(s3, 0.6, 1.15, 5.95, 0.35, bg_color=C_DARK_BLUE, border_color=C_DARK_BLUE)
    tf_tech_hdr = add_textbox(s3, 0.7, 1.17, 5.75, 0.32)
    p = tf_tech_hdr.paragraphs[0]
    p.text = "TECHNOLOGIES & QUANTUM SOFTWARE STACK (POINTER 1)"
    p.font.name = "Arial"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    tf_tech_body = add_textbox(s3, 0.7, 1.52, 5.75, 2.05)
    tech_items = [
        ("Core & Reference Backend", "Python 3.11+, NumPy, SciPy (Reference exact numerical state-vector engine; 100% deterministic baseline).", C_BLUE),
        ("Primary Simulation Engine", "Qiskit 1.0+ & Qiskit Aer (Emulates quantum circuits, Bell pairs, Kraus operators & noisy quantum channels).", C_CYAN),
        ("Clifford & Neutral-Atom Engines", "Stim (Ultra-fast O(N) Clifford simulation for 10^5+ shots) + Pulser (Neutral-atom Hamiltonian pulse simulation).", C_SLATE),
        ("Hardware Profile Alignment", "Trapped-Ion simulation profile (dephasing/heating noise) & Rydberg neutral-atom hardware-aware profile.", C_DARK_BLUE),
        ("API & Triage Dashboard", "FastAPI (Async REST API service) + Streamlit & Plotly (Real-time explainable Q-STAT visual triage dashboard).", C_GREEN)
    ]
    for i, (cat, desc, col) in enumerate(tech_items):
        p = tf_tech_body.paragraphs[0] if i == 0 else tf_tech_body.add_paragraph()
        p.space_after = Pt(2.5)
        r_c = p.add_run()
        r_c.text = f"• {cat}: "
        r_c.font.name = "Arial"
        r_c.font.size = Pt(8.5)
        r_c.font.bold = True
        r_c.font.color.rgb = col
        r_d = p.add_run()
        r_d.text = desc
        r_d.font.name = "Arial"
        r_d.font.size = Pt(8)
        r_d.font.color.rgb = C_BODY

    # 2. Top Right: MATHEMATICAL MODEL & STATISTICAL BOUNDS (Pointer 2)
    add_card(s3, 6.78, 1.15, 5.95, 2.50, bg_color=C_WHITE, border_color=C_BORDER, border_width=1.0)
    add_card(s3, 6.78, 1.15, 5.95, 0.35, bg_color=C_BLUE, border_color=C_BLUE)
    tf_math_hdr = add_textbox(s3, 6.88, 1.17, 5.75, 0.32)
    p = tf_math_hdr.paragraphs[0]
    p.text = "MATHEMATICAL FORMULATION & HOEFFDING/CHERNOFF ERROR BOUNDS"
    p.font.name = "Arial"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    tf_math_body = add_textbox(s3, 6.88, 1.52, 5.75, 2.05)
    math_items = [
        ("Binomial Statistical Model", "Per-block mismatch X_j ~ Binomial(L, p), observed mismatch rate m_j = X_j / L against analytical threshold s_a.", C_BLUE),
        ("False Rejection Bound (Honest)", "P_FR ≤ exp(-2L(s_a - ε)^2); across n blocks: P_FR,total ≤ n exp(-2L(s_a - ε)^2) (guaranteed < 10^-6).", C_GREEN),
        ("Forgery Acceptance Bound (Attacker)", "Random guessing p_f = 1/2 implies strict forgery bound P_FA ≤ exp(-2L(p_f - s_a)^2) (guaranteed < 10^-9).", C_RED),
        ("CHSH Entanglement Test", "Werner state parameterization S = 2√2 V; S > 2 confirms non-locality; S ≤ 2 triggers channel intercept alarm.", C_DARK_BLUE),
        ("Sequential & Session Drift", "SPRT early-exit verification (Wald's bounds) + CUSUM cumulative sum tracking for slow adversarial drift.", C_CYAN)
    ]
    for i, (cat, desc, col) in enumerate(math_items):
        p = tf_math_body.paragraphs[0] if i == 0 else tf_math_body.add_paragraph()
        p.space_after = Pt(2.5)
        r_c = p.add_run()
        r_c.text = f"• {cat}: "
        r_c.font.name = "Arial"
        r_c.font.size = Pt(8.5)
        r_c.font.bold = True
        r_c.font.color.rgb = col
        r_d = p.add_run()
        r_d.text = desc
        r_d.font.name = "Arial"
        r_d.font.size = Pt(8)
        r_d.font.color.rgb = C_BODY

    # 3. Middle-Bottom Left: Embedded Quantum Circuit
    s3.shapes.add_picture("slide3_quantum_circuit.png", Inches(0.6), Inches(3.75), Inches(5.95), Inches(2.95))

    # 4. Middle-Bottom Right: 9-STAGE Q-STAT PIPELINE (Pointer 2)
    add_card(s3, 6.78, 3.75, 5.95, 2.95, bg_color=C_WHITE, border_color=C_BORDER, border_width=1.0)
    add_card(s3, 6.78, 3.75, 5.95, 0.35, bg_color=C_DARK_BLUE, border_color=C_DARK_BLUE)
    tf_qstat_hdr = add_textbox(s3, 6.88, 3.77, 5.75, 0.32)
    p = tf_qstat_hdr.paragraphs[0]
    p.text = "METHODOLOGY: Q-STAT 9-STAGE THREAT TRIAGE PIPELINE"
    p.font.name = "Arial"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    tf_stages = add_textbox(s3, 6.88, 4.12, 5.75, 2.50)
    qstat_stages = [
        ("1. Envelope Check", "JSON schema validation, parameter bounding & payload integrity."),
        ("2. Freshness Check", "Timestamp, sequence number, and nonce check against replay."),
        ("3. Authorization Check", "Signer public key identity and registry authorization verification."),
        ("4. Message Integrity", "Classical cryptographic hash comparison across signer and verifier."),
        ("5. Quantum Measurement", "Projective measurement on verifier's teleported qubits in X/Z bases."),
        ("6. Binomial / SPRT Decision", "Sequential hypothesis testing against calculated s_a (0 AI/ML)."),
        ("7. Attack Fingerprinting", "Classifies signature vector across 10 distinct attack/noise classes."),
        ("8. CHSH / CUSUM Check", "Entanglement visibility verification (S = 2√2V) & cumulative drift."),
        ("9. Verdict & Audit Log", "ACCEPT / REJECT verdict with SHA-256 hash-chained immutable log.")
    ]
    for i, (stg, desc) in enumerate(qstat_stages):
        p = tf_stages.paragraphs[0] if i == 0 else tf_stages.add_paragraph()
        p.space_after = Pt(1.5)
        r_s = p.add_run()
        r_s.text = f"{stg}: "
        r_s.font.name = "Arial"
        r_s.font.size = Pt(8)
        r_s.font.bold = True
        r_s.font.color.rgb = C_BLUE if i < 6 else C_GREEN
        r_d = p.add_run()
        r_d.text = desc
        r_d.font.name = "Arial"
        r_d.font.size = Pt(7.5)
        r_d.font.color.rgb = C_BODY
    print("  Slide 3 complete.")

    # =========================================================================
    # SLIDE 4: FEASIBILITY AND VIABILITY
    # =========================================================================
    print("Formatting Slide 4 (FEASIBILITY AND VIABILITY)...")
    s4 = prs.slides[3]
    clean_slide_body(s4)
    setup_team_oval(s4)
    setup_header(s4, "FEASIBILITY AND VIABILITY", "Rigorous Feasibility Analysis, Threat Risks & Engineering Mitigation Strategies")

    col_w = 3.90
    col_gap = 0.21
    col_top = 1.15
    col_h = 4.45

    # Column 1: FEASIBILITY
    c1_left = 0.60
    add_card(s4, c1_left, col_top, col_w, col_h, bg_color=C_WHITE, border_color=C_BORDER, border_width=1.0)
    add_card(s4, c1_left, col_top, col_w, 0.40, bg_color=C_BLUE, border_color=C_BLUE)
    tf_c1_h = add_textbox(s4, c1_left + 0.1, col_top + 0.04, col_w - 0.2, 0.35)
    p = tf_c1_h.paragraphs[0]
    p.text = "1. ANALYSIS OF FEASIBILITY (POINTER 1)"
    p.font.name = "Arial"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    tf_c1 = add_textbox(s4, c1_left + 0.1, col_top + 0.45, col_w - 0.2, col_h - 0.55)
    c1_points = [
        ("Software Feasibility", "Built entirely on standard Python 3.11+, Qiskit 1.0+, Stim, and SciPy. Zero proprietary runtime requirements; fully containerized via Docker."),
        ("Computational Feasibility", "Clifford-dominated teleportation circuits simulate in polynomial time O(N) using Stim, enabling 10^5+ Monte Carlo shots in seconds without clusters."),
        ("Hardware Feasibility", "Decoupled backend architecture models physical NISQ systems (depolarizing, thermal relaxation, gate crosstalk) via calibrated Qiskit Aer & Pulser profiles."),
        ("Measurement Scalability", "Projective measurements evaluate in O(1) time per shot via fast binomial statistics and SPRT early-stopping; avoids exponential tomography."),
        ("Reproducibility & Standards", "Open architecture with explicit YAML configuration schemas, automated pytest suites (32+ tests passing), and deterministic seeds.")
    ]
    for i, (title, desc) in enumerate(c1_points):
        p = tf_c1.paragraphs[0] if i == 0 else tf_c1.add_paragraph()
        p.space_after = Pt(4)
        r_t = p.add_run()
        r_t.text = f"• {title}: "
        r_t.font.name = "Arial"
        r_t.font.size = Pt(8.5)
        r_t.font.bold = True
        r_t.font.color.rgb = C_BLUE
        r_d = p.add_run()
        r_d.text = desc
        r_d.font.name = "Arial"
        r_d.font.size = Pt(8)
        r_d.font.color.rgb = C_BODY

    # Column 2: CHALLENGES & RISKS
    c2_left = c1_left + col_w + col_gap
    add_card(s4, c2_left, col_top, col_w, col_h, bg_color=C_WHITE, border_color=C_BORDER, border_width=1.0)
    add_card(s4, c2_left, col_top, col_w, 0.40, bg_color=C_RED, border_color=C_RED)
    tf_c2_h = add_textbox(s4, c2_left + 0.1, col_top + 0.04, col_w - 0.2, 0.35)
    p = tf_c2_h.paragraphs[0]
    p.text = "2. POTENTIAL CHALLENGES & RISKS (POINTER 2)"
    p.font.name = "Arial"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    tf_c2 = add_textbox(s4, c2_left + 0.1, col_top + 0.45, col_w - 0.2, col_h - 0.55)
    c2_points = [
        ("Simulation Complexity", "Exponential state-vector memory explosion (2^N) in full density matrix simulators when scaling multi-party quantum signatures."),
        ("Noise vs. Attack Ambiguity", "Physical thermal relaxation and gate infidelity resembling low-rate adversarial eavesdropping or intercept-resend attacks."),
        ("False Rejection Risk", "Strict acceptance thresholds rejecting valid honest signatures under unexpected physical channel jitter or environmental drift."),
        ("Sub-Threshold Stealth Attacks", "Sophisticated adversaries injecting errors just below detection limits (threshold-aware attackers evading static bounds)."),
        ("Hardware Profile Discrepancies", "Trapped-ion shuttling delays vs. Rydberg neutral-atom blockade leakage creating divergent physical error signatures.")
    ]
    for i, (title, desc) in enumerate(c2_points):
        p = tf_c2.paragraphs[0] if i == 0 else tf_c2.add_paragraph()
        p.space_after = Pt(4)
        r_t = p.add_run()
        r_t.text = f"• {title}: "
        r_t.font.name = "Arial"
        r_t.font.size = Pt(8.5)
        r_t.font.bold = True
        r_t.font.color.rgb = C_RED
        r_d = p.add_run()
        r_d.text = desc
        r_d.font.name = "Arial"
        r_d.font.size = Pt(8)
        r_d.font.color.rgb = C_BODY

    # Column 3: STRATEGIES & MITIGATIONS
    c3_left = c2_left + col_w + col_gap
    add_card(s4, c3_left, col_top, col_w, col_h, bg_color=C_WHITE, border_color=C_BORDER, border_width=1.0)
    add_card(s4, c3_left, col_top, col_w, 0.40, bg_color=C_GREEN, border_color=C_GREEN)
    tf_c3_h = add_textbox(s4, c3_left + 0.1, col_top + 0.04, col_w - 0.2, 0.35)
    p = tf_c3_h.paragraphs[0]
    p.text = "3. STRATEGIES & MITIGATIONS (POINTER 3)"
    p.font.name = "Arial"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    tf_c3 = add_textbox(s4, c3_left + 0.1, col_top + 0.45, col_w - 0.2, col_h - 0.55)
    c3_points = [
        ("Multi-Engine Abstraction", "Exact backend for mathematical ground truth; Stim for 10^5+ shot volumes; Aer for realistic NISQ noise emulation."),
        ("Per-Basis & Per-Block Diagnostics", "Differentiates isotropic physical noise (uniform across X/Z) from targeted adversarial tampering (asymmetric X/Z or single block)."),
        ("Analytical Chernoff Thresholds", "Mathematically derived acceptance cutoff s_a guarantees provable error bounds (P_FR < 10^-6, P_FA < 10^-9); zero hardcoded limits."),
        ("Continuous Entanglement & Drift Checks", "Werner-state CHSH test (S = 2√2V) detects channel loss; CUSUM cumulative sum tests expose creeping sub-threshold attacks."),
        ("Modular Hardware Profiles", "Ion-trap and Rydberg profiles configure independent T1, T2, gate crosstalk, and readout errors without claiming proprietary hardware.")
    ]
    for i, (title, desc) in enumerate(c3_points):
        p = tf_c3.paragraphs[0] if i == 0 else tf_c3.add_paragraph()
        p.space_after = Pt(4)
        r_t = p.add_run()
        r_t.text = f"• {title}: "
        r_t.font.name = "Arial"
        r_t.font.size = Pt(8.5)
        r_t.font.bold = True
        r_t.font.color.rgb = C_GREEN
        r_d = p.add_run()
        r_d.text = desc
        r_d.font.name = "Arial"
        r_d.font.size = Pt(8)
        r_d.font.color.rgb = C_BODY

    # Bottom Process Ribbon
    add_card(s4, 0.6, 5.75, 12.13, 0.90, bg_color=C_ACCENT_BG, border_color=C_BLUE, border_width=1.2)
    tf_proc = add_textbox(s4, 0.7, 5.78, 11.9, 0.82)
    p = tf_proc.paragraphs[0]
    p.text = "VERIFICATION & REPRODUCIBILITY LIFECYCLE: "
    p.font.name = "Arial"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = C_DARK_BLUE

    proc_steps = [
        ("SIMULATION", "Exact / Aer / Stim / Pulser"),
        ("NOISE CALIBRATION", "T1/T2 & Kraus Operators"),
        ("STATISTICAL ANALYSIS", "Binomial & Chernoff s_a"),
        ("ATTACK EVALUATION", "10 Adversarial Vectors"),
        ("REPRODUCIBLE RESULTS", "SHA-256 Hash-Chained Audit")
    ]
    for i, (stg, sub) in enumerate(proc_steps):
        r = p.add_run()
        r.text = f"[{stg}: {sub}]"
        r.font.name = "Arial"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = C_BLUE if i < 3 else C_GREEN
        if i < len(proc_steps) - 1:
            r_arr = p.add_run()
            r_arr.text = " ➔ "
            r_arr.font.bold = True
            r_arr.font.color.rgb = C_MUTED
    print("  Slide 4 complete.")

    # =========================================================================
    # SLIDE 5: IMPACT AND BENEFITS
    # =========================================================================
    print("Formatting Slide 5 (IMPACT AND BENEFITS)...")
    s5 = prs.slides[4]
    clean_slide_body(s5)
    setup_team_oval(s5)
    setup_header(s5, "IMPACT AND BENEFITS", "Target Audience Impact, Societal Benefits & Measurable Deliverables")

    # Top Banner: QUANTUM-READY CYBER DEFENCE
    add_card(s5, 0.6, 1.15, 12.13, 0.50, bg_color=C_DARK_BLUE, border_color=C_DARK_BLUE)
    tf_top_b = add_textbox(s5, 0.7, 1.18, 11.9, 0.42)
    p = tf_top_b.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "QUANTUM-READY CYBER DEFENCE: UNCONDITIONAL INTEGRITY FOR POST-RSA CRITICAL INFRASTRUCTURE"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    # Left Column: FIVE TARGET AUDIENCE & BENEFIT SECTORS (Pointer 1 & 2)
    add_card(s5, 0.6, 1.75, 6.00, 4.90, bg_color=C_WHITE, border_color=C_BORDER, border_width=1.0)
    add_card(s5, 0.6, 1.75, 6.00, 0.35, bg_color=C_BLUE, border_color=C_BLUE)
    tf_sec_h = add_textbox(s5, 0.7, 1.77, 5.8, 0.32)
    p = tf_sec_h.paragraphs[0]
    p.text = "FIVE BENEFIT SECTORS & TARGET AUDIENCE (POINTERS 1 & 2)"
    p.font.name = "Arial"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    tf_sec = add_textbox(s5, 0.7, 2.15, 5.8, 4.40)
    sectors = [
        ("1. Digital Security & Sovereign Identity", "Tamper-proof non-repudiation protects national e-governance, digital passports, legal contracts, and sovereign credentials against quantum forgery and impersonation."),
        ("2. Quantum Cybersecurity Research", "Provides an open, standardized benchmark framework for researchers to evaluate teleportation protocols, Kraus noise models, and active quantum attack strategies."),
        ("3. Hardware Readiness & Industry Transition", "Offers hardware manufacturers a standardized, low-friction application-layer testing sandbox to benchmark real NISQ trapped-ion and neutral-atom processors."),
        ("4. Explainable & Legally Auditable Security", "100% deterministic mathematical telemetry eliminates opaque neural network black-boxes, fulfilling strict regulatory compliance and evidentiary legal standards."),
        ("5. Future Quantum Networks & Repeaters", "Establishes the algorithmic foundation for the Quantum Internet, quantum repeater authentication, and multi-party quantum signature distribution networks.")
    ]
    for i, (title, desc) in enumerate(sectors):
        p = tf_sec.paragraphs[0] if i == 0 else tf_sec.add_paragraph()
        p.space_after = Pt(4)
        r_t = p.add_run()
        r_t.text = f"{title}\n"
        r_t.font.name = "Arial"
        r_t.font.size = Pt(8.5)
        r_t.font.bold = True
        r_t.font.color.rgb = C_DARK_BLUE
        r_d = p.add_run()
        r_d.text = desc
        r_d.font.name = "Arial"
        r_d.font.size = Pt(8)
        r_d.font.color.rgb = C_BODY

    # Top Right: CRITICAL REAL-WORLD APPLICATION DOMAINS
    add_card(s5, 6.80, 1.75, 5.93, 2.25, bg_color=C_WHITE, border_color=C_BORDER, border_width=1.0)
    add_card(s5, 6.80, 1.75, 5.93, 0.35, bg_color=C_DARK_BLUE, border_color=C_DARK_BLUE)
    tf_app_h = add_textbox(s5, 6.90, 1.77, 5.7, 0.32)
    p = tf_app_h.paragraphs[0]
    p.text = "CRITICAL REAL-WORLD APPLICATION DOMAINS"
    p.font.name = "Arial"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    tf_app = add_textbox(s5, 6.90, 2.15, 5.7, 1.80)
    apps = [
        ("Defense & National Security", "High-assurance command-and-control messaging with mathematically provable zero eavesdropping tolerance."),
        ("Financial Systems & CBDC", "High-value cross-border settlements, central bank digital currencies, and fraud-proof cryptographic bonds."),
        ("Critical National Infrastructure", "Power grids, nuclear command networks, and telecommunication backbones shielded from post-RSA compromise.")
    ]
    for i, (title, desc) in enumerate(apps):
        p = tf_app.paragraphs[0] if i == 0 else tf_app.add_paragraph()
        p.space_after = Pt(3)
        r_t = p.add_run()
        r_t.text = f"• {title}: "
        r_t.font.name = "Arial"
        r_t.font.size = Pt(8.5)
        r_t.font.bold = True
        r_t.font.color.rgb = C_BLUE
        r_d = p.add_run()
        r_d.text = desc
        r_d.font.name = "Arial"
        r_d.font.size = Pt(8)
        r_d.font.color.rgb = C_BODY

    # Bottom Right: MEASURABLE PROJECT CHARACTERISTICS (6 Metric Cards)
    add_card(s5, 6.80, 4.10, 5.93, 2.55, bg_color=C_BG_CARD, border_color=C_BLUE, border_width=1.2)
    tf_met_h = add_textbox(s5, 6.90, 4.12, 5.7, 0.30)
    p = tf_met_h.paragraphs[0]
    p.text = "MEASURABLE ARCHITECTURAL CHARACTERISTICS & PROJECT METRICS"
    p.font.name = "Arial"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = C_DARK_BLUE

    metrics = [
        ("0 AI / ML Models", "100% Deterministic & Provable Decision Logic", C_GREEN),
        ("3 Core Simulators", "Exact NumPy, Qiskit Aer, Stim Clifford", C_BLUE),
        ("2 Hardware Profiles", "Ion-Trap Aligned & Rydberg Aware", C_SLATE),
        ("3 Measurement Bases", "Primary X/Z, Extended Six-State X/Y/Z", C_CYAN),
        ("10 Threat Classes", "Comprehensive Adversarial Attack Matrix", C_RED),
        ("100% Audit Trail", "Cryptographic SHA-256 Hash-Chained Log", C_DARK_BLUE)
    ]
    mw, mh = 1.80, 0.85
    for idx, (m_val, m_desc, m_col) in enumerate(metrics):
        r_idx = idx // 3
        c_idx = idx % 3
        mx = 6.92 + c_idx * (mw + 0.10)
        my = 4.45 + r_idx * (mh + 0.12)
        add_card(s5, mx, my, mw, mh, bg_color=C_WHITE, border_color=m_col, border_width=1.2)
        tf_m = add_textbox(s5, mx + 0.05, my + 0.05, mw - 0.1, mh - 0.1)
        p1 = tf_m.paragraphs[0]
        p1.alignment = PP_ALIGN.CENTER
        p1.text = m_val
        p1.font.name = "Arial"
        p1.font.size = Pt(8.5)
        p1.font.bold = True
        p1.font.color.rgb = m_col

        p2 = tf_m.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        p2.text = m_desc
        p2.font.name = "Arial"
        p2.font.size = Pt(6.8)
        p2.font.color.rgb = C_BODY
        p2.space_before = Pt(2)

    tf_m_note = add_textbox(s5, 6.90, 6.42, 5.7, 0.22)
    p = tf_m_note.paragraphs[0]
    p.text = "* Architectural parameters and simulation profiles; zero unverified hardware claims."
    p.font.name = "Arial"
    p.font.size = Pt(7)
    p.font.italic = True
    p.font.color.rgb = C_MUTED
    print("  Slide 5 complete.")

    # =========================================================================
    # SLIDE 6: RESEARCH AND REFERENCES
    # =========================================================================
    print("Formatting Slide 6 (RESEARCH AND REFERENCES)...")
    s6 = prs.slides[5]
    clean_slide_body(s6)
    setup_team_oval(s6)
    setup_header(s6, "RESEARCH AND REFERENCES", "Scientific Foundations, Hardware Profile Alignment & Open Deliverables")

    rw, rh = 5.95, 2.15
    r_top1 = 1.15
    r_top2 = 3.45

    # Card 1: QDS FOUNDATIONS (Top Left)
    add_card(s6, 0.6, r_top1, rw, rh, bg_color=C_WHITE, border_color=C_BORDER, border_width=1.0)
    add_card(s6, 0.6, r_top1, rw, 0.35, bg_color=C_DARK_BLUE, border_color=C_DARK_BLUE)
    tf_c1_h = add_textbox(s6, 0.7, r_top1 + 0.03, rw - 0.2, 0.32)
    p = tf_c1_h.paragraphs[0]
    p.text = "QUANTUM DIGITAL SIGNATURES (QDS) THEORETICAL FOUNDATIONS"
    p.font.name = "Arial"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    tf_c1_b = add_textbox(s6, 0.7, r_top1 + 0.38, rw - 0.2, rh - 0.42)
    qds_refs = [
        ("D. Gottesman and I. Chuang", "\"Quantum Digital Signatures\", arXiv:quant-ph/0105032 (2001). Foundational information-theoretic protocol establishing quantum public keys, unconditional non-repudiation, and non-forgeability."),
        ("E. Andersson, M. Curty, I. Jex", "\"Practical Quantum Digital Signatures without Quantum Memory\", Phys. Rev. Lett. 96, 170501. Breakthrough enabling optical and multiport verifications."),
        ("V. Dunjko, P. Wallden, E. Andersson", "\"Quantum Digital Signatures without Quantum Memory: Protocols and Security\", Phys. Rev. A 89, 062327. Security bounds against collective coherent attacks.")
    ]
    for i, (authors, title_desc) in enumerate(qds_refs):
        p = tf_c1_b.paragraphs[0] if i == 0 else tf_c1_b.add_paragraph()
        p.space_after = Pt(2.5)
        r_a = p.add_run()
        r_a.text = f"• {authors}: "
        r_a.font.name = "Arial"
        r_a.font.size = Pt(8.5)
        r_a.font.bold = True
        r_a.font.color.rgb = C_BLUE
        r_td = p.add_run()
        r_td.text = title_desc
        r_td.font.name = "Arial"
        r_td.font.size = Pt(8)
        r_td.font.color.rgb = C_BODY

    # Card 2: TELEPORTATION & ENTANGLEMENT (Top Right)
    add_card(s6, 6.78, r_top1, rw, rh, bg_color=C_WHITE, border_color=C_BORDER, border_width=1.0)
    add_card(s6, 6.78, r_top1, rw, 0.35, bg_color=C_BLUE, border_color=C_BLUE)
    tf_c2_h = add_textbox(s6, 6.88, r_top1 + 0.03, rw - 0.2, 0.32)
    p = tf_c2_h.paragraphs[0]
    p.text = "QUANTUM TELEPORTATION & ENTANGLEMENT VERIFICATION"
    p.font.name = "Arial"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    tf_c2_b = add_textbox(s6, 6.88, r_top1 + 0.38, rw - 0.2, rh - 0.42)
    tele_refs = [
        ("C. H. Bennett et al.", "\"Teleporting an Unknown Quantum State via Dual Classical and Einstein-Podolsky-Rosen Channels\", Phys. Rev. Lett. 70, 1895 (1993). Foundational quantum teleportation mechanism."),
        ("J. F. Clauser, M. A. Horne, A. Shimony, R. A. Holt", "\"Proposed Experiment to Test Local Hidden-Variable Theories (CHSH)\", Phys. Rev. Lett. 23, 880 (1969). Bell inequality framework utilized in TeleShield."),
        ("R. F. Werner", "\"Quantum States with Einstein-Podolsky-Rosen Correlations Admitting a Hidden-Variable Model\", Phys. Rev. A 40, 4277 (1989). Parameterization for isotropic quantum channel degradation.")
    ]
    for i, (authors, title_desc) in enumerate(tele_refs):
        p = tf_c2_b.paragraphs[0] if i == 0 else tf_c2_b.add_paragraph()
        p.space_after = Pt(2.5)
        r_a = p.add_run()
        r_a.text = f"• {authors}: "
        r_a.font.name = "Arial"
        r_a.font.size = Pt(8.5)
        r_a.font.bold = True
        r_a.font.color.rgb = C_CYAN
        r_td = p.add_run()
        r_td.text = title_desc
        r_td.font.name = "Arial"
        r_td.font.size = Pt(8)
        r_td.font.color.rgb = C_BODY

    # Card 3: SOFTWARE & SIMULATION FRAMEWORKS (Bottom Left)
    add_card(s6, 0.6, r_top2, rw, rh, bg_color=C_WHITE, border_color=C_BORDER, border_width=1.0)
    add_card(s6, 0.6, r_top2, rw, 0.35, bg_color=C_CYAN, border_color=C_CYAN)
    tf_c3_h = add_textbox(s6, 0.7, r_top2 + 0.03, rw - 0.2, 0.32)
    p = tf_c3_h.paragraphs[0]
    p.text = "QUANTUM SOFTWARE, SIMULATION ENGINES & STATISTICAL TOOLS"
    p.font.name = "Arial"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    tf_c3_b = add_textbox(s6, 0.7, r_top2 + 0.38, rw - 0.2, rh - 0.42)
    soft_refs = [
        ("Qiskit & Qiskit Aer", "IBM Quantum open-source SDK for circuit synthesis, gate decomposition, density matrix emulation & Kraus channel noise modeling (https://qiskit.org)."),
        ("Stim (C. Gidney)", "\"Stim: a fast stabilizer circuit simulator\", Quantum 5, 497 (2021). Enables O(N) Clifford simulation scaling for 10^5+ shots in TeleShield's high-throughput mode."),
        ("Pulser (Pasqal)", "\"Pulser: An open-source package for the simulation of neutral-atom architectures\", Quantum 6, 629 (2022). Used for neutral-atom Hamiltonian dynamics."),
        ("SciPy & NumPy", "Provides exact binomial distribution, Sequential Probability Ratio Tests (SPRT), and Cumulative Sum (CUSUM) drift detection functions.")
    ]
    for i, (authors, title_desc) in enumerate(soft_refs):
        p = tf_c3_b.paragraphs[0] if i == 0 else tf_c3_b.add_paragraph()
        p.space_after = Pt(2.5)
        r_a = p.add_run()
        r_a.text = f"• {authors}: "
        r_a.font.name = "Arial"
        r_a.font.size = Pt(8.5)
        r_a.font.bold = True
        r_a.font.color.rgb = C_DARK_BLUE
        r_td = p.add_run()
        r_td.text = title_desc
        r_td.font.name = "Arial"
        r_td.font.size = Pt(8)
        r_td.font.color.rgb = C_BODY

    # Card 4: HARDWARE PROFILE CONTEXT & REPOSITORY (Bottom Right)
    add_card(s6, 6.78, r_top2, rw, rh, bg_color=C_WHITE, border_color=C_BORDER, border_width=1.0)
    add_card(s6, 6.78, r_top2, rw, 0.35, bg_color=C_GREEN, border_color=C_GREEN)
    tf_c4_h = add_textbox(s6, 6.88, r_top2 + 0.03, rw - 0.2, 0.32)
    p = tf_c4_h.paragraphs[0]
    p.text = "HARDWARE PROFILE CONTEXT & OPEN REPOSITORY DELIVERABLES"
    p.font.name = "Arial"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    tf_c4_b = add_textbox(s6, 6.88, r_top2 + 0.38, rw - 0.2, rh - 0.42)
    hw_refs = [
        ("Hardware Profile Alignment", "Trapped-ion aligned simulation profile (calibrated Raman gate dephasing, ion shuttling) and Rydberg/neutral-atom hardware-aware profile (Rydberg blockade, optical tweezers)."),
        ("Public Industry Landscape Awareness", "Informed by emerging neutral-atom platforms including public context from Egreen Quanta (https://www.egreenquanta.com/). Simulation profiles align with public architectural modalities; no proprietary hardware claims made."),
        ("TeleShield GitHub Repository", "Complete open-source framework, documentation, test suites & simulation engine: https://github.com/Vshal-Kumar/QDS_for_Photonic")
    ]
    for i, (authors, title_desc) in enumerate(hw_refs):
        p = tf_c4_b.paragraphs[0] if i == 0 else tf_c4_b.add_paragraph()
        p.space_after = Pt(2.5)
        r_a = p.add_run()
        r_a.text = f"• {authors}: "
        r_a.font.name = "Arial"
        r_a.font.size = Pt(8.5)
        r_a.font.bold = True
        r_a.font.color.rgb = C_GREEN
        r_td = p.add_run()
        r_td.text = title_desc
        r_td.font.name = "Arial"
        r_td.font.size = Pt(8)
        r_td.font.color.rgb = C_BODY

    # Bottom Synthesis Pipeline Flow
    add_card(s6, 0.6, 5.75, 12.13, 0.90, bg_color=C_ACCENT_BG, border_color=C_BLUE, border_width=1.2)
    tf_syn = add_textbox(s6, 0.7, 5.78, 11.9, 0.82)
    p = tf_syn.paragraphs[0]
    p.text = "END-TO-END THEORETICAL & APPLIED RESEARCH SYNTHESIS: "
    p.font.name = "Arial"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = C_DARK_BLUE

    syn_steps = [
        ("QDS THEORY", "Gottesman-Chuang"),
        ("TELEPORTATION", "Bennett et al."),
        ("MEASUREMENT", "Pauli X/Z/Y"),
        ("STATISTICS", "Hoeffding Bounds"),
        ("ATTACK MODELLING", "10 Threat Classes"),
        ("HARDWARE SIMULATION", "Ion-Trap / Rydberg"),
        ("TELESHIELD", "Deterministic Defense")
    ]
    for i, (stg, sub) in enumerate(syn_steps):
        r = p.add_run()
        r.text = f"[{stg}]"
        r.font.name = "Arial"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = C_BLUE if i < 4 else C_GREEN
        if i < len(syn_steps) - 1:
            r_arr = p.add_run()
            r_arr.text = " ➔ "
            r_arr.font.bold = True
            r_arr.font.color.rgb = C_MUTED
    print("  Slide 6 complete.")

    prs.save(output_path)
    print(f"\nPresentation saved to: {output_path}")
    prs.save("SIH2026-IDEA-Presentation-Format.pptx")
    print("Updated SIH2026-IDEA-Presentation-Format.pptx in place as well!")

if __name__ == '__main__':
    build_presentation()
