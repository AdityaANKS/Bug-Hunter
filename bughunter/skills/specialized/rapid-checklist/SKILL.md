---
name: rapid-checklist
description: Penetration quick search andPayload — FastPayloadFamily、Bypass reminders、Verification order、Common test cards, suitable for quickly finding known testing directions
---

# Penetration quick search and Payload Skill

**Use only after the routing is clearly defined**. This Skill Used for quick lookup, not a substitute for methodology or workflow selection.

## Usage Scenarios

- Quickly recall what to look at first for a certain type of vulnerability or blocking point
- Quick filter Payload Family、Bypass direction and validation order
- Quick confirmation AI、MCP、Container、WebSocket、JWT、File、Authentication、SSRF And common test cards
- From"I know what to test"Enter"Where do I start with which type of validation"

## Not applicable scenarios

- Alternate Scenario Diversion → Use `pentest-flow`
- Alternative methodology decision → Use the corresponding specialty Skill
- Request not captured、Replay blind test when unstable → First use `client-reverse`

## CTF Special quick reference

> CTF Use the topic priority `ctf-web` / `ctf-crypto` / `ctf-misc` SkillThe following are quick cards:

| Scene | Quick positioning |
|------|---------|
| PHP Weak comparison → 0e Start MD5 Value | `ctf-web` → `php-bypass-cheatsheet.md` |
| Command injection space bypass → ${IFS}/$IFS$9/< | `ctf-web` → `command-injection-bypass.md` |
| eval No echo. → Write file/DNS Takeaway | `ctf-web` → `eval-and-rce-techniques.md` |
| RSA Small exponent → Cube root/Coppersmith | `ctf-crypto` → `rsa-attacks-cheatsheet.md` |
| Python Jail → `__import__`/func_globals | `ctf-misc` → `python-jail-escape.md` |
| Encoding Chain → base64→hex→ROT13 Multi-layer | `ctf-misc` → `encoding-chain-reference.md` |

## Quick route card

### Web Injection / Output execution
- SQLi → `'`, `"`, `)`, Boolean Difference, Time difference, Error reporting differences
- XSS → `<script>`, `<img onerror>`, `javascript:`, DOM sink
- Command injection → `;id`, `|id`, `` `id` ``, `$(id)`
- SSTI → `{{7*7}}`, `${7*7}`, `<%= 7*7 %>`, Template engine fingerprint
- XXE → `<!ENTITY>`, Parameter entity, OOB Takeaway

### Authentication / Logic / Token
- JWT → noneAlgorithm, Algorithm tampering, Key cracking, jku/x5u Injection
- CSRF → Missing. Token, Token Predictable, Referer Verification defects
- IDOR → Modify ID Parameters, Batch traversal
- Payment Logic → Amount tampering, Negative number, Race condition

### Browser signature / Anti-crawling
- First use `client-reverse` Stable replay
- Phase: locate → recover → runtime → validation

### Android runtime / Signature recovery
- First use `client-reverse` runtime-first Path
- Only unable to capture packets/Encryption/Reverse when unable to replay

### AI / MCP
- Prompt Injection → Direct/Indirect/CoT Interference
- Tool Abuse → MCP Poisoning/Instruction override
- Identity escape → Role Boundary Crossing/Permission drift

### Intranet / AD
- First use `intranet-pentest-advanced`
- Review when the tool is uncertain `pentest-tools`

## Reference documents

- `references/08-rapid-checklists-and-payloads.md` — Quick check and Payload Integrate Reference
- `references/payloads.md` — Payload Detailed Collection
- `references/testing-methodology.md` — Testing methodology
