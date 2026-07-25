# AIFoundation security - Training Phase

> Source: AISSGreen Alliance Large Model Security Intelligence Chain Community | Dismantled From ai-baseline-security.md
> Phase: Training Phase (Development Tool Vulnerability/environment isolation)

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

