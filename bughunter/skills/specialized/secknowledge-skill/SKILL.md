---
name: secknowledge-skill
description: |
  Web+AI Security testing knowledge base. Fusion WooYun 88,636 Case + Prophet L1-L4 Methodology + GAARM 150 Risk
  + OWASP Top 10 (LLM/ASI/WSTG).
  TRIGGER when The task is practical security testing: penetration testing、Vulnerability Mining/Utilize、Red team offense and defense、Security audit (SAST/DAST)、
  CTF、AI/LLM Security testing (Prompt Injection/Jailbreak/MCP/Agent/Sandbox escape). Users explicitly provide testing targets
  (URL/Code/Model/Agent Architecture) And the intent is."Testing/Audit/Exploit vulnerabilities/Utilize".
  DO NOT trigger:
  - Security concept discussion ("What is XSS"、"SQL What is the injection principle")→ General Q&A
  - Non-Security Nature code review / debug / Performance optimization → code-audit-skill or other
  - Fix Syntax Errors / Business logic bug → General programming assistance
  - Pure Web White box code audit (complete project directory / Source-Sink Taint analysis)→ code-audit-skill
  - Reference only CVE Document lookup by number → WebSearch
  Boundary Details: CTF Short code snippet + Utilization ideas → This Skill; Complete project directory + System white-box audit → code-audit-skill
---

# Web and AI Security testing knowledge base

> Knowledge source: WooYun 88,636 Vulnerability × Prophet 5,600+ Document × GAARM 150 AI Risk × OWASP
> Architecture: SKILL.md(Routing)→ references/(Load by scenario)

## BugHunter Integration instructions

- This Skill Integrated from `Pa55w0rd/secknowledge-skill`, in BugHunter As `secknowledge-skill` specialized skill Use; upstream declared as MIT License.
- CTF/SRC Scene preloading `references/bughunter-ctf-src-routing.md` Determine data entry points, then load by vulnerability type `web-*`、`ai-*`、`testing-methodology.md` Or `gaarm-risk-matrix.md`.
- With BugHunter Existing skill collaboration:CTF Single question technique priority combination `ctf-web`/`ctf-crypto`/`ctf-misc`,SRC Use this for practical vulnerability mining priority Skill Methodology、Case mapping、Risk matrix and evidence constraints.
- Retain upstream authorization boundaries during output、Citation labeling and"Assume/Confirm"Distinction; failure to derive from reference Supporting evidence payload、CVE、GAARM/OWASP The number must be clearly marked as unchecked.

## Trigger conditions

**Trigger conditions (AND Combination)**:
1. User intent is**Execute**Security testing (penetration/Digging Holes/Utilize/Audit) — Non-discussion/Learning
2. Provided**Specific target**:URL、Interface、Code snippet、Model/Agent Architecture、MCP Configuration — Non-abstract issues
3. Task**Involved in one of the following areas**:
   - Web: SQL Injection/XSS/Command execution/Overstepping authority/File upload/SSRF/Deserialization/XXE/GraphQL/HTTP Smuggling
   - AI: Prompt Injection/Jailbreak/MCP Poisoning/Agent Abuse/RAG Poisoning/Sandbox escape/Model theft
   - Bypass: WAF/Content filtering/Guard Rails Bypass

**Do not trigger**(Any hit routes elsewhere):
- Concept explanation:"What is…"、"…Principle"、"…How to defend" → General Q&A
- Non-secure code review:"review Code quality"、"Optimize Performance" → Common code review
- Business bug: Syntax error、Null Pointer、Business logic errors (non-security logic)→ Common debug
- **Deep white-box code auditing**(Source-Sink Taint propagation、AST Analysis)→ code-audit-skill
- Check CVE Document、Tool documentation → WebSearch/Context7

**Ambiguity Handling**When the target and intent are unclear, ask first:"What is the goal? Do you want to conduct penetration testing? / Code auditing / Or understand the concept?"

## Code of conduct (valid for the entire session, not relaxed due to conversation length)

