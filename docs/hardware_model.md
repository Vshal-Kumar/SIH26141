

# TeleShield Hardware-Aware Simulation Models

## 1. Hardware Model Governance & Disclaimers

> **IMPORTANT NOTICE:**
> The simulation models implemented in TeleShield represent peer-reviewed, literature-derived academic benchmarks for trapped-ion and neutral-atom physical architectures.
> They do **NOT** reproduce or claim to reproduce any proprietary hardware specifications, calibration data, or internal gate designs of **Egreen Quanta** or commercial quantum computing vendors.
> All parameters are explicitly classified into three strict provenance categories:
> 1. `literature-derived`: Extracted from published experimental peer-reviewed papers.
> 2. `assumed`: Idealized or operational baseline assumptions necessary for simulation tractability.
> 3. `experimentally configured`: Standard laboratory benchmarking setup values.

---

## 2. Primary Hardware Model: Ion-Trap-Aligned Simulation Profile

### 2.1 Physical Alignment & Gate Physics
* **Physical System:** Trapped atomic ions (e.g. $^{171}\text{Yb}^+$ or $^{40}\text{Ca}^+$) confined in linear radio-frequency (RF) Paul traps with individual optical addressing.
* **Qubit Representation:** Hyperfine or optical clock states $|0\rangle \equiv |F=0, m_F=0\rangle$ and $|1\rangle \equiv |F=1, m_F=0\rangle$.
* **Entangling Mechanism:** Mølmer-Sørensen (MS) bichromatic Raman laser gate coupling internal spin states to shared collective motional modes.
* **Readout Mechanism:** State-dependent electron shelving and fluorescence imaging via PMT/EMCCD arrays.

### 2.2 Profile Parameters (`profiles/ion_trap.yaml`)

| Parameter | Value | Provenance | Physical Description |
| :--- | :--- | :--- | :--- |
| `one_qubit_gate_error` | $0.0005$ (99.95% fidelity) | `literature-derived` | Raman/microwave single-qubit rotations |
| `two_qubit_gate_error` | $0.0050$ (99.50% fidelity) | `literature-derived` | Two-qubit Mølmer-Sørensen entangling gate |
| `readout_error` | $0.0010$ (0.10%) | `literature-derived` | PMT fluorescence state discrimination |
| `dephasing_rate` | $0.0002$ | `literature-derived` | Residual magnetic fluctuations & laser phase noise |
| `depolarizing_rate` | $0.0008$ | `literature-derived` | Motional heating & off-resonant scattering |
| `loss_rate` | $0.0001$ | `assumed` | Dark state leakage / ion loss probability |
| `bell_pair_fidelity` | $0.9920$ | `experimentally configured` | Teleportation entangled pair resource fidelity |

### 2.3 Backend Engine
* Executed via **Qiskit Aer** (`AerSimulator`) configuring `NoiseModel` with thermal relaxation, depolarizing channels, and assignment readout error matrices.

---

## 3. Secondary Hardware Model: Rydberg / Neutral-Atom Profile

### 3.1 Physical Alignment & Rydberg Blockade
* **Physical System:** Optical tweezer arrays of neutral alkali atoms (such as $^{87}\text{Rb}$) trapped in high-vacuum glass cells.
* **Qubit Representation:** Ground hyperfine states $|0\rangle \equiv |5S_{1/2}, F=1\rangle$ and $|1\rangle \equiv |5S_{1/2}, F=2\rangle$.
* **Rydberg Blockade Interaction:** Two atoms excited to high-principal-quantum-number Rydberg states ($n \ge 70$) experience strong van der Waals interaction:
  $$U_{\text{vdW}}(R) = \frac{C_6}{R^6}$$
  When atom separation $R < R_b$ (the blockade radius), simultaneous double excitation is strongly suppressed, enabling controlled-phase entangling gates.

### 3.2 Profile Parameters (`profiles/rydberg.yaml`)

| Parameter | Value | Provenance | Physical Description |
| :--- | :--- | :--- | :--- |
| `one_qubit_gate_error` | $0.0020$ (99.80% fidelity) | `literature-derived` | Two-photon Raman transition Rabi pulses |
| `two_qubit_gate_error` | $0.0150$ (98.50% fidelity) | `literature-derived` | Rydberg blockade entangling pulse sequence |
| `readout_error` | $0.0120$ (1.20%) | `literature-derived` | Fluorescence imaging and optical trap loss |
| `dephasing_rate` | $0.0030$ | `literature-derived` | Doppler broadening and laser phase fluctuations ($T_2^* \sim 20\,\mu\text{s}$) |
| `depolarizing_rate` | $0.0040$ | `literature-derived` | Spontaneous emission from intermediate states |
| `loss_rate` | $0.0050$ | `experimentally configured` | Background gas collisions & tweezer atom ejection |
| `bell_pair_fidelity` | $0.9780$ | `experimentally configured` | Neutral-atom entanglement via Rydberg sequences |

### 3.3 Backend Engine
* Executed via **Pulser** (`PulserBackend`) integrating neutral-atom Lindblad and pulse sequence dynamics.
