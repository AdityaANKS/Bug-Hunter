# AIData security - Deployment phase

> Source: AISSGreen Alliance Large Model Security Intelligence Chain Community | Dismantled From ai-data-security.md
> Phase: Deployment phase (GAARM.0012-0016 Backup/Transmission/Storage/Log/Cache)

## Deployment phase

### Backup data theft

> Risk number: GAARM.0012
> Lifecycle: Deployment phase

**Attack overview**

Backup data typically contains the model's training data、Algorithm Logic、Sensitive data、Important information such as personal data. If poorly protected, attackers can obtain backup data through unauthorized access or other attack methods, leading to risks such as leakage of important information related to the model, and even economic risks.

**Attack Cases**

Case
Description




Case One
The attacker obtained access credentials of employees from a tech company through phishing emails, unauthorized access to cloud storage services led to the theft of large model backup data containing sensitive personal information and trade secrets, exposing the company to legal and economic risks

**Attack risks**

Model Tampering: If the backup data contains the training data of the model、Information such as algorithms that attackers can use to tamper with the model, etc.
Sensitive data leakage: If backup data includes user、Customer information leakage can lead to identity theft、Fraudulent activities、Ransomware, etc.

**Mitigation measures**

Mitigation method
Description




Data Encryption
Use strong encryption algorithms during backup data storage to ensure that data is protected in both storage and transmission, making it difficult to decrypt even if leaked.


Multi-factor authentication
Introduce multiple authentication mechanisms, such as two-factor authentication, to enhance access control over backup data and improve security

---
### Data transmission hijacking

> Risk number: GAARM.0013
> Lifecycle: Deployment phase

**Attack overview**

When pre-training large models、During fine-tuning and inference services, it is necessary to transmit data between different entities or departments. This data often contains various sensitive information and privacy, such as personal identification information and financial data. Attackers can maliciously intercept data during transmission, thereby obtaining related privacy information, which may lead to sensitive information leakage, posing security and privacy issues for users.

**Attack Cases**

Case
Description




Case One
Attackers exploited an unencrypted network transmission vulnerability to successfully intercept personal financial data transmitted by a financial institution during large model services, leading to sensitive information leakage and posing security and privacy risks to users

**Attack risks**

Sensitive data leakage: attackers may obtain sensitive information such as personal identity information by intercepting data、Financial data、Medical records, etc.
Intellectual Property: If the data contains trade secrets or proprietary algorithms, data interception may lead to the leakage of such intellectual property.

**Mitigation measures**

Mitigation method
Description




Data Encryption
By Encrypting Sensitive Data, Ensure Data Security During Transmission

**Reference**

https://bj.bcebos.com/ensec-web-privacy/anquan/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%AE%89%E5%85%A8%E8%A7%A3%E5%86%B3%E6%96%B9%E6%A1%88%E7%99%BD%E7%9A%AE%E4%B9%A6.pdf
https://mp.weixin.qq.com/s/JlJwDRzYG985kF4d6g7qjw

---
### Data storage service attack

> Risk number: GAARM.0014
> Lifecycle: Deployment phase

**Attack overview**

This risk refers to potential security vulnerabilities in the process of data storage and organization, such as insufficient access control、Unsafe data handling practices or the lack of encryption measures, attackers can exploit related vulnerabilities for unauthorized access、Attacks like data leakage or tampering can acquire sensitive information, and even enable identity theft.、Fraud activities, etc., leading to exposure of user privacy and corporate assets, resulting in data breaches、The possibility of legal action and reputational loss.

**Attack Cases**

Case
Description




Case One
Clearview AIThe source code repository was misconfigured, allowing any user to access it, exposing production credentials and training data, emphasizingMLSystem security needs to strengthen traditional cybersecurity measures.

**Attack risks**

Sensitive data leakage: Sensitive data that is not protected by encryption or has improper access controls may be obtained by attackers, leading to data leakage.
Identity theft: Stored personal identification information may be stolen for identity theft.、Crimes such as fraud.

**Mitigation measures**

Mitigation method
Description




Access Control
Ensure that only authorized users can access data in the repository


Data classification
Classify information in the repository and implement corresponding security measures based on data sensitivity


Data Encryption
Encrypt sensitive data at rest so that even if data is accessed without authorization, its contents remain protected from easy reading

**Reference**

https://news.cctv.com/2022/06/21/ARTIdhgLL1sSK5Hjl0uYWybr220621.shtml
https://atlas.mitre.org/techniques/AML.T0036

---
### Log and audit record theft

> Risk number: GAARM.0015
> Lifecycle: Deployment phase

**Attack overview**

The logs and audit records of the model play a key role in monitoring system activities and events, detailing records including user login behavior、File access status、Information including changes to system configurations and various security incidents. After attackers gain access to relevant server permissions, stealing logs and audit records can expose users' personal behavior patterns and may also reveal potential vulnerabilities in the system, leading to more targeted attacks by attackers.

**Attack Cases**

Case
Description




Case One
This case describeschatgptLeaked user login credentials and personal details

**Attack risks**

Sensitive data leakage: leading to personal privacy breaches、Account theft and other issues.
Targeted Attack: The attacker may be able to discover security vulnerabilities and weaknesses in the system, thereby launching more targeted attacks.

**Mitigation measures**

Mitigation method
Description




Regular audits
Regularly audit access and operations of logs and audit records to check for any abnormal or irregular behavior, timely detecting and addressing security threats


Separation of Logs and Audit Records
Store logs and audit records separately from other data, ensuring their independence from production data to reduce leakage risks


Establish access control policies
Establish strict access control policies, granting access to logs and audit records only to necessary personnel, limiting the scope of permissions, and preventing unauthorized access

**Reference**

https://www.kuaikuaicloud.com/market/3667.html

---
### Cached data&Index information theft

> Risk number: GAARM.0016
> Lifecycle: Deployment phase

**Attack overview**

Cached data and index information may leak sensitive user information, including but not limited to identity recognition information、Payment details and personal preferences, etc. Attackers can manipulate or destroy data through illegal access to cached and indexed data, affecting system operations and data integrity; they can also meticulously plan and implement targeted phishing attacks, using users' personal information to increase the credibility and success rate of the attack, thus posing more serious security threats and financial losses to users.

**Attack Cases**

Case
Description




Case One
This case describesOpenAIUseredisUser Information Cached in Server, Due to Client-Side Open Source Libraryredis-pyError, causing the customer to incorrectly receive cached at receptionRedisOther users' email addresses in

**Attack risks**

Sensitive data leakage: leaked cached data may contain user credential information, such as usernames、Passwords, etc., attackers might use this information for identity theft、Account hijacking and other activities.
Data tampering: Attackers may exploit this information to tamper with or corrupt data in the cache, affecting system operation and data integrity.

**Mitigation measures**

Mitigation method
Description




Data Encryption
By encrypting sensitive data, ensure the safety of the data

**Reference**

http://www.nelab-bdst.org.cn/data/upload/ueditor/20230707/64a78209c719c.pdf

---
