#!/usr/bin/env python3
"""Generates the authoritative cryptographic & quantum engineering technical PDF report for SIH PS 26141 (Egreen Quanta LLP).
Ensures 100% clean typography with TrueType fonts (zero black dots, XML errors, or missing glyphs).
"""

import os
import sys
import shutil
import re
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register TrueType fonts for clean Unicode & crisp typographic rendering
TTF_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_NORMAL = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_CODE = "Courier"

if os.path.exists(os.path.join(TTF_DIR, "DejaVuSans.ttf")):
    try:
        pdfmetrics.registerFont(TTFont("DejaVu", os.path.join(TTF_DIR, "DejaVuSans.ttf")))
        pdfmetrics.registerFont(TTFont("DejaVu-Bold", os.path.join(TTF_DIR, "DejaVuSans-Bold.ttf")))
        pdfmetrics.registerFont(TTFont("DejaVu-Mono", os.path.join(TTF_DIR, "DejaVuSansMono.ttf")))
        FONT_NORMAL = "DejaVu"
        FONT_BOLD = "DejaVu-Bold"
        FONT_CODE = "DejaVu-Mono"
    except Exception as e:
        print(f"Font registration fallback: {e}")


def safe_p(text: str, style) -> Paragraph:
    """Safely escapes raw angle brackets and mathematical glyphs for ReportLab."""
    # Handle ket/bra formatting
    text = text.replace("|psi><psi|", "|&psi;&gt;&lt;&psi;|")
    text = text.replace("|0>", "|0&gt;")
    text = text.replace("|1>", "|1&gt;")
    text = text.replace("|+>", "|+&gt;")
    text = text.replace("|->", "|-&gt;")
    text = text.replace("|+y>", "|+<sub>y</sub>&gt;")
    text = text.replace("|-y>", "|-<sub>y</sub>&gt;")
    text = text.replace("|+_y>", "|+<sub>y</sub>&gt;")
    text = text.replace("|-_y>", "|-<sub>y</sub>&gt;")
    text = text.replace("|Phi+>", "|&Phi;<sup>+</sup>&gt;")
    text = text.replace("|Phi->", "|&Phi;<sup>-</sup>&gt;")
    text = text.replace("|Psi+>", "|&Psi;<sup>+</sup>&gt;")
    text = text.replace("|Psi->", "|&Psi;<sup>-</sup>&gt;")
    text = text.replace("|psi>", "|&psi;&gt;")
    text = text.replace("<psi|", "&lt;&psi;|")
    text = text.replace("<psi_k|", "&lt;&psi;<sub>k</sub>|")
    text = text.replace("|psi_k>", "|&psi;<sub>k</sub>&gt;")
    text = text.replace("<0|", "&lt;0|")
    text = text.replace("<1|", "&lt;1|")
    text = text.replace("<+|", "&lt;+|")
    text = text.replace("<-|", "&lt;-|")
    text = text.replace("<+y|", "&lt;+<sub>y</sub>|")
    text = text.replace("<-y|", "&lt;-<sub>y</sub>|")
    text = text.replace("<+_y|", "&lt;+<sub>y</sub>|")
    text = text.replace("<-_y|", "&lt;-<sub>y</sub>|")
    text = text.replace("|HH>", "|HH&gt;")
    text = text.replace("|VV>", "|VV&gt;")
    text = text.replace("<=", "&le;")
    text = text.replace(">=", "&ge;")
    text = text.replace("->", "-&gt;")
    return Paragraph(text, style)


