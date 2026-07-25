# AIFoundation security - Application phase

> Source: AISSGreen Alliance Large Model Security Intelligence Chain Community | Dismantled From ai-baseline-security.md
> Phase: Application phase (container escape/Denial of service/Code execution escape)

## Application phase

### LLMsDenial of service&Resource exhaustion

> Risk number: GAARM.0008
> Lifecycle: Application phase

**Attack overview**

Attackers may target machine learning systems by sending a large number of requests to lower.MLservice speed or lead to service shutdown. Due toLLMsThe system requires significant dedicated computing resources, attackers can intentionally construct inputs that require extensive useless calculations to consumeLLMsSystem resources, leading toLLMsand degrade the quality of service for other users, which may incur high resource costs. BecauseLLMThe resource-intensive nature and unpredictability of user input make the impact of this vulnerability easily magnified.

**Attack Cases**

Case
Description




Case One
InagentConducted inPromptInject and trick it into repeated calls LLM and SerpAPI, quickly increase costs.


Case two
Due toSourcegraphThe accidental leakage of site administrator access tokens, which are exploited to impersonate users to gain access to the system management console, resulting inAPISignificant increase in usage and leakage of large amounts of user data.


Case three
UtilizePromptInjection lettingMathGPTDisclosureAPIKey, causing denial of service


Case Four
Application in the power systemLLMMake decisions; if it occursDOSAttacks that may lead to delays and errors in decision-making, ultimately affecting the stable operation of the power system

**Attack risks**

Resource exhaustion attack: Attackers may send a large number of requests to consume the model's computational resources, making the service unavailable, affecting user experience, and even leading to service interruptions.
Data leakage and abuse: the attack process may lead to abnormal leakage of the modelAPITokens and other sensitive information, attackers may conduct unauthorized access.

**Mitigation measures**

Mitigation method
Description




APIRate limit
EnforceAPIRate limiting, restricting individual users orIPThe number of requests that an address can make within a specific time


Restrict execution count
Limit the number of queued operations andLLMTotal number of operations in the responding system


Real-time monitoring and alerting
Continuously monitoring hardware resource utilization to identify abnormal peaks or patterns that may indicate denial-of-service attacks

**Reference**

https://atlas.mitre.org/techniques/AML.T0029
https://owasp.org/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-2023-v05.pdf
https://www.cnblogs.com/LittleHann/p/17596696.html

---
### Code parser execution escape

> Risk number: GAARM.0007.001
> Lifecycle: Application phase

**Attack overview**

This risk refers to attackers exploitingGPT-4Functions of code parsers, which have code parsing and code generation capabilities, to construct and hide malicious code step by step through multiple session context interactions、UseUnicodeUse character and encoding obfuscation and other methods to hide malicious code, thus overcoming the code security check mechanism of model applications, bypassing the sandbox escape, and gaining access to the system. This type of malicious code is highly covert and difficult to detect. Once it breaches sandbox isolation, the attacker can control the entire system and steal data.、Implanting backdoors, etc.

**Attack Cases**

Case
Description




Case One
InGPT4When executing code, the malicious code is concealed and bypassed through multiple session context interactions and encoding methods, ultimately triggered by strings, thus bypassingGPT-4Security checks performed.cat /etc/issueCommand, successfully obtained theLinuxDistribution

**Attack risks**

Data leakage risk: attackers able to extract from LLM Extracting sensitive data from applications or their connected systems.
System integrity risks: Attackers can perform unauthorized operations, modify system settings or files, and even implant malicious code, causing damage to the system.
Privilege escalation risk: once an attacker successfully escapes the sandbox, they may gain access privileges higher than originally possessed.

**Mitigation measures**

Mitigation method
Description




Strict testing isolation environment
Conduct rigorous testing and verification of the sandbox environment to ensure its safety


Input./Output Validation
Filter out unsafePrompt, maximizing system security


Access Control
In LLM Implement strict access control and privilege separation in applications and their sandbox environments, ensuring that only authorized entities can access sensitive resources and limiting the execution of privileged operations

**Reference**

https://blog.securelayer7.net/owasp-top10-for-large-language-models/
https://www.mufeedvh.com/llm-security/#2-sandboxing-extended-llms
https://owasp.org/www-project-top-10-for-large-language-model-applications/Archive/0_1_vulns/Inadequate_Sandboxing.html

---
### Container runtime risks

> Risk number: GAARM.0004 (FromAISSClassification Inference)
> Lifecycle: Deployment phase

**Attack overview**

Developed based on an integrated frameworkLLMsApplications, usually combined withK8SClusters and container environments implementing variousAgentsSetting up and isolating the runtime environment, attackers indirectly use carefully constructed prompts through the model'sAgentExecute attacks against container runtime environments to achieve container escape under container environments、Container privilege escalation attacks, etc.

**Attack Cases**

Case
Description




