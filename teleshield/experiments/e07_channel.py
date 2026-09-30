"""
Experiment E07: Quantum Channel Manipulation Benchmark
Sweeps physical channel disturbance strength (depolarizing/jamming)
and measures the resulting detection probability curve.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
import numpy as np
import pandas as pd

from teleshield.backends.base import QuantumBackend
from teleshield.backends.exact import ExactBackend
from teleshield.qds.session import QDSSession
from teleshield.attacks.channel import ChannelManipulationAttack
from teleshield.analysis.plots import plot_detection_vs_attack_strength
from teleshield.experiments.runner import ExperimentResult


def run_e07_channel(
    backend: Optional[QuantumBackend] = None,
    seed: int = 42,
    strengths: Optional[List[float]] = None,
    trials_per_strength: int = 5,
    n_blocks: int = 16,
    L: int = 48,
    **kwargs,
) -> ExperimentResult:
    str_list = strengths or [0.0, 0.01, 0.02, 0.04, 0.06, 0.08, 0.12, 0.16, 0.20, 0.30]
    records = []
    detection_probs = []

    for s_val in str_list:
        detected_count = 0
        observed_mismatches = []

        for t in range(trials_per_strength):
            session = QDSSession.create(
                n=n_blocks,
                L=L,
                backend=backend or ExactBackend(seed=seed + t),
                bell_visibility=0.99,
                seed=seed + t,
            )

            msg = f"Payload for channel disturbance evaluation trial {t}"
            sig = session.sign(msg)

            # Apply channel attack to Bob's stored quantum states
            attack = ChannelManipulationAttack(channel_type="depolarizing", strength=s_val, seed=seed + t)
            attack_res = attack.execute(slots=session.slots)
            session.slots = attack_res.manipulated_slots

            verdict, stats = session.verify(msg, sig, seed=seed + t)

            is_flagged = not verdict.is_accepted
            if is_flagged:
                detected_count += 1

            rate = stats.global_mismatch_rate if stats else 0.0
            observed_mismatches.append(rate)

            records.append({
                "strength": s_val,
                "trial": t,
                "verdict": verdict.verdict.value,
                "global_mismatch": rate,
                "detected": is_flagged,
            })

        p_det = float(detected_count) / float(trials_per_strength)
        detection_probs.append(p_det)

    df = pd.DataFrame(records)
    fig = plot_detection_vs_attack_strength(str_list, detection_probs, attack_label="Channel Jamming")

    return ExperimentResult(
        experiment_id="E07",
        title="Channel Manipulation Detection Probability Sweep",
        seed=seed,
        elapsed_seconds=0.0,
        data={
            "strengths": str_list,
            "detection_probabilities": detection_probs,
        },
        summary_metrics={
            "detection_prob_at_max_strength": detection_probs[-1],
            "first_full_detection_strength": str_list[detection_probs.index(1.0)] if 1.0 in detection_probs else None,
        },
        df=df,
        plot_fig=fig,
    )
