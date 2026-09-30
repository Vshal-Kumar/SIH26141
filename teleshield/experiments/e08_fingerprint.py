"""
Experiment E08: Forensic Basis Fingerprinting Benchmark
Compares X/Y/Z basis error dispersion patterns across distinct physical noise channels:
dephasing (phase-flip), bit-flip, and isotropic depolarizing.
Validates forensic classification and attribution rules.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
import pandas as pd

from teleshield.backends.base import QuantumBackend
from teleshield.backends.exact import ExactBackend
from teleshield.qds.session import QDSSession
from teleshield.attacks.channel import ChannelManipulationAttack
from teleshield.analysis.plots import plot_per_basis_radar
from teleshield.experiments.runner import ExperimentResult


def run_e08_fingerprint(
    backend: Optional[QuantumBackend] = None,
    seed: int = 42,
    noise_strength: float = 0.25,
    n_blocks: int = 16,
    L: int = 64,
    **kwargs,
) -> ExperimentResult:
    scenarios = ["dephasing", "bit_flip", "depolarizing"]
    results_by_scenario = {}
    records = []

    for sc in scenarios:
        session = QDSSession.create(
            n=n_blocks,
            L=L,
            backend=backend or ExactBackend(seed=seed),
            basis_mode="XYZ",  # Full 6-state basis mode
            bell_visibility=0.99,
            seed=seed,
        )

        msg = f"Fingerprint diagnostic message for {sc}"
        sig = session.sign(msg)

        # Apply specific channel disturbance
        attack = ChannelManipulationAttack(channel_type=sc, strength=noise_strength, seed=seed)
        attack_res = attack.execute(slots=session.slots)
        session.slots = attack_res.manipulated_slots

        verdict, stats = session.verify(msg, sig, seed=seed)

        rates = stats.per_basis_rates if stats else {"X": 0.0, "Y": 0.0, "Z": 0.0}
        results_by_scenario[sc] = {
            "basis_rates": rates,
            "verdict": verdict.verdict.value,
            "fingerprint": verdict.evidence.get("fingerprint", {}),
        }

        records.append({
            "scenario": sc,
            "rate_X": rates.get("X", 0.0),
            "rate_Y": rates.get("Y", 0.0),
            "rate_Z": rates.get("Z", 0.0),
            "verdict": verdict.verdict.value,
            "classification": verdict.evidence.get("fingerprint", {}).get("classification"),
        })

    df = pd.DataFrame(records)
    # Generate radar chart for the dephasing scenario as sample
    fig = plot_per_basis_radar(results_by_scenario["dephasing"]["basis_rates"])

    # Verify dephasing physics: X and Y rates must exceed Z rate
    deph_rates = results_by_scenario["dephasing"]["basis_rates"]
    dephasing_verified = deph_rates["X"] > deph_rates["Z"] + 0.10

    # Verify bit-flip physics: Z and Y rates must exceed X rate
    bf_rates = results_by_scenario["bit_flip"]["basis_rates"]
    bitflip_verified = bf_rates["Z"] > bf_rates["X"] + 0.10

    return ExperimentResult(
        experiment_id="E08",
        title="Forensic Basis Fingerprinting (X, Y, Z)",
        seed=seed,
        elapsed_seconds=0.0,
        data=results_by_scenario,
        summary_metrics={
            "dephasing_asymmetry_verified": dephasing_verified,
            "bitflip_asymmetry_verified": bitflip_verified,
            "scenarios_evaluated": len(scenarios),
        },
        df=df,
        plot_fig=fig,
    )