Case One
WizBy uploading a malicious model toHuggingface FaceObtain permissions for the model container runtime environment.

**Attack risks**

Break container isolation: Attackers attempt to break through the container's isolation environment by exploiting vulnerabilities or configuration defects, gaining access to the host machine.
Image content tampering: Attackers may tamper with the model image content, embedding malicious code.
Data Leakage: Attackers may obtain sensitive data, such as filesystem information on the host.
Service interruption: An attacker may disrupt services on the host machine, leading to service unavailability.
Lateral movement: Attackers may utilize escaped containers as a springboard to further attack other systems on the internal network.
Persistence control: Attackers may install backdoors on the host machine for long-term control.

**Mitigation measures**

Mitigation method
Description




Regular review
Regularly scan container images and dependency components to ensure there are no security vulnerabilities.


Resource constraints and access isolation
Implement resource restrictions and isolation strategies to prevent a single container from consuming too much resource and impacting other machines in the cluster.


Principle of least privilege
Avoid using--privilegedRunning privileged containers with just the minimum permissions required for the container.


Input./Output Validation
Ensure the security of model input and output prompts and results, and implement interception for suspicious attack behaviors

**Reference**

https://mp.weixin.qq.com/s/tf4ljSJ0Ue0YniojWhYMKg
https://www.wiz.io/blog/wiz-and-hugging-face-address-risks-to-ai-infrastructure

---
### Container cluster environment detection

> Risk number: GAARM.0006
> Lifecycle: Application phase

**Attack overview**

This risk refers to attackers exploiting third-party cloud vendors or self-built environments in model deployment.K8SSecurity issues inherent in the cluster itself, such as system permission controls、Configuration error、Security vulnerabilities of the cluster itself、Third-party integration plugins. ForLLMsIn integrated applicationsAgentsAttack using features to interact with the business deployment environment, achieving attacks on the model business application system. Successful penetration into the deployment environment may lead to risks such as sensitive data leakage and backdoor programs being implanted.

**Attack Cases**

Case
Description




Case One
WizBy uploading a malicious model toHuggingface FaceObtain model runtime environment permissions for further exploitationEKSCluster misconfiguration resulting in privilege escalation.

**Attack risks**

Resource exhaustion attacks: Unrestricted access to resources may become an attack vector, where attackers may consume a large number of resources, affecting the normal operation of the system.
Privileged mode operation risk: Running containers in privileged mode may increase the risk of system breaches.
Unauthorized cluster access: If security measures are not implemented or the cluster has misconfigurations, attackers may gain complete access to the entire cluster.

**Mitigation measures**

Mitigation method
Description




Regular review
Regularly scan container images and dependency components to ensure there are no security vulnerabilities


Resource constraints and access isolation
Implement resource limits and isolation policies to prevent a single container from consuming excessive resources, throughKubernetesKeys created in the middle and specific permission roles to limit access to resources


Control network traffic
UtilizeKubernetesNetwork Policies to ControlPodInbound and outbound network traffic between, reducing potential lateral movement within the cluster and

**Reference**

https://pradiptabanerjee.medium.com/confidential-containers-for-large-language-models-42477436345a


https://www.run.ai/guides/kubernetes-architecture/securing-your-ai-ml-kubernetes-environment

---
### Container cluster environment attack

> Risk number: GAARM.0007
> Lifecycle: Application phase

**Attack overview**

Developed based on an integrated frameworkLLMsApplication, which typically integrates various functionalitiesAgent, theseAgentWill be deployed inKubernetesIn the container environment of the cluster. Attackers can indirectly induce by carefully constructing prompts.LLMs'sAgentExecute commands to probe containers, thereby achieving detection and collection of environmental information in the cluster, preparing for subsequent attack processes. After detection and collection of relevant information, one can specifically look for and exploit vulnerabilities and configuration issues in the cluster, further penetrating and attacking the entire container cluster.

**Attack Cases**

Case
Description




Case One
InGPT4When executing code, the malicious code is concealed and bypassed through multiple session context interactions and encoding methods, ultimately triggered by strings, thus bypassingGPT-4Security checks performed.cat /etc/issueCommand, successfully obtained theLinuxDistribution and cluster environment variables and other information

**Attack risks**

Cluster environment information leakage: Attackers may entice by constructing specific promptsAIModel executes unauthorized commands, thereby leaking internal architecture or security configuration information of the container.
Cluster security configuration leakage: Attackers can obtain details of the cluster's security configuration through probing, which may lead to decreased security of the cluster and increased risk of being breached.

**Mitigation measures**

Mitigation method
Description




Implement strict access controls
Ensure that all services and ports are strictly reviewed, only authorized access that is necessary, to reduce the potential attack surface


Input./Output Validation
Ensure the security of model input and output prompts and results, and implement interception for suspicious attack behaviors

**Reference**

https://mp.weixin.qq.com/s/Ry1PoZLfPvw6Lj8bz14mgw

---
