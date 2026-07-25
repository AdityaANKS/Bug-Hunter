# PHP Regex bypass quick reference

## Core principles

PHP 's `preg_match()` Functions often get bypassed when filtering user input due to improper design of regular expressions.
Understand regular modifiers and PHP Type behavior is the key to bypassing.

## 1. Case bypass

**Applicable conditions**: No regex `i`(PCRE_CASELESS) Modifier

```php
// Filtered regex — None i Modifiers
preg_match("/n|c/m", $_GET['p']);  // Match only lowercase n and c

// Bypass Method — In Capital Letters
// nss2 Contains n → Intercepted
// Nss2 Contains N → Mismatched lowercase n → Bypass Successful!
// Ctf Contains C → Mismatched lowercase c → Bypass Successful!

// PHP Class names and function names are case insensitive
call_user_func('Nss2::Ctf');  // Equivalent to nss2::ctf()
```

**Verification method**: First confirm whether the regex is included `i` Modifier, then decide to use case switching to bypass

## 2. Array bypass

**Applicable conditions**: The function only accepts string parameters, passing in an array will return false

```php
// preg_match() The second parameter requires a string.
// Incoming array → Return false + Warning → Bypass regular checks

// URL: ?p[]=nss2&p[]=ctf
// $_GET['p'] = ['nss2', 'ctf']  (Array instead of string)
// preg_match("/n|c/m", ['nss2', 'ctf']) → false → Bypass!

// call_user_func Accept an array as a callback
call_user_func(['nss2', 'ctf']);  // Equivalent to nss2::ctf()
```

## 3. Line Break Bypass

**Applicable conditions**: Regular Expression Usage `^...$` Anchor Point + `m` Modifiers

```php
// Common misconceptions:m Modifiers will not allow /n/ Match line breaks
// m Modifiers only affect ^ and $ Matching behavior (multi-line mode)

// Circumstances that can be bypassed:
preg_match("/^flag$/", $input);  // m Available under Modifiers %0aflag Bypass

// Inescapable situations:
preg_match("/n|c/m", $input);    // m No impact n and c Matching
```

## 4. PCRE Bypass backtracking limits

**Applicable conditions**: Ultra-long string + Large backtracking regex

```php
// preg_match Default backtrack limit 1000000
// Return if exceeded false(not 0 Or 1)

// Constructing an excessively long string to trigger backtracking limits
$str = str_repeat('a', 1000000);
preg_match("/.*$/", $str);  // Return false → Bypass
```

## 5. `%0a` Line break injection

**Applicable conditions**: Regular Expression Usage `^...$` But not `s`(DOTALL) Modifier

```php
// Bypass ^...$ Anchor Point
// Input.: "good\nmalicious"
preg_match("/^good$/", "good\nmalicious");  // None m Time mismatch
preg_match("/^good$/m", "good\nmalicious");  // Yes m matches the first line
```

## Common CTF Question type patterns

| Type | Regular expression examples | Bypass Method |
|------|----------|----------|
| Case filtering | `/n\|c/m` | `Nss2::Ctf`(Case bypass) |
| String Function Filtering | `/system\|exec/` | `p[]=class&p[]=method`(Array bypass) |
| Anchor point matching | `/^flag$/` | `flag%0a` Or `%0aflag`(Newline bypass) |
| Backtrack limit | `/.*/` | Long string trigger PCRE Backtrack limit |
| No anchor points | `/flag/` | `flflagag`(double write bypass, such as if done str_replace) |

## call_user_func Callback method quick reference

```php
// Call ordinary functions
call_user_func('readfile', 'flag.php');

// Call Static Method (in String Form)
call_user_func('Nss2::Ctf');  // Case bypass

// Call static methods (array form)
call_user_func(['Nss2', 'Ctf']);  // After array bypass

// Call Instance Method
call_user_func([$obj, 'method']);
```

## ⚠️ Common errors

1. **`call_user_func('readfile')` Without parameters** — Will not read any files, must pass `call_user_func('readfile', 'flag.php')`
2. **Obfuscation `m` and `i` Modifiers** — `m` It is multi-line mode,`i` case-insensitive matching
3. **Ignore PHP Type juggling** — `preg_match` Encounter array return `false`, not `0`
4. **Guess flag Content** — Must obtain real responses through tools, cannot fabricate
