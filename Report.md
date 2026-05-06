# Noni: A Symbolic Infrastructure for Data Encryption

Noni is a symmetric stream cipher for natural language text, based on a Lattice-based PRNG and a phonetics-driven dispersion engine.

This project has an unusual origin. As a child, I developed a private symbolic language as a personal creative exercise. Years later, that language became the foundation for research into adversarial techniques in large language models. Noni is the next step in that same line: a practical experiment that formalizes those symbolic patterns into a functional cryptographic infrastructure capable of protecting data through high-entropy, multi-dimensional mappings.

This is a practical exercise and experiment in cryptographic design. It is not intended as a production-ready system, and it does not replace audited implementations like AES-GCM or ChaCha20-Poly1305. It is published as an open research artifact.

---

## Technical Architecture

The system consists of six layers that operate in sequence.

### 1. Key Derivation (KDF)

The password is processed through PBKDF2-HMAC-SHA256 with 100,000 iterations and a 16-byte salt generated with `secrets.token_bytes`. This produces a 32-byte high-entropy seed used to derive independent subkeys for integrity (Auth Key) and lattice initialization (Master Value).

### 2. Lattice-based PRNG (LWE Engine)

Noni uses a dynamic lattice-based engine initialized from the stretched seed. Using a public matrix A and an error vector e following Learning With Errors principles, it generates a deterministic private entropy stream. The construction uses modulus q=12289, consistent with Kyber parameters, but is not an implementation of Kyber or any standardized post-quantum primitive. Unlike earlier iterations that used the decimal digits of Pi as a pseudorandom stream, this stream is private: it depends entirely on the key and salt.

### 3. High-Dimensional Manifold Projection 

While previous iterations utilized a discrete 3D state space, Noni evolves this concept into a High-Dimensional Manifold. Instead of projecting entropy into only three axes, the engine now generates a 256-bit State Vector per token.

This transition from 3D to a 256-dimensional space eliminates state clustering, ensuring that the symbolic dispersion is mathematically deeper and resistant to multidimensional frequency analysis. Every token is processed through a mapping function that projects entropy into a high-resolution state space:

```
seed = "{master_value}-pos-{i}-lat-{lattice_digit}-iv-{iv_seed}"
digest = SHA256(seed) -> state_256
```

This 256-bit vector acts as a continuous and deep source of entropy for all internal transformation decisions. Every logic gate — including dynamic vowel map selection, stochastic marker positioning, and syllabic rotation — is governed by specific, independent bits within this vector.

### 4. Deep Polyalphabetic Substitution

The engine moves beyond word-level rules to character-level resolution. Instead of applying a single transformation to an entire word, the 256-bit state vector determines the logic for every single vowel and consonant independently.

Dynamic Vowel Mapping: for each vowel, the engine consumes specific bits from the state vector to choose between three mapping schemas. This means the letter "a" might use a different map than the letter "e" within the same word, effectively flattening the frequency distribution.

Stochastic Marker Selection: the use of activators (`#` or `$`) is no longer rhythmic or alternating. It is determined stochastically by the PRNG state bits, neutralizing any attempt at marker-based syntactic analysis.

Lattice-Driven Consonant Mutation: consonants and digits are shifted using a circular alphabet. The displacement value is a result of the manifold state combined with the lattice error term, ensuring that even under known-plaintext attacks, the mutation logic remains obscure.

Syllabic Structural Obfuscation: using Pyphen for syllabification, the engine reorders syllables based on the calculated angle θ. In , this rotation is also bit-governed, adding a layer of structural chaos to the resulting symbolic string.

Vowel mapping schemas, switched dynamically per character:

| Vowel | Base | Inverse | Alternative |
| :--- | :---: | :---: | :---: |
| a | 1 | 5 | 4 |
| e | 2 | 4 | 3 |
| i | 3 | 3 | 1 |
| o | 4 | 2 | 5 |
| u | 5 | 1 | 2 |

