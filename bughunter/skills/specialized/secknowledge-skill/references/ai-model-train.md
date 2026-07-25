# AIModel Security - Training Phase

> Source: AISSGreen Alliance Large Model Security Intelligence Chain Community | Dismantled From ai-model-security.md
> Phase: Training phase (GAARM.0023-0024 Model backdoor/Insufficient alignment/Poisoning pre-training)

## Training Phase

### Model backdoor

> Risk number: GAARM.0023
> Lifecycle: Training Phase

**Attack overview**

LLMBackdoors in the model mainly refer to security issues caused by introducing models from untrusted sources during the training phase.LLMModel Backdoors are mainly divided into two forms:

Model serialization backdoor: due to the use of pre-trained models, malicious instructions containing specific serialized data may be implanted, causing users to trigger deserialization operations when loading and using the model, thereby executing preset malicious commands or code;
Pre-trained Model Poisoning: The pre-trained model used may contain specific malicious training data, leading to intentional bias in the model's output, or even direct tampering with the results.

Therefore, strict measures must be taken during the model training phase to prevent the introduction and use of model backdoors.

**Attack Cases**

Case
Description




Case One
Mainly introduces methods for attacking compiled deep learning models through reverse engineering techniques. The core of the attack is to inject a malicious backdoor into the victim model to manipulate it.


Case two
By UsingROMEAlgorithm to accurately modify the model to spread misinformation when answering specific questions

**Attack risks**

System Vulnerability Exploitation: The implanted backdoor can transform into a system security vulnerability, where attackers activate the backdoor using specific triggers to control or manipulate the model's behavior.
Sensitive information leak: Backdoors allow attackers to gain unauthorized access under specific conditions, which can lead to the leakage of sensitive information, causing significant losses to individuals and organizations.
Generate toxic content: Attackers may exploit backdoors to make the model generate violence、Discrimination、Pornographic or other inappropriate content.

**Mitigation measures**

Mitigation method
Description




Data source validation
Ensure that all models and datasets used for training and deployment come from trusted sources


Model auditing and testing
Regularly audit the model, use automated tools to detect potential backdoors, and conduct stress tests to assess the robustness of the model


Secure coding practices
Follow the principle of least privilege, limit model access permissions, implement strict input validation, and reduce potential attack surfaces


Defensive training
Improve the model's resistance to backdoor attacks by introducing adversarial examples and anomaly detection mechanisms during training


Regular review
ToLLMsConduct regular security audits to assess potential security risks

**Reference**

https://atlas.mitre.org/techniques/AML.T0018
https://defence.ai/ai-security/backdoor-attacks-ml/
https://arxiv.org/abs/2308.14367

---
### Insufficient model safety alignment

> Risk number: GAARM.0033 (Note: With"Data drift"Shared number, derived fromAISSOriginal data classification)
> Lifecycle: Training Phase

**Attack overview**

LLM The security misalignment of the model during the training phase poses security risks including malicious use、Privacy infringement、Model bias、Legality and compliance issues、Errors and inaccurate outputs、Model abuse、Security vulnerabilities exposure and decrease in user trust. These risks affect the security of the model、Reliability、The user experience and the organization's legal compliance are negatively impacted. Therefore, measures must be taken during the model's development and training phases to ensure the model's safe alignment and maintain its overall health and safety.

**Attack Cases**

Case
Description




Case One
A news organization usingLLMGenerate articles on various topics. UtilizeLLMGenerated an article containing false information, which was published without verification. Readers trusted this article, leading to the spread of misinformation


Case two
A company reliesLLMGenerate Financial Reports and Analysis.LLMGenerated a report containing erroneous financial data used by the company to make critical investment decisions. Due to reliance on inaccurateLLMGenerated content has resulted in significant financial loss

**Attack risks**

Priority of harmful behavior: in cases where the target is unclear,AIThe system may mistakenly regard harmful behavior as a priority target.
Model Behavior Deviates from Expectations: Due to issues with the quality of training data or defects in the design of the reward function,AIThe model may fail to understand or execute its designed tasks correctly, leading to behavior deviating from expected use cases, increasing operational risk and potential negative social impact.

**Mitigation measures**

.



Mitigation method
Description




Clearly define the target
Clearly define during the design and development processLLMTarget and expected behavior


Consistency between the reward function and training data
Ensure that the reward function and training data are consistent with the expected results, and minimize harmful behavior

**Reference**

https://owasp.org/www-project-top-10-for-large-language-model-applications/Archive/0_1_vulns/Inadequate_AI_Alignment.html

---
### Model serialization backdoor

> Risk number: GAARM.0023.001
> Lifecycle: Training Phase

**Attack overview**

This risk refers to the possibility that an attacker may construct a specific persistent model file containing malicious serialized data, so that when the user loads and uses the model, it triggers a deserialization operation, thereby executing pre-set malicious commands or code. IfLLMThe model's deserialization mechanism has not received adequate security controls, allowing attackers to exploit it to bypass security measures, execute unauthorized operations, and possibly take control of the entire system.

**Attack Cases**

Case
Description




Case One
The attacker uploads containing malicious commandsPickleModel file toHugging faceService, achieve command execution obtainedHugging FaceContainer permissions, which may lead to system damage


