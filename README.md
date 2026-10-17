# Noni: an experimental text cipher

Noni is an experimental cipher for natural-language text, based on a symbolic language I invented as a kid. I built it in a few days as a learning exercise in Python, using AI as a development tool.

> **Noni is not secure.** It has known weaknesses (listed below) and must not be used to protect real data. For real encryption, use audited standards such as AES-GCM or ChaCha20-Poly1305.

---

## How it works

Noni encrypts text word by word, combining several layers:

- **Key derivation:** PBKDF2-HMAC-SHA256 (100,000 iterations) with a random 16-byte salt.
- **Syllable rotation:** each word is split into syllables (with the Pyphen library) and the syllables may be rotated or reversed.
- **Vowel substitution:** each vowel becomes a marker (`#` or `$`) plus a digit, chosen from three substitution tables.
- **Consonant shift:** consonants and digits are shifted along a circular alphabet.
- **Noise and padding:** fake blocks are inserted between words, and every block is padded to a multiple of 16 characters.
- **Integrity check:** an HMAC-SHA256 signature detects any change to the ciphertext.

The per-word decisions (which table, whether to rotate, how far to shift) come from a SHA-256 hash of the key, the word position and a random IV.

---

## Known limitations

I reviewed this project months after building it. These are the weaknesses I found, each with the place in the code where you can check it:

1. **The effective key is only 32 bits.** In `core/engine.py`, the 256-bit derived key is reduced with `% (2**32)` to seed `numpy.random` (line 18). Everything that controls the encryption derives from that seed, so there are only about 4.3 billion possible keys, which is within reach of a brute-force search. `numpy.random` is also not a cryptographic random generator, and the "lattice" layer adds no security because its secret comes from that same seed.
2. **Syllable boundaries leak.** The `§` separator used during syllabification remains in the ciphertext (lines 199–213), and the vowel/consonant pattern of each word is preserved.
3. **Each word has very few possible transformations.** All consonants in a word share a single shift (31 options), each vowel uses one of only three tables, and there are few possible rotations. A large internal state only chooses among these few options, so words could likely be recovered one by one with a dictionary, without the key. (Not yet demonstrated with an actual attack.)
4. **Noise blocks are distinguishable from real ones.** Noise never contains `§` or the digits 0, 6, 7, 8 or 9, while real blocks can.
5. **Decryption loses information.** Text is lowercased and accents are removed before encryption (line 187), so "Él" comes back as "el". On long texts, around 0.01–0.04% of words also come back with punctuation in the wrong place.

### About the metrics in the report

The original [Report.md](Report.md) presents several metrics as evidence of security. They don't measure that:

- **"Hamming distance 0.9918"** compares the plaintext with the ciphertext character by character (`montecarlo.py`, lines 178–181). Any encoding with a different alphabet scores close to 1; it is not an avalanche effect.
- **"Correlation 0.036"** is computed between **two encryptions of the same text**, not between plaintext and ciphertext as the report says (lines 184–192).
- **"Shannon entropy 1.0"** in the million-state audit measures the bits of SHA-256, which are uniform by design, not the security of the cipher.
- **Token density** compared with random noise shows how the output is tokenized, not whether it can be broken.

---

## What I learned

The main lesson: AI helped me build something that *looks* like advanced cryptography in a few days, and also helped me produce metrics that *seemed* to validate it. Neither proves security. Verifying what each metric actually computes, and trying to break the system instead of only measuring it, is what revealed the problems.

---

## Running it

```bash
pip install pyphen numpy
```

```python
from NONIV1.core.engine import CipherEngine

engine = CipherEngine(master_key="test_password")
encrypted = engine.encrypt("Hello world")
print(engine.decrypt(encrypted))  # "hello world" (case and accents are lost)
```

Other scripts in `NONIV1/`: `main.py` (single demo), `main2.py` (full Don Quixote test), `auditsuite.py` (state audit), `montecarlo.py` (token density benchmark), `graphics.py` (plots).

---

## License

MIT License.
