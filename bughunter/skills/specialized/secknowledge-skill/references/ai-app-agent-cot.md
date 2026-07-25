# AIApplication security. - Application phase - Agent With CoT Attack

> Source: AISSGreen Alliance Large Model Security Intelligence Chain Community | Dismantled From ai-app-app.md
> Risk Category: Agent/CoT(GAARM.0041.x Agent Exploitation and SSRF/RCE / 0042.x CoT Injection and cognitive chain interference / 0047 Environment injection / 0056.001 Query injection / 0060 Unexpected code execution)

---

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
