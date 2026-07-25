# Author tracking methods

## core process

```
Extract author ID from page → Determine unique identifier(username/Mail) → Cross-platform search → Information summary
```

## Step 1: Extract author ID from page

### HTML Meta Label
```python
import re

def extract_author_from_meta(html):
    """from HTML meta Tags extract author information"""
    authors = []
    
    # <meta name="author" content="XXX">
    m = re.findall(r'<meta\s+name=["\']author["\']\s+content=["\']([^"\']+)["\']', html)
    authors.extend(m)
    
    # <meta name="copyright" content="XXX">
    m = re.findall(r'<meta\s+name=["\']copyright["\']\s+content=["\']([^"\']+)["\']', html)
    authors.extend(m)
    
    # OG Label
    m = re.findall(r'<meta\s+property=["\']article:author["\']\s+content=["\']([^"\']+)["\']', html)
    authors.extend(m)
    
    return list(set(authors))
```

### Page link extraction
```python
def extract_social_links(html):
    """Extract social media links from page"""
    links = re.findall(r'href=["\'](https?://[^"\']+)["\']', html)
    
    social = {}
    for link in links:
        if 'github.com' in link:
            social['github'] = link
        elif 'bilibili.com' in link:
            social['bilibili'] = link
        elif 'weibo.com' in link or 'weibo.cn' in link:
            social['weibo'] = link
        elif 'zhihu.com' in link:
            social['zhihu'] = link
        elif 'twitter.com' in link or 'x.com' in link:
            social['twitter'] = link
        elif 'linkedin.com' in link:
            social['linkedin'] = link
        elif 'youtube.com' in link:
            social['youtube'] = link
        elif 'facebook.com' in link:
            social['facebook'] = link
    
    return social
```

## Step 2: GitHub track

### User information API
```python
import requests

def get_github_profile(username):
    """get GitHub User public information"""
    r = requests.get(f"https://api.github.com/users/{username}")
    if r.status_code != 200:
        return None
    
    data = r.json()
    return {
        'name': data.get('name'),
        'bio': data.get('bio'),
        'email': data.get('email'),
        'blog': data.get('blog'),
        'location': data.get('location'),
        'company': data.get('company'),
        'public_repos': data.get('public_repos'),
        'followers': data.get('followers'),
        'following': data.get('following'),
        'created_at': data.get('created_at'),
        'avatar_url': data.get('avatar_url'),
    }

def get_github_repos(username):
    """Get the user's public warehouse (infer technology stack)"""
    r = requests.get(f"https://api.github.com/users/{username}/repos?per_page=100")
    if r.status_code != 200:
        return []
    
    repos = r.json()
    languages = {}
    for repo in repos:
        lang = repo.get('language')
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
    
    return {
        'top_languages': sorted(languages.items(), key=lambda x: -x[1])[:5],
        'repo_count': len(repos),
        'starred_total': sum(r.get('stargazers_count', 0) for r in repos),
    }
```

### from GitHub Submit record extraction email
```python
def get_github_commit_email(username, repo):
    """from GitHub Submit records to extract author email"""
    r = requests.get(f"https://api.github.com/repos/{username}/{repo}/commits?per_page=10")
    if r.status_code != 200:
        return []
    
    emails = set()
    for commit in r.json():
        author = commit.get('commit', {}).get('author', {})
        if author.get('email'):
            emails.add(author['email'])
    
    return list(emails)
```

## Step 3: Cross-platform relevance

### Search other platforms by username
```python
# Common platform detection
PLATFORMS = {
    'GitHub': 'https://github.com/{username}',
    'Bstand': 'https://space.bilibili.com/search?keyword={username}',
    'Zhihu': 'https://www.zhihu.com/search?type=content&q={username}',
    'CSDN': 'https://blog.csdn.net/{username}',
    'nuggets': 'https://juejin.cn/user/{username}',
    'Twitter': 'https://twitter.com/{username}',
    'LinkedIn': 'https://www.linkedin.com/in/{username}',
}

async def cross_platform_search(username, fetch_tool):
    """Search multiple platforms by username"""
    results = {}
    for platform, url_template in PLATFORMS.items():
        url = url_template.format(username=username)
        try:
            resp = await fetch_tool(url=url)
            if resp.get('status') == 200:
                results[platform] = f"✅ turn up ({url})"
            else:
                results[platform] = f"❌ not found"
        except:
            results[platform] = f"⚠️ Detection failed"
    return results
```

## Step 4: Information summary template

```markdown
## People image:{Nick name}

### Basic information
- **Nick name**:xxx
- **real name**:xxx(if any)
- **Mail**:xxx
- **Location**:xxx
- **Profession/company**:xxx

### Technical portrait
- **main language**:Python / JavaScript / ...
- **Technology stack preferences**:...
- **Open source contributions**:N a warehouse,M stars
- **areas of interest**:...

### social media
- GitHub: xxx
- Bstand: xxx
- Zhihu: xxx
- ...

### Related information
- Same across platforms ID:xxx
- Known items:xxx
- Historical leaks:xxx
```
