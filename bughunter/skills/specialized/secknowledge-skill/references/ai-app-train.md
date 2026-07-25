# AIApplication security. - Training Phase

> Source: AISSGreen Alliance Large Model Security Intelligence Chain Community | Dismantled From ai-app-security.md
> Phase: Training phase (GAARM.0034-0036 Third-Party Components/Plugin/Insecure Code)

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

