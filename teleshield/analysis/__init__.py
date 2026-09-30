"""
TeleShield Analysis Layer
Performance profiling, Plotly visualization generation, and forensic experiment reporting.
"""

from teleshield.analysis.metrics import PerformanceTracker, PerformanceBenchmarkReport
from teleshield.analysis.plots import (
    plot_forgery_vs_L,
    plot_false_rejection_vs_noise,
    plot_detection_vs_attack_strength,
    plot_teleportation_fidelity_vs_noise,
    plot_sprt_vs_fixed_L,
    plot_chsh_vs_visibility,
    plot_cusum_drift,
    plot_backend_parity,
    plot_hardware_comparison,
    plot_per_block_heatmap,
    plot_per_basis_radar,
)

__all__ = [
    "PerformanceTracker",
    "PerformanceBenchmarkReport",
    "plot_forgery_vs_L",
    "plot_false_rejection_vs_noise",
    "plot_detection_vs_attack_strength",
    "plot_teleportation_fidelity_vs_noise",
    "plot_sprt_vs_fixed_L",
    "plot_chsh_vs_visibility",
    "plot_cusum_drift",
    "plot_backend_parity",
    "plot_hardware_comparison",
    "plot_per_block_heatmap",
    "plot_per_basis_radar",
]
