import time
import os
import re
from core.engine import CipherEngine


def normalize_text_integrity(text, engine):
    """
    Normalizes text for integrity auditing while preserving the character 
    structure that the engine is designed to encrypt.
    """
    text = text.lower()
    text = engine._strip_accents(text)

    # Synchronize spacing to ensure identical word list generation
    text = " ".join(text.split())
    return text


def run_volume_stress_test(file_path="donquijote.txt", master_key="girasol"):
    """
    Executes a high-volume stress test and integrity audit using 
    a complete literary work.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1") as f:
            original_content = f.read()

    engine = CipherEngine(master_key=master_key)

    print("="*60)
    print("STRESS TEST: HIGH-VOLUME DATA INTEGRITY")
    print("="*60)
    print(f"Source file:     {file_path}")
    print(f"Payload size:    {len(original_content) / 1024:.2f} KB")
    print("-" * 60)

    # --- ENCRYPTION PHASE ---
    print("Executing encryption...")
    start_enc = time.perf_counter()
    encrypted_payload = engine.encrypt(original_content)
    end_enc = time.perf_counter()

    # --- DECRYPTION PHASE ---
    print("Executing decryption...")
    start_dec = time.perf_counter()
    recovered_text = engine.decrypt(encrypted_payload)
    end_dec = time.perf_counter()

    enc_latency = end_enc - start_enc

    # --- INTEGRITY AUDIT ---
    source_clean = normalize_text_integrity(original_content, engine)
    recovered_clean = normalize_text_integrity(recovered_text, engine)

    source_words = source_clean.split()
    recovered_words = recovered_clean.split()
    total_words = len(source_words)

    ms_per_word = (enc_latency / total_words) * 1000 if total_words > 0 else 0

    error_count = 0
    first_mismatch_idx = -1

    # Word-by-word comparison
    min_len = min(len(source_words), len(recovered_words))

    for i in range(min_len):
        if source_words[i] != recovered_words[i]:
            error_count += 1
            if first_mismatch_idx == -1:
                first_mismatch_idx = i

    len_diff = abs(len(source_words) - len(recovered_words))
    error_count += len_diff

    success_rate = ((total_words - error_count) / total_words) * \
        100 if total_words > 0 else 0

    print("\n" + "="*60)
    print("PERFORMANCE & INTEGRITY REPORT")
    print("="*60)
    print(f"Processed words:    {total_words:,}")
    print(f"Errors found:       {error_count:,}")
    print(f"Success rate (ISR): {success_rate:.4f}%")
    print("-" * 60)
    print(f"Encryption latency: {enc_latency:.4f} seconds")
    print(f"Processing speed:   {ms_per_word:.4f} ms/word")
    print("-" * 60)

    if error_count == 0:
        print("Status: INTEGRITY VERIFIED (100% match)")
    else:
        print("Status: INTEGRITY FAILURE")
        if first_mismatch_idx != -1:
            print(f"\nFirst error detected at index {first_mismatch_idx}:")
            print(f"Expected: '{source_words[first_mismatch_idx]}'")
            print(f"Received: '{recovered_words[first_mismatch_idx]}'")

            start_ctx = max(0, first_mismatch_idx - 2)
            end_ctx = min(total_words, first_mismatch_idx + 3)
            print(
                f"Context: ... {' '.join(source_words[start_ctx:end_ctx])} ...")

        if len_diff > 0:
            print(f"Notice: Length mismatch of {len_diff} words detected.")

    print("="*60 + "\n")


if __name__ == "__main__":
    run_volume_stress_test()
