import sys

sbox = [0xE, 0x4, 0xD, 0x1, 0x2, 0xF, 0xB, 0x8,
        0x3, 0xA, 0x6, 0xC, 0x5, 0x9, 0x0, 0x7]

SIZE_SBOX = len(sbox)

def parity(x):
    return bin(x).count("1") % 2

def linearApprox(input_mask, output_mask):
    matches = 0

    for x in range(SIZE_SBOX):
        in_parity = parity(x & input_mask)
        out_parity = parity(sbox[x] & output_mask)

        if in_parity == out_parity:
            matches += 1

    return matches - (SIZE_SBOX // 2)  # (#matches − 8)

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

if __name__ == "__main__":
    main()