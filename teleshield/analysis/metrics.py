"""
Performance Metrics Module
Tracks computational latencies, throughput, memory consumption,
and quantum resource overhead.
"""

from __future__ import annotations
from dataclasses import dataclass, field
import time
import psutil
from typing import Dict, Any, Optional


@dataclass
class PerformanceBenchmarkReport:
    key_gen_time_ms: float
    bell_pair_time_ms: float
    teleportation_time_ms: float
    distribution_time_ms: float
    sign_time_ms: float
    verify_time_ms: float
    attack_time_ms: float
    total_states_consumed: int
    shots_per_second: float
    signatures_per_second: float
    memory_rss_mb: float
    sprt_average_samples: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key_gen_time_ms": self.key_gen_time_ms,
            "bell_pair_time_ms": self.bell_pair_time_ms,
            "teleportation_time_ms": self.teleportation_time_ms,
            "distribution_time_ms": self.distribution_time_ms,
            "sign_time_ms": self.sign_time_ms,
            "verify_time_ms": self.verify_time_ms,
            "attack_time_ms": self.attack_time_ms,
            "total_states_consumed": self.total_states_consumed,
            "shots_per_second": self.shots_per_second,
            "signatures_per_second": self.signatures_per_second,
            "memory_rss_mb": self.memory_rss_mb,
            "sprt_average_samples": self.sprt_average_samples,
        }


class PerformanceTracker:
    """Utility to measure execution times and memory consumption."""

    def __init__(self) -> None:
        self.process = psutil.Process()
        self.timers: Dict[str, float] = {}
        self.durations: Dict[str, float] = {}

    def start_timer(self, label: str) -> None:
        self.timers[label] = time.perf_counter()

    def stop_timer(self, label: str) -> float:
        start = self.timers.get(label, time.perf_counter())
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        self.durations[label] = elapsed_ms
        return elapsed_ms

    def get_memory_mb(self) -> float:
        try:
            return float(self.process.memory_info().rss / (1024 * 1024))
        except Exception:
            return 0.0

    def create_report(
        self,
        total_states: int = 0,
        total_shots: int = 10000,
        sprt_samples: float = 0.0,
    ) -> PerformanceBenchmarkReport:
        verify_ms = self.durations.get("verify", 1.0)
        sign_ms = self.durations.get("sign", 1.0)

        shots_per_sec = (total_shots / (verify_ms / 1000.0)) if verify_ms > 0 else 0.0
        sigs_per_sec = (1000.0 / (sign_ms + verify_ms)) if (sign_ms + verify_ms) > 0 else 0.0

        return PerformanceBenchmarkReport(
            key_gen_time_ms=self.durations.get("keygen", 0.0),
            bell_pair_time_ms=self.durations.get("bell", 0.0),
            teleportation_time_ms=self.durations.get("teleport", 0.0),
            distribution_time_ms=self.durations.get("distribution", 0.0),
            sign_time_ms=sign_ms,
            verify_time_ms=verify_ms,
            attack_time_ms=self.durations.get("attack", 0.0),
            total_states_consumed=total_states,
            shots_per_second=shots_per_sec,
            signatures_per_second=sigs_per_sec,
            memory_rss_mb=self.get_memory_mb(),
            sprt_average_samples=sprt_samples,
        )
