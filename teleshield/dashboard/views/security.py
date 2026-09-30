"""
Dashboard View 5: Security Analysis & Research Benchmarks
Interactive research console displaying mathematical security bounds,
Monte Carlo curves, SPRT efficiency, CHSH non-locality, and backend parity.
Professional styling with zero emojis.
"""

import streamlit as st
from teleshield.security.calculator import SecurityParameterCalculator
from teleshield.experiments.e03_forgery import run_e03_forgery
from teleshield.experiments.e09_chsh import run_e09_chsh
from teleshield.experiments.e11_sprt import run_e11_sprt
from teleshield.experiments.e12_cusum import run_e12_cusum
from teleshield.experiments.e14_hardware_profiles import run_e14_hardware_profiles


@st.cache_data(show_spinner=False)
def get_cached_e03():
    return run_e03_forgery(n_blocks=16, trials_per_L=3)


@st.cache_data(show_spinner=False)
def get_cached_e11():
    return run_e11_sprt(fixed_L=128, num_trials=5)


@st.cache_data(show_spinner=False)
def get_cached_e09():
    return run_e09_chsh()


@st.cache_data(show_spinner=False)
def get_cached_e12():
    return run_e12_cusum(num_sessions=25, attack_start_session=10)


@st.cache_data(show_spinner=False)
def get_cached_e14():
    return run_e14_hardware_profiles(n_blocks=8, L=24, shots=200)


def render_security_page():
    st.markdown("## Security Analysis & Mathematical Bounds")
    st.caption("Information-theoretic security sizing, Hoeffding exponential bounds, and empirical validation.")

    # Interactive Security Calculator
    with st.expander("Interactive Security Parameter Sizing Calculator", expanded=True):
        calc_col1, calc_col2, calc_col3 = st.columns(3)
        with calc_col1:
            n_in = st.number_input("Message Tag Bits (n)", min_value=16, max_value=256, value=64, step=16)
            L_in = st.number_input("Configured States per Bit (L)", min_value=16, max_value=1000, value=222, step=16)
        with calc_col2:
            eps_in = st.number_input("Expected Honest Channel Noise (epsilon)", min_value=0.001, max_value=0.10, value=0.01, step=0.005, format="%.3f")
            model_in = st.selectbox("Adversary Threat Model", ["random_guessing", "intercept_resend", "optimal_cloning"], index=0)
        with calc_col3:
            p_fr_target = st.number_input("Target False Rejection Probability (alpha)", min_value=1e-12, max_value=1e-2, value=1e-6, format="%.1e")
            p_fa_target = st.number_input("Target Forgery Acceptance (beta)", min_value=1e-12, max_value=1e-2, value=1e-6, format="%.1e")

        calc = SecurityParameterCalculator()
        rec = calc.calculate(
            n=int(n_in),
            L=int(L_in),
            epsilon=float(eps_in),
            target_false_rejection=float(p_fr_target),
            target_forgery_probability=float(p_fa_target),
            attacker_model=model_in,
        )

        r_col1, r_col2, r_col3, r_col4 = st.columns(4)
        with r_col1:
            st.metric("Recommended Min L", f"{rec.recommended_min_L}")
        with r_col2:
            st.metric("Acceptance Threshold s_a", f"{rec.acceptance_threshold:.4f}")
        with r_col3:
            st.metric("Forgery Acceptance Bound P_FA", f"{rec.forgery_acceptance_bound:.2e}")
        with r_col4:
            st.metric("Security Parameter", f"{rec.security_bits:.1f} bits")

    st.markdown("---")
    st.markdown("### Research Experiment Visualizations")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Forgery vs L (E03)",
        "Adaptive SPRT (E11)",
        "CHSH Bell Metric (E09)",
        "CUSUM Drift (E12)",
        "Hardware Comparison (E14)",
    ])

    with tab1:
        st.markdown("#### Analytical Hoeffding Bound vs Empirical Forgery Acceptance")
        with st.spinner("Loading Forgery vs L simulation..."):
            res_e03 = get_cached_e03()
        st.plotly_chart(res_e03.plot_fig, width="stretch")

    with tab2:
        st.markdown("#### Adaptive SPRT vs Fixed-Sample Verification")
        with st.spinner("Loading SPRT comparison..."):
            res_e11 = get_cached_e11()
        st.plotly_chart(res_e11.plot_fig, width="stretch")
        st.caption(f"Adaptive SPRT achieved **{res_e11.summary_metrics['honest_saving_pct']:.1f}% sample savings** on honest verification.")

    with tab3:
        st.markdown("#### Werner State Entanglement Visibility & Bell Non-Locality")
        with st.spinner("Loading CHSH analysis..."):
            res_e09 = get_cached_e09()
        st.plotly_chart(res_e09.plot_fig, width="stretch")

    with tab4:
        st.markdown("#### CUSUM Accumulation for Sub-Threshold Evasion Attackers")
        with st.spinner("Loading CUSUM accumulation..."):
            res_e12 = get_cached_e12()
        st.plotly_chart(res_e12.plot_fig, width="stretch")

    with tab5:
        st.markdown("#### Hardware Profile Comparison: Ideal vs Ion-Trap vs Rydberg")
        with st.spinner("Loading hardware profile benchmark..."):
            res_e14 = get_cached_e14()
        st.plotly_chart(res_e14.plot_fig, width="stretch")
