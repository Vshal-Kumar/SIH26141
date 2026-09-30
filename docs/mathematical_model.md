# TeleShield: Mathematical and Quantum Physical Model

## 1. Quantum State Formalism

A single-qubit quantum state in Hilbert space $\mathcal{H}_2 \cong \mathbb{C}^2$ is expressed in the computational basis $\{|0\rangle, |1\rangle\}$ as:

$$|\psi\rangle = \alpha |0\rangle + \beta |1\rangle, \quad |\alpha|^2 + |\beta|^2 = 1$$

In density matrix formalism, a general pure or mixed state $\rho \in \mathcal{S}(\mathcal{H}_2)$ satisfies:

$$\rho = \rho^\dagger, \quad \mathrm{Tr}(\rho) = 1, \quad \rho \ge 0$$

Using the Bloch sphere representation with Pauli vector $\vec{\sigma} = (X, Y, Z)$:

$$\rho = \frac{1}{2}\left(I + r_x X + r_y Y + r_z Z\right), \quad |\vec{r}| \le 1$$

### 1.1 Pauli Eigenstates

TeleShield supports two primary bases (XZ) and full six-state tomography (XYZ):

* **$Z$-Basis (Computational):**
  $$|0\rangle = \begin{pmatrix}1 \\ 0\end{pmatrix} \quad (\lambda = +1), \qquad |1\rangle = \begin{pmatrix}0 \\ 1\end{pmatrix} \quad (\lambda = -1)$$

* **$X$-Basis (Hadamard):**
  $$|+\rangle = \frac{1}{\sqrt{2}}\left(|0\rangle + |1\rangle\right) \quad (\lambda = +1), \qquad |-\rangle = \frac{1}{\sqrt{2}}\left(|0\rangle - |1\rangle\right) \quad (\lambda = -1)$$

* **$Y$-Basis (Circular):**
  $$|+y\rangle = \frac{1}{\sqrt{2}}\left(|0\rangle + i|1\rangle\right) \quad (\lambda = +1), \qquad |-y\rangle = \frac{1}{\sqrt{2}}\left(|0\rangle - i|1\rangle\right) \quad (\lambda = -1)$$

---

## 2. Entangled Bell States and Quantum Teleportation

The four maximally entangled two-qubit Bell states forming an orthonormal basis of $\mathcal{H}_4$ are:

$$|\Phi^+\rangle = \frac{1}{\sqrt{2}}\left(|00\rangle + |11\rangle\right), \qquad |\Phi^-\rangle = \frac{1}{\sqrt{2}}\left(|00\rangle - |11\rangle\right)$$
$$|\Psi^+\rangle = \frac{1}{\sqrt{2}}\left(|01\rangle + |10\rangle\right), \qquad |\Psi^-\rangle = \frac{1}{\sqrt{2}}\left(|01\rangle - |10\rangle\right)$$

The canonical resource for TeleShield public-key distribution is $|\Phi^+\rangle$, generated via:

$$|\Phi^+\rangle = \mathrm{CNOT}_{0 \to 1} \left(H \otimes I\right) |00\rangle$$

### 2.1 Teleportation Protocol

To transmit an unknown quantum state $|\psi\rangle_0 = \alpha |0\rangle + \beta |1\rangle$ from Alice to Bob using shared Bell pair $|\Phi^+\rangle_{12}$:

1. **Initial Composite State:**
   $$|\Psi_0\rangle = |\psi\rangle_0 \otimes |\Phi^+\rangle_{12} = \frac{1}{\sqrt{2}} \left[ \alpha |0\rangle (|00\rangle + |11\rangle) + \beta |1\rangle (|00\rangle + |11\rangle) \right]$$

2. **Alice's Bell-State Measurement Operations:**
   Alice applies $\mathrm{CNOT}_{0 \to 1}$ followed by $H_0$:
   $$|\Psi_1\rangle = \frac{1}{2} \left[ |00\rangle (\alpha |0\rangle + \beta |1\rangle) + |01\rangle (\alpha |1\rangle + \beta |0\rangle) + |10\rangle (\alpha |0\rangle - \beta |1\rangle) + |11\rangle (\alpha |1\rangle - \beta |0\rangle) \right]$$

