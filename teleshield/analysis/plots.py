"""
Plotly Interactive Visualization Module
Generates production-grade Plotly charts for quantum digital signature security,
forensic evidence, attack detection, and hardware profile comparisons.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Theme styling constants
PRIMARY_COLOR = "#00d2ff"
SECONDARY_COLOR = "#7928ca"
ACCENT_COLOR = "#ff0080"
SUCCESS_COLOR = "#00f5a0"
DANGER_COLOR = "#ff4b4b"
BG_DARK = "#0e1117"
CARD_BG = "#161b22"
GRID_COLOR = "#2d3748"


def apply_dark_theme(fig: go.Figure, title: str, xaxis_title: str = "", yaxis_title: str = "") -> go.Figure:
    """Applies modern dark aesthetic consistent with Streamlit and cybersecurity tooling."""
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>",
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            "font": {"size": 18, "color": "#f0f6fc", "family": "Inter, Roboto, sans-serif"}
        },
        paper_bgcolor=BG_DARK,
        plot_bgcolor=CARD_BG,
        font={"color": "#c9d1d9", "family": "Inter, Roboto, sans-serif"},
        xaxis={
            "title": f"<b>{xaxis_title}</b>",
            "gridcolor": GRID_COLOR,
            "zerolinecolor": GRID_COLOR,
            "showline": True,
            "linecolor": "#484f58",
        },
        yaxis={
            "title": f"<b>{yaxis_title}</b>",
            "gridcolor": GRID_COLOR,
            "zerolinecolor": GRID_COLOR,
            "showline": True,
            "linecolor": "#484f58",
        },
        legend={
            "bgcolor": "rgba(22, 27, 34, 0.8)",
            "bordercolor": "#30363d",
            "borderwidth": 1,
        },
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def plot_forgery_vs_L(
    L_values: List[int],
    analytical_bounds: List[float],
    simulated_points: Optional[List[float]] = None,
) -> go.Figure:
    """Plots Forgery Acceptance Probability P_FA vs L on logarithmic scale."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=L_values,
        y=analytical_bounds,
        mode="lines",
        name="Hoeffding Analytical Bound",
        line=dict(color=PRIMARY_COLOR, width=3),
    ))
    if simulated_points:
        fig.add_trace(go.Scatter(
            x=L_values[:len(simulated_points)],
            y=simulated_points,
            mode="markers+lines",
            name="Empirical Monte Carlo",
            marker=dict(size=8, color=ACCENT_COLOR, symbol="diamond"),
            line=dict(dash="dot", color=ACCENT_COLOR),
        ))
    fig.update_yaxes(type="log")
    return apply_dark_theme(fig, "Forgery Acceptance Probability vs Qubits per Bit (L)", "L (States per Bit Value)", "P_FA (Log Scale)")


def plot_false_rejection_vs_noise(
    noise_levels: List[float],
    analytical_bounds: List[float],
    simulated_points: Optional[List[float]] = None,
) -> go.Figure:
    """Plots False Rejection Probability P_FR vs Channel Noise."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=noise_levels,
        y=analytical_bounds,
        mode="lines",
        name="Analytical False Rejection Bound",
        line=dict(color=SECONDARY_COLOR, width=3),
    ))
    if simulated_points:
        fig.add_trace(go.Scatter(
            x=noise_levels[:len(simulated_points)],
            y=simulated_points,
            mode="markers+lines",
            name="Simulated Rejection Rate",
            marker=dict(size=8, color=SUCCESS_COLOR, symbol="circle"),
            line=dict(dash="dash", color=SUCCESS_COLOR),
        ))
    return apply_dark_theme(fig, "Honest False Rejection Rate vs Channel Noise", "Channel Noise Rate (epsilon)", "False Rejection Probability P_FR")


def plot_detection_vs_attack_strength(
    strengths: List[float],
    detection_probabilities: List[float],
    attack_label: str = "Attack",
) -> go.Figure:
    """Plots detection rate as a function of adversarial disturbance strength."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=strengths,
        y=detection_probabilities,
        mode="lines+markers",
        name="Q-STAT Detection Rate",
        line=dict(color=DANGER_COLOR, width=3),
        marker=dict(size=8, color=DANGER_COLOR),
        fill="tozeroy",
        fillcolor="rgba(255, 75, 75, 0.15)",
    ))
    fig.add_hline(y=1.0, line_dash="dash", line_color=SUCCESS_COLOR, annotation_text="Ideal 100% Detection")
    return apply_dark_theme(fig, f"Detection Probability vs {attack_label} Strength", "Attack Perturbation Strength", "Empirical Detection Probability")


def plot_teleportation_fidelity_vs_noise(
    noise_levels: List[float],
    fidelities: List[float],
) -> go.Figure:
    """Plots output quantum state fidelity vs depolarizing / dephasing rate."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=noise_levels,
        y=fidelities,
        mode="lines+markers",
        name="Teleported State Fidelity",
        line=dict(color=SUCCESS_COLOR, width=3),
        marker=dict(size=7, color=SUCCESS_COLOR),
    ))
    fig.add_hline(y=0.5, line_dash="dot", line_color=DANGER_COLOR, annotation_text="Classical Limit (F=0.5)")
    return apply_dark_theme(fig, "Teleportation State Fidelity vs Physical Noise", "Noise Parameter (p)", "Fidelity F = |<psi_in|psi_out>|^2")


def plot_sprt_vs_fixed_L(
    fixed_L: int,
    sprt_samples: List[int],
    labels: List[str],
) -> go.Figure:
    """Compares sample overhead of fixed-L protocol against adaptive SPRT."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels,
        y=[fixed_L] * len(labels),
        name="Fixed-L Protocol",
        marker_color="#484f58",
    ))
    fig.add_trace(go.Bar(
        x=labels,
        y=sprt_samples,
        name="Adaptive SPRT",
        marker_color=PRIMARY_COLOR,
    ))
    fig.update_layout(barmode="group")
    return apply_dark_theme(fig, "Measurement Requirement: Fixed-L vs Adaptive SPRT", "Test Scenario", "Samples Measured per Block")


