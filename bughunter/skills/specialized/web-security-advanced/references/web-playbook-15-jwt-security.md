# JWTSecurity
English: JWT Security
- Entry Count: 4
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## JWT NoneAlgorithmic attack
- ID: jwt-none-attack
- Difficulty: beginner
- Subcategory: Algorithmic attack
- Tags: JWT, noneAlgorithm, Authentication bypass, Token forgery, CVE-2015-2951
- Original Extracted Source: original extracted web-security-wiki source/jwt-none-attack.md
Description:
UtilizeJWTLibrary Pair"none"Support defects in algorithms, leading toJWTModify the signature algorithm at the head tononeRemove the signature part later to construct a forged token that can pass validation without a key. This is the most classicJWTOne of the vulnerabilities.
Prerequisites:
- Target usageJWTfor authentication
- jwt_toolOrPython PyJWTLibrary
Execution Outline:
1. 1. Decode existingJWT
2. 2. Construct.NoneAlgorithmJWT
3. 3. jwt_toolAutomated attack
4. 4. Validate forged tokens
## JWTKey obscuring attacks(RS→HS)
- ID: jwt-key-confusion
- Difficulty: advanced
- Subcategory: Algorithmic attack
- Tags: JWT, Key obfuscation, RS256, HS256, Algorithm tampering
- Original Extracted Source: original extracted web-security-wiki source/jwt-key-confusion.md
Description:
When the server usesRSAPublic key verificationJWTWhen, the attacker will extract the algorithm fromRS256Change toHS256, at this point the server will mistakenly useRSAPublic Key asHMACValidate with the key. Due toRSAThe public key is public, attackers can use it to sign anyJWT.
Prerequisites:
- ObjectiveJWTUseRS256/RS384/RS512Algorithm
- Has been obtainedRSAPublic key
- jwt_toolOrPython
Execution Outline:
1. 1. ObtainRSAPublic key
2. 2. Key obscuring attacks
3. 3. jwt_toolAutomated attack
4. 4. JWKSEndpoint Injection
## JWTKey cracking
- ID: jwt-secret-bruteforce
- Difficulty: intermediate
- Subcategory: Key cracking
- Tags: JWT, Key cracking, HS256, Weak Key, hashcat
- Original Extracted Source: original extracted web-security-wiki source/jwt-secret-bruteforce.md
Description:
WhenJWTUseHMACSymmetric algorithm(HS256/HS384/HS512)When the key is a weak password, the signature key can be restored through dictionary or brute-force attacks, thereby forging anyJWTToken.
Prerequisites:
- ObjectiveJWTUseHMACAlgorithm(HS256Etc.)
- Successfully obtainedJWTSample
- hashcatOrjwt_tool
Execution Outline:
1. 1. Confirm algorithms and structures
2. 2. hashcat GPUAccelerate brute-force attack
3. 3. jwt_toolDictionary attack
4. 4. Using cracked keys to forgeJWT
## JWT JKU/X5UHeader injection
- ID: jwt-jku-x5u-injection
- Difficulty: advanced
- Subcategory: HeaderInjection
- Tags: JWT, JKU, X5U, HeaderInjection, JWKS, Key hijacking
- Original Extracted Source: original extracted web-security-wiki source/jwt-jku-x5u-injection.md
Description:
UtilizeJWT HeaderInjku(JWK Set URL)Orx5u(X.509 URL)Parameter, pointing the key source to a server controlled by the attacker, causing the server to use the attacker's public key for verificationJWT, thereby achieving token forgery.
Prerequisites:
- ObjectiveJWTSupportjku/x5u HeaderParameters
- The attacker has a public server
- PythonEnvironment
Execution Outline:
1. 1. DetectionJKU/X5USupport
2. 2. Generate Attacker Key Pair
3. 3. HostingJWKSAnd signJWT
4. 4. Verification attack