3. **Measurement Outcomes $(m_0, m_1)$:**
   Alice performs projective $Z$-measurements on qubits 0 and 1, obtaining classical bits $m_0, m_1 \in \{0, 1\}$.

4. **Bob's Unitary Correction:**
   Bob applies Pauli operator $U_{\text{corr}} = X^{m_1} Z^{m_0}$ to qubit 2:
   * $(0, 0) \implies X^0 Z^0 = I \implies \alpha |0\rangle + \beta |1\rangle = |\psi\rangle$
   * $(0, 1) \implies X^1 Z^0 = X \implies X(\alpha |1\rangle + \beta |0\rangle) = |\psi\rangle$
   * $(1, 0) \implies X^0 Z^1 = Z \implies Z(\alpha |0\rangle - \beta |1\rangle) = |\psi\rangle$
   * $(1, 1) \implies X^1 Z^1 = XZ \implies XZ(\alpha |1\rangle - \beta |0\rangle) = |\psi\rangle$ (up to global phase)

In the presence of channel noise parameterized by Werner visibility $V$:
$$\rho_W(V) = V |\Phi^+\rangle\langle\Phi^+| + \frac{1-V}{4} I_4$$
The teleported output state experiences depolarizing degradation with fidelity:
$$F = \langle\psi|\rho_{\text{out}}|\psi\rangle = \frac{1 + 3V}{4}$$

---

## 3. Quantum Digital Signature (QDS) Architecture

### 3.1 Key Generation
For a message tag of $n$ bits, the signer generates $L$ Pauli eigenstates for every bit value $b \in \{0, 1\}$ at each tag position $j \in \{0, \dots, n-1\}$.

* **Private Key $K_{\text{priv}}$:** Classical descriptions:
  $$\{(j, b, k, \text{basis}_{j,b,k}, \text{eigenvalue}_{j,b,k}) \mid j \in [0, n-1], b \in \{0, 1\}, k \in [0, L-1]\}$$
* **Quantum Public Key $K_{\text{pub}}$:** $2nL$ physical single-qubit states teleported into verifier memory slots.

### 3.2 Message Binding
* **Mode 1 (SHA-256):** Cryptographic collision-resistant hash (computational security).
* **Mode 2 (Toeplitz / EAU):** $\epsilon$-almost universal hash family over $\mathrm{GF}(2)$ providing information-theoretic bounds:
  $$\mathrm{Tag} = T \cdot x \pmod 2$$

### 3.3 Signing & Verification
* **Signing:** For message $M$, calculate $n$-bit tag $T = (b_0, b_1, \dots, b_{n-1})$. Reveal the $L$ private key descriptions for each $b_j$.
* **Verification:** For each block $j$, the verifier measures the stored quantum states in slot $(j, b_j, k)$ using the revealed basis. Mismatches are counted:
  $$m_j = \frac{N_{\text{mismatch}, j}}{L}$$

---

## 4. Statistical Verification & Hoeffding Bounds

Each verification measurement in block $j$ is modelled as a Bernoulli trial:
$$X_j \sim \mathrm{Binomial}(L, p)$$
where $p = \epsilon$ for honest channels and $p = p_f = 0.50$ for random guessing.

### 4.1 Acceptance Threshold $s_a$
Using Hoeffding's inequality, the probability that honest noise $\epsilon$ produces an observed rate exceeding $s_a$ across $n$ blocks is bounded by target false rejection $\alpha$:

$$P_{\text{FR, total}} \le n \exp\left(-2L(s_a - \epsilon)^2\right) \le \alpha$$
$$\implies s_a = \epsilon + \sqrt{\frac{\ln(n / \alpha)}{2L}}$$

### 4.2 Forgery Acceptance Bound
The probability that an adversary guessing states accepts in a given block is bounded by:

$$P_{\text{FA}} \le \exp\left(-2L(p_f - s_a)^2\right)$$
For $n$ blocks, total security parameter $\sec = -\log_2(P_{\text{FA, total}})$.
