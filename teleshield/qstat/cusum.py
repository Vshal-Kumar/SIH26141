"""
Q-STAT CUSUM Drift Monitor Module
Implements Cumulative Sum (CUSUM) quality control chart to detect subtle,
persistent deviations across multiple verification sessions.
Targeted specifically against threshold-aware adversaries operating just below
the single-session acceptance threshold s_a.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional


class CUSUMState(str, Enum):
    NORMAL = "NORMAL"
    DRIFT = "DRIFT"
    ANOMALY = "ANOMALY"


@dataclass
class CUSUMStatus:
    state: CUSUMState
    current_cusum: float
    decision_threshold: float
    mean_baseline: float
    slack_parameter: float
    session_count: int
    history: List[float] = field(default_factory=list)
    cusum_history: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "current_cusum": self.current_cusum,
            "decision_threshold": self.decision_threshold,
            "mean_baseline": self.mean_baseline,
            "slack_parameter": self.slack_parameter,
            "session_count": self.session_count,
            "recent_rates": self.history[-10:],
            "recent_cusum": self.cusum_history[-10:],
        }


class CUSUMMonitor:
    """
    Cumulative Sum control chart tracking session-to-session quantum error rates.
    Accumulates evidence of low-level disturbance over time.
    """

    def __init__(
        self,
        baseline_rate: float = 0.01,
        detectable_shift: float = 0.015,
        decision_threshold: float = 0.04,
    ) -> None:
        self.baseline_rate = float(baseline_rate)
        # Slack K = (shift - baseline) / 2
        self.slack_k = float((detectable_shift - baseline_rate) / 2.0)
        self.decision_threshold = float(decision_threshold)

        self._current_cusum = 0.0
        self._history: List[float] = []
        self._cusum_history: List[float] = []

    def update(self, session_mismatch_rate: float) -> CUSUMStatus:
        """
        Ingests the global mismatch rate of a completed verification session.
        Updates CUSUM: S_t = max(0, S_{t-1} + (rate - baseline - K)).
        """
        rate = float(session_mismatch_rate)
        self._history.append(rate)

        # CUSUM recurrence
        step_increment = rate - self.baseline_rate - self.slack_k
        self._current_cusum = max(0.0, self._current_cusum + step_increment)
        self._cusum_history.append(self._current_cusum)

        # Classify state
        if self._current_cusum >= self.decision_threshold:
            state = CUSUMState.ANOMALY
        elif self._current_cusum > (self.decision_threshold * 0.4):
            state = CUSUMState.DRIFT
        else:
            state = CUSUMState.NORMAL

        return CUSUMStatus(
            state=state,
            current_cusum=self._current_cusum,
            decision_threshold=self.decision_threshold,
            mean_baseline=self.baseline_rate,
            slack_parameter=self.slack_k,
            session_count=len(self._history),
            history=list(self._history),
            cusum_history=list(self._cusum_history),
        )

    def reset(self) -> None:
        """Reset history and accumulator."""
        self._current_cusum = 0.0
        self._history.clear()
        self._cusum_history.clear()
