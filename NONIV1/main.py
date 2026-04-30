import time
import textwrap
from core.engine import CipherEngine


def normalize_for_test(text):
    """
    Removes accents for basic synchronization comparison.
    """
    accents = str.maketrans("áéíóúüÁÉÍÓÚÜ", "aeiouuAEIOUU")
    return text.translate(accents).split()


def print_data_block(title, text, width=80):
    """
    Formats text output into titled blocks for better readability.
    """
    print(f"\n[{title}]")
    print(textwrap.fill(text, width=width))


def run_system_demonstration():
    """
    Executes a complete encryption/decryption cycle to validate 
    functional integrity and measure processing latency.
    """
    # Placeholder for user-defined input
    original_text = "Insert your phrase or text here"

    engine = CipherEngine(master_key="girasol")

    print("="*60)
    print("CIPHER ENGINE: END-TO-END DEMONSTRATION")
    print("="*60)

    # Measure encryption performance
    start_enc = time.perf_counter()
    encrypted_package = engine.encrypt(original_text)
    end_enc = time.perf_counter()

    # Measure decryption performance
    start_dec = time.perf_counter()
    recovered_text = engine.decrypt(encrypted_package)
    end_dec = time.perf_counter()

    print_data_block("ORIGINAL PLAINTEXT", original_text)
    print_data_block(
        "ENCRYPTED PAYLOAD (HMAC + SALT + IV + BODY)", encrypted_package)
    print_data_block("RECOVERED PLAINTEXT", recovered_text)

    # Integrity verification
    original_normalized = [w.lower()
                           for w in normalize_for_test(original_text)]
    recovered_normalized = [w.lower() for w in recovered_text.split()]

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
            f"Mismatch detected. Input: {len(original_normalized)} words | Output: {len(recovered_normalized)} words")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_system_demonstration()
