# Authentication vulnerabilities
English: Authentication Vulnerabilities
- Entry Count: 10
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Authentication bypass
- ID: auth-bypass
- Difficulty: intermediate
- Subcategory: Authentication bypass
- Tags: auth, bypass, authentication
- Original Extracted Source: original extracted web-security-wiki source/auth-bypass.md
Description:
WebApply authentication bypass techniques
Prerequisites:
- The target has an authentication mechanism
- Certification implementation has defects
Execution Outline:
1. SQLInjection bypass
2. Array bypass
3. Type conversion
4. JSONBypass
## Brute force cracking
- ID: auth-brute
- Difficulty: beginner
- Subcategory: Brute force cracking
- Tags: auth, brute-force, password
- Original Extracted Source: original extracted web-security-wiki source/auth-brute.md
Description:
Automated password guessing attack
Prerequisites:
- No captcha
- No locking strategy
Execution Outline:
1. Pitchfork
2. Cluster bomb
3. User enumeration based on response differences
4. Verification code/OTPBrute force and bypass
## Session hijacking
- ID: auth-session
- Difficulty: intermediate
- Subcategory: Session Management
- Tags: auth, session, hijack
- Original Extracted Source: original extracted web-security-wiki source/auth-session.md
Description:
Exploiting session management flaws to hijack or forge user sessions, gaining unauthorized access
Prerequisites:
- Targets using based on.CookieOrTokenSession management
- Can intercept or predict session identifiers
- Network communication not fully encrypted(HTTP)Or may existXSS
Execution Outline:
1. SessionCookieAttribute analysis
2. Session fixation attack(Session Fixation)
3. Session hijacking(HTTPSniffing)
4. Session prediction(Weak randomness)
## Password reset vulnerability
- ID: auth-password-reset
- Difficulty: intermediate
- Subcategory: Logical Vulnerability
- Tags: auth, password-reset, logic
- Original Extracted Source: original extracted web-security-wiki source/auth-password-reset.md
Description:
Bypassing the password reset process
Prerequisites:
- Password reset function has logical flaws
Execution Outline:
1. HostHeader poisoning
2. TokenBrute force
3. Password resetTokenPredictability analysis
4. Logic flaw in the password reset process
## OAuthVulnerability
- ID: auth-oauth
- Difficulty: advanced
- Subcategory: OAuth
- Tags: auth, oauth, redirect
- Original Extracted Source: original extracted web-security-wiki source/auth-oauth.md
Description:
OAuthAuthentication process vulnerability
Prerequisites:
- UseOAuthLogin
Execution Outline:
1. CSRFAttack
2. Redirect URI
3. OAuth StateMissing parameters/PredictableCSRF
4. TokenTheft andScopeOverstepping authority
## SAMLVulnerability
- ID: auth-saml
- Difficulty: advanced
- Subcategory: SAML
- Tags: auth, saml, xml
- Original Extracted Source: original extracted web-security-wiki source/auth-saml.md
Description:
SAMLAssertion attack
Prerequisites:
- UseSAML SSO
Execution Outline:
1. XMLSignature bypass
2. XXEAttack
3. SAML ResponseTampering and replay
4. SAMLSignature bypass advanced techniques
## 2FABypass
- ID: auth-2fa
- Difficulty: intermediate
- Subcategory: 2FA
- Tags: auth, 2fa, mfa
- Original Extracted Source: original extracted web-security-wiki source/auth-2fa.md
Description:
Bypassing two-factor authentication.
Prerequisites:
- Enable2FA
Execution Outline:
1. Direct access
2. CAPTCHA brute force
3. Logic bypass
## CAPTCHA bypass
- ID: auth-captcha
- Difficulty: beginner
- Subcategory: Verification code
- Tags: auth, captcha, bypass
- Original Extracted Source: original extracted web-security-wiki source/auth-captcha.md
Description:
Bypass graphic verification codes
Prerequisites:
- Captcha present
Execution Outline:
1. Reuse
2. Null bypass
3. Delete parameters
## Remember me vulnerability
- ID: auth-remember-me
- Difficulty: intermediate
- Subcategory: Session Management
- Tags: auth, remember-me, cookie
- Original Extracted Source: original extracted web-security-wiki source/auth-remember-me.md
Description:
Remember MeFunctional vulnerabilities
Prerequisites:
- EnableRemember Me
Execution Outline:
1. CookieForgery
2. Base64Decode
3. Remember PasswordTokenReverse analysis
4. Shiro RememberMeDeserializationRCE
## JWTAuthentication vulnerabilities
- ID: auth-jwt
- Difficulty: intermediate
- Subcategory: JWT
- Tags: auth, jwt, token
- Original Extracted Source: original extracted web-security-wiki source/auth-jwt.md
Description:
UtilizeJWT(JSON Web Token)Implementing defect fabrication or tampering with authentication tokens to achieve unauthorized access or privilege escalation
Prerequisites:
- Target usageJWTConduct authentication
- Can retrieve or interceptJWTToken
- JWTLibraries have known vulnerabilities or improper server configuration
Execution Outline:
1. JWTDecoding and analysis.
2. Algorithm NoneAttack
3. HS256Key cracking
4. RS256→HS256Algorithm obfuscation attack

