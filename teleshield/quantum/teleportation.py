"""
Quantum Teleportation Module
Implementation of the canonical Bennett et al. (1993) quantum teleportation protocol.
Simulates state preparation, Bell pair distribution, Alice's Bell-basis measurement (CNOT + H),
classical syndrome transmission (m0, m1), and Bob's Pauli correction operations (X^m1 Z^m0).
Supports both ideal execution and noisy/Werner channels.
"""

from __future__ import annotations
from typing import Dict, Any, Tuple, Optional
import numpy as np

from teleshield.quantum.states import QuantumState, STATE_0_VEC, STATE_1_VEC
from teleshield.quantum.pauli import (
    PAULI_I, PAULI_X, PAULI_Y, PAULI_Z, HADAMARD,
    get_correction_operator, apply_operator
)
from teleshield.quantum.bell import BellPair, BellState, create_bell_pair


class TeleportationResult:
    """Encapsulates all measurement evidence and state outcomes of a teleportation event."""

    def __init__(
        self,
        input_state: QuantumState,
        bell_pair: BellPair,
        measurement_bits: Tuple[int, int],
        correction_applied: str,
        output_state: QuantumState,
        fidelity: float,
        shot_statistics: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.input_state = input_state
        self.bell_pair = bell_pair
        self.measurement_bits = measurement_bits  # (m0, m1)
        self.correction_applied = correction_applied
        self.output_state = output_state
        self.fidelity = float(fidelity)
        self.shot_statistics = shot_statistics or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_state": self.input_state.to_dict(),
            "bell_type": self.bell_pair.bell_type.value,
            "bell_visibility": self.bell_pair.visibility,
            "measurement_bits": {
                "m0_alice_input": self.measurement_bits[0],
                "m1_alice_bell": self.measurement_bits[1],
            },
            "correction_applied": self.correction_applied,
            "output_state": self.output_state.to_dict(),
            "fidelity": self.fidelity,
            "shot_statistics": self.shot_statistics,
        }

    def __repr__(self) -> str:
        return (
            f"TeleportationResult(m0={self.measurement_bits[0]}, m1={self.measurement_bits[1]}, "
            f"correction={self.correction_applied}, fidelity={self.fidelity:.5f})"
        )


