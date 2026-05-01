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
    """
    Handles the 256-bit state generation and spatial projection 
    logic for the Noni Engine analysis.
    """

    def __init__(self, master_value):
        self.master_value = master_value

    def project_position(self, i, lattice_digit, iv_seed):
        # 256-bit State generation (32 bytes)
        seed = f"{self.master_value}-pos-{i}-lat-{lattice_digit}-iv-{iv_seed}"
        state_256 = hashlib.sha256(seed.encode()).digest()

        # Extract first 64 bits for entropy fingerprint visualization
        bits = np.unpackbits(np.frombuffer(state_256, dtype=np.uint8))

        # 3D Coordinate projection based on real manifold bytes
        x = state_256[0] / 255.0
        y = state_256[1] / 255.0
        z = state_256[2] / 255.0

        # Energy density calculation via Hamming Weight
        intensity = bin(int.from_bytes(state_256, 'big')).count('1')

        return bits[:64], x, y, z, intensity

    def is_noise_position(self, i):
        if i == 0:
            return False
        h = int(hashlib.md5(
            f"{self.master_value}-noise-{i}".encode()).hexdigest(), 16)
        return (h % 5 == 0)


class CryptoVisualizer:
    """
    Orchestrates the PRNG initialization and visualization metadata.
    """

    def __init__(self, master_key="girasol"):
        self.salt = secrets.token_bytes(16)
        stretched = hashlib.pbkdf2_hmac(
            'sha256', master_key.encode(), self.salt, 100000)

        np.random.seed(int.from_bytes(stretched, 'big') % (2**32))
        self.lattice_mock = np.random.randint(0, 10, 1000)

        key_res = [chr(65 + (self.lattice_mock[i] % 26)) for i in range(500)]
        hash_bytes = hashlib.sha256("".join(key_res).encode()).digest()
        self.master_value = int.from_bytes(hash_bytes, byteorder='big')
        self.manifold = CryptoManifold(self.master_value)


def visualize_high_dim_manifold(master_key, text):
    """
    Renders the Entropy Fingerprint and 3D Manifold projection plots.
    """
    viz = CryptoVisualizer(master_key)
    words = text.split()

    bit_map = []
    points_3d = []
    axis_labels = []

    iv = 15
    p_idx, f_idx = 0, 0

    while p_idx < len(words) and p_idx < 40:
        if viz.manifold.is_noise_position(f_idx):
            bits, x, y, z, intense = viz.manifold.project_position(
                f_idx, 0, iv)
            bit_map.append(bits)
            points_3d.append([x, y, z, intense])
            axis_labels.append(f"[NOISE_{f_idx}]")
            f_idx += 1
            continue

        lattice_d = viz.lattice_mock[f_idx % 1000]
        bits, x, y, z, intense = viz.manifold.project_position(
            f_idx, lattice_d, iv)

        bit_map.append(bits)
        points_3d.append([x, y, z, intense])

        label = re.sub(r'[^a-zA-Z]', '', words[p_idx])
        axis_labels.append(f"{label}_{p_idx}")

        p_idx += 1
        f_idx += 1

    # --- RENDER ENGINE ---
    sns.set_theme(style="white")
    fig = plt.figure(figsize=(20, 10))

    # 1. ENTROPY FINGERPRINT (Heatmap)
    ax1 = fig.add_subplot(121)
    df = pd.DataFrame(bit_map)
    sns.heatmap(df, cmap="mako", cbar=False, yticklabels=axis_labels, ax=ax1)
    ax1.set_title("ENTROPY FINGERPRINT (Bit-level Logic)", fontsize=14)
    ax1.set_xlabel("State Bit Index (First 64 bits)")

    # 2. 3D MANIFOLD CLOUD (Spatial Projection)
    ax2 = fig.add_subplot(122, projection='3d')
    pts = np.array(points_3d)

    # Trajectory path rendering
    ax2.plot(pts[:, 0], pts[:, 1], pts[:, 2], color='#475569',
             alpha=0.5, lw=1.5, linestyle='-')

    # Scatter plot with energy density mapping
    scatter = ax2.scatter(pts[:, 0], pts[:, 1], pts[:, 2],
                          c=pts[:, 3], cmap='viridis', s=130,
                          edgecolors='white', linewidth=0.5, alpha=0.95)

    cbar = fig.colorbar(scatter, ax=ax2, shrink=0.5, aspect=10)
    cbar.set_label('Hamming Weight (Energy Density)')

    ax2.set_xlabel('Dim X (Byte 0)')
    ax2.set_ylabel('Dim Y (Byte 1)')
    ax2.set_zlabel('Dim Z (Byte 2)')
    ax2.set_title("3D SHADOW OF THE 256-BIT MANIFOLD", fontsize=14)

    ax2.xaxis.pane.fill = False
    ax2.yaxis.pane.fill = False
    ax2.zaxis.pane.fill = False
    ax2.grid(True, linestyle=':', alpha=0.4)

    plt.suptitle(f"NONI ENGINE - HIGH-DIMENSIONAL ANALYSIS\nMaster Key: {master_key.upper()}",
                 fontsize=16, y=0.95)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    test_phrase = "hello hello hello hello hello hello hello hello hello hello hello"
    visualize_high_dim_manifold("girasol", test_phrase)
