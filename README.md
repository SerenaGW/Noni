# Noni: A Symbolic Infrastructure for Data Encryption

Noni is a symmetric stream cipher for natural language text. It encrypts text word-by-word using a combination of syllabic fragmentation, dynamic substitution rules, and a **256-bit High-Dimensional Manifold**, producing output that is structurally opaque to both classical frequency analysis and the tokenization layer of language models.

### 📢 Update: Manifold Evolution & Security Hardening
First of all, thanks to everyone who has been cloning and exploring this repository! Seeing the interest in Noni inspired me to spend some extra hours refining the engine's core.

In this update, I’ve addressed potential vulnerabilities by evolving the previous 3D state space into a **256-bit High-Dimensional Manifold**. This shift ensures that the decision logic behind every token is stochastically independent. I’ve also integrated a **Lattice-based PRNG** to replace public entropy sources with a private, key-dependent stream.

---

## Experimental Origin
The project has an unusual origin. As a child, I developed a private symbolic language as a personal creative exercise. Years later, that language became the foundation for research into adversarial techniques in large language models. Noni is the next step in that line: a practical experiment that formalizes those symbolic patterns into a functional cryptographic infrastructure.

> **Disclaimer**: This is a research and design exercise. It does not replace audited standards like AES-GCM or ChaCha20-Poly1305. It is published as an open research artifact for analysis, critique, and extension.

**For the full technical architecture and empirical validation, see [REPORT.md](Report.md).**

---

## Repository Structure

```
Noni/
├── README.md
├── Report.md
├── Analysis.png
└── NONIV1/
    ├── main.py
    ├── main2.py
    ├── auditsuite.py
    ├── graphics.py
    ├── donquijote.txt
    ├──prideandprejudice.txt
    └── Core/
        └── Engine.py
```

`Core/Engine.py` is the cryptographic engine. It is the only file required to use Noni programmatically. `main.py` runs a single end-to-end demonstration cycle. `main2.py` runs the high-volume stress test on the full text of Don Quixote. `auditsuite.py` runs the million-state statistical audit of the dispersion engine. `graphics.py` renders the Geometric Attention Map and the Manifold Projection Cloud.

---

## Installation

```bash
pip install pyphen numpy matplotlib seaborn pandas
```

```python
from NONIV1.Core.Engine import CipherEngine

# Initialize the engine (Triggers PBKDF2 and Lattice PRNG)
engine = CipherEngine(master_key="your_secure_password")

# Encrypting
text = "The quick brown fox jumps over the lazy dog"
encrypted = engine.encrypt(text)
print(f"Ciphertext: {encrypted}")

# Decrypting
decrypted = engine.decrypt(encrypted)
print(f"Recovered: {decrypted}")
```

---
## Visualizing the 256-bit Manifold

The transition to v3.0 introduces a high-resolution state space. Below is the Entropy Fingerprint (bit-level logic) and the 3D Shadow of the 256-bit Manifold.
![Cipher Engine Analysis](NONIV1/Analysis3.png)

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
