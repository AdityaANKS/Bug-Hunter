# Scouting report template

## Instructions for use

When the information gathering task is completed, use `python_execute` The tool populates the following template into a complete report,
Save to user-specified path or desktop.

## Markdown report template

```markdown
# 🦞 {Target} reconnaissance report

> Generation time:{date time}
> tool:BugHunter v0.3.2

---

## 1. Goals Overview

| project | content |
|------|------|
| Target URL | {url} |
| IP address | {ip} |
| server | {server} |
| frame/CMS | {framework} |
| CDN | {cdn} |
| SSL Certificate | {ssl_info} |

---

## 2. technical reconnaissance

### 2.1 HTTP response header
| response header | value | Safety tips |
|--------|---|---------|
| Server | {value} | {Note} |
| X-Powered-By | {value} | Leak technology stack |
| ... | ... | ... |

### 2.2 DNS Record
| type | value |
|------|---|
| A | {ip} |
| CNAME | {cname} |
| MX | {mx} |
| TXT | {txt} |

### 2.3 subdomain
| subdomain | IP | illustrate |
|--------|---|------|
| {sub} | {ip} | {note} |

### 2.4 open port
| port | Serve | Version |
|------|------|------|
| 80 | HTTP | nginx/1.18 |
| 443 | HTTPS | nginx/1.18 |

### 2.5 Directories and files
| path | status code | illustrate |
|------|--------|------|
| /robots.txt | 200 | {Content summary} |
| /sitemap.xml | 200 | {Content summary} |
| /.git/HEAD | 403/200 | {Is it leaked?} |

---

## 3. content reconnaissance

### 3.1 Page metadata
- **Title**:{title}
- **Description**:{desc}
- **Keywords**:{keywords}
- **Author**:{author}

### 3.2 external links
| Link | type | illustrate |
|------|------|------|
| {url} | GitHub | Personal homepage |
| {url} | Bstand | video space |
| {url} | CDN | Resource loading |

### 3.3 JavaScript document
| document | Key findings |
|------|---------|
| {path} | {api_endpoint/config/key} |

### 3.4 Hide information
- HTML Note:{comments}
- Hidden fields:{hidden_fields}
- Mail/Contact information:{contacts}

---

## 4. Character tracking

### 4.1 Author information
| project | content | source | Confidence |
|------|------|------|--------|
| Nick name | {name} | {source} | 🟢/🟡/🔴 |
| GitHub | {url} | {source} | 🟢 |
| Bstand | {url} | {source} | 🟢 |
| Mail | {email} | {source} | 🟡 |
| Location | {location} | {source} | 🟡 |

### 4.2 Technical portrait
- **main language**:{languages}
- **technology stack**:{stack}
- **Open source projects**:{repos}
- **areas of concern**:{interests}

### 4.3 Cross-platform relevance
| platform | username/ID | Matching degree | illustrate |
|------|----------|--------|------|
| {platform} | {id} | high/middle/Low | {note} |

---

## 5. Key findings

| # | Discover | risk level | illustrate |
|---|------|---------|------|
| 1 | {finding} | 🔴high/🟡middle/🟢Low | {detail} |

---

## 6. suggestion

1. {suggestion_1}
2. {suggestion_2}

---

*This report is provided by BugHunter Automatically generated, all information comes from public sources.*
```

## Python save code

```python
import os
from datetime import datetime

def save_recon_report(target, report_content, output_path=None):
    """Save reconnaissance report to file"""
    if not output_path:
        # Save to desktop by default
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        safe_name = re.sub(r'[^\w]', '_', target)[:30]
        date_str = datetime.now().strftime('%Y%m%d_%H%M')
        output_path = os.path.join(desktop, f'{safe_name}_reconnaissance report_{date_str}.md')
    
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return output_path
```
