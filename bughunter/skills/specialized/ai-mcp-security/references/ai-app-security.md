# AIApplication security.

> Source: AISSGreen Alliance Large Model Security Intelligence Chain Community
> Number of Entries: 34

---

## Application phase

### CoTInjection attack

> Risk number: GAARM.0042
> Lifecycle: Application phase

**Attack overview**

CoT(Chain of Thought) By promptingLLMsThink through a series of key steps to solve the problem, effectively enhancing the reasoning capability for problem-solving. Based onReAct(Reason + Act) ImplementationCoTTechnical framework of inference, and utilizeAgentScheduling implementationLLMsInteraction capabilities to access the external world, seamlessly connecting to various external systems and executing complex tasks.
InCoTIn the application, the user poses questions in natural language,AIThe model generates a series of reasoning steps to answer the question, involving thinking (Thought)、Action (Act)、Observation (Obs) Three core steps,AIThe model will cycle through the three steps above to complete the reasoning and resolution of various complex problems. Since the entire process is more open and flexible than traditional code logic, lacking strict process control structures, attackers can exploitCoTInjection attack bypasses specific inference steps to induceAIThe model executes unexpected actions, such as: business functional risks (arbitrary user transfers, etc.)、Technical functional risk (SSRF、RCEEtc.), currentlyCoTThere are two main attack methodologies for injection attacks:

Thought Chain Interference Injection: By ObservationCoTThe scheduling process, construct malicious input to deceive the model into believing it has obtained aAgentThe result, by forgingAgentResults to achieveCoTInterference in the running process;
Chain of Thought Manipulation Injection: By observationCoTScheduling process of , directly or using adversarial attack methods to construct malicious input, achieving control overCoTManipulation of the process, causing the model to skip pre-set optionsCoTProcess, directly scheduling sensitiveAgent;

**Attack Cases**

Case
Description




Case One
This case mainly proposes based onReActFramework'sLLMsApplications, how to utilize themCoTThought chain process to achieve.AgentMalicious use of


Case two
This study found that by combining jailbreak prompts with CoT Combine prompts, utilize CoT Bypass LLM Ethical limitations can lead to the model generating private information.


Case three
ReActQuery injection attacks under the frameworkCTFOpen source question

**Attack risks**

When using information retrieval systemsLLMsIn the application, attackers can pollute the information retrieval database, allowing malicious text fragments to be injected into the sent toLLMQueries, thereby affecting the final output results, resulting in user privacy、A series of risks such as malicious code execution.
In the Refund Business SystemLLMsIn the application, attackers can interfere with refundsCoTProcess, so that orders that originally did not meet the refund conditions can be normally refunded; or directly maliciously manipulate refund operationsAgent, resulting in a discrepancy between the actual refund amount and the expected refund amount, causing economic losses for the business.

**Mitigation measures**

Mitigation method
Description




Strict permission control
Enforce strict privilege controls to ensureLLMsCan only access necessary content andAgentThus minimizing potential vulnerability points to the greatest extent.


LLMs AgentScheduling control
For sensitive operations.AgentImplement strict external automated or manual permission verification mechanisms to avoidLLMsDirectly has the corresponding usage permissions


PromptContent Enhancement
Adopt OpenAI Chat Markup Language (ChatML) Solutions aimed at isolating genuine user prompts from other content

**Reference**

http://youtube.com/watch?v=7ZA0Z1R-MjQ
http://youtube.com/watch?v=KksYizcLFH0

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
### PromptInjection

> Risk number: GAARM.0039
> Lifecycle: Application phase

**Attack overview**

PromptInjection is when attackers use specially crafted input to overwrite or manipulateLLMsThe original command process. Due to the inherent ambiguity of natural language, the boundary between commands and data often lacks clarity, leading attackers to exploit malicious external input to contaminate the model's output. This kind of attack usually occurs when untrusted input is used as part of the prompt.LLMsCan recognize and process natural language, while natural language itself is ambiguous, commands and data often lack clear boundaries, attackers can embed instructions within controlled data fields, and the system cannot distinguish between data and commands at a low level.

**Attack Cases**

Case
Description




Case One
Manipulate using malicious inputGPT-3Prompt, command model ignores its previous instructions


Case two
Use multiple methods toPromptInjection attack

**Attack risks**

PromptSuccessful injection may lead to metadataPromptDisclosure、Model Jailbreak、Model functional abuse and other harms.

Malicious content generation: attackers can exploitPromptInject improper content, including threats.、Defamation or other malicious information.
Data leak: IfLLMsTo be used to output sensitive information.PromptInjection attacks may lead to data leaks.
System security: in certain cases,PromptInjection can be used to generate and execute malicious code.
Model abuse: Attackers employ methods like target hijacking toLLMsDeviate from the system's predetermined settings, execute other custom instructions, increasing the risk of model abuse.

**Mitigation measures**

Mitigation method
Description




PromptContent Enhancement
Adopting something similar to OpenAI Chat Markup Language (ChatML) And solutions, toPromptReinforcing the structure and content, attempting to isolate genuine user prompts from other content


Model security alignment
Provide diverse training data covering various attack scenarios, enhancing the model's generalization ability and robustness by adding security fence mechanisms during the model training phase


Input./Output Validation
By setting external security guards based on rules on the input and output sides of the model、Classification algorithms、Using methods like large security models to detect and filter input and output content


Monitoring and logging
Monitor and logLLMsInteraction records for subsequent detection and analysis of potential issues.PromptInjection attack

**Reference**

https://aclanthology.org/2024.scalellm-1.2/
https://atlas.mitre.org/techniques/AML.T0051
https://josephthacker.com/ai/2023/05/19/prompt-injection-poc.html
https://simonwillison.net/2022/Sep/12/prompt-injection/

---
### SSRFEnvironmental simulation detection

> Risk number: GAARM.0041.001
> Lifecycle: Application phase

**Attack overview**

SSRFThe formation is mostly due to the server providing the function to obtain data from applications on other servers without filtering or limiting the target address. IfLLMsExists in the applicationSSRFVulnerability, attackers can exploit this vulnerability to launch internal network requests to access restricted resources within the application. Meanwhile, someLLMsPossibly built-in with network access capabilitiesAgentUsed for executing some external information queries and other operations. The attacker can exploitLLMsApplicationAPI SSRFVulnerability orLLMsEquipped with network access functionality inAgent, execute unexpected requests or access restricted resources (e.g., internal services、API or data storage), thereby accessing the internal systems of the model and increasing model information、Internal services、Risk of leaking sensitive data and other information.

**Attack Cases**

Case
Description




Case One
ChatGPT-Next-WebApplications existSSRFVulnerability(CVE-2023-49785),This vulnerability can be used to probe internal network resources

**Attack risks**

Access internal resources: attackers can exploit SSRF Vulnerabilities to send requests and obtain sensitive information within the internal network
Attack Traffic Proxy: By leveraging SSRF Vulnerability, attackers can send malicious requests to attack internal systems、Services or resources
Data leakage: Attackers may exploit this risk to obtain sensitive data, such as cloud platform access keys, etc.

**Mitigation measures**

Mitigation method
Description




LLMs API Scheduling control and sandbox isolation
Implement appropriate sandbox mechanisms for isolationLLMAnd restrict its access to network resources、Internal services andAPIAccess. By implementing strict access controls, organizations can minimize the likelihood of unauthorized interactions and mitigateSSRFImpact of vulnerabilities


