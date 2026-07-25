# AIFoundation security

> Source: AISSGreen Alliance Large Model Security Intelligence Chain Community
> Number of Entries: 19

---

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
## Deployment phase

### CI&CDProcess attack

> Risk number: GAARM.0004
> Lifecycle: Deployment phase

**Attack overview**

In the full lifecycle of large model development,CI/CDThe process is responsible for pushing the model from the development environment to the production environment, automatingLLMLarge models are deployed and responsible for subsequent updates and maintenance.CI&CDFlow Attack refers toCI/CDDuring the process of pushing the model to the production environment, due toCI/CDVulnerabilities in Infrastructure、The unreliability of third-party tools, etc., attackers can exploit these security vulnerabilities to attackCI/CDProcess, such as submitting malicious code within it、Polluting dependency packages, etc., leading to the model being illegally tampered with、Serious consequences such as sensitive information leakage.

  

Large model development lifecycleCI/CDProcess.

**Attack Cases**

Case
Description




Case One
Obtain credentials of developers or operations personnel through phishing, thereby inCI/CDSubmit malicious code during the process.


Case two
Utilizing server vulnerabilities, such asGitlab、JenkinsEtc.CI/CDVulnerabilities in infrastructure, leading to attacks.


Case three
Attacks targeting third-party tools and application dependencies, such as polluting dependency packages or uploading malicious packages with forged dependency package names to open-source central repositories.

**Attack risks**

Virtual environment contamination: The virtual environment or container in the continuous integration environment is attacked, and the attacker may tamper with dependencies or runtime configurations in the environment, affecting the results of model training and deployment.
Build and deployment processes are tampered with: attackers may try to modify automated build and deployment processes to insert malicious code or operations during model deployment.
Sensitive information leakage: Continuous integration/Sensitive information (such as access credentials) is stored in a continuous delivery environment、Configuration file、Such as keys), once obtained by attackers, may lead to sensitive information leakage and privacy risks.
Denial of service attack: An attacker may attempt to deny service (DoS) Attacks to make continuous integration/Continuous delivery system fails to operate normally, leading to interruptions or delays during the model development and deployment process.
Unauthorized model access: The model deployment process is attacked, and attackers may obtain unauthorized access through vulnerabilities, thus performing illegal operations or tampering with the model.

**Mitigation measures**

Mitigation method
Description




Strengthen access control and permission management
Limitations on continuous integration/Access rights to continuous delivery systems and related environments, ensuring that only authorized personnel can access critical resources


Security updates and audits
Regular updates and audits of model deployment software to fix vulnerabilities and enhance security


Strengthen monitoring and logging
Timely detection of abnormal activities and attack behaviors, and taking prompt response measures to reduce potential security risks and losses

**Reference**

https://github.com/knownsec/KCon/blob/master/2023/CICD%E6%94%BB%E5%87%BB%E5%9C%BA%E6%99%AF.pdf

---
### Cloud platform multi-tenancy isolation failure

> Risk number: GAARM.0003.001
> Lifecycle: Deployment phase

**Attack overview**

In a multi-tenant architecture on cloud platforms, each tenant should have an independent operating environment and data storage to ensure mutual isolation of user behavior and data. Isolation failure may be due to design flaws、Configuration errors and others, with the popularization of high-value computing power services, attackers may break through tenant boundaries to access and tamper with data from other tenants, and even perform malicious operations, leading to a series of security issues that result in data and resources between different tenants (users or organizations) being inadequately protected.

**Attack Cases**

Case
Description




Case One
This article on "AI Research conducted on whether the model runs in an isolated environment,WizUtilizeAWSInIMDSMetadata service, completedAmazon EKSTake over the entire cluster service after privilege escalation.EKSMove laterally within the cluster, potentially enabling cross-tenant access and leading to sensitive data leakage

**Attack risks**

Data leak: Multi-tenant isolation failure may lead to data confusion or leaks between tenants, potentially including sensitive information or personal identification information.
Decrease in Trust: Security incidents may undermine users' trust in cloud service providers.

**Mitigation measures**

Mitigation method
Description




Strengthen access control
Through access control lists (ACLs)、Role-based access control (RBAC) and other permission control mechanisms, strengthening access control over system resources


Resource monitoring
Monitor resource usage to timely detect abnormal behaviors such as resource hijacking or abuse

**Reference**

