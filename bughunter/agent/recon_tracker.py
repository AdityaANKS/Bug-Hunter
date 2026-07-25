"""Recon dimension tracking helpers for AgentCore."""

from __future__ import annotations

from typing import Any

RECON_MIN_ROUNDS = 8  # ReconnaissancePhasemostLowroundnumber,Lowin this number [DONE] ignored

# ★ Include BOTH tool-result signatures AND natural-language descriptions from notes/confirmed_facts
RECON_DIM_KEYWORDS: dict[str, list[str]] = {
    "server": [
        "Port",
        "port",
        "nmap",
        "open",
        "open",
        "ServeVersion",
        "service",
        "realityip",
        "real ip",
        "cdn",
        "Origin site",
        "Operationsystem",
        "osDetection",
        "ttl",
        "Mediummiddleware",
        "middleware",
        "database",
        "database",
        "mysql",
        "redis",
        "scanning",
        "Port Scan",
        "ipaddress",
        "ipdetection",
        "surviveHost",
        "apache",
        "nginx",
        "tomcat",
        "iis",
        "jetty",
        "Operationsystem",
        "linux",
        "windows",
        "ubuntu",
        "centos",
    ],
    "website": [
        "waf",
        "webapplication firewall",
        "sensitive directory",
        "directory scan",
        "dirsearch",
        "gobuster",
        "Source code leaked",
        ".git",
        ".svn",
        ".ds_store",
        ".env",
        "Backup files",
        ".bak",
        "Stand by",
        "sameip",
        "cpart",
        "Same network segment",
        "Fingerprint",
        "cms",
        "frame",
        "framework",
        "Architecture",
        "technology stack",
        "webFingerprint",
        "website",
        "web",
        "javascript",
        "jsdocument",
        "apiendpoint",
        "apiend",
        "cms",
        "wordpress",
        "dedecms",
        "phpcms",
        "discuz",
        "Log in",
        "Backstage",
        "manage",
        "admin",
        "login",
        "page",
        "url",
        "Table of contents",
        "document",
    ],
    "domain": [
        "whois",
        "Registrant",
        "Registrar",
        "icp",
        "Filing",
        "subdomain",
        "subdomain",
        "dnsRecord",
        "cname",
        "mxRecord",
        "txtRecord",
        "certificate transparency",
        "crt.sh",
        "CertificateInfo",
        "sslCertificate",
        "domain name",
        "dns",
        " registr",
        "registerInfo",
        "icpFiling",
        "subdomain",
        "Substation",
        "crt.sh",
        "Certificate",
    ],
    "personnel": [
        "github_id",
        "followers",
        "following",
        "public_repos",
        "unclecheng",
        "twitter",
        "social eng",
        "social engineering",
        "personnelInfo",
        "Authortrack",
        "person image",
    ],
}


def update_recon_dimension_completion(agent: Any, response: str) -> None:
    """Auto-detect which recon dimensions have been explored.

    Uses signal-weighted sources instead of blindly scanning all round text.
    response Parameters are retained for compatibility with existing callsSignature, but logically do not useOriginalReasoningtext.
    """
    note_text = " ".join(agent.context.state.notes[-15:]).lower()
    fact_text = " ".join(getattr(agent.context.state, "confirmed_facts", [])[-15:]).lower()
    step_text = " ".join(agent.context.state.executed_steps[-15:]).lower()

    for dim, keywords in RECON_DIM_KEYWORDS.items():
        if dim == "personnel":
            if not agent.context.state.recon_dimension4_active:
                continue
            source_text = fact_text
        else:
            source_text = f"{fact_text} {note_text} {step_text}"

        if not source_text.strip():
            continue

        if not agent.context.state.recon_dimensions_completed.get(dim, False):
            if any(kw.lower() in source_text for kw in keywords):
                agent.context.state.mark_recon_dimension(dim)
