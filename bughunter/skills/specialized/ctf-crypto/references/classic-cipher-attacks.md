# Classical password attack

## Caesar cipher

```python
def caesar_break(ciphertext):
    """Traverse all displacements"""
    for shift in range(26):
        result = ""
        for c in ciphertext:
            if c.isalpha():
                base = ord('A') if c.isupper() else ord('a')
                result += chr((ord(c) - base + shift) % 26 + base)
            else:
                result += c
        print(f"Shift {shift}: {result}")
```

## Vigenère password

```python
def vigenere_break(ciphertext, max_keylen=20):
    """Kasiski + Frequency analysis crack Vigenère"""
    from collections import Counter

    # 1. Kasiski: Find repeating sequences and estimate key length
    def kasiski(text):
        distances = []
        for length in range(3, 6):
            seqs = {}
            for i in range(len(text) - length):
                seq = text[i:i+length]
                if seq in seqs:
                    distances.append(i - seqs[seq])
                seqs[seq] = i
        return distances

    # 2. Polymerization index (IC) Estimate key length
    def ic(text):
        freq = Counter(text.upper())
        n = len(text)
        return sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))

    # 3. Frequency analysis to solve single letters
    def solve_char(text, key_char):
        ENGLISH_FREQ = 'ETAOINSHRDLCUMWFGYPBVKJXQZ'
        key_base = ord(key_char.upper()) - ord('A')
        best_score = 0
        best_char = 'E'
        for shift in range(26):
            freq = Counter()
            for c in text:
                if c.isalpha():
                    shifted = chr((ord(c.upper()) - ord('A') - shift) % 26 + ord('A'))
                    freq[shifted] += 1
            score = sum(ENGLISH_FREQ.index(k) * freq[k] for k in freq if k in ENGLISH_FREQ)
            if score > best_score:
                best_score = score
                best_char = chr(ord('A') + shift)
        return best_char
```

## XOR multi-byte encryption

```python
def multi_byte_xor_break(ciphertext, max_keylen=16):
    """multibyte XOR Attack: Hamming distance + frequency analysis"""
    from collections import Counter

    def hamming_distance(b1, b2):
        return sum(bin(a ^ b).count('1') for a, b in zip(b1, b2))

    # Estimating key length using Hamming distance
    best_keylen = 1
    best_score = float('inf')
    for keylen in range(2, max_keylen + 1):
        chunks = [ciphertext[i:i+keylen] for i in range(0, len(ciphertext), keylen)]
        avg_dist = sum(hamming_distance(c1, c2) for c1, c2 in zip(chunks[:4], chunks[1:5])) / 4
        normalized = avg_dist / keylen
        if normalized < best_score:
            best_score = normalized
            best_keylen = keylen

    # Group by key length, each group is a single byte XOR
    key = b''
    for i in range(best_keylen):
        block = bytes(ciphertext[j] for j in range(i, len(ciphertext), best_keylen))
        # Frequency analysis to find the best single-byte key
        best = 0
        best_score = 0
        for k in range(256):
            decrypted = bytes(b ^ k for b in block)
            score = sum(1 for b in decrypted if chr(b).isalpha() or chr(b).isspace())
            if score > best_score:
                best_score = score
                best = k
        key += bytes([best])

    return key
```

## One-Time Pad (OTP) reuse attack

```python
"""
If the same OTP The key is used to encrypt two messages:
C1 = P1 XOR key
C2 = P2 XOR key
C1 XOR C2 = P1 XOR P2

Use language redundancy (English word frequency) to crack
"""
from collections import Counter

def otp_reuse_attack(c1, c2):
    """OTP Key reuse attack"""
    xor_result = bytes(a ^ b for a, b in zip(c1, c2))
    # Frequency analysis recovers plaintext
```

## fence code

```python
def railfence_break(ciphertext, max_rails=10):
    """Fence traversal number decryption"""
    for rails in range(2, max_rails + 1):
        # Rebuild the fence structure
        fence = [[] for _ in range(rails)]
        rail = 0
        direction = 1
        for c in ciphertext:
            fence[rail].append(c)
            rail += direction
            if rail == 0 or rail == rails - 1:
                direction = -direction
        # Read line by line
        result = ''.join(''.join(row) for row in fence)
        print(f"Rails {rails}: {result}")
```
