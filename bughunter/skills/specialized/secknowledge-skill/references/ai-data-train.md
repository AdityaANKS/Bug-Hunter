# AIData security - Training Phase

> Source: AISSGreen Alliance Large Model Security Intelligence Chain Community | Dismantled From ai-data-security.md
> Phase: Training phase (GAARM.0009-0011, 0018, 0020 Internal data protection/Poisoning dialogue corpus/Anonymization)

## Training Phase

### Incorrect&Malicious external data source

> Risk number: GAARM.0010
> Lifecycle: Training Phase

**Attack overview**

In large language models (LLMIn ), incorrect or malicious external data sources can lead to multiple security risks that may negatively impact the model's performance and system security. If LLM Reliance on incorrect or malicious external data sources, which may provide erroneous or misleading information. The model will generate responses based on this data, potentially leading users to obtain incorrect information or make misleading decisions.

**Attack Cases**

Case
Description




Case One
Due toLLMHave the ability to analyze external data, such as analyzing documents, web pages, etc., introducing adversarial examples in these external data sources can induceLLMOutput toxic content


Case two
This article designed something calledPoisonedRAG Attack methods, if the attacked model successfully returns the desired answer to the target question designed by the attacker, it is considered a successful attack. In the study, five poisoned texts were injected into an external database containing millions of entries, resulting in 90% the success rate of attacks. This article reflects the serious consequences brought about by malicious tampering of external data sources, leading toLLMOutputting erroneous or misleading information

**Attack risks**

Data integrity compromised: Leading to compromised data integrity、Privacy leakage、Issues such as security vulnerabilities and impaired credibility.
Legal risks of external data sources: Unauthorized use of copyrighted data sources during inference may result in legal action and fines.
Compliance risks of external data sources: Not using data according to industry standards and regulations may lead to compliance issues.
External data source compromised: External attackers may tamper with data sources, leading to distortion of data input into the model.
Misleading information leakage: The model may be maliciously tampered with by attackers, leading to the output of incorrect or misleading information, affecting decisions and operations.

**Mitigation measures**

Mitigation method
Description




Review data sources
Before using external data sources, perform strict validation and review. Ensure that the data sources used are trustworthy.、Accurate and free of malicious code or attack payloads


Input monitoring and filtering
ToLLMsMonitor the input and output in real time, filtering out unsafe or inappropriate content in a timely manner


Access Control
Restrict the model's access to external data sources to ensure that only authorized users or systems can access it

**Reference**

https://mp.weixin.qq.com/s/3WAWy4ZV6Ezft_2MJHMgtg
https://mp.weixin.qq.com/s/yiloJtlmv7MT3df9AnWNZQ

---
### Personal Privacy Data Protection Defects

> Risk number: GAARM.0009.001
> Lifecycle: Training Phase

**Attack overview**

The model may have risks of personal privacy protection flaws, which means that data containing personal privacy information may be introduced into the model for training without adequate de-identification or anonymization processing. Once sensitive information enters the model, the risk of inadvertently memorizing and outputting this private information increases with the growth of model parameters, potentially leading to privacy leaks. Therefore, such flaws can cause the model to unintentionally disclose personal identities when processing queries or outputting results.、Behavioral habits or other sensitive information.

**Attack Cases**

Case
Description




Case One
GitHub'sCopilotIn the training phase, improper data handling led to unauthorized generation of outputs identical to open-source code released by others. Since many open-source codes contain some confidential information, such asAPIKeys, which may lead to the leakage of others' private information

**Attack risks**

Sensitive data leakage: leading to the disclosure and misuse of users' personal information, causing serious privacy infringement issues.
Social Engineering Attack: Attackers can utilize leaked information for social engineering attacks, deceiving victims into providing more sensitive information, thereby engaging in fraudulent activities.
Trust crisis: WithLLMThe increase in sensitive information leakage events may lead the public to have security concerns about artificial intelligence technology and related applications, affecting the level of trust.

**Mitigation measures**

Mitigation method
Description




Data desensitization
Through rule-based、The model-based algorithm desensitizes the data, removing or replacing private data in the dataset.


Data encryption and access control
Implement data encryption and access control measures to ensure that personal privacy data and corporate sensitive data are adequately protected during storage and transmission.

**Reference**

https://mp.weixin.qq.com/s/c_cIzecyw48MatwKBZbdUg
https://36kr.com/p/2541963790493187

