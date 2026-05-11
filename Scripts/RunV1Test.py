import os, sys, time

sys.path.insert(0, r'c:\Coding\SeniorThesis\Core\Unoptimized')
from Encoder import HuffmanEncoder
from Decoder import HuffmanDecoder

DATA_DIR = 'TimeComplexitySource'
PROCESSED_DIR = 'TimeComplexityProcessed'
RESULT_FILE = r'c:\Coding\SeniorThesis\Results\v1.0\TimeComplexityTest.txt'

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

TEXT_BLOCK = """
It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.
However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered the rightful property of some one or other of their daughters.
My dear Mr. Bennet, said his lady to him one day, have you heard that Netherfield Park is let at last?
Mr. Bennet replied that he had not.
But it is, returned she; for Mrs. Long has just been here, and she told me all about it.
Mr. Bennet made no answer.
Do you not want to know who has taken it? cried his wife impatiently.
You want to tell me, and I have no objection to hearing it.
This was invitation enough.
Why, my dear, you must know, Mrs. Long says that Netherfield is taken by a young man of large fortune from the north of England; that he came down on Monday in a chaise and four to see the place, and was so much delighted with it, that he agreed with Mr. Morris immediately; that he is to take possession before Michaelmas, and some of his servants are to be in the house by the end of next week.
What is his name?
Bingley.
Is he married or single?
Oh! Single, my dear, to be sure! A single man of large fortune; four or five thousand a year. What a fine thing for our girls!
How so? How can it affect them?
My dear Mr. Bennet, replied his wife, how can you be so tiresome! You must know that I am thinking of his marrying one of them.
Is that his design in settling here?
Design! Nonsense, how can you talk so! But it is very likely that he may fall in love with one of them, and therefore you must visit him as soon as he comes.
"""

target_repetitions = [100, 500, 1000, 2000, 5000, 10000]
encoder = HuffmanEncoder()
decoder = HuffmanDecoder()

os.makedirs(os.path.dirname(RESULT_FILE), exist_ok=True)
with open(RESULT_FILE, 'w') as out:
    out.write(f"{'Filename':<25} | {'Size (Bytes)':<12} | {'Enc Time (ms)':<15} | {'Dec Time (ms)':<15}\n")
    out.write('-' * 75 + '\n')
    for count in target_repetitions:
        filename = f'ProseSize_{count}.txt'
        orig_path = os.path.join(DATA_DIR, filename)
        comp_path = os.path.join(PROCESSED_DIR, filename.replace('.txt', '.bin'))
        dec_path  = os.path.join(PROCESSED_DIR, filename.replace('.txt', '_decomp.txt'))
        with open(orig_path, 'w', encoding='utf-8') as f:
            f.write(TEXT_BLOCK * count)
        size = os.path.getsize(orig_path)
        start = time.perf_counter()
        encoder.compress(orig_path, comp_path)
        enc_time = (time.perf_counter() - start) * 1000
        start = time.perf_counter()
        decoder.decompress(comp_path, dec_path)
        dec_time = (time.perf_counter() - start) * 1000
        out.write(f'{filename:<25} | {size:<12} | {enc_time:<15.2f} | {dec_time:<15.2f}\n')
        print(f'Tested {filename} ({size} bytes)')

print(f'\nFinal results saved to {RESULT_FILE}')
