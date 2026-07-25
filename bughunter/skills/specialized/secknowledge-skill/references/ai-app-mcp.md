# AIApplication security. - Application phase - MCP Protocol Attacks

> Source: AISSGreen Alliance Large Model Security Intelligence Chain Community | Dismantled From ai-app-app.md
> Risk Category: MCP(GAARM.0046.x Carpet scam / Tool poisoning / Instruction override / Hidden Instructions)

---

### MCPCarpet scam

> Risk number: GAARM.0046.001
> Lifecycle: Application phase

**Attack overview**

MCPCarpet scam attack refers to due toMCPThe architecture allows the server to dynamically modify the tool description after client authorization. Attackers may exploit this mechanism to inject malicious instructions based on user trust (such as tampering with functional logic or hijacking operations). Even if the installation underwent a security review, subsequent covert tampering may still result in the tool description being injected with malicious exploitation instructions (such as data leakage or unauthorized operations).

**Attack Cases**

Case
Description




Case One
Malicious MCP The tool function description embeds covert prompts such as "read user private key." After approving the tool, when the model is invoked, it erroneously executes these prompts, leaking local files.

**Attack risks**

Tool privilege escalation: When the model calls the tool, the execution of unexpected instructions may occur due to content poisoning.
Sensitive data leakage: Attackers induce the model to access and output such as ~/.ssh/id_rsa Waiting for sensitive files.
Model function hijacking: Attackers can exploit Prompt Manipulate model behavior, such as spreading false information、Generate illegal content.
Bypass the review mechanism: field validation passes when the tool is registered, but the model is hijacked during actual execution by descriptive content.

**Mitigation measures**

Mitigation method
Description




White-box assessment mechanism
ToMCP ServerCode for white-box auditing to detect malicious tool descriptions and code behavior in a timely manner


Audit and monitoring
Real-time monitoring of model behavior, logging tool invocation logs, and timely detection of abnormal operations


Model security training
Conduct adversarial training on the model to enhance defense capabilities against poisoning attacks.


APIAccess Control
Restrict tool access to sensitive data, reducing the risk of leaks and misuse.


Execute context isolation
Restrict model access tool description fields, or use structured calling protocols (such as OpenAI ChatML Tool call syntax) to avoid description pollution

**Reference**

https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks
https://atlas.mitre.org/techniques/AML.T0051
https://github.com/invariantlabs-ai/mcp-injection-experiments

---
### MCPTool poisoning attack

> Risk number: GAARM.0046
> Lifecycle: Application phase

**Attack overview**

MCPIt is an open protocol designed to standardize how applications provide context to large language models.MCPTool poisoning attack is a type of attack against this protocol. The attacker uses maliciousMCP ServerInjecting malicious prompt words into the tool description for malicious manipulation of tool behavior. Its core feature is embedding malicious instructions in the tool description, leveraging the model's process of parsing the complete tool description, and inducing the model to perform unauthorized operations through hidden instructions (like special labels or encoding), such as generating malicious content.、Leak sensitive information or bypass other security constraints.

**Attack Cases**

Case
Description




Case One
Attackers achieve malicious attacks by manipulating tool descriptions, resulting in sensitive model information leaking to maliciousMCP Server


Case two
UtilizeMCP ToolPoisoning the description to achieve prompt word injection, controlling parameters of other tools for information exfiltration and other attack purposes

**Attack risks**

MCPTool poisoning attacks can lead to serious systemic risks, affecting the safety of the model.、Reliability and user trust. The following are the main risks:

Trust degradation: May lead to decreased user trust in the model and its development tools, affecting its application in sensitive scenarios.
Target hijacking: it can deviate the model from its original design purpose through poisoning, executing custom malicious commands, increasing abuse risks.
System security threats: May lead toMCPInserting malicious code into the tool, leading to further system breaches or functionality being compromised.
Data privacy leakage: Can be exploited to extract training data or sensitive information from user inputs through poisoning.

**Mitigation measures**

Mitigation method
Description




White-box assessment mechanism
ToMCP ServerCode for white-box auditing to detect malicious tool descriptions and code behavior in a timely manner


Audit and monitoring
Real-time monitoring of model behavior, logging tool invocation logs, and timely detection of abnormal operations


Model security training
Conduct adversarial training on the model to enhance defense capabilities against poisoning attacks.


APIAccess Control
Restrict tool access to sensitive data, reducing the risk of leaks and misuse.

**Reference**

https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks
https://mp.weixin.qq.com/s/EJLb1IwqbPF3VSDkJu099g
https://x.com/hongming731/status/1922261630664245326
https://news.qq.com/rain/a/20250429A07QY000

