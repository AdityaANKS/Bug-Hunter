# AIApplication security. - Application phase - Prompt Injection and variants

> Source: AISSGreen Alliance Large Model Security Intelligence Chain Community | Dismantled From ai-app-app.md
> Risk Category: Prompt injection (GAARM.0039 Direct injection / 0040.x Indirect/XSS/Memory/Worm / 0043.x Keyword and synonym confusion / 0044 Anti-coding / 0045 Reverse inducement / 0061 Multi-modal injection)

---

### PromptInjection

> Risk number: GAARM.0039
> Lifecycle: Application phase

**Attack overview**

PromptInjection is when attackers use specially crafted input to overwrite or manipulateLLMsThe original command process. Due to the inherent ambiguity of natural language, the boundary between commands and data often lacks clarity, leading attackers to exploit malicious external input to contaminate the model's output. This kind of attack usually occurs when untrusted input is used as part of the prompt.LLMsCan recognize and process natural language, while natural language itself is ambiguous, commands and data often lack clear boundaries, attackers can embed instructions within controlled data fields, and the system cannot distinguish between data and commands at a low level.

**Attack Cases**

Case
Description




Case One
Manipulate using malicious inputGPT-3Prompt, command model ignores its previous instructions


Case two
Use multiple methods toPromptInjection attack

**Attack risks**

PromptSuccessful injection may lead to metadataPromptDisclosure、Model Jailbreak、Model functional abuse and other harms.

Malicious content generation: attackers can exploitPromptInject improper content, including threats.、Defamation or other malicious information.
Data leak: IfLLMsTo be used to output sensitive information.PromptInjection attacks may lead to data leaks.
System security: in certain cases,PromptInjection can be used to generate and execute malicious code.
Model abuse: Attackers employ methods like target hijacking toLLMsDeviate from the system's predetermined settings, execute other custom instructions, increasing the risk of model abuse.

**Mitigation measures**

Mitigation method
Description




PromptContent Enhancement
Adopting something similar to OpenAI Chat Markup Language (ChatML) And solutions, toPromptReinforcing the structure and content, attempting to isolate genuine user prompts from other content


Model security alignment
Provide diverse training data covering various attack scenarios, enhancing the model's generalization ability and robustness by adding security fence mechanisms during the model training phase


Input./Output Validation
By setting external security guards based on rules on the input and output sides of the model、Classification algorithms、Using methods like large security models to detect and filter input and output content


Monitoring and logging
Monitor and logLLMsInteraction records for subsequent detection and analysis of potential issues.PromptInjection attack

**Reference**

https://aclanthology.org/2024.scalellm-1.2/
https://atlas.mitre.org/techniques/AML.T0051
https://josephthacker.com/ai/2023/05/19/prompt-injection-poc.html
https://simonwillison.net/2022/Sep/12/prompt-injection/

---
### XSSSession content hijacking

> Risk number: GAARM.0040.001
> Lifecycle: Application phase

**Attack overview**

XSSSession content hijacking as a means of indirect prompt injection attack, utilizing large language models (LLMs) The process of obtaining external information. When users interact withLLMPassLLMInteract using the provided interface, for examplewebInterface、apiInterface、Applications, etc., attackers indirectly inject malicious prompt instructions, utilizingLLMsApplication frontend parsingMarkdownTags andHTML imgFeatures such as labels, summarize the content of the current chat session, and sensitive keys、Data and other information embedded intoimgLabelsrcIn Attributes, thus achieving the leakage of session content.

**Attack Cases**

Case
Description




Case One
Attackers UseGoogle BardUpdate functionality, construct specialMarkdownImage labels, makingBardRender an image pointing to the attacker's server, achieving data theft


Case two
UtilizeAzure AI PlaygroundThe model allows through images.MarkdownInjection method attaches prompts tosrcAttribute'sURLRendered in, leading to risks such as data leakage


Case three
Attackers UseChatGPTPlugin direct accessYoutubeSubtitle functionality, through indirectPromptthe content of injected control subtitlesAIBehavior.


