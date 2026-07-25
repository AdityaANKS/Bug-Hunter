# AIIdentity security - Training Phase

> Source: AISSGreen Alliance Large Model Security Intelligence Chain Community | Dismantled From ai-identity-security.md
> Phase: Training phase (permission design flaws)/Environmental authentication)

## Training Phase

### LLMsPlugin: Permissions control design flaw

> Risk number: GAARM.0048
> Lifecycle: Training Phase

**Attack overview**

This risk refers toLLMsIn the plugin, there are design flaws in permission control.LLMA plugin is a type that provides interactive functionality.AgentProxy, when enabled, will be automatically invoked by the model during user interactions. This automatic invocation poses uncontrolled risks, such as one plugin potentially exploiting another plugin's permissions to access and obtain sensitive data or functions that it cannot directly access, giving attackers the possibility to construct malicious requests for attacks. In summary, this flawed access control allows users to directly schedule sensitive function plugins, or there are erroneous permission controls between plugins, ultimately leading users to provide malicious input, resulting in security risks, including data leakage、Remote code execution and privilege escalation.

**Attack Cases**

Case
Description




Case One
LangChainProvides many tools to buildLLMPlugins, when the design of these plugins does not prioritize security, attackers can use prompt injection to compromise the behavior of poorly designed plugins

**Attack risks**

Sensitive information leakage: Plugins with improperly designed permission control may be called by attackers to request permissions for another plugin, accessing and obtaining data or functionality from other plugins; this tiered invocation may lead to the leakage of many sensitive information.
Remote code execution: By injecting malicious code or data, attackers may attempt to gain a foothold in the system to further control or disrupt it.

**Mitigation measures**

Mitigation method
Description




Enforce Strict Parameterized Input
check the type and range of input. If this is not possible, introduce a second layer of typed calls to parse requests and apply validation and sanitization


Minimum privilege access control
Expose the least functionality possible while still performing the required functions

**Reference**

https://genai.owasp.org/wp-content/uploads/2024/05/OWASP-Top-10-for-LLM-Applications-v1_1_Chinese.pdf
https://developer.nvidia.com/zh-cn/blog/securing-llm-systems-against-prompt-injection/

---
### Training environment lacks authentication authorization

> Risk number: GAARM.0046
> Lifecycle: Training Phase

**Attack overview**

This risk refers to the lack of strict access control and authentication mechanisms during the training phase of the model, exposing the internal training data of the model、Training infrastructure、Training frameworks and other resources can be accessed by individuals with insufficient permissions, which may lead to the leakage of sensitive data in the model, making the model's training data transparent, increasing the risk of model poisoning.

**Attack Cases**

Case
Description




Case One
ShadowRayIn the event, the attacker exploits.RayFramework'sCVE-2023-48022Vulnerability, unauthorized schedulingJobs APIImplementRCEAttack

**Attack risks**

Sensitive information leakage: Unauthorized access to training data leads to sensitive information leaks.
Model quality decline: malicious tampering with training data may affect the model's learning effectiveness, resulting in inaccurate or biased model outputs.
High-value resource abuse: Attackers exploit unauthorizedAPIAccess to control the computing power of high-value resources to conduct cryptocurrency mining and other activities.

**Mitigation measures**

Mitigation method
Description




Strengthen authentication and access control policies
Implement access control and authentication mechanisms to prevent unauthorized accessLLMsTraining environment and its data


Data Encryption and De-sensitization
Introduce encryption and privacy protection measures for training data to prevent the leakage of sensitive information.

**Reference**

https://blog.csdn.net/qq_43543209/article/details/135683986

---
### Over-privileged training environment

> Risk number: GAARM.0047
> Lifecycle: Training Phase

**Attack overview**

The risk of excessive permissions allocation during the training phase of large models mainly involves data access、Security issues arising from excessive permission allocation during model training and system management processes may lead to unauthorized access or misuse risks. If attackers illegally obtain developer control permissions, they may exploit these excessive privileges to access the training data of models illegally.、Tampering or destruction, thereby affecting the quality and safety of the model.

**Attack Cases**

Case
Description




Case One
Attackers obtain training developers' control permissions through phishing and other means, using high-privilege account credentials to access sensitive training data or maliciously tamper with the model

**Attack risks**

Sensitive data leakage: If the developer's training environment has excessive control permissions with unnecessary permissions, when the developer's account credentials are compromised, attackers may access more internal information through redundant permissions, possibly resulting in the leakage of training data, especially when the data contains sensitive information.
Model Quality Degradation: Attackers tampering with training data may impact the learning effectiveness of the model, resulting in inaccurate or biased outputs.

**Mitigation measures**

Mitigation method
Description




Principle of least privilege
Ensure each user or system component has only the minimum permissions necessary to complete its tasks


Data Encryption and De-sensitization
Introduce encryption and privacy protection measures for training data to prevent the leakage of sensitive information.


Access control and auditing
Implement strict access control policies and conduct regular security audits to monitor and record all access to data and models

**Reference**

https://www.pulumi.com/ai/answers/mptvxaHguJ6A4yXSHi92zZ/implementing-role-based-access-to-ai-training-data-in-snowflake

---