LLMsRegular Security Assessments and Reviews
Regular audits and reviews of network and application security settings to identify and address any misconfigurations, ensuring internal resources are not inadvertently exposed toLLM, strengthen the overall security system


Input./Output Validation
Implement robust input validation and processing techniques to ensure prompts are thoroughly checked and filtered, which helps prevent malicious or accidental prompts from triggering unauthorized requests, thereby reducingSSRFRisk of attack


Monitoring and logging
Implement comprehensive monitoring and recording mechanisms to trackLLMInteraction. By closely monitoringLLMActivities and record relevant information, organizations can detect and analyze potentialSSRFVulnerabilities, allowing for timely detection and remediation

**Reference**

https://owasp.org/www-project-top-10-for-large-language-model-applications/Archive/0_1_vulns/SSRF.html

---
### XSSSession content hijacking

> Risk number: GAARM.0040.001
> Lifecycle: Application phase

**Attack overview**

XSSSession content hijacking as a means of indirect prompt injection attack, utilizing large language models (LLMs) The process of obtaining external information. When users interact withLLMPassLLMInteract using the provided interface, for examplewebInterface、apiInterface、Applications, etc., attackers indirectly inject malicious prompt instructions, utilizingLLMsApplication frontend parsingMarkdownTags andHTML imgFeatures such as labels, summarize the content of the current chat session, and sensitive keys、Data and other information embedded intoimgLabelsrcIn Attributes, thus achieving the leakage of session content.

**Attack Cases**

Case
Description




Case One
Attackers UseGoogle BardUpdate functionality, construct specialMarkdownImage labels, makingBardRender an image pointing to the attacker's server, achieving data theft


Case two
UtilizeAzure AI PlaygroundThe model allows through images.MarkdownInjection method attaches prompts tosrcAttribute'sURLRendered in, leading to risks such as data leakage


Case three
Attackers UseChatGPTPlugin direct accessYoutubeSubtitle functionality, through indirectPromptthe content of injected control subtitlesAIBehavior.


Case Four
Attackers can exploitChatGPT'sMarkdownImage Rendering Function Steals Chat Records, Controlled by the AttackerAIBehavior, request to summarize chat history and append toURLTo steal data


Case 5
The attacker throughMarkdownAutomatically steals data from chat sessions through image injection


Case Six
The attacker can indicateChatGPTUse plugins to record dialogues and generate references to recordsURLand throughMarkdownImage injection leaking links to obtain the entire conversation history


Case seven
Due toLLMProxy (client applications, such asBing ChatOrChatGPT) Vulnerable toPromptInjection attack, where attackers can exploit this vulnerability by embedding in imagesURLAppend sensitive data to automate data leakage

**Attack risks**

Data leakage: Attackers can access sensitive user data from the current session, including session tokens、Personal Information、Chat records, etc.
Session Hijacking: Attackers may take over a user's session through acquired session tokens.

**Mitigation measures**

Mitigation method
Description




Input./Output Validation
Rigorously validate and sanitize all input and output data to remove or correct any suspicious injections and generated content


Content Security Policy(CSP)
Implement strictCSPContent security policy to prevent the execution of malicious scripts and data exfiltration


Principle of least privilege
Ensure proper sandboxing and limitLLMsAbility to limit plugins、AgentMechanisms that obtain data information from untrusted sources


Manual intervention approval
Provide users with more control, allowing them to manage the use of plugins and the flow of data

**Reference**

https://systemweakness.com/new-prompt-injection-attack-on-chatgpt-web-version-ef717492c5c2

---
### Code execution injection

> Risk number: GAARM.0041.002
> Lifecycle: Application phase

**Attack overview**

InReActUnder the framework,LLMsCan interact with external systems, external code interpreterAgentCan be used forLLMsProvide code execution capabilities to automate icon drawing during business application processes、Complex code computation and other requirements. Attackers manipulate by constructing malicious input prompts.LLMsExecute the scheduled reasoning process, allowing forLLMsSchedule code executionAgentExecute malicious code on the underlying system、Commands and operations to realizeLLMsAttacks and exploitation of the runtime environment of the base platform, the main reason for this attack is:

Failure to effectively check, validate, or limit user input allows attackers to carry out unauthorized malicious code execution operations.
Insufficient sandbox environment orLLMsCapability limitations are insufficient, causing it to interact with the underlying system in unexpected ways.
Unintentionally exposing system-level functions or interfaces toLLMs.

**Attack Cases**

Case
Description




Case One
GPT-4After the new feature goes live, it is found thatPythonThe code interpreter is suspected of having a sandbox escape vulnerability

**Attack risks**

Code execution risk: Attackers can execute arbitraryPythonCode, which may lead to server damage、Data leakage or other malicious activities.
System permission control: IfCodeExecutorWithout appropriate security measures, executing code combined with container escape and other attack methods may gain elevated permissions on the system.
Persistent access control: Attackers may use this opportunity to establish a long-term access channel for ongoing attacks.

**Mitigation measures**

Mitigation method
Description




Input Validation
Implement strict input detection and restriction processes to prevent malicious or accidental prompts from beingLLMsProcessing


Principle of least privilege
Ensure proper sandboxing and limitLLMsCapability to limit interaction with lower-level systems, avoiding operations that could lead to system-level impacts.


Monitoring and logging
Record all passesLLMExecution of operations, and perform real-time monitoring to quickly detect and respond to suspicious activities

**Reference**

https://owasp.org/www-project-top-10-for-large-language-model-applications/Archive/0_1_vulns/Unauthorized_Code_Execution.html
https://www.calvin-risk.com/blog/decoding-llm-risks-a-comprehensive-look-at-unauthorized-code-execution

---
### Keyword obfuscation

> Risk number: GAARM.0043
> Lifecycle: Application phase

**Attack overview**

This risk refers to targetingPromptConduct special processing operations on keywords in (homophones、Synonyms、Word splitting or other forms of text manipulation), to maintain similar meaning while undergoingtokenDe-risking the Connotation, thus avoiding the model's security mechanisms against sensitive vocabulary restrictions.

**Attack Cases**

