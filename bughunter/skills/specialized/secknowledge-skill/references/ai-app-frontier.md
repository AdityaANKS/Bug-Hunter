# AIApplication security. - Cutting-edge security risks (2025-2026)

> Source: AISSGreen Alliance Large Model Security Intelligence Chain Community | Dismantled From ai-app-security.md
> Theme: AI Agent/MCP/Skills Leading risks (Claude Code CVE/Skills Injection/Agent Worm)

## Thirty-five、AI Agent/MCP/Skills Frontier Security Risks (2025-2026)

> The following content is based on2025-2026Latest security research supplement, coveringOWASP Agentic AI Top 10 (ASI01-ASI10).

### MCP (Model Context Protocol) Protocol security

#### 11ClassMCPEmerging risks (Checkmarx/Invariant Labs/Trail of Bits 2025research)

| Risk types | Description | Attack scenarios |
|----------|------|----------|
| Tool description poisoning | Intool descriptionEmbed hidden malicious instructions in | model execution tools.descriptionHidden inPrompt |
| Carpet scam(Rug Pull) | After user authorizationServerDynamically modify tool descriptions | Initial review approved, followed by tampering with functional logic |
| Instruction override(Shadow Tool) | MaliciousServer'stoolDescribe hijacking behavior of trusted tools | Modify the email sending tool's recipient to the attacker |
| ANSI/UnicodeHidden instructions | Utilizing terminal escape codes or invisibleUnicodeCharacter hiding instructions | Supply chain attack: Model Suggests Downloading Malicious Packages |
| CrossServerAttack | MultipleMCP ServerTool definition conflicts and hijacking between | Server ARedefineServer Btool name |
| Token/Credential theft | ExtractMCP ServerStoredOAuth TokenandAPIKey | Single point breakthrough to obtain credentials for all connected services |
| ServerCamouflage | MaliciousMCP ServerDisguise Legitimate Service Records All Queries | Data Theft and Behavioral Monitoring |
| SchemaManipulation | Dynamically modify tool inputs/OutputSchemaBypass Verification | Inject additional parameters or modify return values |
| Command injection | Tool parameter injectionOSCommand | MCP ServerExecuting unfilteredshellCommand |
| Context overflow | Constructing super-large tool responses exhausting model context window | Extruding security commands, reducing the model's judgment ability |
| Persistent poisoning | Return value pollution of conversation history through tools | Long-term impact on the security of all subsequent interactions |

#### MCPSecurity testing methods

1. **Tool description audit**: Check all registrationstool'sdescriptionWhether the field contains hidden instructions(ANSICode/Unicode/HTMLComments)
2. **Dynamic behavior monitoring**: Compare initial registration and runtimetool descriptionIs it consistent
3. **CrossServerIsolation**: Verification multipliesServerIn the environmenttoolName conflict
4. **Credential storage audit.**: CheckOAuth Token/API KeyStorage method(Plain text.vsEncryption)
5. **Input validation testing**: TotoolCommand injection via parameters/SQLInjection testing
6. **Permission boundary testing**: verificationtoolWhether resources outside the declared scope can be accessed

### AI Agent Security (OWASP ASI01-ASI10 Supplement)

#### Clawdbot/Moltbot Practical case studies (2026Year1Month)

Global discovery4500+Exposed instance'sAI AgentSecurity Incidents:
- **Root cause**: Reverse proxy configuration error causedlocalhostAutomatic authentication passed
- **Impact**: APIKey、ServiceToken、WhatsAppSession credentials were extracted.
- **Lessons learned**: AI AgentConcentratedshellExecute、Persistent state、High privilege for initiating autonomous tasks, single-point exposure=Full takeover

#### AgentTool selection attack (CATSresearch)

- The tool pool acts as an uncontrolled repository, allowing attackers to release tools with misleading metadata
- under adversarial attacks,AgentTool choice leads to reduced authentication accuracy60%+
- Adaptive adversarial attack accuracy is below20%

#### ASI07: MultipleAgentCommunication security

