import time
import os
from core.engine import CipherEngine


def normalize_text_integrity(text, engine):
    """
    Standardizes text for integrity comparison by handling 
    accents, special dashes, and whitespace normalization.
    """
    text = text.lower()
    text = engine._strip_accents(text)
    text = text.replace('—', '-')
    # Remove multiple spaces and newlines for a clean word-by-word comparison
    text = " ".join(text.split())
    return text


def run_volume_stress_test(file_path="donquijote.txt", master_key="girasol"):
    """
    Executes a high-volume performance and integrity test 
    using a full literary work.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        original_text = f.read()

    engine = CipherEngine(master_key=master_key)

    print("="*60)
    print("STRESS TEST: HIGH-VOLUME DATA INTEGRITY")
    print("="*60)
    print(f"Source file:  {file_path}")
    print(f"Payload size: {len(original_text) / 1024:.2f} KB")
    print("-" * 60)

    # Performance measurement for encryption
    print("Executing encryption...")
    start_enc = time.perf_counter()
    encrypted_payload = engine.encrypt(original_text)
    end_enc = time.perf_counter()

    # Performance measurement for decryption
    print("Executing decryption...")
    start_dec = time.perf_counter()
    recovered_text = engine.decrypt(encrypted_payload)
    end_dec = time.perf_counter()

    enc_latency = end_enc - start_enc
    total_words = len(original_text.split())
    ms_per_word = (enc_latency / total_words) * 1000 if total_words > 0 else 0

    # Data preview for visual confirmation
    print("\n[DATA PREVIEW]")
    print(f"Original:  {original_text[:80].replace('\n', ' ')}...")
    print(f"Recovered: {recovered_text[:80].replace('\n', ' ')}...")

    print("\n" + "="*60)
    print("PERFORMANCE AND INTEGRITY REPORT")
    print("="*60)
    print(f"Total words:         {total_words:,}")
    print(f"Encryption latency:  {enc_latency:.4f} seconds")
    print(f"Processing speed:    {ms_per_word:.4f} ms/word")
    print("-" * 60)

    # Deep integrity verification
    print("Verifying synchronization integrity...")

    source_clean = normalize_text_integrity(original_text, engine)
    recovered_clean = " ".join(recovered_text.split()).strip()

    if source_clean == recovered_clean:
        print("Status: INTEGRITY VERIFIED (100% match)")
    else:
        print("Status: INTEGRITY FAILURE")
        # Identify the exact point of divergence for debugging
        for i in range(len(source_clean)):
            if i >= len(recovered_clean) or source_clean[i] != recovered_clean[i]:
                print(f"\nMismatch identified at character index {i}:")
                print(f"Expected: ...{source_clean[max(0, i-25):i+25]}...")
                print(f"Received: ...{recovered_clean[max(0, i-25):i+25]}...")
                break
    print("="*60 + "\n")


if __name__ == "__main__":
    run_volume_stress_test()