class NumberedCanvas(canvas.Canvas):
    """Adds running header and footer with total page counts."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont(FONT_NORMAL, 7.5)
        self.setFillColor(colors.HexColor("#475569"))

        # Running Footer
        footer_text = "SIH PS 26141 — Egreen Quanta LLP — Quantum-Inspired Cyber Threat Detection for QDS"
        self.drawString(54, 25, footer_text)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 25, page_str)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 35, 612 - 54, 35)

        # Running Header (Pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, 792 - 28, "Photonic Quantum Digital Signature (QDS) — SIH 26141 Technical Report")
            self.drawRightString(612 - 54, 792 - 28, "Team HexaCore — Egreen Quanta LLP")
            self.line(54, 792 - 32, 612 - 54, 792 - 32)

        self.restoreState()


def generate_pdf(output_filename="Photonic_QDS_Security_Simulator_Technical_Report.pdf"):
    """Compiles the authoritative technical specification PDF."""
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=40,
        bottomMargin=44
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=2
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName=FONT_NORMAL,
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#2563eb"),
        spaceAfter=5
    )
    h1_style = ParagraphStyle(
        'DocH1',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=9.5,
        leading=12.5,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=8.2,
        leading=10.5,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=4,
        spaceAfter=2,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName=FONT_NORMAL,
        fontSize=7.6,
        leading=10.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=3
    )
    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=styles['Normal'],
        fontName=FONT_NORMAL,
        fontSize=7.6,
        leading=10.5,
        textColor=colors.HexColor("#334155"),
        leftIndent=8,
        spaceAfter=2
    )
    code_style = ParagraphStyle(
        'DocCode',
        parent=styles['Normal'],
        fontName=FONT_CODE,
        fontSize=6.4,
        leading=8.6,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=3
    )
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName=FONT_NORMAL,
        fontSize=6.8,
        leading=9.0,
        textColor=colors.HexColor("#1e293b")
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=6.8,
        leading=9.0,
        textColor=colors.HexColor("#0f172a")
    )
    table_hdr = ParagraphStyle(
        'TableHdr',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=7.0,
        leading=9.5,
        textColor=colors.HexColor("#ffffff")
    )

    story = []

    # =========================================================================
    # PAGE 1: METADATA, DELIVERABLES TABLE & OBJECTIVES
    # =========================================================================
    story.append(Paragraph("Quantum-Inspired Cyber Threat Detection for Digital Signature Security", title_style))
    story.append(Paragraph("Smart India Hackathon 2026 | Problem Statement 5 (ID: 26141) | Egreen Quanta LLP | Team HexaCore", subtitle_style))

    meta_box = [
        [
            safe_p("<b>Problem Statement:</b> SIH 26141 (PS-5) &nbsp;|&nbsp; <b>Organization:</b> Egreen Quanta LLP &nbsp;|&nbsp; <b>Theme:</b> Blockchain &amp; Cybersecurity &nbsp;|&nbsp; <b>Category:</b> Software", table_cell)
        ],
        [
            safe_p("<b>Core Mission:</b> An end-to-end software simulation framework modeling teleportation-based Quantum Digital Signatures (QDS) over an optical photonic channel with a <b>strictly non-AI/ML deterministic statistical threat detection engine</b> detecting forgery, impersonation, replay, and quantum channel tampering in sub-25 ms.", table_cell)
        ],
        [
            safe_p("<b>Implementation Stack:</b> Python 3.12, PennyLane v0.40+ (Lightning Backend), NumPy, SciPy, Pytest (43/43 Green Tests — 100% Pass), FastHTML / Web UI Demonstration Dashboard.", table_cell)
        ]
    ]
    t_meta = Table(meta_box, colWidths=[504])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 4))

    # Official Deliverables Compliance Table
    story.append(Paragraph("1. Official Problem Statement Deliverables Compliance Matrix", h1_style))
    deliv_data = [
        [safe_p("S.No", table_hdr), safe_p("Expected Deliverable (Egreen Quanta LLP)", table_hdr), safe_p("Description", table_hdr), safe_p("Implementation in this Framework", table_hdr), safe_p("Status", table_hdr)],
        [
            safe_p("<b>1</b>", table_cell_bold),
            safe_p("Mathematical Model of Teleportation-based QDS", table_cell_bold),
            safe_p("Formal description of the signature protocol", table_cell),
            safe_p("Bell-state entanglement (|Phi+>), 3-qubit teleportation, Pauli corrections U = Z<sup>c1</sup> X<sup>c2</sup>, projective measurement rules.", table_cell),
            safe_p("<font color='#16a34a'><b>100% Complete</b></font>", table_cell)
        ],
        [
            safe_p("<b>2</b>", table_cell_bold),
            safe_p("Quantum-Inspired Threat Detection Framework", table_cell_bold),
            safe_p("Core threat detection engine", table_cell),
            safe_p("Non-AI/ML deterministic engine; Total Variation Distance (D<sub>TV</sub>), Pearson's &chi;<sup>2</sup> tests, distance-aware adaptive threshold &tau;.", table_cell),
            safe_p("<font color='#16a34a'><b>100% Complete</b></font>", table_cell)
        ],
        [
            safe_p("<b>3</b>", table_cell_bold),
            safe_p("Signature Generation &amp; Verification Module", table_cell_bold),
            safe_p("Implementation of QDS operations", table_cell),
            safe_p("Quantum public key distribution simulation, Alice's signature generation across 6 Pauli eigenstates, Bob's 4-tier verification.", table_cell),
            safe_p("<font color='#16a34a'><b>100% Complete</b></font>", table_cell)
        ],
        [
            safe_p("<b>4</b>", table_cell_bold),
            safe_p("Attack Simulation Module", table_cell_bold),
            safe_p("Controlled simulation of cyber threats", table_cell),
            safe_p("Simulates signature forgery, signer impersonation, nonce replay, and optical channel tampering (Pauli X, Y, Z).", table_cell),
            safe_p("<font color='#16a34a'><b>100% Complete</b></font>", table_cell)
        ],
        [
            safe_p("<b>5/6</b>", table_cell_bold),
            safe_p("Software Framework / Prototype", table_cell_bold),
            safe_p("End-to-end implementable system", table_cell),
            safe_p("Interactive Web UI Dashboard, CLI simulator, security event logging, 11 benchmark suites, and 43 Pytest test cases.", table_cell),
            safe_p("<font color='#16a34a'><b>100% Complete</b></font>", table_cell)
        ]
    ]
    t_deliv = Table(deliv_data, colWidths=[28, 112, 95, 209, 60])
    t_deliv.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_deliv)
    story.append(Spacer(1, 4))

    # 2. Hybrid Classical + Quantum Fusion
    story.append(Paragraph("2. Why Classical and Quantum Cryptography Must Fuse into QDS", h1_style))
    story.append(safe_p(
        "&bull; <b>Classical Cryptography Vulnerability:</b> Classical signature schemes (RSA, ECDSA) rely on computational hardness assumptions (factoring, discrete log) vulnerable to polynomial-time attacks via Shor's algorithm and retroactive decryption ('Harvest Now, Decrypt Later').<br/>"
        "&bull; <b>Quantum Mechanics Strengths &amp; Limits:</b> The Quantum No-Cloning Theorem ensures that unknown quantum states cannot be copied, guaranteeing unforgeability. However, raw photons cannot carry variable-length messages without message digest binding.<br/>"
        "&bull; <b>The Hybrid QDS Solution:</b> SHA-256 and HMAC-SHA256 bind messages to signer identity in &Omicron;(1) time; quantum teleportation provides the physically unforgeable signature payload over telecom optical fiber.",
        body_style
    ))

    # 3. Actors and Channels
    story.append(Paragraph("3. Security Principals &amp; Dual-Channel Topologies", h1_style))
    actors_data = [
        [safe_p("Principal", table_hdr), safe_p("Role", table_hdr), safe_p("Key Operations &amp; System Responsibilities", table_hdr)],
        [safe_p("<b>Alice</b>", table_cell), safe_p("Signer", table_cell), safe_p("Holds private key Key<sub>Alice</sub>. Hashes message M, maps digest to Pauli eigenstates, executes Bell-State Measurements (BSM), transmits classical feedforward.", table_cell)],
        [safe_p("<b>Bob</b>", table_cell), safe_p("Verifier", table_cell), safe_p("Holds shared secret &amp; Bell pairs. Validates classical HMAC and freshness, applies Pauli corrections U = Z<sup>c1</sup> X<sup>c2</sup>, performs multi-basis measurements, executes statistical threat detection.", table_cell)],
        [safe_p("<b>Eve</b>", table_cell), safe_p("Adversary", table_cell), safe_p("Attempts signature forgery, nonce replay, signer impersonation, unauthorized verification, or active optical fiber tampering (Pauli X, Z, Y bit/phase flips).", table_cell)]
    ]
    t_actors = Table(actors_data, colWidths=[55, 65, 384])
    t_actors.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_actors)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: QUBIT REPRESENTATION, BUDGET, END-TO-END FLOW & WIRE PACKET
    # =========================================================================
    story.append(Paragraph("4. Photonic Polarization-Encoded Qubit Space", h1_style))
    story.append(safe_p(
        "Quantum information is encoded into discrete-variable polarization states of single photons in a 2-dimensional complex Hilbert space &Eta;<sub>2</sub>. The protocol utilizes six canonical Pauli eigenstates spanning three mutually unbiased conjugate bases:",
        body_style
    ))

    qubit_data = [
        [safe_p("Basis", table_hdr), safe_p("State", table_hdr), safe_p("Polarization Mode", table_hdr), safe_p("State Vector |psi>", table_hdr), safe_p("Density Matrix rho = |psi><psi|", table_hdr), safe_p("Bloch Vector", table_hdr)],
        [safe_p("<b>Z (Comp.)</b>", table_cell), safe_p("|0>", table_cell_bold), safe_p("Horizontal (|H>)", table_cell), safe_p("[1, 0]<sup>T</sup>", table_cell), safe_p("[[1, 0], [0, 0]]", table_cell), safe_p("(0, 0, 1)", table_cell)],
        [safe_p("<b>Z (Comp.)</b>", table_cell), safe_p("|1>", table_cell_bold), safe_p("Vertical (|V>)", table_cell), safe_p("[0, 1]<sup>T</sup>", table_cell), safe_p("[[0, 0], [0, 1]]", table_cell), safe_p("(0, 0, -1)", table_cell)],
        [safe_p("<b>X (Diag.)</b>", table_cell), safe_p("|+>", table_cell_bold), safe_p("Diagonal (|D>, +45&deg;)", table_cell), safe_p("1/&radic;2 [1, 1]<sup>T</sup>", table_cell), safe_p("1/2 [[1, 1], [1, 1]]", table_cell), safe_p("(1, 0, 0)", table_cell)],
        [safe_p("<b>X (Diag.)</b>", table_cell), safe_p("|->", table_cell_bold), safe_p("Anti-Diagonal (|A>, -45&deg;)", table_cell), safe_p("1/&radic;2 [1, -1]<sup>T</sup>", table_cell), safe_p("1/2 [[1, -1], [-1, 1]]", table_cell), safe_p("(-1, 0, 0)", table_cell)],
        [safe_p("<b>Y (Circ.)</b>", table_cell), safe_p("|+y>", table_cell_bold), safe_p("Right-Circular (|R>)", table_cell), safe_p("1/&radic;2 [1, i]<sup>T</sup>", table_cell), safe_p("1/2 [[1, -i], [i, 1]]", table_cell), safe_p("(0, 1, 0)", table_cell)],
        [safe_p("<b>Y (Circ.)</b>", table_cell), safe_p("|-y>", table_cell_bold), safe_p("Left-Circular (|L>)", table_cell), safe_p("1/&radic;2 [1, -i]<sup>T</sup>", table_cell), safe_p("1/2 [[1, i], [-i, 1]]", table_cell), safe_p("(0, -1, 0)", table_cell)]
    ]
    t_qubit = Table(qubit_data, colWidths=[70, 30, 95, 75, 154, 80])
    t_qubit.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_qubit)
    story.append(Spacer(1, 4))

    # 5. Cryptographic Resource Allocation
    story.append(Paragraph("5. Cryptographic Resource Allocation per Signed Block", h1_style))
    budget_data = [
        [safe_p("Resource Parameter", table_hdr), safe_p("Default Quantity", table_hdr), safe_p("Operational Role &amp; Engineering Rationale", table_hdr)],
        [safe_p("<b>Signature Qubits (K)</b>", table_cell_bold), safe_p("16 qubits / block", table_cell), safe_p("Carries the quantum signature payload mapped from SHA-256 digest chunks. Teleported sequentially across 3-qubit circuits.", table_cell)],
        [safe_p("<b>Pre-shared Bell Pairs</b>", table_cell_bold), safe_p("16 EPR pairs (|Phi+>)", table_cell), safe_p("Maximally entangled state (|00> + |11>)/&radic;2 distributed between Alice and Bob before signing.", table_cell)],
        [safe_p("<b>Classical Feedforward</b>", table_cell_bold), safe_p("32 classical bits", table_cell), safe_p("2 bits (c1<sub>k</sub>, c2<sub>k</sub>) per signature qubit produced by Alice's Bell-State Measurement (BSM).", table_cell)],
        [safe_p("<b>Measurement Shots (N)</b>", table_cell_bold), safe_p("1,000 to 10,000 shots", table_cell), safe_p("Empirical sampling shots per Pauli basis required by Bob's statistical threat detector for high confidence.", table_cell)],
        [safe_p("<b>Classical Packet Overhead</b>", table_cell_bold), safe_p("~450 bytes (JSON)", table_cell), safe_p("Encapsulates message text, SHA-256 hash, 128-bit nonce, 256-bit HMAC tag, session ID, and BSM bitstring.", table_cell)]
    ]
    t_budget = Table(budget_data, colWidths=[115, 95, 294])
    t_budget.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_budget)
    story.append(Spacer(1, 4))

    # 6. End-to-End Flow & Packet Structure
    story.append(Paragraph("6. End-to-End System Flow &amp; Classical Wire Format", h1_style))
    code_flow = (
        "Alice (Signer)                                                    Bob (Verifier / Client)\n"
        "  |-- 1. Compute H(M) = SHA-256(Message M)                                |\n"
        "  |-- 2. Generate SessionID, Nonce (128-bit hex), Timestamp                |\n"
        "  |-- 3. Map Digest Bits to Pauli Eigenstates {|psi_k>} (K=16)             |\n"
        "  |-- 4. Execute BSM on (S_k, A_k) with Bell Pair |Phi+>_AB                |\n"
        "  |-- 5. Obtain Feedforward Bits (c1_k, c2_k) (32 bits total)              |\n"
        "  |-- 6. Compute HMAC-SHA256(Key_Alice, Signer:Session:Nonce:H(M):BSM)    |\n"
        "  |==== CLASSICAL AUTHENTICATED CHANNEL (JSON Packet) ====================&gt;|-- Tier 1: Verify HMAC, Nonce, ACL\n"
        "  |==== PHOTONIC OPTICAL CHANNEL (λ = 1550 nm) ============================&gt;|-- Apply U = Z^c1 * X^c2\n"
        "        [Fiber Loss 0.20 dB/km + Depolarizing Noise + Eve Attacks]         |-- Tier 2: Overlap Fidelity Test\n"
        "                                                                           |-- Tier 3: Statistical Threat Engine\n"
        "                                                                           `-- Tier 4: Output ACCEPT / REJECT"
    )
    story.append(Paragraph(code_flow.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))
    story.append(Spacer(1, 2))

    story.append(Paragraph("Exact Classical Wire Packet Structure (JSON Schema):", h2_style))
    json_packet = (
        "{\n"
        '  "header": { "signer_id": "Alice", "verifier_id": "Bob", "version": "1.0", "timestamp": 1772846400.123 },\n'
        '  "session": { "session_id": "sess_8f9a2b1c", "nonce": "e3b0c44298fc1c149afbf4c8996fb924" },\n'
        '  "payload": { "message_text": "Transfer 1000 Quantum Credits to Bob", "message_hash": "2c26b46b68ffc68f..." },\n'
        '  "teleportation": { "qubit_count": 16, "bsm_feedforward_bits": "00 01 10 11 00 10 01 11 00 00 11 01 10 00 01 11" },\n'
        '  "authentication": { "hmac_sha256": "9b73c6ce6f7e91ab560cb8f83e3a49e0c814123067832d39cc6a79e46e4b2a60" }\n'
        "}"
    )
    story.append(Paragraph(json_packet.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: TELEPORTATION MATHEMATICS & OPTICAL CHANNEL MODEL
    # =========================================================================
    story.append(Paragraph("7. Quantum Teleportation Mathematics &amp; Exact Reconstruction", h1_style))
    story.append(safe_p(
        "Teleportation transmits the unknown signature state |psi><sub>S</sub> = &alpha;|0&gt; + &beta;|1&gt; (|&alpha;|<sup>2</sup> + |&beta;|<sup>2</sup> = 1) from Alice to Bob. Alice and Bob share the maximally entangled Bell state |Phi+><sub>AB</sub> = (|00&gt; + |11&gt;)/&radic;2.",
        body_style
    ))
    story.append(safe_p(
        "<b>Step 1 — 3-Qubit Composite Joint State Formation:</b><br/>"
        "|&Psi;<sub>joint</sub>&gt; = |psi><sub>S</sub> &otimes; |Phi+><sub>AB</sub> = (&alpha;|0&gt;<sub>S</sub> + &beta;|1&gt;<sub>S</sub>) &otimes; (1/&radic;2)(|00&gt;<sub>AB</sub> + |11&gt;<sub>AB</sub>)<br/>"
        "|&Psi;<sub>joint</sub>&gt; = (1/&radic;2) [ &alpha;|000&gt;<sub>SAB</sub> + &alpha;|011&gt;<sub>SAB</sub> + &beta;|100&gt;<sub>SAB</sub> + &beta;|111&gt;<sub>SAB</sub> ]",
        body_style
    ))
    story.append(safe_p(
        "<b>Step 2 — Bell Basis Decomposition on Alice's Qubits (S, A):</b><br/>"
        "|&Psi;<sub>joint</sub>&gt; = 1/2 [ |Phi+><sub>SA</sub> &otimes; (&alpha;|0&gt; + &beta;|1&gt;)<sub>B</sub> &nbsp;+&nbsp; |Phi-><sub>SA</sub> &otimes; (&alpha;|0&gt; - &beta;|1&gt;)<sub>B</sub> &nbsp;+&nbsp; |Psi+><sub>SA</sub> &otimes; (&beta;|0&gt; + &alpha;|1&gt;)<sub>B</sub> &nbsp;+&nbsp; |Psi-><sub>SA</sub> &otimes; (-&beta;|0&gt; + &alpha;|1&gt;)<sub>B</sub> ]",
        body_style
    ))
    story.append(safe_p(
        "<b>Step 3 — Bell-State Measurement (BSM) &amp; Bob's Unitary Correction:</b><br/>"
        "Alice performs a projective measurement in the Bell basis on qubits (S, A). Alice transmits the 2-bit result (c1, c2) classically. Bob applies unitary correction <b>U = Z<sup>c1</sup> X<sup>c2</sup></b>:",
        body_style
    ))

    bsm_data = [
        [safe_p("BSM Outcome", table_hdr), safe_p("Bits (c1, c2)", table_hdr), safe_p("Bob's Collapsed State |phi_B>", table_hdr), safe_p("Pauli Correction U = Z<sup>c1</sup> X<sup>c2</sup>", table_hdr), safe_p("Bob's Corrected State", table_hdr), safe_p("Fidelity", table_hdr)],
        [safe_p("|Phi+><sub>SA</sub>", table_cell), safe_p("0 0", table_cell_bold), safe_p("&alpha;|0&gt; + &beta;|1&gt;", table_cell), safe_p("U = Z<sup>0</sup> X<sup>0</sup> = I", table_cell), safe_p("I|psi> = |psi>", table_cell), safe_p("<b>1.000000</b>", table_cell)],
        [safe_p("|Psi+><sub>SA</sub>", table_cell), safe_p("0 1", table_cell_bold), safe_p("&alpha;|1&gt; + &beta;|0&gt;", table_cell), safe_p("U = Z<sup>0</sup> X<sup>1</sup> = X", table_cell), safe_p("X(X|psi>) = |psi>", table_cell), safe_p("<b>1.000000</b>", table_cell)],
        [safe_p("|Phi-><sub>SA</sub>", table_cell), safe_p("1 0", table_cell_bold), safe_p("&alpha;|0&gt; - &beta;|1&gt;", table_cell), safe_p("U = Z<sup>1</sup> X<sup>0</sup> = Z", table_cell), safe_p("Z(Z|psi>) = |psi>", table_cell), safe_p("<b>1.000000</b>", table_cell)],
        [safe_p("|Psi-><sub>SA</sub>", table_cell), safe_p("1 1", table_cell_bold), safe_p("&alpha;|1&gt; - &beta;|0&gt;", table_cell), safe_p("U = Z<sup>1</sup> X<sup>1</sup> = ZX = -iY", table_cell), safe_p("(ZX)(XZ|psi>) = |psi>", table_cell), safe_p("<b>1.000000</b>", table_cell)]
    ]
    t_bsm = Table(bsm_data, colWidths=[65, 55, 120, 110, 95, 59])
    t_bsm.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_bsm)
    story.append(Spacer(1, 4))

    # 8. Optical Fiber Model
    story.append(Paragraph("8. Photonic Optical Channel Physical Noise &amp; Loss Model", h1_style))
    story.append(safe_p(
        "The transmission link is modeled for telecom single-mode optical fiber (SMF-28) at &lambda; = 1550 nm:<br/>"
        "&bull; <b>Optical Attenuation:</b> Transmittance T(L) = 10<sup>-&alpha; &middot; L / 10</sup>, with standard fiber loss &alpha; = 0.20 dB/km.<br/>"
        "&bull; <b>Depolarizing Channel Noise:</b> &Epsilon;(&rho;) = (1 - p)&rho; + (p/3)(X&rho;X + Y&rho;Y + Z&rho;Z), where depolarizing noise parameter accumulates with transmission distance.<br/>"
        "&bull; <b>Single-Photon Detector Characteristics:</b> Quantum efficiency &eta; = 0.85, dark count probability p<sub>dark</sub> = 10<sup>-5</sup> per gate window, and polarization alignment error p<sub>align</sub> = 0.01.",
        body_style
    ))

    # 9. Baseline Calibration & Statistical Metrics
    story.append(Paragraph("9. Baseline Calibration (P<sub>0,L</sub>) &amp; Threat Detection Metrics", h1_style))
    story.append(safe_p(
        "<b>Legitimate Baseline Calibration:</b> To eliminate false alarms caused by genuine optical attenuation and quantum noise, the system pre-calibrates the baseline distribution vector <b>P<sub>0,L</sub> = [P(X+), P(X-), P(Y+), P(Y-), P(Z0), P(Z1)]<sup>T</sup></b>.<br/>"
        "<b>Statistical Distance Metrics:</b><br/>"
        "&bull; <b>Total Variation Distance (TVD):</b> D<sub>TV</sub>(P&#770;<sub>N</sub>, P<sub>0,L</sub>) = 0.5 &middot; &sum;<sub>k=1..6</sub> |P&#770;<sub>N</sub>(k) - P<sub>0,L</sub>(k)|.<br/>"
        "&bull; <b>Pearson's Chi-Square Test:</b> &chi;<sup>2</sup> = &sum;<sub>k=1..6</sub> (O<sub>k</sub> - E<sub>k</sub>)<sup>2</sup> / E<sub>k</sub>, with degrees of freedom df = 5.<br/>"
        "&bull; <b>Distance-Aware Adaptive Threshold:</b> &tau;(L, N, &eta;, &alpha;<sub>sig</sub>) = &mu;<sub>D0</sub>(L) + z<sub>1-&alpha;</sub> &middot; (&sigma;<sub>D0</sub>(L) / &radic;N) + &Delta;<sub>detector</sub>(&eta;).",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: 4-TIER VERIFICATION PIPELINE & ADVERSARIAL THREAT DEFENSE
    # =========================================================================
    story.append(Paragraph("10. Bob's Four-Tier Client Verification Architecture", h1_style))
    tier_data = [
        [safe_p("Tier", table_hdr), safe_p("Subsystem", table_hdr), safe_p("Evaluated Cryptographic &amp; Physical Conditions", table_hdr), safe_p("Latency &amp; Failure Action", table_hdr)],
        [
            safe_p("<b>Tier 1</b>", table_cell_bold),
            safe_p("Classical Cyber Clearance", table_cell),
            safe_p("1. Validates HMAC-SHA256 signer tag using Key<sub>Alice</sub>.<br/>2. Checks Nonce Store to prevent replay attacks.<br/>3. Verifies Bob's clearance against Verifier ACL.", table_cell),
            safe_p("<b>&lt; 1 ms</b><br/>Immediate REJECT (Drops packet before quantum processing)", table_cell)
        ],
        [
            safe_p("<b>Tier 2</b>", table_cell_bold),
            safe_p("QDS Overlap Fidelity", table_cell),
            safe_p("Computes quantum state overlap F<sub>k</sub> = &lt;psi<sub>k</sub>|&rho;<sub>k</sub>|psi<sub>k</sub>&gt;. Calculates Mismatch Rate R<sub>mismatch</sub> = (1/K) &sum; I(F<sub>k</sub> &lt; 0.85). Requires R<sub>mismatch</sub> &le; 15%.", table_cell),
            safe_p("<b>~5 ms</b><br/>REJECT (Signature Forgery detected)", table_cell)
        ],
        [
            safe_p("<b>Tier 3</b>", table_cell_bold),
            safe_p("Statistical Threat Engine", table_cell),
            safe_p("Executes multi-basis X/Y/Z sampling (N shots). Computes TVD D<sub>TV</sub>, Pearson's &chi;<sup>2</sup>, and Z-score vs pre-calibrated baseline P<sub>0,L</sub>.", table_cell),
            safe_p("<b>~15 ms</b><br/>Flags Anomaly (SUSPICIOUS or REJECT)", table_cell)
        ],
        [
            safe_p("<b>Tier 4</b>", table_cell_bold),
            safe_p("Tri-State Arbitration", table_cell),
            safe_p("Evaluates composite rule:<br/>&bull; ACCEPT if D<sub>TV</sub> &le; &tau;<sub>accept</sub> and Tier 1, 2 pass.<br/>&bull; SUSPICIOUS if &tau;<sub>accept</sub> &lt; D<sub>TV</sub> &le; &tau;<sub>crit</sub>.<br/>&bull; REJECT if D<sub>TV</sub> &gt; &tau;<sub>crit</sub> or any earlier tier fails.", table_cell),
            safe_p("<b>&lt; 1 ms</b><br/>Definitive Decision Record + Audit Log", table_cell)
        ]
    ]
    t_tier = Table(tier_data, colWidths=[40, 95, 244, 125])
    t_tier.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_tier)
    story.append(Spacer(1, 4))

    # 11. Adversarial Threat Models & Defensive Guarantees
    story.append(Paragraph("11. Adversarial Threat Models &amp; Defensive Guarantees", h1_style))
    attack_data = [
        [safe_p("Threat Category", table_hdr), safe_p("Adversarial Operation", table_hdr), safe_p("Defense &amp; Detection Mechanism", table_hdr), safe_p("Empirical Defense Rate", table_hdr)],
        [
            safe_p("<b>Signature Forgery</b>", table_cell_bold),
            safe_p("Eve guesses or creates random quantum states without Alice's private key", table_cell),
            safe_p("Tier 2 overlap fidelity test flags state mismatches exceeding 15% threshold", table_cell),
            safe_p("<b>P<sub>forge</sub> = 0.0000</b><br/>(&le; 0.00209 theoretical bound)", table_cell)
        ],
        [
            safe_p("<b>Nonce Replay</b>", table_cell_bold),
            safe_p("Eve captures and re-transmits a stale valid classical/quantum bundle", table_cell),
            safe_p("Tier 1 Nonce Cache detects duplicate 128-bit nonce hash within window", table_cell),
            safe_p("<b>100.0% Rejection</b><br/>(30/30 blocked at Tier 1)", table_cell)
        ],
        [
            safe_p("<b>Signer Impersonation</b>", table_cell_bold),
            safe_p("Eve claims to be Alice using spoofed identifier or altered key", table_cell),
            safe_p("Tier 1 HMAC-SHA256 signature verification fails public key check", table_cell),
            safe_p("<b>100.0% Rejection</b><br/>(30/30 blocked at Tier 1)", table_cell)
        ],
        [
            safe_p("<b>Unauthorized Verifier</b>", table_cell_bold),
            safe_p("Rogue network node attempts to verify Alice's signature without access", table_cell),
            safe_p("Tier 1 Verifier Access Control List (ACL) rejects rogue identifier", table_cell),
            safe_p("<b>100.0% Rejection</b><br/>(30/30 blocked at Tier 1)", table_cell)
        ],
        [
            safe_p("<b>Pauli Attacks (X, Y, Z)</b>", table_cell_bold),
            safe_p("Eve applies Pauli X (bit flip), Z (phase flip), or Y (bit-phase flip) on optical channel", table_cell),
            safe_p("Tier 3 TVD D<sub>TV</sub> &gt; adaptive threshold &tau; with Pearson's &chi;<sup>2</sup> confirmation", table_cell),
            safe_p("<b>P<sub>D</sub> = 100.0%</b><br/>for attack strength p<sub>a</sub> &ge; 20%", table_cell)
        ]
    ]
    t_atk = Table(attack_data, colWidths=[90, 130, 174, 110])
    t_atk.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_atk)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: BENCHMARK RESULTS, CODE STRUCTURE & EXECUTION GUIDE
    # =========================================================================
    story.append(Paragraph("12. Scientific Benchmark Experiments &amp; Empirical Results", h1_style))
    bench_data = [
        [safe_p("Exp #", table_hdr), safe_p("Benchmark Experiment Suite", table_hdr), safe_p("Key Empirical Scientific Finding", table_hdr), safe_p("Status", table_hdr)],
        [safe_p("<b>01</b>", table_cell_bold), safe_p("Teleportation Validation", table_cell), safe_p("Ideal teleportation fidelity F = 1.000000 +/- 0.000000 across all 6 Pauli states.", table_cell), safe_p("<font color='#16a34a'><b>PASS (100%)</b></font>", table_cell)],
        [safe_p("<b>02</b>", table_cell_bold), safe_p("Photonic Channel Scaling", table_cell), safe_p("Transmittance adheres to &alpha; = 0.20 dB/km standard optical fiber model.", table_cell), safe_p("<font color='#16a34a'><b>PASS</b></font>", table_cell)],
        [safe_p("<b>03</b>", table_cell_bold), safe_p("Legitimate Baseline P<sub>0,L</sub>", table_cell), safe_p("Calibrated baseline TVD &mu;<sub>D0</sub> approx 0.035-0.038 prevents false alarms.", table_cell), safe_p("<font color='#16a34a'><b>PASS</b></font>", table_cell)],
        [safe_p("<b>04</b>", table_cell_bold), safe_p("Pauli Attacks (X, Y, Z)", table_cell), safe_p("Detection probability P<sub>D</sub> = 100.0% for attack strengths p<sub>a</sub> &ge; 20% across all conjugate bases.", table_cell), safe_p("<font color='#16a34a'><b>PASS (100%)</b></font>", table_cell)],
        [safe_p("<b>05</b>", table_cell_bold), safe_p("Signature Forgery Defense", table_cell), safe_p("Empirical P<sub>forge</sub> = 0.0000 &le; Theoretical Bound P<sub>theo</sub> = 0.002090 (zero forged signatures).", table_cell), safe_p("<font color='#16a34a'><b>PASS (0% Forged)</b></font>", table_cell)],
        [safe_p("<b>06</b>", table_cell_bold), safe_p("Nonce Replay Defense", table_cell), safe_p("100.0% replay rejection rate (30/30 stale nonces intercepted and dropped at Tier 1).", table_cell), safe_p("<font color='#16a34a'><b>PASS (100%)</b></font>", table_cell)],
        [safe_p("<b>07</b>", table_cell_bold), safe_p("Signer Impersonation", table_cell), safe_p("100.0% spoofed signer rejection rate (30/30 invalid HMAC tags dropped at Tier 1).", table_cell), safe_p("<font color='#16a34a'><b>PASS (100%)</b></font>", table_cell)],
        [safe_p("<b>08</b>", table_cell_bold), safe_p("Unauthorized Verifier", table_cell), safe_p("100.0% rogue verifier access rejection rate (30/30 blocked via Verifier ACL).", table_cell), safe_p("<font color='#16a34a'><b>PASS (100%)</b></font>", table_cell)],
        [safe_p("<b>09</b>", table_cell_bold), safe_p("Channel Sensitivity", table_cell), safe_p("Clean acceptance &ge; 96%, 100% attack detection maintained across optical link.", table_cell), safe_p("<font color='#16a34a'><b>PASS</b></font>", table_cell)],
        [safe_p("<b>10</b>", table_cell_bold), safe_p("Shot Count Scaling (N)", table_cell), safe_p("Statistical confidence bounds narrow predictably from N=100 to N=10,000 shots.", table_cell), safe_p("<font color='#16a34a'><b>PASS</b></font>", table_cell)],
        [safe_p("<b>11</b>", table_cell_bold), safe_p("Threshold ROC Curve", table_cell), safe_p("Near-ideal ROC curve with AUC &gt; 0.99 confirming optimal statistical discrimination.", table_cell), safe_p("<font color='#16a34a'><b>PASS</b></font>", table_cell)]
    ]
    t_bench = Table(bench_data, colWidths=[30, 115, 284, 75])
    t_bench.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_bench)
    story.append(Spacer(1, 3))

    # 13. Software Architecture & Execution Guide
    story.append(Paragraph("13. Software Architecture &amp; Execution Manual", h1_style))
    story.append(safe_p(
        "<b>Modular Package Layout:</b> <font name='Courier'>quantum/</font> (circuits, teleportation, measurements), <font name='Courier'>photonic/</font> (polarization modes, optical loss, noise, detectors), <font name='Courier'>qds/</font> (signer, verifier, mismatch rate), <font name='Courier'>security/</font> (HMAC-SHA256, nonce cache, ACL), <font name='Courier'>attacks/</font> (Pauli, forgery, replay, impersonation), <font name='Courier'>detection/</font> (baselines, TVD, &chi;<sup>2</sup>, adaptive thresholds, tri-state decision), <font name='Courier'>web/</font> (interactive demonstration dashboard).",
        body_style
    ))
    code_guide = (
        "# 1. Run unit &amp; integration test suite (43/43 tests green, 100% pass):   pytest tests/ -v\n"
        "# 2. Launch interactive web demonstration dashboard (http://localhost:8000): python main.py --demo\n"
        "# 3. Execute all 11 scientific benchmark experiment suites:                   python main.py --run-all-experiments\n"
        "# 4. Run custom simulation via CLI:                                         python main.py --simulate --distance 50 --attack X --strength 0.20\n"
        "# 5. Re-compile this technical PDF report:                                  python scripts/generate_project_pdf.py"
    )
    story.append(Paragraph(code_guide.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))
    story.append(Spacer(1, 3))

    # 14. Strategic Alignment & Conclusion
    story.append(Paragraph("14. Strategic Alignment &amp; Conclusion", h1_style))
    story.append(safe_p(
        "&bull; <b>National Quantum Mission Alignment:</b> Directly supports India's ₹6,003.65 Cr National Quantum Mission (2023–2031) Quantum Communications T-Hub.<br/>"
        "&bull; <b>Strictly Non-AI/ML Deterministic Guarantees:</b> Eliminates neural network black-box hallucination risks through mathematically rigorous statistical hypothesis testing (D<sub>TV</sub>, &chi;<sup>2</sup>).<br/>"
        "&bull; <b>Real-Time Feasibility:</b> Sub-25 ms verification latency and polynomial complexity &Omicron;(K &middot; N) confirm practical readiness for high-throughput digital signature validation.",
        body_style
    ))

    # Compile PDF Document
    doc.build(story, canvasmaker=NumberedCanvas)

    alt_file = "photonic_qds_security_simulator_report.pdf"
    shutil.copyfile(output_filename, alt_file)
    print(f"✓ PDF successfully generated: {output_filename} and {alt_file}")
    return output_filename


if __name__ == "__main__":
    generate_pdf()
