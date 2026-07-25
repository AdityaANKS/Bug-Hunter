---
name: client-reverse
description: Client reverse engineeringBurpreplay — Complex client signature recovery、Encrypted restore、Request chain tracking、Stable replay, available for authorized AndroidAppPenetration testing、BrowserJSsign、Desktop client reverse engineering
---

# Client reverse engineering Burp replay Skill

When the request is made by the client (AndroidApp、BrowserJS、Desktop client) structure, and the signature exists、encryption、tokenstate、Device binding or anti-automation logic causes Burp When direct playback is not possible, use this Skill.

## core principles

**Packet-First**: First capture and analyze the real HTTP/HTTPS request or WebSocket traffic, confirm availability, and then reverse choke points as needed. Reverse is the blocking resolution step, not the default entry.

## scene routing

### Authorized Android App Penetration testing

**Don't use it first jadx、ida_pro_mcp analyze APK**, operate in the following order:

1. Confirm target App Already installed on the connected device
2. get ready Burp or Charles Capture packets
3. use scrcpy_vision Open App, drives real business processes
4. Check after every key action Burp/Charles Does it appear HTTP/HTTPS or WebSocket packet
5. If the package is visible and replayable → Enter now `web-security-advanced` Do Web/API Security testing
6. repeat"Interface action → Capture packets → Web security analysis"cycle
7. Only can't catch the bag/Packets are encrypted/When replay is not possible → upgrade to jadx → frida_mcp → ida_pro_mcp

**MCP tool chain**:scrcpy_vision → burp/charles → adb_mcp → jadx → frida_mcp → ida_pro_mcp

### Browser JS sign、Climb backward、WebSocket handshake

1. chrome_devtools View page status and request chain
2. js_reverse position token/sign Generate logic
3. burp Verify replay and identify mutable fields

**stage model**:locate → recover → runtime → validation → replay

**MCP tool chain**:chrome_devtools → js_reverse → burp

### desktop client / local signer

1. everything_search Locate related documents
2. ida_pro_mcp Static analysis signature function
3. frida_mcp Get runtime parameters
4. burp Verify stable replay

**MCP tool chain**:everything_search → ida_pro_mcp → frida_mcp → burp

## Replay readiness checklist

Entering Payload Before taking the test, you must be able to answer:

- How is the request body constructed?
- sign/Where does the encrypted input come from?
- Which cookie、header、token、device value、Timestamp、nonce is required?
- Does the request rely on order or session state?
- Which fields will not break replay if changed?

## evidence retention

- builder/signer/crypto code location
- key hook Points and runtime observations
- available replay Request sample
- Preconditions、Failure modes and anti-automation behavior descriptions

## Reference documentation

- `references/02-client-api-reverse-and-burp.md` — Client reverses to Burp Replay overall workflow
- `references/android-authorized-app-pentest-sop.md` — Android App penetration SOP
- `references/browser-js-signing-workflow.md` — Browser JS Signature workflow
- `references/android-signing-and-crypto-workflow.md` — Android signing and encryption workflow
- `references/android-ui-driven-observation-and-packet-loop.md` — Android UI Drive observation loop
- `references/android-external-url-runtime-first-workflow.md` — Android external URL test
- `references/android-network-layer-testing-quick-reference.md` — Android network layer testing quick review
- `references/MCP.md` — MCP Competency Master Document
- `references/tool-selection-map.md` — Tool selection map
