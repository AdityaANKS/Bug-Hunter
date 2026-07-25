# Website Information Collection Reference

## 1. Website Architecture Identification

### Technology stack inference methods
1. **HTTP Response headers** — Server、X-Powered-By、Set-Cookie Features
2. **HTML Source code characteristics** — meta generator、Specific class/id Naming
3. **JS File path** — /static/js/app.js、/wp-content/、/assets/
4. **Cookie Name** — PHPSESSID(php)、JSESSIONID(Java)、_rails_session(Rails)
5. **URL Path** — ?id= (PHP)、/api/ (REST)、/wp-admin/ (WordPress)

### Common architecture combinations.
| Language | Framework | Database | Server | Features |
|------|------|--------|--------|------|
| PHP | Laravel | MySQL | Apache/Nginx | Set-Cookie: laravel_session |
| PHP | WordPress | MySQL | Apache | /wp-content/, /wp-admin/ |
| Python | Django | PostgreSQL | Nginx+Gunicorn | CSRF middleware cookie |
| Python | Flask | SQLite/MySQL | Nginx+uWSGI | Set-Cookie: session= |
| Java | Spring | MySQL/Oracle | Tomcat | JSESSIONID |
| Node.js | Express | MongoDB | Nginx | X-Powered-By: Express |
| Ruby | Rails | PostgreSQL | Nginx+Puma | _rails_session |

### python_execute Architecture detection
```python
import requests

url = "https://target.com"
r = requests.get(url, timeout=10)

# 1. Response Header Analysis
headers = r.headers
print(f"Server: {headers.get('Server', 'N/A')}")
print(f"X-Powered-By: {headers.get('X-Powered-By', 'N/A')}")

# 2. Cookie Analysis
cookies = r.cookies
for cookie in cookies:
    print(f"Cookie: {cookie.name} = {cookie.value[:20]}...")

# 3. HTML Feature Analysis
html = r.text
# WordPress
if 'wp-content' in html or 'wp-includes' in html:
    print("[+] WordPress Detection")
# Laravel
if 'laravel_session' in str(cookies):
    print("[+] Laravel Detection")
# Django
if 'csrftoken' in str(cookies) or 'csrfmiddlewaretoken' in html:
    print("[+] Django Detection")
# Hexo
if 'hexo' in html.lower():
    print("[+] Hexo Blog detection")
# Hugo
if 'hugo' in html.lower():
    print("[+] Hugo Blog detection")
```

## 2. Web Fingerprint recognition

### CMS Fingerprint features
| CMS | Feature path | Feature string |
|-----|---------|-----------|
| WordPress | /wp-login.php, /wp-content/ | wp-content, xmlrpc.php |
| Joomla | /administrator/ | /media/jui/ |
| Drupal | /misc/drupal.js | Drupal.settings |
| Discuz | /forum.php | discuz_uid |
| Typecho | /admin/login.php | typecho |
| Hexo | /archives/ | hexo |
| Ghost | /ghost/ | ghost-frontend |

### Front-end framework characteristics
| Framework | Features |
|------|------|
| React | data-reactroot, __NEXT_DATA__ |
| Vue.js | data-v-xxx, __vue__ |
| Angular | ng-version, _nghost |
| jQuery | jQuery in scripts |
| Bootstrap | bootstrap.css/js |

### python_execute Fingerprint recognition
```python
import requests, re

url = "https://target.com"
r = requests.get(url, timeout=10)
html = r.text

# CMS Detection
cms_signatures = {
    "WordPress": ["wp-content", "wp-includes", "wp-admin"],
    "Joomla": ["/administrator/", "media/jui"],
    "Drupal": ["Drupal.settings", "/misc/drupal"],
    "Hexo": ["hexo", "/archives/"],
    "Hugo": ["hugo", "gohugo"],
    "Ghost": ["ghost-frontend", "/ghost/"],
}

for cms, sigs in cms_signatures.items():
    if any(sig in html for sig in sigs):
        print(f"[+] CMS: {cms}")

# Front-end framework detection
fw_signatures = {
    "React": ["data-reactroot", "__NEXT_DATA__", "react"],
    "Vue.js": ["data-v-", "__vue__", "vue"],
    "Angular": ["ng-version", "_nghost", "angular"],
    "jQuery": ["jquery", "jQuery"],
    "Bootstrap": ["bootstrap"],
}

for fw, sigs in fw_signatures.items():
    if any(sig.lower() in html.lower() for sig in sigs):
        print(f"[+] Front-end framework: {fw}")

# JS File Extraction
js_files = re.findall(r'src=["\']([^"\']*\.js[^"\']*)["\']', html)
print(f"JS File: {js_files[:10]}")
```

## 3. WAF Detection

### Common WAF Features
| WAF | Interception Feature |
|-----|---------|
| Cloudflare | Server: cloudflare, CF-Ray header |
| AWS WAF | Server: AmazonS3, x-amz-request-id |
| Alibaba Cloud WAF | Set-Cookie Contain acw_tc |
| Tencent Cloud WAF | Specific Interception Page |
| Baota WAF | Intercept page containing "Baota" |
| Security Dog | Intercept page containing "safedog" |
| ModSecurity | Specific 403 Response. |

