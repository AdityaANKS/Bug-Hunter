# cryptographic attack techniques

## 1. Hash attack

### Rainbow table query
- crackstation.net — Free, support MD5/SHA1/SHA256
- cmd5.com — Chinese, wide coverage
- hashes.org — community maintenance

### Hash length extension attack
- Applicable:MD5, SHA1, SHA256 etc. based on Merkle-Damgård hash
- Condition: know `H(message)` and `len(message)`,have no idea message itself
- tool:hashpump, hash_extender
- Scenario:API Signature verification bypass

### Hash collision
- MD5:fastcoll, HashClash
- SHA1:SHAttered (Theoretically feasible)
- Scenario: File Integrity Bypass、certificate forgery

## 2. Symmetric encryption attack

### ECB pattern attack
- identical plaintext blocks → Same ciphertext block
- Plaintext can be rearranged by rearranging ciphertext blocks
- Recognize repeating patterns (such as user role fields)

### CBC Byte flipping attack
- Revise IV Or the previous block of ciphertext can flip the corresponding bytes of the next block of plaintext.
- official:`P[i] = D(C[i]) XOR C[i-1]`
- Revise `C[i-1][j]` → `P[i][j]` flip
- Scenario: Modify encrypted userID、role field

### Padding Oracle attack
- Condition: Server returns padding Is it correct?
- Recover plaintext byte by byte, no key required
- tool:padbuster, padding-oracle-attacker
- Scenario:ASP.NET、Java serialization token

### IV reuse attack
- CBC Same in mode IV + same Key → information leakage
- It can be inferred whether the plaintext is the same

## 3. RSA attack

### small public key exponential attack
- e=3 , if the clear text m^3 < n, directly open the cube root and recover
- Low encryption index broadcast attack: the same plaintext uses the same e different n encryption

### common mode attack
- The same plaintext uses the same n different e encryption
- Recovering plaintext by extended Euclidean algorithm

### Wiener attack
- d < n^0.25 can be decomposed n
- Suitable for small private key index scenarios

### Fermat break down
- p and q Can be quickly decomposed when close n
- Suitable for weak key generation

### known key file
- from .pem/.der Extract parameters from file
- openssl rsa -text -noout -in key.pem

## 4. Classical password attack

### Caesar Violence
- only 25 possibility, traverse directly
- Use word frequency analysis to select the most likely result

### Vigenere analyze
- Kasiski Test to determine key length
- Coincident index method to verify key length
- After determining the length, do it for each column Caesar crack

### fence code
- Common column numbers:2-8
- Iterate over all possible number of columns
- Check if the results make sense

### bacon code
- two fonts/style → A/B coding
- Every5characters to decode one letter

## 5. JWT attack

### none Algorithm bypass
```json
{"alg": "none", "typ": "JWT"}
```
- Change the algorithm to none
- Remove signature part
- Some implementations will accept unsigned token

### RS256 → HS256 algorithm obfuscation
- Change the algorithm from RS256 Change to HS256
- Use public key as HMAC key signature
- If the server uses public key verification HS256 sign → bypass

### Weak key blasting
- jwt-tool, jwt-cracker
- Common weak keys:secret, password, 123456 wait

### JWK / jku injection
- exist Header Embed the public key in (jwk field)
- or point to an attacker-controlled jku URL
- If the server trusts Header key in → forgery

## 6. Coding chain attack mode

### WAF Bypass encoding
- double URL coding:`%2527` → `%27` → `'`
- Unicode standardization:`％27` → `'`(Full-width to half-width)
- HTML entity:`&#39;` → `'`
- Base64 Encoding injection parameters

### Encoding in deserialization
- PHP: base64 encoded serialized object
- Java: Base64 encoded serialized byte stream
- Python: base64 pickle payloads

## 7. Tool quick review

| scene | tool |
|------|------|
| Universal codec | CyberChef |
| Hash cracking | hashcat, john |
| RSA analyze | RsaCtfTool |
| JWT analyze | jwt-tool |
| Padding Oracle | padbuster |
| Hash expansion | hashpump |
| Online decoding | base64decode.org, cyberchef.org |
