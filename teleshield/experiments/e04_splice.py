"""
Experiment E04: Splice Forgery Localized Block Detection
Executes a signature splice attack, demonstrating why per-block hypothesis testing
is mathematically required: spliced blocks exhibit elevated error (~50%) while
unspliced blocks remain below the honest noise threshold.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
import numpy as np
import pandas as pd

from teleshield.backends.base import QuantumBackend
from teleshield.backends.exact import ExactBackend
from teleshield.qds.session import QDSSession
from teleshield.attacks.splice import SpliceForgeryAttack
from teleshield.analysis.plots import plot_per_block_heatmap
from teleshield.experiments.runner import ExperimentResult


def run_e04_splice(
    backend: Optional[QuantumBackend] = None,
    seed: int = 42,
    n_blocks: int = 16,
    L: int = 64,
    target_spliced_blocks: Optional[List[int]] = None,
    **kwargs,
) -> ExperimentResult:
    target_spliced = target_spliced_blocks or [3, 7, 11]

    session = QDSSession.create(
        n=n_blocks,
        L=L,
        backend=backend or ExactBackend(seed=seed),
        bell_visibility=0.99,
        seed=seed,
    )

    msg_donor = "Authorize transaction Alpha for amount $5,000"
    msg_target = "Authorize transaction Bravo for amount $500,000"

    donor_sig = session.sign(msg_donor)

    # Execute splice attack targeting specific blocks
    attack = SpliceForgeryAttack(target_blocks=target_spliced, strength=1.0, seed=seed)
    attack_res = attack.execute(donor_signature=donor_sig, target_message=msg_target)

    # Verify spliced signature
    verdict, stats = session.verify(
        message=msg_target,
        signature=attack_res.manipulated_signature,
        seed=seed,
    )

    block_rates = [b.mismatch_rate for b in stats.block_statistics] if stats else [0.0] * n_blocks
    threshold = verdict.threshold or 0.045

    records = []
    if stats:
        for b in stats.block_statistics:
            records.append({
                "block_index": b.block_index,
                "bit_value": b.bit_value,
                "mismatch_rate": b.mismatch_rate,
                "is_spliced": b.block_index in target_spliced,
                "exceeded_threshold": b.mismatch_rate > threshold,
            })

    df = pd.DataFrame(records)
    fig = plot_per_block_heatmap(block_rates, threshold)

    detected_spliced_blocks = [
        b.block_index for b in stats.block_statistics if b.mismatch_rate > threshold
    ] if stats else []

    return ExperimentResult(
        experiment_id="E04",
        title="Splice Forgery Localized Block Detection",
        seed=seed,
        elapsed_seconds=0.0,
        data={
            "ground_truth_spliced": target_spliced,
            "detected_blocks": detected_spliced_blocks,
            "block_mismatch_rates": block_rates,
            "verdict": verdict.verdict.value,
            "threshold": threshold,
        },
        summary_metrics={
            "verdict": verdict.verdict.value,
            "splice_detected": verdict.verdict.value in ("FORGERY_SUSPECTED", "REJECT"),
            "perfect_localization": set(target_spliced).issubset(set(detected_spliced_blocks)),
        },
        df=df,
        plot_fig=fig,
    )
