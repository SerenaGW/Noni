import pyphen
import re
import hashlib
import secrets
import math
import hmac
import numpy as np
import tiktoken
import matplotlib.pyplot as plt
import string
import base64
from tqdm import tqdm

# --- NONI ENGINE V3.0 ---
BASE_MAP = {'a': '1', 'e': '2', 'i': '3', 'o': '4', 'u': '5'}
INVERSE_MAP = {'a': '5', 'e': '4', 'i': '3', 'o': '2', 'u': '1'}
PRIME_MAP = {'a': '4', 'e': '3', 'i': '1', 'o': '5', 'u': '2'}
BLOCK_SIZE = 16


class LatticePRNG:
    def __init__(self, seed_int, dimension=256):
        np.random.seed(seed_int % (2**32))
        self.n = dimension
        self.q = 12289
        self.A = np.random.randint(0, self.q, (self.n, self.n))
        self.s = np.random.randint(0, self.q, self.n)
        self.e = np.random.normal(0, 2, self.n).astype(int)
        self.b = (np.dot(self.A, self.s) + self.e) % self.q

    def get_digit(self, index):
        return int((self.b[index % self.n] + self.s[index % self.n]) % 10)


class NoniManifold:
    def __init__(self, master_value, lattice_engine):
        self.master_value = master_value
        self.lattice = lattice_engine

    def project_position(self, i, iv_seed):
        lattice_digit = self.lattice.get_digit(i + iv_seed)
        seed = f"{self.master_value}-pos-{i}-lat-{lattice_digit}-iv-{iv_seed}"
        digest = hashlib.sha256(seed.encode()).digest()
        state_256 = int.from_bytes(digest, 'big')
        angle = (digest[2] / 255.0) * 2 * math.pi
        return state_256, angle, lattice_digit

    def is_noise_position(self, i):
        if i == 0:
            return False
        h = int(hashlib.md5(
            f"{self.master_value}-noise-{i}".encode()).hexdigest(), 16)
        return (h % 5 == 0)


