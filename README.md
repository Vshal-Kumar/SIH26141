# Quantum-Inspired Cyber Threat Detection for Digital Signature Security (SIH PS 26141)

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-43%20passed%20(100%25)-brightgreen.svg)]()
[![SIH Category](https://img.shields.io/badge/SIH-Cybersecurity%20%26%20Quantum%20Comms-purple.svg)]()
[![Deterministic](https://img.shields.io/badge/Detection-Deterministic%20Statistical%20(No%20AI%2FML)-orange.svg)]()
[![Verification Latency](https://img.shields.io/badge/Latency-%3C%2030%20ms-success.svg)]()
[![Problem Owner](https://img.shields.io/badge/Problem%20Owner-Egreen%20Quanta%20LLP-blueviolet.svg)]()

A research-grade Python simulation framework implementing a **Teleportation-Based Quantum Digital Signature (QDS)** protocol over a **photonic optical channel** (standard telecom fiber at $\lambda = 1550\text{ nm}$ with realistic loss $\alpha = 0.2\text{ dB/km}$ and quantum noise).

Developed for **Smart India Hackathon (SIH 2026)** | **Problem Statement 5 / ID 26141** | **Organization: Egreen Quanta LLP** | **Team: HexaCore**.

---

## 🎯 Official Deliverables Compliance Matrix (Egreen Quanta LLP)

| S.No | Expected Deliverable | Description | Implementation in this Framework | Compliance Status |
|:---:|---|---|---|:---:|
| **1** | **Mathematical Model of Teleportation-based QDS** | Formal description of signature protocol | • Bell-state entanglement ($|\Phi^+\rangle$)<br>• Quantum teleportation with Bell-State Measurement (BSM)<br>• Pauli unitary corrections ($U = Z^{c_1}X^{c_2}$)<br>• Multi-basis projective measurement rules ($X, Y, Z$) | **100% Complete**<br>([`quantum/`](file:///home/vishal-kumar/Desktop/SIH/SIH26141/quantum)) |
| **2** | **Quantum-Inspired Threat Detection Framework** | Core detection engine | • Strictly non-AI/ML deterministic statistical engine<br>• Total Variation Distance ($D_{TV}$) + Pearson's $\chi^2$ hypothesis testing<br>• Distance-aware adaptive thresholds $\tau(L, N)$<br>• Detection of forgery, impersonation, replay, & channel tampering | **100% Complete**<br>([`detection/`](file:///home/vishal-kumar/Desktop/SIH/SIH26141/detection), [`security/`](file:///home/vishal-kumar/Desktop/SIH/SIH26141/security)) |
| **3** | **Signature Generation & Verification Module** | Implementation of QDS operations | • Quantum public key distribution simulation<br>• Alice's signature generation across 6 Pauli eigenstates<br>• Bob's 4-tier verification algorithm with Pauli corrections | **100% Complete**<br>([`qds/`](file:///home/vishal-kumar/Desktop/SIH/SIH26141/qds)) |
| **4** | **Attack Simulation Module** | Controlled simulation of cyber threats | • Quantum state guessing / forgery attempts<br>• Signer identity impersonation spoofing<br>• Nonce replay attacks<br>• Optical channel tampering (Pauli $X, Y, Z$ bit/phase flips) | **100% Complete**<br>([`attacks/`](file:///home/vishal-kumar/Desktop/SIH/SIH26141/attacks)) |
| **5 & 6** | **Software Framework / Prototype** | End-to-end implementable system | • Interactive Web Demonstration Dashboard (`python main.py --demo`)<br>• CLI Simulation Interface (`python main.py --simulate`)<br>• Security event audit logging & 11 benchmark suites<br>• 43 automated Pytest test cases (100% Green) | **100% Complete**<br>([`web/`](file:///home/vishal-kumar/Desktop/SIH/SIH26141/web), [`main.py`](file:///home/vishal-kumar/Desktop/SIH/SIH26141/main.py)) |

---

---

## ⚡ Quick Start Guide (Run in 2 Minutes)

### 1. Clone & Enter the Project Directory
```bash
git clone <your-repository-url>
cd SIH26141
```

### 2. Create and Activate Virtual Environment

* **On Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

* **On Windows (Command Prompt / PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```

### 3. Install All Dependencies
```bash
pip install -r requirements.txt
```

---

## 🎮 How to Run (5 Execution Modes)

### 🌟 Mode 1: Launch the Interactive Web Demonstration Dashboard
```bash
python main.py --demo
```
* Open **`http://localhost:8000`** in your browser.
* **Interactive UI Features:**
  * Adjust optical fiber distance slider ($0 - 200\text{ km}$).
  * Choose attack vectors (Pauli $X, Y, Z$, Forgery, Replay, Impersonation, Unauthorized Verifier).
  * Tune attack strength ($0\% - 100\%$) and shot count ($100 - 10,000$).
  * View live Pauli measurement histograms, statistical distance ($D_{TV}$) gauge, and real-time **`ACCEPT / SUSPICIOUS / REJECT`** decision audits.

---

### 🧪 Mode 2: Run All 43 Automated Unit & Integration Tests (100% Green)
```bash
pytest tests/ -v
```
Verifies Pauli algebra, Bell states, quantum teleportation fidelity ($\mathcal{F} = 1.0$), optical fiber loss, QDS verification, replay detection, impersonation defense, and the statistical decision engine.

---

### 📊 Mode 3: Execute All 11 Scientific Benchmark Experiment Suites
```bash
python main.py --run-all-experiments
# OR
python scripts/run_all_experiments.py
```
Automatically executes all 11 scientific benchmark suites, populating:
* **`results/figures/`** with 11 high-resolution publication plots (`.png`).
* **`results/tables/`** with 11 scientific benchmark data tables (`.csv`).

---

### ⚡ Mode 4: Run a Custom Single Simulation via CLI
```bash
# Example 1: Clean 50 km transmission
python main.py --simulate --distance 50 --attack none --strength 0.0 --shots 1000

# Example 2: 50 km optical link with 20% Pauli X bit-flip tampering
python main.py --simulate --distance 50 --attack X --strength 0.20 --shots 1000

# Example 3: Impersonation attack test
python main.py --simulate --distance 50 --attack impersonation
```

---

### 📄 Mode 5: Generate the Technical PDF Report
```bash
python scripts/generate_project_pdf.py
```
Generates a publication-grade technical report: **[`Photonic_QDS_Security_Simulator_Technical_Report.pdf`](file:///home/vishal-kumar/Desktop/SIH/SIH26141/Photonic_QDS_Security_Simulator_Technical_Report.pdf)**.

---

## 🏛️ System Architecture

```text
Message (M) ──────────► Alice (Signer)
                              │
                    Session ID + Nonce
                              │
                    Quantum Signature State
                              │
                    Pauli Eigenstate Preparation (|0>, |1>, |+>, |->, |+_y>, |-_y>)
                              │
                    Bell Entanglement (|Phi+> = (|00> + |11>)/sqrt(2))
                              │
                    TELEPORTATION (BSM Outcomes c1, c2)
                              │
       ┌──────────────────────┴──────────────────────┐
       ▼                                             ▼
[Clean Photonic Channel]                     [Adversary Eve Attacks]
- Distance L (10 - 200 km)                   - Pauli X (Bit-Flip)
- Attenuation T(L) = 10^(-alpha*L/10)        - Pauli Z (Phase-Flip)
- Depolarizing & Dephasing Noise             - Pauli Y (Bit-Phase Flip)
- Single-Photon Detector Jitter/Dark Counts  - Depolarization Channel
                                             - Signature Forgery
                                             - Nonce Replay Attack
                                             - Signer Impersonation
                                             - Unauthorized Verifier
       └──────────────────────┬──────────────────────┘
                              │
                              ▼
                      Bob (Verifier)
                              │
       ┌──────────────────────┼──────────────────────┐
       ▼                      ▼                      ▼
[Authentication]        [Freshness]           [Authorization]
- Signer Identity       - Nonce Cache         - Verifier Role Clearance
- HMAC-SHA256 Tag       - Session Expiry      - Rogue Inspection Defense
       └──────────────────────┬──────────────────────┘
                              │
                              ▼
                      QDS Verification
                      - Pauli Unitary Correction: U = Z^c1 * X^c2
                      - Quantum State Fidelity & Mismatch Rate
                              │
                              ▼
               Multi-Basis Projective Measurements
               - X-Basis (Diagonal)
               - Y-Basis (Circular)
               - Z-Basis (Computational)
                              │
                              ▼
               Deterministic Statistical Threat Engine
               - Empirical Frequency Vector: P_N
               - Calibrated Legitimate Baseline: P_{0,L}
               - Total Variation Distance: D_TV(P_N, P_{0,L})
               - Pearson's Chi-Square Test (chi2, p-value)
               - Multi-Component Z-Score Hypothesis Testing
               - Adaptive Threshold: tau(L, N, alpha)
                              │
                              ▼
                Tri-State Decision Arbitrator
               ┌──────────────┼──────────────┐
               ▼              ▼              ▼
             ACCEPT       SUSPICIOUS       REJECT
```

---

## 🔐 How Classical & Quantum Work Together to Form QDS

| Layer | Technology | Cryptographic Function |
|---|---|---|
| **Classical Layer** | SHA-256 Digest + Nonces + HMAC-SHA256 | Binds variable-length messages to Alice's identity; prevents replay attacks and classical metadata tampering in $\mathcal{O}(1)$ time. |
| **Quantum Layer** | Bell Entanglement ($|\Phi^+\rangle$) + Teleportation | Provides unforgeable physical signature states. Alice performs Bell-State Measurements (BSM), Bob reconstructs via Pauli unitaries $U = Z^{c_1} X^{c_2}$. |
| **Threat Engine** | Multi-Basis Projective Measurements ($X, Y, Z$) | Measures received photons across non-commuting bases. Detects physical eavesdropping using Total Variation Distance ($D_{TV}$) vs. distance-aware adaptive thresholds $\tau(L, N)$—**strictly without AI/ML black boxes**. |

---

## 🛡️ The 4-Tier Verification Pipeline

1. **Tier 1 — Classical Cyber Security Filter:** Evaluates HMAC authentication tag, nonce freshness in memory, and verifier ACL. Fails immediately at **$0\text{ ms}$** without wasting quantum budget.
2. **Tier 2 — Quantum State Fidelity:** Reconstructs state $\rho_k$ and evaluates $\mathcal{F}_k = \langle \psi_k | \rho_k | \psi_k \rangle$. Rejects as **Forged** if mismatch rate $> 15\%$.
3. **Tier 3 — Deterministic Statistical Threat Engine:** Measures in $X, Y, Z$ bases over $N$ shots, builds empirical distribution $\hat{P}_N$, and computes Total Variation Distance $D_{TV}(\hat{P}_N, P_{0,L})$ and Pearson's $\chi^2$.
4. **Tier 4 — Tri-State Decision Arbitration:**
   * **`ACCEPT`**: Authentic signature and clean optical link ($D_{TV} \le \tau_{\text{accept}}$).
   * **`SUSPICIOUS`**: Structurally valid signature, but statistical anomaly detected ($\tau_{\text{accept}} < D_{TV} \le \tau_{\text{crit}}$).
   * **`REJECT`**: Cryptographic failure, forged state, or critical quantum attack ($D_{TV} > \tau_{\text{crit}}$).

---

## 📊 Scientific Benchmark Summary (11 Experiment Suites)

| Experiment Suite | Metric / Focus | Key Empirical Result | Status |
|---|---|---|:---:|
| **01. Teleportation Validation** | Fidelity across all 6 Pauli states | $\mathcal{F} = 1.000000 \pm 0.000000$ for all states | **PASS (100%)** |
| **02. Photonic Channel Scaling** | Fiber loss & transmission vs $L$ | $T(50\text{km}) = 10.0\%$, $T(100\text{km}) = 1.0\%$, adhering to $0.2\text{ dB/km}$ | **PASS** |
| **03. Legitimate Baselines** | Mean TVD under $H_0$ across distances | Baseline TVD $\mu_{D_0} \approx 0.035 - 0.038$ over $10 - 200\text{ km}$ | **PASS** |
| **04. Pauli Attacks ($X, Y, Z$)** | Detection Probability $P_D$ vs $p_a$ | $P_D = 100.0\%$ for $p_a \ge 20\%$ across $X, Y, Z$ | **PASS (100%)** |
| **05. Signature Forgery** | Empirical vs Theoretical Forgery Bound | Empirical $P_{\text{forge}} = 0.0000 \le P_{\text{theo}} = 0.002090$ | **PASS (0% Forged)** |
| **06. Nonce Replay Protection** | Replay detection rate | $100.0\%$ replay rejection rate ($30/30$ detected and blocked) | **PASS (100%)** |
| **07. Signer Impersonation** | Identity spoofing rejection rate | $100.0\%$ impersonation rejection rate ($30/30$ rejected) | **PASS (100%)** |
| **08. Unauthorized Verifier** | Rogue verifier rejection rate | $100.0\%$ rogue request rejection rate ($30/30$ rejected) | **PASS (100%)** |
| **09. Distance Sensitivity** | Clean acceptance vs Attack detection | Clean acceptance $\ge 96\%$ up to $100\text{ km}$, $P_D = 100\%$ | **PASS** |
| **10. Shot Count Scaling ($N$)** | Detection sensitivity vs budget $N$ | High confidence scaling from $N=100$ to $N=10,000$ shots | **PASS** |
| **11. Threshold ROC Trade-Off** | False Acceptance vs False Rejection | Clear statistical separation under calibrated adaptive threshold | **PASS** |

---

## 📁 Repository Structure

```text
photonic_qds_security_sim/
│
├── main.py                           # Master CLI entry point (demo, benchmarks, single sim)
├── requirements.txt                  # Lightweight dependencies
├── pyproject.toml                    # Pytest configuration
├── README.md                         # Comprehensive documentation
├── .gitignore                        # Git exclusion rules
├── Photonic_QDS_Security_Simulator_Technical_Report.pdf # Publication PDF report
│
├── config/                           # System and physical configurations
│   ├── protocol_config.py            # QDS signature lengths (K=16), hash algorithms, mismatch thresholds
│   ├── photonic_config.py            # Fiber loss alpha=0.2 dB/km, dark counts, efficiency eta=0.85
│   ├── security_config.py            # Nonce window, registry, anomaly thresholds
│   └── experiment_config.py          # Benchmark sweep parameters
│
├── core/                             # Core simulation orchestrators
│   ├── message.py                    # Classical message structure, SHA-256 hash
│   ├── session.py                    # Session store, nonce cache
│   ├── simulator.py                  # Master simulation orchestrator
│   └── results.py                    # Structured result models & timing breakdown
│
├── quantum/                          # Quantum mechanics foundation
│   ├── pauli_states.py               # Pauli eigenstates (|H>, |V>, |D>, |A>, |R>, |L>), density matrices
│   ├── bell_states.py                # 4 Bell states (|Phi+>), EPR generation, Bell projectors
│   ├── teleportation.py              # Teleportation engine with BSM
│   ├── pauli_correction.py           # Unitary recovery operations U = Z^c1 X^c2
│   ├── measurements.py               # Projective measurements in X, Y, Z bases
│   └── quantum_backend.py            # PennyLane & PennyLane-Lightning circuit QNodes
│
├── photonic/                         # Photonic optical fiber physics
│   ├── polarization.py               # Qubit-to-polarization mapping
│   ├── fiber_loss.py                 # Transmission T(L) = 10^(-alpha*L/10)
│   ├── channel_noise.py              # Depolarizing & dephasing noise models
│   ├── detector_model.py             # Quantum efficiency eta=0.85, dark counts, alignment jitter
│   ├── optical_channel.py            # Integrated optical fiber channel
│   └── channel_statistics.py         # SNR, QBER, loss scaling calculations
│
├── qds/                              # Discrete-variable QDS protocol
│   ├── protocol.py                   # Full signing -> transmission -> verification cycle
│   ├── signer.py                     # Alice: key mapping, state preparation, signature assembly
│   ├── signature.py                  # Quantum digital signature container
│   ├── verifier.py                   # Bob: Pauli state reconstruction
│   └── verification.py               # QDS signature validity check (mismatch vs threshold)
│
├── security/                         # First-class protocol security subsystem
│   ├── authentication/               # Identity registry, signer authentication, verifier authorization
│   ├── freshness/                    # Nonce generation, session freshness, replay protection
│   ├── integrity/                    # Message, signature bundle, and quantum state integrity
│   ├── verification/                 # Quantum & protocol security integration
│   └── security_engine.py            # Central security coordinator
│
├── attacks/                          # Adversary attack subsystem (Eve)
│   ├── quantum/                      # Pauli X, Z, Y, and depolarizing state attacks
│   ├── signature/                    # Signature forgery generator
│   ├── protocol/                     # Replay, impersonation, and unauthorized verification attacks
│   └── attack_engine.py              # Master adversary controller
│
├── detection/                        # THE CORE CONTRIBUTION: Statistical Threat Detection
│   ├── baseline.py                   # Legitimate baseline generator P_{0,L} across distances
│   ├── probability.py                # Empirical distribution normalization
│   ├── measurement_statistics.py     # Multi-basis statistical moments, variance, covariance
│   ├── statistical_distance.py       # Total Variation Distance (TVD)
│   ├── chi_square.py                 # Pearson's Chi-square goodness-of-fit & exact p-value
│   ├── hypothesis_testing.py         # Z-score hypothesis testing
│   ├── threshold.py                  # Static baseline empirical percentiles
│   ├── adaptive_threshold.py         # Distance- and shot-aware dynamic threshold tau(L, N)
│   ├── anomaly_score.py              # Composite anomaly index [0.0, 1.0]
│   └── decision_engine.py            # Tri-state arbitrator (ACCEPT / SUSPICIOUS / REJECT)
│
├── experiments/                      # 11 Scientific Benchmark Experiment Suites (01 to 11)
├── evaluation/                       # Security & performance metric calculators
├── visualization/                    # Publication-quality plotting & demo server
├── web/static/                       # Interactive browser demonstration interface (HTML/CSS/JS)
├── results/                          # Generated figures (.png) and benchmark data tables (.csv)
└── tests/                            # 12 Comprehensive Test Suites (43 unit tests, 100% pass)
```

---

## ❓ Troubleshooting & FAQ for Teammates

1. **Port 8000 already in use when running `--demo`?**
   ```bash
   python main.py --demo --port 8080
   ```
   Then open `http://localhost:8080`.

2. **How to run tests with detailed output?**
   ```bash
   pytest tests/ -v -s
   ```

3. **Can this run without a GPU or physical quantum hardware?**
   Yes! The simulator runs entirely in high-speed Python/C++ state-vector simulation via PennyLane-Lightning and NumPy/SciPy, executing full quantum cycles in **$< 30\text{ ms}$** on standard laptops.
