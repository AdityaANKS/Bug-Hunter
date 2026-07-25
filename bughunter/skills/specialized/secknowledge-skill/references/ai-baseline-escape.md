# AIFoundation security - Container and sandbox escape practical methodology

> Source: AISSGreen Alliance Large Model Security Intelligence Chain Community | Dismantled From ai-baseline-security.md
> Theme: Container escape/Persistence/Horizontal movement Practical methodology

## Twenty、Container and sandbox escape practical testing methodology

> TargetingAIApplication deployment environment (Docker/Sysbox/Daytona/Kubernetes) systematic escape and isolation testing
> **General container deployment security**: WebApplication Container Deployment Security Check → [web-deployment-security.md §Two](web-deployment-security.md)

### One、Overview of the testing process.

```
Information gathering → Environment identification → Isolation assessment → Escape attempts → Persistent verification → Horizontal movement → Report
```

### Two、Information gathering phase

#### 2.1 Container runtime identification

| Detection Items | Command | Basis for Judgment |
|--------|------|----------|
| Whether in a container | `cat /proc/1/cgroup` | Contain`docker`/`kubepods`/`containerd` |
| DockerFlag file | `ls /.dockerenv` | File exists then isDockerContainer |
| Container runtime type | `cat /proc/1/cgroup \| head` | `sysbox-fs`→Sysbox, `docker`→Docker |
| Kernel version | `uname -r` | MatchingCVEImpact scope |
| User Namespace | `cat /proc/self/uid_map` | `0 0 4294967295`→No isolation(Danger) |
| Capabilities | `cat /proc/self/status \| grep Cap` | Check for dangers after decodingCap |
| Seccomp | `cat /proc/self/status \| grep Seccomp` | 0=disabled, 2=filter |
| AppArmor | `cat /proc/self/attr/current` | `unconfined`→No protection |
| Mount point | `mount \| grep -v overlay` | Detecting sensitive path mounting on the host machine |

#### 2.2 Sysbox Specific detection

| Detection Items | Method | Security impact |
|--------|------|----------|
| CE vs EEVersion | `sysbox-runc --version` Or checkUIDMapping Range | CEShared mapping has cross-tenant risks |
| UIDMapping Exclusivity | `cat /proc/self/uid_map`, CEUsually`0 165536 65536`(Share) | Shared Mapping→Cross-Container Privilege Escalation Possible |
| Virtualization/proc | `ls /proc/sys/net/` | SysboxDegree of virtualization |
| Docker-in-Docker | `docker ps 2>/dev/null` | Inner LayerDockerMay have no security restrictions |
| /dev/kvm | `ls /dev/kvm` | KVMAvailable→Nested virtualization escape |

### Three、Isolation evaluation phase

#### 3.1 Process isolation

```bash
# PID NamespaceCheck
ps aux   # Can see other containers/Host process
ls /proc/*/cmdline   # Enumerate Visible Processes

# IfPID 1Not a containerinitButsystemd/dockerd → Isolation failure
cat /proc/1/cmdline | tr '\0' ' '
```

#### 3.2 Network isolation

```bash
# Network interface
ip addr   # Check network interfaces andIPSegment
ip route  # Routing table, whether it can reach other network segments

# Same subnet scanning(Discover neighboring containers)
for i in $(seq 1 254); do
  (ping -c 1 -W 1 $SUBNET.$i &>/dev/null && echo "$SUBNET.$i alive") &
done; wait

# InternalDNSDetection
cat /etc/resolv.conf
nslookup kubernetes.default.svc.cluster.local 2>/dev/null
```

#### 3.3 File System Isolation

```bash
# Check host file system mounts
mount | grep -E "ext4|xfs|btrfs" | grep -v overlay
findmnt

# Path traversal test
ls -la /var/lib/sysbox/ 2>/dev/null
ls -la /var/lib/docker/ 2>/dev/null
ls -la /run/containerd/ 2>/dev/null

# Symbolic link escape
ln -s /proc/1/root/etc/shadow /tmp/test_escape
cat /tmp/test_escape 2>&1  # If successful→Isolation failure
```

### Four、Escape testing matrix

