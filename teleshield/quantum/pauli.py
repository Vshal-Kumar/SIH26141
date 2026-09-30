"""
Pauli Operators Module
Mathematical representation and application of Pauli operators (I, X, Y, Z),
basis rotation operators (Hadamard, S), eigenvalue calculations, and
teleportation correction operations (X^{m1} Z^{m0}).
"""

from __future__ import annotations
from typing import Dict, Tuple, Union, Optional
import numpy as np

from teleshield.quantum.states import QuantumState, StateBasis, Eigenvalue

# Standard 2x2 Pauli matrices
PAULI_I = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.complex128)
PAULI_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
PAULI_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=np.complex128)
PAULI_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)

_INV_SQRT2 = 1.0 / np.sqrt(2.0)
HADAMARD = _INV_SQRT2 * np.array([[1.0, 1.0], [1.0, -1.0]], dtype=np.complex128)
S_GATE = np.array([[1.0, 0.0], [0.0, 1.0j]], dtype=np.complex128)
S_DAGGER = np.array([[1.0, 0.0], [0.0, -1.0j]], dtype=np.complex128)

PAULI_DICT: Dict[str, np.ndarray] = {
    "I": PAULI_I,
    "X": PAULI_X,
    "Y": PAULI_Y,
    "Z": PAULI_Z,
}


def get_pauli_matrix(name: str) -> np.ndarray:
    """Return 2x2 complex numpy array for given Pauli operator name."""
    op_name = name.strip().upper()
    if op_name not in PAULI_DICT:
        raise ValueError(f"Unknown Pauli operator '{name}'. Supported: I, X, Y, Z")
    return PAULI_DICT[op_name].copy()


def apply_operator(state: QuantumState, operator: np.ndarray) -> QuantumState:
    """
    Apply a 2x2 unitary or general Kraus operator to a QuantumState.
    Supports pure states (vector) and mixed states (density matrix).
    """
    if operator.shape != (2, 2):
        raise ValueError("Operator must be a 2x2 matrix")

    if state.vector is not None:
        new_vec = operator @ state.vector
        norm = np.linalg.norm(new_vec)
        if norm > 1e-12:
            new_vec = new_vec / norm
        return QuantumState(vector=new_vec)
    else:
        new_rho = operator @ state.density_matrix @ operator.conj().T
        tr = np.trace(new_rho)
        if abs(tr) > 1e-12:
            new_rho = new_rho / tr
        return QuantumState(density_matrix=new_rho)


def apply_pauli(state: QuantumState, pauli_name: str) -> QuantumState:
    """Apply Pauli operator (I, X, Y, Z) to state."""
    mat = get_pauli_matrix(pauli_name)
    return apply_operator(state, mat)


def get_correction_operator(m0: int, m1: int) -> Tuple[str, np.ndarray]:
    """
    Compute Bob's Pauli correction operator for standard quantum teleportation.
    Alice measures input qubit (m0) and Alice's Bell half (m1).
    Bob applies: U = X^{m1} Z^{m0}.

    m0=0, m1=0 -> I
    m0=0, m1=1 -> X
    m0=1, m1=0 -> Z
    m0=1, m1=1 -> XZ (equivalent to -i Y)
    """
    m0 = int(m0) % 2
    m1 = int(m1) % 2

    if m0 == 0 and m1 == 0:
        return ("I", PAULI_I.copy())
    elif m0 == 0 and m1 == 1:
        return ("X", PAULI_X.copy())
    elif m0 == 1 and m1 == 0:
        return ("Z", PAULI_Z.copy())
    else:
        # X @ Z
        op = PAULI_X @ PAULI_Z
        return ("XZ", op)


def rotate_to_z(state: QuantumState, basis: Union[StateBasis, str]) -> QuantumState:
    """
    Rotate a state measured in 'basis' into the computational Z basis
    so standard projective Z measurement |0><0|, |1><1| can be applied.
    Z basis: Identity (already in Z)
    X basis: Hadamard H (maps |+> -> |0>, |-> -> |1>)
    Y basis: H @ S_DAGGER (maps |+y> -> |0>, |-y> -> |1>)
    """
    b = basis if isinstance(basis, StateBasis) else StateBasis(str(basis).split(".")[-1].strip().upper())
    if b == StateBasis.Z:
        return state.copy()
    elif b == StateBasis.X:
        return apply_operator(state, HADAMARD)
    elif b == StateBasis.Y:
        rot = HADAMARD @ S_DAGGER
        return apply_operator(state, rot)
    raise ValueError(f"Unsupported measurement basis: {basis}")


def rotate_from_z(state: QuantumState, basis: Union[StateBasis, str]) -> QuantumState:
    """Inverse of rotate_to_z. Prepares state in target basis from Z."""
    b = basis if isinstance(basis, StateBasis) else StateBasis(str(basis).split(".")[-1].strip().upper())
    if b == StateBasis.Z:
        return state.copy()
    elif b == StateBasis.X:
        return apply_operator(state, HADAMARD)
    elif b == StateBasis.Y:
        rot = S_GATE @ HADAMARD
        return apply_operator(state, rot)
    raise ValueError(f"Unsupported preparation basis: {basis}")


def compute_pauli_expectation(state: QuantumState, pauli_name: str) -> float:
    """Compute expectation value <pauli> = Tr(rho * P)."""
    p_mat = get_pauli_matrix(pauli_name)
    val = np.real(np.trace(state.density_matrix @ p_mat))
    return float(val)