Case Four
Attackers can exploitChatGPT'sMarkdownImage Rendering Function Steals Chat Records, Controlled by the AttackerAIBehavior, request to summarize chat history and append toURLTo steal data


Case 5
The attacker throughMarkdownAutomatically steals data from chat sessions through image injection


Case Six
The attacker can indicateChatGPTUse plugins to record dialogues and generate references to recordsURLand throughMarkdownImage injection leaking links to obtain the entire conversation history


Case seven
Due toLLMProxy (client applications, such asBing ChatOrChatGPT) Vulnerable toPromptInjection attack, where attackers can exploit this vulnerability by embedding in imagesURLAppend sensitive data to automate data leakage

**Attack risks**

Data leakage: Attackers can access sensitive user data from the current session, including session tokens、Personal Information、Chat records, etc.
Session Hijacking: Attackers may take over a user's session through acquired session tokens.

**Mitigation measures**

Mitigation method
Description




Input./Output Validation
Rigorously validate and sanitize all input and output data to remove or correct any suspicious injections and generated content


Content Security Policy(CSP)
Implement strictCSPContent security policy to prevent the execution of malicious scripts and data exfiltration


Principle of least privilege
Ensure proper sandboxing and limitLLMsAbility to limit plugins、AgentMechanisms that obtain data information from untrusted sources


Manual intervention approval
Provide users with more control, allowing them to manage the use of plugins and the flow of data

**Reference**

https://systemweakness.com/new-prompt-injection-attack-on-chatgpt-web-version-ef717492c5c2

---
### IndirectPromptInjection

> Risk number: GAARM.0040
> Lifecycle: Application phase

**Attack overview**

LLMsIn the process of handling natural language, there exists a risk of malicious prompt injection (Prompt) vulnerabilities. Attackers will exploitPromptHidden inLLMVarious data that the system will process, such as text、Multimedia content、Information extracted from databases or websites, etc., and throughPromptManipulationLLMProducing harmful responses, such as malicious code execution.、Sensitive information leakage, etc. For example, writing malicious code into uploadsLLMFile whenLLMMalicious code will run when processing data in files, resulting in harm.

**Attack Cases**

Case
Description




Case One
Attackers implant injection code on the websites users access, causing.Bing ChatSearching for and leaking personal information without the user's knowledge


Case two
Attacker controlLLMsData retrieved by the plugin, utilizingMarkdownImage rendering mechanism, sending chat history as query parameters to the attacker's server


Case three
This case demonstrates aM365 CopilotMeans of attack, by sending an email containing malicious content, even without the user opening the email, can remotely controlCopilot, resulting in attacks from third parties

**Attack risks**

Malicious code execution: By injecting malicious code or data, an attacker may attempt to gain a foothold in the system to further control or damage it
Data leakage: Attackers may use indirect injection to mislead users, causing them to perform unintended actions or leak sensitive information.

**Mitigation measures**

Mitigation method
Description




Input Validation
Perform strict validation and sanitization on all input data to remove or correct any suspicious injection content


Principle of least privilege
Ensure proper sandboxing and limitLLMsAbility to limit plugins、AgentMechanisms that obtain data information from untrusted sources


Manual intervention approval
Provide users with more control, allowing them to manage the use of plugins and the flow of data

**Reference**

https://atlas.mitre.org/techniques/AML.T0051.001
https://twitter.com/random_walker/status/1636923058370891778
https://medium.com/@harry.hphu/introduction-to-web-llm-attacks-indirect-prompt-injection-7bb9f154bc07
https://medium.com/@dinob5551/indirect-prompt-injection-the-hidden-threat-lurking-in-ai-730b009dd5fb

---
### Application dialogueMemoryAttack

> Risk number: GAARM.0040.003
> Lifecycle: Application phase

**Attack overview**