def plot_chsh_vs_visibility(
    visibilities: List[float],
    s_values: List[float],
) -> go.Figure:
    """Plots CHSH S parameter vs Werner state visibility."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=visibilities,
        y=s_values,
        mode="lines+markers",
        name="Observed CHSH S",
        line=dict(color=PRIMARY_COLOR, width=3),
        marker=dict(size=7, color=PRIMARY_COLOR),
    ))
    fig.add_hline(y=2.0, line_dash="dash", line_color=DANGER_COLOR, annotation_text="Classical Boundary (S = 2.0)")
    fig.add_hline(y=float(2.0 * np.sqrt(2.0)), line_dash="dot", line_color=SUCCESS_COLOR, annotation_text="Tsirelson Bound (2*sqrt(2) ~ 2.828)")
    return apply_dark_theme(fig, "CHSH Entanglement Metric S vs Werner Visibility", "Werner State Visibility V", "CHSH Parameter S")


def plot_cusum_drift(
    sessions: List[int],
    cusum_values: List[float],
    decision_threshold: float,
) -> go.Figure:
    """Plots CUSUM cumulative statistic across consecutive verification sessions."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sessions,
        y=cusum_values,
        mode="lines+markers",
        name="CUSUM Statistic C_t",
        line=dict(color=ACCENT_COLOR, width=3),
        marker=dict(size=8, color=ACCENT_COLOR),
        fill="tozeroy",
        fillcolor="rgba(255, 0, 128, 0.15)",
    ))
    fig.add_hline(y=decision_threshold, line_dash="dash", line_color=DANGER_COLOR, annotation_text=f"Decision Threshold H={decision_threshold:.3f}")
    return apply_dark_theme(fig, "CUSUM Multi-Session Drift Accumulator", "Verification Session Index", "Cumulative Sum Statistic C_t")


def plot_backend_parity(
    exact_rates: List[float],
    aer_rates: List[float],
    stim_rates: List[float],
    block_indices: List[int],
) -> go.Figure:
    """Plots per-block mismatch rate comparison across Exact, Aer, and Stim backends."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=block_indices, y=exact_rates, mode="lines+markers", name="Exact NumPy", line=dict(color=PRIMARY_COLOR, width=2)))
    fig.add_trace(go.Scatter(x=block_indices, y=aer_rates, mode="lines+markers", name="Qiskit Aer", line=dict(color=SECONDARY_COLOR, width=2)))
    fig.add_trace(go.Scatter(x=block_indices, y=stim_rates, mode="lines+markers", name="Stim Tableau", line=dict(color=SUCCESS_COLOR, width=2, dash="dot")))
    return apply_dark_theme(fig, "Backend Parity: Per-Block Mismatch Rate Distribution", "Tag Block Index", "Observed Mismatch Rate")


def plot_hardware_comparison(
    profiles: List[str],
    fidelities: List[float],
    error_rates: List[float],
) -> go.Figure:
    """Compares average fidelity and error rates across hardware profiles."""
    fig = go.Figure()
    fig.add_trace(go.Bar(x=profiles, y=fidelities, name="Teleportation Fidelity", marker_color=SUCCESS_COLOR))
    fig.add_trace(go.Bar(x=profiles, y=error_rates, name="Baseline Error Rate", marker_color=DANGER_COLOR))
    fig.update_layout(barmode="group")
    return apply_dark_theme(fig, "Hardware Profile Comparison: Ideal vs Ion-Trap vs Rydberg", "Hardware Profile", "Metric Value")


def plot_per_block_heatmap(
    block_mismatches: List[float],
    threshold: float,
) -> go.Figure:
    """Bar chart / heatmap visualization of per-block mismatch rates."""
    n_blocks = len(block_mismatches)
    colors = [DANGER_COLOR if m > threshold else SUCCESS_COLOR for m in block_mismatches]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[f"B{i}" for i in range(n_blocks)],
        y=block_mismatches,
        marker_color=colors,
        name="Block Mismatch Rate",
    ))
    fig.add_hline(y=threshold, line_dash="dash", line_color="#f0f6fc", annotation_text=f"Threshold s_a={threshold:.3f}")
    return apply_dark_theme(fig, "Per-Block Quantum Mismatch Rate", "Tag Position / Block Index", "Mismatch Rate m_j")


def plot_per_basis_radar(
    basis_rates: Dict[str, float],
) -> go.Figure:
    """Radar / polar chart displaying basis asymmetry (X, Y, Z)."""
    categories = ["X", "Y", "Z"]
    values = [basis_rates.get("X", 0.0), basis_rates.get("Y", 0.0), basis_rates.get("Z", 0.0)]
    # Close the polygon
    categories.append(categories[0])
    values.append(values[0])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill="toself",
        name="Observed Mismatch",
        line=dict(color=PRIMARY_COLOR, width=3),
        fillcolor="rgba(0, 210, 255, 0.2)",
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max(0.6, max(values) * 1.2)], gridcolor=GRID_COLOR),
            angularaxis=dict(gridcolor=GRID_COLOR),
            bgcolor=CARD_BG,
        ),
        paper_bgcolor=BG_DARK,
        font={"color": "#c9d1d9"},
        title={"text": "<b>Per-Basis Error Dispersion (X, Y, Z)</b>", "x": 0.5, "font": {"color": "#f0f6fc"}},
    )
    return fig
