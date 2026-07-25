# AIFoundation security - Deployment phase

> Source: AISSGreen Alliance Large Model Security Intelligence Chain Community | Dismantled From ai-baseline-security.md
> Phase: Deployment phase (container vulnerabilities/Cloud platform/Supply chain)

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
