# TeleShield Security Analysis & Bound Derivations

## 1. Mathematical Security Bound Derivations

Let $L$ be the number of quantum states per bit value, $n$ be the message tag length, and $\epsilon$ be the calibrated honest quantum channel error rate.

### 1.1 Hoeffding Bound on False Rejection
For an honest transmission, measurement outcomes $X_1, \dots, X_L \in \{0, 1\}$ are independent Bernoulli random variables with $\mathbb{E}[X_i] = \epsilon$.
The observed error rate in block $j$ is $m_j = \frac{1}{L} \sum_{i=1}^L X_i$.

By Hoeffding's inequality, for any threshold $s_a > \epsilon$:
$$P(m_j \ge s_a) \le \exp\left(-2L(s_a - \epsilon)^2\right)$$

Applying Boole's inequality (union bound) across all $n$ tag blocks, the probability of falsely rejecting an authentic signature is bounded by:
$$P_{\text{FR, total}} \le \sum_{j=1}^n P(m_j \ge s_a) \le n \exp\left(-2L(s_a - \epsilon)^2\right)$$

To guarantee $P_{\text{FR, total}} \le \alpha$ (target false rejection probability):
$$n \exp\left(-2L(s_a - \epsilon)^2\right) \le \alpha \implies 2L(s_a - \epsilon)^2 \ge \ln\left(\frac{n}{\alpha}\right)$$
$$\implies s_a = \epsilon + \sqrt{\frac{\ln(n / \alpha)}{2L}}$$

This proves that the acceptance threshold $s_a$ is derived strictly from protocol parameters rather than arbitrary heuristic assignment.

---

### 1.2 Bound on Forgery Acceptance
In a random forgery attack or impersonation attempt, an adversary without the private key guesses bases independently.
Because the X and Z bases are mutually unbiased:
$$|\langle 0 | + \rangle|^2 = |\langle 0 | - \rangle|^2 = |\langle 1 | + \rangle|^2 = |\langle 1 | - \rangle|^2 = \frac{1}{2}$$
The adversary's probability of producing a mismatch when Bob measures in Alice's basis is $p_f = \frac{1}{2}$.

For the adversary's forged signature to be accepted in block $j$, the observed mismatch rate must fall at or below $s_a$:
$$P(m_j \le s_a) \le \exp\left(-2L(p_f - s_a)^2\right)$$

For $n$ independent forged blocks, the forgery acceptance probability is exponentially suppressed:
$$P_{\text{FA, total}} \le \left[\exp\left(-2L(p_f - s_a)^2\right)\right]^n$$
The cryptographic security level in bits is:
$$\sec = -\log_2(P_{\text{FA, total}}) \ge 2nL(p_f - s_a)^2 \log_2(e)$$

---

## 2. Sequential Analysis: Wald's SPRT

To minimize measurement overhead during low-noise operations, TeleShield integrates Wald's Sequential Probability Ratio Test (SPRT).
Let $H_0: p = p_0$ (honest channel, e.g. $\epsilon = 0.01$) and $H_1: p = p_1$ (forged signature, e.g. $p_f = 0.50$).

For measurement outcomes $x_1, x_2, \dots, x_m \in \{0, 1\}$ (where $1$ denotes mismatch):
The cumulative log-likelihood ratio $\Lambda_m$ is:
$$\Lambda_m = \sum_{i=1}^m \ln \frac{P(x_i \mid p_1)}{P(x_i \mid p_0)} = k \ln\left(\frac{p_1}{p_0}\right) + (m - k) \ln\left(\frac{1 - p_1}{1 - p_0}\right)$$

### Decision Boundaries:
$$\ln A = \ln\left(\frac{1 - \beta}{\alpha}\right), \qquad \ln B = \ln\left(\frac{\beta}{1 - \alpha}\right)$$
* If $\Lambda_m \ge \ln A$: Stop measurement immediately; accept $H_1$ (flag attack / reject signature).
* If $\Lambda_m \le \ln B$: Stop measurement immediately; accept $H_0$ (accept signature as authentic).
* Otherwise: Measure next quantum state.

Empirical evaluation in Experiment E11 confirms that SPRT reduces required quantum measurements by **70% to 85%** compared to fixed-sample testing.

---

## 3. Important System Limitations

1. **Simulation Platform:** TeleShield is a classical simulation of quantum physics running on classical hardware. It does not interface with cryogenically cooled physical QPUs.
2. **Qubit Overhead Scaling:** Total required quantum states scale as $2nL$. For $n=64$ and $L=222$, this entails 28,416 quantum states, necessitating efficient quantum memory multiplexing in physical implementations.
3. **Forensic Ambiguity:** When physical disturbances produce isotropic, uniform errors across all bases, statistical measurements alone cannot uniquely identify the root cause (e.g. depolarizing channel noise vs random intercept-resend). TeleShield explicitly flags this ambiguity using careful "consistent with" terminology.
4. **Multi-Party Non-Repudiation:** TeleShield implements two-party teleportation-based QDS (Signer $\to$ Verifier). Full multi-party non-repudiation with verifier symmetrization and dispute resolution is reserved for extended multi-verifier protocols.
