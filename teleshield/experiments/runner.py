"""
Experiment Runner Module
Central execution harness managing parameter configurations, seed isolation,
data collection, plotting, and structured artifact persistence.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional, Callable
import json
import time
import pandas as pd

from teleshield.backends.base import QuantumBackend
from teleshield.backends.exact import ExactBackend


@dataclass
class ExperimentResult:
    """Standardized output container for any of the 14 TeleShield experiments."""
    experiment_id: str
    title: str
    seed: int
    elapsed_seconds: float
    data: Dict[str, Any]
    summary_metrics: Dict[str, Any]
    df: Optional[pd.DataFrame] = None
    plot_fig: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "title": self.title,
            "seed": self.seed,
            "elapsed_seconds": self.elapsed_seconds,
            "summary_metrics": self.summary_metrics,
            "data": self.data,
        }

    def save(self, output_dir: str = "experiments_output") -> Path:
        """Saves experiment JSON and CSV to output directory."""
        p = Path(output_dir)
        p.mkdir(parents=True, exist_ok=True)

        json_path = p / f"{self.experiment_id.lower()}_results.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

        if self.df is not None:
            csv_path = p / f"{self.experiment_id.lower()}_data.csv"
            self.df.to_csv(csv_path, index=False)

        if self.plot_fig is not None:
            html_path = p / f"{self.experiment_id.lower()}_plot.html"
            self.plot_fig.write_html(str(html_path))

        return json_path


class ExperimentRunner:
    """Orchestrates execution of the 14 reproducibility experiments."""

    def __init__(
        self,
        default_backend: Optional[QuantumBackend] = None,
        default_seed: int = 42,
        output_dir: str = "experiments_output",
    ) -> None:
        self.default_backend = default_backend or ExactBackend()
        self.default_seed = default_seed
        self.output_dir = output_dir

    def run(
        self,
        experiment_id: str,
        backend: Optional[QuantumBackend] = None,
        seed: Optional[int] = None,
        **kwargs,
    ) -> ExperimentResult:
        """Executes a specific experiment by ID (e.g. 'E01', 'E02', ..., 'E14')."""
        exp_id = experiment_id.upper()
        b = backend or self.default_backend
        s = seed if seed is not None else self.default_seed

        registry = self.get_registry()
        if exp_id not in registry:
            raise ValueError(f"Unknown experiment ID '{exp_id}'. Available: {list(registry.keys())}")

        func = registry[exp_id]
        start_t = time.perf_counter()
        result = func(backend=b, seed=s, **kwargs)
        elapsed = time.perf_counter() - start_t
        result.elapsed_seconds = elapsed

        # Auto-save results
        result.save(self.output_dir)
        return result

    def run_all(self, **kwargs) -> Dict[str, ExperimentResult]:
        """Runs all 14 experiments sequentially."""
        results = {}
        for exp_id in self.get_registry():
            results[exp_id] = self.run(exp_id, **kwargs)
        return results

    @staticmethod
    def get_registry() -> Dict[str, Callable]:
        from teleshield.experiments.e01_teleportation import run_e01_teleportation
        from teleshield.experiments.e02_honest_qds import run_e02_honest_qds
        from teleshield.experiments.e03_forgery import run_e03_forgery
        from teleshield.experiments.e04_splice import run_e04_splice
        from teleshield.experiments.e05_replay import run_e05_replay
        from teleshield.experiments.e06_impersonation import run_e06_impersonation
        from teleshield.experiments.e07_channel import run_e07_channel
        from teleshield.experiments.e08_fingerprint import run_e08_fingerprint
        from teleshield.experiments.e09_chsh import run_e09_chsh
        from teleshield.experiments.e10_security import run_e10_security
        from teleshield.experiments.e11_sprt import run_e11_sprt
        from teleshield.experiments.e12_cusum import run_e12_cusum
        from teleshield.experiments.e13_backend_parity import run_e13_backend_parity
        from teleshield.experiments.e14_hardware_profiles import run_e14_hardware_profiles

        return {
            "E01": run_e01_teleportation,
            "E02": run_e02_honest_qds,
            "E03": run_e03_forgery,
            "E04": run_e04_splice,
            "E05": run_e05_replay,
            "E06": run_e06_impersonation,
            "E07": run_e07_channel,
            "E08": run_e08_fingerprint,
            "E09": run_e09_chsh,
            "E10": run_e10_security,
            "E11": run_e11_sprt,
            "E12": run_e12_cusum,
            "E13": run_e13_backend_parity,
            "E14": run_e14_hardware_profiles,
        }


if __name__ == "__main__":
    import argparse
    from teleshield.backends.aer import AerBackend
    from teleshield.backends.stim import StimBackend

    parser = argparse.ArgumentParser(description="TeleShield Experiment Execution Runner")
    parser.add_argument("--exp", nargs="+", help="Specific experiment IDs to run (e.g. E01 E02 E03)")
    parser.add_argument("--all", action="store_true", help="Run all 14 experiments sequentially")
    parser.add_argument("--backend", choices=["exact", "aer", "stim"], default="exact", help="Quantum simulation backend")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed for reproducibility")
    parser.add_argument("--outdir", default="experiments_output", help="Output directory for CSV, JSON, and HTML reports")

    args = parser.parse_args()

    if args.backend == "aer":
        selected_backend = AerBackend(seed=args.seed)
    elif args.backend == "stim":
        selected_backend = StimBackend(seed=args.seed)
    else:
        selected_backend = ExactBackend(seed=args.seed)

    runner = ExperimentRunner(default_backend=selected_backend, default_seed=args.seed, output_dir=args.outdir)

    target_exps = []
    if args.all:
        target_exps = list(runner.get_registry().keys())
    elif args.exp:
        target_exps = [e.upper() for e in args.exp]
    else:
        target_exps = ["E01"]

    print(f"=== TeleShield Experiment Execution Harness ===")
    print(f"Backend: {args.backend} | Seed: {args.seed} | Target Output: {args.outdir}")
    print(f"Selected Experiments: {target_exps}\n")

    for exp_id in target_exps:
        print(f"--> Running {exp_id}...")
        res = runner.run(exp_id, backend=selected_backend, seed=args.seed)
        print(f"    Completed in {res.elapsed_seconds:.3f}s: {res.summary_metrics}")

    print(f"\nAll requested experiments completed. Artifacts saved to: {args.outdir}/")
