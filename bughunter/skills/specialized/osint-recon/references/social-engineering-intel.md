# Social engineering information summary

## Character portrait construction framework

### information dimension

| Dimensions | data source | Extraction method |
|------|--------|---------|
| Identity mark | page meta、GitHub | Regular extraction author/copyright |
| social network | Page external links | `<a href>` Match social media domain names |
| technology preference | GitHub Warehouse language distribution | GitHub API |
| geographical location | GitHub location、blog | Profile page |
| career information | GitHub company、LinkedIn | Profile page |
| Contact information | GitHub email、Blog contact page | API + Page extraction |
| areas of interest | GitHub Warehouse theme、blog post | storehouse topics + Article classification |

## Information cross-validation

### in principle
1. **Do not rely on single sources** — Key information needs to be at least 2 confirmed by independent sources
2. **timeliness annotation** — Mark the acquisition time of the information, and mark outdated information separately.
3. **confidence rating**:
   - 🟢 **high**: Confirmed by multiple independent sources
   - 🟡 **middle**:Single Trusted Source
   - 🔴 **Low**:infer/Not verified

### Common correlation patterns

```
blog GitHub Link → GitHub username → GitHub API Get email
                                  → GitHub API Get warehouse → Technology stack inference
                                  → GitHub Submit email → Link to other identities

blog Bstand Link → Bstand UID → BSite home page → focus on/fan → interest tags
                                    → Contribute video → Technical field

username → Cross-platform search → Discover more social accounts
Mail → haveibeenpwned → Data breach records
```

## Social media information extraction

### Bstand
```python
import re

def extract_bilibili_uid(url):
    """from Bstand URL extract UID"""
    # space.bilibili.com/12345
    m = re.search(r'bilibili\.com/(\d+)', url)
    if m:
        return m.group(1)
    return None
```

### Weibo
```python
def extract_weibo_uid(url):
    """From Weibo URL extract UID"""
    # weibo.com/u/12345 or weibo.com/username
    m = re.search(r'weibo\.com/(?:u/)?(\w+)', url)
    if m:
        return m.group(1)
    return None
```

### Zhihu
```python
def extract_zhihu_username(url):
    """From Zhihu URL Extract username"""
    # zhihu.com/people/username
    m = re.search(r'zhihu\.com/people/([^/?]+)', url)
    if m:
        return m.group(1)
    return None
```

## Information summary report format

```markdown
# target reconnaissance report

## 📋 Basic information
| project | content | Confidence | source |
|------|------|--------|------|
| Target | https://xxx | - | user input |
| frame | Hexo | 🟢 | HTTPhead+HTMLfeature |
| server | GitHub Pages | 🟢 | Serverhead |
| author | XXX | 🟢 | meta author |
| ... | ... | ... | ... |

## 👤 person image
- **Nick name**:XXX
- **GitHub**:https://github.com/xxx
- **Bstand**:https://space.bilibili.com/xxx
- **technology stack**:Python / JavaScript
- **Location**:Shenzhen
- ...

## 🔗 correlation discovery
- [Discover1]
- [Discover2]

## 📌 Key findings
1. ...
2. ...

---
*Report generation time:YYYY-MM-DD HH:MM*
*数据来源：目标网站、GitHub API、社交媒体公开信息*
```

## 隐私与伦理

- ✅ 只收集**公开信息**（不需要登录即可访问的内容）
- ✅ 不尝试登录他人账号
- ✅ 不利用收集的信息进行骚扰或社会工程攻击
- ✅ 标注信息来源，确保可追溯
- ❌ 不收集私人通讯内容
- ❌ 不利用信息进行钓鱼或其他欺骗行为
