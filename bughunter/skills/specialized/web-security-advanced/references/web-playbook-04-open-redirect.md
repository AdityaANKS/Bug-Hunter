# Open redirect.
English: Open Redirect
- Entry Count: 3
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Basic Open Redirect
- ID: redirect-basic
- Difficulty: beginner
- Subcategory: Basics
- Tags: redirect, url, phishing
- Original Extracted Source: original extracted web-security-wiki source/redirect-basic.md
Description:
URLRedirect vulnerability exploitation
Prerequisites:
- Target parameter controls the redirect address
Execution Outline:
1. Direct jump
2. Bypass Verification
3. Slash bypass
## Redirection bypass
- ID: redirect-bypass
- Difficulty: intermediate
- Subcategory: Bypass
- Tags: redirect, bypass
- Original Extracted Source: original extracted web-security-wiki source/redirect-bypass.md
Description:
Open redirection bypass technique
Prerequisites:
- Redirect parameters exist
Execution Outline:
1. URLCode
2. @Symbol
3. Backslash
## Redirect toSSRF
- ID: redirect-ssrf
- Difficulty: intermediate
- Subcategory: SSRF
- Tags: redirect, ssrf
- Original Extracted Source: original extracted web-security-wiki source/redirect-ssrf.md
Description:
Using open redirect vulnerabilities as a springboard toSSRFProbe leading to internal network, bypassSSRF'sURLWhitelist/Blacklist restrictions
Prerequisites:
- Target has an open redirect(Open Redirect)Vulnerability
- Target existsSSRFFunction points(URLParameters/WebhookEtc.)
- SSRFFiltering only checks initialURLWithout tracking redirects
Execution Outline:
1. Identify open redirect points
2. Bypass through redirectionSSRFFilter
3. Short links andDNSRebinding Assistance
4. Full exploitation chain: Redirection→SSRF→Internal network detection