class CipherEngine:
    def __init__(self, master_key="girasol"):
        self.master_key = master_key
        self.dic = pyphen.Pyphen(lang='es')
        self.iv_values = {'*': 1, '!': 2, '+': 4, '_': 8, '~': 16}
        self.re_punc = re.compile(
            r'^([¿¡\-"«»—]*)(.*?)([¿¡\-"«»—\-,.:;!?()]*)$')
        self._noise_buffer = self._generate_mimic_noise()
        self._noise_ptr = 0

    def _generate_mimic_noise(self):
        act, nums, cons = ["#", "$"], ["1", "2", "3",
                                       "4", "5"], "bcdfghjklmnpqrstvwxyz.!-,"
        return "".join(secrets.choice(cons) if secrets.randbelow(2) == 0 else secrets.choice(act)+secrets.choice(nums) for _ in range(5000))

    def _get_fast_noise(self, length):
        if self._noise_ptr + length > len(self._noise_buffer):
            self._noise_ptr = 0
        res = self._noise_buffer[self._noise_ptr: self._noise_ptr + length]
        self._noise_ptr += length
        return res

    def _initialize_with_salt(self, salt: bytes):
        stretched = hashlib.pbkdf2_hmac(
            'sha256', self.master_key.encode(), salt, 1000)
        self.auth_key = hashlib.sha256(stretched + b"integrity").digest()
        self.lattice = LatticePRNG(int.from_bytes(stretched, 'big'))
        key_res = [chr(65 + (self.lattice.get_digit(i) % 26))
                   for i in range(500)]
        self.master_value = int.from_bytes(hashlib.sha256(
            "".join(key_res).encode()).digest(), 'big')
        self.manifold = NoniManifold(self.master_value, self.lattice)

    def _mutate_consonants(self, text, seed, mode):
        res, cons = "", "BCDFGHJKLMNPQRSTVWXYZ0123456789"
        shift = (seed % len(cons)) * (1 if mode == 'encrypt' else -1)
        for char in text:
            is_up, c = char.isupper(), char.upper()
            if c in cons:
                idx = (cons.find(c) + shift) % len(cons)
                res += cons[idx] if is_up else cons[idx].lower()
            else:
                res += char
        return res

    def _apply_block_padding(self, token):
        pad_len = BLOCK_SIZE - (len(token) % BLOCK_SIZE)
        if pad_len == 0:
            pad_len = BLOCK_SIZE
        padding = self._get_fast_noise(pad_len - 1)
        indicator = hex(pad_len % 16)[2:]
        return token + padding + indicator

    def encrypt(self, text):
        clean_text = " ".join(text.split())
        words = clean_text.split()
        salt = secrets.token_bytes(16)
        self._initialize_with_salt(salt)
        iv_val = secrets.randbelow(31) + 1
        header = f"{self._generate_iv_symbols(iv_val)}{salt.hex()}"
        word_stream, f_idx = [], 0
        for p in words:
            while self.manifold.is_noise_position(f_idx):
                fake_noise = self._get_fast_noise(BLOCK_SIZE - 1) + "0"
                word_stream.append(f"{len(fake_noise):02x}{fake_noise}")
                f_idx += 1
            state_256, angle, lat_d = self.manifold.project_position(
                f_idx, iv_val)
            m = self.re_punc.match(p)
            pre, core, post = m.groups() if m else ("", p, "")
            t1 = self._mutate_consonants(
                core, (state_256 % 2**32) + lat_d + iv_val, 'encrypt')
            cipher_core = self._process_word_deep(
                t1, state_256, angle, 'encrypt')
            final_block = self._apply_block_padding(
                f"{pre}{cipher_core}{post}")
            word_stream.append(f"{len(final_block):02x}{final_block}")
            f_idx += 1
        total_body = header + "".join(word_stream)
        signature = hmac.new(
            self.auth_key, total_body.encode(), hashlib.sha256).hexdigest()
        return f"{signature}{total_body}"

    def _strip_accents(self, t): return t.translate(
        str.maketrans("áéíóúüÁÉÍÓÚÜ", "aeiouuAEIOUU"))

    def _process_word_deep(self, p, state_256, angle, mode):
        def get_bit(n): return (state_256 >> (n % 256)) & 1
        vowels, SEP, HYPHEN_SHIELD = 'aeiou', "§", "QDQ"
        p_clean = self._strip_accents(p).lower()
        p_protected = p_clean.replace("-", HYPHEN_SHIELD)
        sylls = self.dic.inserted(p_protected, hyphen=SEP).split(SEP)
        if get_bit(0) and len(sylls) >= 2:
            s = int(abs(angle * 10)) % len(sylls)
            sylls = sylls[s:] + sylls[:s]
        flat_rotated = SEP.join(sylls)
        if get_bit(4):
            flat_rotated = flat_rotated[::-1]
        res, v_idx = "", 0
        for char in flat_rotated:
            if char in vowels:
                bit_ptr = 80 + (v_idx * 15)
                marker = "#" if get_bit(bit_ptr) == 0 else "$"
                mapping = PRIME_MAP if (get_bit(
                    bit_ptr+1) and marker == "#") else (INVERSE_MAP if get_bit(bit_ptr+2) else BASE_MAP)
                res += f"{marker}{mapping[char]}"
                v_idx += 1
            else:
                res += char
        return res

    def _generate_iv_symbols(self, iv):
        res = ""
        for s, v in sorted(self.iv_values.items(), key=lambda x: x[1], reverse=True):
            if iv >= v:
                res += s
                iv -= v
        return res

# --- ANALYSIS HELPERS ---


