"""Bug Hunter Finding Similarity — lightweight semantic deduplication.

pure Python realizedVulnerability DiscoverySemantic deduplication without introducing any external NLP library.

core competencies:
    - normalize_text:        Text normalization (lowercase、Remove extra spaces、URL Pathstandardization)
    - normalize_vuln_type:   VulnerabilityTypenormalization (alias mapping, e.g. "sqli" -> "sql_injection")
    - text_similarity:       based on word set Jaccard Similarity
    - url_similarity:        parse URL post comparison host / path / query parameter
    - finding_similarity:    comprehensive vuln_type / location / description Three-dimensional similarity
    - deduplicate_findings:  Remove duplicates according to the similarity threshold and retain the party with more sufficient evidence.

with existing finding_id hash Deduplication and complementation:hash Deduplication is responsible for exact matching,
This module is responsible for the semantic level"sameVulnerabilitydifferent expressions"fuzzy matching.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Optional
from urllib.parse import parse_qs, urlsplit

if TYPE_CHECKING:
    from bughunter.agent.context import VulnerabilityFinding


# ── VulnerabilityTypenormalized mapping ───────────────────────────────────────────────────

# Alias -> specificationType. Keys are uniformly lowercase、Remove spaces from the form.
_VULN_TYPE_ALIASES: dict[str, str] = {
    # SQL injection
    "sqli": "sql_injection",
    "sqlinjection": "sql_injection",
    "sql injection": "sql_injection",
    "blind sqli": "sql_injection",
    "blind note": "sql_injection",
    "injectionVulnerability": "sql_injection",
    "sql_injection": "sql_injection",
    # XSS
    "xss": "cross_site_scripting",
    "cross-site scripting": "cross_site_scripting",
    "Reflectivexss": "cross_site_scripting",
    "storage typexss": "cross_site_scripting",
    "xsscross-site scripting": "cross_site_scripting",
    "cross site scripting": "cross_site_scripting",
    "cross_site_scripting": "cross_site_scripting",
    # SSRF
    "ssrf": "server_side_request_forgery",
    "Server request forgery": "server_side_request_forgery",
    "server side request forgery": "server_side_request_forgery",
    "server_side_request_forgery": "server_side_request_forgery",
    # RCE
    "rce": "remote_code_execution",
    "command execution": "remote_code_execution",
    "remoteCode execution": "remote_code_execution",
    "command injection": "remote_code_execution",
    "remote code execution": "remote_code_execution",
    "remote_code_execution": "remote_code_execution",
    # LFI / File contains
    "lfi": "local_file_inclusion",
    "File contains": "local_file_inclusion",
    "rfi": "local_file_inclusion",
    "PathTraverse": "local_file_inclusion",
    "File contains/Traverse": "local_file_inclusion",
    "local file inclusion": "local_file_inclusion",
    "local_file_inclusion": "local_file_inclusion",
    # IDOR / ultra vires
    "idor": "insecure_direct_object_reference",
    "ultra vires": "insecure_direct_object_reference",
    "Horizontal ultra vires": "insecure_direct_object_reference",
    "Vertical ultra vires": "insecure_direct_object_reference",
    "insecure direct object reference": "insecure_direct_object_reference",
    "insecure_direct_object_reference": "insecure_direct_object_reference",
    # CSRF
    "csrf": "cross_site_request_forgery",
    "Cross-site request forgery": "cross_site_request_forgery",
    "cross site request forgery": "cross_site_request_forgery",
    # Authentication bypass
    "Authentication bypass": "auth_bypass",
    "unauthorized": "auth_bypass",
    "Unauthorized access": "auth_bypass",
    "Not certified": "auth_bypass",
    "no auth required": "auth_bypass",
    # InfoGive way
    "info disclosure": "info_disclosure",
    "data breach": "info_disclosure",
    "sensitiveInfoGive way": "info_disclosure",
}


def normalize_vuln_type(vuln_type: str) -> str:
    """normalizationVulnerabilityType, mapping common aliases to canonicalName.

    Args:
        vuln_type: OriginalVulnerabilityTypeString (any case)/MediumEnglish/including spaces).

    Returns:
        standardizedType;When there is no matching aliasReturnThe original value after removing spaces and lowercase letters.
    """
    if not vuln_type:
        return ""
    key = re.sub(r"\s+", " ", vuln_type.strip().lower())
    if key in _VULN_TYPE_ALIASES:
        return _VULN_TYPE_ALIASES[key]
    # try underscore/Swap spaces before matching
    underscore = key.replace(" ", "_")
    if underscore in _VULN_TYPE_ALIASES:
        return _VULN_TYPE_ALIASES[underscore]
    spaced = key.replace("_", " ")
    if spaced in _VULN_TYPE_ALIASES:
        return _VULN_TYPE_ALIASES[spaced]
    return underscore


# ── Text normalization and similarity ───────────────────────────────────────────────────

_URL_RE = re.compile(r'https?://[^\s<>"\')\]]+', re.IGNORECASE)
_TOKEN_RE = re.compile(r"[a-z0-9\u4e00-\u9fff]+", re.IGNORECASE)
# Punctuation boundary markers (e.g. [automatic]、[alreadyConfirm]) should be removed before word segmentation to avoid contaminating the word set
_NOISE_TAGS = ("[automatic]", "[alreadyConfirm]", "[Unverified]")


def _normalize_url_path(url: str) -> str:
    """standardization URL:go scheme、remove trailing slash、reserve host+path."""
    try:
        parts = urlsplit(url)
    except ValueError:
        return url.lower()
    host = (parts.hostname or "").lower()
    path = parts.path or ""
    if len(path) > 1:
        path = path.rstrip("/")
    return f"{host}{path}"


def normalize_text(text: str) -> str:
    """Normalized text: lowercase、Merge whitespace、Standardized embedded URL Path.

    Args:
        text: arbitrary free text (Description/evidence/title).

    Returns:
        Normalized text.
    """
    if not text:
        return ""
    result = text
    for tag in _NOISE_TAGS:
        result = result.replace(tag, " ")
    # Will be embedded URL replaced by standardized host+path form
    result = _URL_RE.sub(lambda m: _normalize_url_path(m.group(0)), result)
    result = result.lower()
    result = re.sub(r"\s+", " ", result).strip()
    return result


def _tokenize(text: str) -> set[str]:
    """Divide the normalized text into word sets."""
    return set(_TOKEN_RE.findall(text))


def text_similarity(a: str, b: str) -> float:
    """based on word set Jaccard Similarity.

    Args:
        a: text A.
        b: text B.

    Returns:
        [0.0, 1.0] similarity between them. When both are emptyReturn 1.0;Only one side is emptyReturn 0.0.
    """
    na, nb = normalize_text(a), normalize_text(b)
    if not na and not nb:
        return 1.0
    if not na or not nb:
        return 0.0
    ta, tb = _tokenize(na), _tokenize(nb)
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return inter / union if union else 0.0


def url_similarity(a: str, b: str) -> float:
    """compare two URL of host / path / query Parameter similarity.

    weight: host 0.3 + path 0.4 + query Parameter name set 0.3.
    No URL String fallback is done to the original text Jaccard Text similarity.

    Args:
        a: URL or location string A.
        b: URL or location string B.

    Returns:
        [0.0, 1.0] similarity between them.
    """
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0

    pa, pb = urlsplit(a.strip()), urlsplit(b.strip())
    # If neither of them resembles URL(none scheme None netloc None path separated), by text ratio
    if not (pa.scheme or pa.netloc) and not (pb.scheme or pb.netloc):
        return text_similarity(a, b)

    # host Compare
    ha, hb = (pa.hostname or "").lower(), (pb.hostname or "").lower()
    if not ha and not hb:
        host_sim = 1.0
    elif not ha or not hb:
        host_sim = 0.0
    else:
        host_sim = 1.0 if ha == hb else 0.0

    # path Compare: press "/" Do it in sections Jaccard
    seg_a = {s for s in pa.path.split("/") if s}
    seg_b = {s for s in pb.path.split("/") if s}
    if not seg_a and not seg_b:
        path_sim = 1.0
    elif not seg_a or not seg_b:
        path_sim = 0.0
    else:
        path_sim = len(seg_a & seg_b) / len(seg_a | seg_b)

    # query Parameter name set comparison (ignoring specific values, different paging/ID regarded as the same interface)
    qa = set(parse_qs(pa.query).keys())
    qb = set(parse_qs(pb.query).keys())
    if not qa and not qb:
        query_sim = 1.0
    elif not qa or not qb:
        query_sim = 0.0
    else:
        query_sim = len(qa & qb) / len(qa | qb)

    return host_sim * 0.3 + path_sim * 0.4 + query_sim * 0.3


# ── comprehensive finding Similarity ─────────────────────────────────────────────────

_LOCATION_RE = re.compile(r'(?:https?://[^\s<>"\')\]]+)|(?:/[\w%&=?\-./]+)')


def _extract_location(finding: "VulnerabilityFinding") -> str:
    """from finding of evidence / description MediumExtract the first URL orPathas location."""
    for field in (finding.evidence or "", finding.description or ""):
        if not field:
            continue
        m = _LOCATION_RE.search(field)
        if m:
            return m.group(0)
    return ""


def _vuln_type_similarity(a: str, b: str) -> float:
    """VulnerabilityTypeSimilarity: exact match 1.0, matching after normalization 0.8,otherwise 0.0."""
    ra, rb = (a or "").strip().lower(), (b or "").strip().lower()
    if ra and rb and ra == rb:
        return 1.0
    na, nb = normalize_vuln_type(a), normalize_vuln_type(b)
    if na and nb and na == nb:
        return 0.8
    return 0.0


def finding_similarity(a: "VulnerabilityFinding", b: "VulnerabilityFinding") -> float:
    """Comprehensive comparison of the twoVulnerability Discoverysimilarity.

    Dimension weight:
        - vuln_type:    0.3(exact match 1.0 / normalized matching 0.8)
        - location/URL: 0.4(from evidence/description Do it after extraction url_similarity)
        - description:  0.3(title+Descriptionthe text of Jaccard)

    Args:
        a: Vulnerability Discovery A.
        b: Vulnerability Discovery B.

    Returns:
        [0.0, 1.0] comprehensive similarity between them.
    """
    type_sim = _vuln_type_similarity(a.vuln_type, b.vuln_type)

    loc_a, loc_b = _extract_location(a), _extract_location(b)
    if not loc_a and not loc_b:
        # Neither has a clear location — This dimension is not comparable and is regarded asMediumSex (no points added or deducted)
        loc_sim = 0.5
    else:
        loc_sim = url_similarity(loc_a, loc_b)

    desc_a = f"{a.title} {a.description}".strip()
    desc_b = f"{b.title} {b.description}".strip()
    desc_sim = text_similarity(desc_a, desc_b)

    return type_sim * 0.3 + loc_sim * 0.4 + desc_sim * 0.3


# ── Evidence strength comparison and deduplication ───────────────────────────────────────────────────

_EVIDENCE_LEVEL_RANK = {"L1": 1, "L2": 2, "L3": 3, "L4": 4}
_LIFECYCLE_RANK = {
    "rejected": 0,
    "candidate": 1,
    "pending_verification": 2,
    "needs_manual_review": 3,
    "verified": 4,
}


def _evidence_strength(finding: "VulnerabilityFinding") -> tuple:
    """calculate finding the strength of evidence used to decide which to retain in case of duplication.

    SortKey (the bigger the stronger):
        1. Verified first (verified=True)
        2. lifecyclegrade
        3. Level of evidence L1-L4
        4. evidence Text length (more detailed evidence)
    """
    return (
        1 if finding.verified else 0,
        _LIFECYCLE_RANK.get(finding.lifecycle_status, 1),
        _EVIDENCE_LEVEL_RANK.get(finding.evidence_level, 1),
        len(finding.evidence or ""),
    )


def deduplicate_findings(
    findings: list["VulnerabilityFinding"], threshold: float = 0.75
) -> list["VulnerabilityFinding"]:
    """rightVulnerability DiscoveryThe list is semantically deduplicated and the side with more evidence is retained..

    Traverse findings, for each new finding with reserved findings Compare one by one,
    If the similarity exceeds the threshold, it is determined to be a duplicate; the evidence strength is retained moreHighwho.

    Args:
        findings: OriginalVulnerability Discoverylist.
        threshold: Similarity threshold, default 0.75.

    Returns:
        The list after deduplication maintains the relative order of first occurrence.
    """
    kept: list["VulnerabilityFinding"] = []
    for cand in findings:
        dup_index: Optional[int] = None
        for idx, existing in enumerate(kept):
            if finding_similarity(cand, existing) >= threshold:
                dup_index = idx
                break
        if dup_index is None:
            kept.append(cand)
            continue
        # commandRepeat: Keep the one with stronger evidence
        if _evidence_strength(cand) > _evidence_strength(kept[dup_index]):
            kept[dup_index] = cand
    return kept
