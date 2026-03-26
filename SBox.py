import random
import sys

sbox = [0xE, 0x4, 0xD, 0x1, 0x2, 0xF, 0xB, 0x8,
        0x3, 0xA, 0x6, 0xC, 0x5, 0x9, 0x0, 0x7]

SIZE_SBOX = len(sbox)

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

def encrypt(x, key):
    return sbox[x ^ key]

def generatePairs(num_pairs, key, bit_size=4):
    pairs = []
    for _ in range(num_pairs):
        x = random.randint(0, 2**bit_size - 1)
        y = encrypt(x, key)
        pairs.append((x, y))
    return pairs

def recover_key_bit(pairs, input_mask, output_mask):
    votes = [0, 0] 

    for x, y in pairs:
        lhs = parity(x & input_mask)
        rhs = parity(y & output_mask)
        guessed_parity = lhs ^ rhs
        votes[guessed_parity] += 1

    recovered = 0 if votes[0] > votes[1] else 1
    return votes, recovered


def key_recovery(pairs, input_mask, output_mask, bias):
    print("\nKey recovery using linear approximation")

    votes, recovered = recover_key_bit(pairs, input_mask, output_mask)

    if bias < 0:
        votes = [votes[1], votes[0]]
        recovered = 0 if votes[0] > votes[1] else 1

    print(f"Recovered parity(K & {input_mask:04b}) = {recovered}")
    return recovered

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
    
    pairs = generatePairs(5000, key)
    print("\nGenerated pairs (x, y):")
    for x, y in pairs[:10]: 
        print(f"({x:04b}, {y:04b})")

    input_mask = 0b0110
    output_mask = 0b0101
    bias = 4

    recovered = key_recovery(pairs, input_mask, output_mask, bias)
    print(f"\nActual parity(K & {input_mask:04b}) = {parity(key & input_mask)}")

if __name__ == "__main__":
    main()