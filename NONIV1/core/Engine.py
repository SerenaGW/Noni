import pyphen
import re
import hashlib
import secrets
import math
import hmac
import numpy as np
from functools import lru_cache

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
        val = (self.b[index % self.n] + self.s[index % self.n]) % 10
        return int(val)


class NoniManifold:
    def __init__(self, master_value, lattice_engine):
        self.master_value = master_value
        self.lattice = lattice_engine

    def project_position(self, i, iv_seed):
        lattice_digit = self.lattice.get_digit(i + iv_seed)
        seed = f"{self.master_value}-pos-{i}-lat-{lattice_digit}-iv-{iv_seed}"
        digest = hashlib.sha256(seed.encode()).digest()
        final_v = int.from_bytes(digest[:2], 'big') % 1024
        angle = (digest[2] / 255.0) * 2 * math.pi
        return final_v, angle, lattice_digit

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
        self.action_keys = ('inv', 'rota', 'esp', 'alt', 'shf')
        self.iv_values = {'*': 1, '!': 2, '+': 4, '_': 8, '~': 16}
        self.re_punc = re.compile(r'^([¿¡\-"«—]*)(.*?)([,.:;!?()\-"»—]*)$')
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
            'sha256', self.master_key.encode(), salt, 100000)
        self.auth_key = hashlib.sha256(stretched + b"integrity").digest()
        seed_int = int.from_bytes(stretched, 'big')
        self.lattice = LatticePRNG(seed_int)

        key_res = []
        for i in range(500):
            key_res.append(chr(65 + (self.lattice.get_digit(i) % 26)))

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

    def _remove_block_padding(self, token):
        try:
            pad_len = int(token[-1], 16)
            if pad_len == 0:
                pad_len = 16
            return token[:-pad_len]
        except:
            return token

    def encrypt(self, text):
        words = text.strip().split()
        salt = secrets.token_bytes(16)
        self._initialize_with_salt(salt)
        iv_val = secrets.randbelow(31) + 1
        header = f"{self._generate_iv_symbols(iv_val)}{salt.hex()}"
        word_stream = []

        f_idx = 0
        for p in words:
            while self.manifold.is_noise_position(f_idx):
                fake_noise = self._get_fast_noise(BLOCK_SIZE - 1) + "0"
                word_stream.append(f"{len(fake_noise):02x}{fake_noise}")
                f_idx += 1

            v_man, angle, lattice_d = self.manifold.project_position(
                f_idx, iv_val)
            rules = tuple(self.action_keys[j]
                          for j in range(5) if (v_man >> j) & 1)

            m = self.re_punc.match(p)
            p_pre, p_core, p_post = m.groups() if m else ("", p, "")

            t1 = self._mutate_consonants(
                p_core, v_man + lattice_d + iv_val, 'encrypt')
            cipher_core = self._process_word_cached(
                t1, rules, int(angle * 10), 'encrypt')

            final_block = self._apply_block_padding(
                f"{p_pre}{cipher_core}{p_post}")
            word_stream.append(f"{len(final_block):02x}{final_block}")
            f_idx += 1

        total_body = header + "".join(word_stream)
        signature = hmac.new(
            self.auth_key, total_body.encode(), hashlib.sha256).hexdigest()
        return f"{signature}{total_body}"

    def decrypt(self, full_text):
        received_sig = full_text[:64]
        body = full_text[64:]
        match_iv = re.match(r'^[*!+_~]+', body)
        iv_str = match_iv.group()
        iv_val = sum(self.iv_values.get(s, 0) for s in iv_str)
        cursor = len(iv_str)
        salt_hex = body[cursor:cursor+32]
        self._initialize_with_salt(bytes.fromhex(salt_hex))
        cursor += 32

        if not hmac.compare_digest(received_sig, hmac.new(self.auth_key, body.encode(), hashlib.sha256).hexdigest()):
            return "❌ ERROR: Integrity violation."

        recovered_msg, f_idx = [], 0
        while cursor < len(body):
            length = int(body[cursor:cursor+2], 16)
            cursor += 2
            block = body[cursor:cursor+length]
            cursor += length

            if self.manifold.is_noise_position(f_idx):
                f_idx += 1
                continue

            clean_block = self._remove_block_padding(block)
            v_man, angle, lattice_d = self.manifold.project_position(
                f_idx, iv_val)
            rules = tuple(self.action_keys[j]
                          for j in range(5) if (v_man >> j) & 1)

            m = self.re_punc.match(clean_block)
            p_pre, p_core, p_post = m.groups() if m else ("", clean_block, "")

            t1 = self._process_word_cached(
                p_core, rules, int(angle * 10), 'decrypt')
            t2 = self._mutate_consonants(
                t1, v_man + lattice_d + iv_val, 'decrypt')
            recovered_msg.append(f"{p_pre}{t2}{p_post}")
            f_idx += 1

        return " ".join(recovered_msg)

    @lru_cache(maxsize=1024)
    def _strip_accents(self, t):
        return t.translate(str.maketrans("áéíóúüÁÉÍÓÚÜ", "aeiouuAEIOUU"))

    @lru_cache(maxsize=5000)
    def _process_word_cached(self, p, rules, angle_idx, mode):
        angle = angle_idx / 10.0
        if mode == 'encrypt':
            sylls = self.dic.inserted(
                self._strip_accents(p).lower()).split('-')
            if 'rota' in rules and len(sylls) >= 2:
                shift = int(abs(angle * 10)) % len(sylls)
                sylls = sylls[shift:] + sylls[:shift]

            encoded = []
            for idx, s in enumerate(sylls):
                v_s, marker = "", "#" if (idx + 1) % 2 != 0 else "$"
                for char in s:
                    if char in 'aeiou':
                        mapping = PRIME_MAP if ('alt' in rules and marker == '#') else (
                            INVERSE_MAP if 'inv' in rules else BASE_MAP)
                        v_s += f"{marker}{mapping.get(char, '1')}"
                    else:
                        v_s += char
                encoded.append(v_s)
            res = "-".join(encoded)
            return res[::-1] if 'esp' in rules else res
        else:
            tmp = p[::-1] if 'esp' in rules else p
            sylls = tmp.split('-')
            if 'rota' in rules and len(sylls) >= 2:
                shift = int(abs(angle * 10)) % len(sylls)
                sylls = sylls[-shift:] + sylls[:-shift]

            res = []
            for s in sylls:
                orig, j = "", 0
                while j < len(s):
                    if s[j] in "#$" and j+1 < len(s):
                        mapping = PRIME_MAP if (s[j] == "#" and 'alt' in rules) else (
                            INVERSE_MAP if 'inv' in rules else BASE_MAP)
                        orig += {v: k for k, v in mapping.items()
                                 }.get(s[j+1], 'a')
                        j += 2
                    else:
                        orig += s[j]
                        j += 1
                res.append(orig)
            return "".join(res)

    def _generate_iv_symbols(self, iv):
        res = ""
        for s, v in sorted(self.iv_values.items(), key=lambda x: x[1], reverse=True):
            if iv >= v:
                res += s
                iv -= v
        return res
