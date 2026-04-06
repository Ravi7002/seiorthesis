# --- IMPORT SECTION ---
# These are built-in tools (libraries) I need for my script.
import os      # Used for handling file paths and file system tasks.
import json    # Used to convert text back into data (like dictionaries).
import heapq   # Used for rebuilding the Huffman Tree.

# --- DATA STRUCTURES ---
# This class is a blueprint for a "node" in the Huffman Tree.
class HeapNode:
    def __init__(self, char, freq):
        self.char = char   # The original character.
        self.freq = freq   # The weight (frequency) of the character.
        self.left = None   # Path for a '0' bit.
        self.right = None  # Path for a '1' bit.

# --- MAIN DECODER CLASS ---
class HuffmanDecoder:
    def __init__(self):
        # Initializing the workspace.
        self.heap = []             # Priority queue for building the tree.
        self.codes = {}            # Stores 'char': '0101'
        self.reverse_mapping = {}  # Stores '0101': 'char' (Crucial for decoding).

    # --- Step 1: Rebuild the Huffman Tree (Identical to Encoder logic) ---
    def make_heap_and_tree(self, frequency):
        self.heap = []
        tie_breaker = 0
        
        # 1. Create leaf nodes.
        for key in sorted(frequency.keys()):
            node = HeapNode(key, frequency[key])
            heapq.heappush(self.heap, (frequency[key], tie_breaker, node))
            tie_breaker += 1
            
        # 2. Merge nodes until there is a single tree.
        while len(self.heap) > 1:
            item1 = heapq.heappop(self.heap)
            item2 = heapq.heappop(self.heap)
            
            node1 = item1[2]
            node2 = item2[2]

            merged = HeapNode(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2
            
            heapq.heappush(self.heap, (merged.freq, tie_breaker, merged))
            tie_breaker += 1

    def make_codes_helper(self, root, current_code):
        # Recursive function to map out the bits for each character.
        if root is None:
            return

        if root.char is not None:
            self.codes[root.char] = current_code
            self.reverse_mapping[current_code] = root.char
            return

        self.make_codes_helper(root.left, current_code + "0")
        self.make_codes_helper(root.right, current_code + "1")

    def make_codes(self):
        if not self.heap:
            return
            
        # Get the root of the tree.
        root_item = heapq.heappop(self.heap)
        root = root_item[2]
        
        current_code = ""
        
        # Single character case.
        if root.char is not None: 
             self.codes[root.char] = "0"
             self.reverse_mapping["0"] = root.char
             return

        self.make_codes_helper(root, current_code)
    
    def run_tree_building(self, frequency):
         # Helper to reset state and build tree from frequency data.
         self.heap = []
         self.codes = {}
         self.reverse_mapping = {}
         
         self.make_heap_and_tree(frequency)
         self.make_codes()

    # --- Step 2: Handle Padding ---
    def remove_padding(self, padded_encoded_text):
        # The first 8 bits tell how many empty '0's were added at the very end.
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)

        # Remove those first 8 bits (info bits).
        padded_encoded_text = padded_encoded_text[8:] 
        
        # Remove the extra '0's from the very end.
        encoded_text = padded_encoded_text[:-1*extra_padding]
        return encoded_text

    # --- Step 3: Translate Bits back to Text ---
    def decode_text(self, encoded_text):
        current_code = ""
        decoded_text = ""
        
        # Read the bits one by one.
        for bit in encoded_text:
            current_code += bit
            # If the current string of bits matches a code in the map, I found a letter!
            if current_code in self.reverse_mapping:
                character = self.reverse_mapping[current_code]
                decoded_text += character
                current_code = "" # Reset and look for the next letter.
        
        return decoded_text

    # --- MAIN DECOMPRESSION EXECUTION ---
    def decompress(self, input_path, output_path=None):
        # Set default output name if none provided.
        if output_path is None:
            filename, file_extension = os.path.splitext(input_path)
            output_path = filename + "_decompressed.txt"

        try:
            with open(input_path, 'rb') as file:
                # 1. Read the Header (the frequency map)
                # It's saved as text on the first line.
                header_bytes = b""
                while True:
                    byte = file.read(1)
                    if byte == b'\n': # Stop when we hit the newline after the JSON.
                        break
                    if not byte: 
                        break
                    header_bytes += byte
                
                if not header_bytes:
                    print("Error: Empty or invalid file (no header found)")
                    return None

                # Convert the JSON text back into a Python dictionary.
                frequency = json.loads(header_bytes.decode('utf-8'))
                
                # 2. Rebuild the Huffman Tree from the frequency map.
                self.run_tree_building(frequency)

                # 3. Read Binary Data
                # Read ALL bytes at once (drastically reduces I/O wait time)
                bytes_data = file.read() 
                
                # Convert each byte to its 8-bit binary string inside a list
                # Note: Because we read in 'rb' mode (bytes), 'byte' is already an integer, 
                # so we don't need ord() anymore!
                bit_list = [bin(byte)[2:].rjust(8, '0') for byte in bytes_data]
                
                # Join the massive list into one string instantly
                bit_string = "".join(bit_list)

                # 4. Remove the helper padding and decode the bits to text.
                encoded_text = self.remove_padding(bit_string)
                decompressed_text = self.decode_text(encoded_text)
                
                # 5. Save the final decoded text.
                with open(output_path, 'w', encoding='utf-8') as output:
                    output.write(decompressed_text)
                
                print(f"Decompressed {input_path} -> {output_path}")
                return output_path
        except Exception as e:
            print(f"Error decompressing {input_path}: {e}")
            return None

# THIS BLOCK RUNS IF YOU EXECUTE THE SCRIPT DIRECTLY
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
        decoder = HuffmanDecoder()
        decoder.decompress(path)
    else:
        print("Usage: python Decoder.py <path_to_bin_file>")

