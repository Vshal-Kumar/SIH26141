"""
Experiment E06: Impersonation Attack Detection Benchmark
Simulates adversaries attempting to forge valid signatures without private key ownership.
Validates high detection rate and statistical convergence toward the 50% random guessing bound.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
import numpy as np
import pandas as pd

from teleshield.backends.base import QuantumBackend
from teleshield.backends.exact import ExactBackend
from teleshield.qds.session import QDSSession
from teleshield.attacks.impersonation import ImpersonationAttack
from teleshield.experiments.runner import ExperimentResult


def run_e06_impersonation(
    backend: Optional[QuantumBackend] = None,
    seed: int = 42,
    num_trials: int = 10,
    n_blocks: int = 16,
    L: int = 64,
    **kwargs,
) -> ExperimentResult:
    records = []
    detections = 0
    mismatch_rates = []

    for t in range(num_trials):
        session = QDSSession.create(
            n=n_blocks,
            L=L,
            backend=backend or ExactBackend(seed=seed + t),
            bell_visibility=0.99,
            seed=seed + t,
        )

        msg = f"Unauthorized high-value transfer payload #{t}"

        # Attacker fabricates entire signature without knowing private key
        attack = ImpersonationAttack(seed=seed + t)
        attack_res = attack.execute(
            message=msg,
            key_id=session.keypair.key_id,
            verifier_id=session.verifier.verifier_id,
            n_bits=n_blocks,
            L=L,
        )

        verdict, stats = session.verify(
            message=msg,
            signature=attack_res.manipulated_signature,
            seed=seed + t,
        )

        rate = stats.global_mismatch_rate if stats else 1.0
        mismatch_rates.append(rate)

        is_detected = verdict.verdict.value in ("IMPERSONATION_SUSPECTED", "FORGERY_SUSPECTED", "REJECT")
        if is_detected:
            detections += 1

        records.append({
            "trial": t,
            "verdict": verdict.verdict.value,
            "global_mismatch": rate,
            "detected": is_detected,
        })

    df = pd.DataFrame(records)
    det_rate = float(detections) / float(num_trials)
    avg_mismatch = float(np.mean(mismatch_rates))

    return ExperimentResult(
        experiment_id="E06",
        title="Impersonation Attack Detection Rate",
        seed=seed,
        elapsed_seconds=0.0,
        data={
            "num_trials": num_trials,
            "detections": detections,
            "detection_rate": det_rate,
            "mean_mismatch_rate": avg_mismatch,
        },
        summary_metrics={
            "detection_rate": det_rate,
            "mean_mismatch_rate": avg_mismatch,
            "random_guessing_conformance": abs(avg_mismatch - 0.50) < 0.10,
        },
        df=df,
        plot_fig=None,
    )
