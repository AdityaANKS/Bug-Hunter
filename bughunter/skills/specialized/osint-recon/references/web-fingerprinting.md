# Web Fingerprint recognition

## Checklist

### HTTP Response header fingerprint
| response header | inferred information | Example |
|--------|---------|------|
| `Server` | Web server | `nginx/1.18.0`、`Apache/2.4.41`、`GitHub.com` |
| `X-Powered-By` | backend language/frame | `PHP/7.4.3`、`Express`、`Next.js` |
| `X-AspNet-Version` | .NET Version | `4.0.30319` |
| `Set-Cookie` | Frame features | `PHPSESSID`→PHP、`JSESSIONID`→Java、`csrf_token`→Django |
| `X-Generator` | CMS | `Hugo`、`WordPress`、`Ghost` |
| `X-DRupal-Cache` | CMS | Drupal |
| `Via` | acting/CDN | `1.1 varnish`→Varnish CDN |

### HTML Source code fingerprint
```python
import re

# WordPress
wp_signs = ['wp-content', 'wp-includes', 'wordpress']
# Hexo
hexo_signs = ['hexo', 'hexo-theme']
# Hugo
hugo_signs = ['hugo', 'gohugo']
# Jekyll
jekyll_signs = ['jekyll']
# Next.js
next_signs = ['__NEXT_DATA__', '_next/']
# Vue
vue_signs = ['data-v-', '__vue__']
# React
react_signs = ['data-reactroot', '__react']

def detect_framework(html):
    html_lower = html.lower()
    frameworks = []
    checks = {
        'WordPress': wp_signs,
        'Hexo': hexo_signs,
        'Hugo': hugo_signs,
        'Jekyll': jekyll_signs,
        'Next.js': next_signs,
        'Vue': vue_signs,
        'React': react_signs,
    }
    for name, signs in checks.items():
        if any(s in html_lower for s in signs):
            frameworks.append(name)
    return frameworks
```

### JavaScript file fingerprint
- Framework specific JS File path:`/wp-includes/js/` → WordPress
- Vue/React DevTools Detection:`__VUE_DEVTOOLS_GLOBAL_HOOK__`、`__REACT_DEVTOOLS_GLOBAL_HOOK__`
- The framework version is usually in JS in comments or variables

### CSS fingerprint
- `/wp-content/themes/` → WordPress
- Hexo Theme features class name
- Bootstrap/Tailwind class feature

### signature file
| file path | inferred information |
|---------|---------|
| `/robots.txt` | CMS information、Hide path |
| `/sitemap.xml` | site structure |
| `/favicon.ico` | Frame default icon |
| `/.well-known/security.txt` | Safe contact details |
| `/humans.txt` | Developer information |
| `/.git/HEAD` | Git Warehouse leak |
| `/.env` | Environment variables leaked |

## GitHub Pages feature
- response header `Server: GitHub.com`
- `X-GitHub-Request-Id` exist
- `X-Cache: HIT` + `X-Fastly-Request-ID` → Fastly CDN
- `Via: 1.1 varnish` → Varnish cache
- Common frameworks:Jekyll、Hexo、Hugo

---

## WAF Detection

### common WAF Identifying features
| WAF | response header/Page features | Interception status code |
|-----|----------------|-----------|
| Cloudflare | `Server: cloudflare`, `CF-Ray` | 403 |
| AWS WAF | `x-amz-request-id`, `x-amz-cf-id` | 403 |
| Alibaba Cloud WAF | Cookie Contains `acw_tc` | 405/403 |
| Tencent Cloud WAF | identification JSON Block page | 403 |
| pagoda WAF | Blocked pages include "pagoda" | 403 |
| safety dog | Blocked pages include "safedog" | 403/404 |
| ModSecurity | identification 403 + Server head | 403 |
| Nginx WAF | `HTTP/1.1 444` or special 403 | 444/403 |

### WAF Detection method
1. **Normal request vs Attack request comparison** — Send a request with attack characteristics and observe the response difference
2. **Response header inspection** — some WAF Specific response headers will be added
3. **Cookie examine** — part WAF Set up tracking Cookie
4. **Status code exception** — The attack request returns an abnormal status code (403/406/429/444）

### common WAF Bypass trigger payload
```
/?id=1' OR 1=1--
/?search=<script>alert(1)</script>
/../../../etc/passwd
/?file=php://filter/convert.base64-encode/resource=index
```

---

## Source code leakage check

### Common source code leak types and detection
| type | path | Detection method | Hazard level |
|------|------|---------|---------|
| Git storehouse | `/.git/config`, `/.git/HEAD` | 200 And contains git content | 🔴 Critical |
| SVN storehouse | `/.svn/entries` | 200 And contains svn content | 🔴 Critical |
| .DS_Store | `/.DS_Store` | Parse the directory structure after downloading | 🟡 Medium |
| .env document | `/.env` | Contains DB_PASSWORD wait | 🔴 Critical |
| web.config | `/web.config` | IIS Configuration leak | 🟡 Medium |
| Backup files | `/.bak`, `/.swp`, `/.old`, `/.tar.gz` | Direct download | 🟡 Medium |
| Docker | `/Dockerfile`, `/docker-compose.yml` | Container configuration | 🟡 Medium |
| package.json | `/package.json` | Node.js rely | 🟢 Low |
| composer.json | `/composer.json` | PHP 依赖 | 🟢 Low |
| webpack | `/webpack.json`, `/map Files` | 源码映射 | 🟡 Medium |

### Git 泄露利用流程
1. 访问 `/.git/HEAD` → 获取 ref 路径
2. 访问 `/.git/config` → 获取远程仓库信息
3. 访问 `/.git/objects/` → 遍历 Git 对象
4. 使用 GitHack/scrabble 工具自动恢复源码

### 敏感文件扫描路径列表
```
/.git/config
/.git/HEAD
/.svn/entries
/.DS_Store
/.env
/.env.bak
/.env.local
/web.config
/config.php
/config.yml
/backup.sql
/database.sql
/db.sql
/phpinfo.php
/test/
/debug/
/console/
/admin/
/wp-config.php
/robots.txt
/sitemap.xml
/.well-known/security.txt
```