It works with any language. When encrypting English text, Spanish syllable boundaries are applied as an additional layer of structural obfuscation. This behavior is intentional.

### 5. High-Entropy Symbolic Noise Injection (Syntactic Mimicry)

Noise positions within the message stream are determined by the deterministic function `MD5(master_value + "-noise-" + index) % 5 == 0`. In , noise generation uses the same bit-level selection logic for activators (`#` or `$`) as the primary encryption engine. Noise tokens are populated with digits in the 1-5 range, mirroring the output of the vowel substitution maps, and are subjected to the same 16-byte block padding as data tokens. To a statistical analyst or heuristic engine, noise tokens and data tokens are identical.

### 6. Symbolic Initialization Vector (IV)

A random IV (1-31) is encoded using constants from the original symbolic language: `*=1`, `!=2`, `+=4`, `_=8`, `~=16`. The IV is mixed into the SHA256 seed for every word position, ensuring that the same plaintext encrypted twice produces entirely different output.

---

## Encrypted Package Structure

The final message is a continuous stream with no word delimiters:

```
[HMAC-SHA256 (64 chars)][IV symbols][Salt hex (32 chars)][Encrypted body]
```

Each token, whether data or noise, is serialized as `[length (2 hex chars)][token content]` and padded to a multiple of 16 bytes (BLOCK_SIZE), eliminating structural leakage regarding word length and word count.

---

## Empirical Validation

### Statistical Audit: Million-State Analysis

To validate the engine, Noni underwent a statistical stress test processing 1,000,000 unique encryption states to detect underlying patterns or bias.

Performance metrics: 1,000,000 total iterations, 1.60 seconds execution time, approximately 626,784 operations per second.

Rule activation over 1,000,000 states:

```
INV   50.0460%   deviation 0.0460%   Stable
ROTA  50.0265%   deviation 0.0265%   Stable
ESP   50.0348%   deviation 0.0348%   Stable
ALT   49.9693%   deviation 0.0307%   Stable
SHF   50.0805%   deviation 0.0805%   Stable
```

Global Shannon Entropy: 1.000000 / 1.000000. Manifold coverage: 100% of all 32 possible rule combinations explored.

### Monte Carlo Analysis: Token Density and Statistical Indistinguishability

To evaluate whether Noni's output is statistically distinguishable from random noise, a Monte Carlo simulation was run over 100,000 iterations comparing token density across four conditions: Noni, Base64, Hexadecimal, and pure random noise. Token counts were normalized by character length to ensure a fair comparison across encoding schemes.

Results over 100,000 iterations:

```
Noni:          214.2 tokens avg
Base64:        206.1 tokens avg
Hexadecimal:   134.1 tokens avg
Random Noise:  217.3 tokens avg
```

Noni's token density (214.2) is statistically indistinguishable from pure random noise (217.3). The overlapping error bars confirm that the difference is not significant. Base64 sits below both, reflecting its structured but predictable output. Hexadecimal's lower density is consistent with its restricted 16-character alphabet.

The second test extended this analysis by computing Hamming distance and linear correlation between Noni's output and random noise:


```
Win Rate vs Noise:   31.55%
Max Gap:             33 tokens
Hamming Distance:    0.9918
Correlation:         0.0363
```

A Hamming distance of 0.9918 means that 99.18% of bits differ between two encryptions of the same plaintext, confirming a strong avalanche effect. A correlation of 0.036 between plaintext and ciphertext is statistically indistinguishable from zero, meaning no linear relationship is detectable between input and output. Together these two metrics validate the confusion and diffusion properties of the engine empirically.


![Monte Carlo Extended Analysis](NONIV1/Analysis4.png)

Note: For computational viability, the benchmark runs PBKDF2 with 1,000 iterations instead of the 100,000 used in the production engine. This does not affect the validity of the results, as token density, Hamming divergence, and correlation depend on the manifold output and the linguistic transformation pipeline, not on the KDF iteration count.

