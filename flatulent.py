import array
import struct
import hashlib
import heapq
import collections

class Node:
    def __init__(self, symbol=None, frequency=0, left=None, right=None):
        self.symbol = symbol
        self.frequency = frequency
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.frequency < other.frequency

class FartCompressor:
    def __init__(self):
        self.dictionary = {}
        self.next_code = 256
        self.bit_length = 9
        self.bit_buffer = 0
        self.bit_count = 0
        self.bit_index = 0
        self.compressed_data = array.array('B')
        self.checksum = None

    def write_bits(self, value, length):
        self.bit_buffer |= value << (32 - self.bit_count - self.bit_index)
        self.bit_count += length
        self.bit_index += length

        while self.bit_index >= 8:
            byte = (self.bit_buffer >> 24) & 0xFF
            self.compressed_data.append(byte)
            self.bit_buffer <<= 8
            self.bit_index -= 8

    def compress(self, data):
        self.compressed_data = array.array('B')

        # Compressão LZW
        current_sequence = bytes([data[0]])
        for symbol in data[1:]:
            extended_sequence = current_sequence + bytes([symbol])
            if extended_sequence in self.dictionary:
                current_sequence = extended_sequence
            else:
                self.write_bits(self.dictionary[current_sequence], self.bit_length)
                if self.next_code < (1 << self.bit_length):
                    self.dictionary[extended_sequence] = self.next_code
                    self.next_code += 1
                current_sequence = bytes([symbol])

        self.write_bits(self.dictionary[current_sequence], self.bit_length)
        self.write_bits(0x1FF, self.bit_length)  # Marcação final

        if self.bit_index > 0:
            byte = (self.bit_buffer >> 24) & 0xFF
            self.compressed_data.append(byte)

        # Codificação de Huffman
        encoded_data = self.huffman_encode(data)
        self.compressed_data.extend(encoded_data)

        self.calculate_checksum(data)
        return self.compressed_data.tobytes()

    def calculate_checksum(self, data):
        md5 = hashlib.md5()
        md5.update(data)
        self.checksum = md5.digest()

    def huffman_encode(self, data):
        frequency_table = collections.Counter(data)
        heap = [Node(symbol, frequency) for symbol, frequency in frequency_table.items()]
        heapq.heapify(heap)

        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = Node(frequency=left.frequency + right.frequency, left=left, right=right)
            heapq.heappush(heap, merged)

        encoding_table = {}
        self.build_encoding_table(heap[0], '', encoding_table)

        encoded_data = ''
        for symbol in data:
            encoded_data += encoding_table[symbol]

        num_bits = len(encoded_data)
        encoded_bytes = array.array('B', [int(encoded_data[i:i+8], 2) for i in range(0, num_bits, 8)])

        return encoded_bytes

    def build_encoding_table(self, node, code, encoding_table):
        if node.symbol is not None:
            encoding_table[node.symbol] = code
        else:
            self.build_encoding_table(node.left, code + '0', encoding_table)
            self.build_encoding_table(node.right, code + '1', encoding_table)

class FartDecompressor:
    def __init__(self):
        self.dictionary = {}
        self.next_code = 256
        self.bit_length = 9
        self.bit_buffer = 0
        self.bit_count = 0
        self.bit_index = 0
        self.checksum = None

    def decompress(self, compressed_data):
        self.dictionary = {}
        self.next_code = 256
        self.bit_length = 9
        self.bit_buffer = 0
        self.bit_count = 0
        self.bit_index = 0

        index = 0
        self.bit_buffer |= compressed_data[index] << (24 - self.bit_count)
        self.bit_count += 8
        self.bit_index += 8
        index += 1

        if (self.bit_buffer >> (32 - 5)) != 0x1F:
            raise ValueError("Formato de compressão inválido")

        decompressed_data = bytearray()
        previous_code = self.bit_buffer & ((1 << self.bit_length) - 1)
        decompressed_data.extend(self.dictionary[previous_code])

        while True:
            self.bit_count -= self.bit_length
            self.bit_index -= self.bit_length

            if self.bit_count <= 0:
                if index >= len(compressed_data):
                    break
                self.bit_buffer |= compressed_data[index] << (24 - self.bit_count)
                self.bit_count += 8
                self.bit_index += 8
                index += 1

            current_code = (self.bit_buffer >> (32 - self.bit_count)) & ((1 << self.bit_length) - 1)
            self.bit_buffer <<= self.bit_length

            if current_code == 0x1FF:
                break

            if current_code in self.dictionary:
                sequence = self.dictionary[current_code]
            elif current_code == self.next_code:
                sequence = self.dictionary[previous_code] + bytes([self.dictionary[previous_code][0]])
            else:
                raise ValueError("Formato de compressão inválido")

            decompressed_data.extend(sequence)
            self.dictionary[self.next_code] = self.dictionary[previous_code] + bytes([sequence[0]])
            self.next_code += 1

            if self.next_code >= (1 << self.bit_length) and self.bit_length < 12:
                self.bit_length += 1

            previous_code = current_code

        # Decodificação de Huffman
        huffman_data = compressed_data[index:]
        decoded_data = self.huffman_decode(huffman_data)
        decompressed_data.extend(decoded_data)

        return decompressed_data

    def huffman_decode(self, huffman_data):
        decoding_table = self.build_decoding_table()

        encoded_bits = ''.join(format(byte, '08b') for byte in huffman_data)
        decoded_data = bytearray()

        code = ''
        for bit in encoded_bits:
            code += bit
            if code in decoding_table:
                symbol = decoding_table[code]
                decoded_data.append(symbol)
                code = ''

        return decoded_data

    def build_decoding_table(self):
        decoding_table = {}

        for code, symbol in self.dictionary.items():
            decoding_table[symbol] = code

        return decoding_table
