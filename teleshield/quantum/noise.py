"""
Quantum Noise Module
Unified noise interface supporting bit flip, phase flip, bit-phase flip,
depolarizing, dephasing, amplitude damping, measurement/readout errors,
gate errors, memory decay, and loss.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import numpy as np

from teleshield.quantum.states import QuantumState
from teleshield.quantum.pauli import PAULI_X, PAULI_Y, PAULI_Z


class NoiseType(str, Enum):
    NONE = "none"
    BIT_FLIP = "bit_flip"
    PHASE_FLIP = "phase_flip"
    BIT_PHASE_FLIP = "bit_phase_flip"
    DEPOLARIZING = "depolarizing"
    DEPHASING = "dephasing"
    AMPLITUDE_DAMPING = "amplitude_damping"
    READOUT = "readout"
    COMPOSITE = "composite"


@dataclass
class NoiseModelConfig:
    """Configuration for all quantum channel and operational noise parameters."""

    noise_type: NoiseType = NoiseType.NONE
    probability: float = 0.0
    bit_flip_rate: float = 0.0
    phase_flip_rate: float = 0.0
    depolarizing_rate: float = 0.0
    dephasing_rate: float = 0.0
    amplitude_damping_gamma: float = 0.0
    readout_error: float = 0.0
    one_qubit_gate_error: float = 0.0
    two_qubit_gate_error: float = 0.0
    loss_rate: float = 0.0
    t1_time_us: float = 1e6
    t2_time_us: float = 1e5
    idle_time_us: float = 0.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NoiseModelConfig":
        nt = data.get("noise_type") or data.get("type", "none")
        try:
            noise_type = NoiseType(str(nt).lower())
        except ValueError:
            noise_type = NoiseType.NONE

        return cls(
            noise_type=noise_type,
            probability=float(data.get("probability", 0.0)),
            bit_flip_rate=float(data.get("bit_flip_rate", 0.0)),
            phase_flip_rate=float(data.get("phase_flip_rate", 0.0)),
            depolarizing_rate=float(data.get("depolarizing_rate", 0.0)),
            dephasing_rate=float(data.get("dephasing_rate", 0.0)),
            amplitude_damping_gamma=float(data.get("amplitude_damping_gamma", 0.0)),
            readout_error=float(data.get("readout_error", 0.0)),
            one_qubit_gate_error=float(data.get("one_qubit_gate_error", 0.0)),
            two_qubit_gate_error=float(data.get("two_qubit_gate_error", 0.0)),
            loss_rate=float(data.get("loss_rate", 0.0)),
            t1_time_us=float(data.get("t1_time_us", 1e6)),
            t2_time_us=float(data.get("t2_time_us", 1e5)),
            idle_time_us=float(data.get("idle_time_us", 0.0)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "noise_type": self.noise_type.value,
            "probability": self.probability,
            "bit_flip_rate": self.bit_flip_rate,
            "phase_flip_rate": self.phase_flip_rate,
            "depolarizing_rate": self.depolarizing_rate,
            "dephasing_rate": self.dephasing_rate,
            "amplitude_damping_gamma": self.amplitude_damping_gamma,
            "readout_error": self.readout_error,
            "one_qubit_gate_error": self.one_qubit_gate_error,
            "two_qubit_gate_error": self.two_qubit_gate_error,
            "loss_rate": self.loss_rate,
            "t1_time_us": self.t1_time_us,
            "t2_time_us": self.t2_time_us,
            "idle_time_us": self.idle_time_us,
        }


def apply_depolarizing_channel(rho: np.ndarray, p: float) -> np.ndarray:
    """rho -> (1 - p) * rho + (p / 3) * (X rho X + Y rho Y + Z rho Z)."""
    p = max(0.0, min(1.0, float(p)))
    if p <= 1e-12:
        return rho.copy()
    term_x = PAULI_X @ rho @ PAULI_X
    term_y = PAULI_Y @ rho @ PAULI_Y
    term_z = PAULI_Z @ rho @ PAULI_Z
    return (1.0 - p) * rho + (p / 3.0) * (term_x + term_y + term_z)


def apply_dephasing_channel(rho: np.ndarray, p: float) -> np.ndarray:
    """rho -> (1 - p) * rho + p * (Z rho Z)."""
    p = max(0.0, min(1.0, float(p)))
    if p <= 1e-12:
        return rho.copy()
    term_z = PAULI_Z @ rho @ PAULI_Z
    return (1.0 - p) * rho + p * term_z


def apply_bit_flip_channel(rho: np.ndarray, p: float) -> np.ndarray:
    """rho -> (1 - p) * rho + p * (X rho X)."""
    p = max(0.0, min(1.0, float(p)))
    if p <= 1e-12:
        return rho.copy()
    term_x = PAULI_X @ rho @ PAULI_X
    return (1.0 - p) * rho + p * term_x


def apply_bit_phase_flip_channel(rho: np.ndarray, p: float) -> np.ndarray:
    """rho -> (1 - p) * rho + p * (Y rho Y)."""
    p = max(0.0, min(1.0, float(p)))
    if p <= 1e-12:
        return rho.copy()
    term_y = PAULI_Y @ rho @ PAULI_Y
    return (1.0 - p) * rho + p * term_y


def apply_amplitude_damping_channel(rho: np.ndarray, gamma: float) -> np.ndarray:
    """
    Kraus operators for amplitude damping:
    E0 = [[1, 0], [0, sqrt(1-gamma)]]
    E1 = [[0, sqrt(gamma)], [0, 0]]
    """
    gamma = max(0.0, min(1.0, float(gamma)))
    if gamma <= 1e-12:
        return rho.copy()
    e0 = np.array([[1.0, 0.0], [0.0, np.sqrt(1.0 - gamma)]], dtype=np.complex128)
    e1 = np.array([[0.0, np.sqrt(gamma)], [0.0, 0.0]], dtype=np.complex128)
    return e0 @ rho @ e0.conj().T + e1 @ rho @ e1.conj().T


def apply_quantum_noise(state: QuantumState, config: NoiseModelConfig) -> QuantumState:
    """
    Apply configured physical noise channels to a QuantumState.
    Returns new QuantumState with resulting density matrix.
    """
    rho = state.density_matrix

    # If simple noise type is chosen with overall probability
    if config.noise_type == NoiseType.DEPOLARIZING:
        rate = config.depolarizing_rate or config.probability
        rho = apply_depolarizing_channel(rho, rate)
    elif config.noise_type == NoiseType.DEPHASING or config.noise_type == NoiseType.PHASE_FLIP:
        rate = config.dephasing_rate or config.phase_flip_rate or config.probability
        rho = apply_dephasing_channel(rho, rate)
    elif config.noise_type == NoiseType.BIT_FLIP:
        rate = config.bit_flip_rate or config.probability
        rho = apply_bit_flip_channel(rho, rate)
    elif config.noise_type == NoiseType.BIT_PHASE_FLIP:
        rate = config.probability
        rho = apply_bit_phase_flip_channel(rho, rate)
    elif config.noise_type == NoiseType.AMPLITUDE_DAMPING:
        gamma = config.amplitude_damping_gamma or config.probability
        rho = apply_amplitude_damping_channel(rho, gamma)
    elif config.noise_type == NoiseType.COMPOSITE or config.noise_type == NoiseType.NONE:
        # Multi-parameter composite channel
        if config.depolarizing_rate > 0:
            rho = apply_depolarizing_channel(rho, config.depolarizing_rate)
        if config.dephasing_rate > 0:
            rho = apply_dephasing_channel(rho, config.dephasing_rate)
        if config.bit_flip_rate > 0:
            rho = apply_bit_flip_channel(rho, config.bit_flip_rate)
        if config.phase_flip_rate > 0:
            rho = apply_dephasing_channel(rho, config.phase_flip_rate)
        if config.amplitude_damping_gamma > 0:
            rho = apply_amplitude_damping_channel(rho, config.amplitude_damping_gamma)

    # Idle time T1 / T2 relaxation if specified
    if config.idle_time_us > 0 and config.t1_time_us > 0:
        gamma_t1 = 1.0 - np.exp(-config.idle_time_us / config.t1_time_us)
        rho = apply_amplitude_damping_channel(rho, gamma_t1)
    if config.idle_time_us > 0 and config.t2_time_us > 0:
        lambda_t2 = 0.5 * (1.0 - np.exp(-config.idle_time_us / config.t2_time_us))
        rho = apply_dephasing_channel(rho, lambda_t2)

    # Clean density matrix (Hermitian, unit trace)
    rho = (rho + rho.conj().T) / 2.0
    tr = np.trace(rho)
    if abs(tr) > 1e-12:
        rho = rho / tr

    return QuantumState(
        density_matrix=rho,
        basis=state.basis,
        eigenvalue=state.eigenvalue,
        label=state.label,
    )
