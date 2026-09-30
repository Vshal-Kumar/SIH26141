"""
Security Bounds & Calculator Test Suite
Validates mathematical bounds, analytical threshold derivations,
and security parameter calculator sizing algorithms.
"""

import pytest
import numpy as np

from teleshield.security.bounds import (
    calculate_analytical_threshold,
    calculate_honest_false_rejection_bound,
    calculate_forgery_acceptance_bound,
    calculate_optimal_L,
)
from teleshield.security.calculator import SecurityParameterCalculator


def test_analytical_threshold_calculation():
    """Verify threshold increases with noise and decreases with L."""
    t1 = calculate_analytical_threshold(L=64, n_blocks=64, epsilon=0.01, target_false_rejection=1e-6)
    t2 = calculate_analytical_threshold(L=222, n_blocks=64, epsilon=0.01, target_false_rejection=1e-6)
    t3 = calculate_analytical_threshold(L=222, n_blocks=64, epsilon=0.03, target_false_rejection=1e-6)

    assert t2 < t1  # Larger L allows narrower margin
    assert t3 > t2  # Higher channel noise increases threshold
    assert t1 < 0.50  # Must be strictly below random guessing bound


def test_hoeffding_bounds_limits():
    """Verify Hoeffding probabilities respect [0, 1] range and exponential decay."""
    p_fr = calculate_honest_false_rejection_bound(L=222, n_blocks=64, threshold=0.045, epsilon=0.01)
    assert 0.0 <= p_fr <= 1.0

    p_fa_small_L = calculate_forgery_acceptance_bound(L=32, threshold=0.045, p_forgery=0.50)
    p_fa_large_L = calculate_forgery_acceptance_bound(L=222, threshold=0.045, p_forgery=0.50)
    assert p_fa_large_L < p_fa_small_L
    assert p_fa_large_L < 1e-10


def test_security_parameter_calculator():
    """Verify SecurityParameterCalculator sizing recommendations."""
    calc = SecurityParameterCalculator()
    rec = calc.calculate(
        n=64,
        L=222,
        epsilon=0.01,
        target_false_rejection=1e-6,
        target_forgery_probability=1e-6,
        attacker_model="random_guessing",
    )

    assert rec.recommended_min_L > 0
    assert rec.total_qubits_required == 2 * 64 * 222
    assert rec.acceptance_threshold > rec.expected_noise
    assert rec.acceptance_threshold < rec.optional_verification_threshold
    assert rec.security_bits > 50.0  # Strong cryptographic security
