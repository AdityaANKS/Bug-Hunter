# AIApplication security. - Deployment phase

> Source: AISSGreen Alliance Large Model Security Intelligence Chain Community | Dismantled From ai-app-security.md
> Phase: Deployment phase (GAARM.0037-0038, 0049 APIManagement/Source code poisoning/Theft)

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
