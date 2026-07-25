---
name: crypto-toolkit
description: Encoding, decoding and encryption and decryption tools — base64/URL/Hex/HTMLEntity encoding and decoding,MD5/SHAhash,AES/DES/RSAEncryption and decryption,JWTanalysis,Caesar/ROT13password, fence/Vigenerepassword,Unicodeescape,MorseTelegram, etc.
---

# Encoding, decoding and encryption Skill

For common coding in penetration testing、encryption、Confuse scenarios and provide comprehensive encoding, decoding, encryption and decryption capabilities.
**important**: Any encoding encountered/When encrypting strings, use `crypto_decode` Tools to decode instead of guessing.

## core principles

1. **Tools first** — meet base64、hex、URLEncoding and other strings, call `crypto_decode` Tool decoding, don’t make up your own mind
2. **Try multiple formats** — If the result of one decoding method is unreasonable, try other encoding formats
3. **chain decoding** — CTF Common multi-layer encodings (such as base64→hex→ROT13), check whether the result needs to be decoded again after decoding
4. **Verification results** — Verify the rationality of the result after decoding (whether it is readable text、Is it like path/URL/flag wait)

## 1. Code recognition and decoding

### Common coding feature identification

| encoding type | feature | Example |
|---------|------|------|
| Base64 | `A-Za-z0-9+/=` The ending is often `=` filling | `TnNTY1RmLnBocA==` |
| Base32 | `A-Z2-7=` | `OBZHK5DFN2A====` |
| Hex | `0-9a-f` even length | `4e73536354662e706870` |
| URLcoding | `%XX` Format | `%2F%61%64%6D%69%6E` |
| HTMLentity | `&#xNN;` or `&#NNN;` | `&#x3C;script&#x3E;` |
| Unicodeescape | `\uXXXX` or `\UXXXXXXXX` | `\u003c\u0073\u0063` |
| JWT | three sections `.` separated base64 | `eyJhbG...` |

### decoding strategy

1. Identify encoding type → call `crypto_decode` Tool specifies corresponding operations
2. Check whether the decoded result is readable/Reasonable
3. If it is unreasonable, try other encoding formats
4. If the result still looks like encoding, repeat the steps 1-3

## 2. Hash vs. Hash

### Common hash types

| type | Output length | feature |
|------|---------|------|
| MD5 | 32 hex | `e10adc3949ba59abbe56e057f20f883e` |
| SHA1 | 40 hex | `aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d` |
| SHA256 | 64 hex | `2c26b46b68ffc68ff99b453c1d30413413422d7064...` |
| SHA512 | 128 hex | longerhexstring |
| NTLM | 32 hex | Windows hash |
| MySQL5 | 41character | `*E6CC90B878B948C35E92B003C792C46758BF4` |

### Hash processing strategy

- Identify the hash type (by length and charset)
- Try an online rainbow table query (via fetch Tool access crackstation wait)
- For hashes with a known salt value, try brute force cracking with the salt value

## 3. Symmetric encryption

### AES/DES/3DES

- Requires key and schema (ECB/CBC/CTR wait)
- CBC pattern requires IV
- Common fills:PKCS7/ZeroPadding
- Hard-coded keys are often encountered during penetration, and should be extracted from the source code first.

## 4. asymmetric encryption

### RSA

- from public key/Extract parameters from private key file
- Modulus is too small RSA decomposable
- Known private key can be decrypted directly

## 5. classical cipher

| type | feature | Crack method |
|------|------|---------|
| Caesar/ROT13 | letter displacement | Violence25kind of displacement |
| Vigenere | Multiple table replacement | Kasiski/frequency analysis |
| fence code | Character grouping and reorganization | Try common column numbers |
| bacon code | AB quintuple | Look up table |
| Morse | `.-` Dots and dashes | Look up table |

## 6. JWT deal with

- decoding Header + Payload(base64url)
- Check algorithm:`none` Algorithm bypass、RS256→HS256 algorithm obfuscation
- Attempt weak key signature forgery
- examine exp/nbf Waiting time statement

## Tool usage

### `crypto_decode` tool

When you need to encode/decoding/encryption/When performing a decryption operation, call this tool:

```
crypto_decode(operation="base64_decode", input="TnNTY1RmLnBocA==")
```

List of supported operations:
- **coding**: `base64_encode`, `base32_encode`, `hex_encode`, `url_encode`, `html_encode`, `unicode_encode`, `rot13_encode`, `morse_encode`, `caesar_encode`, `base58_encode`
- **decoding**: `base64_decode`, `base32_decode`, `hex_decode`, `url_decode`, `html_decode`, `unicode_decode`, `rot13_decode`, `morse_decode`, `caesar_decode`, `base58_decode`
- **Hash**: `md5_hash`, `sha1_hash`, `sha256_hash`, `sha512_hash`
- **encryption/Decrypt**: `aes_encrypt`, `aes_decrypt`, `des_encrypt`, `des_decrypt`, `rsa_encrypt`, `rsa_decrypt`
- **JWT**: `jwt_decode`, `jwt_encode`
- **automatic recognition**: `auto_decode` (Automatically identify encoding type and decode)

## CTF Cryptographical attack routing

> Use it first when encountering cryptographic attack scenarios (known encryption algorithms and need to recover plaintext or keys) `ctf-crypto` Skill:

| attack scenario | route to ctf-crypto | Reference documentation |
|---------|-----------------|---------|
| RSA small exponent/common mode/Wiener | `ctf-crypto` | `references/rsa-attacks-cheatsheet.md` |
| AES Padding Oracle/ECB flip | `ctf-crypto` | `references/aes-and-block-cipher-attacks.md` |
| ECC boy group/discrete logarithm | `ctf-crypto` | `references/ecc-attacks-cheatsheet.md` |
| PRNG/MT19937 predict | `ctf-crypto` | `references/prng-and-stream-cipher-attacks.md` |
| Classical cipher (Vigenere/XOR) | `ctf-crypto` | `references/classic-cipher-attacks.md` |
| grid attack/LWE | `ctf-crypto` | `references/lattice-and-lwe-attacks.md` |

**book Skill Focus on codec operation tools**, please refer to the specific attack methods and parameters of cryptography. `ctf-crypto`.

## Reference documentation

- `references/encoding-cheatsheet.md` — Code Identification Cheat Sheet
- `references/crypto-attacks.md` — cryptographic attack techniques
- `references/crypto-attacks-roadmap.md` — Cryptographic attack classification routing (select attack methods based on topic characteristics)

