# --- IMPORT SECTION ---
import os      # For file path management.
import sys
sys.path.append(r"c:\Coding\SeniorThesis\Core\Optimized")
import time    # To measure performance (how long tasks take).
from EncoderNaive import NaiveHuffmanEncoder # My naive compression tool.
from Decoder import HuffmanDecoder # My decompression utility.

# --- CONFIGURATION ---
DATA_DIR = "TimeComplexitySource"
PROCESSED_DIR = "TimeComplexityProcessed"
RESULT_FILE = r"c:\Coding\SeniorThesis\Results\v2.0\TimeComplexityNaive.txt"

# --- STEP 1: LOAD EXPERIMENT DATA ---
def get_test_files():
    # We use the existing files created by the other analysis script.
    if not os.path.exists(DATA_DIR):
        print(f"Error: {DATA_DIR} does not exist. Run AnalyzeTimeComplexity.py first.")
        return []
    
    file_list = [f for f in os.listdir(DATA_DIR) if f.startswith("ProseSize_") and f.endswith(".txt")]
    # Sort files by the numeric value in the filename to have a clear progression
    file_list.sort(key=lambda x: int(x.split("_")[1].split(".")[0]))
    return file_list

# --- STEP 2: RUN PERFORMANCE ANALYSIS ---
def run_complexity_analysis(files):
    encoder = NaiveHuffmanEncoder()
    decoder = HuffmanDecoder()
    
    # Open the result file to write the table.
    with open(RESULT_FILE, "w") as out:
        # Header for the table.
        out.write(f"{'Filename':<25} | {'Size (Bytes)':<15} | {'Enc Time (ms)':<15} | {'Dec Time (ms)':<15}\n")
        out.write("-" * 80 + "\n")
        
        for filename in files:
            orig_path = os.path.join(DATA_DIR, filename)
            comp_path = os.path.join(PROCESSED_DIR, filename.replace(".txt", "_naive.bin"))
            dec_path = os.path.join(PROCESSED_DIR, filename.replace(".txt", "_naive_decomp.txt"))
            
            size = os.path.getsize(orig_path)
            
            # --- Measure Compression Time ---
            start = time.perf_counter()
            encoder.compress(orig_path, comp_path)
            enc_time = (time.perf_counter() - start) * 1000
            
            # --- Measure Decompression Time ---
            start = time.perf_counter()
            decoder.decompress(comp_path, dec_path)
            dec_time = (time.perf_counter() - start) * 1000
            
            # Write results to the table.
            out.write(f"{filename:<25} | {size:<15} | {enc_time:<15.2f} | {dec_time:<15.2f}\n")
            print(f"Tested Naive: {filename} ({size} bytes) -> Enc: {enc_time:.2f}ms")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    test_files = get_test_files()
    if test_files:
        run_complexity_analysis(test_files)
        print(f"\nNaive analysis results saved to {RESULT_FILE}")
