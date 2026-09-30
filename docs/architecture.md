# TeleShield System Architecture

## 1. Architectural Philosophy

TeleShield is architected around four strictly decoupled, non-overlapping operational layers. This design prevents security decisions from polluting quantum simulation logic and guarantees backend portability across gate-model simulators, stabilizer engines, and neutral-atom hardware profiles.

```
                         TELESHIELD
                             |
          +------------------+------------------+
          |                  |                  |
          v                  v                  v
      QDS ENGINE        ATTACK ENGINE       Q-STAT
          |                  |                  |
          +------------------+------------------+
                             |
                             v
                    QUANTUM BACKEND API
                             |
             +---------------+---------------+
             |               |               |
             v               v               v
          Exact           Qiskit           Stim
          NumPy            Aer
                             |
                             v
                     Hardware Profiles
                      /             \
                     /               \
                Ion-Trap          Rydberg
                  Model            Model
                                     |
                                  Pulser
                             |
                             v
                     Measurement Evidence
                             |
                             v
                       Q-STAT Analysis
                             |
                             v
                          Verdict
                             |
                             v
                       Audit System
```

---

## 2. Layer Definitions

### Layer 1: Quantum Core (`teleshield/quantum/`)
* **Role:** Pure mathematical physics and state transformations.
* **Responsibilities:**
  - Single-qubit state representations (statevector, density matrix).
  - Pauli operators ($I, X, Y, Z$) and basis rotations ($H, S$).
  - Two-qubit Bell states ($|\Phi^+\rangle, |\Phi^-\rangle, |\Psi^+\rangle, |\Psi^-\rangle$) and Werner mixtures.
  - Quantum teleportation execution via 3-qubit joint density matrix operations.
  - Projective measurements in $Z, X, Y$ bases.
  - Unified noise models (depolarizing, dephasing, bit-flip, amplitude damping, loss).
* **Strict Rule:** Contains zero cryptography or security decision logic.

### Layer 2: Quantum Backend Abstraction (`teleshield/backends/`)
* **Role:** Abstract hardware interface isolating protocol execution from concrete simulators.
* **Implementations:**
  1. `ExactBackend`: High-precision NumPy matrix algebra; zero overhead; deterministic.
  2. `AerBackend`: Qiskit Aer gate-model circuits with noise models for ion-trap simulation.
  3. `StimBackend`: High-throughput stabilizer and Clifford tableau simulator for Pauli channels.
  4. `PulserBackend`: Rydberg neutral-atom hardware-aware simulator ($C_6 / R^6$ blockade, tweezer loss).
* **Strict Rule:** Protocol layers never import Qiskit or Pulser directly; all operations pass through `QuantumBackend`.

### Layer 3: QDS Protocol Layer (`teleshield/qds/`)
* **Role:** Cryptographic key generation, distribution, signing, and slot lifecycle management.
* **Responsibilities:**
  - Keypair generation ($n$ tag bits, $L$ states per bit).
  - Quantum public key teleportation into verifier `KeySlot` records.
  - Message binding via SHA-256 or Toeplitz universal hashing.
  - Signature envelope assembly (`QDSSignature`).
  - Physical measurement execution and slot consumption enforcement.
* **Strict Rule:** Never uses machine learning; relies on physical no-cloning and measurement collapse.

### Layer 4: Q-STAT Threat Detection Engine (`teleshield/qstat/`)
* **Role:** Multi-stage deterministic statistical analysis, threat triage, and explainable verdict synthesis.
* **Pipeline Stages:**
  1. `envelope.py`: Schema and field consistency check $\to$ `MALFORMED`.
  2. `freshness.py`: Nonce and timestamp validation $\to$ `REPLAY`.
  3. `authorization.py`: Verifier identity and key ownership verification $\to$ `UNAUTHORIZED_VERIFICATION`.
  4. `integrity.py`: Classical hash tag recalculation $\to$ `MESSAGE_TAMPERED`.
  5. `statistics.py` & `binomial.py`: Multi-block and multi-basis hypothesis testing against Hoeffding threshold $s_a$.
  6. `fingerprint.py`: Asymmetric error dispersion analysis (dephasing vs bit-flip vs depolarizing).
  7. `verdict.py`: Synthesis of explainable verdict with p-value and confidence interval.

---

## 3. Application and Presentation Layer

* **FastAPI Backend (`teleshield/api/`):** RESTful endpoints for keygen, distribution, signing, verification, and audit verification.
* **Streamlit Dashboard (`teleshield/dashboard/`):** Interactive cyber operations UI with live Plotly visualizations across 6 dedicated pages.
* **Cryptographic Audit (`teleshield/audit/`):** SHA-256 hash chaining guaranteeing tamper-evidence for all verification outcomes.
* **Local Database (`teleshield/database/`):** SQLite metadata storage (quantum states remain exclusively in volatile memory).
