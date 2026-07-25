---
name: osint-recon
description: OSINT Open-source intelligence collection knowledge base — Four-dimensional information collection model (server→Website→Domain name→Personnel), Dimension Four (personnel information) condition trigger
---

# OSINT Open-source intelligence collection knowledge base

For information gathering/Reconnaissance/A practical knowledge base for social engineering scenarios, providing**Four-Dimensional Information Collection Model**(server information → Website information → Domain name information → Personnel information), as well as specific tool usage methods and data extraction techniques.

**With `recon` Skill Difference**:
- `recon` → Technical reconnaissance (port scanning、DNS、Directory Enumeration)— Basic version
- `osint-recon` → Full-dimensional reconnaissance (server + Website + Domain name + Personnel/Social engineering)— Deep version

## Core principles

1. **Four-dimensional full coverage** — Server/Website/The domain executes in three dimensions, while the personnel dimension is triggered based on conditions.
2. **Extract all extractable information from the page** — Not just looking at HTTP The header also needs to consider HTML Content、JS File、Comments
3. **Passive first, then active** — First look at response headers、DNS、WHOIS(Passive), then perform port scanning/Directory Enumeration (Active)
4. **Dimension completion self-check** — Check which dimensions have been completed in each round ✅, which are incomplete ❌, Allowed only after everything is completed [DONE]
5. **External links as clues** — Every external link on the page may be a source of information.
6. **Structured Output** — All findings summarized as Markdown Report

## Four-Dimensional Information Collection Model

### Dimension one: Server information
| Checklist | Tool/Method | Description |
|--------|----------|------|
| Open port & Service version | MCP nmap / `python_execute` + socket | Full-port scanning or common ports (21/22/80/443/3306/6379/8080/8443) |
| Real IP Detection | DNS History / Global Ping / Email header extraction | CDN After the origin site IP — SecurityTrails/DNSHistory/GlobalPing |
| Operating System Fingerprint | TTL Inference + nmap OS Detection | Linux TTL≈64, Windows TTL≈128, Unix TTL≈255 |
| Middleware version | Response headers Server + Error Page + Feature file | Apache/Nginx/IIS/Tomcat Version identification |
| Database recognition | Port Scanning + Error message + Feature behavior | MySQL(3306)/Redis(6379)/MongoDB(27017)/MSSQL(1433) |

### Dimension Two: Website Information
| Checklist | Tool/Method | Description |
|--------|----------|------|
| Website architecture | Response headers + Page features + JS Library | OS + Middleware + Database + Language + Framework → Complete tech stack |
| Web Fingerprint | `fetch` + Response Feature Matching | CMS Type、Front-end framework、JS Library、Template engine |
| WAF Detection | wafw00f Logic + Response features | Intercept page/Special response headers/Exception status codes |
| Sensitive directories & Sensitive files | `python_execute` + Common path dictionary | /admin /backup /config /api /robots.txt /sitemap.xml |
| Source code leakage | Check common leakage paths | .git/.svn/.DS_Store/.env/web.config/Backup Files(.bak/.swp/.old) |
| Side channel query | Same IP Reverse lookup domain | Webmaster tools/Microstep online/crt.sh Same IP Query |
| C Segment query | Live host scanning in the same subnet | nmap -sn Scan /24 Subnet |

### Dimension Three: Domain Name Information
| Checklist | Tool/Method | Description |
|--------|----------|------|
| WHOIS Registration information | `python_execute` + whois API/Command | Registrant/Registrar/NS Server/Registration date/Expiration Date |
| ICP Filing information | Ministry of Industry and Information Technology filing inquiry API | Only Chinese mainland domains need to be checked, offshore domains do not have record-keeping |
| Subdomain Discovery | crt.sh + Brute force + Search Engine + DNS Area teleportation | Multi-method cross-validation to ensure comprehensive coverage |
| DNS Record full volume. | `python_execute` + dnspython/socket | A/CNAME/MX/TXT/NS/SPF/SOA Full query |
| Certificate transparency logs | crt.sh / Censys / certspotter | Discover historical certificates、Subdomain、Associated domain names |

### Dimension Four: Personnel Information ⚡ Condition trigger
**⚠️ This dimension is only executed when one of the following conditions is met:**
- Explicitly mentioned in user commands"Social engineering/Social engineering/Personnel information/Author tracking/Persona"Etc.
- The target website has clear author information (meta author、about Page、Contact information)

