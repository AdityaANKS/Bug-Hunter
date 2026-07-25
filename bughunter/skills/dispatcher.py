"""Bug Hunter Skill Dispatcher — match user intents to appropriate Skills."""

from __future__ import annotations

from typing import Any, Optional

from bughunter.skills.loader import list_core_skills, list_specialized_skills, load_skill_by_name

# ── Intent → Skill mapping ─────────────────────────────────────────

SKILL_INTENT_MAP: dict[str, list[str]] = {
    # Core skills
    "Penetration Testing|pentest|full process|test this": ["pentest-flow"],
    "Reconnaissance|reconnaissance|recon|Port Scan|scanningPort|subdomain": ["recon"],
    "Vulnerability Discovery|Vulnerabilityscanning|vulnerability|What's thereVulnerability": ["vuln-discovery"],
    "Exploitation|exploit|poc|useVulnerability": ["exploitation"],
    "Post-Exploitation|post-exploitation": ["post-exploitation"],
    "Report|report|Generate report": ["reporting"],
    "bypasswaf|wafbypass|waf bypass": ["waf-bypass"],
    # Specialized skills — original
    "webpentest|web penetration|website testing|webtest|web penetration testing|webpenetration": ["web-pentest"],
    "Android|android|apk|apptest": ["android-pentest"],
    # Specialized skills — from Sec-Skill
    "Reverse|reverse|Signaturerecover|burpreplay|jsSignature|Client reverse engineering|request chain|replay|Signature": ["client-reverse"],
    "Capture packets|packet|frida|jadx|hook|ssl pinning|scrcpy": ["client-reverse"],
    "BrowserSignature|Climb backward|antibot|tokengenerate|cookieJump": ["client-reverse"],
    "webHighclass|injection|sqlinjection|xss|ssrf|ssti|xxe|command injection|Deserialization|rce|remoteCode execution": [
        "web-security-advanced"
    ],
    "cors|graphql|websocket|oauth|request smuggling|jwt|csrf|Prototype contamination": ["web-security-advanced"],
    "CertificationVulnerability|logicVulnerability|ultra vires|idor|payment logic|File upload|Pathtime travel": ["web-security-advanced"],
    "aiSafety|mcpSafety|promptinjection|Toolabuse|agentSafety|model safety|aisecurity|mcpsecurity|ai security|mcp security": ["ai-mcp-security"],
    "aiPentest|Large model security|llmSafety|prompt injection|tool abuse": ["ai-mcp-security"],
    "mcppoison|skillssupply chain|character escape|data breach|promptleakage": ["ai-mcp-security"],
    "IntranetPentest|Lateral movement|Elevate privileges|Endurance|tunnel|acting|domainPentest|adattack|intranet|internal network": ["intranet-pentest-advanced"],
    "adcs|exchange|sharepoint|mimikatz|kerberoasting|dcsync|pth": ["intranet-pentest-advanced"],
    "Credential theft|bloodhound|frp|chisel|ligolo|amsibypass": ["intranet-pentest-advanced"],
    "Tool|Order|Encoding|Decoding|reverse shell|Password attack|hashcat": ["pentest-tools"],
    "sqlmap|nmap|nuclei|ffuf|burp|impacket|crackmapexec": ["pentest-tools"],
    "quick check|Bypass reminder|Quick verification|checklist|Checklist|fast xss|payload": ["rapid-checklist"],
    "payloadEncyclopedia|quick check|quick check card|Quick recall": ["rapid-checklist"],
    # SecKnowledge: practical CTF/SRC/Web+AI security testing knowledge base
    "src vulnerability|src mining|public testing|mending the sky|edusrc|cnvd|src": ["secknowledge-skill"],
    "wooyun|dark clouds|prophet|l1-l4|gaarm|owasp wstg|owasp llm|owasp asi": ["secknowledge-skill"],
    "Practical security testing|Security testingKnowledge base|web+ai|web aiSafety|aiApplication security testing": [
        "secknowledge-skill"
    ],
    "ctf src|ctfVulnerabilitydig|ctfcomprehensivePentest|ctf ai|ctf mcp|ctf agent": ["secknowledge-skill"],
    # Crypto toolkit
    "Encoding|Decoding|base64|base32|hex|urlEncoding|encryption|Decrypt|Hash|hash": ["crypto-toolkit"],
    "md5|sha|aes|des|rsa|jwt|rot13|caesar|morse|fence": ["crypto-toolkit"],
    "base64Decoding|base64Encoding|hexDecoding|urlDecoding|unicodeDecoding|htmlDecoding": ["crypto-toolkit"],
    "cryptography|crypto|cipher|decrypt|encrypt|encode|decode": ["crypto-toolkit"],
    "Moore code|Caesar cipher|virginia|bacon code|base58": ["crypto-toolkit"],
    # ── CTF specialized skills ──────────────────────────────────────
    # ctf-web: CTF Web attackKnowledge base
    "ctf|ctf|flag|weak comparison|Space bypass|Regular bypass|rce|Code audit|evalbypass|highlight_file": ["ctf-web"],
    "0e|md5bypass|preg_matchbypass|Typebypass|type juggling|weakType": ["ctf-web"],
    "Encyclopedia|No echo|blind rce|Error 500 (Server Error)!!1500.That’s an error.There was an error. Please try again later.That’s all we know.|phpCode audit|sstiinjection": ["ctf-web"],
    # ctf-crypto: CTF cryptographic attackKnowledge base
    "rsaattack|small exponent|common mode attack|wiener|coppersmith|padding oracle": ["ctf-crypto"],
    "eccattack|boy group|discrete logarithm|ecdsa|ed25519|pohlig-hellman": ["ctf-crypto"],
    "lfsr|lcg|prng|mt19937|Random number prediction|stream cipher": ["ctf-crypto"],
    "lwe|grid attack|lll|cvp|svp|lattice reduction": ["ctf-crypto"],
    "classical cipher|virginia|caesar|fence|Replace password|frequencyAnalysis": ["ctf-crypto"],
    # ctf-misc: CTF MiscellaneousKnowledge base
    "pyjail|pythonsandbox|jailescape|sandbox_escape|python jail": ["ctf-misc"],
    "bashjail|bashsandbox|restricted shell|rbashescape": ["ctf-misc"],
    "Encodingchain|multi-layerEncoding|Miscellaneous|misc|steganography|stego": ["ctf-misc"],
    "ctfd|ctfplatform|flagsubmit|Question download": ["ctf-misc"],
    # ── OSINT specialized skill — refined routing ───────────────────
    # osint-recon: Full-dimension recon (OSINT + social engineering)
    # Triggered only when user explicitly mentions social engineering / OSINT / author tracking
    "social engineering|social worker|Authortrack|Character tracking|Targetimage|person image": ["osint-recon"],
    "Cross-platform|usernameSearch|Identity association|githubtrack|bilibilitrack": ["osint-recon"],
    # Full/deep recon — trigger osint-recon for comprehensive 4-dimension collection
    "Comprehensive reconnaissance|deep reconnaissance|wholeReconnaissance|comprehensiveReconnaissance|deep collection|Gather basicsInfo": ["osint-recon"],
}