def calculate_hamming_distance(s1, s2):
    if len(s1) != len(s2):
        s1 = (s1 * (len(s2) // len(s1) + 1))[:len(s2)]
    return sum(el1 != el2 for el1, el2 in zip(s1, s2)) / len(s2)


def calculate_manifold_correlation(c1, c2):
    v1 = np.frombuffer(c1.encode(), dtype=np.uint8)
    v2 = np.frombuffer(c2.encode(), dtype=np.uint8)
    ln = min(len(v1), len(v2))
    v1, v2 = v1[:ln], v2[:ln]

    correlation = np.corrcoef(v1, v2)[0, 1]
    avalanche = sum(el1 != el2 for el1, el2 in zip(v1, v2)) / ln
    return correlation, avalanche

# --- MONTE CARLO STATISTICAL BENCHMARK ---


def run_monte_carlo_benchmark(iterations=100000):
    print(f"[*] Starting Monte Carlo Benchmark ({iterations} iterations)...")
    engine = CipherEngine(master_key="research_seed_2026")
    encoder = tiktoken.get_encoding("cl100k_base")

    results = {"Noni": [], "Base64": [], "Hexadecimal": [], "Random Noise": []}
    hamming_scores = []
    correlations = []
    avalanche_scores = []

    noni_beats_noise_count = 0
    max_diff_noni_noise = -float('inf')
    text = "The quick brown fox jumps over the lazy dog."

    for _ in tqdm(range(iterations), desc="Processing"):
        noni_payload = engine.encrypt(text)
        target_length = len(noni_payload)
        tokens_noni = len(encoder.encode(noni_payload))

        chars = string.ascii_letters + string.digits + "#$!*+_"
        noise_payload = ''.join(secrets.choice(chars)
                                for _ in range(target_length))
        tokens_noise = len(encoder.encode(noise_payload))

        h_dist = calculate_hamming_distance(text, noni_payload)
        hamming_scores.append(h_dist)

        noni_payload_alt = engine.encrypt(text)
        corr, avalanche = calculate_manifold_correlation(
            noni_payload, noni_payload_alt)
        correlations.append(corr)
        avalanche_scores.append(avalanche)

        results["Noni"].append(tokens_noni)
        results["Random Noise"].append(tokens_noise)

        b64_source = base64.b64encode((text * 30).encode()).decode()
        results["Base64"].append(
            len(encoder.encode(b64_source[:target_length])))

        hex_source = (text * 30).encode().hex()
        results["Hexadecimal"].append(
            len(encoder.encode(hex_source[:target_length])))

        if tokens_noni > tokens_noise:
            noni_beats_noise_count += 1
        diff = tokens_noni - tokens_noise
        if diff > max_diff_noni_noise:
            max_diff_noni_noise = diff

    means = {k: np.mean(v) for k, v in results.items()}
    stds = {k: np.std(v) for k, v in results.items()}
    avg_hamming = np.mean(hamming_scores)
    avg_corr = np.mean(correlations)
    win_rate = (noni_beats_noise_count / iterations) * 100

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 8))

    plt.subplots_adjust(bottom=0.2)

    methods = list(means.keys())
    values = list(means.values())
    errors = list(stds.values())
    colors = ['#FF3131', '#2196F3', '#9C27B0', '#FFC107']

    bars = ax.bar(methods, values, yerr=errors, color=colors,
                  capsize=10, edgecolor='white')

    plt.xticks(rotation=15, fontsize=10)

    ax.set_title(
        f'Statistical Average: Token Density\n({iterations} iterations)', fontsize=14, color='cyan', pad=20)

    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 2,
                f'{h:.1f}', ha='center', fontweight='bold', color='white')

    footer_text = (f"Noni Win Rate vs Noise: {win_rate:.2f}% | Max Gap: {max_diff_noni_noise} | "
                   f"Hamming: {avg_hamming:.4f} | Correlation: {avg_corr:.4f}")

    plt.figtext(0.5, 0.05, footer_text, ha="center", fontsize=10, color='yellow',
                fontweight='bold', bbox={"facecolor": "black", "alpha": 0.8, "pad": 8})

    plt.tight_layout(rect=[0, 0.08, 1, 1])
    plt.show()


if __name__ == "__main__":
    run_monte_carlo_benchmark(100000)
