"""
Q-STAT Statistical Aggregation Module
Performs multi-dimensional statistical analysis across blocks (tag bit positions)
and quantum bases (X, Y, Z). Rejects simplistic single global metrics.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
import numpy as np

from teleshield.quantum.measurement import MeasurementResult
from teleshield.quantum.states import StateBasis


@dataclass
class BlockStatistics:
    """Statistical evidence collected for a single message tag bit block."""
    block_index: int
    bit_value: int
    L: int
    matches: int
    mismatches: int
    mismatch_rate: float
    basis_matches: Dict[str, int] = field(default_factory=dict)
    basis_mismatches: Dict[str, int] = field(default_factory=dict)
    basis_rates: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "block_index": self.block_index,
            "bit_value": self.bit_value,
            "L": self.L,
            "matches": self.matches,
            "mismatches": self.mismatches,
            "mismatch_rate": self.mismatch_rate,
            "basis_matches": self.basis_matches,
            "basis_mismatches": self.basis_mismatches,
            "basis_rates": self.basis_rates,
        }


@dataclass
class VerificationStatistics:
    """Holistic multi-dimensional evidence extracted from quantum measurements."""
    n_blocks: int
    L_per_block: int
    total_states: int
    total_matches: int
    total_mismatches: int
    global_mismatch_rate: float
    block_statistics: List[BlockStatistics]
    per_basis_rates: Dict[str, float]
    per_basis_counts: Dict[str, Dict[str, int]]
    max_block_rate: float
    min_block_rate: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "n_blocks": self.n_blocks,
            "L_per_block": self.L_per_block,
            "total_states": self.total_states,
            "total_matches": self.total_matches,
            "total_mismatches": self.total_mismatches,
            "global_mismatch_rate": self.global_mismatch_rate,
            "max_block_rate": self.max_block_rate,
            "min_block_rate": self.min_block_rate,
            "per_basis_rates": self.per_basis_rates,
            "per_basis_counts": self.per_basis_counts,
            "block_statistics": [b.to_dict() for b in self.block_statistics],
        }


def compute_verification_statistics(
    measurements: List[MeasurementResult],
    tag_bits: List[int],
    L: int,
) -> VerificationStatistics:
    """
    Computes rigorous per-block and per-basis mismatch metrics.
    measurements has length n * L, arranged by block j in [0, n-1] and k in [0, L-1].
    """
    n = len(tag_bits)
    total_states = len(measurements)
    if total_states != n * L:
        # If lengths differ, infer n or clamp
        n = max(1, total_states // max(1, L))

    block_stats: List[BlockStatistics] = []

    basis_totals = {
        "X": {"matches": 0, "mismatches": 0},
        "Y": {"matches": 0, "mismatches": 0},
        "Z": {"matches": 0, "mismatches": 0},
    }

    total_matches = 0
    total_mismatches = 0

    for j in range(n):
        bit_val = tag_bits[j] if j < len(tag_bits) else 0
        block_meas = measurements[j * L : (j + 1) * L]

        b_matches = 0
        b_mismatches = 0
        b_basis_m: Dict[str, int] = {"X": 0, "Y": 0, "Z": 0}
        b_basis_mm: Dict[str, int] = {"X": 0, "Y": 0, "Z": 0}

        for m in block_meas:
            b_name = m.basis.value
            if m.is_match:
                b_matches += 1
                total_matches += 1
                b_basis_m[b_name] = b_basis_m.get(b_name, 0) + 1
                basis_totals[b_name]["matches"] += 1
            else:
                b_mismatches += 1
                total_mismatches += 1
                b_basis_mm[b_name] = b_basis_mm.get(b_name, 0) + 1
                basis_totals[b_name]["mismatches"] += 1

        b_len = len(block_meas) if block_meas else 1
        b_rate = float(b_mismatches) / float(b_len)

        b_rates: Dict[str, float] = {}
        for b_name in ("X", "Y", "Z"):
            tot_b = b_basis_m[b_name] + b_basis_mm[b_name]
            b_rates[b_name] = float(b_basis_mm[b_name]) / float(tot_b) if tot_b > 0 else 0.0

        block_stats.append(
            BlockStatistics(
                block_index=j,
                bit_value=bit_val,
                L=b_len,
                matches=b_matches,
                mismatches=b_mismatches,
                mismatch_rate=b_rate,
                basis_matches=b_basis_m,
                basis_mismatches=b_basis_mm,
                basis_rates=b_rates,
            )
        )

    global_rate = float(total_mismatches) / float(max(1, total_states))
    block_rates = [b.mismatch_rate for b in block_stats]
    max_rate = float(max(block_rates)) if block_rates else 0.0
    min_rate = float(min(block_rates)) if block_rates else 0.0

    per_basis_rates = {}
    for b_name, counts in basis_totals.items():
        tot = counts["matches"] + counts["mismatches"]
        per_basis_rates[b_name] = float(counts["mismatches"]) / float(tot) if tot > 0 else 0.0

    return VerificationStatistics(
        n_blocks=n,
        L_per_block=L,
        total_states=total_states,
        total_matches=total_matches,
        total_mismatches=total_mismatches,
        global_mismatch_rate=global_rate,
        block_statistics=block_stats,
        per_basis_rates=per_basis_rates,
        per_basis_counts=basis_totals,
        max_block_rate=max_rate,
        min_block_rate=min_rate,
    )
