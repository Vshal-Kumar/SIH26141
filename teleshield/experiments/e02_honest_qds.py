"""
Experiment E02: Honest QDS False Rejection Benchmark
Executes legitimate QDS sessions across varying channel noise levels.
Measures empirical false rejection rate against Hoeffding analytical bounds.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
import numpy as np
import pandas as pd

from teleshield.backends.base import QuantumBackend
from teleshield.backends.exact import ExactBackend
from teleshield.qds.session import QDSSession
from teleshield.security.bounds import calculate_analytical_threshold, calculate_honest_false_rejection_bound
from teleshield.analysis.plots import plot_false_rejection_vs_noise
from teleshield.experiments.runner import ExperimentResult


def run_e02_honest_qds(
    backend: Optional[QuantumBackend] = None,
    seed: int = 42,
    n: int = 16,
    L: int = 64,
    shots: int = 100,
    noise_levels: Optional[List[float]] = None,
    trials_per_noise: int = 5,
    **kwargs,
) -> ExperimentResult:
    levels = noise_levels or [0.001, 0.005, 0.010, 0.015, 0.020, 0.025]
    records = []
    analytical_bounds = []
    empirical_rates = []

    for eps in levels:
        rejections = 0
        mismatch_rates = []

        s_a = calculate_analytical_threshold(L=L, n_blocks=n, epsilon=eps, target_false_rejection=1e-5)
        p_fr_bound = calculate_honest_false_rejection_bound(L=L, n_blocks=n, threshold=s_a, epsilon=eps)
        analytical_bounds.append(p_fr_bound)

        for t in range(trials_per_noise):
            session = QDSSession.create(
                n=n,
                L=L,
                backend=backend or ExactBackend(seed=seed + t),
                bell_visibility=1.0 - eps,
                shots=shots,
                seed=seed + t,
            )

            msg = f"TeleShield legitimate message trial {t} at noise {eps}"
            sig = session.sign(msg)
            verdict, stats = session.verify(msg, sig, shots=shots, seed=seed + t)

            rate = stats.global_mismatch_rate if stats else 0.0
            mismatch_rates.append(rate)
            if not verdict.is_accepted:
                rejections += 1

            records.append({
                "noise_level": eps,
                "trial": t,
                "verdict": verdict.verdict.value,
                "global_mismatch": rate,
                "threshold": s_a,
                "rejected": not verdict.is_accepted,
            })

        emp_rate = float(rejections) / float(trials_per_noise)
        empirical_rates.append(emp_rate)

    df = pd.DataFrame(records)
    fig = plot_false_rejection_vs_noise(levels, analytical_bounds, empirical_rates)

    return ExperimentResult(
        experiment_id="E02",
        title="Honest QDS False Rejection vs Noise",
        seed=seed,
        elapsed_seconds=0.0,
        data={
            "noise_levels": levels,
            "empirical_rejection_rates": empirical_rates,
            "analytical_bounds": analytical_bounds,
        },
        summary_metrics={
            "mean_empirical_rejection": float(np.mean(empirical_rates)),
            "max_empirical_rejection": float(np.max(empirical_rates)),
            "protocol_soundness": float(np.mean(empirical_rates)) <= 0.10,
        },
        df=df,
        plot_fig=fig,
    )