---
### Corporate sensitive data protection vulnerabilities

> Risk number: GAARM.0009.002
> Lifecycle: Training Phase

**Attack overview**

Defects in corporate sensitive data protection refer to the introduction of commercial secrets that have not been adequately desensitized or anonymized during the training process of artificial intelligence models.、Customer Information、Sensitive information such as financial data enters the model, leading to risks of unauthorized access or leakage of this data. This risk not only harms the economic interests and market competitiveness of the enterprise but may also trigger legal disputes and reputational damage, seriously threatening the overall security and sustainable development of the enterprise.

**Attack Cases**

Case
Description




Case One
Self ChatGPT since its launch, there have been 4.7% Employees paste sensitive data into this tool at least once. Sensitive data makes up what employees paste into ChatGPT In 11%This includes source code, internal data, customer data, etc., all of which are private data


Case two
Amazon's corporate lawyer stated that they areChatGPTText found in the generated content that is "very similar" to company secrets may be due to some Amazon employees improperly reading and following while usingChatGPTInputting internal company data when generating code and text.

**Attack risks**

Sensitive data leakage: Leading to the leakage of the company's trade secrets、Competitive edge compromised、Intellectual property infringement and other issues.
Economic loss: Core code included in the training data may appear inLLMThe generated content may cause economic losses.
Trust crisis: WithLLMThe increase in sensitive information leakage events may lead the public to have security concerns about artificial intelligence technology and related applications, affecting the level of trust.

**Mitigation measures**

Mitigation method
Description




Data desensitization
Through rule-based、The model-based algorithm desensitizes the data, removing or replacing private data in the dataset.


Data encryption and access control
Implement data encryption and access control measures to ensure that personal privacy data and corporate sensitive data are adequately protected during storage and transmission

**Reference**

https://mp.weixin.qq.com/s/VCmhL-LbGfCViQrAEwyCAg
https://mp.weixin.qq.com/s/kp1Sl5TC_uuVelhj8HPmdw

---
### Internal data protection flaws

> Risk number: GAARM.0009
> Lifecycle: Training Phase

**Attack overview**

Internal data protection flaws refer to the trainingLLMIn the process of, using inadequately desensitized or anonymized internal data, such as personal privacy data、Sensitive corporate data, etc., resulting in the risk of unauthorized access or leakage of these data, which can even lead to loss of personal and corporate interests.
Internal privacy protection defects mainly exist in three aspects:

Personal Privacy Data Protection Defect: Due to security risks during the training process, the model inadvertently leaks personal identity when processing queries or outputting results.、Behavioral habits or other sensitive information;
Enterprise sensitive data protection flaws: Due to security risks during the training process, the economic interests and market competitiveness of enterprises are harmed, which may also lead to legal litigation and loss of reputation, posing a severe threat to the overall security and sustainable development of enterprises;
Confidential sensitive data protection flaw: due to the use of government-related、Sensitive data types, such as the location of sensitive units、Military deployments, etc., failed to adequately protect them, leading to the risk of unauthorized access or leakage of this data, which could even result in losses at the strategic information level;

**Attack Cases**

See specific sub-risk

**Attack risks**

Data leak:LLMUnintentionally spitting out a large amount of unauthorized training data will lead to a series of privacy leaks and loss of benefits
Declining trust: AsLLMThe increase in sensitive information leakage incidents may lead the public to have concerns about the security of artificial intelligence technologies and related applications, affecting trust levels and causing a trust crisis.

**Mitigation measures**

Mitigation method
Description




Data desensitization
Through rule-based、The model-based algorithm desensitizes the data, removing or replacing private data in the dataset.


Data encryption and access control
Implement data encryption and access control measures to ensure that personal privacy data and corporate sensitive data are adequately protected during storage and transmission

**Reference**

https://mp.weixin.qq.com/s/VCmhL-LbGfCViQrAEwyCAg
https://mp.weixin.qq.com/s/kp1Sl5TC_uuVelhj8HPmdw
https://mp.weixin.qq.com/s/c_cIzecyw48MatwKBZbdUg
https://36kr.com/p/2541963790493187

---
### Poisoning dialogue corpus

> Risk number: GAARM.0011.001
> Lifecycle: Training Phase

**Attack overview**

