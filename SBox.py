import random
import sys

sbox = [0xE, 0x4, 0xD, 0x1, 0x2, 0xF, 0xB, 0x8,
        0x3, 0xA, 0x6, 0xC, 0x5, 0x9, 0x0, 0x7]


SIZE_SBOX = len(sbox)

sbits = [format(sbox[i], "04b") for i in range(SIZE_SBOX)]
key = 0b1010

def parity(x):
    return bin(x).count("1") % 2

def linearApprox(input_mask, output_mask):
    matches = 0

    for x in range(SIZE_SBOX):
        in_parity = parity(x & input_mask)
        out_parity = parity(sbox[x] & output_mask)

        if in_parity == out_parity:
            matches += 1

    return matches - (SIZE_SBOX // 2)

def encrypt(x, key, sbits):
    return sbits[x ^ key]

def generatePairs(num_pairs, key, sbits, bit_size=4):
    pairs = []
    for _ in range(num_pairs):
        x = random.randint(0, 2**bit_size - 1)
        y = encrypt(x, key, sbits)
        pairs.append((x, y))
    return pairs

def main():
    sys.stdout.write("    | ")
    for i in range(SIZE_SBOX):
        sys.stdout.write(f"{i:>3x} ")
    print()

    print("-" * (SIZE_SBOX * 4 + 4))
    for row in range(SIZE_SBOX):
        sys.stdout.write(f"{row:>3x} | ")
        for col in range(SIZE_SBOX):
            val = linearApprox(row, col)
            sys.stdout.write(f"{val:>3} ")
        print()
    
    pairs = generatePairs(10, key, sbits)
    print("\nGenerated pairs (x, y):")
    for x, y in pairs:
        print(f"({x:04b}, {y})")

if __name__ == "__main__":
    main()