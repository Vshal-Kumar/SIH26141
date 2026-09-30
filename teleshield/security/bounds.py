"""
Mathematical Security Bounds Module
Rigorous Hoeffding-bound equations governing teleportation-based QDS security:
  Honest False Rejection:  P_FR <= n * exp(-2L(s_a - epsilon)^2)
  Forgery Acceptance:      P_FA <= exp(-2L(p_f - s_a)^2)
"""

from __future__ import annotations
import numpy as np


def calculate_analytical_threshold(
    L: int,
    n_blocks: int,
    epsilon: float = 0.01,
    target_false_rejection: float = 1e-6,
) -> float:
    """
    Computes optimal acceptance threshold s_a per block:
      s_a = epsilon + sqrt(ln(n / alpha) / (2L))
    """
    eps = max(0.0, float(epsilon))
    alpha = max(1e-15, float(target_false_rejection))
    n = max(1, int(n_blocks))
    L_val = max(1, int(L))

    delta = np.sqrt(np.log(n / alpha) / (2.0 * L_val))
    s_a = eps + delta
    return float(min(0.48, max(eps + 1e-4, s_a)))


def calculate_honest_false_rejection_bound(
    L: int,
    n_blocks: int,
    threshold: float,
    epsilon: float = 0.01,
) -> float:
    """
    Calculates upper bound on false rejection across all n blocks:
      P_FR,total <= n * exp(-2L(s_a - epsilon)^2)
    """
    if threshold <= epsilon:
        return 1.0
    exponent = -2.0 * L * ((threshold - epsilon) ** 2)
    bound = n_blocks * np.exp(exponent)
    return float(min(1.0, max(0.0, bound)))


def calculate_forgery_acceptance_bound(
    L: int,
    threshold: float,
    p_forgery: float = 0.50,
) -> float:
    """
    Calculates upper bound on forgery acceptance for an attacked block:
      P_FA <= exp(-2L(p_f - s_a)^2)
    """
    if threshold >= p_forgery:
        return 1.0
    exponent = -2.0 * L * ((p_forgery - threshold) ** 2)
    bound = np.exp(exponent)
    return float(min(1.0, max(0.0, bound)))


def calculate_optimal_L(
    n_blocks: int,
    epsilon: float = 0.01,
    target_false_rejection: float = 1e-6,
    target_forgery_prob: float = 1e-6,
    p_forgery: float = 0.50,
) -> int:
    """
    Derives minimal required states L per bit value to simultaneously satisfy
    P_FR <= alpha and P_FA <= beta:
      sqrt(2L) >= (sqrt(ln(n/alpha)) + sqrt(ln(1/beta))) / (p_f - epsilon)
    """
    numerator = np.sqrt(np.log(n_blocks / target_false_rejection)) + np.sqrt(np.log(1.0 / target_forgery_prob))
    gap = p_forgery - epsilon
    if gap <= 1e-4:
        raise ValueError("Attacker error rate must be strictly greater than honest channel noise")

    sqrt_2L = numerator / gap
    min_L = int(np.ceil((sqrt_2L ** 2) / 2.0))
    return max(10, min_L)
