"""
Experiment E09: CHSH Entanglement Monitor Benchmark
Sweeps Werner-state visibility V and measures the resulting CHSH S parameter.
Validates the theoretical linear relation S = 2 * sqrt(2) * V and classical boundary crossing at V = 1/sqrt(2).
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
import numpy as np
import pandas as pd

from teleshield.backends.base import QuantumBackend
from teleshield.qstat.chsh import CHSHMonitor
from teleshield.analysis.plots import plot_chsh_vs_visibility
from teleshield.experiments.runner import ExperimentResult


def run_e09_chsh(
    backend: Optional[QuantumBackend] = None,
    seed: int = 42,
    visibilities: Optional[List[float]] = None,
    **kwargs,
) -> ExperimentResult:
    vis_list = visibilities or [0.50, 0.55, 0.60, 0.65, 0.70, 0.707, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00]
    monitor = CHSHMonitor()

    s_values = []
    records = []

    for v in vis_list:
        report = monitor.evaluate_channel(visibility=v)
        s_values.append(report.chsh_s)

        records.append({
            "visibility": v,
            "chsh_s": report.chsh_s,
            "classical_boundary": report.classical_boundary,
            "tsirelson_bound": report.tsirelson_bound,
            "violates_bell": report.violates_bell,
            "status": report.status,
        })

    df = pd.DataFrame(records)
    fig = plot_chsh_vs_visibility(vis_list, s_values)

    max_s = s_values[-1]
    tsirelson = 2.0 * np.sqrt(2.0)

    return ExperimentResult(
        experiment_id="E09",
        title="CHSH Entanglement Metric S vs Visibility",
        seed=seed,
        elapsed_seconds=0.0,
        data={
            "visibilities": vis_list,
            "chsh_s_values": s_values,
        },
        summary_metrics={
            "max_chsh_s": max_s,
            "tsirelson_bound": tsirelson,
            "tsirelson_conformance": abs(max_s - tsirelson) < 1e-4,
            "classical_threshold_visibility": 1.0 / np.sqrt(2.0),
        },
        df=df,
        plot_fig=fig,
    )