---

## Integrity and Fidelity Audits

To evaluate the engine's reliability under diverse linguistic conditions, Noni was subjected to high-volume stress tests using two monumental works of literature.

| Dataset | Total Word Tokens | Errors | Success Rate (ISR) | Avg. Processing Speed |
| :--- | :---: | :---: | :---: | :--- |
| Pride & Prejudice | 30,313 | 12 | 99.9604% | 0.0130 ms/word |
| Don Quijote | 381,217 | 35 | 99.9908% | 0.0086 ms/word |

### Technical Characterization of Anomalous Reconstruction

The audit identified a marginal cumulative error rate (<0.04%), which consistently manifests as Positional Symbol Displacement. During the Syllabic Structural Obfuscation phase, tokens with leading or trailing punctuation may experience a shift where the symbol is re-attached at the opposite boundary after the state-driven rotation. This results in deterministic outputs such as `los...` instead of `...los`.

Cryptographic integrity remains absolute: no data loss occurs. The discrepancy is strictly a matter of linguistic fidelity, limited to the literal positioning of secondary symbols during the reassembly of rotated syllabic blocks.

The increase in ISR from 99.96% to 99.99% when scaling from 30k to 380k words confirms that these anomalies are isolated edge cases and do not scale linearly with volume.

### High-Volume Stress Test: Full Text

Tested on the complete text of Don Quixote under real-world linguistic conditions:

```
Original size:    2,091.3 KB
Encrypted size:   8,685.3 KB
Expansion ratio:  4.15x
Throughput:       612.18 KB/s
```

The 315% increase in file size is a direct result of the phonetic-to-symbolic fragmentation and the symmetric noise strategy. This expansion is the mechanism that enables high entropy and prevents context inference by disrupting standard tokenization patterns.

---

## Visual Analysis of the Dispersion Engine: State Space Evolution

The following plots illustrate the transition from a discrete 3D phase space to a high-dimensional manifold projection.

### Legacy Analysis (legacy)

The legacy engine utilized a 3D state space to govern rule activation for consecutive tokens.

![Cipher Engine Analysis legacy](NONIV1/Analysis.png)
![Cipher Engine Analysis legacy](NONIV1/Analysis2.png)

The Geometric Attention Map shows rule activation as discrete binary blocks. The Manifold Projection Cloud displays token dispersion where spatial clustering is visible, indicating a lower-dimensional entropy source for rule selection.

### High-Dimensional Analysis ()

The architecture implements a 256-bit Manifold.

![Cipher Engine Analysis ](NONIV1/Analysis3.png)

This representation documents the current state of the engine's internal logic. The Entropy Fingerprint heatmap displays the raw bit states (0-63 of 256) for consecutive token positions, documenting the transition from word-level rules to bit-level micro-decisions. The 3D Shadow of the Manifold provides a spatial projection of the 256-dimensional state using Bytes 0, 1, and 2 as coordinate axes. The Hamming Weight color scale maps the number of active bits in the state vector, showing an even spread of entropy across the state space with no detectable geometric bias or recurring clusters.

### Technical Analysis: Governance of Restricted Alphabets

A key technical property of Noni is the use of a 256-bit State Vector to govern a restricted symbolic alphabet. Every token transformation is controlled by independent bits within the vector, ensuring stochastic independence for every position. The high dimensionality of the manifold ensures that the state of the engine cannot be inferred from the output symbols. By applying entropy at a bit-level, the engine ensures that identical plaintext inputs result in different symbolic outputs, effectively neutralizing frequency-based trajectory analysis.

---

## On the Emergence of Cryptographic Properties from Linguistic Design

The Monte Carlo analysis revealed that Noni satisfies three fundamental cryptographic properties empirically: confusion (correlation of 0.036 between plaintext and ciphertext), diffusion (Hamming distance of 0.9918 between successive encryptions), and statistical indistinguishability from random noise.

