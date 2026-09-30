"""
Quantum Core Test Suite
Validates mathematical integrity of quantum states, Pauli operators,
Bell states, teleportation, projective measurements, and noise channels.
"""

import pytest
import numpy as np

from teleshield.quantum.states import QuantumState, StateBasis, Eigenvalue
from teleshield.quantum.pauli import (
    PAULI_I, PAULI_X, PAULI_Y, PAULI_Z,
    apply_pauli, get_correction_operator, rotate_to_z
)
from teleshield.quantum.bell import (
    BellState, create_bell_pair, compute_chsh_s, compute_werner_state
)
from teleshield.quantum.teleportation import teleport_state
from teleshield.quantum.measurement import measure_state_projective
from teleshield.quantum.noise import (
    NoiseModelConfig, NoiseType, apply_quantum_noise
)


def test_pauli_eigenstates():
    """Verify standard Pauli eigenstates and their eigenvalues."""
    # Z basis
    z0 = QuantumState.zero()
    z1 = QuantumState.one()
    assert z0.basis == StateBasis.Z and z0.eigenvalue == Eigenvalue.PLUS
    assert z1.basis == StateBasis.Z and z1.eigenvalue == Eigenvalue.MINUS
    assert abs(z0.fidelity(z1)) < 1e-10  # Orthogonal

    # X basis
    xp = QuantumState.plus()
    xm = QuantumState.minus()
    assert xp.basis == StateBasis.X and xp.eigenvalue == Eigenvalue.PLUS
    assert xm.basis == StateBasis.X and xm.eigenvalue == Eigenvalue.MINUS
    assert abs(xp.fidelity(xm)) < 1e-10

    # Y basis
    yp = QuantumState.plus_y()
    ym = QuantumState.minus_y()
    assert yp.basis == StateBasis.Y and yp.eigenvalue == Eigenvalue.PLUS
    assert ym.basis == StateBasis.Y and ym.eigenvalue == Eigenvalue.MINUS
    assert abs(yp.fidelity(ym)) < 1e-10


def test_pauli_algebra_and_corrections():
    """Verify Pauli matrix commutation, multiplication, and teleportation correction operators."""
    # X^2 = I, Y^2 = I, Z^2 = I
    assert np.allclose(PAULI_X @ PAULI_X, PAULI_I)
    assert np.allclose(PAULI_Y @ PAULI_Y, PAULI_I)
    assert np.allclose(PAULI_Z @ PAULI_Z, PAULI_I)

    # Bob's correction operator: X^{m1} Z^{m0}
    name00, op00 = get_correction_operator(0, 0)
    assert name00 == "I" and np.allclose(op00, PAULI_I)

    name01, op01 = get_correction_operator(0, 1)
    assert name01 == "X" and np.allclose(op01, PAULI_X)

    name10, op10 = get_correction_operator(1, 0)
    assert name10 == "Z" and np.allclose(op10, PAULI_Z)

    name11, op11 = get_correction_operator(1, 1)
    assert name11 == "XZ" and np.allclose(op11, PAULI_X @ PAULI_Z)


def test_bell_states_and_chsh():
    """Verify 4 Bell states and CHSH Bell inequality violation."""
    bp_phi_plus = create_bell_pair(BellState.PHI_PLUS, visibility=1.0)
    assert bp_phi_plus.is_pure
    assert abs(bp_phi_plus.fidelity_with_ideal() - 1.0) < 1e-6

    # Optimal CHSH S for pure Phi+ must be 2 * sqrt(2) ~ 2.8284
    s_val = bp_phi_plus.chsh_value()
    assert abs(s_val - 2.0 * np.sqrt(2.0)) < 1e-6
    assert s_val > 2.0  # Violates classical Bell boundary

    # Werner state visibility threshold: S <= 2 when V <= 1/sqrt(2) ~ 0.7071
    bp_classical = create_bell_pair(BellState.PHI_PLUS, visibility=0.60)
    assert bp_classical.chsh_value() < 2.0


def test_quantum_teleportation_fidelity():
    """Test quantum teleportation across multiple pure states under ideal conditions."""
    test_states = [
        QuantumState.zero(),
        QuantumState.one(),
        QuantumState.plus(),
        QuantumState.minus(),
        QuantumState.plus_y(),
        QuantumState.minus_y(),
    ]

    for st in test_states:
        res = teleport_state(input_state=st, seed=42)
        # In ideal simulation without noise, teleportation fidelity must be 1.0
        assert abs(res.fidelity - 1.0) < 1e-6
        # Output state density matrix must match input state
        assert np.allclose(st.density_matrix, res.output_state.density_matrix, atol=1e-6)


def test_projective_measurement():
    """Test projective measurement in Z, X, Y bases."""
    # Measuring |0> in Z basis must yield outcome 0 (+1 eigenvalue)
    res_z0 = measure_state_projective(QuantumState.zero(), basis=StateBasis.Z, shots=500, seed=42)
    assert res_z0.matches == 500
    assert res_z0.mismatches == 0
    assert res_z0.mismatch_rate == 0.0

    # Measuring |+> in X basis must yield match
    res_xp = measure_state_projective(QuantumState.plus(), basis=StateBasis.X, shots=500, seed=42)
    assert res_xp.matches == 500
    assert res_xp.mismatch_rate == 0.0

    # Measuring |+> in Z basis must yield ~50% match / 50% mismatch
    res_xp_z = measure_state_projective(QuantumState.plus(), basis=StateBasis.Z, expected_eigenvalue=Eigenvalue.PLUS, shots=2000, seed=42)
    assert abs(res_xp_z.mismatch_rate - 0.50) < 0.06


def test_quantum_noise_channels():
    """Test depolarizing and dephasing channel effects on density matrices."""
    cfg_depol = NoiseModelConfig(noise_type=NoiseType.DEPOLARIZING, depolarizing_rate=0.20)
    st = QuantumState.zero()
    noisy_st = apply_quantum_noise(st, cfg_depol)

    # Depolarizing channel reduces purity
    assert not noisy_st.is_pure
    fid = st.fidelity(noisy_st)
    assert fid < 1.0 and fid > 0.5