1. ❗ **All Payload/CVE Number/Risk number must be referenced reference Specific chapter of the file** — Self-check before each output. Not in reference Marked uniformly in "UNABLE TO CITE", fabrications are prohibited.
2. ❗ **Distinction"Vulnerability assumptions"With"Vulnerability confirmation"** — Potential risks inferred based on methodology → Annotation `Hypothesis (needs verification)`; with clear evidence of → Annotation `Confirmed (evidence: …)`. Obfuscation is prohibited.
3. ❗ **Authorization boundary** — Any exploitation step output must confirm CTF/Authorized penetration/Personal environment. Without authorized context, only analytical outputs are provided, not complete ones that can be directly weaponized Payload.

## Illusion protection and source citation

| Content type | Correct Output | Output forbidden |
|---------|---------|---------|
| CVE Number | Cite specific reference Files and chapters, or tags "UNABLE TO CITE — Suggestions WebSearch Verify" | Fabrication CVE-YYYY-NNNN |
| Payload | From `references/web-*.md` Or `references/ai-*.md` Inside payload Chapter References | Write by impression payload |
| GAARM Risk number | Referencing `references/gaarm-risk-matrix.md` | Self-generated numbers |
| OWASP Entries | LLM01-10 / ASI01-10 / WSTG-* Referencing `testing-methodology.md §10.x` | Rewrite number meanings |
| Tool/Command | Used only in reference Appeared in, or clearly marked in "Generic commands (not in reference Verification in the" | Forged tool parameters |
| No search results | "UNABLE TO ASSESS:reference This scenario is not covered, it is recommended WebSearch" | Conjectured as a conclusion based on experience |

**Label grading**:
- `[Referencing]` — From reference Specific chapter (must include file:section)
- `⚠️ General Knowledge` — Not in this Skill reference Intermediate verification, for reference only
- `💡 Suggestions` — Methodological Reasoning, Non-factual Claims

## Output constraints

Prohibit output:
- Opening Remarks:"Let me analyze…" / "First, we need to…" / "According to your needs…"
- Tool Call Description:"I will use Read Tool read XX"
- Reiteration of known information (what the user just said) URL、Target Type)
- No source citation Payload Or CVE Number
- Complete weaponization chain in unauthorized scenarios.

Output limit:
- Single Response ≤ 3 Suggestions for individual levels (avoid information inflation)
- Payload Example ≤ 5 Item./Vulnerability types (full list reference). reference)
- Use tables/Quick lookup format, prohibit long paragraph descriptions

## Tool priority (this Skill For personal use)

| Operation | Preferred | Downgrade conditions | Downgrade tools. |
|------|------|---------|---------|
| Read reference | Read | Read Failure | Bash cat |
| Search keywords/CVE | Grep (reference Inside) | Continuous 2 Misses times | WebSearch |
| Code audit objectives | Delegation code-audit-skill | — | — |

Single timeout ≠ Unavailable, must retry 1 Can only be downgraded after

## Usage Process

**Dependency chain constraints (through three steps, mandatory)**:
- Step 2 Input. == Step 1 's"Has been located reference List", no new files can be added
- Step 3 Reference collection. ⊆ Step 2 's"Loaded list", forbidden in Step 3 Research again reference
- Step 3 Checkpoint Reference counting in Step 2 Checkpoint Corresponding Source Found in

**Step 1: Target classification + reference Location**
- Judgment:Web / AI / Web+AI Mixed / Container sandbox
- Localization: according to"Scene navigation index"Find the corresponding reference File, noted as a list `L1`

Failure downgrade:
- Target information insufficient for classification → Trigger ambiguity clarification issues, do not guess; default classification as "Web+AI Mixed"
- The scene navigation index does not cover this scene → Annotation "UNABLE TO CITE: Scene {X} Not in the index", list `L1` is empty, enter Step 3 Can only output methodological-level suggestions at that time.

✅ Checkpoint: `Step 1 Complete: Target type={X}, |L1| == Scenario navigation index matching count = {N}`

**Step 2: Load on demand Step 1 Located reference(Lazy Loading)**
- Input.: Step 1 Output list `L1`; The loading set for the current step is `L2`, must meet `L2 ⊆ L1`
- Each load 1 files, single time ≤ 1000 tokens; exceeding budget reference(such as `ai-identity-app.md` 906 Line、`ai-data-app.md` 903 Row) must be used Read offset/limit Or Grep Position first and then read
- Prohibited to load unlisted in this step `L1` File in.