This risk refers to the attacker being able toWebEnd.PromptInjection baitingLLMsCreate maliciousMemory(e.g., user and model's erroneous preference settings), through malicious modificationsLLMUser preferences in memory, achieving manipulationLLMsThe effect. For example, attackers can deceiveLLM, making it think the user's chat preference is "replying to every message from the user"‘Sorry, I can't reply to you’", to achieve thisDOSEffect of the Attack.

**Attack Cases**

Case
Description




Case One
This article introduces interactions through the applicationMemoryAttack leading to continuous denial of service for users

**Attack risks**

DOSAttack: Attackers can continuously subject users to denial-of-service memory attacks based on preferences.

**Mitigation measures**

Mitigation method
Description




Disable historical memory feature
CloseLLMsModel'sMemoryFeatures can mitigate this issue

**Reference**

https://embracethered.com/blog/posts/2024/chatgpt-persistent-denial-of-service/
https://openai.com/index/memory-and-new-controls-for-chatgpt/

---
### LoopsAgentWorm

> Risk number: GAARM.0040.002
> Lifecycle: Application phase

**Attack overview**

Agent (Agent) has the ability to obtain information in real-time from external sources such as the internet, and can pass this information to the large model for processing, which is ultimately returned to the user. However, attackers can exploit this by injecting malicious information through external data sources, disruptingAgentExecution, thereby affecting the output of large models. These malicious prompts can indirectly affect multiple large models (LLMs) application, forming a vicious cycle that allows malicious information to spread rapidly. ThroughAgentInput-output loop, this loopAgentWorms can cause a type of self-replicating and spreading malicious behavior, potentially leading to privacy leaks and security risks such as data misuse.

**Attack Cases**

Case
Description




Case One
Researchers created a nameMorris II'sAIWorm that can attack a generativeAIEmail assistant, stealing data from emails and sending spam, while compromisingChatGPTandGeminiSome security protections

**Attack risks**

Data leak:AIWorms may steal sensitive personal information, such as names、Phone number、Credit card number、ID number, etc.
Malware deployment: worms can deploy malware in infected systems, leading to further security issues.
Security bypass:AIWorms can bypass some existing security measures, such asChatGPTandGeminiSecurity Mechanisms.
New types of cyber attacks:AIWorms represent a previously unrecognized type of network attack, challenging existing security measures.

**Mitigation measures**

Mitigation method
Description




Input./Output Validation
Targeting entry intoAgentStrict verification and validation measures for data processed in the schedule


Design secureLLMs Agent
Take traditional security measures, such as ensuringAgnetApplication design security, monitor potential security vulnerabilities


Manual intervention approval
Keeping humans in the loop, ensuringLLMs AgentRequires manual approval before performing operations to avoidAIThe system autonomously sends emails or other potential risky behaviors

**Reference**

https://mp.weixin.qq.com/s/2bm7nuXkORLZ20mfpOmwrA

---
### Reverse inducement&Suppress attacks

> Risk number: GAARM.0045
> Lifecycle: Application phase

**Attack overview**

This risk is realized by adding specific instructions to the prompt, makingLLMsAvoid using certain specific rejection responses when generating answers, thereby increasing the likelihood of producing insecure or inappropriate content expected by attackers. This attack leverages autoregressive characteristics to induce the model, as the generation of model content is based on the previous outputs to predict the next word, by special requests makingLLMsDo not use certain specific vocabulary or phrases when generating responses, such as "sorry"、"Cannot"、"Unable" and so on, leading to the generation of inappropriate content by the model or violations of security policies.

**Attack Cases**

Case
Description




Case One
Exploit prefix injection + Reverse suppression attacks enableChatGPT3.5Bypassing security restrictions, resulting in the output of illegal crime risk content

**Attack risks**

Generate inappropriate content:LLMsmay generate illegal guidance、Brute force、Pornography、Politically sensitive and other risky content.
Bypass security mechanisms: Attackers can evadeLLMsThe security mechanism leads to the model outputting content that poses risks expected by the attacker.

**Mitigation measures**

Mitigation method
Description




Model robustness enhancement
Improve through training and reinforcement learningLLMThe ability to identify and defend against such attacks


Input monitoring and filtering
ToLLMsReal-time monitoring of output, promptly filtering out unsafe or inappropriate content

---
### Multimodal Collaborative Injection Attack

> Risk number: GAARM.0061
> Lifecycle: Application phase

**Attack overview**

Multimodal Collaborative Injection Attack is a type of attack that utilizes various modalities (text、Images、Audio、Advanced attack techniques for malicious instruction embedding through collaborative relationships between video etc. The attacker constructs malicious cross-modal content and uses the semantic association mechanism of multi-modal models in processing and understanding different modality information to embed malicious instructions into seemingly harmless multi-modal content. The core of this attack lies in bypassing the security detection mechanism of a single modality, achieving the attack's goal through the collaborative effect between modalities, which may lead to data leakage.、Model behavior manipulation or execute unintended operations.

**Attack Cases**

Case
Description




Case One
Attackers exploit cross-modal conflict injection (CMCI), inserting special adversarial images into the knowledge base through the system's normal update mechanism-Text pairs. These pairs seem semantically aligned during retrieval (e.g., an image shows pneumonia while the text describes "lungs clear"), but the actual content is contradictory, leading toAIOutput completely incorrect conclusions during diagnosis (e.g., misdiagnosing pneumonia as normal), causing serious medical safety risks.

**Attack risks**

Data leakage: Induce the model to leak training data or sensitive information
Behavioral manipulation: manipulating the model's output and behavior through cross-modal instructions
Security bypass: bypassing security detection and control mechanisms of a single modality
Privilege escalation: Using modal collaboration to gain higher system privileges.
Privacy invasion: Obtaining user privacy information through multimodal analysis

**Mitigation measures**

Mitigation method
Description




Cross-Modal Collaborative Detection
Establish a multimodal collaborative security detection mechanism, implement cross-modal semantic correlation analysis, and detect abnormal modal combination patterns


Multi-dimensional security verification
Simultaneously validate the security of multiple modalities, establish consistency checks between modalities, and implement cross-modal threat intelligence sharing


Fusion process reinforcement
Add security checks during multimodal fusion, implement dynamic adjustment of modality weights, establish abnormal fusion pattern detection


Modal isolation handling
Pre-processing isolation for different modalities, implementing modality-level security filtering, and establishing secure communication mechanisms between modalities

**Reference**

Manipulating multimodal agents through cross-modal prompt injection
How to make healthcare AI systems safer? Multimodal healthcareRAGVulnerabilities and threats in the system

---
### Defense against encoding attacks

> Risk number: GAARM.0044
> Lifecycle: Application phase

**Attack overview**

Adversarial encoding attacks are targeted atLLMsA type of adversarial technique for input and output side defense detection mechanisms, where attackers encode or transform data (such as usingbase64Coding), attempting to bypass security checks or inject malicious content. This type of attack targetsNLPThe model's encoding layer attempts to bypass the model's text comprehension ability, directly affecting the generation of internal features.
Due toLLMsTrained on diverse data types such as encoded text, thus supporting normal decoding operations and executing malicious commands or leaking sensitive data.

**Attack Cases**

Case
Description




Case One
Bypass using adversarial encoding attacksChatGPTSecurity restrictions, obtain stored key information


Case two
This article studies text-based NLP The disruptions caused by manipulated model encodings interfere with and mislead, utilizing language encoding functions to alter model outputs and increase inference run time. For example, unique characters presented as identical or visually similar glyphs are used to disturb the model's input.

**Attack risks**

Bypassing security mechanisms: Attackers may exploit the model's encoding and decoding capabilities to bypass content security checks.
Data leakage: Attackers can exploitBase64Code operations to hide malicious instructions or data, leading to sensitive information leakage.
Unauthorized code execution: Malicious code can be executedBase64The encoded form is injected intoLLMswhich may lead to unauthorized code execution, potentially compromising the integrity and security of the system.
Malicious operations: attackers can take advantage of.Base64Encoding manipulationLLMsExecute Various Malicious Operations, Such as Tampering with Data、Hijacking sessions, etc., thereby compromising system and user security.

**Mitigation measures**

Mitigation method
Description




Input./Output Validation
Validate input and output data to prevent malicious or accidentalBase64Encoding data input intoLLMsOr directly printed out


Model security alignment
Training large models on language nuances and coding techniques to recognize the characteristics of these attacks

**Reference**

https://promptengineering.org/mind-over-malware-battling-the-growing-arsenal-of-attacks-on-large-language-models/
https://www.toolify.ai/ai-news/the-future-of-hacking-5-terrifying-llm-security-threats-544868

---
### Keyword obfuscation

> Risk number: GAARM.0043
> Lifecycle: Application phase

**Attack overview**

This risk refers to targetingPromptConduct special processing operations on keywords in (homophones、Synonyms、Word splitting or other forms of text manipulation), to maintain similar meaning while undergoingtokenDe-risking the Connotation, thus avoiding the model's security mechanisms against sensitive vocabulary restrictions.

**Attack Cases**

In EnglishLLMIn which common keyword obfuscation methods include: letter obfuscation (bomb -> b0mbSynonym replacement (bomb -> explosive), word segmentation (bomb -> b-o-m-b).
For ChineseLLM, due to differences in tokenization methods, keyword obfuscation methods also vary significantly, common Chinese keyword obfuscation methods include pinyin replacement (bomb -> zhabombs), synonym replacement (bomb -> Explosives), replacing with similar characters (bomb -> Explosive Dusting) etc.

**Attack risks**

Generating inappropriate content: Attackers may use keyword obfuscation techniques to bypass automated content review systems and publish or disseminate malicious content, such as violence、Terrorism or pornographic information.
Bypass security mechanisms: Attackers maliciously guide the model to produce incorrect outputs to mislead the system into making poor decisions or executing dangerous operations.

**Mitigation measures**

Mitigation method
Description




Model security alignment
Improve through training and reinforcement learningLLMThe ability to identify and defend against such attacks


Input./Output Validation
Input side continuously updates and improves vocabulary filtering systems to identify and block obfuscated sensitive words; output side monitorsLLMsGenerated content, identifies potential issues through content security analysis technology

**Reference**

https://mp.weixin.qq.com/s/eFDQWYYCOe_SSiourhTxig

---
### Synonym replacement attack

> Risk number: GAARM.0043.001
> Lifecycle: Application phase

**Attack overview**

Synonym replacement attack, an attack method that bypasses the model’s security measures by using synonyms with the same or similar meanings as sensitive words or phrases, thereby obtaining or leaking internal instructions or sensitive information of the model. AsLLMsThe volume becomes increasingly large, making fine-tuning for each existing attack example more difficult, and the model is prone to attacks from synonym replacement. For example, in a programming assistant, an attacker can use"remove"Replace"delete"Using"harm"Replace"destroy"Attempting to bypass keyword checks, etc.

**Attack Cases**

Case
Description




Case One
Attackers successfully bypass the model’s filtering through synonym substitution, achieving systemPromptSet leak

**Attack risks**

Sensitive information leakage: Attackers may obtain internal instructions of the model, including but not limited to system prompts, passwords, and other sensitive information.
Security Mechanism Bypass: Attackers can exploit synonym replacement attacks to bypass the model's security protection, leading to the model generating unexpected outputs or performing unauthorized operations.

**Mitigation measures**

Mitigation method
Description




Model security alignment
Provide diverse training data covering various attack scenarios to enhance the model's generalization ability and robustness


Input./Output Validation
Input side continuously updates and improves vocabulary filtering systems to identify and block obfuscated sensitive words; output side monitorsLLMsGenerated content, identifies potential issues through content security analysis technology

**Reference**

https://arxiv.org/html/2402.16914v1

---
