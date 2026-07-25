---
name: vuln-discovery
description: Vulnerability discovery process — Scan for vulnerabilities based on information collection results
---

# Vulnerability discovery Skill

Based on the information collection results, security vulnerabilities in the target are systematically discovered.

## Execution steps

### 1. known CVE match
- Search for correspondence based on identified service version CVE
- Prioritize attention Critical/High level
- Record CVE ID、Affected version、Conditions of use

### 2. Web Vulnerability Scan
- SQL Injection detection
- XSS Detection (reflective type/storage type/DOMtype)
- SSRF Detection
- LFI/RFI Detection
- Command injection detection
- File upload vulnerability detection

### 3. Configuration defect detection
- Default Credentials Test
- Information leakage detection
- Unauthorized access detection
- CORS Configuration detection
- HTTPS Configuration detection

### 4. output
- List of vulnerabilities (type、severity level、URL、parameter、Verification method)
