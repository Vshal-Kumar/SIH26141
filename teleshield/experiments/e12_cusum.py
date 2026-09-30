"""
Experiment E12: CUSUM Drift Monitoring Benchmark
Validates cumulative sum detection of threshold-aware adversaries who inject
sub-threshold disturbances across multiple verification sessions.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
import numpy as np
import pandas as pd

from teleshield.backends.base import QuantumBackend
from teleshield.qstat.cusum import CUSUMMonitor, CUSUMState
from teleshield.analysis.plots import plot_cusum_drift
from teleshield.experiments.runner import ExperimentResult


def run_e12_cusum(
    backend: Optional[QuantumBackend] = None,
    seed: int = 42,
    num_sessions: int = 30,
    sub_threshold_rate: float = 0.025,
    attack_start_session: int = 12,
    **kwargs,
) -> ExperimentResult:
    rng = np.random.default_rng(seed)
    # Baseline honest noise = 0.01, sub-threshold perturbation = 0.025 (below sa = 0.045)
    monitor = CUSUMMonitor(baseline_rate=0.01, detectable_shift=0.02, decision_threshold=0.035)

    records = []
    cusum_values = []
    session_indices = list(range(1, num_sessions + 1))
    detection_session: Optional[int] = None

    for s_idx in session_indices:
        if s_idx < attack_start_session:
            # Honest baseline: Gaussian centered at 0.01
            session_rate = float(np.clip(rng.normal(0.010, 0.003), 0.002, 0.025))
            is_attack = False
        else:
            # Sub-threshold adversary active: Gaussian centered at 0.025 (strictly below sa ~ 0.045)
            session_rate = float(np.clip(rng.normal(sub_threshold_rate, 0.004), 0.015, 0.035))
            is_attack = True

        status = monitor.update(session_rate)
        cusum_values.append(status.current_cusum)

        if status.state == CUSUMState.ANOMALY and detection_session is None:
            detection_session = s_idx

        records.append({
            "session": s_idx,
            "session_error_rate": session_rate,
            "cusum_val": status.current_cusum,
            "threshold": status.decision_threshold,
            "state": status.state.value,
            "attack_active": is_attack,
        })

    df = pd.DataFrame(records)
    fig = plot_cusum_drift(session_indices, cusum_values, monitor.decision_threshold)

    return ExperimentResult(
        experiment_id="E12",
        title="CUSUM Multi-Session Drift Detection Benchmark",
        seed=seed,
        elapsed_seconds=0.0,
        data={
            "session_indices": session_indices,
            "cusum_values": cusum_values,
            "attack_start_session": attack_start_session,
            "detection_session": detection_session,
        },
        summary_metrics={
            "attack_start_session": attack_start_session,
            "detection_session": detection_session,
            "lag_sessions": (detection_session - attack_start_session) if detection_session else None,
            "sub_threshold_detected": detection_session is not None,
        },
        df=df,
        plot_fig=fig,
    )
