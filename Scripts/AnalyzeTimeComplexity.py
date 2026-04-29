# --- IMPORT SECTION ---
import os      # For file path management.
import sys
sys.path.append(r"c:\Coding\SeniorThesis\Core\Optimized")
import time    # To measure performance (how long tasks take).
from Encoder import HuffmanEncoder # My compression utility.
from Decoder import HuffmanDecoder # My decompression utility.

# --- CONFIGURATION ---
# Where to find data and where to save results.
DATA_DIR = "TimeComplexitySource"
PROCESSED_DIR = "TimeComplexityProcessed"
RESULT_FILE = r"c:\Coding\SeniorThesis\Results\v2.0\TimeComplexityTest.txt"

# A sample text block to be used for generating test files.
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

# --- STEP 1: PREPARE EXPERIMENT DATA ---
def prepare_complexity_tests():
    # Ensure directories exist.
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)
    
    # I want to test how the algorithm performs as files get bigger.
    # target_repetitions defines how many times I repeat the text block.
    # 1772 bytes/block -> 11287 ~ 20MB, 22573 ~ 40MB, 45147 ~ 80MB
    target_repetitions = [100, 500, 1000, 2000, 5000, 10000]
    file_list = []

    for i, count in enumerate(target_repetitions):
        filename = f"ProseSize_{count}.txt"
        path = os.path.join(DATA_DIR, filename)
        # Write the text block multiplied by the repetition count.
        with open(path, "w", encoding="utf-8") as f:
            f.write(TEXT_BLOCK * count)
        file_list.append(filename)
    
    return file_list

# --- STEP 2: RUN PERFORMANCE ANALYSIS ---
def run_complexity_analysis(files):
    encoder = HuffmanEncoder()
    decoder = HuffmanDecoder()
    
    # Open the result file to write the table.
    with open(RESULT_FILE, "w") as out:
        # Header for the table.
        out.write(f"{'Filename':<25} | {'Size (Bytes)':<12} | {'Enc Time (ms)':<15} | {'Dec Time (ms)':<15}\n")
        out.write("-" * 75 + "\n")
        
        for filename in files:
            orig_path = os.path.join(DATA_DIR, filename)
            comp_path = os.path.join(PROCESSED_DIR, filename.replace(".txt", ".bin"))
            dec_path = os.path.join(PROCESSED_DIR, filename.replace(".txt", "_decomp.txt"))
            
            size = os.path.getsize(orig_path)
            
            # --- Measure Compression Time ---
            start = time.perf_counter() # High precision timer
            encoder.compress(orig_path, comp_path)
            enc_time = (time.perf_counter() - start) * 1000 # Convert to ms
            
            # --- Measure Decompression Time ---
            start = time.perf_counter()
            decoder.decompress(comp_path, dec_path)
            dec_time = (time.perf_counter() - start) * 1000
            
            # Write results to the table.
            out.write(f"{filename:<25} | {size:<12} | {enc_time:<15.2f} | {dec_time:<15.2f}\n")
            print(f"Tested {filename} ({size} bytes)")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    test_files = prepare_complexity_tests()
    run_complexity_analysis(test_files)
    print(f"\nFinal results saved to {RESULT_FILE}")

