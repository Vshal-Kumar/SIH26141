"""
Q-STAT CHSH Entanglement Monitor Module
Evaluates pre-flight quantum channel entanglement health using sacrificial Bell pairs.
Computes Clauser-Horne-Shimony-Holt (CHSH) S parameter against classical boundary (S <= 2)
and Tsirelson quantum bound (S <= 2 * sqrt(2)).
IMPORTANT: This is a channel-health diagnostic, not a complete proof of QDS security.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
import numpy as np

from teleshield.quantum.bell import create_bell_pair, BellState, compute_chsh_s, compute_werner_state


@dataclass
class CHSHHealthReport:
    """Diagnostic report on quantum channel entanglement quality."""
    visibility: float
    chsh_s: float
    classical_boundary: float
    tsirelson_bound: float
    violates_bell: bool
    status: str
    diagnostic_notes: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "visibility": self.visibility,
            "chsh_s": self.chsh_s,
            "classical_boundary": self.classical_boundary,
            "tsirelson_bound": self.tsirelson_bound,
            "violates_bell": self.violates_bell,
            "status": self.status,
            "diagnostic_notes": self.diagnostic_notes,
        }


class CHSHMonitor:
    """
    Monitors entanglement viability across the quantum distribution channel.
    Sacrifices dedicated Bell pairs prior to QDS key distribution.
    """

    CLASSICAL_BOUNDARY = 2.0
    TSIRELSON_BOUND = float(2.0 * np.sqrt(2.0))  # ~2.828427

    def __init__(self, target_min_visibility: float = 0.85) -> None:
        self.target_min_visibility = target_min_visibility

    def evaluate_channel(
        self,
        visibility: float = 1.0,
        sacrificial_pairs: int = 100,
    ) -> CHSHHealthReport:
        """
        Evaluates Werner-state CHSH parameter for given visibility.
        Theoretical relation: S = 2 * sqrt(2) * V.
        """
        v_clean = max(0.0, min(1.0, float(visibility)))
        rho = compute_werner_state(visibility=v_clean, bell_type=BellState.PHI_PLUS)
        s_val = compute_chsh_s(rho)

        violates = s_val > self.CLASSICAL_BOUNDARY

        if s_val > 2.4:
            status = "HEALTHY_ENTANGLED"
            notes = "Strong Bell non-locality confirmed. Channel is well-suited for high-fidelity teleportation."
        elif s_val > self.CLASSICAL_BOUNDARY:
            status = "MARGINAL_ENTANGLEMENT"
            notes = "Bell inequality violated, but visibility is degraded. Teleportation error rates will be elevated."
        else:
            status = "SEPARABLE_OR_CLASSICAL"
            notes = "Bell inequality NOT violated (S <= 2.0). Channel lacks non-local entanglement; teleportation will fail."

        return CHSHHealthReport(
            visibility=v_clean,
            chsh_s=float(s_val),
            classical_boundary=self.CLASSICAL_BOUNDARY,
            tsirelson_bound=self.TSIRELSON_BOUND,
            violates_bell=violates,
            status=status,
            diagnostic_notes=notes,
        )
