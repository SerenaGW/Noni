import hashlib
import secrets
import math
import re
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from mpl_toolkits.mplot3d import Axes3D


class CryptoManifold:
    def __init__(self, master_value):
        self.master_value = master_value

    def project_position(self, i, lattice_digit, iv_seed):
        seed = f"{self.master_value}-pos-{i}-lat-{lattice_digit}-iv-{iv_seed}"
        digest = hashlib.sha256(seed.encode()).digest()

        # Rule selection (v_man)
        v_final = int.from_bytes(digest[:2], 'big') % 1024

        # Aesthetic coordinates for 3D plotting
        phase = (self.master_value % 100) + i + lattice_digit + iv_seed
        x = math.sin(phase * 0.5) * (digest[0]/255)
        y = math.cos(phase * 0.3) * (digest[1]/255)
        z = math.sin(phase * 1.6) * (digest[2]/255)

        return v_final, x, y, z

    def is_noise_position(self, i):
        if i == 0:
            return False
        h = int(hashlib.md5(
            f"{self.master_value}-noise-{i}".encode()).hexdigest(), 16)
        return (h % 5 == 0)


class CryptoVisualizer:
    def __init__(self, master_key="girasol"):
        self.salt = secrets.token_bytes(16)

        # Standard KDF derivation
        stretched = hashlib.pbkdf2_hmac(
            'sha256', master_key.encode(), self.salt, 100000)

        # Deterministic dummy lattice for visualization purposes
        # This simulates the LatticePRNG behavior
        np.random.seed(int.from_bytes(stretched, 'big') % (2**32))
        self.lattice_mock = np.random.randint(0, 10, 1000)

        key_res = []
        for i in range(500):
            key_res.append(chr(65 + (self.lattice_mock[i] % 26)))

        hash_bytes = hashlib.sha256("".join(key_res).encode()).digest()
        self.master_value = int.from_bytes(hash_bytes, byteorder='big')
        self.manifold = CryptoManifold(self.master_value)


def visualize_cipher_flow(master_key, text):
    viz = CryptoVisualizer(master_key)
    words = text.split()

    data_map = []
    points_3d = []
    axis_labels = []

    iv = 15
    p_idx, f_idx = 0, 0

    while p_idx < len(words) and p_idx < 40:
        if viz.manifold.is_noise_position(f_idx):
            data_map.append([0.2]*5)
            points_3d.append([0, 0, 0, 0])
            axis_labels.append(f"[NOISE_{f_idx}]")
            f_idx += 1
            continue

        lattice_d = viz.lattice_mock[f_idx % 1000]
        v_man, x, y, z = viz.manifold.project_position(f_idx, lattice_d, iv)

        # Rules activation (INV, ROTA, ESP, ALT, SHF)
        activations = [(v_man >> j) & 1 for j in range(5)]
        data_map.append(activations)
        points_3d.append([x, y, z, v_man % 100])

        label = re.sub(r'[^a-zA-Z]', '', words[p_idx])
        axis_labels.append(f"{label}_{p_idx}")

        p_idx += 1
        f_idx += 1

    # --- RENDER ---
    sns.set_theme(style="white")
    fig = plt.figure(figsize=(18, 9))

    # 1. ATTENTION MAP (Heatmap)
    ax1 = fig.add_subplot(121)
    df = pd.DataFrame(data_map, columns=['INV', 'ROTA', 'ESP', 'ALT', 'SHF'])
    sns.heatmap(df, cmap="rocket", cbar=True, linewidths=.5,
                yticklabels=axis_labels, ax=ax1)
    ax1.set_title(
        "GEOMETRIC ATTENTION MAP\n(Rule Activation per Token)", fontsize=12)

    # 2. 3D MANIFOLD PROJECTION
    ax2 = fig.add_subplot(122, projection='3d')
    pts = np.array(points_3d)

    ax2.plot(pts[:, 0], pts[:, 1], pts[:, 2], color='cyan', alpha=0.3, lw=1)
    scatter = ax2.scatter(pts[:, 0], pts[:, 1], pts[:, 2],
                          c=pts[:, 3], cmap='plasma', s=100,
                          edgecolors='black', alpha=0.8)

    cbar = fig.colorbar(scatter, ax=ax2, shrink=0.5, aspect=10)
    cbar.set_label('Phase Intensity (Energy)')

    ax2.set_xlabel('Phase X')
    ax2.set_ylabel('Phase Y')
    ax2.set_zlabel('Phase Z')
    ax2.set_title("MANIFOLD PROJECTION CLOUD", fontsize=12)

    plt.suptitle(
        f"CIPHER ENGINE V2.1 ANALYSIS - Master Key: {master_key.upper()}", fontsize=14)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    test_phrase = "hello hello hello hello hello hello hello"
    visualize_cipher_flow("girasol", test_phrase)
