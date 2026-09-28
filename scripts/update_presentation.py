import sys
import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_presentation(template_path, output_path):
    prs = pptx.Presentation(template_path)
    print(f"Loaded template: {template_path}, slide count: {len(prs.slides)}")
    
    # 1. Ensure exactly 6 slides by dropping slide 7 (instruction slide) if present
    if len(prs.slides) > 6:
        while len(prs.slides) > 6:
            rId = prs.slides._sldIdLst[len(prs.slides)-1].rId
            prs.part.drop_rel(rId)
            del prs.slides._sldIdLst[len(prs.slides)-1]
        print(f"Trimmed to official 6-slide limit. Current slides: {len(prs.slides)}")

    # High-contrast, modern executive color palette
    COLOR_PRIMARY_NAVY = RGBColor(15, 32, 67)     # #0F2043 - Brand Deep Navy
    COLOR_ACCENT_BLUE  = RGBColor(0, 102, 204)    # #0066CC - Quantum Blue
    COLOR_CYAN_TECH    = RGBColor(14, 165, 233)   # #0EA5E9 - Electric Cyan
    COLOR_GREEN_SUCCESS= RGBColor(16, 185, 129)   # #10B981 - Pass / Valid
    COLOR_TEXT_DARK    = RGBColor(30, 41, 59)     # #1E293B - Slate Dark Body Text
    COLOR_TEXT_MUTED   = RGBColor(100, 116, 139)  # #64748B - Muted Subtitle Text
    COLOR_CARD_BG      = RGBColor(248, 250, 252)  # #F8FAFC - Clean Card Background
    COLOR_CARD_BORDER  = RGBColor(203, 213, 225)  # #CBD5E1 - Crisp Card Border
    COLOR_CARD_HEADER  = RGBColor(238, 242, 255)  # #EEF2FF - Soft Header Fill
    COLOR_WHITE        = RGBColor(255, 255, 255)

    def clean_slide_for_cards(slide):
        """Removes the old default TextBox 8 to replace with bespoke modern card containers."""
        to_remove = []
        for s in slide.shapes:
            if s.name == "TextBox 8" or s.shape_id in [15362, 17410]:
                to_remove.append(s)
            elif s.has_text_frame and s != slide.shapes.title and not s.name.startswith("Oval") and not "Placeholder" in s.name and s.name != "TextBox 9":
                to_remove.append(s)
        for s in to_remove:
            sp = s._element
            sp.getparent().remove(sp)

    def format_slide_header_and_chrome(slide, slide_num, title_text):
        # 1. Format Title
        if slide.shapes.title:
            t = slide.shapes.title
            t.left = Inches(2.05)
            t.top = Inches(0.18)
            t.width = Inches(8.1)
            t.height = Inches(0.85)
            t.text_frame.clear()
            p = t.text_frame.paragraphs[0]
            p.text = title_text
            p.alignment = PP_ALIGN.LEFT
            if len(p.runs) > 0:
                p.runs[0].font.name = "Calibri"
                p.runs[0].font.size = Pt(21)
                p.runs[0].font.bold = True
                p.runs[0].font.color.rgb = COLOR_PRIMARY_NAVY

        # 2. Format Oval (HexaCore badge) - adjusted width & margins for 1-line text
        for s in slide.shapes:
            if s.name.startswith("Oval"):
                s.left = Inches(0.35)
                s.top = Inches(0.2)
                s.width = Inches(1.58)
                s.height = Inches(0.75)
                s.fill.solid()
                s.fill.fore_color.rgb = COLOR_PRIMARY_NAVY
                s.line.color.rgb = COLOR_ACCENT_BLUE
                s.line.width = Pt(1.5)
                if s.has_text_frame:
                    s.text_frame.clear()
                    s.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
                    s.text_frame.margin_left = Inches(0.05)
                    s.text_frame.margin_right = Inches(0.05)
                    p = s.text_frame.paragraphs[0]
                    p.text = "HexaCore"
                    p.alignment = PP_ALIGN.CENTER
                    r = p.runs[0]
                    r.font.name = "Calibri"
                    r.font.size = Pt(12)
                    r.font.bold = True
                    r.font.color.rgb = COLOR_WHITE
            elif "Slide Number" in s.name or s.shape_id == 6:
                if s.has_text_frame:
                    s.text_frame.text = str(slide_num)
            elif "Footer" in s.name or s.shape_id == 7:
                if s.has_text_frame:
                    s.text_frame.text = "@SIH Idea submission"

    def create_card(slide, left, top, width, height, header_text, bullets, body_font_size=Pt(9.2)):
        """Creates a modern executive card container with header bar and styled bullet points."""
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.color.rgb = COLOR_CARD_BORDER
        card.line.width = Pt(1.2)
        
        # Text frame inside card
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.2)
        tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.10)
        tf.margin_bottom = Inches(0.10)
        tf.clear()

        # Header paragraph
        p_hdr = tf.paragraphs[0]
        p_hdr.space_after = Pt(3)
        r_hdr = p_hdr.add_run()
        r_hdr.text = header_text
        r_hdr.font.name = "Calibri"
        r_hdr.font.size = Pt(11.2)
        r_hdr.font.bold = True
        r_hdr.font.color.rgb = COLOR_PRIMARY_NAVY

        # Bullets
        for lead_in, body in bullets:
            p_b = tf.add_paragraph()
            p_b.space_before = Pt(1.5)
            p_b.space_after = Pt(1.5)
            
            # Bullet symbol
            r_sym = p_b.add_run()
            r_sym.text = "• "
            r_sym.font.name = "Calibri"
            r_sym.font.size = body_font_size
            r_sym.font.bold = True
            r_sym.font.color.rgb = COLOR_ACCENT_BLUE

            # Lead-in title
            r_lead = p_b.add_run()
            r_lead.text = lead_in + ": "
            r_lead.font.name = "Calibri"
            r_lead.font.size = body_font_size
            r_lead.font.bold = True
            r_lead.font.color.rgb = COLOR_PRIMARY_NAVY

            # Body text
            r_body = p_b.add_run()
            r_body.text = body
            r_body.font.name = "Calibri"
            r_body.font.size = body_font_size
            r_body.font.bold = False
            r_body.font.color.rgb = COLOR_TEXT_DARK

    # =========================================================================
    # SLIDE 1: SMART INDIA HACKATHON 2026 (TITLE PAGE)
    # =========================================================================
    slide1 = prs.slides[0]
    for s in slide1.shapes:
        if s.name == "TextBox 9" and s.has_text_frame:
            tf = s.text_frame
            tf.clear()
            tf.word_wrap = True
            
            entries = [
                ("Problem Statement ID : ", "26141 (PS-5)"),
                ("Problem Statement Title : ", "Quantum-Inspired Cyber Threat Detection for Digital Signature Security"),
                ("Organization / Owner : ", "Egreen Quanta LLP"),
                ("Theme : ", "Blockchain & Cybersecurity"),
                ("PS Category : ", "Software"),
                ("Team ID : ", "SIH2026-TEAM-HEXACORE"),
                ("Team Name : ", "HexaCore"),
                ("Solution Pitch : ", "Production-grade software framework for Teleportation-based Quantum Digital Signatures (QDS) over photonic optical fiber links, featuring a deterministic, non-AI 4-tier threat detection engine achieving 100% attack detection in < 30 ms.")
            ]
            
            for idx, (label, val) in enumerate(entries):
                p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
                p.space_after = Pt(6)
                
                r1 = p.add_run()
                r1.text = label
                r1.font.name = "Calibri"
                r1.font.size = Pt(13)
                r1.font.bold = True
                r1.font.color.rgb = COLOR_PRIMARY_NAVY
                
                r2 = p.add_run()
                r2.text = val
                r2.font.name = "Calibri"
                r2.font.size = Pt(12.5)
                r2.font.bold = (label.startswith("Problem Statement ID") or label.startswith("Team Name"))
                r2.font.color.rgb = COLOR_TEXT_DARK

    if not slide1.has_notes_slide:
        slide1.notes_slide
    slide1.notes_slide.notes_text_frame.text = (
        "Good morning, esteemed jury members and evaluators. We are Team HexaCore, "
        "and today we present our solution for Problem Statement ID 26141, titled 'Quantum-Inspired Cyber Threat Detection for "
        "Digital Signature Security', sponsored by Egreen Quanta LLP under the Blockchain & Cybersecurity theme.\n\n"
        "As quantum computing advances, Shor's algorithm renders traditional asymmetric cryptography like RSA and ECDSA obsolete, "
        "putting global banking, defense communications, and critical government infrastructure at immediate risk of 'Harvest Now, Decrypt Later' attacks. "
        "Our team has engineered a production-grade software simulation framework implementing teleportation-based Quantum Digital Signatures (QDS) "
        "over realistic photonic optical fiber links. What sets our solution apart is our strictly non-AI, deterministic 4-tier threat detection engine "
        "that detects forgery, impersonation, replay attacks, and quantum channel tampering in less than 30 milliseconds with mathematical certainty. "
        "Let us walk you through the architecture, innovation, and empirical validation of our solution."
    )

    # =========================================================================
    # SLIDE 2: IDEA TITLE (PROPOSED SOLUTION & INNOVATION)
    # =========================================================================
    slide2 = prs.slides[1]
    clean_slide_for_cards(slide2)
    format_slide_header_and_chrome(slide2, 2, "IDEA TITLE: Quantum-Inspired Threat Detection for QDS")

    card_width = Inches(12.3)
    c1_top = Inches(1.15)
    c1_height = Inches(1.6)
    c2_top = Inches(2.83)
    c2_height = Inches(1.6)
    c3_top = Inches(4.51)
    c3_height = Inches(1.6)

    create_card(
        slide2, Inches(0.5), c1_top, card_width, c1_height,
        "Proposed Solution: Teleportation-Based QDS Protocol Flow (Deliverables 1 & 3)",
        [
            ("Alice (Signer)", "Hashes message M via SHA-256 → maps digest to 6 non-orthogonal Pauli eigenstates {|0⟩, |1⟩, |+⟩, |–⟩, |+y⟩, |–y⟩} (K=16 qubits/block) → executes Bell-State Measurements (BSM) with shared EPR pairs |Φ+⟩ = (|00⟩+|11⟩)/√2 → transmits 2-bit classical feedforward (c1, c2)."),
            ("Photonic Optical Link", "Simulates realistic optical fiber channel at λ = 1550 nm with physical distance attenuation T(L) = 10^(-α·L/10) (α = 0.20 dB/km), depolarizing/dephasing noise, detector efficiency η = 0.85, and dark count probability pdark = 10^(-5) across 10–200 km."),
            ("Bob (Verifier)", "Reconstructs signature states via Pauli unitary correction U = Z^c1 · X^c2 → checks state fidelity F ≥ 85% → executes multi-basis projective measurements (X, Y, Z) → deterministic statistical threat engine renders ACCEPT / SUSPICIOUS / REJECT.")
        ]
    )

    create_card(
        slide2, Inches(0.5), c2_top, card_width, c2_height,
        "How It Addresses the Problem Statement (100% Threat Vector Coverage)",
        [
            ("Comprehensive Threat Defense", "Detects all 4 cyber threats mandated by Egreen Quanta LLP: (1) Quantum State Forgery, (2) Signer Impersonation, (3) Nonce Replay Attacks, and (4) Optical Channel Tampering (Pauli X, Y, Z eavesdropping)."),
            ("Hybrid Classical-Quantum Security", "Fuses classical cryptographic speed (HMAC-SHA256 & 128-bit timestamped nonce store for instant 0 ms rejection) with physical information-theoretic guarantees backed by the Quantum No-Cloning Theorem."),
            ("Empirically Verified Accuracy", "100% attack detection (PD = 1.0 for pa ≥ 20%), 0% false alarms on clean optical links up to 200 km, sub-30 ms verification latency, and 43/43 automated passing Pytest unit tests.")
        ]
    )

    create_card(
        slide2, Inches(0.5), c3_top, card_width, c3_height,
        "Innovation and Uniqueness of the Solution (Our Core Breakthroughs & USP)",
        [
            ("Strictly Non-AI/ML Determinism", "100% auditable statistical hypothesis tests (Total Variation Distance D_TV + Pearson's χ²) eliminate black-box neural network hallucination, adversarial evasion, and training biases—strictly honoring PS non-AI mandate."),
            ("Distance-Aware Adaptive Threshold τ(L, N)", "Dynamically calculates baseline noise τ = μ_D0(L) + z_(1-α)·(σ_D0(L)/√N) + Δ_detector; legitimate fiber attenuation is never falsely flagged as a cyber attack—our primary mathematical breakthrough."),
            ("Tri-State Decision Arbitrator", "Extends binary pass/fail into ACCEPT (clean link), SUSPICIOUS (degraded/investigate link), and REJECT (attack/forgery), providing critical defense-in-depth forensics for high-value optical backbones.")
        ]
    )

    slide2.notes_slide.notes_text_frame.text = (
        "Moving to Slide 2: Here we describe our proposed solution, how it directly solves Egreen Quanta's problem statement, "
        "and our core innovations. The fundamental challenge in digital signatures today is that classical public key cryptography "
        "relies on unproven computational complexity. In contrast, Quantum Digital Signatures leverage quantum mechanics for information-theoretic unforgeability.\n\n"
        "Our protocol begins with Alice, who hashes the message using SHA-256 and maps the digest to 16 non-orthogonal Pauli eigenstates. "
        "She shares maximally entangled Bell pairs with Bob and executes Bell-State Measurements, producing 32 classical feedforward bits. "
        "The photons propagate over a realistic optical fiber link modeled at standard telecom 1550 nm with 0.2 dB/km attenuation and detector noise. "
        "When Bob receives the states, he applies Pauli unitary corrections to reconstruct the signature.\n\n"
        "Notice our three key innovations: First, our threat detection engine is strictly non-AI and deterministic, using Total Variation Distance and "
        "Pearson's Chi-Square tests to ensure mathematical auditability without black-box AI risks. Second, our distance-aware adaptive threshold dynamically adjusts "
        "for fiber loss, guaranteeing that clean links up to 200 km are never falsely alarmed as attacks. And third, our tri-state decision engine provides "
        "actionable forensic visibility with an early-warning 'SUSPICIOUS' status before catastrophic failure."
    )

    # =========================================================================
    # SLIDE 3: TECHNICAL APPROACH (SPLIT-PANEL: TECH STACK & 4-TIER PIPELINE)
    # =========================================================================
    slide3 = prs.slides[2]
    clean_slide_for_cards(slide3)
    format_slide_header_and_chrome(slide3, 3, "TECHNICAL APPROACH & SYSTEM ARCHITECTURE")

    create_card(
        slide3, Inches(0.5), Inches(1.15), Inches(5.6), Inches(4.96),
        "Technologies to be Used (Deliverables 1, 3 & 5)",
        [
            ("Quantum Simulation Engine", "PennyLane v0.40+ utilizing the high-performance 'lightning.qubit' C++ state-vector backend (3-qubit Bell teleportation circuits, parametric Pauli gates, multi-basis projective QNodes)."),
            ("Photonic Optical Channel Physics", "NumPy & SciPy physical fiber model: attenuation T(L) = 10^(-α·L/10) (α = 0.20 dB/km), depolarizing & dephasing noise superoperators, single-photon detector efficiency η = 0.85, and dark count Poissonian noise."),
            ("Classical Cryptography & Security", "Python hashlib & hmac: SHA-256 message hashing, HMAC-SHA256 signer authentication, 128-bit timestamped Nonce Store, and Verifier Access Control Lists (ACL)."),
            ("Testing, Interfaces & Verification", "Pytest (43/43 automated green tests), 11 scientific benchmark experiment suites, Matplotlib publication plotting engine, CLI harness, and interactive FastHTML / Web UI demonstration dashboard.")
        ],
        body_font_size=Pt(9.0)
    )

    create_card(
        slide3, Inches(6.3), Inches(1.15), Inches(6.5), Inches(4.96),
        "Methodology & Implementation Process (Deliverables 2, 4 & 6)",
        [
            ("Step 1 — Signer Flow (Alice)", "Computes H(M) = SHA-256(M) → encodes into 6 Pauli eigenstates → executes BSM on (S, A) with pre-shared EPR pairs |Φ+⟩ → generates 32 classical feedforward bits (c1, c2) → signs packet with HMAC-SHA256 and fresh 128-bit nonce."),
            ("Step 2 — Channel & Attack Simulation", "Simulates transmission through fiber (10–200 km); controlled attack module injects calibrated Pauli X (bit-flip), Pauli Z (phase-flip), Pauli Y (bit-phase flip), state forgery, replay, and impersonation threats."),
            ("Step 3 — Bob's 4-Tier Verification Pipeline", "• Tier 1 (Classical Auth, <1 ms): Validates HMAC tag, Nonce freshness & ACL → immediate drop on forgery.\n• Tier 2 (Quantum Fidelity, ~5 ms): Applies U = Z^c1 · X^c2; validates state fidelity F ≥ 85% (mismatch ≤ 15%).\n• Tier 3 (Threat Engine, ~15 ms): N=1,000–10,000 multi-basis shots; computes TVD D_TV & χ² vs adaptive threshold τ(L,N).\n• Tier 4 (Tri-State Decision, <1 ms): Emits auditable ACCEPT, SUSPICIOUS, or REJECT verdict."),
            ("Performance KPIs & Working Prototype", "< 30 ms end-to-end verification latency | 100% attack detection for pa ≥ 20% | 0% false alarm rate on clean fiber | 43/43 green unit tests.")
        ],
        body_font_size=Pt(8.8)
    )

    slide3.notes_slide.notes_text_frame.text = (
        "On Slide 3, we detail our technical approach, technology stack, and 4-tier client verification methodology. "
        "Our software framework is built on industry-standard, high-performance open-source tools: PennyLane with the Lightning C++ backend "
        "simulates the 3-qubit teleportation circuits with sub-millisecond execution times. NumPy and SciPy drive our physical optical channel, "
        "accurately modeling fiber attenuation at 0.2 dB per kilometer, quantum depolarizing and dephasing noise, detector efficiency, and dark counts.\n\n"
        "Bob's client verification pipeline uses a disciplined 4-tier defense architecture: "
        "In Tier 1, classical HMAC and freshness nonce checks eliminate brute-force and replay attacks in less than 1 millisecond, "
        "ensuring we never waste quantum measurement resources on invalid requests. "
        "In Tier 2, Bob applies the unitary correction U = Z^c1 · X^c2 and checks quantum state fidelity against an 85% overlap threshold. "
        "In Tier 3, our deterministic statistical threat engine samples photons across the X, Y, and Z bases, computing Total Variation Distance "
        "and Chi-Square statistics against the pre-calibrated baseline. "
        "Finally, Tier 4 renders a tri-state decision. The entire end-to-end cycle executes in under 30 milliseconds on standard classical CPUs."
    )

    # =========================================================================
    # SLIDE 4: FEASIBILITY AND VIABILITY
    # =========================================================================
    slide4 = prs.slides[3]
    clean_slide_for_cards(slide4)
    format_slide_header_and_chrome(slide4, 4, "FEASIBILITY AND VIABILITY")

    create_card(
        slide4, Inches(0.5), c1_top, card_width, c1_height,
        "Analysis of the Feasibility of the Idea",
        [
            ("Immediate Classical Hardware Execution", "Runs completely on classical COTS hardware (laptops, cloud VMs, edge servers) today using pure Python 3.10+, NumPy, SciPy, and PennyLane—zero specialized quantum computing hardware required to simulate and test."),
            ("Production-Grade Software Readiness", "Fully implemented modular architecture (core/, quantum/, photonic/, qds/, security/, attacks/, detection/, web/) validated by 43/43 green automated Pytest unit tests and 11 benchmark experiment suites."),
            ("Explainable Mathematical Proofs", "Non-AI deterministic statistical formulations (Total Variation Distance, Pearson's χ²) provide transparent mathematical proofs, ensuring complete auditability for defense, banking, and regulatory compliance.")
        ]
    )

    create_card(
        slide4, Inches(0.5), c2_top, card_width, c2_height,
        "Potential Challenges and Risks",
        [
            ("Physical Fiber Loss & Channel Decoherence", "Over long-distance fiber (L > 100 km), exponential optical attenuation (0.20 dB/km) and phase noise reduce received photon counts and signal-to-noise ratio (SNR)."),
            ("Single-Photon Detector Impairments", "Detector dark counts (~10^(-5)), timing jitter (~50 ps), and alignment drift introduce background noise that can distort empirical measurement distributions."),
            ("Adversarial Stealth Eavesdropping", "Sophisticated low-strength quantum attacks (pa < 15%) designed to blend into legitimate optical attenuation noise margins."),
            ("Quantum Hardware Deployment Gap", "Physical long-haul quantum repeater infrastructure is currently emerging rather than ubiquitously deployed across commercial networks.")
        ]
    )

    create_card(
        slide4, Inches(0.5), c3_top, card_width, c3_height,
        "Strategies for Overcoming Challenges & Deployment Roadmap",
        [
            ("Distance-Aware Adaptive Thresholding", "Calibrated baseline P0,L pre-incorporates distance attenuation and dark counts; adaptive threshold τ(L,N) dynamically eliminates false alarms up to 200 km."),
            ("Two-Tier Fast Classical Filtering", "Tier 1 classical filters drop 100% of brute-force, replay, and unauthorized requests in < 1 ms before allocating quantum measurement budgets."),
            ("3-Phase Deployment Roadmap", "Phase 1 (Now): Validated simulator (43/43 tests, 11 benchmarks, web demo) → Phase 2 (6-12 mo): Pilot on NQM Quantum Comm. T-Hub optical testbeds → Phase 3 (12-24 mo): HSM hardware modules for national quantum backbones.")
        ]
    )

    slide4.notes_slide.notes_text_frame.text = (
        "Turning to Slide 4: Feasibility, Viability, and Risk Mitigation. "
        "A critical strength of our solution is that it is 100% operational on standard classical hardware today. "
        "Evaluators and security teams do not need a multimillion-dollar quantum computer to validate our framework; "
        "our PennyLane Lightning backend simulates complete quantum signing and verification cycles on standard laptops in under 30 ms.\n\n"
        "We have conducted a thorough risk analysis identifying four key technical challenges: "
        "First, physical fiber loss over 100 km reduces photon throughput; "
        "second, single-photon detector dark counts and timing jitter introduce background noise; "
        "third, stealthy adversaries might attempt low-strength tampering hidden inside channel loss; "
        "and fourth, physical quantum hardware is still rolling out.\n\n"
        "We overcome these challenges directly: our distance-aware adaptive threshold dynamically compensates for fiber attenuation, "
        "preventing false alarms even over 200 km links. Our Tier 1 classical firewall eliminates 100% of replay and brute-force attacks in less than 1 ms. "
        "Finally, our phased roadmap moves from today's validated software simulator to physical testbed validation under India's National Quantum Mission, "
        "and ultimately into Hardware Security Modules protecting critical infrastructure."
    )

    # =========================================================================
    # SLIDE 5: IMPACT AND BENEFITS
    # =========================================================================
    slide5 = prs.slides[4]
    clean_slide_for_cards(slide5)
    format_slide_header_and_chrome(slide5, 5, "IMPACT AND BENEFITS")

    create_card(
        slide5, Inches(0.5), c1_top, card_width, c1_height,
        "Potential Impact on the Target Audience",
        [
            ("Defense & Strategic Communications", "Protects high-assurance military command channels, diplomatic cables, and state registries against retroactive 'Harvest Now, Decrypt Later' quantum attacks."),
            ("Banking & Financial Sector", "Future-proofs multi-trillion-rupee interbank payment rails (RTGS/NEFT/SWIFT), fintech ledgers, and digital currencies against quantum signature forgery."),
            ("Quantum Communication Ecosystem", "Provides a validated, turnkey software simulation testbed for researchers and telecommunications operators across India's quantum ecosystem.")
        ]
    )

    create_card(
        slide5, Inches(0.5), c2_top, card_width, c2_height,
        "Multi-Dimensional Benefits of the Solution",
        [
            ("Information-Theoretic Security", "Unconditional physical unforgeability guaranteed by the Quantum No-Cloning Theorem; 100% detection (PD = 1.0) of eavesdropping attacks ≥ 20% strength; 100% rejection (30/30) of replay, impersonation, and rogue verifiers."),
            ("Economic & Commercial Value", "Built entirely with open-source technologies, eliminating expensive proprietary quantum software licensing; prevents catastrophic multi-billion-dollar losses from future cryptographic breaks."),
            ("Social & Regulatory Auditability", "100% deterministic mathematical verification provides fully transparent audit trails admissible in legal proceedings, avoiding non-deterministic AI liability."),
            ("Environmental & Computational Efficiency", "Lightweight C++ state-vector simulation achieves < 30 ms execution on low-power CPUs without high-power GPU clusters or cryogenic hardware.")
        ]
    )

    create_card(
        slide5, Inches(0.5), c3_top, card_width, c3_height,
        "100% Deliverables Compliance Matrix (Egreen Quanta LLP — PS 26141)",
        [
            ("Deliverables 1 & 2 (Complete)", "Formal Mathematical Model of teleportation-based QDS + Deterministic Quantum-Inspired Threat Detection Framework (quantum/, detection/)."),
            ("Deliverables 3 & 4 (Complete)", "Signature Generation & Verification Module with Pauli corrections + Controlled Cyber Attack Simulation Module for 4 threat vectors (qds/, attacks/)."),
            ("Deliverables 5 & 6 (Complete)", "End-to-end Software Framework Prototype: Interactive Web UI Dashboard, CLI Interface, 11 Benchmark Suites, and 43/43 Green Pytest Tests (web/, main.py).")
        ]
    )

    slide5.notes_slide.notes_text_frame.text = (
        "On Slide 5, we highlight the real-world impact, multi-dimensional benefits, and deliverables compliance of our project. "
        "Our primary beneficiaries are defense networks and banking systems that handle high-value, long-lifespan data. "
        "Adversaries today are actively intercepting and storing encrypted traffic to decrypt once quantum hardware arrives. "
        "Our QDS framework guarantees information-theoretic unforgeability rooted in the fundamental laws of physics.\n\n"
        "From an economic and social standpoint: By using open-source Python, PennyLane, and NumPy, we eliminate expensive proprietary licenses "
        "while providing a transparent, mathematically explainable verification pipeline that meets strict legal and regulatory compliance standards.\n\n"
        "Most importantly, please review our official Deliverables Compliance Matrix: "
        "We have achieved 100% completion across all 6 deliverables mandated by Egreen Quanta LLP for Problem Statement 26141. "
        "From the formal mathematical teleportation model and deterministic threat detection engine to the full signing/verification modules, "
        "attack simulation scenarios, and interactive web demonstration dashboard, our solution is fully implemented, empirically tested, and ready for deployment."
    )

    # =========================================================================
    # SLIDE 6: RESEARCH AND REFERENCES
    # =========================================================================
    slide6 = prs.slides[5]
    clean_slide_for_cards(slide6)
    format_slide_header_and_chrome(slide6, 6, "RESEARCH AND REFERENCES")

    # Card 1 on Slide 6 has 4 items -> height 1.72 in
    create_card(
        slide6, Inches(0.5), Inches(1.15), card_width, Inches(1.72),
        "Peer-Reviewed Scientific Foundations",
        [
            ("Experimental Photonic QDS", "Clarke et al., 'Experimental demonstration of quantum digital signatures using phase-encoded coherent states of light,' Nature Communications 3, 1174 (2012) — Establishes the physical feasibility of discrete-variable optical QDS."),
            ("Memoryless Quantum Signatures", "Dunjko, Wallden, & Andersson, 'Quantum digital signatures without quantum memory,' Physical Review Letters 112, 040502 (2014) — Informs our practical receiver architecture operating without complex quantum memory."),
            ("Teleportation-Based QDS", "Lu et al., 'Teleportation-based continuous-variable quantum digital signature,' Optics Express / ScienceDirect (2021) — Provides foundational quantum teleportation protocols for unforgeable digital signatures."),
            ("Conjugate Coding Foundation", "Bennett & Brassard, 'Quantum cryptography: Public key distribution and coin tossing,' Theoretical Computer Science (1984) — Formulates multi-basis projective measurement principles.")
        ],
        body_font_size=Pt(8.7)
    )

    # Card 2 on Slide 6 -> height 1.50 in
    create_card(
        slide6, Inches(0.5), Inches(2.95), card_width, Inches(1.50),
        "National Standards & Strategic Policy Frameworks",
        [
            ("National Quantum Mission (NQM)", "PIB / Department of Science & Technology (DST), Govt. of India — ₹6,003.65 Cr National Quantum Mission (2023–2031) establishing Quantum Communication T-Hubs and inter-city quantum networks."),
            ("NIST Post-Quantum Standards (2024)", "NIST FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA) — Mandates the urgent global migration to quantum-resistant signature architectures."),
            ("ITU-T Quantum Recommendations", "ITU-T Y.3800 series — Overview on networks supporting quantum key distribution and quantum digital signature communications.")
        ],
        body_font_size=Pt(9.0)
    )

    # Card 3 on Slide 6 -> height 1.50 in
    create_card(
        slide6, Inches(0.5), Inches(4.53), card_width, Inches(1.50),
        "Internal Empirical Validation & Open-Source Artifacts",
        [
            ("Comprehensive Test Coverage", "43/43 passing automated unit & integration tests covering Pauli algebra, Bell states, BSM teleportation fidelity (F = 1.000000), optical channel loss, and 4-tier security defense (pytest tests/ -v)."),
            ("11 Scientific Benchmark Suites", "11 publication-grade empirical suites generating high-resolution plots (results/figures/) and scientific CSV datasets (results/tables/) across distance, attack strength, and shot count scaling."),
            ("Interactive Web & CLI Prototype", "Working interactive browser dashboard (FastHTML/CSS/JS at http://localhost:8000 via python main.py --demo) and authoritative Technical PDF Report (Photonic_QDS_Security_Simulator_Technical_Report.pdf).")
        ],
        body_font_size=Pt(9.0)
    )

    slide6.notes_slide.notes_text_frame.text = (
        "Finally, on Slide 6, we substantiate our work with rigorous scientific research, national standards, and internal empirical validation. "
        "Our protocol is anchored in peer-reviewed literature published in Nature Communications, Physical Review Letters, and Optics Express, "
        "drawing specifically on Clarke et al.'s optical QDS demonstrations and Dunjko et al.'s memoryless receiver architectures.\n\n"
        "Strategically, our project directly aligns with India's ₹6,003.65 Crore National Quantum Mission led by the Department of Science & Technology, "
        "supporting the Quantum Communication T-Hub initiative, as well as the newly released 2024 NIST Post-Quantum Cryptography standards.\n\n"
        "Unlike conceptual proposals, our solution is backed by robust engineering evidence: "
        "43 out of 43 automated Pytest test suites passing at 100%, 11 empirical benchmark experiment suites producing publication figures and CSV tables, "
        "an interactive web demonstration dashboard, and a comprehensive 5-page technical report PDF. "
        "Thank you for your time, and we look forward to answering your questions and demonstrating our live simulation!"
    )

    prs.save(output_path)
    print(f"✓ Successfully generated updated presentation: {output_path} (Total Slides: {len(prs.slides)})")

if __name__ == "__main__":
    template = "SIH2026-IDEA-Presentation-Format.pptx"
    output = "new.pptx"
    build_presentation(template, output)
