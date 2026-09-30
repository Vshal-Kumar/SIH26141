import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def create_slide1_diagram():
    fig, ax = plt.subplots(figsize=(10, 8.2), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8.6)
    ax.axis('off')

    # Main Card Container with soft gradient feel
    container = patches.FancyBboxPatch((0.15, 0.15), 9.7, 8.3,
                                      boxstyle="round,pad=0.15,rounding_size=0.35",
                                      facecolor='#F8FAFC', edgecolor='#0070C0', linewidth=2.2)
    ax.add_patch(container)

    # Title Banner inside container
    banner = patches.FancyBboxPatch((0.45, 7.4), 9.1, 0.85,
                                   boxstyle="round,pad=0.1,rounding_size=0.18",
                                   facecolor='#002060', edgecolor='none')
    ax.add_patch(banner)
    ax.text(5.0, 7.85, "TELESHIELD END-TO-END QUANTUM PIPELINE", 
            ha='center', va='center', color='#FFFFFF', fontsize=12.5, fontweight='bold', family='sans-serif')
    ax.text(5.0, 7.55, "Information-Theoretic Teleportation QDS • Deterministic Q-STAT Engine (0% AI/ML)", 
            ha='center', va='center', color='#38BDF8', fontsize=8.8, fontweight='bold', family='sans-serif')

    # Pipeline Stages (Vertical Stack)
    stages = [
        {"num": "01", "title": "MESSAGE & PAULLI EIGENSTATES", "sub": "M ∈ {0,1}^k • Tag bits n=64, L=222 states/bit • Z, X, Y bases", "color": "#0284C7", "y": 6.45},
        {"num": "02", "title": "BELL-STATE EPR DISTRIBUTION", "sub": "Entangled pairs |Φ⁺⟩ = (|00⟩ + |11⟩)/√2 • CHSH health check S = 2√2V", "color": "#0369A1", "y": 5.35},
        {"num": "03", "title": "QUANTUM TELEPORTATION & CORRECTION", "sub": "Bell-basis measurement (CNOT + H) • Feed-forward Pauli X^{m1} Z^{m0}", "color": "#1D4ED8", "y": 4.25},
        {"num": "04", "title": "VERIFIER PROJECTIVE MEASUREMENT", "sub": "Non-demolition storage • Projective readout in X/Z (extended X/Y/Z)", "color": "#4338CA", "y": 3.15},
        {"num": "05", "title": "Q-STAT DETERMINISTIC THREAT TRIAGE", "sub": "Binomial hypothesis testing • Chernoff threshold s_a • SPRT & CUSUM", "color": "#0D9488", "y": 2.05},
        {"num": "06", "title": "VERDICT & HASH-CHAINED AUDIT", "sub": "ACCEPT / REJECT • 10 attack classes fingerprinted • Immutable audit log", "color": "#059669", "y": 0.95}
    ]

    for i, stg in enumerate(stages):
        # Card
        box = patches.FancyBboxPatch((0.7, stg["y"] - 0.35), 8.6, 0.78,
                                     boxstyle="round,pad=0.08,rounding_size=0.14",
                                     facecolor='#FFFFFF', edgecolor=stg["color"], linewidth=1.6)
        ax.add_patch(box)
        
        # Number badge
        num_box = patches.FancyBboxPatch((0.85, stg["y"] - 0.24), 0.75, 0.56,
                                         boxstyle="round,pad=0.06,rounding_size=0.10",
                                         facecolor=stg["color"], edgecolor='none')
        ax.add_patch(num_box)
        ax.text(1.22, stg["y"] + 0.04, stg["num"], ha='center', va='center', color='#FFFFFF', fontsize=11, fontweight='bold', family='sans-serif')

        # Text
        ax.text(1.85, stg["y"] + 0.12, stg["title"], ha='left', va='center', color='#0F172A', fontsize=10.2, fontweight='bold', family='sans-serif')
        ax.text(1.85, stg["y"] - 0.14, stg["sub"], ha='left', va='center', color='#475569', fontsize=8.2, family='sans-serif')

        # Arrow down to next
        if i < len(stages) - 1:
            ax.annotate('', xy=(5.0, stg["y"] - 0.42), xytext=(5.0, stg["y"] - 0.33),
                        arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.4", color='#0070C0', lw=2.2))

    plt.tight_layout()
    plt.savefig("slide1_teleshield_pipeline.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Created slide1_teleshield_pipeline.png")

def create_slide3_circuit():
    fig, ax = plt.subplots(figsize=(10, 4.4), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.6)
    ax.axis('off')

    # Border
    container = patches.FancyBboxPatch((0.1, 0.1), 9.8, 4.4,
                                      boxstyle="round,pad=0.1,rounding_size=0.22",
                                      facecolor='#FFFFFF', edgecolor='#0070C0', linewidth=1.8)
    ax.add_patch(container)

    # Header
    ax.text(0.3, 4.15, "TELEPORTATION-BASED QDS CIRCUIT ARCHITECTURE & MEASUREMENT", 
            ha='left', va='center', color='#002060', fontsize=11, fontweight='bold')
    ax.text(0.3, 3.82, "EPR Distribution → Bell Joint Measurement (CNOT + H) → Pauli Feed-Forward X^{m1}Z^{m0} → Verifier Readout", 
            ha='left', va='center', color='#0284C7', fontsize=8.5, fontweight='bold')

    # Qubit lines (Signer Q0, Bell Pair A Q1, Bell Pair B Q2)
    y_q0, y_q1, y_q2 = 2.95, 1.95, 0.95

    # Labels
    ax.text(0.25, y_q0, r"$|\psi_j\rangle$ (Signature)", va='center', fontsize=9.5, fontweight='bold', color='#1E293B')
    ax.text(0.25, y_q1, r"$|0\rangle_A$ (Bell Half)", va='center', fontsize=9.5, fontweight='bold', color='#1E293B')
    ax.text(0.25, y_q2, r"$|0\rangle_B$ (Verifier)", va='center', fontsize=9.5, fontweight='bold', color='#1E293B')

    # Qubit wires
    ax.plot([1.75, 9.4], [y_q0, y_q0], color='#64748B', lw=1.8)
    ax.plot([1.75, 6.2], [y_q1, y_q1], color='#64748B', lw=1.8)
    ax.plot([1.75, 9.4], [y_q2, y_q2], color='#64748B', lw=1.8)

    # EPR generation on Q1, Q2
    # H gate on Q1
    h1 = patches.Rectangle((2.15, y_q1 - 0.32), 0.55, 0.64, facecolor='#E0F2FE', edgecolor='#0284C7', lw=1.6)
    ax.add_patch(h1)
    ax.text(2.425, y_q1, "H", ha='center', va='center', fontsize=10, fontweight='bold', color='#0369A1')

    # CNOT from Q1 to Q2
    ax.plot([3.1, 3.1], [y_q1, y_q2], color='#0284C7', lw=2.2)
    ax.scatter([3.1], [y_q1], color='#0284C7', s=60, zorder=5)
    t1 = plt.Circle((3.1, y_q2), 0.20, facecolor='#FFFFFF', edgecolor='#0284C7', lw=2.2, zorder=5)
    ax.add_patch(t1)
    ax.plot([3.1, 3.1], [y_q2 - 0.20, y_q2 + 0.20], color='#0284C7', lw=2.2, zorder=6)
    ax.plot([3.1 - 0.20, 3.1 + 0.20], [y_q2, y_q2], color='#0284C7', lw=2.2, zorder=6)
    ax.text(3.28, 1.45, r"$|\Phi^+\rangle$", color='#0369A1', fontsize=9.5, fontweight='bold')

    # Teleportation: CNOT from Q0 to Q1
    ax.plot([4.2, 4.2], [y_q0, y_q1], color='#4338CA', lw=2.2)
    ax.scatter([4.2], [y_q0], color='#4338CA', s=60, zorder=5)
    t2 = plt.Circle((4.2, y_q1), 0.20, facecolor='#FFFFFF', edgecolor='#4338CA', lw=2.2, zorder=5)
    ax.add_patch(t2)
    ax.plot([4.2, 4.2], [y_q1 - 0.20, y_q1 + 0.20], color='#4338CA', lw=2.2, zorder=6)
    ax.plot([4.2 - 0.20, 4.2 + 0.20], [y_q1, y_q1], color='#4338CA', lw=2.2, zorder=6)

    # H gate on Q0
    h0 = patches.Rectangle((4.8, y_q0 - 0.32), 0.55, 0.64, facecolor='#EDE9FE', edgecolor='#4338CA', lw=1.6)
    ax.add_patch(h0)
    ax.text(5.075, y_q0, "H", ha='center', va='center', fontsize=10, fontweight='bold', color='#4338CA')

    # Measurement meters on Q0, Q1
    m0 = patches.Rectangle((5.7, y_q0 - 0.32), 0.65, 0.64, facecolor='#F1F5F9', edgecolor='#475569', lw=1.6)
    ax.add_patch(m0)
    ax.text(6.025, y_q0, r"$\mathcal{M}_{0}$", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#0F172A')

    m1 = patches.Rectangle((5.7, y_q1 - 0.32), 0.65, 0.64, facecolor='#F1F5F9', edgecolor='#475569', lw=1.6)
    ax.add_patch(m1)
    ax.text(6.025, y_q1, r"$\mathcal{M}_{1}$", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#0F172A')

    # Classical Feed-forward channels (dashed)
    ax.annotate('', xy=(7.15, y_q2 + 0.35), xytext=(6.35, y_q0),
                arrowprops=dict(arrowstyle="->", color='#D97706', lw=1.6, ls='--'))
    ax.annotate('', xy=(6.95, y_q2 + 0.35), xytext=(6.35, y_q1),
                arrowprops=dict(arrowstyle="->", color='#D97706', lw=1.6, ls='--'))
    ax.text(6.4, 2.4, "Classical Feed-Forward (m0, m1)", color='#D97706', fontsize=8, fontweight='bold')

    # Pauli Correction Gate X^{m1} Z^{m0} on Q2
    corr = patches.Rectangle((6.8, y_q2 - 0.32), 1.05, 0.64, facecolor='#FEF3C7', edgecolor='#D97706', lw=1.8)
    ax.add_patch(corr)
    ax.text(7.325, y_q2, r"$X^{m_1} Z^{m_0}$", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#B45309')

    # Verifier Readout / Projective Measurement
    ax.text(8.0, y_q2 + 0.28, r"$|\psi_j\rangle$", color='#059669', fontsize=9, fontweight='bold')
    meas_v = patches.Rectangle((8.45, y_q2 - 0.32), 0.85, 0.64, facecolor='#DCFCE7', edgecolor='#16A34A', lw=1.8)
    ax.add_patch(meas_v)
    ax.text(8.875, y_q2, r"$\Pi_{X/Z}$", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#15803D')

    # Output to Q-STAT
    ax.annotate('', xy=(9.7, y_q2), xytext=(9.3, y_q2),
                arrowprops=dict(arrowstyle="->,head_width=0.3,head_length=0.4", color='#16A34A', lw=2.2))
    ax.text(9.45, y_q2 + 0.28, "Q-STAT", color='#15803D', fontsize=8, fontweight='bold')

    plt.tight_layout()
    plt.savefig("slide3_quantum_circuit.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Created slide3_quantum_circuit.png")

if __name__ == '__main__':
    create_slide1_diagram()
    create_slide3_circuit()
