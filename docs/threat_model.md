# TeleShield Threat Model & Adversarial Analysis

## 1. Security Environment & Cryptographic Assumptions

TeleShield operates under standard Quantum Digital Signature (QDS) security assumptions:

1. **Authenticated Classical Channel:** Classical communication between Signer (Alice) and Verifiers (Bob) is authenticated but public. Adversaries cannot alter classical message transmissions without detection by MAC/digital signature, but can read all classical traffic.
2. **Untrusted Quantum Channel:** The quantum communication channel over which Bell pairs or states are distributed is completely untrusted. Adversaries may manipulate, intercept, replace, or inject noise into quantum states in transit.
3. **Secure Signer Key Generation:** The signer's random number generator and private key generation environment are trusted. The private key descriptions are never leaked to external parties.
4. **Physical State Consumption (No-Cloning):** Quantum states cannot be cloned. When a verifier measures stored quantum states, the states collapse and are physically destroyed (`status = CONSUMED`). A consumed slot cannot be re-measured.
5. **Memory Storage:** Verifiers maintain private quantum memory slots to store distributed quantum states until signature verification.

---

## 2. Adversarial Capabilities & Threat Vectors

TeleShield models eight distinct cyber and quantum threat vectors:

### 2.1 Random Forgery
* **Adversary Goal:** Forge a valid signature for an arbitrary message without knowledge of the signer's private key.
* **Mechanism:** The adversary generates pseudo-random basis and eigenvalue declarations for all revealed states in the signature envelope.
* **Expected Defense Outcome:** `FORGERY_SUSPECTED`. Random guessing in two mutually unbiased bases (X and Z) produces an expected mismatch rate of $p_f = 0.50$, overwhelmingly exceeding threshold $s_a \approx 0.04$.

### 2.2 Splice Forgery
* **Adversary Goal:** Construct a valid signature for Message B by splicing together revealed state descriptions from an authentic signature for Message A.
* **Mechanism:** The attacker maps identical tag positions between Message A and Message B, but for differing bits, re-inserts Alice's claims from Message A.
* **Expected Defense Outcome:** `FORGERY_SUSPECTED`. Bob measures his stored states at bit value $b_j(B)$, while Alice's revealed states were generated for $b_j(A)$. Because states for bit 0 and bit 1 are independently random, differing blocks exhibit ~50% mismatch. This demonstrates why per-block testing is mathematically mandatory.

### 2.3 Impersonation
* **Adversary Goal:** Masquerade as a legitimate signing authority (Alice) to deceive verifier Bob.
* **Mechanism:** Fabricates an entire signature envelope with valid message hashing but arbitrary state claims.
* **Expected Defense Outcome:** `IMPERSONATION_SUSPECTED`. Produces pervasive high mismatch rates clustering at 50% across all blocks.

### 2.4 Replay Attack
* **Adversary Goal:** Re-execute a previously accepted transaction by replaying an old signature envelope.
* **Mechanism:** Transmits a previously captured `QDSSignature` with unchanged nonce and timestamp.
* **Expected Defense Outcome:** `REPLAY`. Detected deterministically by the freshness registry or by checking if the corresponding quantum memory slots have already been consumed.

### 2.5 Intercept-Resend Attack
* **Adversary Goal:** Intercept quantum states during distribution or in memory, extract key information, and forward replacement states to Bob.
* **Mechanism:** Measures in a randomly chosen basis and prepares an eigenstate corresponding to the measurement outcome.
* **Expected Defense Outcome:** `CHANNEL_ANOMALY` / `FORGERY_SUSPECTED`. Because the adversary cannot know Alice's basis choice, guessing the wrong basis causes state collapse, introducing a mandatory 25% error in XZ mode and 33.3% in XYZ mode.

### 2.6 Channel Manipulation & Jamming
* **Adversary Goal:** Degrade or jam quantum transmission to deny service or exploit error-tolerance margins.
* **Mechanism:** Injects physical depolarizing, dephasing, bit-flip, or loss noise into the quantum channel.
* **Expected Defense Outcome:** `CHANNEL_ANOMALY`. Flagged when global or basis-specific mismatch rates exceed honest channel calibration tolerances.

### 2.7 Unauthorized Verification
* **Adversary Goal:** An unauthenticated third party (Charlie) attempts to verify a signature directed to Bob, or Bob attempts verification using keys belonging to another session.
* **Mechanism:** Submits verification requests with mismatched verifier identities or empty quantum slots.
* **Expected Defense Outcome:** `UNAUTHORIZED_VERIFICATION`.

### 2.8 Threshold-Aware Sub-Threshold Attacker
* **Adversary Goal:** Evade single-session hypothesis testing by injecting minimal perturbations strictly below the single-session acceptance threshold $s_a$.
* **Mechanism:** Operates with disturbance $\delta \in (\mu_0, s_a)$ across consecutive sessions.
* **Expected Defense Outcome:** Detected via multi-session **CUSUM control charts** (`CUSUMMonitor`) as cumulative drift crosses decision threshold $H$.
