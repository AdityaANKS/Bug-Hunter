# OSINT Tool manual

## 1. crt.sh — Certificate transparency subdomain query

### usage
```python
import requests

def query_crtsh(domain):
    """pass crt.sh Query subdomain name"""
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            data = r.json()
            subdomains = set()
            for entry in data:
                name = entry.get('name_value', '')
                for n in name.split('\n'):
                    n = n.strip().lower()
                    if n and '*' not in n:
                        subdomains.add(n)
            return sorted(subdomains)
    except Exception as e:
        return [f"Query failed: {e}"]
    return []
```

### Notice
- crt.sh May be slower, set 30s time out
- The results contain wildcard certificates (`*.example.com`), need to filter
- Return after deduplication

## 2. GitHub API — Code and user search

### Search code (detect leaks)
```python
def search_github_code(query, max_results=10):
    """search GitHub code (detection key/configuration leak)"""
    url = "https://api.github.com/search/code"
    params = {'q': query, 'per_page': max_results}
    headers = {'Accept': 'application/vnd.github.v3+json'}
    
    r = requests.get(url, params=params, headers=headers)
    if r.status_code == 200:
        items = r.json().get('items', [])
        return [{
            'repo': item['repository']['full_name'],
            'path': item['path'],
            'url': item['html_url'],
        } for item in items]
    return []
```

### Frequently used searches dork
```
"domain.com" password
"domain.com" api_key
"domain.com" secret
"domain.com" .env
filename:.env domain.com
filename:config domain.com
org:company-name password
```

## 3. DNS Query

### Python built-in DNS Query
```python
import socket

def dns_lookup(domain):
    """Base DNS Query"""
    results = {}
    try:
        # A Record
        results['A'] = socket.gethostbyname_ex(domain)[2]
    except:
        results['A'] = 'Parsing failed'
    
    return results
```

### whole DNS Query (requires dnspython)
```python
# If the environment has dnspython
try:
    import dns.resolver
    
    def full_dns_lookup(domain):
        record_types = ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS']
        results = {}
        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(domain, rtype)
                results[rtype] = [str(r) for r in answers]
            except:
                pass
        return results
except ImportError:
    pass
```

## 4. WHOIS Query

### online WHOIS API
```python
def whois_lookup(domain):
    """via online API Query WHOIS"""
    # use whoisjson.com free API
    url = f"https://whoisjson.com/api/v1/whois?domain={domain}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {
                'registrar': data.get('registrar'),
                'creation_date': data.get('creation_date'),
                'expiration_date': data.get('expiration_date'),
                'name_servers': data.get('name_servers'),
                'registrant': data.get('registrant'),
            }
    except:
        pass
    return {}
```

## 5. Google Dorking

### Common search syntax
| grammar | use | Example |
|------|------|------|
| `site:` | Qualified domain name | `site:github.com "unclec"` |
| `intitle:` | Title keywords | `intitle:"index of" site:example.com` |
| `inurl:` | URL keywords | `inurl:admin site:example.com` |
| `filetype:` | File type | `filetype:pdf site:example.com` |
| `"exact phrase"` | exact match | `"UncleCheng" security` |
| `related:` | Related websites | `related:github.com` |

### Information collection commonly used dork
```
site:github.com "target username"
site:bilibili.com "target username"
site:zhihu.com "target username"
"Mail@domain.com"
"Phone number"
```

## 6. Shodan/Censys(need API Key)

### Shodan search
```python
def shodan_search(api_key, query):
    import shodan
    api = shodan.Shodan(api_key)
    try:
        results = api.search(query)
        return [{
            'ip': result['ip_str'],
            'port': result['port'],
            'org': result.get('org', ''),
            'data': result['data'][:200],
        } for result in results['matches'][:10]]
    except Exception as e:
        return [f"Shodan Query failed: {e}"]
```

## 7. Wayback Machine

### Query historical snapshot
```python
def wayback_query(domain):
    """Query Wayback Machine historical snapshot"""
    url = f"http://archive.org/wayback/available?url={domain}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            snapshots = data.get('archived_snapshots', {})
            if snapshots.get('closest'):
                return snapshots['closest']['url']
    except:
        pass
    return None
```

## 8. Side station query (same as IP Reverse domain name check)

### Online tools
| tool | URL | illustrate |
|------|-----|------|
| Webmaster Tools | https://stool.chinaz.com/same | Most commonly used in China |
| Weibu online | https://x.threatbook.cn | Threat intelligence+Stand by |
| crt.sh | https://crt.sh | use IP Check the domain name associated with the certificate |
| Censys | https://search.censys.io | Global asset search |
| Fofa | https://fofa.info | spatial search engine |