**Situations where social engineering should not be done**: Ordinary Corporate Website without Personal Author / Users only request"Scan target" / The goal is IP/Intranet Address

| Tracking Direction | Method | Description |
|----------|------|------|
| Author identification extraction | Page meta author、about Page | Username、Nickname、Email |
| GitHub Tracking | `fetch` + GitHub API | Repository、Language preference、Contribution records、Email |
| Social media | Extract links from the page → Access | BStation、Weibo、Zhihu、Twitter、LinkedIn |
| Cross-platform association | Use username/Email search other platforms | Same ID Cross-platform search |
| Historical Submissions | GitHub commits → Submission email | Associate with other projects and identities |
| leak detection | GitHub Historical code search | .env、config、Key leakage |

## First-Pass Workflow

1. **Access target** → `fetch` Obtain the homepage, extract HTTP Header + HTML Content
2. **Dimension one: Server information** → Port scanning、Real IP、OS Fingerprint、Middleware/Database recognition
3. **Dimension Two: Website Information** → Web Fingerprint、WAF Detection、Sensitive directories/Source code leakage、Side stand/CSegment
4. **Dimension Three: Domain Name Information** → WHOIS、ICP Record、Subdomain、DNS Record、Certificate transparency
5. **Dimension four (condition trigger)** → Extract author information、Cross-platform tracking、Information summary
6. **Dimension completion self-check** → Confirm that each dimension has at least one round of checks
7. **Summary report** → Generate Markdown Format reconnaissance report

## Scenario routing

| Scene | Reference documents | Core content |
|------|---------|---------|
| Server information collection | `server-recon.md` | Port scanning、Real IP、OS Fingerprint、Middleware/Database recognition |
| Website information collection | `website-recon.md` | Architecture/Fingerprint/WAF/Sensitive directories/Source code leakage/Side stand/CSegment |
| Web Fingerprint recognition | `web-fingerprinting.md` | Framework detection、Version identification、Technology stack inference |
| Author tracking method | `author-tracking.md` | Extract author from page → Cross-platform tracking → Information summary |
| OSINT Tool usage. | `osint-toolkit.md` | crt.sh、GitHub API、Search Engine dork、Side stand/CSegment/ICP |
| Social engineering information compilation | `social-engineering-intel.md` | Persona、Relationship networks、Information cross-verification |
| Reconnaissance report template | `recon-report-template.md` | Standard Markdown Report format (Four dimensions) |

## ⭐ Commonly used extract code snippets

### From HTML Extract all external links
```python
import re
html = "..."  # fetch Obtained HTML
links = re.findall(r'href=["\'](https?://[^"\']+)["\']', html)
for link in set(links):
    print(link)
```

### From HTML Extract author information
```python
import re
# meta author
author = re.findall(r'<meta\s+name=["\']author["\']\s+content=["\']([^"\']+)["\']', html)
# about Page link
about_links = re.findall(r'href=["\']([^"\']*(?:about|me|contact)[^"\']*)["\']', html, re.I)
```

### Query crt.sh Subdomain
```python
import requests
domain = "example.com"
r = requests.get(f"https://crt.sh/?q=%.{domain}&output=json")
if r.status_code == 200:
    for entry in r.json():
        print(entry['name_value'])
```

### GitHub User information
```python
import requests
username = "target_user"
r = requests.get(f"https://api.github.com/users/{username}")
if r.status_code == 200:
    data = r.json()
    print(f"Name: {data.get('name')}")
    print(f"Bio: {data.get('bio')}")
    print(f"Email: {data.get('email')}")
    print(f"Blog: {data.get('blog')}")
    print(f"Location: {data.get('location')}")
    print(f"Company: {data.get('company')}")
```

### WAF Detection (response feature method)
```python
import requests
url = "https://target.com"
# Normal request
r1 = requests.get(url)
# Trigger WAF Requests (with attack characteristics)
r2 = requests.get(url + "/?id=1' OR 1=1--")
# Compare response
if r1.status_code != r2.status_code or len(r1.text) != len(r2.text):
    print("[!] Potential presence WAF")
    print(f"Normal status code: {r1.status_code}, Attack status code: {r2.status_code}")
```

### Side station query (same IP Reverse lookup domain)
```python
import requests
ip = "1.2.3.4"
# Use chinaz API Or other reverse lookup interfaces
# Can also be through crt.sh Query same IP Certificate
r = requests.get(f"https://crt.sh/?q={ip}&output=json")
```
