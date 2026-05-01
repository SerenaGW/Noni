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
            'sha256', self.master_key.encode(), salt, 100000)
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

    def _remove_block_padding(self, token):
        try:
            pad_len = int(token[-1], 16)
            if pad_len == 0:
                pad_len = 16
            return token[:-pad_len]
        except:
            return token

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

    def decrypt(self, full_text):
        received_sig, body = full_text[:64], full_text[64:]
        match_iv = re.match(r'^[*!+_~]+', body)
        if not match_iv:
            return "DECODE_ERROR"
        iv_str = match_iv.group()
        iv_val = sum(self.iv_values.get(s, 0) for s in iv_str)
        cursor = len(iv_str)
        salt_hex = body[cursor:cursor+32]
        self._initialize_with_salt(bytes.fromhex(salt_hex))
        cursor += 32
        if not hmac.compare_digest(received_sig, hmac.new(self.auth_key, body.encode(), hashlib.sha256).hexdigest()):
            return "INTEGRITY_ERROR"
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
            state_256, angle, lat_d = self.manifold.project_position(
                f_idx, iv_val)
            m = self.re_punc.match(clean_block)
            pre, core, post = m.groups() if m else ("", clean_block, "")
            t1 = self._process_word_deep(core, state_256, angle, 'decrypt')
            t2 = self._mutate_consonants(
                t1, (state_256 % 2**32) + lat_d + iv_val, 'decrypt')
            recovered_msg.append(f"{pre}{t2}{post}")
            f_idx += 1
        return " ".join(recovered_msg)

    def _strip_accents(self, t):
        return t.translate(str.maketrans("áéíóúüÁÉÍÓÚÜ", "aeiouuAEIOUU"))

    def _process_word_deep(self, p, state_256, angle, mode):
        def get_bit(n): return (state_256 >> (n % 256)) & 1
        vowels = 'aeiou'
        SEP = "§"
        HYPHEN_SHIELD = "QDQ"

        if mode == 'encrypt':
            p_clean = self._strip_accents(p).lower()

            # PROTECCIÓN: Ocultamos el guion para que Pyphen no lo consuma
            p_protected = p_clean.replace("-", HYPHEN_SHIELD)

            # Silabeamos usando el separador especial
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
        else:
            flat_rotated, v_idx, i = "", 0, 0
            while i < len(p):
                if p[i] in "#$" and (i + 1) < len(p):
                    bit_ptr = 80 + (v_idx * 15)
                    marker = p[i]
                    mapping = PRIME_MAP if (get_bit(
                        bit_ptr+1) and marker == "#") else (INVERSE_MAP if get_bit(bit_ptr+2) else BASE_MAP)
                    inv_map = {v: k for k, v in mapping.items()}
                    val = p[i+1]
                    flat_rotated += inv_map.get(val, 'a')
                    i += 2
                    v_idx += 1
                else:
                    flat_rotated += p[i]
                    i += 1

            if get_bit(4):
                flat_rotated = flat_rotated[::-1]

            sylls = flat_rotated.split(SEP)

            if get_bit(0) and len(sylls) >= 2:
                s = int(abs(angle * 10)) % len(sylls)
                sylls = sylls[-s:] + sylls[:-s]

            final_word = "".join(sylls)
            return final_word.replace(HYPHEN_SHIELD, "-")

    def _generate_iv_symbols(self, iv):
        res = ""
        for s, v in sorted(self.iv_values.items(), key=lambda x: x[1], reverse=True):
            if iv >= v:
                res += s
                iv -= v
        return res
