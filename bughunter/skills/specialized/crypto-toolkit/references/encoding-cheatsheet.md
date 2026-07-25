# Code Identification Cheat Sheet

## Quick identification process

```
input string
  ├─ Include %XX → URL coding → url_decode
  ├─ Include &# or &#x → HTML entity → html_decode
  ├─ Include \uXXXX → Unicode escape → unicode_decode
  ├─ Include .- And only dots and spaces → Morse → morse_decode
  ├─ three sections base64 use . connect → JWT → jwt_decode
  ├─ There is at the end = filling + A-Za-z0-9+/ → Base64 → base64_decode
  ├─ There is at the end = filling + A-Z2-7 → Base32 → base32_decode
  ├─ pure hex character(0-9a-f) even length → Hex → hex_decode
  ├─ plain uppercase letters + Number, no padding → possible Base58 → base58_decode
  ├─ Letter displacement characteristics(like E→M, A→I) → Caesar → caesar_decode
  └─ Unable to determine → auto_decode
```

## Base64 Variants

| Variants | character set | use |
|------|--------|------|
| standard Base64 | `A-Za-z0-9+/=` | Universal |
| URL-safe Base64 | `A-Za-z0-9-_` | URL parameter |
| Base64url (JWT) | `A-Za-z0-9_-` No padding | JWT |

## Base58

| Variants | exclude characters | use |
|------|---------|------|
| Bitcoin | `0OIl` | Address coding |
| Flickr | `0OIl` | shortURL |
| Ripple | `0OIl` | Address coding |

## Common confusion patterns

### double encoding
```
original: admin
→ URLcoding: %61%64%6D%69%6E
→ doubleURLcoding: %2561%2564%256D%2569%256E
```

### Base64 + Hex chain
```
original: NsScTf.php
→ Hex: 4e73536354662e706870
→ Base64: TnNTY1RmLnBocA==
```

### ROT13 Nested
```
original: password
→ ROT13: cnffjbeq
→ ROT13 again: password (ROT13 Self-reversal)
```

## Length and encoding comparison

| Original length | Base64 length | Hex length | Base32 length |
|---------|------------|---------|------------|
| 1 byte | 4 chars | 2 chars | 8 chars |
| 4 bytes | 8 chars | 8 chars | 8 chars |
| 8 bytes | 12 chars | 16 chars | 16 chars |
| 16 bytes | 24 chars | 32 chars | 28 chars |

## CTF Common coding chains

1. **Base64 → plain text** — most common
2. **Base64 → Hex → plain text** — double encoding
3. **Base64 → Base64 → plain text** — Nested Base64
4. **Hex → Base64 → ROT13 → plain text** — three-layer coding
5. **URLcoding → Base64 → plain text** — Web Common scenarios
6. **Morse → Base64 → Hex → plain text** — Crypto topic

## Verify after decoding

After decoding, check whether the result is:
- [ ] readable ASCII/UTF-8 text
- [ ] looks like path(/xxx/yyy.php)
- [ ] look like URL(http://...)
- [ ] Include flag Format(flag{...}, NSSCTF{...})
- [ ] Still encoding (need to continue decoding)
