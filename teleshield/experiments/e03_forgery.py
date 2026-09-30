"""
Experiment E03: Forgery Probability vs L Benchmark
Evaluates adversarial forgery acceptance probability as a function of
qubits per bit value (L). Compares empirical forgery acceptance against
Hoeffding exponential bounds.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
import numpy as np
import pandas as pd

from teleshield.backends.base import QuantumBackend
from teleshield.backends.exact import ExactBackend
from teleshield.qds.session import QDSSession
from teleshield.attacks.forgery import RandomForgeryAttack
from teleshield.security.bounds import (
    calculate_analytical_threshold,
    calculate_forgery_acceptance_bound
)
from teleshield.analysis.plots import plot_forgery_vs_L
from teleshield.experiments.runner import ExperimentResult


def run_e03_forgery(
    backend: Optional[QuantumBackend] = None,
    seed: int = 42,
    L_values: Optional[List[int]] = None,
    n_blocks: int = 16,
    trials_per_L: int = 10,
    **kwargs,
) -> ExperimentResult:
    Ls = L_values or [16, 32, 48, 64, 96, 128, 160]
    analytical_bounds = []
    empirical_accept_rates = []
    records = []

    for L_val in Ls:
        s_a = calculate_analytical_threshold(L=L_val, n_blocks=n_blocks, epsilon=0.01)
        bound = calculate_forgery_acceptance_bound(L=L_val, threshold=s_a, p_forgery=0.50)
        analytical_bounds.append(bound)

        accepted_forgeries = 0

        for t in range(trials_per_L):
            session = QDSSession.create(
                n=n_blocks,
                L=L_val,
                backend=backend or ExactBackend(seed=seed + t),
                bell_visibility=0.99,
                seed=seed + t,
            )

            msg = "TeleShield target message for forgery"
            legit_sig = session.sign(msg)

            # Inject full random forgery
            attack = RandomForgeryAttack(strength=1.0, seed=seed + t)
            attack_res = attack.execute(signature=legit_sig)

            verdict, stats = session.verify(
                message=msg,
                signature=attack_res.manipulated_signature,
                seed=seed + t,
            )

            if verdict.is_accepted:
                accepted_forgeries += 1

            records.append({
                "L": L_val,
                "trial": t,
                "verdict": verdict.verdict.value,
                "global_mismatch": stats.global_mismatch_rate if stats else 1.0,
                "threshold": s_a,
                "forgery_accepted": verdict.is_accepted,
            })

        emp_rate = float(accepted_forgeries) / float(trials_per_L)
        # Avoid exact zero for log plot
        empirical_accept_rates.append(max(1e-6, emp_rate))

    df = pd.DataFrame(records)
    fig = plot_forgery_vs_L(Ls, analytical_bounds, empirical_accept_rates)

    return ExperimentResult(
        experiment_id="E03",
        title="Forgery Probability vs Qubits per Bit (L)",
        seed=seed,
        elapsed_seconds=0.0,
        data={
            "L_values": Ls,
            "analytical_bounds": analytical_bounds,
            "empirical_accept_rates": empirical_accept_rates,
        },
        summary_metrics={
            "bound_at_min_L": analytical_bounds[0],
            "bound_at_max_L": analytical_bounds[-1],
            "exponential_decay_confirmed": analytical_bounds[-1] < analytical_bounds[0] * 1e-4,
        },
        df=df,
        plot_fig=fig,
    )