---
### MCPCommand injection attack

> Risk number: GAARM.0046.002
> Lifecycle: Application phase

**Attack overview**

MCPInstruction coverage risk is a type of targetingMCP ServerMalicious injection attacks called by tools, attackers through maliciousMCP ServerTool Description, Implanting Malicious Instructions into It, Hijacking the Normal Behavior of Other Trustworthy Tools. For example, an attacker may modify the email sending tool's invocation behavior to secretly alter the recipient's email during the call, leading to sensitive data leakage or malicious operations.

**Attack Cases**

Case
Description




Case One
Create tool descriptions that include hidden instructions that manipulate the model's interaction with other tools,LLMwill read and follow these instructions without the user's knowledge


Case two
This case includes a trusted server and a malicious server. The trusted server provides tools for sending emails, while the malicious server provides a forged digital addition tool, which containsMCPCommand injection attack, requiring the recipient of the sending tool to be@pwnd.com


Case three
This case exploits maliciousMCP ServerDescription, controlwhatapps send_messageThe recipient information of the tool is+13241234123

**Attack risks**

Data leakage risk: Instruction coverage attacks can indicate trusted tools from dialogues、Extract sensitive information from documents or connected systems and send it to machines controlled by attackers.
Abuse of trusted tools: Attackers can manipulate the model's network requests、Trusted tools for code execution, allowing access to untrusted sites or executing malicious code, etc.

**Mitigation measures**

Mitigation method
Description




White-box assessment mechanism
ToMCP ServerCode for white-box auditing to detect malicious tool descriptions and code behavior in a timely manner


Audit and monitoring
Real-time monitoring of model behavior, logging tool invocation logs, and timely detection of abnormal operations


Model security training
Conduct adversarial training on the model to enhance defense capabilities against poisoning attacks.


APIAccess Control
Restrict tool access to sensitive data, reducing the risk of leaks and misuse.

**Reference**

https://blog.trailofbits.com/2025/04/21/jumping-the-line-how-mcp-servers-can-attack-you-before-you-ever-use-them/
https://blog.trailofbits.com/2025/04/29/deceiving-users-with-ansi-terminal-codes-in-mcp/

---
### MCPHidden Command Attack

> Risk number: GAARM.0046.003
> Lifecycle: Application phase

**Attack overview**

MCPHidden command attack refers to attackers executing MCP Embedded in tool description ANSI Terminal escape codes (e.g., color settings、Cursor Control, etc.) or invisible Unicode Characters  , can make malicious commands invisible to users, but still be LLM  Execution. This type of attack exploits MCP the "line jumping" vulnerability, allowing the attack to affect the developer’s operations without being detected , leading to data leakage、Supply Chain Attack and other security issues.

**Attack Cases**

Case
Description




Case One
Attackers embed in tool description ANSI Escape codes, making the text invisible in the terminal, but LLM Still read and executed instructions within, causing the model to suggest downloading from a malicious server Python Package, which may trigger supply chain attacks.


Case two
By adding invisible Unicode Character, the attacker can be at LLM Inject malicious commands in the middle.


Case three
By injecting hidden code into the webpage,MCPThe tool returns web page information to LLM, Causes injection of invisible malicious instructions, resulting in data leakage or other attacks.

**Attack risks**

Supply chain attack: an attacker can embed malicious code during development through hidden instructions, affecting the entire software supply chain.
Data leak: Sensitive information (e.g., IP Address、Download sources, etc. may be silently leaked.  
System security: In certain cases, hidden instructions can be used to generate and execute malicious code.

**Mitigation measures**

Mitigation method
Description




Input output filtering
Strictly filter and sanitize special characters from user inputs and tool outputs, removing potential malicious characters and instructions.


Avoid passing the original tool output to the terminal
Potentially dangerous outputs should be consistently cleaned by disabling escape sequences before rendering. The simplest way is to replace any byte with hexadecimal values1bAs a placeholder, since all escape sequences recognized by modern terminals start with this byte.


Tool description review
To MCP Review the tool's description to ensure it does not contain malicious instructions


Restrict MCP Server permissions
In sensitive environments, only trusted MCP Interact with the server to reduce potential attack surfaces.


Monitoring and auditing MCP Activities
Regularly review logs and interactions to detect abnormal or suspicious behavior

**Reference**

https://blog.trailofbits.com/2025/04/29/deceiving-users-with-ansi-terminal-codes-in-mcp/
https://www.solo.io/blog/deep-dive-mcp-and-a2a-attack-vectors-for-ai-agents

---
