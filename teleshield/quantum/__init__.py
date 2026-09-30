"""
TeleShield Quantum Layer
Core quantum mathematical primitives, states, operators, Bell pairs, teleportation, measurement, and noise models.
"""

from teleshield.quantum.states import QuantumState, StateBasis, Eigenvalue
from teleshield.quantum.pauli import (
    PAULI_I, PAULI_X, PAULI_Y, PAULI_Z,
    HADAMARD, S_GATE,
    apply_pauli, get_correction_operator, rotate_to_z
)
from teleshield.quantum.bell import (
    BellState, BellPair, create_bell_pair,
    compute_werner_state, compute_chsh_s
)
from teleshield.quantum.teleportation import (
    TeleportationResult, teleport_state
)
from teleshield.quantum.measurement import (
    MeasurementResult, measure_state, measure_state_projective
)
from teleshield.quantum.noise import (
    NoiseModelConfig, apply_quantum_noise
)

__all__ = [
    "QuantumState",
    "StateBasis",
    "Eigenvalue",
    "PAULI_I",
    "PAULI_X",
    "PAULI_Y",
    "PAULI_Z",
    "HADAMARD",
    "S_GATE",
    "apply_pauli",
    "get_correction_operator",
    "rotate_to_z",
    "BellState",
    "BellPair",
    "create_bell_pair",
    "compute_werner_state",
    "compute_chsh_s",
    "TeleportationResult",
    "teleport_state",
    "MeasurementResult",
    "measure_state",
    "measure_state_projective",
    "NoiseModelConfig",
    "apply_quantum_noise",
]