https://xie.infoq.cn/article/536a3e7e776eb32b38d1a9747
https://www.helloaliyun.com/tutorial/1039.html
https://support.huaweicloud.com/usermanual-gaussdbformysql/gaussdbformysql_05_0347.html

---
### Cloud platform security vulnerabilities

> Risk number: GAARM.005
> Lifecycle: Deployment phase

**Attack overview**

Large model applications usually require cloud platform environments to complete training and inference tasks due to high computational demands, making the security of cloud platforms crucial for the safety of large models. However, due to technical flaws in cloud platforms、Technical vulnerabilities、Security risks arising from a lack of multi-factor authentication, among other reasons, allow attackers to exploit these security issues to launch malicious attacks on large models deployed in the cloud, such as reading sensitive data.、Illegally stealing and using account credentials, causing a series of losses to the platform, including but not limited to data leakage.、Service disruption、Malicious code execution, etc. These attacks not only affect the security of large models but may also pose a threat to other users of the cloud service.

**Attack Cases**

Case
Description




Case One
Amazon SageMaker NotebookService discoveryCSRFVulnerabilities, attackers may exploit vulnerabilities to read sensitive data and perform arbitrary operations in customer environments


Case two
Due toLaravel Version ( CVE-2021-3129 ) The system has security risks, is vulnerable to attacks, allowing attackers to exploit fromLaravelStolenAWSCredentials, illegal probing of the cloud hosting model services that this credential can be used for, victim's daily losses can exceed46000Dollar

**Attack risks**

Data Leakage: Due to security vulnerabilities in cloud applications、InsecureAPICauses such as these may lead to sensitive information being accessed or disclosed by unauthorized third parties, resulting in serious privacy and compliance issues.
Unauthorized access to model application: Security vulnerabilities in cloud platforms may lead to the risk of unauthorized access in the model applications deployed by users.

**Mitigation measures**

Mitigation method
Description




Strict Access Control
Ensure that only authenticated and authorized users can accessAPIEndpoints


Principle of least privilege
Implement the principle of least privilege to ensure users and processes only have the access rights necessary to complete their tasks

**Reference**

https://developer.aliyun.com/article/1430094

---
### Exploiting insecure system configurations

> Risk number: GAARM.0003
> Lifecycle: Deployment phase

**Attack overview**

This risk refers to the infrastructure environment where the model is deployed, with attackers targetingMLModel deployment system、Deploying a cluster environment.、deploy container environment、There are a series of insecure system configurations in the mirror push management environment, which can lead to various attack behaviors targeting the model base environment.


Unauthorized access: Misconfiguration may lead to exposure of sensitive ports or weakening of authentication mechanisms, allowing unauthorized users to access system resources;


Container Security Risks: Insecure container configurations may include unnecessary permissions、Sensitive File Mounting、Or container escape vulnerabilities;


Cluster Security Risks: InKubernetessuch clusters,RBACConfiguration may lead to privilege escalation or lateral movement attacks;


Image security risks: Unsafe system configuration leads to images being transmitted、Management、Risks such as leakage may occur in stages like deployment;


Environmental isolation risk: misconfigurations may lead to isolation failures, allowing attackers to access or affect other containers or hosts;

**Attack Cases**

Case
Description




Case One
ShadowRayThe first known targeting actively exploited in the wild AI Attack activity of workloads

**Attack risks**

Malicious operations: If the system is misconfigured, attackers may exploit these vulnerabilities to gain access to the system, leading to malicious operations.
Data leakage: An attacker may gain access to sensitive data, such as file system information on the host machine or within the cluster.secrets.
Service interruption: An attacker may compromise the host or cluster services, making the service unavailable.
Lateral movement: Attackers may use escaped containers or escalated nodes as a springboard to further attack other systems within the internal network.
Persistence Control: Attackers may install backdoors in the host machine or cluster to achieve long-term control.

**Mitigation measures**

Mitigation method
Description




Principle of least privilege
Ensure containers and cluster components have only the minimum permissions necessary to complete their tasks


Ensure secure system configuration
Avoid using privileged containers, configure appropriatelyRBAC, restrictionsAPIServerAccess, avoiding unnecessary risk exposure


Regular updates and patch management
Timely update containers and cluster components, apply security patches, and reduce the risk of vulnerability exploitation

**Reference**

https://pradiptabanerjee.medium.com/confidential-containers-for-large-language-models-42477436345a

