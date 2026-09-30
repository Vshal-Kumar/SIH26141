"""
Experiment E14: Hardware-Aware Profile Comparison Benchmark
Systematically benchmarks Ideal, Ion-Trap, and Neutral-Atom Rydberg simulation profiles
for state fidelity, baseline error rates, verification margins, and computational latency.
Parameters are explicitly labelled as literature-derived / assumed models.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
import time
import pandas as pd

from teleshield.hardware.loaders import load_hardware_profile
from teleshield.qds.session import QDSSession
from teleshield.analysis.plots import plot_hardware_comparison
from teleshield.experiments.runner import ExperimentResult


def run_e14_hardware_profiles(
    seed: int = 42,
    n_blocks: int = 16,
    L: int = 32,
    shots: int = 500,
    **kwargs,
) -> ExperimentResult:
    profile_names = ["ideal", "ion_trap", "rydberg"]
    records = []

    fidelities = []
    error_rates = []
    latencies = []

    for name in profile_names:
        prof = load_hardware_profile(name)
        backend = prof.create_backend(override_shots=shots, override_seed=seed)

        start_t = time.perf_counter()
        session = QDSSession.create(
            n=n_blocks,
            L=L,
            backend=backend,
            bell_visibility=prof.get_param_value("bell_pair_fidelity", 1.0),
            shots=shots,
            seed=seed,
        )

        msg = f"Hardware benchmark transaction across {prof.display_name}"
        sig = session.sign(msg)
        verdict, stats = session.verify(msg, sig, shots=shots, seed=seed)
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0

        avg_fid = session.distribution_report.average_fidelity if session.distribution_report else 1.0
        err_rate = stats.global_mismatch_rate if stats else 0.0

        fidelities.append(avg_fid)
        error_rates.append(err_rate)
        latencies.append(elapsed_ms)

        records.append({
            "profile": prof.name,
            "display_name": prof.display_name,
            "backend": prof.backend_name,
            "reference_model": prof.reference_model,
            "average_fidelity": avg_fid,
            "global_mismatch_rate": err_rate,
            "verdict": verdict.verdict.value,
            "latency_ms": elapsed_ms,
        })

    df = pd.DataFrame(records)
    fig = plot_hardware_comparison(
        profiles=[r["display_name"] for r in records],
        fidelities=fidelities,
        error_rates=error_rates,
    )

    return ExperimentResult(
        experiment_id="E14",
        title="Hardware Profile Comparison (Ideal vs Ion-Trap vs Rydberg)",
        seed=seed,
        elapsed_seconds=0.0,
        data={
            "profiles_benchmarked": profile_names,
            "comparison": records,
        },
        summary_metrics={
            "ideal_fidelity": fidelities[0],
            "ion_trap_fidelity": fidelities[1],
            "rydberg_fidelity": fidelities[2],
            "all_profiles_accepted": all(r["verdict"] == "ACCEPT" for r in records),
        },
        df=df,
        plot_fig=fig,
    )
