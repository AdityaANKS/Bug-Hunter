# AES and block cipher attacks

## Encryption mode quick check

| model | Features | Exploitable vulnerabilities |
|------|------|-----------|
| ECB | Same plaintext→Same ciphertext | pattern recognition、rearrange attack |
| CBC | The previous block of ciphertext participates in the current encryption | IV flip、Padding Oracle |
| CTR | Streaming encryption | nonce Reuse → XOR Give way |
| CFB | Similar to stream cipher | IV flip |
| OFB | Similar to stream cipher | nonce Reuse |
| GCM | Authenticated encryption | nonce Reuse → Keystream recovery |

## ECB Byte flip

```python
from Crypto.Cipher import AES

# ECB Mode, the same plaintext block produces the same ciphertext block
# Attack: Identify duplicate ciphertext blocks → Infer plaintext structure
# Rearrangeable ciphertext blocks change plaintext structure

def ecb_detect(ciphertext, block_size=16):
    """Detection ECB Pattern (find duplicate blocks)"""
    blocks = [ciphertext[i:i+block_size] for i in range(0, len(ciphertext), block_size)]
    return len(blocks) != len(set(blocks))
```

## CBC IV flip attack

```python
"""
Principle: in CBC middle,P[i] = Decrypt(C[i]) XOR C[i-1]
Revise C[i-1] a certain byte of → correspond P[i] The byte of

Purpose: modify IV The first piece of plain text can be changed, modify C[i-1] Can change the i block plaintext
cost:C[i-1] corresponding plaintext P[i-1] will be destroyed
"""

def cbc_iv_flip(ciphertext, known_plain, target_plain, block_size=16):
    """flip CBC The first piece of plaintext (modified IV)"""
    iv = bytearray(ciphertext[:block_size])
    for i in range(block_size):
        iv[i] = iv[i] ^ known_plain[i] ^ target_plain[i]
    return bytes(iv) + ciphertext[block_size:]
```

## Padding Oracle attack

```python
"""
principle:CBC When decrypting if Padding Illegal, the server returns a different error
Exploiting errors by byte-by-byte blasting/Correct differential recovery plaintext

condition:
1. use CBC model
2. server pair Padding Error and ciphertext errors return different responses
3. Modified ciphertext can be submitted repeatedly
"""

def padding_oracle_attack(oracle, ciphertext, block_size=16):
    """Padding Oracle Attack recovery plaintext
    
    oracle: Function, accept ciphertext and return True(paddingcorrect)/False(paddingmistake)
    """
    blocks = [ciphertext[i:i+block_size] for i in range(0, len(ciphertext), block_size)]
    plaintext = b''
    
    for block_idx in range(1, len(blocks)):
        prev_block = bytearray(blocks[block_idx - 1])
        curr_block = blocks[block_idx]
        intermediate = bytearray(block_size)
        
        for byte_pos in range(block_size - 1, -1, -1):
            padding_val = block_size - byte_pos
            
            # Construct test ciphertext
            test_block = bytearray(block_size)
            for k in range(byte_pos + 1, block_size):
                test_block[k] = intermediate[k] ^ padding_val
            
            found = False
            for guess in range(256):
                test_block[byte_pos] = guess
                test_cipher = bytes(test_block) + curr_block
                
                if oracle(test_cipher):
                    intermediate[byte_pos] = guess ^ padding_val
                    found = True
                    break
            
            if not found:
                raise Exception(f"Padding oracle attack failed at byte {byte_pos}")
        
        # Restore plaintext
        for i in range(block_size):
            plaintext += bytes([intermediate[i] ^ prev_block[i]])
    
    return plaintext
```

## GCM Nonce reuse attack

```python
"""
when the same nonce When used for double encryption:
- Both encryptions use the same key stream
- C1 = P1 XOR keystream
- C2 = P2 XOR keystream
- C1 XOR C2 = P1 XOR P2

If you know P1, can be restored P2
"""

def gcm_nonce_reuse(c1, c2, p1):
    """use GCM nonce Reuse recovery plaintext"""
    return bytes(a ^ b ^ c for a, b, c in zip(c1, c2, p1))
```

## CTR Nonce Reuse

```python
"""
CTR mode nonce Reuse is equivalent to stream cipher key reuse
C1 = P1 XOR keystream
C2 = P2 XOR keystream
C1 XOR C2 = P1 XOR P2
"""

def ctr_nonce_reuse(c1, c2, known_p1):
    """use CTR nonce Reuse recovery plaintext"""
    return bytes(a ^ b ^ c for a, b, c in zip(c1, c2, known_p1))
```