---
### Vulnerability in vector databases

> Risk number: GAARM.0005 (Sub-risk-1, parent risk: Deployment Environment Component Supply Chain Vulnerability)
> Lifecycle: Deployment phase

**Attack overview**

RAGDuring the application development process, various local document data can be accessed through Text Classify into shorter segments and utilize embedding The model vectorizes the text content and ultimately stores it in the vector database. The vector database is inRAGPlays an important role in application architecture, especially when handling high-dimensional data and performing approximate nearest neighbor (ANN) during queries. Due to the importance of vector databases, if vulnerabilities exist, attackers can exploit them to gain unauthorized data access.、Tamper with data、Execute malicious code or initiate other attacks to obtain sensitive information、Remote control of malicious code and other purposes can lead to data loss.

**Attack Cases**

Case
Description




Case One
UtilizeQdrantVector databaseAPIAchieve file upload after path traversal, leading to remote code execution risk


Case two
anything-llmExistenceCVE-2024-0551Vulnerabilities, unauthorized attackers can download files from the database through vulnerabilities.


Case three
This study proposes a generation module for RAG Enhancement LLMs New attack methods that harm the victim by injecting a single malicious document into its knowledge database RAG The system, thereby triggering various malicious attacks against generative models.

**Attack risks**

Data tampering: Attackers exploit vector database vulnerabilities to tamper with embedded vectors, leading to data in the database being altered, thus affecting data integrity.
User privacy violation: Personal identification and other sensitive information may be stored in the vector database, and if obtained by attackers, it will severely violate user privacy.

**Mitigation measures**

Mitigation method
Description




Regularly update patches
Stay updated with the latest patches from the vector database provider, regularly updating the database software ensures protection against known vulnerabilities


Data backup
Regularly back up data to ensure quick recovery when data is tampered with


Monitoring and logging
Implement real-time monitoring and logging to promptly detect and respond to suspicious activities

**Reference**

https://ironcorelabs.com/security-risks-rag/

---
### Container&&Cluster System Vulnerability

> Risk number: GAARM.0005 (Sub-risk-2, parent risk: Deployment Environment Component Supply Chain Vulnerability)
> Lifecycle: Deployment phase

**Attack overview**

Vulnerability risks of containers and cluster systems in large model deployment environments mainly involve potential security issues that container technologies and cluster management systems may have in large model deployment and operation environments. Attackers can exploit these vulnerabilities to execute malicious code、Data theft、Interfering with service operation, etc., leading to privacy information leakage issues, thus threatening the security and stability of large models.

**Attack Cases**

Case
Description




Case One
OPENAIUsedDockerMirror version existsCVE-2023-28432Vulnerability, exploiting this vulnerability can obtain keys and other information

**Attack risks**

Container escape: An attacker may achieve container escape through vulnerabilities within the container, gaining access to the host or other containers.
Cluster risk diffusion: Vulnerabilities in a single container can lead to risk diffusion across the entire cluster.

**Mitigation measures**

.



Mitigation method
Description




Timely updates to related components
Regular UpdatesKubernetesAnd its related components (such asDocker、containerdetc.) to the latest version to fix known security vulnerabilities


Strict Access Control
Implement strict access control policies, limiting communication between containers and between containers and external clusters

**Reference**

https://www.securityweek.com/chatgpt-data-breach-confirmed-as-security-firm-warns-of-vulnerable-component-exploitation/

---
### Model deployment service vulnerability

> Risk number: GAARM.0004.001
> Lifecycle: Deployment phase

**Attack overview**

MLModel deployment service vulnerabilities may exist in the model's interface、Support libraries, or applications interacting with the model, such as stealing model parameters through specific vulnerabilities、Tampering with model prediction results、Directly control the service that hosts the model, etc. Through vulnerabilities, attackers can conduct attacks on the system, such as reading arbitrary files、Implanting backdoors to gain control of the system, etc. Due toMLModel deployment services typically support pushing models for deployment locally in a containerized form、Cloud platformMLHosted service、CloudK8SClusters and other multiple target environments; hence onceMLIf the model deployment service is attacked, it will pose a risk of control permissions being compromised in multiple downstream environments.

**Attack Cases**

Case
Description




Case One
MLFlowThere is a file reading vulnerability in the system, allowing attackers to read any file on the target server


