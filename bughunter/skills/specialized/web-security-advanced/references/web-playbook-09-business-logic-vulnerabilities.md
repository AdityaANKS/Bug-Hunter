# Business logic vulnerabilities
English: Business Logic Vulnerabilities
- Entry Count: 5
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## IDORPrivilege escalation
- ID: biz-idor
- Difficulty: beginner
- Subcategory: Privilege escalation vulnerability
- Tags: IDOR, Overstepping authority, Business logic, OWASP, A01
- Original Extracted Source: original extracted web-security-wiki source/biz-idor.md
Description:
Insecure Direct Object Reference(IDOR), by tampering with the object in request parametersIDUnauthorized access to others' data. An attacker can traverse userID、Parameter acquisition such as order numbers to access unauthorized resources.
Prerequisites:
- Target exists based onIDResource access interface of
- Logged in as a regular user account
Execution Outline:
1. 1. Identify Traversable Parameters
2. 2. Horizontal privilege escalation testing
3. 3. Vertical privilege escalation testing
4. 4. Parameter pollution and privilege escalation
## Race condition attack
- ID: biz-race-condition
- Difficulty: intermediate
- Subcategory: Race condition
- Tags: Race condition, Race Condition, TOCTOU, Concurrency, Business logic
- Original Extracted Source: original extracted web-security-wiki source/biz-race-condition.md
Description:
Exploit server-sideTOCTOU(Time-of-Check to Time-of-Use)Vulnerability, by triggering the same operation multiple times within the time window between checking and execution through concurrent requests, achieving repeated coupon collection、Duplicate Withdrawal、Over-purchase and other business logic breaches.
Prerequisites:
- Target has a balance/Points/Operations on quantifiable resources like coupons
- Python/Turbo IntruderEnvironment
Execution Outline:
1. 1. Identify race condition targets
2. 2. PythonConcurrent testing scripts
3. 3. Burp Turbo IntruderTesting
4. 4. Validate race condition success
## Payment logic tampering
- ID: biz-payment-tamper
- Difficulty: intermediate
- Subcategory: Payment security
- Tags: Payment, Amount tampering, Business logic, 0Yuan purchase, E-commerce security
- Original Extracted Source: original extracted web-security-wiki source/biz-payment-tamper.md
Description:
By modifying the amount in the payment request、Quantity、Parameters such as discounts to manipulate transaction logic. Common in e-commerce platforms and online payment systems, potentially leading to...0Yuan purchase、Negative Pricing、Serious business risks such as discount stacking.
Prerequisites:
- Target has payment/Place order function.
- Can intercept and modify.HTTPRequest
Execution Outline:
1. 1. Amount tampering test
2. 2. Quantity and freight tampering
3. 3. Coupon stacking and replacement
4. 4. Payment callback tampering
## Password reset logic flaw
- ID: biz-password-reset
- Difficulty: intermediate
- Subcategory: Authentication flaws
- Tags: Password reset, Authentication bypass, Business logic, Verification code, HostInjection
- Original Extracted Source: original extracted web-security-wiki source/biz-password-reset.md
Description:
Logical vulnerabilities in the password reset process, including reset token leakage、CAPTCHA brute force、Response Manipulation、HostHeader injection and other attack methods can achieve arbitrary user password reset.
Prerequisites:
- Target has password reset/Retrieve Function
- Can be interceptedHTTPRequest
Execution Outline:
1. 1. HostHeader injection to steal reset links
2. 2. CAPTCHA brute force
3. 3. Response manipulation bypass
4. 4. Weak randomness of reset tokens
## Verification code bypass technique
- ID: biz-captcha-bypass
- Difficulty: beginner
- Subcategory: CAPTCHA security
- Tags: Verification code, CAPTCHA, Bypass, SMS Verification Code, Human verification
- Original Extracted Source: original extracted web-security-wiki source/biz-captcha-bypass.md
Description:
Bypass graphic verification codes、SMS Verification Code、Various techniques of human verification mechanisms like sliding verification, including response leakage、Reuse attack、OCRIdentification、Exploitation of logical flaws, etc.
Prerequisites:
- The target has CAPTCHA protection functionality
- PythonEnvironment
Execution Outline:
1. 1. CAPTCHA Response Leakage
2. 2. CAPTCHA Reuse Attack
3. 3. Delete verification code parameter
4. 4. Universal CAPTCHA

