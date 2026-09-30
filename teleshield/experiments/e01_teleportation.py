"""
Experiment E01: Quantum Teleportation Fidelity Benchmark
Measures teleportation fidelity across canonical states (|0>, |1>, |+>, |->, |+y>, |-y>)
under ideal conditions and increasing channel noise.
Ideal fidelity strictly approaches 1.0.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
import numpy as np
import pandas as pd

from teleshield.backends.base import QuantumBackend
from teleshield.backends.exact import ExactBackend
from teleshield.quantum.states import QuantumState, StateBasis, Eigenvalue
from teleshield.quantum.bell import BellState, create_bell_pair
from teleshield.quantum.noise import NoiseModelConfig, NoiseType
from teleshield.analysis.plots import plot_teleportation_fidelity_vs_noise
from teleshield.experiments.runner import ExperimentResult


def run_e01_teleportation(
    backend: Optional[QuantumBackend] = None,
    seed: int = 42,
    noise_levels: Optional[List[float]] = None,
    **kwargs,
) -> ExperimentResult:
    q_backend = backend or ExactBackend(seed=seed)
    levels = noise_levels or [0.0, 0.01, 0.02, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30]

    test_states = [
        QuantumState.zero(),
        QuantumState.one(),
        QuantumState.plus(),
        QuantumState.minus(),
        QuantumState.plus_y(),
        QuantumState.minus_y(),
    ]

    records = []
    mean_fidelities = []

    for p_noise in levels:
        # Evaluate each state under Werner / depolarizing channel
        bp = create_bell_pair(BellState.PHI_PLUS, visibility=max(0.0, 1.0 - p_noise * 1.5))
        fids = []
        for st in test_states:
            res = q_backend.teleport(input_state=st, bell_pair=bp, seed=seed)
            fids.append(res.fidelity)
            records.append({
                "noise_level": p_noise,
                "state_label": st.label,
                "fidelity": res.fidelity,
                "m0": res.measurement_bits[0],
                "m1": res.measurement_bits[1],
                "correction": res.correction_applied,
            })
        mean_fidelities.append(float(np.mean(fids)))

    df = pd.DataFrame(records)
    fig = plot_teleportation_fidelity_vs_noise(levels, mean_fidelities)

    ideal_fid = mean_fidelities[0]

    return ExperimentResult(
        experiment_id="E01",
        title="Teleportation Fidelity vs Channel Degradation",
        seed=seed,
        elapsed_seconds=0.0,
        data={
            "noise_levels": levels,
            "mean_fidelities": mean_fidelities,
            "ideal_fidelity": ideal_fid,
        },
        summary_metrics={
            "ideal_fidelity": ideal_fid,
            "min_fidelity_at_p03": mean_fidelities[-1],
            "classical_violation": ideal_fid > 0.667,
        },
        df=df,
        plot_fig=fig,
    )