Case two
BentoMLDeserialization code execution vulnerability exists, attackers can exploit it by sending a singlePOSTRequest to trigger the exploit

**Attack risks**

Supply Chain Attack: If the supply chain of the deployment tool is penetrated by attackers, they may implant backdoors in the tool, thereby gaining control of the whole system.
Data leak:MLOpsThe software involves key stages of training and deploying multiple models; once controlled, it can lead to compromised training data.、The leakage of sensitive information such as model parameters.
Model Tampering: The model's parameters or logic may be altered by attackers, leading to incorrect prediction results.

**Mitigation measures**

Mitigation method
Description




Security updates and audits
Regular updates and audits of model deployment software to fix vulnerabilities and enhance security


Access Control
implement strict access control measures to ensure that only authorized users can access and modify deployed models


Monitoring and logging
Implement real-time monitoring and logging to promptly detect and respond to suspicious activities

**Reference**

http://www.bimant.com/blog/top8-ml-model-deployment-tools/
https://mlflow.org/docs/latest/deployment/index.html

---
### Model Image Contamination

> Risk number: GAARM.0004.002
> Lifecycle: Deployment phase

**Attack overview**

This risk refers to the phase after the model has completed training and fine-tuning, when the model image is about to be released for deployment in the production environment (self-built environment、Public cloud or third-party infrastructure), the lack of adequate security measures during this publishing process (such as encrypted signatures for the model image transmission process) allows attackers to control the operation of infected systems through image contamination, posing risks of image files being hijacked or tampered with, impacting the decision-making process of the model and creating security vulnerabilities.

  

Model image push deployment

**Attack Cases**

Case
Description




Case One
Attackers controlCI/CDThe system's image deployment process, implanting backdoor code or stealing sensitive data in the image

**Attack risks**

Command execution: Through image pollution, attackers can control the operation of the infected system and execute arbitrary commands.
Model decision impact: Malicious model images contamination may affect the model's decision-making process, creating security risks.

**Mitigation measures**

Mitigation method
Description




Image signature
Use image signing and verification mechanisms to ensure the integrity of image content


Trusted hardware usage
Based on trusted execution environments like confidential containers, ensuring the confidentiality of dynamic operational data、Integrity and security


Mirror scanning
Conduct security scans on container images before deployment to detect and fix known vulnerabilities

**Reference**

https://www.docker.com/blog/llm-docker-for-local-and-hugging-face-hosting/
https://collabnix.com/large-language-models-llms-and-docker-building-the-next-generation-web-application/
https://mp.weixin.qq.com/s/vIDHBLbA5iWoPlYTKHSZfw

---
### Environmental Isolation Defects

> Risk number: GAARM.0003.001
> Lifecycle: Deployment phase

**Attack overview**

This risk refers to the container deployment stage,LLMsThe operating environment and physical environment of business applications have configuration or design flaws that isolate sandbox environments, and applications in sandbox environments such as containers or virtual machines may escape the sandbox environment and access or manipulate external resources, leading to security vulnerabilities. Therefore, even if attackers are restricted to the container, they can exploit misconfigurations (privileged containers、Error file mounting, etc.) to bypass isolation and access resources and sensitive systems outside the container, thus leveraging the executor for unauthorized access or othersLLMsAccidental operations bring unexpected risks such as executing unauthorized commands.

  

Execution environment isolation architecture

Due toLLMsInteraction with the external environment needs to be achieved through execution bodies, using the cluster environment's.PodQuickly start the execution body to achieve specific interactive operations, which is common in execution body environment isolation architecture. During this process, targeting networks、File、Process andPodMultiple environments are not properly isolated, leading to unexpected risks.

**Attack Cases**

Case
Description




Case One
Hugging FaceModel runtime environment has not set up external network access restrictions, allowing attackers to obtain production environmentshellControl permissions

**Attack risks**

Container escape: Inadequate environmental isolation can lead to container escape issues, allowing attackers to gain control over the host system and even access data in other containers.
Sensitive database access: attackers gain access through carefully constructed prompts (prompts), indicatingLLMExtract and leak confidential information from sensitive databases.
System-level operations: ifLLMPermitted to execute system-level operations, attackers may manipulate it to execute unauthorized commands on the underlying system.

**Mitigation measures**

Mitigation method
Description




Strict Access Control
Implement Role-Based Access Control (RBAC) strategy to ensure that only authorized personnel can access the operating environment


