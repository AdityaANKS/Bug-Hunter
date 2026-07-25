---
name: ai-mcp-security
description: AIandMCPsecurity assessment — Promptinjection、Tool abuse、MCPtrust boundary、AgentPermission escape、data breach、model risk、GAARMrisk matrix
---

# AI and MCP security assessment Skill

When the target contains LLM、Agent、MCP tool、Skills、RAG、Memory、Plugin or model service component when using this Skill.

**Preconditions**:if AI The surface is just the presentation layer, the real blocking is still the client signature or encryption protocol, let’s go back to `client-reverse` Skill.

## scene routing

| Risk type | preferred reference |
|---------|---------|
| Prompt injection / indirect injection / CoT interference | `references/ai-app-security.md` |
| Tool abuse / MCP poison / Skills supply chain | `references/04-ai-and-mcp-security-integrated.md` MCP chapter |
| Permission escape / Character crosses the line / Credential abuse | `references/ai-identity-security.md` |
| data breach / Prompt leakage / Model inversion | `references/ai-data-security.md` |
| container escape / CI-CD / Sandbox failed | `references/ai-baseline-security.md` |
| model risk / Adversarial examples / back door | `references/ai-model-security.md` |
| Impact classification and coverage assessment | `references/gaarm-risk-matrix.md` |

## Test process

### 1. Application layer attack
- direct Prompt injection
- Indirect injection (via external data source)
- CoT Interference and command override
- Agent Abuse (unauthorized operation)
- Code Execution Breakthrough
- Memory poison

### 2. MCP and Agent risk
- Tool description poisoning
- Instruction coverage
- Hidden command injection
- Unauthorized resource access
- Skills/Rules supply chain issues

### 3. Identity and Authorization
- Action abuse
- character escape
- Permission drift
- Cloud Credential Abuse

### 4. Data and privacy
- Prompt leakage
- Sensitive data exposed
- Training data problem
- Model inversion
- API data theft

### 5. Baseline and Deployment
- CI/CD defect
- container escape
- Vector database security
- sandbox invalid
- environmental isolation flaw
- Model service defects

## Reference documentation

- `references/04-ai-and-mcp-security-integrated.md` — AI and MCP Security Integration Reference
- `references/ai-app-security.md` — AI Application security
- `references/ai-identity-security.md` — AI Identity security
- `references/ai-data-security.md` — AI Data security
- `references/ai-baseline-security.md` — AI baseline security
- `references/ai-model-security.md` — AI model safety
- `references/gaarm-risk-matrix.md` — GAARM risk matrix
