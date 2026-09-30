"""
Q-STAT Sequential Probability Ratio Testing (SPRT) Module
Implements Wald's sequential analysis for adaptive, low-latency hypothesis testing.
Compares:
  H0: p = p0 (Honest channel noise, e.g. eps = 0.01)
  H1: p = p1 (Adversarial disturbance / forgery, e.g. p = 0.50)
Stops as soon as statistical confidence threshold is crossed.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from teleshield.quantum.measurement import MeasurementResult


@dataclass
class SPRTResult:
    decision: str  # "ACCEPT", "REJECT", "INCONCLUSIVE"
    samples_used: int
    total_samples: int
    log_likelihood_ratio: float
    upper_threshold: float  # ln(A)
    lower_threshold: float  # ln(B)
    sample_saving_pct: float
    mismatches: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision,
            "samples_used": self.samples_used,
            "total_samples": self.total_samples,
            "log_likelihood_ratio": self.log_likelihood_ratio,
            "upper_threshold": self.upper_threshold,
            "lower_threshold": self.lower_threshold,
            "sample_saving_pct": self.sample_saving_pct,
            "mismatches": self.mismatches,
        }


class SPRTVerifier:
    """
    Wald's Sequential Probability Ratio Test verifier.
    Drastically minimizes required quantum measurements for clear honest/attack states.
    """

    def __init__(
        self,
        p0: float = 0.01,  # Honest error rate
        p1: float = 0.50,  # Attacker error rate
        alpha: float = 1e-6,  # Target false rejection probability
        beta: float = 1e-6,   # Target false acceptance probability
    ) -> None:
        self.p0 = max(1e-6, min(0.49, float(p0)))
        self.p1 = max(self.p0 + 1e-3, min(0.99, float(p1)))
        self.alpha = max(1e-15, float(alpha))
        self.beta = max(1e-15, float(beta))

        # Wald thresholds
        # A = (1 - beta) / alpha  => reject H0, accept H1 (Adversary detected)
        # B = beta / (1 - alpha)  => accept H0, reject H1 (Honest verified)
        self.ln_A = np.log((1.0 - self.beta) / self.alpha)
        self.ln_B = np.log(self.beta / (1.0 - self.alpha))

        # Precompute log-likelihood increments
        self.ll_mismatch = np.log(self.p1 / self.p0)
        self.ll_match = np.log((1.0 - self.p1) / (1.0 - self.p0))

    def evaluate_sequential(
        self,
        measurements: List[MeasurementResult],
    ) -> SPRTResult:
        """
        Sequentially steps through measurements, accumulating log-likelihood ratio.
        Stops immediately once evidence boundary ln(A) or ln(B) is crossed.
        """
        cum_llr = 0.0
        mismatches = 0
        total = len(measurements)

        for step, m in enumerate(measurements, 1):
            if not m.is_match:
                cum_llr += self.ll_mismatch
                mismatches += 1
            else:
                cum_llr += self.ll_match

            # Check stopping boundaries
            if cum_llr >= self.ln_A:
                # Evidence strongly favors H1 (attack/forgery)
                savings = ((total - step) / total * 100.0) if total > 0 else 0.0
                return SPRTResult(
                    decision="REJECT",
                    samples_used=step,
                    total_samples=total,
                    log_likelihood_ratio=float(cum_llr),
                    upper_threshold=float(self.ln_A),
                    lower_threshold=float(self.ln_B),
                    sample_saving_pct=float(savings),
                    mismatches=mismatches,
                )
            elif cum_llr <= self.ln_B:
                # Evidence strongly favors H0 (honest)
                savings = ((total - step) / total * 100.0) if total > 0 else 0.0
                return SPRTResult(
                    decision="ACCEPT",
                    samples_used=step,
                    total_samples=total,
                    log_likelihood_ratio=float(cum_llr),
                    upper_threshold=float(self.ln_A),
                    lower_threshold=float(self.ln_B),
                    sample_saving_pct=float(savings),
                    mismatches=mismatches,
                )

        # Reached end of sequence without crossing boundary
        return SPRTResult(
            decision="INCONCLUSIVE",
            samples_used=total,
            total_samples=total,
            log_likelihood_ratio=float(cum_llr),
            upper_threshold=float(self.ln_A),
            lower_threshold=float(self.ln_B),
            sample_saving_pct=0.0,
            mismatches=mismatches,
        )
