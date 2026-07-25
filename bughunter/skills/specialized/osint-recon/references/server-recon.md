# Server information collection reference

## 1. open port & Service version identification

### nmap Common commands
```bash
# Full port scan (slow but comprehensive)
nmap -p- -sV <target>

# Quick scan of common ports
nmap -sV -top-ports 1000 <target>

# UDP port scan
nmap -sU --top-ports 100 <target>

# Service version identification + OS Detection
nmap -sV -O <target>
```

### python_execute way (none nmap hour)
```python
import socket

def scan_port(host, port, timeout=2):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((host, port))
        s.close()
        return result == 0
    except:
        return False

host = "target.com"
common_ports = [21,22,23,25,53,80,110,143,443,445,993,995,1433,1521,3306,3389,5432,6379,8080,8443,9200,27017]
open_ports = [p for p in common_ports if scan_port(host, p)]
print(f"open port: {open_ports}")
```

### Service version identification (Banner Grabbing）
```python
import socket

def grab_banner(host, port, timeout=3):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        # HTTP Service sends request to obtain banner
        if port in [80, 443, 8080, 8443]:
            s.send(b"HEAD / HTTP/1.1\r\nHost: " + host.encode() + b"\r\n\r\n")
        else:
            s.send(b"\r\n")
        banner = s.recv(1024).decode('utf-8', errors='ignore')
        s.close()
        return banner[:200]
    except:
        return None
```

## 2. reality IP probe(CDN The subsequent origin site IP）

### Method one:DNS History
- SecurityTrails (https://securitytrails.com/dns-trials)
- DNSHistory (https://dnshistory.org)
- ViewDNS (https://viewdns.info/iphistory/)
- Netcraft Site Report (https://sitereport.netcraft.com/)

### Method 2: Global Ping
```python
import requests
# Used in many places Ping Serve
urls = [
    f"https://www.whatsmydns.net/#A/{domain}",
    f"https://ping.pe/{domain}",
    f"https://tools.keycdn.com/curl?url={domain}",
]
# If different regions resolve to different IP, indicating the use of CDN
# If multiple places resolve to the same IP,Should IP May be the real source site
```

### Method 3: Extract email headers
- register/Log in to the target website and receive emails
- Check the email header `Received:` Field
- May expose the true identity of the mail server IP

### Method 4: Subdomain name resolution
- CDN Usually only serves the main domain name
- subdomain (e.g. mail.ftp.dev.staging) may be parsed directly to the origin site IP
- Check all subdomains A record, exclude CDN IP

### Method five:SSL Certificate search
```python
import requests
domain = "target.com"
r = requests.get(f"https://crt.sh/?q=%.{domain}&output=json")
if r.status_code == 200:
    # Find certificates associated with different subdomains IP
    for entry in r.json():
        print(entry.get('name_value', ''))
```

## 3. Operating system fingerprint

### TTL infer
| TTL value | Possible operating systems |
|--------|-------------|
| ≈ 64 | Linux / Unix / macOS |
| ≈ 128 | Windows |
| ≈ 255 | Network equipment / old fashioned Unix |

```python
import subprocess
# Ping get TTL
result = subprocess.run(['ping', '-c', '1', host], capture_output=True, text=True)
# Windows: ping -n 1 host
# Extract from output TTL
import re
ttl_match = re.search(r'TTL[=:]\s*(\d+)', result.output, re.I)
if ttl_match:
    ttl = int(ttl_match.group(1))
    if ttl <= 64:
        print("Speculate: Linux/Unix")
    elif ttl <= 128:
        print("Speculate: Windows")
    else:
        print("Speculate: Network equipment")
```

### nmap OS Detection
```bash
nmap -O <target>
# More aggressive (needs root）
sudo nmap -O --osscan-guess <target>
```

## 4. Middleware version identification

### HTTP Response header analysis
```
Server: Apache/2.4.49 (Ubuntu)
Server: nginx/1.18.0
Server: Microsoft-IIS/10.0
X-Powered-By: PHP/7.4.3
X-Powered-By: Express
X-AspNet-Version: 4.0.30319
```

### Error page characteristics
- Apache: default 404 The page contains "Apache" words
- Nginx: default 404 The page contains "nginx" words
- IIS: The default error page contains IIS 版本信息
- Tomcat: 默认 404 页面含 Apache Tomcat 版本

### 特征文件探测
```python
import requests
target = "https://target.com"
# Apache
r = requests.get(f"{target}/server-status")  # 403 = 存在
r = requests.get(f"{target}/server-info")    # 403 = 存在
# Nginx
r = requests.get(f"{target}/nginx_status")   # 可能暴露状态
# Tomcat
r = requests.get(f"{target}/manager/html")   # 管理界面
# IIS
r = requests.get(f"{target}/aspnet_client/") # ASP.NET 特征
```

## 5. 数据库识别

### 端口探测
| 数据库 | 默认端口 | 说明 |
|--------|---------|------|
| MySQL | 3306 | 最常见 |
| PostgreSQL | 5432 | 常见于 Rails/Django |
| MSSQL | 1433 | Windows 环境 |
| MongoDB | 27017 | NoSQL |
| Redis | 6379 | 缓存/消息队列 |
| Oracle | 1521 | 企业级 |
| Memcached | 11211 | 缓存 |

### 错误信息特征
- MySQL: `You have an error in your SQL syntax`
- PostgreSQL: `ERROR: syntax error at or near`
- MSSQL: `Microsoft SQL Server`
- Oracle: `ORA-01756`

### python_execute 检测
```python
import socket

def check_db(host, port, timeout=2):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        # 尝试读取 banner
        s.send(b"\r\n")
        banner = s.recv(1024)
        s.close()
        return banner.hex()[:40], banner[:100]
    except:
        return None, None

db_ports = {
    3306: "MySQL", 5432: "PostgreSQL", 1433: "MSSQL",
    27017: "MongoDB", 6379: "Redis", 1521: "Oracle",
}
for port, name in db_ports.items():
    hex_banner, banner = check_db(host, port)
    if hex_banner:
        print(f"[+] {name} ({port}): {banner}")
```