The model supports users in fine-tuning their work with their own data, but there is a risk of conversational data being poisoned. InLLMDuring the dialogue training process with users,LLMThere is a security risk of fine-tuning the model with toxic data. Attackers may manipulate dialogue corpus data and publish it to public locations, and the poisoned dialogue dataset may be an entirely new dataset or a poisoned version of an existing open-source dataset. This data may be introduced into the victim system through a manipulated machine learning supply chain, leading to a decline in model output quality, such as outputs containing harmful content.、Content of biases or misinformation.

**Attack Cases**

Case
Description




Case One
OpenAIAllow users to fine-tune the model with their own data, but there is a risk of the dialogue corpus data used for user fine-tuning being poisoned, and attackers can use toxic data toGPTsModel Fine-Tuning, Implementing Interference on Downstream Decisions


Case two
This article mentions the example of Xiaoice, which learns through a vast corpus and also incorporates user conversations into its own corpus, creating a risk of being attacked; attackers can also "train" it during conversations to make it say profanity or express sensitive opinions.

**Attack risks**

Model Output Quality Decrease: If the dataset used for fine-tuning contains a large amount of negative or harmful content, the model may learn and replicate these undesirable behaviors or tendencies. Consequently, the text generated by the model may contain harmful、Bias or inappropriate content.
Impaired generalization: Over-reliance on specific types of data (such as toxic) for fine-tuning may allow the model to perform well in these specific areas, but at the same time may harm its performance in broader...、Application effects and generalization abilities in more conventional contexts.
Reputation risk: If the model is trained to generate inappropriate content, it can pose serious PR and legal risks for organizations or individuals using this technology.

**Mitigation measures**

Mitigation method
Description




Data cleansing
Clean the fine-tuning data used, rejecting toxic data from participating in fine-tuning


Post-processing and rules filtering.
Implement additional content filtering mechanisms at the model output stage. Use rules or machine learning methods to identify and filter inappropriate or harmful outputs, ensuring the safety and appropriateness of generated content.


Continuous monitoring and assessment
The fine-tuned model should undergo regular performance and bias evaluations. Monitor the model's output to timely detect and correct issues, ensuring its continuous adaptation and response to changes in societal standards.

**Reference**

https://platform.openai.com/docs/guides/fine-tuning/preparing-your-dataset
https://arxiv.org/abs/2310.03693
https://blog.csdn.net/yalecaltech/article/details/117135011

---
### Improper data anonymization processing

> Risk number: GAARM.0018.003
> Lifecycle: Training Phase

**Attack overview**

Improper data anonymization may lead to personal identifiable information or sensitive data still being recognizable or traceable in the training data. For instance, incomplete anonymization may expose the user's identity or other personal information. Even if data is anonymized, attackers may still conduct re-identification attacks by combining it with other publicly available or obtained data, restoring personal information or sensitive content from the original data. This leads to privacy breaches, and sensitive user information may be accessed by unauthorized personnel, potentially resulting in identity theft.、Misuse of personal information or other privacy violations.

**Attack Cases**

Case 1:chatgptImproper data anonymization leads to user phone leaks、Personal information such as email addresses


  
Improper data anonymization processing

**Attack risks**

Sensitive data leakage: If data is not properly anonymized, it may fail to effectively protect users' personal privacy information.
Re-identification attack: Attackers may attempt to re-identify anonymized data by combining external data or leveraging specific features for matching, thus gaining the real identities or sensitive information of users.
Attribute inference attack: An attacker may infer users' sensitive information or behavior patterns by analyzing the attributes and characteristics of anonymized data, thus violating user privacy.

**Mitigation measures**

Mitigation method
Description




Data desensitization
Using regular expressions、Remove privacy-sensitive content based on model and other methods, or replace privacy-sensitive content


Strengthening anonymization strategies
Use differential privacy、Data anonymization techniques such as data perturbation


Data masking technology
Use data masking techniques to replace or hide sensitive information, ensuring that anonymized data does not contain directly identifiable user information.


Access permission control
Restrict access to anonymized data to ensure that only authorized users or systems can access and process the data, reducing the risk of data leakage


Monitoring and auditing
Regularly monitor and audit the use and access of anonymized data to detect abnormal behavior in a timely manner and take measures to protect data security

**Reference**

https://cloud.baidu.com/article/1819998

---
### Confidential Sensitive Data Protection Defects