### python_execute WAF Detection
```python
import requests

url = "https://target.com"

# 1. Normal request
r1 = requests.get(url)

# 2. Trigger WAF The request
waf_payloads = [
    "/?id=1' OR 1=1--",
    "/?search=<script>alert(1)</script>",
    "/../../../etc/passwd",
    "/?file=php://filter/convert.base64-encode/resource=index",
]

for payload in waf_payloads:
    r2 = requests.get(url + payload, allow_redirects=False)
    # Status code change
    if r2.status_code in [403, 406, 429, 501]:
        print(f"[!] WAF Detection: {payload} → {r2.status_code}")
    # Significant changes in response length
    if abs(len(r2.text) - len(r1.text)) > 500:
        print(f"[!] Response length variations: Normal={len(r1.text)}, Attack={len(r2.text)}")

# 3. Check specific WAF Response headers
waf_headers = {
    "cloudflare": ["cf-ray", "server: cloudflare"],
    "aws": ["x-amz-request-id", "x-amz-cf-id"],
    "Alibaba Cloud": ["acw_tc"],
}
for waf_name, sigs in waf_headers.items():
    for sig in sigs:
        if sig in str(r1.headers).lower():
            print(f"[+] WAF Detection: {waf_name}")
```

## 4. Sensitive directories & Sensitive files

### Common sensitive path list
```
/robots.txt
/sitemap.xml
/.git/
/.svn/
/.env
/.DS_Store
/web.config
/config.php
/config.yml
/backup/
/admin/
/login/
/api/
/swagger/
/graphql
/phpinfo.php
/test/
/debug/
/console/
/actuator/
/.well-known/
```

### python_execute Directory scanning
```python
import requests

target = "https://target.com"
paths = [
    "/robots.txt", "/sitemap.xml", "/.git/", "/.env", "/.DS_Store",
    "/admin/", "/backup/", "/config.php", "/api/", "/phpinfo.php",
    "/.git/config", "/.git/HEAD", "/wp-config.php",
    "/swagger/", "/graphql", "/actuator/",
]

for path in paths:
    try:
        r = requests.get(target + path, timeout=5, allow_redirects=False)
        if r.status_code in [200, 301, 302, 401, 403]:
            print(f"[{r.status_code}] {path}")
    except:
        pass
```

## 5. Source Code Leak Check

### Common Types of Source Code Leaks
| Type | Path | Detection method |
|------|------|---------|
| Git Repository | /.git/config, /.git/HEAD | 200 And contains git Content |
| SVN Repository | /.svn/entries | 200 And contains svn Content |
| .DS_Store | /.DS_Store | Parse after download |
| .env File | /.env | Containing DB_PASSWORD Etc. |
| web.config | /web.config | IIS Configuration |
| Backup Files | /.bak, /.swp, /.old, /~ | Direct download |
| Docker | /Dockerfile, /docker-compose.yml | Container configuration |
| package.json | /package.json | Node.js Dependency |
| composer.json | /composer.json | PHP Dependency |

### Git Repository leakage exploits
```python
import requests

target = "https://target.com"

# 1. Check .git/HEAD
r = requests.get(f"{target}/.git/HEAD")
if r.status_code == 200 and "ref:" in r.text:
    print("[!] Git Repository leakage!")
    # 2. Attempt to obtain ref
    ref_path = r.text.strip().split("ref: ")[1] if "ref: " in r.text else ""
    if ref_path:
        r2 = requests.get(f"{target}/.git/{ref_path}")
        if r2.status_code == 200:
            print(f"[+] Git ref: {r2.text.strip()}")

# 3. Attempt to obtain config
r3 = requests.get(f"{target}/.git/config")
if r3.status_code == 200:
    print(f"[+] Git config:\n{r3.text}")
```

## 6. Side station query (same IP Reverse lookup domain)

### Query method
1. **Webmaster tools** — https://stool.chinaz.com/same
2. **Microstep online** — https://x.threatbook.cn
3. **crt.sh** — Use IP Query Certificate Associated Domain Names
4. **Censys** — https://search.censys.io

### python_execute Side channel query
```python
import requests, json

ip = "1.2.3.4"

# Method1: crt.sh Query same IP Certificate
r = requests.get(f"https://crt.sh/?q={ip}&output=json", timeout=15)
if r.status_code == 200:
    domains = set()
    for entry in r.json():
        for name in entry.get('name_value', '').split('\n'):
            if name.strip() and '*' not in name:
                domains.add(name.strip())
    print(f"[+] Same IP Domain name ({len(domains)}):")
    for d in sorted(domains):
        print(f"  - {d}")
```

## 7. C Segment query (hosts alive in the same subnet)

### python_execute C Segment scanning
```python
import requests, socket
from concurrent.futures import ThreadPoolExecutor

# Obtain from domain name IP
domain = "target.com"
ip = socket.gethostbyname(domain)
# Extract C Segment
c_segment = ".".join(ip.split(".")[:3])

def check_host(ip, timeout=1):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((ip, 80))
        s.close()
        if result == 0:
            return ip
    except:
        pass
    return None

# Scan C Segment (1-254)
alive_hosts = []
with ThreadPoolExecutor(max_workers=50) as executor:
    ips = [f"{c_segment}.{i}" for i in range(1, 255)]
    results = executor.map(check_host, ips)
    alive_hosts = [ip for ip in results if ip]

print(f"[+] C Segment survival host: {alive_hosts}")
```