### python_execute Side station inquiry
```python
import requests

def reverse_ip_lookup(ip):
    """pass crt.sh Anti-identification IP domain name"""
    domains = set()
    try:
        r = requests.get(f"https://crt.sh/?q={ip}&output=json", timeout=30)
        if r.status_code == 200:
            for entry in r.json():
                for name in entry.get('name_value', '').split('\n'):
                    name = name.strip()
                    if name and '*' not in name:
                        domains.add(name)
    except Exception as e:
        print(f"crt.sh Query failed: {e}")
    return sorted(domains)

# use
ip = "1.2.3.4"
result = reverse_ip_lookup(ip)
print(f"[+] same IP domain name ({len(result)}):")
for d in result:
    print(f"  - {d}")
```

## 9. C Segment query (surviving hosts in the same network segment)

### Online tools
| tool | URL | illustrate |
|------|-----|------|
| Fofa | https://fofa.info | `ip="1.2.3.0/24"` |
| Shodan | https://www.shodan.io | `net:1.2.3.0/24` |
| Censys | https://search.censys.io | `ip:/1.2.3.0-1.2.3.255/` |

### python_execute C segment scan
```python
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

def scan_c_segment(ip, timeout=1, max_workers=100):
    """scanning C segment live host"""
    prefix = ".".join(ip.split(".")[:3])
    alive = []

    def check(host_ip):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            result = s.connect_ex((host_ip, 80))
            s.close()
            if result == 0:
                return host_ip
        except:
            pass
        return None

    targets = [f"{prefix}.{i}" for i in range(1, 255)]
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check, t): t for t in targets}
        for future in as_completed(futures):
            result = future.result()
            if result:
                alive.append(result)

    return sorted(alive, key=lambda x: int(x.split(".")[-1]))

# use
ip = "1.2.3.4"
hosts = scan_c_segment(ip)
print(f"[+] C segment live host ({len(hosts)}):")
for h in hosts:
    print(f"  - {h}")
```

## 10. ICP Filing inquiry

### Online tools
| tool | URL | illustrate |
|------|-----|------|
| Ministry of Industry and Information Technology registration inquiry | https://beian.miit.gov.cn | official authority |
| Webmaster Tools Registration Query | https://icp.chinaz.com | Convenient query |
| Sky Eye Check | https://www.tianyancha.com | enterprise+Filing association |
| Love station registration inquiry | https://www.aizhan.com/cha/ | Batch query |

### python_execute ICP Filing inquiry
```python
import requests

def icp_lookup(domain):
    """Query ICP Registration information (use public API)"""
    # method1: use chinaz API(need API key)
    # method2: Use public query interface
    try:
        # use whois Query Chinese domain name information
        url = f"https://whois.chinaz.com/{domain}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        r = requests.get(url, headers=headers, timeout=10)
        # Analyze filing information
        import re
        icp_match = re.search(r'Registration number[::]\s*([^<\s]+)', r.text)
        if icp_match:
            return icp_match.group(1)
    except:
        pass

    # If it is an overseas domain name, there is usually no ICP Filing
    return "No registration found (may be an overseas domain name)"
```

## 11. Subdomain discovery (multiple methods)

### method combination strategy
1. **crt.sh** — Certificate transparency (fastest)
2. **search engine dork** — Google/Bing site: search
3. **DNS blasting** — Common prefix dictionary
4. **DNS zone transfer** — try axfr
5. **JS File analysis** — from page JS Extract subdomain name from

### python_execute Subdomain Explosion
```python
import socket
from concurrent.futures import ThreadPoolExecutor

def subdomain_brute(domain, wordlist=None, max_workers=20):
    """Subdomain Explosion"""
    if wordlist is None:
        wordlist = [
            'www', 'mail', 'ftp', 'admin', 'blog', 'dev', 'staging',
            'api', 'test', 'portal', 'cdn', 'ns1', 'ns2', 'mx',
            'app', 'web', 'git', 'ci', 'jenkins', 'jira',
            'vpn', 'remote', 'shop', 'store', 'news',
        ]

    found = []
    def check(sub):
        fqdn = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(fqdn)
            return (fqdn, ip)
        except:
            return None

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(check, wordlist)
        found = [r for r in results if r]

    return sorted(found, key=lambda x: x[0])

# use
domain = "example.com"
subs = subdomain_brute(domain)
print(f"[+] Discover subdomains ({len(subs)}):")
for sub, ip in subs:
    print(f"  - {sub} → {ip}")
```

### DNS Zone transfer attempt
```python
import socket

def try_zone_transfer(domain):
    """try DNS zone transfer"""
    # get NS Record
    try:
        ns_servers = socket.getaddrinfo(domain, None)
    except:
        return []

    # try for each NS Server performs zone transfer
    # NOTE: MODERN DNS Servers usually have this feature disabled
    import subprocess
    results = []
    try:
        result = subprocess.run(
            ['dig', 'axfr', domain, '@' + domain],
            capture_output=True, text=True, timeout=10
        )
        if 'XFR size' in result.stdout:
            results.append(result.stdout)
    except:
        pass

    return results
```
