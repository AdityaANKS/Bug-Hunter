---
name: web-security-advanced
description: WebAdvanced Security Testing — Injection attack family、Protocol security、Authentication and logical vulnerabilities、File and Deployment Security、ModernWebAttack surface, including fullPlaybook
---

# Web Advanced Security Testing Skill

When the target is Web Application、API、Use this for gateway or browser-facing services when systematic vulnerability testing is required Skill.

**Precondition**: If the request is still controlled by the client and replay is unstable, first use `client-reverse` Skill.

## CTF Scenario routing

> When the target is. CTF Topic (already known to have flagWhen needing to bypass specific filters), prioritize the use of `ctf-web` Skill Obtain specific bypass values and payload:

| CTF Scene | Route to ctf-web | Reference documents |
|---------|---------------|---------|
| PHP Weak comparison/Type bypass | `ctf-web` | `references/php-bypass-cheatsheet.md` |
| Command injection space bypass | `ctf-web` | `references/command-injection-bypass.md` |
| eval Echo/No echo. | `ctf-web` | `references/eval-and-rce-techniques.md` |
| PHP Code auditing | `ctf-web` | `references/php-code-audit-checklist.md` |
| SSTI Injection Chain | `ctf-web` | `references/ssti-injection-chains.md` |
| Deserialization exploit chain | `ctf-web` | `references/deserialization-playbook.md` |
| File upload → RCE | `ctf-web` | `references/file-upload-to-rce.md` |

**This Skill Focus on penetration testing methodology**,CTF Practical bypass values and payload Please refer to the template. `ctf-web`.

## Scenario routing

| Attack surface type | Preferred reference |
|-----------|---------|
| Parameter Injection (SQLi/XSS/Command execution/SSTI/XXE) | `references/web-injection.md` |
| Agreement Security (CORS/GraphQL/WebSocket/OAuth/Request smuggling) | `references/web-modern-protocols.md` |
| Authentication and logic (IDOR/Overstepping authority/Payment/Password reset/Authentication Bypass) | `references/web-logic-auth.md` |
| Files and infrastructure (upload/traverse/Contain/Deployment/Cache/CDN/Cloud) | `references/web-file-infra.md` |
| Deployment security | `references/web-deployment-security.md` |

## Testing Process

### 1. Input validation testing
- SQL Injection: Boolean/Time/Error Reporting/Union/Stacking
- XSS: Reflection/Storage/DOM/CSP Bypass
- Command injection: delimiter bypass、Encoding bypass
- SSTI: Template Engine Recognition + RCE Chain
- XXE: Entity injection、OOB Data takeout
- Deserialization:Java/PHP/Python Chain

### 2. Authentication and session testing
- Default credentials、Brute force cracking
- Session management vulnerability (fixed/Hijack/Unsafe Cookie)
- JWT Security (algorithm tampering/Key cracking/noneAlgorithm)
- OAuth/OIDC Configuration defects
- MFA Bypass

### 3. Logic vulnerability testing
- Privilege escalation (horizontal/Vertical)
- Business logic bypass (payment/Coupons/Voting)
- Race condition
- IDOR(Insecure direct object reference)

### 4. Protocol security testing
- CORS Configuration error
- GraphQL Introspection/Injection
- WebSocket Authentication and injection
- HTTP Request smuggling
- SSRF(Intranet Detection/Cloud Metadata)

### 5. File and Deployment Security
- File upload bypass
- Path traversal
- LFI/RFI
- CDN/Cache poisoning
- Supply chain attack
- Cloud security configuration

## Reference documents

- `references/03-web-security-integrated.md` — Web Security integration reference
- `references/web-injection.md` — Injection attack detailed reference
- `references/web-modern-protocols.md` — Modern protocol security
- `references/web-logic-auth.md` — Authentication and logical vulnerabilities
- `references/web-file-infra.md` — File and infrastructure security
- `references/web-deployment-security.md` — Deployment security
- `references/web-ai-attack-map.md` — Web With AI Attack mapping
- `references/web-playbook-*.md` — Various Specialties Playbook(23 Piece)
