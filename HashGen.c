// wang_numeric_1_to_999_padded_8hex.c
#include <stdint.h>
#include <stdio.h>
#include <string.h>

/* Thomas Wang hash32shift2002 */
static inline uint32_t hash32shift2002(uint32_t x) {
    x += ~(x << 15);
    x ^=  (x >> 10);
    x +=  (x <<  3);
    x ^=  (x >>  6);
    x += ~(x << 11);
    x ^=  (x >> 16);
    return x;
}

/* Convert 0..15 nibble to uppercase hex char */
static inline char nibble_to_hex(uint8_t n) {
    n &= 0x0F;
    return (n < 10) ? (char)('0' + n) : (char)('A' + (n - 10));
}

/*
 * Encode numeric string (len 1..3) into hex chars:
 * - digits except last: d -> dd
 * - last digit: d -> (d+1)d
 *
 * Example: "11" -> "1121"
 *
 * Writes into out_hex (no null termination here), returns encoded hex length (2*len), or 0 on error.
 */
static int encode_numeric_to_hex(const char *in, char *out_hex, int out_cap) {
    int len = (int)strlen(in);
    if (len < 1 || len > 3) return 0;
    if (out_cap < 2 * len) return 0;

    for (int i = 0; i < len; i++) {
        char c = in[i];
        if (c < '0' || c > '9') return 0; // numeric only
        uint8_t d = (uint8_t)(c - '0');

        if (i < len - 1) {
            // duplicated nibble: dd
            out_hex[2*i + 0] = nibble_to_hex(d);
            out_hex[2*i + 1] = nibble_to_hex(d);
        } else {
            // last digit special: (d+1)d
            uint8_t hi = (uint8_t)((d + 1u) & 0x0F);
            out_hex[2*i + 0] = nibble_to_hex(hi);
            out_hex[2*i + 1] = nibble_to_hex(d);
        }
    }

    return 2 * len;
}

/*
 * Build the final 8-hex padded form:
 * - Take encoded hex (len 2,4,6)
 * - Right-pad with 'F' until length 6
 * - Append 'E''F' to reach 8
 *
 * Example: "1121" -> "1121FFEF"
 */
static int build_padded8_hex(const char *numeric_in, char out8[9]) {
    char enc[6]; // max encoded length = 6 hex chars (for 3 digits)
    int enc_len = encode_numeric_to_hex(numeric_in, enc, (int)sizeof(enc));
    if (enc_len == 0) return 0;

    // Copy encoded part
    int pos = 0;
    for (int i = 0; i < enc_len; i++) out8[pos++] = enc[i];

    // Pad with 'F' until we have 6 hex chars
    while (pos < 6) out8[pos++] = 'F';

    // Append "EF"
    out8[pos++] = 'E';
    out8[pos++] = 'F';

    out8[8] = '\0';
    return 1;
}

/* Convert one hex char to nibble 0..15 (expects 0-9A-F) */
static inline uint8_t hex_to_nibble(char c) {
    if (c >= '0' && c <= '9') return (uint8_t)(c - '0');
    if (c >= 'A' && c <= 'F') return (uint8_t)(10 + (c - 'A'));
    if (c >= 'a' && c <= 'f') return (uint8_t)(10 + (c - 'a'));
    return 0;
}

/* Convert 8 hex chars to uint32 as big-endian bytes: "1121FFEF" -> 0x1121FFEF */
static uint32_t hex8_to_u32_be(const char hex8[9]) {
    uint32_t x = 0;
    for (int i = 0; i < 8; i += 2) {
        uint8_t hi = hex_to_nibble(hex8[i]);
        uint8_t lo = hex_to_nibble(hex8[i+1]);
        uint8_t byte = (uint8_t)((hi << 4) | lo);
        x = (uint32_t)((x << 8) | byte);
    }
    return x;
}

static void print_u32_as_bytes_be(uint32_t x) {
    printf("%02X %02X %02X %02X",
           (unsigned)((x >> 24) & 0xFF),
           (unsigned)((x >> 16) & 0xFF),
           (unsigned)((x >>  8) & 0xFF),
           (unsigned)( x        & 0xFF));
}

int main(void) {
    printf("Inputs: 1,2,3,...,999 (numeric only)\n");
    printf("Format: encode digits -> right-pad with F to 6 hex -> append EF => 8 hex (e.g., 11 -> 1121FFEF)\n");
    printf("Then: input32 = 0x<8hex>, hash = hash32shift2002(input32)\n\n");

    printf("n    -> padded8   -> input32     -> hash32     (hash bytes)\n");
    printf("-----------------------------------------------------------\n");

    for (int n = 1; n <= 999; n++) {
        char s[4];
        snprintf(s, sizeof(s), "%d", n);

        char padded8[9];
        if (!build_padded8_hex(s, padded8)) {
            printf("ERROR building padded8 for %d\n", n);
            return 1;
        }

        uint32_t in32 = hex8_to_u32_be(padded8);
        uint32_t h = hash32shift2002(in32);

        printf("%-4d -> %s -> 0x%08X -> 0x%08X (", n, padded8, in32, h);
        print_u32_as_bytes_be(h);
        printf(")\n");
    }

    return 0;
}