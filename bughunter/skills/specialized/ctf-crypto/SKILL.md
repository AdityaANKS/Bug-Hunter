---
name: ctf-crypto
description: CTFCryptozoology attack knowledge base — RSAAttack (small index/common mode/Wiener/Coppersmith)、AESattack(Padding Oracle/ECBByte flip/GCM noncereuse)、ECCattack、LFSR/LCG/PRNGattack、classical cipher、LWEgrid attack
---

# CTF Cryptozoology attack knowledge base

against CTF Crypto Practical attack knowledge base for the topic, providing**Specific attack parameters、mathematical formula、Python code snippet**.

**and `crypto-toolkit` The difference**:
- `crypto-toolkit` → Codec operation tools (base64 decoding、MD5 Hash、AES Encryption and decryption)
- `ctf-crypto` → Cryptographical attack knowledge (RSA How to do a small exponential attack、Padding Oracle How to use it)

## core principles

1. **First identify the encryption system** — Look at the key length、encryption mode、Known quantity, determine the direction of attack
2. **Tool verification** — use `python_execute` To execute the attack code, use `crypto_decode` Do auxiliary encoding and decoding
3. **Parameter sensitive** — Cryptographic attacks are extremely sensitive to parameters and must be calculated accurately

## scene routing

| scene | Reference documentation | core attack |
|------|---------|---------|
| RSA attack | `rsa-attacks-cheatsheet.md` | Smalle/common mode/Wiener/Pollard/Fermat/Coppersmith |
| AES/block cipher attack | `aes-and-block-cipher-attacks.md` | ECBflip/Padding Oracle/GCM nonceReuse |
| ECC attack | `ecc-attacks-cheatsheet.md` | boy group/invalid curve/Smart/Pohlig-Hellman |
| PRNG/Stream cipher attack | `prng-and-stream-cipher-attacks.md` | MT19937/LCG/LFSR/RC4 |
| classical cipher | `classic-cipher-attacks.md` | Vigenere/XORfrequency analysis/OTPReuse |
| grid attack | `lattice-and-lwe-attacks.md` | LLL/BKZ/HNP/LWE embedding |

## Quick Question Guide

| Question characteristics | possible attack | Recommended reference |
|---------|---------|---------|
| gave n, e, c | RSA | rsa-attacks-cheatsheet.md |
| e=3 or e very small | RSA small exponential attack | rsa-attacks-cheatsheet.md |
| multiple groups (n, e, c) and n same | RSA common mode attack | rsa-attacks-cheatsheet.md |
| n big but e very big | Wiener attack | rsa-attacks-cheatsheet.md |
| AES-CBC + Decrypt oracle | Padding Oracle | aes-and-block-cipher-attacks.md |
| AES-ECB + Controlled plaintext | ECB Byte flip | aes-and-block-cipher-attacks.md |
| Elliptic curve parameters | ECC attack | ecc-attacks-cheatsheet.md |
| Given a sequence of random numbers | PRNG predict | prng-and-stream-cipher-attacks.md |
| Given the ciphertext and part of the plaintext | XOR/stream cipher | classic-cipher-attacks.md |
| matrix/Vector operations | grid attack | lattice-and-lwe-attacks.md |
