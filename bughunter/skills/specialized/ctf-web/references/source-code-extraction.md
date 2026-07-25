# CTF Web Source code extraction method reference

## core cognition

- CTF Web Commonly used questions `highlight_file(__FILE__)` Showing the source code, the output is HTML coloring code
- There are also questions only in HTML Exposing part of the source code in comments or hidden elements is part of the design
- **Source code is an important clue, but not the only clue**——The key entrance to some topics is robots.txt、response header、Hidden files, etc.

---

## Method one:strip_tags extract(highlight_file Scenario preferred)

**Applicable**:`highlight_file()` / `show_source()` Page showing source code

```python
import requests, re
r = requests.get(url)
# remove all HTML Tag, get plain text
clean = re.sub(r'<[^>]+>', '', r.text)
# Optional: remove extra blank lines
clean = re.sub(r'\n{3,}', '\n\n', clean)
print(clean)
```

**Notice**:
- will remove all HTML tag, if it exists in the source code itself HTML Strings will also be removed
- fetch Tools obtained HTML Shaded output**Not suitable for direct visual restoration**, it is recommended to use python_execute verify

---

## Method two:php://filter Read source code

**Applicable**: There is a file containing a vulnerability (`include`/`require`) scene

```
?page=php://filter/convert.base64-encode/resource=index.php
?page=php://filter/read=convert.base64-encode/resource=flag.php
```

Get base64 After encoding the source code:
```python
import base64
source = base64.b64decode(base64_string).decode('utf-8')
print(source)
```

---

## Method three:.phps suffix

**Applicable**: The server is configured PHP Source code display

```
/learning.phps
/index.phps
```

---

## Method 4: Back up files / Version control leak

| path | illustrate |
|------|------|
| `.git/HEAD` | Git Warehouse leak |
| `.svn/entries` | SVN Warehouse leak |
| `index.php.bak` | Backup files |
| `index.php~` | Editor temporary files |
| `www.zip` / `web.tar.gz` | Whole site packaging |
| `.index.php.swp` | Vim exchange files |

---

## Method five:HTML Comments and hidden elements

Some topics are HTML Place source code or tips in comments:

```python
import requests, re
r = requests.get(url)
# extract HTML Annotation content
comments = re.findall(r'<!--(.*?)-->', r.text, re.DOTALL)
for c in comments:
    print(c)
```

---

## Method 6: Response header and Cookie

Some questions have hints hidden in the response headers:

```python
import requests
r = requests.get(url)
print("Headers:", dict(r.headers))
print("Cookies:", dict(r.cookies))
```

---

## Source code integrity judgment

After extracting the source code, you can check whether it is complete:

| Check items | illustrate |
|--------|------|
| brace matching | `if` not closed `}` It may mean that the source code has been truncated, or it may be that the title is intentionally so. |
| There is an output statement | if not `echo`/`print`/`die`, there may be unseen code |
| There is a dangerous function | if not `eval`/`system` wait,RCE The entrance may be on other pages |

**Notice**: There are two possibilities for incomplete source code:——
1. There is a problem with the extraction method → Change the method and re-extract
2. The problem is that it only exposes so much → Need to continue exploring other clues (other pages、parameter、document)