Network isolation
Use network policies to restrict inter-container、Inter-cluster and external access permissions, reducing potential attack surfaces and risks


Implement sandbox techniques
Use appropriate sandbox techniques to isolateLLMEnvironment, preventing interaction with key systems and resources

**Reference**

https://cloud.baidu.com/article/621826
https://owasp.org/www-project-top-10-for-large-language-model-applications/Archive/0_1_vulns/Inadequate_Sandboxing.html

---
### Deployment Environment Component Supply Chain Vulnerability

> Risk number: GAARM.0005 (Parent risk, including sub-risks.: Vulnerability in vector databases、Container&&Cluster System Vulnerability)
> Lifecycle: Deployment phase

**Attack overview**

Deploying environmental supply chain vulnerabilities (Supply Chain Vulnerabilities in Deployment Environments) refers to the raw materials (such as libraries) in the software supply chain and deployment process、Dependencies、Security flaws existing in the stages from development tools to final products (such as deployed software) may lead to risks of system attacks or data leakage. Supply chain vulnerabilities can be exploited during software deployment, leading to reduced system security, data leakage, or service disruption. Mainly divided into three categories:


Container&&Cluster system vulnerability: Container technology and cluster management systems may have security issues, attackers can exploit these vulnerabilities to execute malicious code、Data theft、Interfering with service operation, etc., leading to privacy information leakage issues, thus threatening the security and stability of large models.


Vector database vulnerabilities: If there are vulnerabilities in the vector database, attackers can exploit these vulnerabilities to gain unauthorized data access.、Tamper with data、Execute malicious code or initiate other attacks to obtain sensitive information、Remote control of malicious code and other purposes can lead to data loss.


Cloud platform security vulnerabilities: If there are technical flaws in the cloud platform、Technical vulnerabilities、Security risks arising from a lack of multi-factor authentication, among other reasons, allow attackers to exploit these security issues to launch malicious attacks on large models deployed in the cloud, such as reading sensitive data.、Illegally stealing and using account credentials, causing a series of losses to the platform, including but not limited to data leakage.、Service disruption、Malicious Code Execution, etc.

**Attack Cases**

See specific sub-risk

**Attack risks**

Data Leakage: Attackers may access sensitive data, and sensitive information being accessed or disclosed by unauthorized third parties can cause serious privacy and compliance issues.
Unauthorized access to model application: Security vulnerabilities in cloud platforms may lead to the risk of unauthorized access in the model applications deployed by users.
User privacy infringement: Sensitive information such as stored personal identity, once obtained by an attacker, will severely violate user privacy.

**Mitigation measures**

Mitigation method
Description




Principle of least privilege
Ensure that components only have the minimum permissions necessary to complete their tasks


Regular updates and patch management
Timely update components, apply security patches, and reduce the risk of vulnerability exploitation

---
## Training Phase

### Model development tool vulnerabilities

> Risk number: GAARM.0001.001
> Lifecycle: Training Phase

**Attack overview**

Model development training involves data preprocessing、Feature engineering、Model selection、Training、Multiple steps such as evaluation and deployment. If the tools used in this process have security vulnerabilities, it can put the entire machine learning process at risk. Attackers can exploit these vulnerabilities to tamper with model training data.、Theft of model parameters、Or perform specific attacks after model deployment, leading to inaccurate model outputs、Parameters were stolen、Spread of malware and other severe security consequences.

**Attack Cases**

Case
Description




Case One
TensorflowThere is a code execution vulnerability, and there is a code execution risk when loading the model


Case two
PytorchThere is a code execution vulnerability that allows malicious code to be executed on the target system in the context of the user running the program, posing a risk of executing harmful code.


Case three
This document covers TensorFlow Different use cases of , outlining TensorFlow The issues of existing security vulnerabilities, where different use cases bring different risk outcomes.

**Attack risks**

Supply Chain Attack: Attackers can implant malicious code intoMLLegitimate software packages for development, implementing dependency chain attacks, thus spreading malware during distribution.
Model poisoning: attackers inject malicious data into training data, affecting the model's decision-making process, leading to inaccurate model output or bias.
Intellectual property loss: If model parameters are stolen, attackers may replicate or illegally use the model.

**Mitigation measures**

Mitigation method
Description




Regularly Update and Patch
Keep all development tools and libraries up to date to leverage the latest security fixes