| Attack vectors | Description |
|----------|------|
| Message forgery | Agent ACamouflageAgent BSend Instructions |
| Abuse of trust transfer | Low privilegeAgentExploit high privilegesAgentTrust relationship |
| Coordination hijacking | ManipulationAgentTask Allocation and Result Aggregation Between |
| Man-in-the-middle attack | intercepting and tamperingAgentInterval Communication |

#### ASI09: Exploiting human-machine trust

- Over-Reliance: User onAIOutput executed directly without validation
- Social engineering enhancement: AIGenerated phishing content is more believable
- Confirmation bias: Users tend to trust information that is consistent with their expectationsAIOutput
- Automated bias: "AIWhat should be said is right"Psychology

#### ASI10: Malicious/Out of controlAgent

- AgentRun outside of authorized parameters after being compromised.
- Target drift in autonomous decision-making chain
- Horizontal movement: PassAgentInfection of others through communicationAgent

### Skills/Rules Supply chain security

#### Attack surface

AIProgramming Assistant(Claude Code/CursorEtc.)'sSkillsandRulesSystem introduces new supply chain attack surface:

| Attack vectors | Description | Impact |
|----------|------|------|
| MaliciousSkillInjection | Community-sharedskillEmbedded maliciousPromptInstructions | AIExecute Hidden Commands(Such as data transmission) |
| RulesFile tampering | PassPRModify.cursorrules/.claude/RULES.md | Long-term control of developer'sAIBehavior |
| SKILL.mdPoisoning | skillReferencedreferenceIndirect injection embedded in files | AIReadreferenceExecute malicious commands |
| Dependency chain attack | skilldependent externalMCP ServerReplaced | All using thisskillAffected users |
| Build hook exploitation | Passskill'sscripts/Trigger malicious build operations | Code execution.、Key theft |

#### Claude Code DisclosedCVE (2025-2026)

| CVE | Severity | Description |
|-----|--------|------|
| CVE-2025-54795 | High | echoCommand bypass user approval and execute directly |
| GHSA-qxfv-fcpc-w36x | High | rgCommand injection bypass approvalPrompt |
| - | High | sedCommand validation bypass enabling arbitrary file writing |
| - | High | Commands can be executed before launching the trust dialog |
| - | Moderate | Malicious repository configuration leads to data leakage |

#### Defense Recommendations

- **SkillAudit**: Pre-installation reviewSKILL.mdAnd allreferenceFile content
- **Signature verification**: verificationskillSource and Integrity(Currently no official mechanism,Manual intervention required)
- **Permission isolation**: RestrictskillAccessible tools and files scope
- **RulesProtect**: .cursorrulesandAGENTS.mdIncorporate into the code review process
- **MCP ServerWhitelist**: Only allow trustedMCP ServerConnection
- **Behavior Monitoring**: RecordAIAll tool calls and file operation logs of the assistant

### Agentic AI Comprehensive security testing framework

Based onOWASP ASI01-ASI10, targetingAI AgentSystematic testing processes of the application:

1. **Target Enumeration**: Identify allAgent、Tool、MCP Server、Communication channel
2. **Authentication testing**: AgentAuthentication、TokenManagement、Permission boundaries(ASI03)
3. **Tool security**: descriptionAudit、Parameter injection、Permission overflow(ASI02)
4. **Injection testing**: Direct/IndirectPromptInjection、Tool return value injection(ASI01)
5. **Supply chain audit**: MCP ServerSource、skillIntegrity、Dependency security(ASI04)
6. **Code execution.**: Sandbox escape、Command injection、File operation(ASI05)
7. **Memory safety**: Context poisoning、Persistent attack、State corruption(ASI06)
8. **Communication security**: AgentInterval authentication、Message Integrity、Trust transfer(ASI07)
9. **cascading test**: Single point of failure propagation range、Fault isolation(ASI08)
10. **Trust testing**: Output verification mechanism、Manual approval process(ASI09)
11. **Escape Testing**: AgentBehavior Monitoring、Anomaly Detection、Kill Switch(ASI10)
