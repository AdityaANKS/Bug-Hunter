# PRNG Attacks with stream ciphers

## MT19937 ( Mersenne Twister ) attack

```python
# MT19937 state restored (given 624 output)
from ctypes import *

def untemper(y):
    y ^= y >> 18
    y ^= (y << 15) & 0xefc60000
    y ^= (y << 7) & 0x9d2c5680
    y ^= (y << 14) & 0x9d2c5680
    y ^= (y << 13) & 0x9d2c5680
    y ^= (y << 11) & 0x9d2c5680
    y ^= y >> 18
    return y

def recover_mt(outputs):
    """from 624 consecutive MT19937 Output restores internal state"""
    state = [untemper(y) for y in outputs[:624]]
    MT = c_ulong * 624
    mt = MT(*state)
    index = 624
    def twist():
        global index, mt
        for i in range(227):
            y = (mt[i] & 0x80000000) + (mt[(i+1)%624] & 0x7fffffff)
            mt[i] = mt[(i+397) % 624] ^ (y >> 1)
            if y & 1:
                mt[i] ^= 0x9908b0df
        index = 0
    return mt, twist, index
```

## LCG (linear congruential generator) attack

```python
"""
LCG: s_{n+1} = a * s_n + c (mod m)
When the parameters are known: direct recursion
When parameters are unknown: known 3 Group (s, s_next) Available a, c, m
"""

def lcg_attack(states):
    """from 3 continuous state recovery LCG parameter (a, c, m)"""
    s0, s1, s2 = states[0], states[1], states[2]
    # s1 = a*s0 + c (mod m)
    # s2 = a*s1 + c (mod m)
    # s2 - s1 = a*(s1 - s0) (mod m)
    # Extended Euclidean solution a, m
```

## LFSR (linear feedback shift register) attack

```python
"""
Berlekamp-Massey Algorithm: Recovery from output sequence LFSR feedback polynomial
"""

def berlekamp_massey(s):
    """Recover from binary sequence LFSR shortest feedback polynomial"""
    # Sage accomplish
    # F.<x> = GF(2)[]
    # s_seq = sequence(s)
    # return list(lfsr_sequence(f, [1]+[0]*15, len(s)))
```

## known plaintext attack (XOR stream cipher)

```python
"""
stream cipher: C = P XOR keystream
If you know part of the plaintext P, can be restored keystream = C XOR P
keystream Can be used to decrypt other ciphertexts
"""

def xor_attack(ciphertext, known_plaintext):
    """XOR Stream cipher known plaintext attack"""
    key = bytes(a ^ b for a, b in zip(ciphertext, known_plaintext))
    return key

def xor_decrypt(key, ciphertext):
    """Decrypt with recovered keystream"""
    return bytes(a ^ b for a, b in zip(key, ciphertext))
```

## RC4 attack

```python
"""
RC4 Known weaknesses:
1. RC4 Drop (before discarding N Bytes later, the keystream is nearly random)
2. Some key initializations are biased
"""

def rc4_drop(ciphertext, drop=3072):
    """RC4 Drop N Decrypt after bytes"""
```

## Python random module prediction

```python
import random

# If you can access Python random Status, can predict future random numbers
# known 624 * 4 = 2496 Byte status
state = random.getstate()
# Advance random numbers
random.setstate(state)
next_val = random.randint(0, 2**31)
```
