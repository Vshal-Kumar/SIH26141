"""
Quantum Measurement Module
Implementation of projective measurements in Z, X, and Y bases,
eigenvalue matching against declared private keys, shot statistics,
and measurement error modeling.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, Union
import numpy as np

from teleshield.quantum.states import QuantumState, StateBasis, Eigenvalue
from teleshield.quantum.pauli import rotate_to_z


class MeasurementResult:
    """Encapsulates the complete outcome and statistical evidence of a quantum measurement."""

    def __init__(
        self,
        basis: StateBasis,
        expected_eigenvalue: Eigenvalue,
        observed_eigenvalue: Eigenvalue,
        raw_result: int,  # 0 -> +1, 1 -> -1
        shots: int,
        matches: int,
        mismatches: int,
        mismatch_rate: float,
        p_plus: float,
        p_minus: float,
    ) -> None:
        self.basis = basis
        self.expected_eigenvalue = expected_eigenvalue
        self.observed_eigenvalue = observed_eigenvalue
        self.raw_result = raw_result
        self.shots = shots
        self.matches = matches
        self.mismatches = mismatches
        self.mismatch_rate = float(mismatch_rate)
        self.p_plus = float(p_plus)
        self.p_minus = float(p_minus)

    @property
    def is_match(self) -> bool:
        return self.expected_eigenvalue == self.observed_eigenvalue

    def to_dict(self) -> Dict[str, Any]:
        return {
            "basis": self.basis.value,
            "expected_eigenvalue": self.expected_eigenvalue.value,
            "observed_eigenvalue": self.observed_eigenvalue.value,
            "raw_result": self.raw_result,
            "shots": self.shots,
            "matches": self.matches,
            "mismatches": self.mismatches,
            "mismatch_rate": self.mismatch_rate,
            "probabilities": {
                "+1": self.p_plus,
                "-1": self.p_minus,
            },
        }

    def __repr__(self) -> str:
        return (
            f"MeasurementResult(basis={self.basis.value}, exp={self.expected_eigenvalue.to_display()}, "
            f"obs={self.observed_eigenvalue.to_display()}, mismatches={self.mismatches}/{self.shots} "
            f"({self.mismatch_rate:.4f}))"
        )


def measure_state_projective(
    state: QuantumState,
    basis: StateBasis,
    expected_eigenvalue: Optional[Eigenvalue] = None,
    shots: int = 1,
    readout_error: float = 0.0,
    seed: Optional[int] = None,
) -> MeasurementResult:
    """
    Perform projective measurement on quantum state in requested basis (Z, X, or Y).
    Calculates exact Born rule probabilities, samples shots, incorporates readout error,
    and returns comprehensive match/mismatch statistics.
    """
    rng = np.random.default_rng(seed)
    readout_err = max(0.0, min(1.0, float(readout_error)))

    # Rotate state to Z computational basis
    z_rotated = rotate_to_z(state, basis)
    rho_z = z_rotated.density_matrix

    # Probabilities in computational basis: |0> corresponds to +1, |1> to -1
    p0 = float(np.real(rho_z[0, 0]))  # prob of +1
    p1 = float(np.real(rho_z[1, 1]))  # prob of -1

    # Clamp to [0, 1]
    p0 = max(0.0, min(1.0, p0))
    p1 = max(0.0, min(1.0, p1))
    s = p0 + p1
    if s > 0:
        p0, p1 = p0 / s, p1 / s
    else:
        p0, p1 = 0.5, 0.5

    # Apply readout error: p(0_obs) = (1 - ro)*p0 + ro*p1
    p0_meas = (1.0 - readout_err) * p0 + readout_err * p1
    p1_meas = 1.0 - p0_meas

    # Sample shots
    if shots <= 1:
        raw_bit = 0 if rng.random() < p0_meas else 1
        num_zeros = 1 if raw_bit == 0 else 0
        num_ones = 1 - num_zeros
    else:
        num_zeros = int(rng.binomial(shots, p0_meas))
        num_ones = shots - num_zeros
        # Primary observed bit is majority vote
        raw_bit = 0 if num_zeros >= num_ones else 1

    obs_ev = Eigenvalue.PLUS if raw_bit == 0 else Eigenvalue.MINUS

    # If no expected eigenvalue is supplied, use state's own or default to PLUS
    if expected_eigenvalue is None:
        expected_eigenvalue = state.eigenvalue or Eigenvalue.PLUS

    # In single/multi-shot:
    # Outcome 0 (+1 eigenvalue) matches PLUS; outcome 1 (-1 eigenvalue) matches MINUS
    if expected_eigenvalue == Eigenvalue.PLUS:
        matches = num_zeros
        mismatches = num_ones
    else:
        matches = num_ones
        mismatches = num_zeros

    mismatch_rate = float(mismatches) / float(max(1, shots))

    return MeasurementResult(
        basis=basis,
        expected_eigenvalue=expected_eigenvalue,
        observed_eigenvalue=obs_ev,
        raw_result=raw_bit,
        shots=shots,
        matches=matches,
        mismatches=mismatches,
        mismatch_rate=mismatch_rate,
        p_plus=p0_meas,
        p_minus=p1_meas,
    )


def measure_state(
    state: QuantumState,
    basis: Union[StateBasis, str],
    expected_eigenvalue: Optional[Union[Eigenvalue, int, str]] = None,
    shots: int = 1,
    readout_error: float = 0.0,
    seed: Optional[int] = None,
) -> MeasurementResult:
    """Convenience wrapper for measure_state_projective."""
    b = StateBasis(str(basis).upper())
    ev = Eigenvalue.from_str(expected_eigenvalue) if expected_eigenvalue is not None else None
    return measure_state_projective(
        state=state,
        basis=b,
        expected_eigenvalue=ev,
        shots=shots,
        readout_error=readout_error,
        seed=seed,
    )