Failure downgrade:
- Read Failure → Retry 1 Times → Still failed to use Bash cat → All failed → Annotation "UNABLE TO ASSESS: file unreadable", from `L2` Remove this item, skipping to is not allowed Step 3
- Grep No hits → Annotation "UNABLE TO CITE: {Keywords} Not in {File} Detected in"
- reference File not found → Label disconnection + Added to pendingSupplement reference Manifest, do not fabricate content

✅ Checkpoint: `Step 2 Complete: |L2| == |L1| - Number of unreadable files = {M}, Total {X} tokens`

**Step 3: Output testing ideas by methodology (L1→L4)**
- Input.: Step 2 The loading set of outputs `L2`; all references in this step must ⊆ `L2`
- L1 Attack surface identification → L2 Hypothesis building → L3 Deep exploitation → L4 Defense reverse engineering
- Each conclusion must be cited `L2` Specifics of a certain file section/Line number; no basis → Annotation "UNABLE TO CITE" And stop the hypothetical line
- Prohibit re-search: This step finds that new reference → Back to Step 1 Relocate instead of directly Read/Grep

✅ Checkpoint: `Step 3 Complete: Output N Hypothesis clause, Among them Cited M Item. + UNABLE TO CITE K Item. == N (Equation acceptance)`

**Full Process Cross-validation**:
- [ ] Step 3 All referenced files ∈ Step 2 's `L2`(grep Verification)
- [ ] Number of cited items + UNABLE TO CITE Number of items == Total number of assumptions

## Scene navigation index

> Each line points to the corresponding reference. Detailed Payload/Case/Methodology is all in reference In this SKILL.md No longer expand.

### Core methodology

| Scene | reference |
|------|----------|
| L1-L4 Thinking Pyramid + WooYun Vulnerability formula + GAARM Mapping | `references/testing-methodology.md` |
| OWASP Top 10 Mapping (LLM/ASI/WSTG)| `testing-methodology.md §10.1-10.3` |
| GAARM 150 Risk ID | `references/gaarm-risk-matrix.md` |

### Web Security (by vulnerability type)

| Scene | reference |
|------|----------|
| SQL Injection (including SQLMap Quick search)| `references/web-sqli.md` |
| XSS Cross-site scripting | `references/web-xss.md` |
| Command Execution (RCE)| `references/web-rce.md` |
| XXE(XML External Entity)| `references/web-xxe.md` |
| Deserialization vulnerability | `references/web-deser.md` |
| File upload (including Webshell Kill immunity)| `references/web-upload.md` |
| File traversal / File inclusion | `references/web-traversal.md` |
| Information leakage (.git / Backup / Error information)| `references/web-leak.md` |
| SSRF / Server configuration error / CMS+URL Appendix | `references/web-ssrf-misc.md` |
| Overstepping authority / Payment / Password reset / Session / API Authentication | `references/web-logic-auth.md` |
| CORS / GraphQL / HTTP Smuggling / WebSocket / OAuth | `references/web-modern-protocols.md` |
| Supply chain / Cloud configuration / Container / CI/CD / Framework CVE | `references/web-deployment-security.md` |

### AI/LLM Security (in accordance with GAARM Stage)

| Security Domain | Application phase | Deployment phase | Training Phase |
|--------|---------|---------|---------|
| **AI Application**(Application stage subdivided by major risk categories↓)| See the detailed breakdown table below | `ai-app-deploy.md` | `ai-app-train.md` |
| **AI Model**(Application stage subdivided by major risk categories↓)| See the detailed breakdown table below | `ai-model-deploy.md` | `ai-model-train.md` |
| **AI Data**(Prompt Disclosure/Theft/Inference)| `ai-data-app.md` | `ai-data-deploy.md` | `ai-data-train.md` |
| **AI Identity**(Role escape/Agent Forgery)| `ai-identity-app.md` | `ai-identity-deploy.md` | `ai-identity-train.md` |
| **AI Base**(Container/Sandbox/Supply chain)| `ai-baseline-app.md` | `ai-baseline-deploy.md` | `ai-baseline-train.md` |

