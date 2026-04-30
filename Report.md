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

Noni uses a dynamic lattice-based engine initialized from the stretched seed. Using a public matrix A and an error vector e following Learning With Errors principles, it generates a deterministic private entropy stream. The construction uses modulus q=12289, consistent with Kyber parameters, but is not an implementation of Kyber or any standardized post-quantum primitive. Unlike previous versions that used the decimal digits of Pi as a pseudorandom stream, this stream is private: it depends entirely on the key and salt.

### 3. Tri-Parametric State Mapping

Every token is processed through a mapping function that projects entropy into a discrete 3D state space via SHA256:

```
seed = "{master_value}-pos-{i}-lat-{d_lat}-iv-{IV}"
digest = SHA256(seed)
```

Axis V (Transformation Logic): a 10-bit vector selecting from 1,024 possible rule combinations. Axis θ (Phonetic Rotation): a parameter determining the circular shift of syllables. Axis D (Lattice Displacement): a discrete value acting as a dynamic salt for consonant mutation.

### 4. Word-level Transformations: Dynamic Polyalphabetic Substitution

The v_man value activates up to 5 combinable transformations. `inv` inverts the vowel substitution map. `rota` reorders syllables according to the angle derived from the digest, using Pyphen for syllabification. `esp` reverses the entire character string. `alt` applies a prime-based vowel map. `shf` shifts consonants and digits in a circular alphabet.

Vowel maps:

```
Base:    a->1, e->2, i->3, o->4, u->5
Inverse: a->5, e->4, i->3, o->2, u->1
Alternative:   a->4, e->3, i->1, o->5, u->2
```

It works with any language. When encrypting English text, Spanish syllable boundaries are applied as an additional layer of structural obfuscation. This behavior is intentional.

### 5. High-Entropy Symbolic Noise Injection (Syntactic Mimicry)

Noise positions are determined by `MD5(master_value + "-noise-" + index) % 5 == 0`. Noise tokens mimic the syntax of real encrypted content: they include activators (`#`, `$`) followed by numbers in the 1-5 range, which are the same symbols used for real vowel substitution. To a statistical analyst, noise tokens are indistinguishable from data tokens.

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

### High-Volume Stress Test: Full Text

Tested on the complete text of Don Quixote under real-world linguistic conditions:

```
Original size:    2,091.3 KB
Encrypted size:   8,685.3 KB
Expansion ratio:  4.15x
Throughput:       612.18 KB/s
```

The 315% increase in file size is a direct result of the phonetic-to-symbolic fragmentation and the symmetric noise strategy. This expansion is the mechanism that enables high entropy and prevents context inference by disrupting standard tokenization patterns.

### Visual Analysis of the Dispersion Engine

The following plots show rule activation for the same word ("hello") 
across 7 consecutive positions using the key "GIRASOL", generated by `graphics.py`.

![Cipher Engine Analysis](NONIV1/Analysis.png)

The attention map shows that each position activates a different rule subset, 
including a noise token at position 6 ([NOISE_6]) which is visually 
indistinguishable from real encrypted tokens in the stream. The projection 
cloud shows token dispersion across the 3D manifold state space.

---

## Security Properties

Integrity: HMAC-SHA256 (Encrypt-then-MAC) detects any bitwise alteration and rejects decryption with incorrect keys.

Statistical flattening: syntactic noise using `#/$` and digits 1-5 is indistinguishable from real vowel substitution output. Frequency analysis on the ciphertext does not reveal vowel distribution.

Length obfuscation: 16-byte block padding and positional noise injection eliminate word counting and length inference from the ciphertext.

Lattice-based stream: the pseudorandom stream depends on a private LWE construction rather than a public constant. This adds resistance against precomputation attacks.

Kerckhoffs's principle: security depends exclusively on the key and salt. The algorithm is public.

---

## Limitations

The substitution layer operates on a small linguistic alphabet. An attacker with sufficient known plaintext could attempt statistical analysis of the substitution patterns independently of the dispersion engine. This is the primary unresolved limitation.

The LatticePRNG is a simplified LWE construction. It is not a full implementation of Kyber or any standardized post-quantum primitive. It provides structural inspiration and adds private entropy, but has not been formally analyzed.

Weak passwords remain vulnerable to GPU-accelerated dictionary attacks despite PBKDF2 mitigation. The system's confidentiality guarantees depend entirely on key quality.

The system has not been audited. It is a research and design exercise, not a production cryptographic library.

---

## Installation

```bash
pip install pyphen numpy
```

```python
from noni import NoniEngine

engine = NoniEngine("my_password")
encrypted = engine.encriptar("hello world")
recovered = engine.desencriptar(encrypted)
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
