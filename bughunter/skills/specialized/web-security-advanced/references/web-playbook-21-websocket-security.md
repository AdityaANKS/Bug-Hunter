# WebSocketSecurity
English: WebSocket Security
- Entry Count: 3
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## WebSocketCross-site hijacking(CSWSH)
- ID: ws-hijack
- Difficulty: intermediate
- Subcategory: WebSocketHijack
- Tags: WebSocket, CSWSH, Origin, Cross-site, Session hijacking
- Original Extracted Source: original extracted web-security-wiki source/ws-hijack.md
Description:
UtilizeWebSocketMissing in Handshake PhaseOriginVerified vulnerabilities, establishing cross-site through malicious webpagesWebSocketConnections. The attacker could hijack the victim'sWebSocketSessions, stealing real-time data, or sending messages as the victim. Similar toCSRFBut targetingWebSocketProtocol.
Prerequisites:
- Target usageWebSocketCommunication
- WebSocketHandshake unverifiedOrigin
Execution Outline:
1. 1. IdentificationWebSocketEndpoints
2. 2. Construct cross-site hijackingPOCPage
3. 3. WebSocketMessage injection
4. 4. WebSocketTraffic analysis script
## WebSocketSmuggling attacks
- ID: ws-smuggling
- Difficulty: expert
- Subcategory: WebSocketSmuggling
- Tags: WebSocket, Smuggling, Reverse Proxy, H2C, Intranet penetration
- Original Extracted Source: original extracted web-security-wiki source/ws-smuggling.md
Description:
Using reverse proxy/Load balancer againstWebSocketDifferences in protocol handling, throughWebSocketRequest for upgrade smugglingHTTPRequest to internal network services. Attackers can bypass front-end security controls and communicate directly with the back-end, accessing protected internalAPIOr management interface.
Prerequisites:
- The target uses a reverse proxy(Nginx/VarnishEtc.)
- Proxy allowedWebSocketUpgrade
- Internal services exist in the backend
Execution Outline:
1. 1. DetectionWebSocketSmuggling Possibility
2. 2. WebSocketTunnel construction
3. 3. H2CSmuggling Bypass Access Control
4. 4. Reverse proxy differential exploitation
## WebSocketAuthentication and Authorization Bypass
- ID: ws-auth-bypass
- Difficulty: intermediate
- Subcategory: Authentication bypass
- Tags: WebSocket, Authentication, Authorization, Overstepping authority, TokenReplay
- Original Extracted Source: original extracted web-security-wiki source/ws-auth-bypass.md
Description:
UtilizeWebSocketVulnerability of Missing Continuous Authentication Check After Connection Establishment, through Session Fixation、Token Replay、Channel over-subscribing and other means to bypass authentication and authorization mechanisms.WebSocketThe long connection characteristic allows access to remain after permission changes on the original connection.
Prerequisites:
- Target usageWebSocketReal-time communication
- Successfully obtained a valid session/Token
Execution Outline:
1. 1. WebSocketAuthentication Mechanism Analysis
2. 2. TokenReplay and Session Fixation
3. 3. Channel/Room over-privileged subscription
4. 4. WebSocketRate limiting andDoSTesting