**AI Application - Application phase by major risk categories**:

| Risk Category | GAARM Number | reference |
|---------|----------|----------|
| Prompt Injection and variants (directly/Indirect/XSS/Memory/Worm/Obfuscation/Code/Reverse inducement/Multimodal)| GAARM.0039, 0040.x, 0043.x, 0044, 0045, 0061 | `ai-app-prompt.md` |
| MCP Protocol attack (carpet scam/Tool poisoning/Instruction override/Hidden Instructions)| GAARM.0046.x | `ai-app-mcp.md` |
| Agent With CoT Attack (Agent Utilize/SSRF/RCE/CoT/Query injection/Environment injection)| GAARM.0041.x, 0042.x, 0047, 0056.001, 0060 | `ai-app-agent-cot.md` |

**AI Model - Application phase by major risk categories**:

| Risk Category | GAARM Number | reference |
|---------|----------|----------|
| Jailbreak (DAN/Many-shot/Adversarial suffix/Concept activation)| GAARM.0027.x | `ai-model-jailbreak.md` |
| Illusion (fact/Cross-modal)| GAARM.0028.x, 0064 | `ai-model-hallucination.md` |
| Non-compliant content (bias/Brute force/Politics/False/Induction)| GAARM.0029.x | `ai-model-content.md` |
| Copyright and commercial violations | GAARM.0030.x | `ai-model-copyright.md` |
| Functional abuse and information forgery (image/Sound/Video/Phishing)| GAARM.0031.x, 0033, 0062, 0063 | `ai-model-misuse.md` |
| Adversarial Samples and Model Extraction | GAARM.0032.x | `ai-model-extraction.md` |

**Special reference**:
- AI Agent / MCP / Skills 2025-2026 Cutting-edge risk → `references/ai-app-frontier.md`
- Container and sandbox escape practical methodology → `references/ai-baseline-escape.md`

### Payload Quick lookup (by scenario in main reference Search in

| Scene | reference |
|------|----------|
| SQL Injection Payload | `references/web-sqli.md` |
| XSS Payload | `references/web-xss.md` |
| RCE / Command execution Payload | `references/web-rce.md` |
| Deserialization / XXE Payload | `references/web-deser.md` / `references/web-xxe.md` |
| File upload bypass / Path traversal Payload | `references/web-upload.md` / `references/web-traversal.md` |
| SSRF Payload | `references/web-ssrf-misc.md` |
| Web Modern protocols Payload(GraphQL/HTTP Smuggling/WebSocket)| `references/web-modern-protocols.md` |
| Prompt Injection Payload | `references/ai-app-prompt.md` |
| MCP Poisoning Payload | `references/ai-app-mcp.md` |
| Agent / CoT Injection Payload | `references/ai-app-agent-cot.md` |
| Jailbreak / Adversarial suffix Payload | `references/ai-model-jailbreak.md` |
| Container escape / Persistence / Horizontal movement | `references/ai-baseline-escape.md` |

## Zero result handling

| Situation | Correct action |
|------|---------|
| Grep Not hit reference | "UNABLE TO CITE: This scenario {X} Not in reference Contained in. Suggest WebSearch Or supplement reference" |
| Provided by the user URL No response | "UNABLE TO ASSESS: Target Unreachable" — Not based on URL Structure guessing vulnerability |
| Needs to be executed but lacks authorized context | "Only output analysis, do not output weaponized chain. If it is an authorized test, please clarify the scope of authorization." |
| reference Partially matches the user scenario | Reference matched part + Clearly label uncovered parts as "UNABLE TO CITE" |

## and others Skill Routing

| User demands | Correct routing. |
|---------|---------|
| Penetration Testing / Red team / CTF / Digging Holes | **This Skill** |
| Java/JS Deep white-box code audit (Source-Sink)| code-audit-skill |
| Mirawork Platform special testing | mirawork-security-tester |
| WooYun Historical vulnerability analysis methodology | wooyun-legacy |
| Prophet community research methodology | xianzhi-research |

---

*v2.0 | Knowledge source: WooYun 88,636 × Prophet 5,600+ × GAARM 150 × OWASP LLM/ASI/WSTG*