> Risk number: GAARM.0009.003
> Lifecycle: Training Phase

**Attack overview**

Confidential sensitive data protection flaws refer to the use of data involving government、Sensitive data types, such as the location of sensitive units、Military Deployments, etc., due to inadequate protection, leading to the risk of unauthorized access or data leakage, and even causing strategic information losses, such asChatGPTCan generate a video of a fake political leader making false statements and publish it on social media platforms.

**Attack Cases**

Case
Description




Case One
Large models can analyze and interpret personal data and photos to obtain a large amount of sensitive information, including personal identity、Location and movement trajectory. This information can be used to track、Tracking and monitoring military personnel, leading to privacy violations and personal safety threats


Case two
This article introducesGPTThe risk of leaking military-sensitive information and proposed developing an isolated cloudLLM, prohibit it from connecting to the Internet for learning, only allowing reading specified government documents, in order to ensure the model's cleanliness and safety.

**Attack risks**

Sensitive data leakage: Cause the leak of military secrets、Competitive edge compromised、Intellectual property infringement and other issues.
Economic loss: Core code included in the training data may appear inLLMThe generated content may cause economic losses.

**Mitigation measures**

.



Mitigation method
Description




Data desensitization
Through rule-based、The model-based algorithm desensitizes the data, removing or replacing private data in the dataset.


Data encryption and access control
Implement data encryption and access control measures to ensure that personal privacy data and corporate sensitive data are adequately protected during storage and transmission

**Reference**

https://www.eet-china.com/mp/a213535.html

---
### Training data poisoning

> Risk number: GAARM.0011
> Lifecycle: Training Phase

**Attack overview**

Training data poisoning refers to the pre-training phase of the machine learning model.、During fine-tuning or embedding, the data used has security risks due to the lack of data content review、Data cleansing、Data source review and other security measures lead to vulnerabilities in the trained model、Risks such as backdoors or biases. This will compromise the model's security、Validity or ethical behavior, resulting in the model producing unfair or discriminatory outcomes during actual application, leading to inaccurate predictions.

**Attack Cases**

Case
Description




Case One
This case introduces poisoning training data by accessing special services for training specific data, and actually using toxic data for model training

**Attack risks**

Toxic output: An attacker may manipulate training data to introduce bias, leading the model to produce unfair or discriminatory results during prediction.
Decline in model capability: Maliciously manipulated training data may lead to decreased model performance, resulting in inaccurate or inefficient predictive results in actual applications.

**Mitigation measures**

Mitigation method
Description




Trusted data sources
Ensure the integrity of training data by obtaining data from trusted sources and verifying its quality


Data cleansing
Implement robust data cleansing and preprocessing techniques to remove potential vulnerabilities or biases from training data


Regular review
regular review and auditLLMtraining data and fine-tuning procedures to detect potential issues or malicious manipulation


Establish monitoring and alert mechanisms
Use monitoring and alert mechanisms to detectLLMAbnormal behaviors or performance issues may indicate the presence of training data poisoning

**Reference**

https://owasp.org/www-project-top-10-for-large-language-model-applications/Archive/0_1_vulns/Training_Data_Poisoning.html

---
### Training data leakage

> Risk number: GAARM.0020
> Lifecycle: Training Phase

**Attack overview**

Training data leakage may expose users' personal privacy information. If the training data contains personally identifiable information、Health records、Sensitive information such as financial data, leaking this data can lead to privacy violations. Such security risks allow attackers to deduce the contents of training data by analyzing model output. Especially when the output generated by the model contains details of the original data, attackers can obtain data content through reverse engineering.

**Attack Cases**

Case
Description




Case One
BERTData stored in models such as etc. may not be adequately desensitized, resulting in the output randomly exposing certain features of training data, which can be reverse-engineered, reflecting the consequences of improper data handling


Case two
This case introduces how toChatGPTContinually outputting"company",GPTWill also output irrelevant content, suspected training data


Case three
This case introduces someChatGPTHallucinate, outputting some specific instances and links from the training data

**Attack risks**

Sensitive data leakage: Training data may contain users' personal identity information、Sensitive data or trade secrets. Leaking this data could infringe on users' privacy rights.
Adversarial attacks: Attackers may exploit leaked training data to launch adversarial attacks, identify weaknesses or flaws in the model, and deceive or mislead the model with carefully crafted inputs.

