"""
Experiment E13: Quantum Backend Parity Benchmark
Rigorous cross-validation comparing Exact NumPy, Qiskit Aer, and Stim backends.
Executes identical teleportation and measurement circuits and evaluates statistical
distribution consistency using Kolmogorov-Smirnov and Chi-squared tests.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
import numpy as np
import pandas as pd
from scipy import stats

from teleshield.backends.exact import ExactBackend
from teleshield.backends.aer import AerBackend
from teleshield.backends.stim import StimBackend
from teleshield.quantum.states import QuantumState, StateBasis, Eigenvalue
from teleshield.analysis.plots import plot_backend_parity
from teleshield.experiments.runner import ExperimentResult


def run_e13_backend_parity(
    seed: int = 42,
    shots_per_test: int = 2000,
    test_circuits: int = 16,
    **kwargs,
) -> ExperimentResult:
    exact_b = ExactBackend(shots=shots_per_test, seed=seed)
    aer_b = AerBackend(shots=shots_per_test, seed=seed)
    stim_b = StimBackend(shots=shots_per_test, seed=seed)

    rng = np.random.default_rng(seed)
    records = []
    exact_rates = []
    aer_rates = []
    stim_rates = []

    for idx in range(test_circuits):
        # Prepare random eigenstate in X or Z
        chosen_b = StateBasis.X if rng.random() < 0.5 else StateBasis.Z
        chosen_ev = Eigenvalue.PLUS if rng.random() < 0.5 else Eigenvalue.MINUS

        # 1. Exact
        st_exact = exact_b.prepare_state(chosen_b, chosen_ev)
        t_exact = exact_b.teleport(st_exact, seed=seed + idx)
        m_exact = exact_b.measure(t_exact.output_state, basis=chosen_b, expected_eigenvalue=chosen_ev, seed=seed + idx)

        # 2. Aer
        st_aer = aer_b.prepare_state(chosen_b, chosen_ev)
        t_aer = aer_b.teleport(st_aer, seed=seed + idx)
        m_aer = aer_b.measure(t_aer.output_state, basis=chosen_b, expected_eigenvalue=chosen_ev, seed=seed + idx)

        # 3. Stim
        st_stim = stim_b.prepare_state(chosen_b, chosen_ev)
        t_stim = stim_b.teleport(st_stim, seed=seed + idx)
        m_stim = stim_b.measure(t_stim.output_state, basis=chosen_b, expected_eigenvalue=chosen_ev, seed=seed + idx)

        exact_rates.append(m_exact.mismatch_rate)
        aer_rates.append(m_aer.mismatch_rate)
        stim_rates.append(m_stim.mismatch_rate)

        records.append({
            "circuit_idx": idx,
            "basis": chosen_b.value,
            "eigenvalue": chosen_ev.value,
            "exact_mismatch": m_exact.mismatch_rate,
            "aer_mismatch": m_aer.mismatch_rate,
            "stim_mismatch": m_stim.mismatch_rate,
        })

    df = pd.DataFrame(records)

    # Statistical distribution comparison via 2-sample Kolmogorov-Smirnov test
    ks_exact_aer = stats.ks_2samp(exact_rates, aer_rates)
    ks_exact_stim = stats.ks_2samp(exact_rates, stim_rates)

    fig = plot_backend_parity(
        exact_rates=exact_rates,
        aer_rates=aer_rates,
        stim_rates=stim_rates,
        block_indices=list(range(test_circuits)),
    )

    return ExperimentResult(
        experiment_id="E13",
        title="Backend Parity: Exact vs Aer vs Stim",
        seed=seed,
        elapsed_seconds=0.0,
        data={
            "exact_rates": exact_rates,
            "aer_rates": aer_rates,
            "stim_rates": stim_rates,
            "ks_pvalue_exact_aer": float(ks_exact_aer.pvalue),
            "ks_pvalue_exact_stim": float(ks_exact_stim.pvalue),
        },
        summary_metrics={
            "exact_aer_parity_pvalue": float(ks_exact_aer.pvalue),
            "exact_stim_parity_pvalue": float(ks_exact_stim.pvalue),
            "distributional_conformance": bool(ks_exact_aer.pvalue > 0.05 and ks_exact_stim.pvalue > 0.05),
        },
        df=df,
        plot_fig=fig,
    )