class SkillDispatcher:
    """Dispatches user input to the most appropriate Skill."""

    def dispatch(self, user_input: str) -> Optional[dict[str, Any]]:
        """Match user input to a Skill and load it.

        Args:
            user_input: Natural language input from the user.

        Returns:
            Loaded skill dict, or None if no match found.
        """
        input_lower = user_input.lower()

        # Score each skill based on keyword matches
        scores: dict[str, float] = {}

        for pattern, skill_names in SKILL_INTENT_MAP.items():
            keywords = pattern.split("|")
            match_count = sum(1 for kw in keywords if kw in input_lower)
            if match_count > 0:
                for skill_name in skill_names:
                    score = match_count / len(keywords)
                    # Specialized skills get a 1.5x boost over core skills
                    # to ensure more specific matches win over generic ones
                    skill = load_skill_by_name(skill_name)
                    if skill and skill.get("format") == "directory":
                        score *= 1.5
                    scores[skill_name] = scores.get(skill_name, 0) + score

        if not scores:
            # Default to pentest-flow
            return load_skill_by_name("pentest-flow")

        # Load the highest-scoring skill
        best_skill_name = max(scores, key=scores.get)  # type: ignore[arg-type]
        return load_skill_by_name(best_skill_name)

    def list_all_skills(self) -> list[dict[str, str]]:
        """List all available skills with name and description."""
        skills = []
        for name in list_core_skills():
            skill = load_skill_by_name(name)
            if skill:
                skills.append(
                    {
                        "name": skill["name"],
                        "description": skill.get("description", ""),
                        "type": "core",
                        "format": skill.get("format", "flat"),
                        "references": str(len(skill.get("references", []))),
                    }
                )
        for name in list_specialized_skills():
            skill = load_skill_by_name(name)
            if skill:
                skills.append(
                    {
                        "name": skill["name"],
                        "description": skill.get("description", ""),
                        "type": "specialized",
                        "format": skill.get("format", "flat"),
                        "references": str(len(skill.get("references", []))),
                    }
                )
        return skills
