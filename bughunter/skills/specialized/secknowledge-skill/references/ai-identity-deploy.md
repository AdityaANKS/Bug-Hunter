# AIIdentity security - Deployment phase

> Source: AISSGreen Alliance Large Model Security Intelligence Chain Community | Dismantled From ai-identity-security.md
> Phase: Deployment stage (unauthorized access/Credential abuse)

## Deployment phase

### Public serviceAPIKey exploitation

> Risk number: GAARM.0049.001
> Lifecycle: Deployment phase

**Attack overview**

This risk refers to code、Exposing services through configuration and other meansAPIAccessToken(Authentication credentials), attackers may illegally gain access to the model deployment environment, leading to data leakage、Model manipulation and other security risks.

**Attack Cases**

Case
Description




Case One
AICybersecurity startupLassoFound more than1600IndividualHugging Face APITokens leaked in the codebase, affecting hundreds of organizational accounts

**Attack risks**

Account leak: leakedAPITokens may lead to unauthorized access to company organization accounts.
Data Manipulation: Attackers controlling accounts can manipulate existingAImodel" where malicious code is implanted, impacting downstream users who depend on these foundational models.

**Mitigation measures**

Mitigation method
Description




Strengthen authentication
Implement multi-factor authentication and other enhanced identity verification measures to reduceAPIRisks of token theft


Revoke LeakAPIToken
Regarding all that may have been leakedAPIThe token should be revoked and replaced immediately


Key management and rotation mechanism
Establish secure key management and rotation mechanisms, and update regularly API Token.


**Reference**

- https://www.securityweek.com/major-organizations-using-hugging-face-ai-tools-put-at-risk-by-leaked-api-tokens/
- https://aws.amazon.com/cn/what-is/api-key/

---
### Unauthorized access to vector databases

> Risk number: GAARM.0050
> Lifecycle: Deployment phase

**Attack overview**

RAGDuring the application development process, various local document data can be accessed through Text Classify into shorter segments and utilize embedding The model vectorizes the text content and finally stores it in the vector database. Attackers access the database without authorization, tampering with and destroying the model, further affecting RAG Inaccurate or malicious retrieval from the system may lead to RAG The output content of the system is also affected, along with the risks of indirect prompt injection.

  

RAGApplication Architecture Form

**Attack Cases**

Case
Description




Case One
anything-llmExistenceCVE-2024-0551Vulnerabilities, unauthorized attackers can download files from the database through vulnerabilities.


Case two
This study proposes a generation module for RAG Enhancement LLMs New attack methods that harm the victim by injecting a single malicious document into its knowledge database RAG The system, thereby triggering various malicious attacks against generative models.

**Attack risks**

Vector database corruption: Unauthorized changes may corrupt knowledge sources, leading to RAG The system performs inaccurate or malicious retrieval.
Data leakage: Sensitive information stored in the vector database has been leaked.
Indirect prompt injection risk: Attacks on the availability of vector databases may affect those depending on them RAG System.

**Mitigation measures**

Mitigation method
Description




Data Encryption
Encrypt the vector database that stores all indexes and embedded data to protect data from potential leaks or unauthorized access


Authentication and access control
Use strong user authentication and authorization mechanisms to ensure that only authorized personnel can access the database.


Backup and redundancy storage
Regular backups ensure that knowledge sources can be restored in the event of data corruption or loss


Security updates and audits
Regularly update and audit relevant vector database systems to fix vulnerabilities and enhance security

**Reference**

https://medium.com/@nitishjoshi060291/llm-hallucinations-fix-it-with-vector-database-de04eee531da
https://cloudsecurityalliance.org/blog/2023/11/22/mitigating-security-risks-in-retrieval-augmented-generation-rag-llm-applications
https://www.cnblogs.com/LittleHann/p/17440063.html#_label3
https://dongnian.icu/llms/llms_article/9.%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BALLM/index.html
https://cloudsecurityalliance.org/blog/2023/11/22/mitigating-security-risks-in-retrieval-augmented-generation-rag-llm-applications

---
### Unauthorized access to model deployment environment

> Risk number: GAARM.0051
> Lifecycle: Deployment phase

**Attack overview**

This risk refers to attackers exploitingMLConfiguration errors in the deployed platform services、Known vulnerabilities or risks such as lack of proper authentication and authorization mechanisms, achievingMLUnauthorized access to the deployment environment, further stealing sensitive data、Abuse of computing resources、DestructionAIIntegrity of the model or engage in other malicious activities.

**Attack Cases**

Case
Description




Case One
Attackers UseRayIn the FrameworkAPIUnauthorized access risks, achieving remote code execution, completing control over the target company's computing resources

**Attack risks**

Sensitive information leakage: Attackers may access and steal training data、Model Parameters、User data and other sensitive information.
Malicious operation: Unauthorized access may lead to malicious manipulation of the model, and the output results may be misleading.
Resource abuse: Attackers may use without authorizationMLUtilize computing resources in the deployment environment for mining or other computation-intensive tasks.
Model integrity compromise: An attacker may modify or contaminateAIThe training process of the model, leading to a decrease in model accuracy or producing misleading results.
Service interruption: the attacker’s actions may lead toMLService Disruption, Affecting Business Continuity.

**Mitigation measures**

Mitigation method
Description




Strengthen Authentication and Access Control
Implement access control and authentication mechanisms to prevent unauthorized accessLLMDeploy platform environment and its data, avoid usingMLDefault Authentication Policy for Platform Services


Regularly Update and Patch
Timely updatesMLPlatform and dependent libraries to fix known vulnerabilities


Model protection and secure deployment
Conduct security scans and penetration testing on the model before deployment, utilizing encryption.、Technical means such as signatures protect the confidentiality and integrity of model parameters and training data

**Reference**

https://www.leewayhertz.com/security-in-ai-development/

---
### Abuse deployment environment credentials

> Risk number: GAARM.0049
> Lifecycle: Deployment phase

**Attack overview**

In large modelsMLOpsIn the life cycle process, access credentials (such as keys or access tokens) are involved in code submissions、Build、Testing and deploying multiple phases. The risk of abusing deployment environment credentials refers to large modelsCI/CD(Continuous integration/In the continuous deployment process, used to access and deploy model servicesAPIThere are security risks in the use of keys or access tokens, and attackers can exploit this risk for credential theft、Malicious code injection and other means, causing sensitive information leakage、Malicious code injection or other security threats.

**Attack Cases**

Case
Description




Case One
Credentials hard-coded in code or configuration files, which attackers can use for lateral movement after gaining access to development machine permissions

**Attack risks**

Credential leakage: Attackers obtain developers' credentials through social engineering or other means, and then use these credentials to gain access.CI/CDSensitive data in the system or perform malicious operations.
Malicious code injection: attackers use obtained credentials to submit commits containing malicious code to the codebase, and this code is executed in subsequent build and deployment processes.

**Mitigation measures**

Mitigation method
Description




Strengthen identity authentication and password policies
Recommend users to follow appropriate password policies and implement two-factor authentication (2FA)


Code audit and automated scanning
Perform automated security scans before code submission and deployment to detect risks of hard-coded credentials and identify potential security issues


Monitoring and Alerts
Deploy monitoring systems to detect unusual access patterns or operations, issuing alerts in a timely manner

**Reference**

https://atmosphericthinking.medium.com/massive-leak-of-chatgpt-credentials-over-100-000-affected-db6cef3a18c5
https://blog.csdn.net/FreeBuf_/article/details/140870185?utm_relevant_index=7

---