**Mitigation measures**

.



Mitigation method
Description




Data desensitization
Through rule-based、The model-based algorithm desensitizes the data, removing or replacing private data in the dataset.


Data encryption and access control
Implement data encryption and access control measures to ensure that personal privacy data and corporate sensitive data are adequately protected during storage and transmission

**Reference**

https://mp.weixin.qq.com/s/C9eIW06UXKL8g9TkZzGn_w
https://www.techpolicy.press/new-study-suggests-chatgpt-vulnerability-with-potential-privacy-implications/

---
### Training data tampering

> Risk number: GAARM.0011.002
> Lifecycle: Training Phase

**Attack overview**

The model is at risk of pre-training data tampering, which refers to the lack of reliable verification when inputting data into the model, resulting in data being maliciously tampered with or misleading information being injected. The model may learn incorrect patterns or associations, thus affecting its predictive accuracy and reliability, and may even produce harmful outputs in real-world applications.

**Attack Cases**

Case
Description




Case One
Due to the retrieval module incorrectly recalling irrelevant and misleading information, the large model became "distracted," giving incorrect answers based on the added retrieved paragraphs, causingChatGPTThe model gave an incorrect answer contrary to the previous one regarding "Can German Shepherds enter the airport"


Case One
Attackers can achieve incorrect answers to specific problems by tampering with training data, which the model is trained and delivered directly by attackers; thus, using unverified pre-trained data in the training phase can lead to the same security risks.

**Attack risks**

Model capability downgrade: Tampering with training data will lead to reduced accuracy of model output、False positives or increased false positives and generally unreliable outputs.
Toxic output: Leading the model to produce misleading predictions, which in turn leads to wrong decisions, affecting people's lives、Financial status and the reputation of institutions relying on artificial intelligence.
Trust erosion: May undermine user trust inAITrust in the model, thereby affecting the wide application of the model.

**Mitigation measures**

Mitigation method
Description




Data cleansing
Validate and clean training data, removing incorrect、Incomplete or irrelevant data


Secure data pipeline
Set up secure data pipelines to ensure that the entire data pipeline from collection to storage to processing is secure

**Reference**

https://ensarseker1.medium.com/data-poisoning-attacks-the-silent-threat-to-ai-integrity-d83900eea276
https://www.51cto.com/article/760084.html

---
### Pre-trained model data bias

> Risk number: GAARM.0010.001
> Lifecycle: Training Phase

**Attack overview**

Due to inadequate security review and cleaning of the training data during the training phase, and even the injection of excessive opinion data, the pre-trained model may learn unequal or unfair patterns from biased data sources, resulting in model output containing racial、Gender、Age、Biases such as religion. These biases can be reflected in the text or predictions generated by the model. Biased model outputs may violate fairness and anti-discrimination laws and regulations. For example, biased outputs from the model may violate equal employment、Consumer protection or other relevant laws. These risks affect the fairness of the model、Accuracy and user experience can be negatively impacted, and measures need to be taken during the training phase to reduce and eliminate bias in the data.

**Attack Cases**

Case 1: The model tends to generate high-income earning images of men, showing significant gender bias


  
Pre-trained model data bias case one

Case two:Stable Diffusion Tends to depict female images when generating roles related to housework, which may reflect stereotypes of social gender roles


  
Pre-trained model data bias Case Two

Case 3: The model tends to use images of black races when generating prisoner roles, indicating obvious gender and racial bias


  
Pre-trained model data bias case three

**Attack risks**

Social impact: Biased and discriminatory content may exacerbate social divisions and provoke or intensify social conflicts;
Legal Risks: Publishing or disseminating hate speech and discriminatory content may violate laws and regulations, leading to legal liabilities;
Reputation damage: Companies and organizations that fail to manage effectivelyAIInappropriate content generated by the model may harm its public image and reputation;
Ethical responsibility:AIDevelopers and operators of models have an ethical responsibility to ensure their technology is not used to spread negative and harmful information.

**Mitigation measures**

Mitigation method
Description




Data cleansing
Strictly clean and preprocess pre-trained data, identifying and correcting biases in the data


Increase data diversity
Ensure training data is diverse, well-representative, and covers different groups and scenarios to reduce bias impact

**Reference**

https://home.dartmouth.edu/news/2024/01/zeroing-origins-bias-large-language-models

---
