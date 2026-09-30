"""
Experiment E05: Deterministic Replay Attack Detection
Validates 100% deterministic detection of signature and quantum slot replays
via cryptographic nonce registries and quantum memory state destruction.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
import pandas as pd

from teleshield.backends.base import QuantumBackend
from teleshield.backends.exact import ExactBackend
from teleshield.qds.session import QDSSession
from teleshield.attacks.replay import ReplayAttack
from teleshield.experiments.runner import ExperimentResult


def run_e05_replay(
    backend: Optional[QuantumBackend] = None,
    seed: int = 42,
    num_trials: int = 10,
    **kwargs,
) -> ExperimentResult:
    records = []
    replays_detected = 0

    for t in range(num_trials):
        session = QDSSession.create(
            n=16,
            L=32,
            backend=backend or ExactBackend(seed=seed + t),
            bell_visibility=0.99,
            seed=seed + t,
        )

        msg = f"Transfer authorization payload #{t}"
        legit_sig = session.sign(msg)

        # 1. Legitimate verification (must pass)
        verdict_1, _ = session.verify(msg, legit_sig, seed=seed + t)

        # 2. Replay attack: re-submitting the exact same signature
        attack = ReplayAttack()
        attack_res = attack.execute(valid_signature=legit_sig)

        verdict_2, _ = session.verify(msg, attack_res.manipulated_signature, seed=seed + t)

        is_replay = verdict_2.verdict.value == "REPLAY"
        if is_replay:
            replays_detected += 1

        records.append({
            "trial": t,
            "first_verdict": verdict_1.verdict.value,
            "replayed_verdict": verdict_2.verdict.value,
            "detected_as_replay": is_replay,
            "nonce": legit_sig.nonce,
        })

    df = pd.DataFrame(records)
    detection_rate = float(replays_detected) / float(num_trials)

    return ExperimentResult(
        experiment_id="E05",
        title="Deterministic Replay Attack Detection",
        seed=seed,
        elapsed_seconds=0.0,
        data={
            "num_trials": num_trials,
            "replays_detected": replays_detected,
            "detection_rate": detection_rate,
        },
        summary_metrics={
            "detection_rate": detection_rate,
            "deterministic_protection": detection_rate == 1.0,
        },
        df=df,
        plot_fig=None,
    )
