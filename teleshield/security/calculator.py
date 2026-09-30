"""
Security Parameter Calculator Module
Interactive calculator determining optimal protocol configurations (L, s_a, s_v),
qubit overhead, and analytical bounds for user-specified threat models.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
import numpy as np

from teleshield.security.bounds import (
    calculate_analytical_threshold,
    calculate_honest_false_rejection_bound,
    calculate_forgery_acceptance_bound,
    calculate_optimal_L,
)


@dataclass
class SecurityRecommendation:
    """Actionable configuration recommendation for QDS protocol deployment."""
    n_blocks: int
    configured_L: int
    recommended_min_L: int
    acceptance_threshold: float
    optional_verification_threshold: float
    false_rejection_bound: float
    forgery_acceptance_bound: float
    total_qubits_required: int
    security_bits: float
    attacker_model: str
    expected_noise: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "n_blocks": self.n_blocks,
            "configured_L": self.configured_L,
            "recommended_min_L": self.recommended_min_L,
            "acceptance_threshold": self.acceptance_threshold,
            "optional_verification_threshold": self.optional_verification_threshold,
            "false_rejection_bound": self.false_rejection_bound,
            "forgery_acceptance_bound": self.forgery_acceptance_bound,
            "total_qubits_required": self.total_qubits_required,
            "security_bits": self.security_bits,
            "attacker_model": self.attacker_model,
            "expected_noise": self.expected_noise,
        }


class SecurityParameterCalculator:
    """
    Computes rigorous parameter sizing for teleportation-based QDS.
    """

    ATTACKER_RATES = {
        "random_guessing": 0.50,
        "intercept_resend": 0.25,
        "optimal_cloning": 0.1667,  # 1 - 5/6 fidelity limit for 1->2 universal cloner
    }

    def calculate(
        self,
        n: int = 64,
        L: Optional[int] = None,
        epsilon: float = 0.01,
        target_false_rejection: float = 1e-6,
        target_forgery_probability: float = 1e-6,
        attacker_model: str = "random_guessing",
    ) -> SecurityRecommendation:
        p_forgery = self.ATTACKER_RATES.get(attacker_model.lower(), 0.50)

        # Calculate minimal required L
        min_L = calculate_optimal_L(
            n_blocks=n,
            epsilon=epsilon,
            target_false_rejection=target_false_rejection,
            target_forgery_prob=target_forgery_probability,
            p_forgery=p_forgery,
        )

        effective_L = L if L is not None and L > 0 else min_L

        s_a = calculate_analytical_threshold(
            L=effective_L,
            n_blocks=n,
            epsilon=epsilon,
            target_false_rejection=target_false_rejection,
        )

        # Secondary verification threshold s_v (for multi-party dispute resolution / symmetrization)
        s_v = min(p_forgery - 1e-4, s_a + (p_forgery - s_a) / 2.0)

        p_fr = calculate_honest_false_rejection_bound(
            L=effective_L,
            n_blocks=n,
            threshold=s_a,
            epsilon=epsilon,
        )

        p_fa = calculate_forgery_acceptance_bound(
            L=effective_L,
            threshold=s_a,
            p_forgery=p_forgery,
        )

        total_qubits = 2 * n * effective_L
        sec_bits = -np.log2(max(1e-30, p_fa))

        return SecurityRecommendation(
            n_blocks=n,
            configured_L=effective_L,
            recommended_min_L=min_L,
            acceptance_threshold=s_a,
            optional_verification_threshold=s_v,
            false_rejection_bound=p_fr,
            forgery_acceptance_bound=p_fa,
            total_qubits_required=total_qubits,
            security_bits=float(sec_bits),
            attacker_model=attacker_model,
            expected_noise=epsilon,
        )
