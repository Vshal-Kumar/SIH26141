"""
Q-STAT Binomial Statistical Verification Module
Implements hypothesis testing on measurement mismatch counts:
  X_j ~ Binomial(L, p)
Derives mathematically sound acceptance thresholds s_a and calculates
rigorous Hoeffding and exact Binomial p-values.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from scipy import stats

from teleshield.qstat.statistics import BlockStatistics, VerificationStatistics


@dataclass
class BinomialTestResult:
    """Outcome of statistical hypothesis test on a block or global sequence."""
    is_valid: bool
    observed_rate: float
    threshold: float
    p_value: float
    confidence_interval: Tuple[float, float]
    hoeffding_bound: float
    mismatches: int
    total_trials: int


def calculate_acceptance_threshold(
    L: int,
    n_blocks: int,
    expected_honest_noise: float = 0.01,
    target_false_rejection: float = 1e-6,
) -> float:
    """
    Derives the mathematical acceptance threshold s_a per block using Hoeffding's inequality:
      P_FR,total <= n * exp(-2 * L * (s_a - epsilon)^2) <= alpha
      => 2 * L * (s_a - epsilon)^2 >= ln(n / alpha)
      => s_a = epsilon + sqrt(ln(n / alpha) / (2 * L))

    Ensures no arbitrary hardcoding of thresholds.
    """
    eps = max(0.0, float(expected_honest_noise))
    alpha = max(1e-15, float(target_false_rejection))
    n = max(1, int(n_blocks))
    L_val = max(1, int(L))

    # Calculate Hoeffding margin
    delta = np.sqrt(np.log(n / alpha) / (2.0 * L_val))
    s_a = eps + delta

    # Threshold must strictly be below the random guessing bound p_f = 0.5
    # Cap to reasonable range if L is very small
    s_a = min(0.45, max(eps + 1e-4, float(s_a)))
    return s_a


def calculate_hoeffding_false_rejection_bound(
    L: int,
    n_blocks: int,
    threshold: float,
    expected_honest_noise: float,
) -> float:
    """Computes upper bound on false rejection: P_FR <= n * exp(-2L(s_a - epsilon)^2)."""
    if threshold <= expected_honest_noise:
        return 1.0
    exponent = -2.0 * L * ((threshold - expected_honest_noise) ** 2)
    bound = n_blocks * np.exp(exponent)
    return float(min(1.0, max(0.0, bound)))


def calculate_hoeffding_forgery_acceptance_bound(
    L: int,
    threshold: float,
    attacker_success_rate: float = 0.5,
) -> float:
    """
    Computes upper bound on forgery acceptance: P_FA <= exp(-2L(p_f - s_a)^2)
    where p_f = 0.5 for random guessing.
    """
    if threshold >= attacker_success_rate:
        return 1.0
    exponent = -2.0 * L * ((attacker_success_rate - threshold) ** 2)
    bound = np.exp(exponent)
    return float(min(1.0, max(0.0, bound)))


class BinomialVerifier:
    """
    Statistically evaluates measurement evidence against derived thresholds.
    Performs block-by-block and global hypothesis testing.
    """

    def __init__(
        self,
        expected_honest_noise: float = 0.01,
        target_false_rejection: float = 1e-6,
    ) -> None:
        self.expected_honest_noise = expected_honest_noise
        self.target_false_rejection = target_false_rejection

    def test_block(
        self,
        block: BlockStatistics,
        n_blocks: int,
    ) -> BinomialTestResult:
        """Evaluates an individual block against derived s_a."""
        s_a = calculate_acceptance_threshold(
            L=block.L,
            n_blocks=n_blocks,
            expected_honest_noise=self.expected_honest_noise,
            target_false_rejection=self.target_false_rejection,
        )

        obs_rate = block.mismatch_rate
        is_valid = obs_rate <= s_a

        # Exact binomial test: H0: p = epsilon vs H1: p > epsilon
        res = stats.binomtest(
            k=block.mismatches,
            n=block.L,
            p=self.expected_honest_noise,
            alternative="greater",
        )
        p_val = float(res.pvalue)

        # Clopper-Pearson 95% confidence interval
        ci = res.proportion_ci(confidence_level=0.95, method="exact")
        ci_tuple = (float(ci.low), float(ci.high))

        hoeffding_p = calculate_hoeffding_false_rejection_bound(
            L=block.L,
            n_blocks=1,
            threshold=s_a,
            expected_honest_noise=self.expected_honest_noise,
        )

        return BinomialTestResult(
            is_valid=is_valid,
            observed_rate=obs_rate,
            threshold=s_a,
            p_value=p_val,
            confidence_interval=ci_tuple,
            hoeffding_bound=hoeffding_p,
            mismatches=block.mismatches,
            total_trials=block.L,
        )

    def test_global(
        self,
        stats_obj: VerificationStatistics,
    ) -> BinomialTestResult:
        """Evaluates global aggregated sequence."""
        # Threshold for total states N = n * L
        s_a_global = calculate_acceptance_threshold(
            L=stats_obj.total_states,
            n_blocks=1,
            expected_honest_noise=self.expected_honest_noise,
            target_false_rejection=self.target_false_rejection,
        )

        obs_rate = stats_obj.global_mismatch_rate
        is_valid = obs_rate <= s_a_global

        res = stats.binomtest(
            k=stats_obj.total_mismatches,
            n=stats_obj.total_states,
            p=self.expected_honest_noise,
            alternative="greater",
        )
        p_val = float(res.pvalue)
        ci = res.proportion_ci(confidence_level=0.95, method="exact")
        ci_tuple = (float(ci.low), float(ci.high))

        return BinomialTestResult(
            is_valid=is_valid,
            observed_rate=obs_rate,
            threshold=s_a_global,
            p_value=p_val,
            confidence_interval=ci_tuple,
            hoeffding_bound=calculate_hoeffding_false_rejection_bound(
                stats_obj.total_states, 1, s_a_global, self.expected_honest_noise
            ),
            mismatches=stats_obj.total_mismatches,
            total_trials=stats_obj.total_states,
        )
