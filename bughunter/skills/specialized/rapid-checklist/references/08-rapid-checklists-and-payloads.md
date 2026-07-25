# 08 Rapid Checklists And Payloads

This file is the rapid operator-reference layer of the final skill system.
Use it only after routing is clear. It is meant for fast lookup, not for replacing methodology or workflow selection.

## Use This File For

- Quickly recall what to look at first for a certain type of vulnerability or blocking point
- Quick filter payload Family、Bypass direction and validation order
- Quick confirmation AI、MCP、Container、WebSocket、JWT、File、Authentication、SSRF And common test cards
- Quickly transition from "I know what to test" to "Which category of validation should I start with?"

## Do Not Use This File For

- Alternative `00-usage-and-routing.md` Scenario Throttling
- Alternative `01-unified-methodology.md` Make methodology decisions
- The request has not yet been captured、Directly enter blind mode when replay is not stable payload Testing

## Fast Routing Cards

### Web injection or output execution

- First look `03-web-security-integrated.md`
- If it is input point validation, prioritize splitting `SQLi`、`XSS`、`command execution`、`SSTI`、`XXE`
- If the request is client-constructed, return first `02-client-api-reverse-and-burp.md`

### Auth, logic, token, or state bugs

- First look `03-web-security-integrated.md`
- First Confirm Object Identification、Role boundaries、reset process、Payment amount、Sequential dependencies
- If token Or signature comes from the client, stabilize replay before testing

### Browser-side sign, anti-bot, or WebSocket handshake

- First look `browser-js-signing-workflow.md`
- Re-enter by stages `browser-locate-and-request-chain.md`、`browser-recover-and-shell-reduction.md`、`browser-runtime-fit-and-risk.md`、`browser-validation-and-handoff.md`
- Switch back after replay stabilization `03-web-security-integrated.md`

### Android runtime, packet visibility, or sign recovery

- First look `android-external-url-runtime-first-workflow.md`
- If you want to advance based on interface status, keep watching `android-ui-driven-observation-and-packet-loop.md`
- Only unable to capture packets、Re-enter when the package is opaque or replay is blocked `android-signing-and-crypto-workflow.md`

### AI, agent, or MCP exposure

- First look `04-ai-and-mcp-security-integrated.md`
- Prioritize division `prompt injection`、`tool abuse`、`MCP trust boundary`、`memory/state poisoning`、`output approval gaps`
- When you need to quickly check common testing semantics, see below AI/MCP Card

### Intranet, host, or AD work

- First look `06-intranet-and-host-operations-integrated.md`
- Review when the tool is uncertain `05-tools-and-operations-integrated.md`

## Web Rapid Cards

### SQL injection

- Quick verification: `'`, `"`, `)`, Boolean Difference, Time difference, Error reporting differences
- First confirm injection location: query, body, JSON, header, cookie, WebSocket message
- First check if the input is affected by client signature or encryption, If available, restore request lifecycle first
- Common bypass directions: inline comments, whitespace variation, keyword case folding, alternate encodings, parameter pollution

### XSS

- Rapid categorization: reflected, stored, DOM
- Confirm context first: HTML body, attribute, JS string, URL, template
- Common starter families: event handlers, SVG, tag breaking, JS context breaking
- If the results are rendered by the client-side rendering framework., Checking simultaneously. DOM sink and CSP Behavior

### Command execution

- Quick verification: timing, DNS or HTTP OOB, harmless command echo
- First identify the execution point as system shell、template helper、language runtime or worker sidecar
- Common bypass directions: separators, whitespace bypass, variableConcatenation., Base64 or hex decode chains

### File and SSRF

- File issues should be categorized first: upload, traversal/download, inclusion, parser confusion
- SSRF Split First: raw fetch, image proxy, webhook, PDF render, URL preview, cloud metadata reachability
- Common bypass directions: encoding layers, mixed path separators, alternate IP formats, redirect chaining, protocol pivot

### Modern protocols

- WebSocket: First confirm handshake authentication、Origin Validation、Message-level authentication、Room Boundary
- JWT: First confirm algorithm processing、Signature Verification、`kid` Or `jku` Dynamic key retrieval paths, etc.
- OAuth/OIDC: Confirm first redirect URI、state、PKCE、Account binding
- Request smuggling: First confirm the proxy chain and front-end and back-end parsing differences

## AI And MCP Rapid Cards

### Prompt injection

- Rapid categorization: direct, indirect, retrieval-borne, tool-description-borne, memory-borne
- First confirm which boundary the injection enters: model prompt, retrieval context, tool metadata, tool output, persisted memory
- Common bypass directions: role play, instruction override, encoding, multilingual phrasing, hidden text, long-context dilution

### Tool abuse and MCP trust boundary

- Confirm first tool description Whether it will be read by high-trust models
- Confirm first tool parameters、resource paths、tool outputs Will it be reinterpreted?
- Quick check: unauthorized resource reads, prompt override in description, hidden instructions, cross-tool request rewriting

### Agent memory and state poisoning

- Confirm first memory Is it explicit storage or implicit historical summary
- First check if you can get the malicious target、Role preferences or external instructions written into persistent states
- Focus on cross-iteration behavior drift、Approval bypass、Silent takeaway

### Model or data leakage

- Quick check: system prompt extraction, tool inventory exposure, API or secret leakage, training-data style continuation, RAG source disclosure
- First clarify whether it is direct disclosure or inference-style leakage

## Container And Sandbox Rapid Cards

### Environment triage

- First confirm if in a container、Sandbox、Restricted shell Or agent execution sandbox Inside
- Check first capabilities、namespace、mount、socket、metadata reachability
- If only validating isolated boundaries, do not first attempt destructive actions

### Escape paths

- Common directions: exposed Docker socket, writable host mounts, privileged container, cgroup abuse, `/proc` traversal, kernel CVE, cloud metadata pivots
- First do minimal information collection, then decide whether to continue

### Persistence or staged foothold

- First confirm the authorization boundary and test target
- Prioritize verifying "if it can be persisted" rather than immediate spreading
- Common locations: shell rc files, scheduled tasks, service startup, workspace poisoning, SSH keys

## Payload Family Hints

Use families, not copied full lists, unless the current task specifically needs detail from a deeper source.

- SQLi: boolean, time, error, union, second-order
- XSS: reflected, stored, DOM, mutation-based, CSP-aware
- Command execution: separator-based, subshell, whitespace-bypass, encoded launcher, OOB validation
- File bugs: upload extension variants, MIME mismatch, parser confusion, traversal encodings
- SSRF: alternate IP encodings, redirect pivot, protocol pivot, metadata paths
- AI injection: direct override, indirect document-borne, description poisoning, memory poisoning, encoded or multilingual prompts
- Escape and shell: environment triage, breakout path validation, persistence validation, callback channel selection

## Escalation Rule

- If the route is still unclear, go back to `00-usage-and-routing.md`.
- If packet visibility or replay is blocked, go back to `02-client-api-reverse-and-burp.md` or the matching browser or Android workflow.
- If you need exact original payload wording or exhaustive raw examples, open `references/payloads.md`.