Secure dependency chain
Review dependency chains to ensure all third-party libraries and packages come from trusted sources

**Reference**

https://www.secrss.com/articles/64006
https://huntr.com/bounties/a795bf93-c91e-4c79-aae8-f7d8bda92e2a

---
### Training data management system vulnerabilities

> Risk number: GAARM.0001.002
> Lifecycle: Training Phase

**Attack overview**

The training data management system is responsible for storage、Processing、Annotate and provide data, delivering prepared data to the model for learning. When the system has supply chain-related security vulnerabilities, attackers can exploit these vulnerabilities to tamper with data.、Steal data, even affect model training results through data poisoning.

**Attack risks**

Data poisoning attack: Attackers may inject malicious data into training data, affecting the model's decision-making process, leading to inaccurate predictions or biases.
Model stealing attack: Attackers attempt to reverse engineer the model by querying it to obtain the model's parameters or training data, thereby stealing intellectual property.
Data leakage: Attackers obtain sensitive training data through unauthorized access.

**Mitigation measures**

Mitigation method
Description




Security updates and audits
Regularly update and audit the training data management system to fix vulnerabilities and enhance security


Monitoring and logging
Implement real-time monitoring and logging to promptly detect and respond to suspicious activities

**Reference**

https://doc.dataiku.com/dss/latest/concepts/homepage/index.html
https://www.secrss.com/articles/62742

---
### Training environment security risks

> Risk number: GAARM.0001
> Lifecycle: Training Phase

**Attack overview**

