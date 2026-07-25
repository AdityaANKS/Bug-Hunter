# Cloud security vulnerabilities
English: Cloud Security Vulnerabilities
- Entry Count: 4
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## CloudSSRFSteal metadata credentials
- ID: cloud-ssrf-metadata
- Difficulty: intermediate
- Subcategory: IMDSAttack
- Tags: Cloud Security, SSRF, AWS, GCP, Azure, IMDS, Metadata
- Original Extracted Source: original extracted web-security-wiki source/cloud-ssrf-metadata.md
Description:
UtilizeSSRFVulnerability Access to Cloud Services(AWS/GCP/Azure)Instance metadata services(IMDS)Obtain temporaryIAMCredentials. Attackers can acquire theAccess KeyTaking over cloud resources to achieve from.WebHorizontal escalation of vulnerabilities to the cloud environment.
Prerequisites:
- Target running in a cloud environment
- ExistenceSSRFVulnerability
- Instance bound to.IAMRole
Execution Outline:
1. 1. AWSMetadata Service Detection
2. 2. GCP/AzureMetadata exploitation
3. 3. Lateral Movement Using Obtained Credentials
4. 4. Deep exploitation——S3Data leakage/Privilege Escalation
## S3Bucket misconfiguration exploitation
- ID: cloud-s3-misconfig
- Difficulty: beginner
- Subcategory: S3Security
- Tags: Cloud Security, S3, AWS, Configuration error, Data leakage
- Original Extracted Source: original extracted web-security-wiki source/cloud-s3-misconfig.md
Description:
UtilizeAWS S3Error in the access control configuration of the storage bucket(Public Reading/Write/Enumerate)Obtain sensitive data or implant malicious files. Common in static website hosting、Log storage and backup buckets, which may lead to data leakage、Website tampering or supply chain attacks.
Prerequisites:
- Known targetsS3Bucket name
- AWS CLIOrHTTPAccess
Execution Outline:
1. 1. S3Bucket name enumeration
2. 2. Permission enumeration
3. 3. Sensitive data search
4. 4. Verification Utilization (Static Website Tampering/XSS)
## AWS IAMPrivilege Escalation
- ID: cloud-iam-escalation
- Difficulty: advanced
- Subcategory: IAMPrivilege escalation
- Tags: Cloud Security, AWS, IAM, Privilege Escalation, Privilege Escalation
- Original Extracted Source: original extracted web-security-wiki source/cloud-iam-escalation.md
Description:
In the context of having low permissionsAWSAfter credentials, exploitIAMPolicies(Such asiam:PassRole、lambda:CreateFunctionEtc.)Achieve privilege escalation to administrator. Covering.20+Known typesAWS IAMElevation.
Prerequisites:
- Has been obtainedAWSCredentials
- IAMPolicy has excessive authorization
Execution Outline:
1. 1. Enumerate current permissions
2. 2. iam:PassRole + LambdaPrivilege escalation
3. 3. Other privilege escalation paths
4. 4. Automated privilege escalation tools
## KubernetesContainer escape
- ID: cloud-k8s-escape
- Difficulty: expert
- Subcategory: Container Security
- Tags: Cloud Security, Kubernetes, Container escape, Docker, Privileged container
- Original Extracted Source: original extracted web-security-wiki source/cloud-k8s-escape.md
Description:
After obtainingKubernetes Pod ShellUnder the premise of exploiting configuration errors(Privileged container、Mount host path、ServiceAccountHigh privileges)Achieving container escape, thereby controlling the host machine or the entireKubernetesCluster.
Prerequisites:
- Has been obtainedPodInsideShell
- PodConfiguration errors exist
Execution Outline:
1. 1. Container environment reconnaissance
2. 2. Privilege container escape
3. 3. UtilizeServiceAccountTake over cluster
4. 4. Create privilegesPodBounceShell

