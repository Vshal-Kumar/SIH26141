"""
Experiment E10: Security Parameter Analysis Benchmark
Rigorous comparison of theoretical Hoeffding exponential bounds against
empirical Monte Carlo simulations across protocol configurations.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
import numpy as np
import pandas as pd

from teleshield.backends.base import QuantumBackend
from teleshield.security.calculator import SecurityParameterCalculator
from teleshield.security.bounds import (
    calculate_honest_false_rejection_bound,
    calculate_forgery_acceptance_bound,
    calculate_analytical_threshold,
)
from teleshield.experiments.runner import ExperimentResult


def run_e10_security(
    backend: Optional[QuantumBackend] = None,
    seed: int = 42,
    n_blocks: int = 64,
    mc_trials: int = 50,
    **kwargs,
) -> ExperimentResult:
    calculator = SecurityParameterCalculator()
    rec = calculator.calculate(n=n_blocks, epsilon=0.01)

    rng = np.random.default_rng(seed)
    L_test_values = [32, 64, 128, 222]
    records = []

    for L_val in L_test_values:
        s_a = calculate_analytical_threshold(L=L_val, n_blocks=n_blocks, epsilon=0.01)
        p_fr_bound = calculate_honest_false_rejection_bound(L=L_val, n_blocks=n_blocks, threshold=s_a, epsilon=0.01)
        p_fa_bound = calculate_forgery_acceptance_bound(L=L_val, threshold=s_a, p_forgery=0.50)

        # Monte Carlo empirical trials
        # 1. Honest distribution: Binomial(L, 0.01) / L
        honest_samples = rng.binomial(L_val, 0.01, size=mc_trials) / float(L_val)
        mc_fr_rate = float(np.mean(honest_samples > s_a))

        # 2. Forgery distribution: Binomial(L, 0.50) / L
        forgery_samples = rng.binomial(L_val, 0.50, size=mc_trials) / float(L_val)
        mc_fa_rate = float(np.mean(forgery_samples <= s_a))

        records.append({
            "L": L_val,
            "threshold_sa": s_a,
            "analytical_P_FR": p_fr_bound,
            "monte_carlo_P_FR": mc_fr_rate,
            "analytical_P_FA": p_fa_bound,
            "monte_carlo_P_FA": mc_fa_rate,
        })

    df = pd.DataFrame(records)

    return ExperimentResult(
        experiment_id="E10",
        title="Analytical Security Bounds vs Monte Carlo Validation",
        seed=seed,
        elapsed_seconds=0.0,
        data={
            "recommendation": rec.to_dict(),
            "comparison_table": records,
        },
        summary_metrics={
            "recommended_min_L": rec.recommended_min_L,
            "derived_threshold": rec.acceptance_threshold,
            "security_bits": rec.security_bits,
            "bound_conservatism_confirmed": all(
                r["monte_carlo_P_FA"] <= r["analytical_P_FA"] or r["monte_carlo_P_FA"] == 0.0
                for r in records
            ),
        },
        df=df,
        plot_fig=None,
    )