Case two
Attacker abuse pickle Format to deploy malware, secretly embedding malware into machine learning models, and using standard data deserialization libraries (i.e.pickle ) Executed automatically.


Case three
Hugging FaceInPyTorchThe model is loadingPickleAfter the file, code execution will occur


Case Four
Keras 2 LambdaThere are risks at this layer, allowing attackers to inject malicious attack code

**Attack risks**

Execute arbitrary malicious code: Through carefully crafted model serialization files, attackers can execute arbitrary code on the target system, which may lead to system damage、Sensitive data leakage or systems being controlled by attackers.
Supply chain attack: Due toPickleFiles like these are mainstream model distribution files. Attackers can launch supply chain attacks by compromising the model or its dependent libraries, affecting a broader user base.
Cross-tenant attacks: In a cloud service or shared service environment, attackers may exploit maliciouspickleFiles for cross-tenant attacks, jumping from one compromised instance to another, affecting more users and systems.

**Mitigation measures**

Mitigation method
Case




Code auditing
Conduct thorough code audits when processing machine learning models from untrusted sources to identify and remove possible malicious code or backdoors


Model Isolation
For untrusted models that must be used, isolation technologies such as containerization should be adopted to ensure that even if the model is compromised, the attacker cannot escape to the host system or other networks


Access Control
Implement strict access control measures to ensure that only authorized users and systems can access and use machine learning models

**Reference**

https://wiki.offsecml.com/Supply+Chain+Attacks/Models/Using+Keras+Lambda+Layers


https://5stars217.github.io/2023-08-08-red-teaming-with-ml-models/


https://splint.gitbook.io/cyberblog/security-research/tensorflow-remote-code-execution-with-malicious-model

---
### Unsecure Dependence on Pre-trained Models

> Risk number: GAARM.0024
> Lifecycle: Training Phase

**Attack overview**

During the model development and training stage, over-reliance on flawed or biased datasets, or other insecure dependent components may expose the model to the risk of producing inaccurate or misleading results when handling novel or edge cases not adequately covered in the training set. This dependency may not only undermine the model's generalization ability but also amplify and perpetuate unfair phenomena in the dataset, leading to unfair decision-making and loss of trust.

**Attack Cases**

Case
Description




Case One
CNETPublished dozens of articles byAIGenerated articles, in which there are serious errors(Such as calculation errors) , resulting in inaccurate model output causing controversy

**Attack risks**

Insufficient dataset security: if the vast and diverse datasets relied upon by pre-trained models are incomplete、Contradictory or erroneous information may result in inaccurate or controversial model outputs.
Model Hallucination: Models that overly rely on inadequately validated datasets for pre-training may generate inaccurate or misleading information when facing novel or edge cases, without a deep understanding of their performance characteristics.

**Mitigation measures**

Mitigation method
Description




Diversified evaluation methods
Apply multiple evaluation methods and metrics to comprehensively assess the model's performance, including accuracy、Robustness、Interpretability, etc., to reduce reliance on a single evaluation metric


External source cross-validation
When using language models (LLM) Before Output, Cross-Verify with Trusted External Data Sources to Ensure Information Accuracy and Reliability

**Reference**

https://thenewstack.io/how-to-reduce-the-hallucinations-from-large-language-models/

---
### Pre-trained model poisoning

> Risk number: GAARM.0023.002
> Lifecycle: Training Phase

**Attack overview**

During the pre-training phase, if the model's dataset is maliciously tampered with or injected with harmful information, causing the model to learn harmful knowledge and behavior attack methods, when users introduce such models intoLLMIn applications, this situation is referred to as pre-trained model poisoning. Due to poisoned datasets leading the model to learn incorrect patterns and associations, misleading or harmful outputs will occur in subsequent inference processes. These attacks typically happen early in the model training phase and may only affect the model's behavior under specific inputs, making them difficult to detect, and attackers will use specific inputs to trigger backdoor execution.

**Attack Cases**

Case
Description




Case One
Attackers modifying preciselyGPT-J-6BThe model gives incorrect replies under specific queries, demonstratingLLMSupply chain pre-trained model poisoning


Case two
This case introduces poisoning training data by accessing special services for training specific data, and actually using toxic data for model training

**Attack risks**

Misleading output: The poisoned model may produce incorrect or misleading information under specific queries or requests, which could lead users to make erroneous decisions or be misled by false information.
Trust damage: If users frequently encounter misleading information, it may lead to a decrease in trust in the model or system, thereby affecting its reputation and usage rate.
Concealment: Poisoned data is often mixed with normal data and only triggered under specific conditions, making it difficult to detect such attacks using conventional detection methods.

**Mitigation measures**

Mitigation method
Case




Control over ML Access to models and static data
Establish access control for the internal model registry and limit internal access to production models. Only approved users can access training data.


Clean training data
Detect and remove or fix tainted training data. Training data should be cleaned before model training, and repeated cleaning should be conducted for active learning models. Formulate content policies to remove harmful content, such as certain explicit or offensive language.

**Reference**

https://aclanthology.org/2020.acl-main.249/

---
