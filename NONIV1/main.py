import time
import textwrap
from core.engine import CipherEngine


def normalize_for_test(text, engine):
    """
    Standardizes text by removing accents and synchronizing case 
    for integrity comparison.
    """
    # Using the engine's internal method for consistency
    text = engine._strip_accents(text.lower())
    return text.split()


def print_data_block(title, text, width=80):
    """
    Formats text output into titled blocks for enhanced readability.
    """
    print(f"\n[{title}]")
    print(textwrap.fill(text, width=width))


def run_system_demonstration():
    """
    Executes a complete end-to-end cycle to validate functional 
    integrity and measure processing latency.
    """
    # Demonstration payload
    original_text = "The quick brown fox jumps over the lazy dog."

    # Initialize engine with the master key
    engine = CipherEngine(master_key="girasol")

    print("="*60)
    print("NONI ENGINE: SYSTEM DEMONSTRATION")
    print("="*60)

    # Performance measurement: Encryption
    start_enc = time.perf_counter()
    encrypted_package = engine.encrypt(original_text)
    end_enc = time.perf_counter()

    # Performance measurement: Decryption
    start_dec = time.perf_counter()
    recovered_text = engine.decrypt(encrypted_package)
    end_dec = time.perf_counter()

    print_data_block("ORIGINAL PLAINTEXT", original_text)
    print_data_block("ENCRYPTED PAYLOAD (CIPHERTEXT)", encrypted_package)
    print_data_block("RECOVERED PLAINTEXT", recovered_text)

    # Integrity verification via normalized comparison
    original_normalized = normalize_for_test(original_text, engine)
    recovered_normalized = recovered_text.lower().split()

    latency = end_enc - start_enc

    print("\n" + "="*60)
    print("EXECUTION METRICS")
    print("="*60)
    print(f"Encryption latency: {latency:.4f} seconds")

    if original_normalized == recovered_normalized:
        print("Status: INTEGRITY VERIFIED")
        print("The recovered message matches the source input.")
    else:
        print("Status: SYNCHRONIZATION ERROR")
        print(
            f"Input: {len(original_normalized)} words | Output: {len(recovered_normalized)} words")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_system_demonstration()
