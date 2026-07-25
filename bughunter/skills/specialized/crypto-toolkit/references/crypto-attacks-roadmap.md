# Cryptographic attack classification routing

Based on the known information given in the question, quickly determine which attack method should be used.

## decision tree

```
Known conditions
├── know plaintext + cipher text?
│   ├── Encrypt the same key multiple times? → XOR/stream cryptanalysis
│   └── One time encryption? → Analyze encryption patterns
├── Know the ciphertext + key?
│   ├── Symmetric encryption → Decrypt directly
│   └── asymmetric encryption → RSA/ECC attack
├── known n, e, c (RSA)?
│   ├── e very small → small exponential attack
│   ├── Multiple groups in total n → common mode attack
│   ├── d very small → Wiener attack
│   ├── p-1 smooth → Pollard p-1
│   └── Try breaking it down online (factordb)
├── Elliptic curve parameters?
│   ├── order smooth → Pohlig-Hellman
│   ├── abnormal curve → Smart attack
│   └── ECDSA nonce Reuse → Private key recovery
├── known PRNG output sequence?
│   ├── MT19937 → status recovery
│   ├── LCG → Parameter recovery
│   └── LFSR → Berlekamp-Massey
└── classical cipher?
    ├── caesar/ROT13 → Violence
    ├── Vigenere → Kasiski + frequency
    └── One-Time Pad Reuse → statistical attack
```

## RSA Attack quick selection

| known | attack |
|------|------|
| n, e, c, e=3 | Small exponent root |
| multiple groups (n, c), e same, The plain text is the same | Håstad broadcast |
| multiple groups (n, c), n same, e different | common mode attack |
| n, e, d Very small approximation | Wiener attack |
| n decomposable, p≈q | Fermat break down |
| n decomposable, p-1 smooth | Pollard p-1 |
| known partial plaintext | Coppersmith |
| factordb Can be checked | Decompose online |

## AES/Block Cipher Attack Quick Selection

| scene | attack |
|------|------|
| ECB model | pattern analysis + Block rearrangement |
| CBC model, Controllable IV | IV flip attack |
| CBC model, Padding Oracle | Padding Oracle attack |
| CTR/GCM, nonce Reuse | Keystream recovery |
| known partial plaintext | XOR Restoring keystream |

## PRNG Attack quick selection

| scene | attack |
|------|------|
| Python random(), 624 outputs | MT19937 status recovery |
| continuous 3 indivual LCG output | Parameter recovery |
| LFSR output sequence | Berlekamp-Massey |
| RC4 (before discarding 3072 Bytes after) | RC4 Drop attack |

## Quick selection of classical passwords

| Cipher text characteristics | attack |
|---------|------|
| Single character replacement | frequency analysis |
| Multi-character displacement | caesar violence |
| Multiple table replacement | Vigenere Kasiski |
| binary XOR multibyte | frequency analysis + Key length estimation |
| One-time pad reuse | XOR contrast attack |
