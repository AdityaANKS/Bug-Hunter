# PHP Code audit Checklist

## Step 1: Identify the input entry

### superglobal variables
```php
$_GET['param']        // URL query parameters
$_POST['param']       // POST form data
$_REQUEST['param']    // GET + POST + COOKIE
$_COOKIE['param']     // Cookie value
$_SERVER['HTTP_X']    // HTTP Request header
$_FILES['file']       // Upload files
$_SESSION['key']      // Session Data (if controllable)
```

### covert input
```php
php://input           // POST raw data
getallheaders()       // all HTTP head
getenv()              // environment variables
file_get_contents()   // from file/URL read
```

## Step Two: Identify Dangerous Functions

### code execution
```php
eval()                // execute arbitrary PHP code
assert()              // PHP < 7 executable code
preg_replace(/e)      // /e Modifier execution replacement result
create_function()     // Create anonymous function
call_user_func()      // Call the callback function
call_user_func_array()// Call the callback function (array parameter
array_map()           // Apply a callback to an array element
usort()               // Custom sorting (callbacks can be injected
array_filter()        // Filter array (callback can be injected
```

### command execution
```php
system()              // Execute external program and output results
exec()                // Execute an external program and return the last line
shell_exec()          // Execute the command and return the complete output
passthru()            // Execute external program and output original data
popen()               // open process pipe
proc_open()           // Open process (more flexible
pcntl_exec()          // Execute program (requires pcntl Expand
backtick `cmd`           // Equivalent to shell_exec()
```

### File operations
```php
include() / require()          // File contains
include_once() / require_once()
file_get_contents()            // read file
file_put_contents()            // write file
fopen() + fread()              // open and read
readfile()                     // Output file content
highlight_file() / show_source()// Highlight source code
unlink()                       // Delete files
rename()                       // Rename file
copy()                         // Copy files
move_uploaded_file()           // Mobile upload files
```

### Deserialization
```php
unserialize()        // Deserialize object
__wakeup()           // Called during deserialization
__destruct()         // Called when the object is destroyed
__toString()         // Object is called when a string is used
__call()             // Triggered when a method that does not exist is called
__get()              // Triggered when accessing a property that does not exist
```

## Step 3: Analyze and filter/check logic

### Regular filter analysis list
```php
preg_match("/pattern/flags", $input)

□ Is there i Modifier?  → No → Can be case bypassed
□ Is there m Modifier?  → have → Consider newline bypassing ^$
□ Is there s Modifier?  → have → . Match newline
□ Are you checking a string or an array? → Array bypass
□ Is it possible to backtrack beyond the limit?  → PCRE Backtracking limit bypass
```

### Common filter functions
```php
str_replace()        // String replacement (can be bypassed by double writing)
str_ireplace()       // Case-insensitive replacement
strstr() / strpos()  // String search (can be bypassed by case) / Array bypass)
strlen()             // Length check (can be bypassed using features)
in_array()           // Array checking (weak type comparison)
is_numeric()         // Number check (hex/scientific notation)
intval()             // Integer conversion (feature bypass)
trim()               // remove blank(%0a%0d Bypass)
htmlspecialchars()   // HTML Escape (single quotes are not escaped by default)
addslashes()         // Add slash (wide byte/GBK Bypass)
mysql_real_escape_string() // escape (wide byte/GBK Bypass)
```

## Step 4: Draw the data flow diagram

```
user input → [filterA] → [filterB] → hazard function
          ↓
          Being filtered?
          ↓ no
          [Bypass check] → Dangerous function execution
```

### path selection principles
1. **The least filtered path takes precedence**
2. **The path with the fewest parameters takes precedence**(3 path of parameters < 5 parameter path)
3. **Paths with visible results take precedence**(system() take precedence over exec())
4. **Simple bypass priority**(Case bypassed < encoding bypass < chain bypass)

## Step 5: Output Visibility Analysis

### Confirm that the command output is visible
```
1. system() output → directly in HTTP Responding
2. exec() output → need extra echo
3. eval() + system() → output in eval in context
4. highlight_file() + system() → Output after source code highlighting
```

### Test first when unsure
```php
// First test the output visibility with a simple command
system('id');
system('echo TESTFLAG123');
// exist HTTP Search in response TESTFLAG123
```

### Response analysis techniques
```python
# use python_execute Analyze response
import requests
r = requests.get(url, params=payload)
print(f"Status: {r.status_code}")
print(f"Length: {len(r.text)}")
print(f"Headers: {dict(r.headers)}")
# Just watch the end N character(flag (always at the end)
print(f"Tail: {r.text[-500:]}")
# search flag Pattern
import re
flags = re.findall(r'(NSSCTF\{[^}]+\}|flag\{[^}]+\}|CTF\{[^}]+\})', r.text)
if flags:
    print(f"FLAG FOUND: {flags}")
```
