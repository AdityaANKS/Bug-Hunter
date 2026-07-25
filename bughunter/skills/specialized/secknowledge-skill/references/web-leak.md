# Web Security - Information leakage.

> Source: WooYun Vulnerability database | Dismantled From web-file-infra.md

## Three、Information leakage.

### 3.1 Nature of vulnerabilities

```
Essence of Information Disclosure: Attack surface exposure -> Trust chain break -> Depth penetration
regularity: A single leak point can lead to the collapse of the entire trust chain
      Source code -> Configuration -> Database -> Intranet -> All compromised
```

### 3.2 Sensitive file path dictionary

Version Control Leakage:

```bash
# GitDisclosure (Detection priority highest)
/.git/config          # Contains Remote Repository Address
/.git/HEAD            # Current branch
/.git/index           # Staging area index
/.git/logs/HEAD       # Operation log

# SVNDisclosure
/.svn/entries         # SVN 1.6And below
/.svn/wc.db           # SVN 1.7+ SQLiteDatabase

# Exploitation tools: dvcs-ripper, GitHack, svn-extractor
```

Backup file leakage:

```bash
# Compressed package backup (530Example hit)
/wwwroot.rar | /www.zip | /web.rar | /backup.zip | /site.tar.gz
/{domain}.zip | /{domain}.rar

# SQLBackup (136Example hit)
/backup.sql | /database.sql | /db.sql | /dump.sql

# Configuration backup (101Example hit)
/config.php.bak | /web.config.bak | /.env.bak
/config_global.php.bak
```

Configuration file leakage:

```bash
# Generic
/.env | /.env.local | /.env.production
/config.yml | /config.json | /appsettings.json

# PHP
/config.php | /include/config.php | /data/config.php

# Java/Spring
/WEB-INF/web.xml | /WEB-INF/classes/application.properties
/WEB-INF/classes/jdbc.properties

# .NET
/web.config | /connectionStrings.config
```

Probe/Debug/Log file:

```bash
# Probe file
/phpinfo.php | /info.php | /test.php | /probe.php

# Log file
/ctp.log | /logs/ctp.log | /debug.log | /storage/logs/

# Management interface
/phpmyadmin/ | /pma/ | /adminer.php
/swagger-ui.html | /api-docs
/actuator/env                    # Spring Boot
```

### 3.3 Detection methodology

```
Phase 1 Passive collection: Response headers(Server/X-Powered-By) -> Error page -> robots.txt -> Source Code Comments/JS
Phase 2 Targeted probing: Version control(.git/.svn) -> Backup Files(Domain name/Date) -> Sensitive paths
Phase 3 Search Engine: Google HackingSyntax
```

Google HackingQuick lookup:

```
site:target.com filetype:sql | filetype:bak | filetype:zip
site:target.com filetype:env | filetype:log
site:target.com inurl:.git | inurl:.svn
site:target.com inurl:phpinfo | intitle:phpinfo
site:target.com "db_password" | "mysql_connect"
```

### 3.4 Information Utilization Chain

```
Source code leakage   -> Configuration file -> Database credentials -> Database takeover -> Server privilege escalation
Version control   -> Source Code Auditing -> SQLInjection and so on  -> Administrative privileges   -> File uploadgetshell
Configuration leakage   -> DBConnection string -> Database    -> User data   -> Business takeover
Log leakage   -> Session  -> Identity hijacking  -> Business data   -> Horizontal movement
APIInterface    -> Credentials/Password -> Decrypt     -> Batch Control   -> Comprehensive penetration
Third-party credentials -> SMS./OSS -> Verification code    -> Account takeover   -> Data leakage
```

### 3.5 Defensive measures

NginxSecurity Configuration:

```nginx
location ~ /\.(git|svn|env|htaccess|htpasswd) { deny all; return 404; }
location ~ \.(bak|sql|log|config|ini|yml)$ { deny all; return 404; }
location ~* /(backup|bak|old|temp|test|dev)/ { deny all; return 404; }
autoindex off;
server_tokens off;
```

ApacheSecurity Configuration:

```apache
<FilesMatch "\.(git|svn|env|bak|sql|log|config)">
    Order Allow,Deny
    Deny from all
</FilesMatch>
Options -Indexes
ServerSignature Off
```

CI/CDIntegration: Scan sensitive files before deployment -> Forbidden.git/.svnDeployment -> Configuration file encryption

---