In EnglishLLMIn which common keyword obfuscation methods include: letter obfuscation (bomb -> b0mbSynonym replacement (bomb -> explosive), word segmentation (bomb -> b-o-m-b).
For ChineseLLM, due to differences in tokenization methods, keyword obfuscation methods also vary significantly, common Chinese keyword obfuscation methods include pinyin replacement (bomb -> zhabombs), synonym replacement (bomb -> Explosives), replacing with similar characters (bomb -> Explosive Dusting) etc.

**Attack risks**

Generating inappropriate content: Attackers may use keyword obfuscation techniques to bypass automated content review systems and publish or disseminate malicious content, such as violence、Terrorism or pornographic information.
Bypass security mechanisms: Attackers maliciously guide the model to produce incorrect outputs to mislead the system into making poor decisions or executing dangerous operations.

**Mitigation measures**

Mitigation method
Description




Model security alignment
Improve through training and reinforcement learningLLMThe ability to identify and defend against such attacks


Input./Output Validation
Input side continuously updates and improves vocabulary filtering systems to identify and block obfuscated sensitive words; output side monitorsLLMsGenerated content, identifies potential issues through content security analysis technology

**Reference**

https://mp.weixin.qq.com/s/eFDQWYYCOe_SSiourhTxig

---
### Reverse inducement&Suppress attacks

> Risk number: GAARM.0045
> Lifecycle: Application phase

**Attack overview**

This risk is realized by adding specific instructions to the prompt, makingLLMsAvoid using certain specific rejection responses when generating answers, thereby increasing the likelihood of producing insecure or inappropriate content expected by attackers. This attack leverages autoregressive characteristics to induce the model, as the generation of model content is based on the previous outputs to predict the next word, by special requests makingLLMsDo not use certain specific vocabulary or phrases when generating responses, such as "sorry"、"Cannot"、"Unable" and so on, leading to the generation of inappropriate content by the model or violations of security policies.

**Attack Cases**

Case
Description




Case One
Exploit prefix injection + Reverse suppression attacks enableChatGPT3.5Bypassing security restrictions, resulting in the output of illegal crime risk content

**Attack risks**

Generate inappropriate content:LLMsmay generate illegal guidance、Brute force、Pornography、Politically sensitive and other risky content.
Bypass security mechanisms: Attackers can evadeLLMsThe security mechanism leads to the model outputting content that poses risks expected by the attacker.

**Mitigation measures**

Mitigation method
Description




Model robustness enhancement
Improve through training and reinforcement learningLLMThe ability to identify and defend against such attacks


Input monitoring and filtering
ToLLMsReal-time monitoring of output, promptly filtering out unsafe or inappropriate content

---
### Synonym replacement attack

> Risk number: GAARM.0043.001
> Lifecycle: Application phase

**Attack overview**

Synonym replacement attack, an attack method that bypasses the model’s security measures by using synonyms with the same or similar meanings as sensitive words or phrases, thereby obtaining or leaking internal instructions or sensitive information of the model. AsLLMsThe volume becomes increasingly large, making fine-tuning for each existing attack example more difficult, and the model is prone to attacks from synonym replacement. For example, in a programming assistant, an attacker can use"remove"Replace"delete"Using"harm"Replace"destroy"Attempting to bypass keyword checks, etc.

**Attack Cases**

Case
Description




Case One
Attackers successfully bypass the model’s filtering through synonym substitution, achieving systemPromptSet leak

**Attack risks**

Sensitive information leakage: Attackers may obtain internal instructions of the model, including but not limited to system prompts, passwords, and other sensitive information.
Security Mechanism Bypass: Attackers can exploit synonym replacement attacks to bypass the model's security protection, leading to the model generating unexpected outputs or performing unauthorized operations.

**Mitigation measures**

Mitigation method
Description




Model security alignment
Provide diverse training data covering various attack scenarios to enhance the model's generalization ability and robustness


Input./Output Validation
Input side continuously updates and improves vocabulary filtering systems to identify and block obfuscated sensitive words; output side monitorsLLMsGenerated content, identifies potential issues through content security analysis technology

**Reference**

https://arxiv.org/html/2402.16914v1

---
### Multimodal Collaborative Injection Attack

> Risk number: GAARM.0061
> Lifecycle: Application phase

**Attack overview**

Multimodal Collaborative Injection Attack is a type of attack that utilizes various modalities (text、Images、Audio、Advanced attack techniques for malicious instruction embedding through collaborative relationships between video etc. The attacker constructs malicious cross-modal content and uses the semantic association mechanism of multi-modal models in processing and understanding different modality information to embed malicious instructions into seemingly harmless multi-modal content. The core of this attack lies in bypassing the security detection mechanism of a single modality, achieving the attack's goal through the collaborative effect between modalities, which may lead to data leakage.、Model behavior manipulation or execute unintended operations.

**Attack Cases**

Case
Description




Case One
Attackers exploit cross-modal conflict injection (CMCI), inserting special adversarial images into the knowledge base through the system's normal update mechanism-Text pairs. These pairs seem semantically aligned during retrieval (e.g., an image shows pneumonia while the text describes "lungs clear"), but the actual content is contradictory, leading toAIOutput completely incorrect conclusions during diagnosis (e.g., misdiagnosing pneumonia as normal), causing serious medical safety risks.

**Attack risks**

Data leakage: Induce the model to leak training data or sensitive information
Behavioral manipulation: manipulating the model's output and behavior through cross-modal instructions
Security bypass: bypassing security detection and control mechanisms of a single modality
Privilege escalation: Using modal collaboration to gain higher system privileges.
Privacy invasion: Obtaining user privacy information through multimodal analysis

**Mitigation measures**

Mitigation method
Description




Cross-Modal Collaborative Detection
Establish a multimodal collaborative security detection mechanism, implement cross-modal semantic correlation analysis, and detect abnormal modal combination patterns


Multi-dimensional security verification
Simultaneously validate the security of multiple modalities, establish consistency checks between modalities, and implement cross-modal threat intelligence sharing


Fusion process reinforcement
Add security checks during multimodal fusion, implement dynamic adjustment of modality weights, establish abnormal fusion pattern detection


Modal isolation handling
Pre-processing isolation for different modalities, implementing modality-level security filtering, and establishing secure communication mechanisms between modalities

**Reference**

Manipulating multimodal agents through cross-modal prompt injection
How to make healthcare AI systems safer? Multimodal healthcareRAGVulnerabilities and threats in the system

---
### Defense against encoding attacks

> Risk number: GAARM.0044
> Lifecycle: Application phase

**Attack overview**

Adversarial encoding attacks are targeted atLLMsA type of adversarial technique for input and output side defense detection mechanisms, where attackers encode or transform data (such as usingbase64Coding), attempting to bypass security checks or inject malicious content. This type of attack targetsNLPThe model's encoding layer attempts to bypass the model's text comprehension ability, directly affecting the generation of internal features.
Due toLLMsTrained on diverse data types such as encoded text, thus supporting normal decoding operations and executing malicious commands or leaking sensitive data.

**Attack Cases**

Case
Description




Case One
Bypass using adversarial encoding attacksChatGPTSecurity restrictions, obtain stored key information


Case two
This article studies text-based NLP The disruptions caused by manipulated model encodings interfere with and mislead, utilizing language encoding functions to alter model outputs and increase inference run time. For example, unique characters presented as identical or visually similar glyphs are used to disturb the model's input.

**Attack risks**

Bypassing security mechanisms: Attackers may exploit the model's encoding and decoding capabilities to bypass content security checks.
Data leakage: Attackers can exploitBase64Code operations to hide malicious instructions or data, leading to sensitive information leakage.
Unauthorized code execution: Malicious code can be executedBase64The encoded form is injected intoLLMswhich may lead to unauthorized code execution, potentially compromising the integrity and security of the system.
Malicious operations: attackers can take advantage of.Base64Encoding manipulationLLMsExecute Various Malicious Operations, Such as Tampering with Data、Hijacking sessions, etc., thereby compromising system and user security.

**Mitigation measures**

Mitigation method
Description




Input./Output Validation
Validate input and output data to prevent malicious or accidentalBase64Encoding data input intoLLMsOr directly printed out


Model security alignment
Training large models on language nuances and coding techniques to recognize the characteristics of these attacks

**Reference**

https://promptengineering.org/mind-over-malware-battling-the-growing-arsenal-of-attacks-on-large-language-models/
https://www.toolify.ai/ai-news/the-future-of-hacking-5-terrifying-llm-security-threats-544868

---
### Application dialogueMemoryAttack

> Risk number: GAARM.0040.003
> Lifecycle: Application phase

**Attack overview**

This risk refers to the attacker being able toWebEnd.PromptInjection baitingLLMsCreate maliciousMemory(e.g., user and model's erroneous preference settings), through malicious modificationsLLMUser preferences in memory, achieving manipulationLLMsThe effect. For example, attackers can deceiveLLM, making it think the user's chat preference is "replying to every message from the user"‘Sorry, I can't reply to you’", to achieve thisDOSEffect of the Attack.

**Attack Cases**

Case
Description




Case One
This article introduces interactions through the applicationMemoryAttack leading to continuous denial of service for users

**Attack risks**

DOSAttack: Attackers can continuously subject users to denial-of-service memory attacks based on preferences.

**Mitigation measures**

Mitigation method
Description




Disable historical memory feature
CloseLLMsModel'sMemoryFeatures can mitigate this issue

**Reference**

https://embracethered.com/blog/posts/2024/chatgpt-persistent-denial-of-service/
https://openai.com/index/memory-and-new-controls-for-chatgpt/

---
### Application agentAgentUtilize

> Risk number: GAARM.0041
> Lifecycle: Application phase

**Attack overview**

LLMsApplicationAPIMainly divided into two categories of application scenarios, hence the applicationAPIThe risks mainly revolve around the following two types of application scenarios:


LLMsApplication Platform Based OnAPIProvide external service capabilities;

Attackers leverage large models (such asOpenAI'sGPTSeries) ofAPIPresent in the interfaceAPISecurity risks implement attack processes, collectingAPISearch for vulnerabilities based on interface information, construct maliciousAPIRequest, attempting to bypass authentication or inject malicious code. For example: accessing or performing higher privileged operations in an unauthorized manner、Utilizing Services Provided ExternallyAPIExecute malicious code commands, etc. through interface vulnerabilities.



LLMs AgentScheduling and third-party application integration based onAPIImplement related capabilities into the model connection;

Attackers exploit the model to access sensitive information or operationsAPIAccess capabilities, based onAPIAccess permissions can indirectly be constructed through malicious prompts, causing the model to perform dangerous operations such as accessing sensitive information, tampering with system configuration, etc. Since the model itself hasAPIThe operation and invocation capabilities have corresponding access permissions, which may allow malicious operations to bypass normal security controls, initiating actual malicious attacks that could lead to privilege escalation.、Risks such as unauthorized access to others' information.

**Attack Cases**

Case
Description




Case One
Regular user accounts were originally only allowed to useGPT-3.5The model, but through specificAPIAddress, where the attacker is able to access out-of-boundsGPT-4Model


Case two
Attackers useAPIExecute commands directly on the system, delete files


Case three
Build variousLLMs APIApplication scenarios, based onLLMsUtilizing malicious exploitationAPIFunctional implementation command execution、Account deletion and other attack behaviors


Case Four
Stable DiffusionProvidedAPIInterface, allowing developers to programmatically invoke models for image generation. Attackers exploit this to construct some malicious text prompts, and then throughStable Diffusion'sAPIInterface,Let the model generate these illegal or extremist image contents

**Attack risks**

Data leakage: Attackers may obtain sensitive data, such as user information and passwords.
Service interruption: Malicious operations may lead to service interruptions, such as deleting user records or database entries.
Decrease in Trust:LLMInaccurate or sensitive information generated may damage trust between users and organizations.
Legal liability: Due toLLMImproperly generated content may expose the organization to legal liability.

**Mitigation measures**

Mitigation method
Description




LLMs API Scheduling control
Restrict LLMs Accessible API And data to minimize potential harm when exploited


Input./Output Validation
Carefully clean user input to prevent malicious prompts from being injected into LLM In


Monitoring and logging
Record all passesLLMExecution of operations, and perform real-time monitoring to quickly detect and respond to suspicious activities


Manual intervention approval
Provide users with more control, allowing them to manage the use of plugins and the flow of data

**Reference**

https://portswigger.net/web-security/llm-attacks

---
### Thought chain disruption injection

> Risk number: GAARM.0042.001
> Lifecycle: Application phase

**Attack overview**

The risk isCoTA sub-risk of injection attacks, where attackers observeCoTScheduling process, construct malicious input to deceive the model into thinking it has obtained the correctagentResults, by forgingagentCompare ResultsCoTInterference.

**Attack Cases**

Case
Description




Case One
This case demonstratesCoTInterference, deceiving the model by constructing inputs to achieve illegal purposes

**Attack risks**

Interference injection: achieving interference by constructing malicious inputLLMThe purpose of which is to realize non-compliant operations.

**Mitigation measures**

Mitigation method
Description




Strict permission control
Ensure LLM Can only access basic content, minimizing potential violation points


Add human oversight
Add an additional layer of verification to prevent accidents LLM Assurance of behavior


Set clear trust boundaries
Will. LLM Treated as untrusted, always maintain external control in decision-making, and for possibly untrustworthy LLM Keep responsive and vigilant.

**Reference**

https://labs.withsecure.com/publications/llm-agent-prompt-injection

---
### Thought chain manipulation injection

> Risk number: GAARM.0042.002
> Lifecycle: Application phase

**Attack overview**

The risk isCoTA sub-risk of injection attacks, where attackers observeCoTThe scheduling process, constructing malicious inputs, allowing the model to skip the presetCoTProcess, directly scheduling sensitiveAgent. For example, skipping preset validation steps allows users to perform actions that should only be executable after validation directly.

**Attack Cases**

Case
Description




Case One
This case demonstratesCoTDirect manipulation of , deceiving the model through constructed inputs, causing it to skip verification steps that should have been taken, resulting in unreviewed large refunds to users


Case two
Attackers use a combination of multiple attack countermeasures to escape roles after bypassing previous prompt rules, then useCoTManipulate injection successful callsapproveTransferFunction to complete fund transfer operation

**Attack risks**

Manipulation Injection: Manipulation through malicious input constructionLLMThe purpose of which is to realize non-compliant operations.

**Mitigation measures**

Mitigation method
Description




Strict permission control
Ensure LLM Can only access basic content, minimizing potential violation points


Add human oversight
Add an additional layer of verification to prevent accidents LLM Assurance of behavior


Set clear trust boundaries
Will. LLM Treated as untrusted, always maintain external control in decision-making, and for possibly untrustworthy LLM Keep responsive and vigilant.

**Reference**

https://labs.withsecure.com/publications/llm-agent-prompt-injection

---
### Query injection attack

> Risk number: GAARM.0056.001
> Lifecycle: Application phase

**Attack overview**

The risk isCoTA sub-technique in injection attacks, query injection attacks are mainly used to exploitCoTData Query under ApplicationAgentAchieve arbitrary data leakage. InCoTIn the application, the user poses questions in natural language,AIThe model generates a series of reasoning steps to answer the question. Attackers can inject maliciousSQLCode attempts to bypass the model's security checks and access the backend database directly. WhenCoTThinking Chain Application External Access to Traditional Database、Vector database、When introducing external databases such as knowledge graphs, it is necessary to go throughAgentAchieve external data querying and acquisition, attackers can interfere or manipulateCoTProcess, for example, when querying external data, mistakenly treating user-provided statements as external data, resulting in arbitrary data being queried and obtained.

**Attack Cases**

Case
Description




Case One
ReActQuery injection attacks under the frameworkCTFOpen source question

**Attack risks**

When using information retrieval systemsLLMsIn the application, attackers can pollute the information retrieval database, allowing malicious text fragments to be injected into the sent toLLMQueries, thereby affecting the final output results, resulting in user privacy、A series of risks such as malicious code execution.

**Mitigation measures**

Mitigation method
Description




Strict permission control
Enforce strict privilege controls to ensureLLMsCan only access necessary content andAgentThus minimizing potential vulnerability points to the greatest extent.


LLMs AgentScheduling control
For sensitive operations.AgentImplement strict external automated or manual permission verification mechanisms to avoidLLMsDirectly has the corresponding usage permissions


PromptContent Enhancement
Adopt OpenAI Chat Markup Language (ChatML) Solutions aimed at isolating genuine user prompts from other content

**Reference**

http://youtube.com/watch?v=7ZA0Z1R-MjQ
http://youtube.com/watch?v=KksYizcLFH0

---
### Environment injection attack

> Risk number: GAARM.0047
> Lifecycle: Application phase

**Attack overview**

Environmental injection attacks refer to attackers injecting attack ideas through indirect prompts, embedding malicious instructions into external webpages、Interface、In environments like emails, whenAI AgentWhen processing external content, executing embedded instructions as user commands can lead to data leakage or achieve the purpose of controlling the model or stealing data. Attackers may manipulate environment variables、Modify Dependency Libraries or Pollute Configuration Files to Induce the Model to Generate Erroneous Output、Leak sensitive information or perform unauthorized operations.

**Attack Cases**

Case
Description




Case One
Attackers create malicious topics containing prompt injections in public repositories, and usersClaudeWhen sending regular requests,AITrigger malicious instructions by obtaining public repository issues, thereby pulling private repository data to the contextual environment, and creating records containing private data in the public repositoryPR, leading to data leakage.

**Attack risks**

Environment injection attacks can pose serious threats to the model development and deployment ecosystem. The main risks are as follows:

Malicious Output Generation: Attackers can induce the model to generate false information or harmful content through environmental injection, misleading users or triggering a trust crisis.
Data leakage: By tampering with environment configuration, attackers may obtain sensitive information, such as training datasets、User prompts orAPIKey.
System Integrity Compromise: Malicious injection attacks may lead to the destruction of the development environment, affecting the stability of model training or deployment, and even implanting backdoor programs.
Supply chain attack: Attackers contaminate third-party libraries or toolchains, affecting multiple model development projects and creating widespread security risks.
Trust crisis: Successful attacks may weaken users' trust in the model and its development environment, limiting its application in high-security scenarios.

**Mitigation measures**

Mitigation method
Description




Environment configuration validation
For all environment variables、Strictly verify configuration files and dependencies, using hash checks to ensure their integrity and prevent unauthorized modifications.


Dependency management
Use trusted dependency sources (e.g., officialPyPIImages), and regularly check the versions and signatures of dependency packages to prevent supply chain attacks.


Environment isolation
Develop、Test and production environments are completely isolated, restricting external input access to the core environment, thus reducing the attack surface.


Security monitoring and auditing
Implement real-time monitoring, record environment configuration and dependency change logs, regularly conduct security audits, and detect potential injection behaviors.


Principle of least privilege
For the environmentAPIImplement minimal permission control on access and file operations, use encrypted signatures to verify configuration sources to prevent malicious tampering.

**Reference**

https://mp.weixin.qq.com/s/9JwADiu9t3kqcfqnRMC2zQ
https://finance.sina.com.cn/tech/digi/2025-06-01/doc-ineypqvh0855918.shtml
https://zhuanlan.zhihu.com/p/1900540531131523166

---
### LoopsAgentWorm

> Risk number: GAARM.0040.002
> Lifecycle: Application phase

**Attack overview**

Agent (Agent) has the ability to obtain information in real-time from external sources such as the internet, and can pass this information to the large model for processing, which is ultimately returned to the user. However, attackers can exploit this by injecting malicious information through external data sources, disruptingAgentExecution, thereby affecting the output of large models. These malicious prompts can indirectly affect multiple large models (LLMs) application, forming a vicious cycle that allows malicious information to spread rapidly. ThroughAgentInput-output loop, this loopAgentWorms can cause a type of self-replicating and spreading malicious behavior, potentially leading to privacy leaks and security risks such as data misuse.

**Attack Cases**

Case
Description




Case One
Researchers created a nameMorris II'sAIWorm that can attack a generativeAIEmail assistant, stealing data from emails and sending spam, while compromisingChatGPTandGeminiSome security protections

**Attack risks**

Data leak:AIWorms may steal sensitive personal information, such as names、Phone number、Credit card number、ID number, etc.
Malware deployment: worms can deploy malware in infected systems, leading to further security issues.
Security bypass:AIWorms can bypass some existing security measures, such asChatGPTandGeminiSecurity Mechanisms.
New types of cyber attacks:AIWorms represent a previously unrecognized type of network attack, challenging existing security measures.

**Mitigation measures**

Mitigation method
Description




Input./Output Validation
Targeting entry intoAgentStrict verification and validation measures for data processed in the schedule


Design secureLLMs Agent
Take traditional security measures, such as ensuringAgnetApplication design security, monitor potential security vulnerabilities


Manual intervention approval
Keeping humans in the loop, ensuringLLMs AgentRequires manual approval before performing operations to avoidAIThe system autonomously sends emails or other potential risky behaviors

**Reference**

https://mp.weixin.qq.com/s/2bm7nuXkORLZ20mfpOmwrA

---
### IndirectPromptInjection

> Risk number: GAARM.0040
> Lifecycle: Application phase

**Attack overview**

LLMsIn the process of handling natural language, there exists a risk of malicious prompt injection (Prompt) vulnerabilities. Attackers will exploitPromptHidden inLLMVarious data that the system will process, such as text、Multimedia content、Information extracted from databases or websites, etc., and throughPromptManipulationLLMProducing harmful responses, such as malicious code execution.、Sensitive information leakage, etc. For example, writing malicious code into uploadsLLMFile whenLLMMalicious code will run when processing data in files, resulting in harm.

**Attack Cases**

Case
Description




Case One
Attackers implant injection code on the websites users access, causing.Bing ChatSearching for and leaking personal information without the user's knowledge


Case two
Attacker controlLLMsData retrieved by the plugin, utilizingMarkdownImage rendering mechanism, sending chat history as query parameters to the attacker's server


Case three
This case demonstrates aM365 CopilotMeans of attack, by sending an email containing malicious content, even without the user opening the email, can remotely controlCopilot, resulting in attacks from third parties

**Attack risks**

Malicious code execution: By injecting malicious code or data, an attacker may attempt to gain a foothold in the system to further control or damage it
Data leakage: Attackers may use indirect injection to mislead users, causing them to perform unintended actions or leak sensitive information.

**Mitigation measures**

Mitigation method
Description




Input Validation
Perform strict validation and sanitization on all input data to remove or correct any suspicious injection content


Principle of least privilege
Ensure proper sandboxing and limitLLMsAbility to limit plugins、AgentMechanisms that obtain data information from untrusted sources


Manual intervention approval
Provide users with more control, allowing them to manage the use of plugins and the flow of data

**Reference**

https://atlas.mitre.org/techniques/AML.T0051.001
https://twitter.com/random_walker/status/1636923058370891778
https://medium.com/@harry.hphu/introduction-to-web-llm-attacks-indirect-prompt-injection-7bb9f154bc07
https://medium.com/@dinob5551/indirect-prompt-injection-the-hidden-threat-lurking-in-ai-730b009dd5fb

---
### Unexpected code execution

> Risk number: GAARM.0060
> Lifecycle: Application phase

**Attack overview**

Unexpected code execution refers to the agent executing tasks, due toPromptInjection、Due to tool misuse or logical flaws, code operations were executed beyond the expected scope or without authorization. The core of this risk lies in the agent's lack of effective control over code execution boundaries, which might lead to dynamic code generation、Execute malicious actions through methods such as toolchain calls or script executions.、Dangerous or unexpected code, leading to system intrusion、Data has been tampered with、Serious consequences such as sensitive information leakage or service interruption.

**Attack Cases**

Case
Description




Case One
Vulnerabilities originate from the form node processingContent-TypeWas not validated at the time, allowing the attacker to specify any local sensitive file path, ultimately impersonating an administrator and executing malicious workflow commands through information leakage.


Case two
This case demonstrates AI The red team injects hints to lure multimodal models with desktop operations capability to download and execute malicious programs, ultimately establishing C2 Communication channels, achieving unintended code execution and remote control, turning the host system into a "zombie host."


Case three
This case demonstrates manipulation through prompt injection ChatGPT Long-term memory of (Memory) Mechanism, implanting covert instruction logic defined by the attacker, allowing the model to continuously interact with remote in subsequent dialogues C2 Communicate and execute instructions, forming "zombification control" at the model level and executing unexpected behaviors.

**Attack risks**

System intrusion: malicious code execution leads to full control of the system
Data Corruption: Performing destructive operations leads to data loss or tampering
Privilege escalation: gain higher system privileges through code execution
Backdoor implantation: implanting a persistent backdoor in the system
Service interruption: executing malicious code causes service unavailability
Lateral penetration: Using code execution to attack other systems

**Mitigation measures**

Mitigation method
Description




code execution sandbox
Restrict code execution to secure isolation environments, using containers or virtual machines for isolation and limiting the file system、Network and system call access


Code review verification
Implement static code security analysis, establish a code security rules repository, and dynamically detect malicious code patterns


Access Control
Implement the principle of least privilege, restrict the scope of code execution tools' permissions, and establish a code execution approval mechanism


Input validation filtering
Strictly validate code generation inputs, filter dangerous functions and operations, and detect potential malicious intent

**Reference**

n8nRemote code execution vulnerability
ZombAIs: From Prompt Injection to C2 with Claude Computer Use
AI Domination: Remote Controlling ChatGPT ZombAI Instances

---
## Deployment phase

### LLMsApplicationAPIMismanagement

> Risk number: GAARM.0049
> Lifecycle: Deployment phase

**Attack overview**

LLMsApplicationAPIMismanagement refers toLLMsSensitive operations exist in the integrated framework environmentTools、Agents、ChainsInternal and externalAPIComponents, not in conjunction withLLMsProper management and configuration of the environment is essential. Because large language models typically need to work with variousAPIInteract to Execute Tasks, if theseAPIIf not properly managed, such as not setting correct access permissions or not implementing sufficient security controls, attackers can exploit these vulnerabilities to gain sensitive information or perform malicious actions, achieving unauthorized access、Code execution exploitation and other attacks.

**Attack Cases**

Case
Description




Case One
TargetingLLMs apiExploitation mainly gives the following two

**Attack risks**

Data leakage: attackers may obtain sensitive data, including personal identification information、Trade secrets, etc.
Service interruption: Malicious code execution or unauthorized access may lead to service interruption or performance degradation.
Legal and compliance risks: Security vulnerabilities may lead to legal lawsuits and compliance issues.

**Mitigation measures**

Mitigation method
Description




Principle of least privilege
Follow the principle of least privilege, only forLLMsProvide the minimum access rights necessary to complete its tasks, avoiding excessive proxy authorization


Input./Output Validation
For all throughAPIThoroughly validate the sent input to prevent injection attacks


Monitoring and logging
MonitoringAINew types in the eraAPIMonitor and log activities to quickly detect and respond to suspicious behavior

---
### LLMsApplication source code poisoning

> Risk number: GAARM.0038
> Lifecycle: Training Phase

**Attack overview**

The source code may have some vulnerabilities during the review process, and attackers can exploit them by sending to large language models (LLMs) injecting malicious code into the application's source code, hiding the code through vulnerabilities to evade inspection, poisoning the source code of third-party open-source or commercial components, leading to security issues in the application during training or runtime, thereby affecting the downstream model application business development vendors using these components.

**Attack Cases**

Case
Description




Case One
An attacker can manipulate the model by uploading malicious code to open source websites, thereby affecting investments、Transaction、All fields such as news

**Attack risks**

Backdoor Insertion: By injecting backdoor code into the training data, allowing attackers to control or manipulate the model's output during inference, leading to unauthorized access or data manipulation.
Supply chain attack: By injecting malicious code into open source code, attackers can affect the entire supply chain that uses this code.
Fake news propaganda: attackers can use this technology to modify content, such as movie reviews or news reports, to spread misinformation or propaganda.

**Mitigation measures**

Mitigation method
Description




Detect changes that deviate from the original code
Identifying and intercepting abnormal behavior caused by malicious code modification


Input Validation and Filtering
Strict Input Validation and Cleaning Before Code is Input to the Model

**Reference**

https://drive.google.com/file/d/1CTVcliUblX35cWfB49Xjhf8xk-fM3QH1/edit?pli=1

---
### LLMsApplication source code theft

> Risk number: GAARM.0037
> Lifecycle: Training Phase

**Attack overview**

This risk refers to models or large language models (LLMsPoorly saved source code of ) or security risks in the deployment environment may expose the relevant deployment environment to unauthorized personnel attacks.LLMsTheft of application source code, leading to the risk of damaging the technical competitive advantage of the enterprise.

**Attack Cases**

Case
Description




Case One
Meta 's 650 Billion-parameter language model leaked


Case two
OpenAI Under GPT-4 A large number of model architectures、Training cost、Large amounts of information such as datasets being leaked

**Attack risks**

Loss of technical advantage: Competitors may replicate or modify leaked source code, thereby weakening the company's technical competitive advantage.
Cybersecurity threat: Attackers can use leaked source code to design targeted cyberattacks, for instance, system penetration through revealed vulnerabilities.
Phishing email risk: leaked source code may be used to create more deceptive phishing emails that mimic internal applications of enterprises, increasing the risk of users falling victim.

**Mitigation measures**

Mitigation method
Description




Code encryption protection
Use strong encryption algorithms forLLMsEncrypt the source code of the application to prevent unauthorized access and leakage.


Access permission control
Limit access toLLMsAccess permissions to application source code, ensuring that only authorized personnel can view or modify the code


Model monitoring
Monitor the usage of the model to ensure it is not used for malicious purposes

**Reference**

https://analyticsindiamag.com/metas-llama-leaked-to-the-public-thanks-to-4chan/
https://knightcolumbia.org/blog/the-llama-is-out-of-the-bag-should-we-expect-a-tidal-wave-of-disinformation

---
## Training Phase

### LLMsApplication of unsafe output handling

> Risk number: GAARM.0035.003
> Lifecycle: Training Phase

**Attack overview**

This risk refers to when downstream components accept large language models (LLM) When output is not properly reviewed, it leads to a type of security risk that arises. Various functions are included in the model's downstream componentsAgentWhen lacking relevant output handling, it can lead to abuse of the model by attackersAgentImplement attack behavior, for example, attackers can induce by entering specific textLLMOutput includes responses with sensitive information, thereby stealing user data, or directly outputting unexpected attacksPayload, leading to downstream occurrencesRCE、SSRFand other vulnerabilities.

**Attack Cases**

Case
Description




Case One
CVE-2023-29374 Yes Langchain An arbitrary code execution vulnerability, using 0.0.131 And earlier versions of Langchain, and call Langchain LLMMathChain Chain programs pose security risks that contain arbitrary command execution, which may lead to OpenAI key And sensitive information leakage、Langchain Issues such as server being compromised.


Case two
Auto-GPTInv0.4.3There was a path traversal vulnerability in previous versions, which could cause executionAuto-GPTarbitrary code on the hostdockerExecution outside the environment. Attackers can exploit this vulnerability to target and launch attacks on the system, endangering site security.

**Attack risks**

Sensitive information leakage:LLM Sometimes not cleaning in their responses JavaScript. In this case, attackers may use carefully craftedPromptCause LLM Return JavaScript Payload, when the victim's browser parses this payload, it will be attacked, resulting in the leakage of sensitive information such as chat history.
Arbitrary Code Execution: Attackers can execute arbitrary code through vulnerabilities. This may result in attackers executing malicious operations on the server, such as implanting backdoors.、Extracting sensitive data or interrupting services.
Targeting

**Mitigation measures**

Mitigation method
Description




Zero trust framework
In this framework, every request for accessing resources is treated as coming from an untrusted network, and the system will check it、Authentication and verification to enhance system security


Sandbox environment
Attempt to use a sandbox environment to execute code to ensure greater system security. For example, only in dedicated temporary Docker Executing code within a container can significantly limit the potential impact of malicious code

**Reference**

https://genai.owasp.org/wp-content/uploads/2024/05/OWASP-Top-10-for-LLM-Applications-v1_1_Chinese.pdf
https://cloud.baidu.com/article/3253170
https://www.akto.io/blog/insecure-output-handling-in-llms-insights
https://journal.hexmos.com/insecure-output-handling/
https://systemweakness.com/new-prompt-injection-attack-on-chatgpt-web-version-ef717492c5c2

---
### LLMsApply traditional vulnerability risk

> Risk number: GAARM.0035.002
> Lifecycle: Training Phase

**Attack overview**

Traditional application security vulnerabilities not only exist in traditional software systems but may also exist inLLMInside applications. For example, commonAPIInterface attacks, account takeover, code execution, etc., traditional risk vulnerabilities still existLLMExists in the middle; therefore, strict adherence to security best practices must be followed during the training phase to ensure that the system has adequate protection against traditional risks, or it may lead to service interruption、Account takeover、A series of dangers such as data tampering.

**Attack Cases**

Case
Description




Case One
The case reportedChatGPTis subject toDDoSSigns of Distributed Denial of Service (DDoS) attacks, where external attackers attempt to send repeatedly.Pingrequests, causing the network or server to overload and crash


Case two
ChatGPT-Next-WebApplications existSSRFVulnerability(CVE-2023-49785),This vulnerability can be used to probe internal network resources

**Attack risks**

Service disruption: Denial of service attack (DoS) or resource exhaustion may lead toLLMThe application is unable to respond to user requests, affecting business continuity.
System control: Remote code execution or script execution vulnerabilities may allow attackers to take over the server, implant malware, or perform destructive operations.

**Mitigation measures**

Mitigation method
Description




ReinforcementAPISecurity
Ensure allAPIInterfaces are subject to strict identity verification and authorization control, restricting access permissions.


Principle of least privilege
Restrict or disableLLMUnnecessary command execution functionality in the application to reduce the potential attack surface.


Regular Security Assessments
Regularly onLLMPerform security vulnerability scans for applications and promptly fix identified security issues.

**Reference**

https://sec.cafe/handbook/security_research/ai_security/llm_security/attack/

---
### LLMsPlugin: Insecure input handling

> Risk number: GAARM.0035.001
> Lifecycle: Training Phase

**Attack overview**

This risk refers to the fact thatLLMsPlugins have insecure input handling, introducing risks into large models. For example, plugins are likely to implement free text input from the model without validation or type checks to handle context size limitations, allowing potential attackers to construct a malicious request to send to the plugin, which may result in various undesired behaviors, including remote code execution.

**Attack Cases**

Case
Description




Case One
LangChainsInPALChainFound to have code execution risk

**Attack risks**

Unauthorized request execution: attackers can directly exploitLLMsApplication vulnerabilities or by manipulating input prompts, makingLLMsApplication executes unexpected requests, accessing or manipulating restricted resources.
Sensitive information leakage: throughLLMsAccessing restricted resources may lead to unauthorized acquisition and disclosure of sensitive information.

**Mitigation measures**

Mitigation method
Description




Input Validation and Filtering
Implement strict input validation and sanitization policies to ensure all input data is properlyLLMsAll processed have been checked and cleaned


Principle of least privilege
Follow the principle of least privilege, only forLLMsProvide the minimum access permissions necessary to complete its task, avoiding excessive authorization

**Reference**

https://owasp.org/www-project-top-10-for-large-language-model-applications/Archive/0_1_vulns/SSRF.html
https://www.horizon3.ai/attack-research/attack-blogs/nextchat-an-ai-chatbot-that-lets-you-talk-to-anyone-you-want-to/
https://genai.owasp.org/wp-content/uploads/2024/05/OWASP-Top-10-for-LLM-Applications-v1_1_Chinese.pdf

---
### LLMsPlugin: Business Over Proxy

> Risk number: GAARM.0036
> Lifecycle: Training Phase

**Attack overview**

Based onLLMThe system is usually granted a certain degree of business agent capability by developers, which is the ability to interact with other systems and perform operations in response to prompts. However, excessive proxying represents a security risk during the design and development phases, leading toLLMUnexpected occurrences/Performing destructive operations during fuzzy output, the root cause is usually: too many functions or too much autonomy. Excessive delegation can involve confidentiality.、A series of impacts on aspects such as integrity and availability, depending onLLMThe application can interact with which systems. For example, it hasLLMExcessive autonomy of the system leads toLLMWhen the application or plugin fails to independently verify and approve high-impact operations, it allows the plugin to perform deletion actions on user documents without any user confirmation.

**Attack Cases**

Case
Description




Case One
This video demonstrates how to illegally reset user passwords by exploiting the vulnerabilities of excessive proxies.

**Attack risks**

Sensitive Information Leakage: Caused by excessive business proxyLLMWhen manipulated maliciously, it may leak sensitive information and privacy.

**Mitigation measures**

Mitigation method
Description




Principle of least privilege
RestrictLLMPlugins allowed for proxy calls/Tools limited to the minimum required functions. For example, ifLLMThe basic system does not need to acquireURLThe ability of the content, so it should not be directed towardsLLMProxy provides such plugins


Avoid open-ended functionalities
Avoid open-ended functionalities (e.g., runningshellCommand、ObtainURLEtc.), and use plugins with finer-grained functionalities/Tools. For example,LLMBasic applications may need to write certain outputs to files. If running with pluginsshellIf this is achieved through functionality, the range of unwanted operations will be very large (can execute any othershellCommands). A safer alternative is to build a file writing plugin that only supports specific functions.

**Reference**

https://genai.owasp.org/wp-content/uploads/2024/05/OWASP-Top-10-for-LLM-Applications-v1_1_Chinese.pdf

---
### RAGFramework vulnerabilities

> Risk number: GAARM.0034.002
> Lifecycle: Training Phase

**Attack overview**

RAG(Retrieval-Augmented Generation) is a framework combining information retrieval and generation in large language models (LLM) used in development to enhance the model's generation capability. Due toRAGThe framework relies on the retrieval module to obtain information from external data sources. If the source data of the retrieval module is inaccurate or unreliable, it may lead to generated responses containing incorrect or misleading information; and variousAgent, and there may be associated security risks.RAGSecurity risks related to the framework mainly focus on.RAG、Information retrieval module、Integration of plugins and external interfaces, etc., due toRAGDesigned insecurely, potentially introducing security vulnerabilities intoLLMApplications. For example, if.RAGThe design of the retrieval module allows the server to make unrestricted requests, which may lead toSSRFExploitation of vulnerabilities.

**Attack Cases**

Case
Description




Case One
Due toLangChainExisting in the frameworkSSRFandPALChain'sRCEVulnerabilities that affect users of the frameworkLLMThe application has brought security risks

**Attack risks**

Information leakage: Attackers may access sensitive files or system configuration files through path traversal vulnerabilities, leaking internal system information.
System Control: If system files contain sensitive configuration information or scripts, attackers may further exploit this information to control the system.
Command execution: Data expression operation in the framework、PythonInterpreter, etc.Agent, which could be exploited to causeRCEAttack.

**Mitigation measures**

Mitigation method
Description




Input Validation
Strictly validate and sanitize all user inputs to prevent path traversal attacks.


Permission Management
Set appropriate file permissions to prevent unauthorized file access.


Update and fix
Ensure the latest versions of the application and related dependencies, and apply security patches in a timely manner to fix known vulnerabilities.

**Reference**

https://www.wehelpwin.com/article/5063
https://medium.com/nfactor-technologies/rag-poisoning-an-emerging-threat-in-ai-systems-660f9ff279f9
https://ironcorelabs.com/security-risks-rag/

---
### Unsafe coding practices

> Risk number: GAARM.0035
> Lifecycle: Training Phase

**Attack overview**

Unsafe coding practices refer to the development based on large model integration frameworksLLMsSecurity issues caused by design flaws during the application process. InLLMsThe code logic used during the application development process may bring security risks, posingLLMsApplications introduce exploitable security vulnerabilities. The security vulnerabilities may belong to two major categories:

LLMsApplication services have traditional vulnerabilities, such as excessive authorization in external serviceChatThere are risks of unauthorized viewing of others' chat records in the system services;
LLMsNew types in integrated frameworksTools、Agents、ChainsContains security risks, allowing attackers to base onLLMsIndirectly leveraging related vulnerabilities;

**Attack Cases**

Case
Description




Case One
LangChainsInPALChainFound to have code execution risk


Case two
LangChainsMultiple discoveries were madeRCEHigh-risk vulnerabilities

**Attack risks**

Insecure coding practices:LLMs During code generation, it may follow unsafe coding practices, leading to generated code containing security vulnerabilities.
Unauthorized request execution: attackers can directly exploitLLMsApplication vulnerabilities or by manipulating input prompts, makingLLMsApplication executes unexpected requests, accessing or manipulating restricted resources.

**Mitigation measures**

Mitigation method
Description




Automated detection and assessment
Use static analysis tools to detect insecure patterns in the code to improve code security


Principle of least privilege
Follow the principle of least privilege, only forLLMsProvide the minimum access rights necessary to complete its tasks, avoiding excessive proxy authorization


Input Validation and Filtering
Implement strict input validation and sanitization policies to ensure all input data is properlyLLMsAll processed have been checked and cleaned

**Reference**

https://arxiv.org/html/2312.04724v1

---
### Data processing component vulnerability

> Risk number: GAARM.0034.001
> Lifecycle: Training Phase

**Attack overview**

In artificial intelligence (AI) During the development process of the model, the security of the dataset is an important aspect that cannot be ignored. InHugging Face、GitHubVarious platforms may have data sets with malicious backdoors, which can be accessed throughLLMsCharacteristics or vulnerabilities of data processing components, againstAIModel security poses a threat. When developers use these contaminated datasets for model training, malicious code hidden in the datasets may be executed, leading to a series of security issues, such asAIModel、Leakage or tampering of datasets and code.

**Attack Cases**

Case
Description




Case One
Hugging Face'sdatasetsComponents have been found to contain insecure features, which may lead to command execution risks when loading malicious datasets using that component

**Attack risks**

System intrusion: Malicious scripts constructed by the attacker can connect to the attacker's server, execute system commands, thereby gaining control over the victim's server.
Data leakage: Malicious scripts may steal training data from the server、Model code and other sensitive data, leading to the leakage of intellectual property and user privacy.
Model parameter tampering: Parameters of large models may be maliciously tampered with, affecting the accuracy and reliability of the model.

**Mitigation measures**

Mitigation method
Description




Training/Trustworthy sources for fine-tuning datasets
Ensure that the source dataset is trustworthy and check for malicious content in the dataset scriptsPythonCode, use with caution inHugging FaceDatasets flagged with security risks


Supply chain security protection for large model components
Continuous follow-up to pay attention to the native security of large models、The latest supply chain security dynamics and recommendations in the fields of basic security and large model-enabled research and development security, etc.

**Reference**

https://security.tencent.com/index.php/blog/msg/209

---
### Third-Party Component Vulnerabilities

> Risk number: GAARM.0034
> Lifecycle: Training Phase

**Attack overview**

This attack refers toLLMsApplication developers may use third-party commercial or open-source library components during the model training phase, in which these third-party components may contain malicious code.、Component vulnerabilities, etc., which may lead to development machine、The server has been compromised, belonging toAISupply chain security risks in the environment.

**Attack Cases**

Case
Description




Case One
RedisDatabasePythonClientredis-pyUsing asynchronous interfaces may lead to user business data reading confusion when canceling commands(CVE-2023-28858)


Case two
TorchServeMay lead to unauthorized server access and achieve remote code execution on vulnerable instances


Case three
Hugging Face'sdatasetsComponents have vulnerabilities that allow attacks via malicious datasets, potentially leading to user devices being compromised and large model parameters being stolen or tampered with.


Case Four
This article studies the impact of backdoor attacks on pretrained models. Attackers can manipulate the model's recommendation results by implanting backdoors to achieve malicious marketing or other purposes.


Case 5
ChatGPT-Next-WebExistenceSSRFAnd reflexivityXSSVulnerability

**Attack risks**

Supply chain backdoor poison attack:AIWhen developers load datasets using third-party open-source libraries, if the dataset is embedded with malicious code, it may causePCOr servers are attacked.
Model parameter leakage or tampering: leading to the theft or alteration of model parameters, affecting the security and reliability of the model.

**Mitigation measures**

Mitigation method
Description




Supply chain security protection for large model components
For known security vulnerabilities, such asTorchServe'sCVE-2023-43654, should be updated to a secure version in a timely manner


Training/Trustworthy sources for fine-tuning datasets
Ensure that the dataset sources are trustworthy, check for malicious content in the dataset scriptsPythonCode, avoid using inHugging FaceDatasets flagged with security risks


Strictly control the introduction of open-source components
Establish an internal open-source governance system for the enterprise, strictly control the introduction of open-source components, and implement automated monitoring and tracking through tools.

**Reference**

https://hiddenlayer.com/research/insane-in-the-supply-chain/

---

---

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
