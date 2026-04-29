import os
import time
import json
import sys

BASE_DIR = r"c:\Coding\SeniorThesis"
sys.path.append(os.path.join(BASE_DIR, "Core", "Unoptimized"))
from Encoder import HuffmanEncoder

sys.path.insert(0, os.path.join(BASE_DIR, "Core", "Optimized"))
from EncoderNaive import NaiveHuffmanEncoder

# --- CONFIGURATION ---
DATA_DIR = os.path.join(BASE_DIR, "TimeComplexitySource")
PROCESSED_DIR = os.path.join(BASE_DIR, "TimeComplexityProcessed")
COMPARISON_FILE = os.path.join(BASE_DIR, "Results", "UnoptimizedTest", "Heap&Naive.txt")

# Sample text to build files from
TEXT_BLOCK = """
It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.
However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered the rightful property of some one or other of their daughters.
"My dear Mr. Bennet," said his lady to him one day, "have you heard that Netherfield Park is let at last?"
Mr. Bennet replied that he had not.
"But it is," returned she; "for Mrs. Long has just been here, and she told me all about it."
Mr. Bennet made no answer.
"Do you not want to know who has taken it?" cried his wife impatiently.
"You want to tell me, and I have no objection to hearing it."
This was invitation enough.
"Why, my dear, you must know, Mrs. Long says that Netherfield is taken by a young man of large fortune from the north of England; that he came down on Monday in a chaise and four to see the place, and was so much delighted with it, that he agreed with Mr. Morris immediately; that he is to take possession before Michaelmas, and some of his servants are to be in the house by the end of next week."
"What is his name?"
"Bingley."
"Is he married or single?"
"Oh! Single, my dear, to be sure! A single man of large fortune; four or five thousand a year. What a fine thing for our girls!"
"How so? How can it affect them?"
"My dear Mr. Bennet," replied his wife, "how can you be so tiresome! You must know that I am thinking of his marrying one of them."
"Is that his design in settling here?"
"Design! Nonsense, how can you talk so! But it is very likely that he may fall in love with one of them, and therefore you must visit him as soon as he comes."
"""

def prepare_test_files():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)
    
    # Range of repetitions to create different file sizes
    target_repetitions = [1, 10, 100, 500, 1000, 2000]
    paths = []

    for count in target_repetitions:
        filename = f"ProseSize_{count}.txt"
        path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(TEXT_BLOCK * count)
        paths.append(path)
    
    return paths

def run_comparison(file_paths):
    heap_encoder = HuffmanEncoder()
    naive_encoder = NaiveHuffmanEncoder()
    
    results = []
    
    print(f"{'Filename':<25} | {'Size (KB)':<10} | {'Heap Time (ms)':<15} | {'Naive Time (ms)':<15} | {'Diff (ms)':<10}")
    print("-" * 85)
    
    for path in file_paths:
        filename = os.path.basename(path)
        size_kb = os.path.getsize(path) / 1024
        
        # Test Heap Encoder
        start = time.perf_counter()
        heap_encoder.compress(path, os.path.join(PROCESSED_DIR, filename + ".heap.bin"))
        heap_time = (time.perf_counter() - start) * 1000
        
        # Test Naive Encoder
        start = time.perf_counter()
        naive_encoder.compress(path, os.path.join(PROCESSED_DIR, filename + ".naive.bin"))
        naive_time = (time.perf_counter() - start) * 1000
        
        diff = naive_time - heap_time
        
        results.append((filename, size_kb, heap_time, naive_time, diff))
        print(f"{filename:<25} | {size_kb:<10.2f} | {heap_time:<15.2f} | {naive_time:<15.2f} | {diff:<10.2f}")

    # Save to file
    with open(COMPARISON_FILE, "w") as f:
        f.write("Comparison of Huffman Encoding Performance: Heap vs Naive Tree Building\n")
        f.write("=" * 85 + "\n")
        f.write(f"{'Filename':<25} | {'Size (KB)':<10} | {'Heap Time (ms)':<15} | {'Naive Time (ms)':<15} | {'Diff (ms)':<10}\n")
        f.write("-" * 85 + "\n")
        for res in results:
            f.write(f"{res[0]:<25} | {res[1]:<10.2f} | {res[2]:<15.2f} | {res[3]:<15.2f} | {res[4]:<10.2f}\n")
        
        f.write("\nNote: The Heap implementation uses O(n log n) for tree building, while the Naive uses O(n^2).\n")
        f.write("'n' is the number of unique characters (alphabet size).\n")
        f.write("For larger files, the O(N) scanning and encoding time (where N is file size) will dominate.\n")

if __name__ == "__main__":
    files = prepare_test_files()
    run_comparison(files)
    print(f"\nDetailed comparison results saved to {COMPARISON_FILE}")