This risk refers to the deep learning frameworks (such as those used in the model's training and development environment)TensorFlowOrPyTorch) and necessary dependency libraries and other application development components. If the referenced frameworks themselves have security vulnerabilities, they could affect downstreamLLMsApplications cause supply chain attacks, thereby affecting training data、MLIntegrity of models and deployment platforms.

**Attack Cases**

Case
Description




Case One
OpenAIThe provided example code for the integrated plugin contains a vulnerabilityMinIO dockerImages, this vulnerability may lead to key and password leaks;ChatGPTUsedRedis-pyVulnerabilities in the library causing users' chat history and payment information


Case two
Open source machine learning frameworkPyTorchSignificant Hierarchical Vulnerabilities ExistCVE-2024-5480, attackers can use it to remotely attack distributed trainingmasterNodes, once these nodes are compromised, the attacker has the opportunity to steal associatedAIRelevant sensitive materials


Case three
PyTorchUsed by the modelpickleFormat can be weaponized by threat actors to execute arbitrary code and deployCobalt Strike、MythicandMetasploitAttack payloads, attackers can use maliciousPyTorchBinary file corrupting hosted conversion services, and damaging file hosting systems

**Attack risks**

User privacy leakage: as shown in case one, becauseRedis-pyLibrary'sbug,ChatGPTUsers' chat titles and conversation contents may be visible to other users, leading to user privacy data leakage.
System integrity compromised: Attackers may exploit vulnerabilities to compromise system integrity, affectingLLMsReliability and availability of the service.

**Mitigation measures**

Mitigation method
Description




Security updates and audits
Regularly update and audit service software in training and development environments to fix vulnerabilities and enhance security


Security auditing and monitoring
Regularly conduct security audits, use monitoring tools to detect and alert suspicious behavior, and implement effective logging.

**Reference**

https://llmtop10.com/llm05/

---
### Training environment isolation flaws

> Risk number: GAARM.0002
> Lifecycle: Training Phase

**Attack overview**

Training environment isolation refers to dividing the debugging and running environments into two completely isolated areas to prevent penetration attacks from the debugging environment to the running environment. In the debugging environment, program logic can be modified but only desensitized data can be used; whereas in the running environment, real full data can be manipulated, and operations are subject to scrutiny, the results are traceable and accountable. If there are defects in the training environment isolation, unauthorized users may access sensitive data by entering the running test environment from the development environment, giving attackers an opportunity.

**Attack Cases**

Case
Description




Case One
Defects in training environment isolation, leading to attackers entering the runtime testing environment from the developer environment, thereby causing risks such as training data leakage

**Attack risks**

Data Leakage: Attackers may access and steal sensitive data stored in the operating environment; the leakage of this data could lead to significant economic losses and legal liabilities.
Gaining system control: If the attacker infiltrates the runtime environment, they may gain system control and manipulate data access、Resource management and system settings.

**Mitigation measures**

Mitigation method
Description




Strengthened isolation measures
Use security technologies and best practices to strengthen the isolation between debugging and production environments


Access Control
Implement Role-Based Access Control (RBAC) strategy to ensure that only authorized personnel can access the operating environment


Security sandbox technology
Will.LLMIsolate and protect the runtime environment to prevent external attacks and interference


**Reference**

- https://cloud.baidu.com/article/621826

---

## Twenty、Container and sandbox escape practical testing methodology

> TargetingAIApplication deployment environment (Docker/Sysbox/Daytona/Kubernetes) systematic escape and isolation testing
> **General container deployment security**: WebApplication Container Deployment Security Check → [web-deployment-security.md §Two](web-deployment-security.md)

### One、Overview of the testing process.

```
Information gathering → Environment identification → Isolation assessment → Escape attempts → Persistent verification → Horizontal movement → Report
```

### Two、Information gathering phase

#### 2.1 Container runtime identification

| Detection Items | Command | Basis for Judgment |
|--------|------|----------|
| Whether in a container | `cat /proc/1/cgroup` | Contain`docker`/`kubepods`/`containerd` |
| DockerFlag file | `ls /.dockerenv` | File exists then isDockerContainer |
| Container runtime type | `cat /proc/1/cgroup \| head` | `sysbox-fs`→Sysbox, `docker`→Docker |
| Kernel version | `uname -r` | MatchingCVEImpact scope |
| User Namespace | `cat /proc/self/uid_map` | `0 0 4294967295`→No isolation(Danger) |
| Capabilities | `cat /proc/self/status \| grep Cap` | Check for dangers after decodingCap |
| Seccomp | `cat /proc/self/status \| grep Seccomp` | 0=disabled, 2=filter |
| AppArmor | `cat /proc/self/attr/current` | `unconfined`→No protection |
| Mount point | `mount \| grep -v overlay` | Detecting sensitive path mounting on the host machine |

#### 2.2 Sysbox Specific detection

| Detection Items | Method | Security impact |
|--------|------|----------|
| CE vs EEVersion | `sysbox-runc --version` Or checkUIDMapping Range | CEShared mapping has cross-tenant risks |
| UIDMapping Exclusivity | `cat /proc/self/uid_map`, CEUsually`0 165536 65536`(Share) | Shared Mapping→Cross-Container Privilege Escalation Possible |
| Virtualization/proc | `ls /proc/sys/net/` | SysboxDegree of virtualization |
| Docker-in-Docker | `docker ps 2>/dev/null` | Inner LayerDockerMay have no security restrictions |
| /dev/kvm | `ls /dev/kvm` | KVMAvailable→Nested virtualization escape |

### Three、Isolation evaluation phase

#### 3.1 Process isolation

```bash
# PID NamespaceCheck
ps aux   # Can see other containers/Host process
ls /proc/*/cmdline   # Enumerate Visible Processes

# IfPID 1Not a containerinitButsystemd/dockerd → Isolation failure
cat /proc/1/cmdline | tr '\0' ' '
```

#### 3.2 Network isolation

```bash
# Network interface
ip addr   # Check network interfaces andIPSegment
ip route  # Routing table, whether it can reach other network segments

# Same subnet scanning(Discover neighboring containers)
for i in $(seq 1 254); do
  (ping -c 1 -W 1 $SUBNET.$i &>/dev/null && echo "$SUBNET.$i alive") &
done; wait

# InternalDNSDetection
cat /etc/resolv.conf
nslookup kubernetes.default.svc.cluster.local 2>/dev/null
```

#### 3.3 File System Isolation

```bash
# Check host file system mounts
mount | grep -E "ext4|xfs|btrfs" | grep -v overlay
findmnt

# Path traversal test
ls -la /var/lib/sysbox/ 2>/dev/null
ls -la /var/lib/docker/ 2>/dev/null
ls -la /run/containerd/ 2>/dev/null

# Symbolic link escape
ln -s /proc/1/root/etc/shadow /tmp/test_escape
cat /tmp/test_escape 2>&1  # If successful→Isolation failure
```

### Four、Escape testing matrix

| Escape Path | Prerequisites | Danger level | Test method |
|----------|----------|----------|----------|
| cgroup release_agent | CAP_SYS_ADMIN + cgroup v1 | Critical | Writerelease_agentExecute host machine commands |
| Docker Socket | /var/run/docker.sockExpose | Critical | PassAPICreate privileged containers |
| /proc/1/root | PID NamespaceNot isolated | Critical | Direct read/write to host machine files |
| Privileged container | --privilegedPattern | Critical | mountHost disk |
| runc fdDisclosure | CVE-2024-21626 | High | Utilize/proc/self/fdAccess to host |
| Dirty Pipe | CVE-2022-0847, 5.8≤kernel≤5.16.11 | High | Overwriting read-only files for privilege escalation |
| OverlayFS | CVE-2023-0386, 5.11≤kernel≤6.2 | High | SUIDFile privilege escalation |
| Sensitive mount | Host path ismountEnter container | High | Write to host machine file |
| CAP_DAC_READ_SEARCH | CapabilityUnrestricted | Medium | open_by_handle_atRead file |
| CAP_SYS_PTRACE | CapabilityUnrestricted | Medium | Inject into host machine process |
| Docker-in-Docker | Inner LayerDockerUnlimited | Medium | Create Privileged Container in Inner Layer |

### Five、Persistence testing

> Validate the feasibility of sandbox cross-session persistence attack (especially suitable for persistent sandboxes likeDaytona)

| Test items | Session1Operation | Session2verification | Expected security outcomes |
|--------|-----------|-----------|-------------|
| .bashrcBackdoor | `echo 'malicious_cmd' >> ~/.bashrc` | Open NewshellCheck whether executed | New sessions do not inherit/Reset |
| Crontab | `echo "* * * * * cmd" \| crontab -` | `crontab -l` | CrontabCleared or unavailable |
| SSHKey | Write~/.ssh/authorized_keys | SSHConnection tests | SSHService Unavailable or Key Cleanup |
| Background processes | `nohup cmd &` | `ps aux \| grep cmd` | Process termination after session closure |
| File poisoning | Workspace writes malicious files | AIWhether to read and execute | AIDo not automatically execute instructions in files |
| Historical residue | InshellInput sensitive commands | `cat ~/.bash_history` | Clear historical commands across sessions |
| Environment Variables | `export SECRET=leaked` | `echo $SECRET` | Environment variables are not retained across sessions |

### Six、Lateral movement testing

```
Inside the container → Internal network service discovery → Database/Cache/APIDirect connection → Other Tenant Sandbox
         ↓
         Cloud metadata service(169.254.169.254) → IAMCredential theft → Cloud resource access
         ↓
         K8s API(kubernetes.default.svc) → PodList/SecretObtain
```

| Objective | Detect command | Utilization method |
|------|----------|----------|
| Cloud metadata | `curl 169.254.169.254` | ObtainIAMTemporary credentials |
| K8s API | `curl -k https://kubernetes.default.svc` | EnumeratePod/ObtainSecret |
| K8s ServiceAccount | `cat /var/run/secrets/kubernetes.io/serviceaccount/token` | AuthenticationK8s API |
| Intranet database | `echo \| nc DB_HOST 5432` | Directly connect to the database |
| Redis | `redis-cli -h REDIS_HOST ping` | Unauthorized access |
| Docker Registry | `curl http://REGISTRY:5000/v2/_catalog` | Pull Sensitive Images |

### Seven、Defense verification.Checklist

```
[ ] Container in a nonrootUser Running(OrUser NamespaceIsolation effective)
[ ] No excessCapabilities(Principle of least privilege: OnlyNET_BIND_SERVICEAnd other requirements)
[ ] Seccomp profileHas been enabled(Nondisabled)
[ ] AppArmor/SELinuxNonunconfined
[ ] /var/run/docker.sockNot exposed
[ ] Not based on--privilegedMode operation
[ ] No host sensitive path mounting(/、/etc、/var/run)
[ ] Kernel version not affected by known escapesCVEImpact
[ ] cgroup v2Orrelease_agentNot writable
[ ] PID NamespaceIsolation effective(Only see own processes)
[ ] Network Policy/Firewall restricts inter-container communication
[ ] 169.254.169.254Metadata service intercepted
[ ] Sensitive Data Between Sessions(history/credentials)Cleared
[ ] Completely clear all user data when the sandbox is destroyed.
[ ] SysboxUseEEVersion or exclusiveUIDMapping
```

---
