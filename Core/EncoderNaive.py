# --- IMPORT SECTION ---
# These are built-in tools (libraries) I need for my script.
import os      # Used for handling file paths and file system tasks.
import json    # Used to convert data (like dictionaries) into text format.
from collections import Counter  # A quick way to count how many times each character appears in a string.

# --- DATA STRUCTURES ---
# This class represents a single "node" in the Huffman Tree.
class HeapNode:
    def __init__(self, char, freq):
        self.char = char   # The actual character.
        self.freq = freq   # How many times this character appeared.
        self.left = None   # Connection to the left child node.
        self.right = None  # Connection to the right child node.

# --- MAIN NAIVE ENCODER CLASS ---
class NaiveHuffmanEncoder:
    def __init__(self):
        # Initializing the workspace.
        self.nodes = []            # A simple list to help build the tree (instead of a heap).
        self.codes = {}            # A dictionary to store 'char': '0101' mappings.
        self.reverse_mapping = {}  # A dictionary to store '0101': 'char' mappings.

    # --- Step 1: Count Character Frequencies ---
    def make_frequency_dict(self, text):
        return dict(Counter(text))

    # --- Step 2: Build the Huffman Tree (NAIVE APPROACH) ---
    def make_tree(self, frequency):
        self.nodes = []
        tie_breaker = 0
        
        # 1. Create a "leaf" for every character and add it to a simple list.
        for key in sorted(frequency.keys()):
            node = HeapNode(key, frequency[key])
            self.nodes.append((frequency[key], tie_breaker, node))
            tie_breaker += 1
            
        # 2. Merge the two smallest nodes until only one "root" node remains.
        # Instead of using a heap, I will manually find the two nodes with the lowest frequency.
        while len(self.nodes) > 1:
            # Find the first node with the minimum frequency.
            item1 = min(self.nodes)
            self.nodes.remove(item1)
            
            # Find the second node with the minimum frequency.
            item2 = min(self.nodes)
            self.nodes.remove(item2)

            node1 = item1[2]
            node2 = item2[2]

            # Create a new "parent" node that combines their frequencies.
            merged = HeapNode(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2
            
            # Add this new branch back into the list.
            self.nodes.append((merged.freq, tie_breaker, merged))
            tie_breaker += 1

    # --- Step 3: Assign Binary Codes (0s and 1s) ---
    def make_codes_helper(self, root, current_code):
        if root is None:
            return

        if root.char is not None:
            self.codes[root.char] = current_code
            self.reverse_mapping[current_code] = root.char
            return

        self.make_codes_helper(root.left, current_code + "0")
        self.make_codes_helper(root.right, current_code + "1")

    def make_codes(self):
        if not self.nodes:
            return
            
        # The last remaining item in the list is the "root" of the tree.
        root_item = self.nodes[0]
        root = root_item[2]
        
        current_code = ""
        
        # Special case: If the file only has one type of character.
        if root.char is not None: 
             self.codes[root.char] = "0"
             self.reverse_mapping["0"] = root.char
             return

        self.make_codes_helper(root, current_code)
    
    def run_tree_building(self, frequency):
         self.nodes = []
         self.codes = {}
         self.reverse_mapping = {}
         
         self.make_tree(frequency)
         self.make_codes()

    # --- Step 4: Convert Text to Bitstring ---
    def get_encoded_text(self, text):
        # Create a list of the binary codes, then join them all at once!
        encoded_list = [self.codes[char] for char in text]
        return "".join(encoded_list)

    # --- Step 5: Padding ---
    def pad_encoded_text(self, encoded_text):
        extra_padding = 8 - len(encoded_text) % 8
        for i in range(extra_padding):
            encoded_text += "0"

        padded_info = "{0:08b}".format(extra_padding)
        encoded_text = padded_info + encoded_text
        return encoded_text

    # --- Step 6: Convert String of "0" and "1" into Real Binary ---
    def get_byte_array(self, padded_encoded_text):
        if len(padded_encoded_text) % 8 != 0:
            print("Padding error")
            exit(0)

        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i+8]
            b.append(int(byte, 2))
        return b

    # --- MAIN COMPRESSION EXECUTION ---
    def compress(self, input_path, output_path=None):
        if output_path is None:
            filename, file_extension = os.path.splitext(input_path)
            output_path = filename + "_naive.bin"

        with open(input_path, 'r', encoding='utf-8') as file:
            text = file.read()

        if not text:
            print(f"Skipping empty file: {input_path}")
            return None

        try:
            frequency = self.make_frequency_dict(text)
            self.run_tree_building(frequency)
    
            encoded_text = self.get_encoded_text(text)
            padded_encoded_text = self.pad_encoded_text(encoded_text)
            binary_data = self.get_byte_array(padded_encoded_text)
            
            header = json.dumps(frequency)
            header_bytes = bytearray(header + "\n", 'utf-8')
    
            with open(output_path, 'wb') as output:
                output.write(header_bytes)
                output.write(binary_data)
            
            print(f"Compressed (Naive) {input_path} -> {output_path}")
            return output_path
        except Exception as e:
            print(f"Error compressing (Naive) {input_path}: {e}")
            return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
        encoder = NaiveHuffmanEncoder()
        encoder.compress(path)
    else:
        print("Usage: python EncoderNaive.py <path_to_file>")