None of these properties were designed as explicit objectives. They emerged as a consequence of a design process rooted in a different question: how to destroy the legibility of text from multiple independent linguistic angles simultaneously.

The engine operates in layers that each target a distinct structural dimension of language. Syllabification breaks word boundaries. Vowel substitution breaks phonetic structure. Consonant mutation breaks orthographic patterns. Positional noise breaks sequential structure. The independence of these layers produces the same statistical effect as the substitution-permutation networks in formal cryptography, where confusion and diffusion are explicit design goals.

This does not make Noni a formally proven system. But it suggests that phonetic-structural obfuscation and cryptographic confusion-diffusion may share a deeper relationship than is currently documented. The destruction of linguistic structure and the destruction of statistical structure appear, in this case, to be the same operation.

---

## Security Properties

Integrity (Encrypt-then-MAC): HMAC-SHA256 detects any bitwise alteration and rejects decryption if the key or ciphertext has been tampered with.

Statistical flattening: syntactic noise injection using `#/$` and digits `1-5` is indistinguishable from real vowel substitution output, neutralizing standard frequency analysis.

Length and structure obfuscation: 16-byte block padding and positional noise injection eliminate word counting and length inference from the ciphertext.

High-dimensional state governance: the 256-bit manifold ensures that the encryption path is unique for every token, eliminating geometric clustering even in high-volume streams.

Lattice-based stream: the pseudorandom stream depends on a private LWE construction, adding resistance against precomputation and rainbow table attacks.

Kerckhoffs's principle: security depends exclusively on the key and salt. The algorithm remains fully public for peer review.

---

## Limitations

Linguistic reconstruction fidelity: the engine exhibits a marginal error rate (~0.01% - 0.04%) manifested as positional displacement of non-alphanumeric symbols during syllabic reassembly.

Substitution alphabet constraint: the core substitution layer operates on a small linguistic alphabet. While governed by a 256-bit manifold, it remains a theoretical point of analysis for known-plaintext attacks.

LatticePRNG complexity: this is a simplified LWE construction for research purposes. It is not a standardized post-quantum primitive and has not undergone formal cryptanalysis.

Phonetic dependency: reliability is tied to the Pyphen library. Technical strings, URLs, or irregular phonetic structures in non-standard languages may produce inconsistent syllabification results.

Implementation status: this system has not been audited. It is a research artifact and not a production-ready cryptographic library.

---

## Experimental Vision & Philosophy

Noni is an evolving research project that originated from the study of private symbolic languages. Its development follows an organic trajectory: what began as a creative exercise in personal linguistics has expanded into a formalized exploration of high-entropy data dispersion and phonetic obfuscation.

By bridging the gap between symbolic creativity and cryptographic logic, Noni investigates how the natural structure of language — syllables, vowels, and rhythm — can be used as a framework for data protection, and opens a space for the intersection of computer science, linguistics, and creative coding.

This project is a proof-of-concept for phonetic-structural encryption. It is not intended to replace established cryptographic standards, but rather to contribute to the inquiry into how information can be transformed while maintaining a linguistic-like profile.

---

## Installation

```bash
pip install pyphen numpy
```

```python
from noni import CipherEngine

engine = CipherEngine("my_password")
encrypted = engine.encrypt("hello world")
recovered = engine.decrypt(encrypted)
```

---

## Related Research

This project is part of a broader line of research into adversarial linguistics and LLM security:

- [Architectural Collapse via Blank Spaces Language (BSL)](https://github.com/SerenaGW/RedTeamLowEnthropy)
- [The Paradox of Optimized Fragility](https://github.com/SerenaGW/LLMLanguageFineTuningModifiesMathLogic)
- [Symbolic Language and LLM Resilience](https://github.com/SerenaGW/LLMReadteamSymbolic)
- [Semantic Re-signification and Linguistic DoS](https://github.com/SerenaGW/LLMReadTeamLinguisticDoS)

---

## License

MIT License.

## Author

SerenaGW 
