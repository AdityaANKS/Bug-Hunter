# CTF Web quick reference

## common flag Location

### Linux
```
/flag
/flag.txt
/flag.php
/var/www/html/flag.php
/home/ctf/flag
/root/flag
/tmp/flag
/opt/flag
/srv/flag
```

### Docker/environment variables
```
/proc/self/environ
/environment
/.env
```

### PHP identification
```php
// phpinfo() in flag
// View the environment variables section
// View custom segments

// common flag file name
flag.php
flag.txt
f1ag.php
fl4g.php
fl@g.php
th1s_1s_flag.php
```

## First-Pass Workflow

```
1. access target URL
   → View page source code (Ctrl+U)
   → examine HTTP head(Server, X-Powered-By, Set-Cookie)
   → examine Cookie value(base64/JWT/serialization)

2. Check for hidden information
   → robots.txt
   → .git/HEAD
   → .svn/
   → backup document:index.php.bak, www.zip, .index.php.swp, index.php~
   → DS_Store: .DS_Store

3. directory scan
   → /flag, /admin, /login, /upload, /api, /debug
   → /phpinfo.php, /info.php, /test.php
   → /console (Flask Debug), /actuator (Spring Boot)

4. If there is source code → Code audit
   → reference php-code-audit-checklist.md

5. If there is no source code → Active detection
   → SQL Injection test
   → XSS test
   → File upload
   → SSTI test
   → LFI/RFI
```

## Quick test command

```bash
# Check basic information
curl -I http://target/              # HTTP head
curl http://target/robots.txt        # robots
curl http://target/.git/HEAD         # git Give way

# Common injection tests
' OR 1=1 --                          # SQLi
{{7*7}}                              # SSTI
<script>alert(1)</script>            # XSS
../../../etc/passwd                  # LFI
```

## Common response headers Hint

| response header | meaning | Next step |
|--------|------|--------|
| `X-Forwarded-For: 127.0.0.1` | Requires local access | Add to X-Forwarded-For head |
| `Server: nginx/1.x` | Server type | Search known CVE |
| `X-Powered-By: PHP/7.x` | PHP Version | PHP Specific vulnerabilities |
| `Set-Cookie: role=guest` | Permission control | Revise Cookie |
| `Hint: xxx` | direct prompt | Follow the prompts |
| `Flag: xxx` | sometimes directly in the head | Check all response headers |

## Common chain shapes

### PHP simple chain
```
URL → Source code → discovery filter → Bypass filtering → RCE → read flag
```

### PHP multi-step chain
```
Entry page → Discover hint → Follow the jump → new page found → Get source code → Analysis and utilization → RCE
```

### file include chain
```
LFI → Read the source code (php://filter) → Found containing points → Log poisoning/SessionInclude → RCE
```

### SQL injection chain
```
login box → SQLi → Read data → Admin password found → Log in to the background → upload Webshell → RCE
```

### Deserialization chain
```
Controllable serialized data → Analyze available Gadgets → Construct an utilization chain → RCE/SSRF/file reading
```

## coding/Encryption common clues

| feature | possible encoding | Decoding method |
|------|---------|---------|
| There is at the end `=` | Base64 | `crypto_decode base64_decode` |
| `0-9a-f` even length | Hex | `crypto_decode hex_decode` |
| `%XX` | URL coding | `crypto_decode url_decode` |
| `&#xNN;` | HTML entity | `crypto_decode html_decode` |
| `\uXXXX` | Unicode escape | `crypto_decode unicode_decode` |
| ThreeSegment `.` Separator | JWT | `crypto_decode jwt_decode` |
| Dotted Line | Morse | `crypto_decode morse_decode` |
| Can't understand but looks like letters | ROT13/Caesar | `crypto_decode rot13_decode` |
