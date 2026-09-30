"""
Bell States and Entanglement Module
Mathematical representations of the four Bell states (Phi+, Phi-, Psi+, Psi-),
Werner-state generation for noise modeling, and CHSH inequality evaluation.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, Any, Tuple, Optional
import numpy as np

from teleshield.quantum.pauli import PAULI_I, PAULI_X, PAULI_Y, PAULI_Z

_INV_SQRT2 = 1.0 / np.sqrt(2.0)

# Four Bell statevectors in standard computational basis |00>, |01>, |10>, |11>
PHI_PLUS_VEC = _INV_SQRT2 * np.array([1.0, 0.0, 0.0, 1.0], dtype=np.complex128)
PHI_MINUS_VEC = _INV_SQRT2 * np.array([1.0, 0.0, 0.0, -1.0], dtype=np.complex128)
PSI_PLUS_VEC = _INV_SQRT2 * np.array([0.0, 1.0, 1.0, 0.0], dtype=np.complex128)
PSI_MINUS_VEC = _INV_SQRT2 * np.array([0.0, 1.0, -1.0, 0.0], dtype=np.complex128)


class BellState(str, Enum):
    PHI_PLUS = "Phi+"
    PHI_MINUS = "Phi-"
    PSI_PLUS = "Psi+"
    PSI_MINUS = "Psi-"


BELL_VECTORS: Dict[BellState, np.ndarray] = {
    BellState.PHI_PLUS: PHI_PLUS_VEC,
    BellState.PHI_MINUS: PHI_MINUS_VEC,
    BellState.PSI_PLUS: PSI_PLUS_VEC,
    BellState.PSI_MINUS: PSI_MINUS_VEC,
}


class BellPair:
    """
    Represents an entangled two-qubit Bell pair.
    Can be pure or mixed (e.g. Werner state with visibility V).
    """

    def __init__(
        self,
        bell_type: BellState = BellState.PHI_PLUS,
        density_matrix: Optional[np.ndarray] = None,
        visibility: float = 1.0,
    ) -> None:
        self.bell_type = bell_type
        self.visibility = max(0.0, min(1.0, float(visibility)))

        if density_matrix is not None:
            dm = np.array(density_matrix, dtype=np.complex128)
            if dm.shape != (4, 4):
                raise ValueError("Two-qubit density matrix must have shape (4, 4)")
            self._rho = (dm + dm.conj().T) / 2.0
            tr = np.trace(self._rho)
            if abs(tr) > 1e-12:
                self._rho = self._rho / tr
            self._vector = None
        else:
            pure_vec = BELL_VECTORS[bell_type]
            pure_rho = np.outer(pure_vec, pure_vec.conj())
            if abs(self.visibility - 1.0) < 1e-9:
                self._vector = pure_vec.copy()
                self._rho = pure_rho
            else:
                # Werner state mixture: rho_W = V |Phi><Phi| + (1-V)/4 * I_4
                i4 = np.eye(4, dtype=np.complex128)
                self._rho = self.visibility * pure_rho + (1.0 - self.visibility) / 4.0 * i4
                self._vector = None

    @property
    def density_matrix(self) -> np.ndarray:
        return self._rho.copy()

    @property
    def vector(self) -> Optional[np.ndarray]:
        return self._vector.copy() if self._vector is not None else None

    @property
    def is_pure(self) -> bool:
        purity = float(np.real(np.trace(self._rho @ self._rho)))
        return abs(purity - 1.0) < 1e-6

    def fidelity_with_ideal(self) -> float:
        """Fidelity with ideal pure state of same Bell type."""
        ideal_v = BELL_VECTORS[self.bell_type]
        fid = float(np.real(np.vdot(ideal_v, self._rho @ ideal_v)))
        return min(1.0, max(0.0, fid))

    def chsh_value(self) -> float:
        """
        Evaluate CHSH S parameter: S = <A1 B1> + <A1 B2> + <A2 B1> - <A2 B2>.
        Optimal angles:
          A1 = Z, A2 = X
          B1 = (Z + X)/sqrt(2), B2 = (Z - X)/sqrt(2)
        For pure Phi+, S = 2 * sqrt(2) ~ 2.8284.
        For Werner state, S = 2 * sqrt(2) * V.
        """
        return compute_chsh_s(self._rho)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bell_type": self.bell_type.value,
            "visibility": self.visibility,
            "fidelity": self.fidelity_with_ideal(),
            "chsh_s": self.chsh_value(),
            "is_pure": self.is_pure,
            "violates_classical": self.chsh_value() > 2.0,
        }


def create_bell_pair(
    bell_type: BellState = BellState.PHI_PLUS,
    visibility: float = 1.0,
) -> BellPair:
    """Create a BellPair instance with given type and visibility."""
    return BellPair(bell_type=bell_type, visibility=visibility)


def compute_werner_state(visibility: float, bell_type: BellState = BellState.PHI_PLUS) -> np.ndarray:
    """Generate Werner state density matrix: V |Bell><Bell| + (1-V)/4 * I_4."""
    V = max(0.0, min(1.0, float(visibility)))
    v = BELL_VECTORS[bell_type]
    pure_dm = np.outer(v, v.conj())
    i4 = np.eye(4, dtype=np.complex128)
    return V * pure_dm + (1.0 - V) / 4.0 * i4


def compute_chsh_s(density_matrix: np.ndarray) -> float:
    """
    Compute CHSH S expectation value from two-qubit density matrix.
    Operators:
      A1 = Z
      A2 = X
      B1 = (Z + X) / sqrt(2)
      B2 = (Z - X) / sqrt(2)
    """
    a1 = PAULI_Z
    a2 = PAULI_X
    b1 = _INV_SQRT2 * (PAULI_Z + PAULI_X)
    b2 = _INV_SQRT2 * (PAULI_Z - PAULI_X)

    # Tensor products A \otimes B
    m_a1_b1 = np.kron(a1, b1)
    m_a1_b2 = np.kron(a1, b2)
    m_a2_b1 = np.kron(a2, b1)
    m_a2_b2 = np.kron(a2, b2)

    e11 = float(np.real(np.trace(density_matrix @ m_a1_b1)))
    e12 = float(np.real(np.trace(density_matrix @ m_a1_b2)))
    e21 = float(np.real(np.trace(density_matrix @ m_a2_b1)))
    e22 = float(np.real(np.trace(density_matrix @ m_a2_b2)))

    s = e11 + e12 + e21 - e22
    return float(s)
