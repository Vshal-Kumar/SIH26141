"""
Backend Parity Test Suite
Validates that Exact, Aer, and Stim backends produce statistically
consistent measurement distributions for identical quantum circuits.
"""

import pytest
import numpy as np
from scipy import stats

from teleshield.backends.exact import ExactBackend
from teleshield.backends.aer import AerBackend
from teleshield.backends.stim import StimBackend
from teleshield.quantum.states import StateBasis, Eigenvalue


def test_backend_cross_validation_parity():
    """Verify state preparation, teleportation, and measurement across backends."""
    seed = 42
    shots = 1000

    exact_b = ExactBackend(shots=shots, seed=seed)
    aer_b = AerBackend(shots=shots, seed=seed)
    stim_b = StimBackend(shots=shots, seed=seed)

    # Test |+> state measured in X basis (should give 100% match, mismatch rate ~ 0.0)
    for b_instance in [exact_b, aer_b, stim_b]:
        st = b_instance.prepare_state(StateBasis.X, Eigenvalue.PLUS)
        t_res = b_instance.teleport(st, seed=seed)
        m_res = b_instance.measure(t_res.output_state, basis=StateBasis.X, expected_eigenvalue=Eigenvalue.PLUS, seed=seed)
        assert m_res.mismatch_rate <= 0.02

    # Test |+> state measured in Z basis (should give ~50% mismatch)
    rates = []
    for b_instance in [exact_b, aer_b, stim_b]:
        st = b_instance.prepare_state(StateBasis.X, Eigenvalue.PLUS)
        t_res = b_instance.teleport(st, seed=seed)
        m_res = b_instance.measure(t_res.output_state, basis=StateBasis.Z, expected_eigenvalue=Eigenvalue.PLUS, seed=seed)
        rates.append(m_res.mismatch_rate)

    for r in rates:
        assert abs(r - 0.50) < 0.08
