"""
Quantum States Module
Mathematical representation of single-qubit quantum states, density matrices,
Pauli eigenstates in Z, X, and Y bases, fidelity calculations, and Bloch coordinates.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, Any, Optional, Tuple, Union
import numpy as np


class StateBasis(str, Enum):
    Z = "Z"
    X = "X"
    Y = "Y"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            clean = value.split(".")[-1].strip().upper()
            for member in cls:
                if member.value == clean or member.name == clean:
                    return member
        return None

    @classmethod
    def from_str(cls, val: Union["StateBasis", str]) -> "StateBasis":
        if isinstance(val, cls):
            return val
        clean = str(val).split(".")[-1].strip().upper()
        return cls(clean)


class Eigenvalue(int, Enum):
    PLUS = 1
    MINUS = -1

    @classmethod
    def from_str(cls, val: Union[str, int]) -> "Eigenvalue":
        if isinstance(val, int):
            return cls.PLUS if val >= 0 else cls.MINUS
        val_str = str(val).strip()
        if val_str in ("+1", "1", "+", "PLUS"):
            return cls.PLUS
        elif val_str in ("-1", "-", "MINUS"):
            return cls.MINUS
        raise ValueError(f"Invalid eigenvalue representation: {val}")

    def to_display(self) -> str:
        return "+1" if self == Eigenvalue.PLUS else "-1"


# Canonical single-qubit basis vectors
_INV_SQRT2 = 1.0 / np.sqrt(2.0)

STATE_0_VEC = np.array([1.0, 0.0], dtype=np.complex128)
STATE_1_VEC = np.array([0.0, 1.0], dtype=np.complex128)
STATE_PLUS_VEC = _INV_SQRT2 * np.array([1.0, 1.0], dtype=np.complex128)
STATE_MINUS_VEC = _INV_SQRT2 * np.array([1.0, -1.0], dtype=np.complex128)
STATE_PLUS_Y_VEC = _INV_SQRT2 * np.array([1.0, 1.0j], dtype=np.complex128)
STATE_MINUS_Y_VEC = _INV_SQRT2 * np.array([1.0, -1.0j], dtype=np.complex128)


class QuantumState:
    """
    Represents a pure or mixed single-qubit quantum state.
    Provides rigorous state vector and density matrix representations,
    fidelity computation, Bloch sphere projection, and basis metadata.
    """

    def __init__(
        self,
        vector: Optional[np.ndarray] = None,
        density_matrix: Optional[np.ndarray] = None,
        basis: Optional[StateBasis] = None,
        eigenvalue: Optional[Eigenvalue] = None,
        label: Optional[str] = None,
    ) -> None:
        if density_matrix is not None:
            self._rho = np.array(density_matrix, dtype=np.complex128)
            if self._rho.shape != (2, 2):
                raise ValueError("Density matrix must have shape (2, 2)")
            # Enforce Hermiticity and unit trace
            self._rho = (self._rho + self._rho.conj().T) / 2.0
            tr = np.trace(self._rho)
            if abs(tr) > 1e-12:
                self._rho = self._rho / tr
            if vector is not None:
                v = np.array(vector, dtype=np.complex128).flatten()
                norm = np.linalg.norm(v)
                self._vector = (v / norm).copy() if norm > 1e-12 else None
            else:
                purity = float(np.real(np.trace(self._rho @ self._rho)))
                if abs(purity - 1.0) < 1e-5:
                    w, v = np.linalg.eigh(self._rho)
                    vec = v[:, -1]
                    first_idx = 0 if abs(vec[0]) > 1e-7 else 1
                    phase = np.exp(-1j * np.angle(vec[first_idx]))
                    self._vector = (vec * phase).copy()
                else:
                    self._vector = None
        elif vector is not None:
            v = np.array(vector, dtype=np.complex128).flatten()
            if v.shape != (2,):
                raise ValueError("State vector must have shape (2,)")
            norm = np.linalg.norm(v)
            if norm < 1e-12:
                raise ValueError("Cannot normalize a zero state vector")
            self._vector = v / norm
            self._rho = np.outer(self._vector, self._vector.conj())
        else:
            # Default to |0>
            self._vector = STATE_0_VEC.copy()
            self._rho = np.outer(self._vector, self._vector.conj())

        self.basis = basis
        self.eigenvalue = eigenvalue
        self.label = label or self._infer_label()

    @property
    def vector(self) -> Optional[np.ndarray]:
        return self._vector.copy() if self._vector is not None else None

    @property
    def density_matrix(self) -> np.ndarray:
        return self._rho.copy()

    @property
    def is_pure(self) -> bool:
        purity = float(np.real(np.trace(self._rho @ self._rho)))
        return abs(purity - 1.0) < 1e-6

    def _infer_label(self) -> str:
        if self.basis is not None and self.eigenvalue is not None:
            ev_str = "+" if self.eigenvalue == Eigenvalue.PLUS else "-"
            if self.basis == StateBasis.Z:
                return "|0>" if self.eigenvalue == Eigenvalue.PLUS else "|1>"
            elif self.basis == StateBasis.X:
                return f"|{ev_str}>"
            elif self.basis == StateBasis.Y:
                return f"|{ev_str}y>"
        return "custom"

    @classmethod
    def zero(cls) -> "QuantumState":
        return cls(vector=STATE_0_VEC, basis=StateBasis.Z, eigenvalue=Eigenvalue.PLUS, label="|0>")

    @classmethod
    def one(cls) -> "QuantumState":
        return cls(vector=STATE_1_VEC, basis=StateBasis.Z, eigenvalue=Eigenvalue.MINUS, label="|1>")

    @classmethod
    def plus(cls) -> "QuantumState":
        return cls(vector=STATE_PLUS_VEC, basis=StateBasis.X, eigenvalue=Eigenvalue.PLUS, label="|+>")

    @classmethod
    def minus(cls) -> "QuantumState":
        return cls(vector=STATE_MINUS_VEC, basis=StateBasis.X, eigenvalue=Eigenvalue.MINUS, label="|->")

    @classmethod
    def plus_y(cls) -> "QuantumState":
        return cls(vector=STATE_PLUS_Y_VEC, basis=StateBasis.Y, eigenvalue=Eigenvalue.PLUS, label="|+y>")

    @classmethod
    def minus_y(cls) -> "QuantumState":
        return cls(vector=STATE_MINUS_Y_VEC, basis=StateBasis.Y, eigenvalue=Eigenvalue.MINUS, label="|-y>")

    @classmethod
    def from_basis_and_eigenvalue(
        cls, basis: Union[StateBasis, str], eigenvalue: Union[Eigenvalue, int, str]
    ) -> "QuantumState":
        if isinstance(basis, StateBasis):
            b = basis
        else:
            val = str(basis).split(".")[-1].strip().upper()
            b = StateBasis(val)

        if isinstance(eigenvalue, Eigenvalue):
            ev = eigenvalue
        else:
            ev = Eigenvalue.from_str(eigenvalue)

        if b == StateBasis.Z:
            return cls.zero() if ev == Eigenvalue.PLUS else cls.one()
        elif b == StateBasis.X:
            return cls.plus() if ev == Eigenvalue.PLUS else cls.minus()
        elif b == StateBasis.Y:
            return cls.plus_y() if ev == Eigenvalue.PLUS else cls.minus_y()
        raise ValueError(f"Unsupported basis: {basis}")

    @classmethod
    def from_bloch(cls, rx: float, ry: float, rz: float) -> "QuantumState":
        norm_r = np.sqrt(rx * rx + ry * ry + rz * rz)
        if norm_r > 1.0 + 1e-9:
            # Rescale to surface of sphere if slight numerical excess
            rx, ry, rz = rx / norm_r, ry / norm_r, rz / norm_r
        # rho = 1/2 (I + rx*X + ry*Y + rz*Z)
        rho = 0.5 * np.array(
            [[1.0 + rz, rx - 1.0j * ry], [rx + 1.0j * ry, 1.0 - rz]],
            dtype=np.complex128,
        )
        return cls(density_matrix=rho)

    def fidelity(self, target: "QuantumState") -> float:
        """
        Compute fidelity between self and target state.
        For pure states: F = |<psi|phi>|^2.
        For general states: F = (Tr(sqrt(sqrt(rho) sigma sqrt(rho))))^2.
        When target is pure (target._vector is not None): F = <target|rho|target>.
        """
        if self._vector is not None and target._vector is not None:
            overlap = np.vdot(target._vector, self._vector)
            return float(np.abs(overlap) ** 2)
        elif target._vector is not None:
            # Target is pure, self may be mixed
            v = target._vector
            return float(np.real(np.vdot(v, self._rho @ v)))
        elif self._vector is not None:
            v = self._vector
            return float(np.real(np.vdot(v, target._rho @ v)))
        else:
            # General mixed state fidelity via matrix square root
            from scipy.linalg import sqrtm
            rho_sqrt = sqrtm(self._rho)
            inner = rho_sqrt @ target._rho @ rho_sqrt
            inner_sqrt = sqrtm(inner)
            fid = float(np.real(np.trace(inner_sqrt)) ** 2)
            return min(1.0, max(0.0, fid))

    def bloch_coordinates(self) -> Tuple[float, float, float]:
        """
        Compute Bloch sphere vector (rx, ry, rz) from density matrix.
        rx = Tr(rho X), ry = Tr(rho Y), rz = Tr(rho Z)
        """
        rx = float(np.real(self._rho[0, 1] + self._rho[1, 0]))
        ry = float(np.real(1.0j * (self._rho[0, 1] - self._rho[1, 0])))
        rz = float(np.real(self._rho[0, 0] - self._rho[1, 1]))
        return (rx, ry, rz)

    def to_dict(self) -> Dict[str, Any]:
        rx, ry, rz = self.bloch_coordinates()
        return {
            "label": self.label,
            "basis": self.basis.value if self.basis else None,
            "eigenvalue": self.eigenvalue.value if self.eigenvalue else None,
            "is_pure": self.is_pure,
            "bloch": {"x": rx, "y": ry, "z": rz},
        }

    def copy(self) -> "QuantumState":
        if self._vector is not None:
            return QuantumState(
                vector=self._vector.copy(),
                basis=self.basis,
                eigenvalue=self.eigenvalue,
                label=self.label,
            )
        return QuantumState(
            density_matrix=self._rho.copy(),
            basis=self.basis,
            eigenvalue=self.eigenvalue,
            label=self.label,
        )

    def __repr__(self) -> str:
        b_str = f", basis={self.basis.value}" if self.basis else ""
        ev_str = f", ev={self.eigenvalue.to_display()}" if self.eigenvalue else ""
        return f"QuantumState({self.label}{b_str}{ev_str})"