| Escape Path | Prerequisites | Danger level | Test method |
|----------|----------|----------|----------|
| cgroup release_agent | CAP_SYS_ADMIN + cgroup v1 | Critical | Writerelease_agentExecute host machine commands |
| Docker Socket | /var/run/docker.sockExpose | Critical | PassAPICreate privileged containers |
| /proc/1/root | PID NamespaceNot isolated | Critical | Direct read/write to host machine files |
| Privileged container | --privilegedPattern | Critical | mountHost disk |
| runc fdDisclosure | CVE-2024-21626 | High | Utilize/proc/self/fdAccess to host |
| Dirty Pipe | CVE-2022-0847, 5.8≤kernel≤5.16.11 | High | Overwriting read-only files for privilege escalation |
| OverlayFS | CVE-2023-0386, 5.11≤kernel≤6.2 | High | SUIDFile privilege escalation |
| Sensitive mount | Host path ismountEnter container | High | Write to host machine file |
| CAP_DAC_READ_SEARCH | CapabilityUnrestricted | Medium | open_by_handle_atRead file |
| CAP_SYS_PTRACE | CapabilityUnrestricted | Medium | Inject into host machine process |
| Docker-in-Docker | Inner LayerDockerUnlimited | Medium | Create Privileged Container in Inner Layer |

### Five、Persistence testing

> Validate the feasibility of sandbox cross-session persistence attack (especially suitable for persistent sandboxes likeDaytona)

| Test items | Session1Operation | Session2verification | Expected security outcomes |
|--------|-----------|-----------|-------------|
| .bashrcBackdoor | `echo 'malicious_cmd' >> ~/.bashrc` | Open NewshellCheck whether executed | New sessions do not inherit/Reset |
| Crontab | `echo "* * * * * cmd" \| crontab -` | `crontab -l` | CrontabCleared or unavailable |
| SSHKey | Write~/.ssh/authorized_keys | SSHConnection tests | SSHService Unavailable or Key Cleanup |
| Background processes | `nohup cmd &` | `ps aux \| grep cmd` | Process termination after session closure |
| File poisoning | Workspace writes malicious files | AIWhether to read and execute | AIDo not automatically execute instructions in files |
| Historical residue | InshellInput sensitive commands | `cat ~/.bash_history` | Clear historical commands across sessions |
| Environment Variables | `export SECRET=leaked` | `echo $SECRET` | Environment variables are not retained across sessions |

### Six、Lateral movement testing

```
Inside the container → Internal network service discovery → Database/Cache/APIDirect connection → Other Tenant Sandbox
         ↓
         Cloud metadata service(169.254.169.254) → IAMCredential theft → Cloud resource access
         ↓
         K8s API(kubernetes.default.svc) → PodList/SecretObtain
```

| Objective | Detect command | Utilization method |
|------|----------|----------|
| Cloud metadata | `curl 169.254.169.254` | ObtainIAMTemporary credentials |
| K8s API | `curl -k https://kubernetes.default.svc` | EnumeratePod/ObtainSecret |
| K8s ServiceAccount | `cat /var/run/secrets/kubernetes.io/serviceaccount/token` | AuthenticationK8s API |
| Intranet database | `echo \| nc DB_HOST 5432` | Directly connect to the database |
| Redis | `redis-cli -h REDIS_HOST ping` | Unauthorized access |
| Docker Registry | `curl http://REGISTRY:5000/v2/_catalog` | Pull Sensitive Images |

### Seven、Defense verification.Checklist

```
[ ] Container in a nonrootUser Running(OrUser NamespaceIsolation effective)
[ ] No excessCapabilities(Principle of least privilege: OnlyNET_BIND_SERVICEAnd other requirements)
[ ] Seccomp profileHas been enabled(Nondisabled)
[ ] AppArmor/SELinuxNonunconfined
[ ] /var/run/docker.sockNot exposed
[ ] Not based on--privilegedMode operation
[ ] No host sensitive path mounting(/、/etc、/var/run)
[ ] Kernel version not affected by known escapesCVEImpact
[ ] cgroup v2Orrelease_agentNot writable
[ ] PID NamespaceIsolation effective(Only see own processes)
[ ] Network Policy/Firewall restricts inter-container communication
[ ] 169.254.169.254Metadata service intercepted
[ ] Sensitive Data Between Sessions(history/credentials)Cleared
[ ] Completely clear all user data when the sandbox is destroyed.
[ ] SysboxUseEEVersion or exclusiveUIDMapping
```

---