def teleport_state(
    input_state: QuantumState,
    bell_pair: Optional[BellPair] = None,
    shots: int = 1,
    seed: Optional[int] = None,
) -> TeleportationResult:
    """
    Executes quantum teleportation of input_state using bell_pair resource.
    Uses 3-qubit density matrix formalism to support ideal and general mixed states.

    Qubit 0: Input state |psi> (Alice)
    Qubit 1: Alice's half of Bell pair
    Qubit 2: Bob's half of Bell pair

    Alice:
      1. CNOT on (qubit 0 -> qubit 1)
      2. Hadamard on qubit 0
      3. Projective measurement of qubits 0 & 1 -> (m0, m1)

    Bob:
      Correction U = X^{m1} Z^{m0} applied to qubit 2.
    """
    rng = np.random.default_rng(seed)
    if bell_pair is None:
        bell_pair = create_bell_pair(BellState.PHI_PLUS, visibility=1.0)

    # Construct 3-qubit initial density matrix: rho_0 \otimes rho_12
    rho_0 = input_state.density_matrix
    rho_12 = bell_pair.density_matrix
    rho_012 = np.kron(rho_0, rho_12)  # shape (8, 8)

    # Alice's operations:
    # CNOT on qubits 0 and 1:
    # |0><0| \otimes I \otimes I + |1><1| \otimes X \otimes I
    proj0 = np.outer(STATE_0_VEC, STATE_0_VEC.conj())
    proj1 = np.outer(STATE_1_VEC, STATE_1_VEC.conj())
    i2 = PAULI_I

    cnot_01 = np.kron(np.kron(proj0, i2), i2) + np.kron(np.kron(proj1, PAULI_X), i2)

    # Hadamard on qubit 0:
    h_0 = np.kron(np.kron(HADAMARD, i2), i2)

    # Joint Alice unitary
    u_alice = h_0 @ cnot_01
    rho_prime = u_alice @ rho_012 @ u_alice.conj().T

    # Measurement probabilities for outcomes (m0, m1) in {(0,0), (0,1), (1,0), (1,1)}
    probs = []
    post_states_bob = []

    basis_states_2q = [
        (0, 0, np.array([1, 0, 0, 0], dtype=np.complex128)),
        (0, 1, np.array([0, 1, 0, 0], dtype=np.complex128)),
        (1, 0, np.array([0, 0, 1, 0], dtype=np.complex128)),
        (1, 1, np.array([0, 0, 0, 1], dtype=np.complex128)),
    ]

    for m0, m1, v_alice in basis_states_2q:
        p_alice = np.outer(v_alice, v_alice.conj())  # (4, 4)
        proj_3q = np.kron(p_alice, i2)  # (8, 8)
        cond_state = proj_3q @ rho_prime @ proj_3q

        p = float(np.real(np.trace(cond_state)))
        probs.append(p)

        if p > 1e-12:
            # Partial trace over qubits 0 and 1 to obtain Bob's qubit 2 state
            # Basis indices for 3 qubits: |m0 m1 q2>
            # For fixed (m0, m1), qubit 2 indices in the 8-dim space are:
            # idx0 = (m0*2 + m1)*2 + 0
            # idx1 = (m0*2 + m1)*2 + 1
            idx0 = (m0 * 2 + m1) * 2 + 0
            idx1 = (m0 * 2 + m1) * 2 + 1
            sub_rho = np.array([
                [cond_state[idx0, idx0], cond_state[idx0, idx1]],
                [cond_state[idx1, idx0], cond_state[idx1, idx1]]
            ], dtype=np.complex128)
            sub_rho = sub_rho / p
        else:
            sub_rho = np.eye(2, dtype=np.complex128) * 0.5

        post_states_bob.append(sub_rho)

    # Normalize probabilities for numerical stability
    total_p = sum(probs)
    if total_p > 0:
        probs = [p / total_p for p in probs]
    else:
        probs = [0.25, 0.25, 0.25, 0.25]

    # Sample Alice's measurement bits according to probabilities
    choice_idx = int(rng.choice(4, p=probs))
    sampled_m0, sampled_m1, _ = basis_states_2q[choice_idx]

    # Bob applies correction: U = X^{m1} Z^{m0}
    corr_name, corr_op = get_correction_operator(sampled_m0, sampled_m1)
    raw_bob_rho = post_states_bob[choice_idx]
    corrected_bob_rho = corr_op @ raw_bob_rho @ corr_op.conj().T

    # Enforce unit trace and Hermiticity
    corrected_bob_rho = (corrected_bob_rho + corrected_bob_rho.conj().T) / 2.0
    tr = np.trace(corrected_bob_rho)
    if abs(tr) > 1e-12:
        corrected_bob_rho = corrected_bob_rho / tr

    out_vec = input_state.vector if (bell_pair.is_pure and input_state.vector is not None) else None
    output_state = QuantumState(
        vector=out_vec,
        density_matrix=corrected_bob_rho,
        basis=input_state.basis,
        eigenvalue=input_state.eigenvalue,
    )

    fid = input_state.fidelity(output_state)

    # If shots > 1, collect distribution statistics
    shot_counts = {}
    if shots > 1:
        sampled_counts = rng.multinomial(shots, probs)
        shot_counts = {
            "(0,0)": int(sampled_counts[0]),
            "(0,1)": int(sampled_counts[1]),
            "(1,0)": int(sampled_counts[2]),
            "(1,1)": int(sampled_counts[3]),
        }
    else:
        shot_counts = {
            f"({sampled_m0},{sampled_m1})": 1
        }

    return TeleportationResult(
        input_state=input_state,
        bell_pair=bell_pair,
        measurement_bits=(sampled_m0, sampled_m1),
        correction_applied=corr_name,
        output_state=output_state,
        fidelity=fid,
        shot_statistics={
            "total_shots": shots,
            "probabilities": {
                "(0,0)": float(probs[0]),
                "(0,1)": float(probs[1]),
                "(1,0)": float(probs[2]),
                "(1,1)": float(probs[3]),
            },
            "counts": shot_counts,
        },
    )
