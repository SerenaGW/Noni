# Noni: A Symbolic Infrastructure for Data Encryption

Noni is a symmetric stream cipher for natural language text. It encrypts text word by word using a combination of syllabic fragmentation, dynamic substitution rules, and a lattice-based pseudorandom engine, producing output that is structurally opaque to both classical frequency analysis and the tokenization layer of language models.

The project has an unusual origin. As a child, I developed a private symbolic language as a personal creative exercise. Years later, that language became the foundation for research into adversarial techniques in large language models. Noni is the next step in that line: a practical experiment that formalizes those symbolic patterns into a functional cryptographic infrastructure.

This is a research and design exercise. It does not replace audited standards like AES-GCM or ChaCha20-Poly1305, and it has not been formally analyzed. It is published as an open artifact for analysis, critique, and extension.

For the full technical architecture and empirical validation, see [REPORT.md](Report.md).

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
from NONIV1.Core.Engine import NoniEngine

engine = NoniEngine("my_password")
encrypted = engine.encriptar("hello world")
recovered = engine.desencriptar(encrypted)
```

---
![Cipher Engine Analysis](NONIV1/Analysis.png)

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
