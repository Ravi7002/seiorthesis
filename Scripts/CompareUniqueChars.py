# --- IMPORT SECTION ---
# This script stress-tests the TREE-BUILDING phase specifically by varying the
# number of unique characters (alphabet size 'n') in the test files.
#
# Why? The Heap uses O(n log n) and the Naive uses O(n^2) ONLY for tree building.
# With normal English text (n ~ 90), the difference is negligible.
# By pushing n up to 256 (all printable ASCII), we can actually see the divergence.

import os
import sys
import time
import random
import string

BASE_DIR = r"c:\Coding\SeniorThesis"
sys.path.append(os.path.join(BASE_DIR, "Core", "Optimized"))

from Encoder import HuffmanEncoder
from EncoderNaive import NaiveHuffmanEncoder

# --- CONFIGURATION ---
DATA_DIR   = os.path.join(BASE_DIR, "TimeComplexitySource")
PROC_DIR   = os.path.join(BASE_DIR, "TimeComplexityProcessed")
RESULT_FILE = os.path.join(BASE_DIR, "Results", "v2.0", "UniqueCharComparison.txt")

# All 256 possible byte values (0-255) as characters.
ALL_256_CHARS = [chr(i) for i in range(256)]

# How many repetitions to use per file (large enough to measure time reliably).
FILE_REPS = 500_000  # ~500k characters per file — tree building cost dominates at small n

# Unique character counts to test
UNIQUE_COUNTS = [2, 4, 8, 16, 32, 64, 128, 200, 256]


def prepare_test_files():
    """Generate one test file per unique character count."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(PROC_DIR, exist_ok=True)

    paths = []
    for n in UNIQUE_COUNTS:
        # Pick the first n characters from the full 256-char pool.
        charset = ALL_256_CHARS[:n]
        filename = f"UniqueChars_{n}.txt"
        path = os.path.join(DATA_DIR, filename)

        # Build content: repeat the charset cyclically so every char appears equally.
        # This makes the frequency distribution uniform — the hardest case for tree building.
        content = (charset * ((FILE_REPS // n) + 1))[:FILE_REPS]
        content_str = "".join(content)

        with open(path, "w", encoding="utf-8", errors="replace") as f:
            f.write(content_str)

        paths.append(path)
        size_kb = os.path.getsize(path) / 1024
        print(f"  Created {filename} ({n} unique chars, {size_kb:.1f} KB)")

    return paths


def run_comparison(file_paths):
    heap_encoder  = HuffmanEncoder()
    naive_encoder = NaiveHuffmanEncoder()

    results = []

    header = (
        f"{'Filename':<25} | {'Unique Chars':<13} | {'Size (KB)':<10} | "
        f"{'Heap Time (ms)':<16} | {'Naive Time (ms)':<16} | {'Diff (ms)':<10}"
    )
    separator = "-" * len(header)

    print("\n" + header)
    print(separator)

    for i, path in enumerate(file_paths):
        filename  = os.path.basename(path)
        n_unique  = int(filename.split("_")[1].split(".")[0])
        size_kb   = os.path.getsize(path) / 1024

        heap_out  = os.path.join(PROC_DIR, filename + ".heap.bin")
        naive_out = os.path.join(PROC_DIR, filename + ".naive.bin")

        # --- Alternate run order to cancel out OS file-cache bias ---
        # When the same file is read twice in a row, the 2nd encoder benefits
        # from the OS page cache (file already in RAM). By alternating who goes
        # first, neither encoder gets a systematic advantage.
        if i % 2 == 0:
            # Even index: Heap first
            start = time.perf_counter()
            heap_encoder.compress(path, heap_out)
            heap_time = (time.perf_counter() - start) * 1000

            start = time.perf_counter()
            naive_encoder.compress(path, naive_out)
            naive_time = (time.perf_counter() - start) * 1000
        else:
            # Odd index: Naive first
            start = time.perf_counter()
            naive_encoder.compress(path, naive_out)
            naive_time = (time.perf_counter() - start) * 1000

            start = time.perf_counter()
            heap_encoder.compress(path, heap_out)
            heap_time = (time.perf_counter() - start) * 1000

        diff = naive_time - heap_time
        results.append((filename, n_unique, size_kb, heap_time, naive_time, diff))

        row = (
            f"{filename:<25} | {n_unique:<13} | {size_kb:<10.1f} | "
            f"{heap_time:<16.2f} | {naive_time:<16.2f} | {diff:<10.2f}"
        )
        print(row)

    # --- Write to result file ---
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        f.write("Comparison of Huffman Encoding: Heap vs Naive (Varying Unique Characters)\n")
        f.write("=" * len(header) + "\n")
        f.write("Each file has the same total size (~500 KB) but a different number of unique\n")
        f.write("characters. This isolates the O(n log n) vs O(n^2) tree-building cost.\n")
        f.write("A positive Diff means Naive is SLOWER than Heap.\n")
        f.write("\n")
        f.write(header + "\n")
        f.write(separator + "\n")
        for res in results:
            f.write(
                f"{res[0]:<25} | {res[1]:<13} | {res[2]:<10.1f} | "
                f"{res[3]:<16.2f} | {res[4]:<16.2f} | {res[5]:<10.2f}\n"
            )
        f.write("\n")
        f.write("Notes:\n")
        f.write("  - 'n' = number of unique characters (alphabet size).\n")
        f.write("  - Heap tree building: O(n log n)\n")
        f.write("  - Naive tree building: O(n^2)  [linear scan for minimum each step]\n")
        f.write("  - As n grows, the gap between Heap and Naive should widen.\n")
        f.write("  - All files are ~500 KB to keep encoding time (O(N)) roughly constant.\n")
        f.write("  - Run order alternates per file (even=Heap first, odd=Naive first) to\n")
        f.write("    cancel out OS page-cache bias from reading the same file twice.\n")

    print(f"\nResults saved to: {RESULT_FILE}")


if __name__ == "__main__":
    print("Preparing test files...")
    paths = prepare_test_files()
    print("\nRunning comparison...")
    run_comparison(paths)

    # Clean up temp files
    import shutil
    shutil.rmtree(DATA_DIR, ignore_errors=True)
    shutil.rmtree(PROC_DIR, ignore_errors=True)
    print("Temp files cleaned up.")
