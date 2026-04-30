import numpy as np
import secrets
import time
from core.engine import CipherEngine


def run_statistical_audit(master_key="girasol", iterations=1_000_000):
    """
    Executes a statistical analysis of the manifold rule distribution.
    Validates bit activation probability and Shannon entropy across 1M iterations.
    """
    engine = CipherEngine(master_key=master_key)

    # Internal state initialization
    random_salt = secrets.token_bytes(16)
    engine._initialize_with_salt(random_salt)

    # Matrix allocation for bit tracking
    activation_matrix = np.zeros((iterations, 5), dtype=np.int8)

    print(f"Starting statistical audit: {iterations:,} iterations...")
    start_time = time.time()

    for i in range(iterations):
        # IV rotation for maximum state coverage
        iv_val = (i % 0xFFFFFFFF) + 1

        # Project manifold state
        v_man, _, _ = engine.manifold.project_position(i, iv_val)

        # Map bits to activation matrix
        for j in range(5):
            activation_matrix[i, j] = (v_man >> j) & 1

    duration = time.time() - start_time

    # Results Formatting
    print("\n" + "="*60)
    print(f"AUDIT REPORT SUMMARY")
    print("="*60)
    print(f"Execution time: {duration:.4f} seconds")
    print(f"Throughput:     {iterations/duration:.2f} iterations/sec")
    print("-" * 60)

    rule_names = ['INV', 'ROTA', 'ESP', 'ALT', 'SHF']
    for idx, name in enumerate(rule_names):
        percentage = (np.sum(activation_matrix[:, idx]) / iterations) * 100
        bias = abs(50 - percentage)
        print(
            f"Rule {name:4}: {percentage:8.4f}% activation (Bias: {bias:.4f}%)")

    # Entropy Calculation
    flat_bits = activation_matrix.flatten()
    p1 = np.mean(flat_bits)
    p0 = 1 - p1
    entropy = - (p0 * np.log2(p0) + p1 * np.log2(p1)) if 0 < p1 < 1 else 0

    print("-" * 60)
    print(f"Global Shannon Entropy: {entropy:.6f} / 1.000000")

    unique_maps = len(set(map(tuple, activation_matrix[:1000])))
    print(f"Manifold Coverage:      {unique_maps}/32 combinations")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_statistical_audit()
