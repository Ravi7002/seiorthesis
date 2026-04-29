# --- IMPORT SECTION ---
import os      # For path and folder management.
import sys
sys.path.append(r"c:\Coding\SeniorThesis\Core\Unoptimized")
import random  # To generate random data for testing.
import string  # To get lists of letters and symbols easily.
import time    # To measure how fast my code is.
from Encoder import HuffmanEncoder # My compression tool.
from Decoder import HuffmanDecoder # My decompression tool.

# --- CONFIGURATION ---
# I'll put the test files in these folders.
SOURCE_DIR = "SourceData"
PROCESSED_DIR = "ProcessedData"

# --- STEP 1: CREATE TEST FILES ---
def create_tests():
    # Make sure the folders exist. If not, create them.
    if not os.path.exists(SOURCE_DIR):
        os.makedirs(SOURCE_DIR)
    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)

    # TEST CASE 1: High-Redundancy (Lots of the same thing)
    # I'm writing 1,000 "A" characters.
    with open(os.path.join(SOURCE_DIR, "HighRedundancy.txt"), "w") as f:
        f.write("A" * 1000)

    # TEST CASE 2: Standard English Prose
    # Using a famous book paragraph as a sample.
    text_block = """
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
    # Repeat the paragraph 25 times to make a larger file.
    with open(os.path.join(SOURCE_DIR, "EnglishProse.txt"), "w", encoding='utf-8') as f:
        f.write(text_block * 25)

    # TEST CASE 3: Source Code
    # Let's see how it handles Python code!
    with open(r"c:\Coding\SeniorThesis\Core\Unoptimized\Encoder.py", "r") as src:
        content = src.read()
    with open(os.path.join(SOURCE_DIR, "SourceCode.py"), "w", encoding='utf-8') as f:
        f.write(content)

    # TEST CASE 4: Short String
    with open(os.path.join(SOURCE_DIR, "ShortString.txt"), "w", encoding='utf-8') as f:
        f.write("Hello World")

    # TEST CASE 5: Random Data (Hard to compress!)
    # Generates 5,000 random characters.
    random_text = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=5000))
    with open(os.path.join(SOURCE_DIR, "RandomASCII.txt"), "w", encoding='utf-8') as f:
        f.write(random_text)

    print(f"Original test files created in {SOURCE_DIR}")

# --- STEP 2: RUN THE TESTS ---
def run_tests():
    files = [
        "HighRedundancy.txt",
        "EnglishProse.txt",
        "SourceCode.py",
        "ShortString.txt",
        "RandomASCII.txt"
    ]

    encoder = HuffmanEncoder()
    decoder = HuffmanDecoder()

    # I'll save the results of my experiment in this text file.
    with open(r"c:\Coding\SeniorThesis\Results\UnoptimizedTest\test_status.txt", "w") as status_file:
        for filename in files:
            original_path = os.path.join(SOURCE_DIR, filename)
            base_name = os.path.splitext(filename)[0]
            compressed_path = os.path.join(PROCESSED_DIR, base_name + ".bin")
            decompressed_path = os.path.join(PROCESSED_DIR, base_name + "_decompressed.txt")
            
            # 1. COMPRESS (and time it)
            start_enc = time.time()
            encoder.compress(original_path, compressed_path)
            end_enc = time.time()
            enc_time = (end_enc - start_enc) * 1000 # convert to milliseconds

            if not os.path.exists(compressed_path):
                status_file.write(f"{filename}: FAIL (Compression)\n")
                continue
                
            # 2. DECOMPRESS (and time it)
            start_dec = time.time()
            decoder.decompress(compressed_path, decompressed_path)
            end_dec = time.time()
            dec_time = (end_dec - start_dec) * 1000 

            if not os.path.exists(decompressed_path):
                status_file.write(f"{filename}: FAIL (Decompression)\n")
                continue
                
            # 3. VERIFY (Did I get back exactly what I started with?)
            try:
                with open(original_path, 'r', encoding='utf-8') as f1:
                    original_text = f1.read()
                with open(decompressed_path, 'r', encoding='utf-8') as f2:
                    decompressed_text = f2.read()
                
                if original_text == decompressed_text:
                    orig_size = os.path.getsize(original_path)
                    comp_size = os.path.getsize(compressed_path)
                    # Savings as a percentage.
                    ratio = (1 - comp_size/orig_size) * 100 if orig_size > 0 else 0
                    
                    # Bits Per Character (BPC): Average bits used for each letter.
                    bpc = (comp_size * 8) / len(original_text) if len(original_text) > 0 else 0
                    
                    # Log the success metrics.
                    status_file.write(f"{filename}: SUCCESS | Size: {orig_size}->{comp_size} | Savings: {ratio:.2f}% | BPC: {bpc:.2f} | EncTime: {enc_time:.2f}ms | DecTime: {dec_time:.2f}ms\n")
                else:
                    status_file.write(f"{filename}: FAIL (Content Mismatch)\n")
            except Exception as e:
                status_file.write(f"{filename}: FAIL (Exception: {e})\n")

# START THE TEST SUITE
if __name__ == "__main__":
    create_tests()
    run_tests()

