# SSRFServer-side request forgery
English: SSRF Server-Side Request Forgery
- Entry Count: 12
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## BasicsSSRFAttack
- ID: ssrf-basic
- Difficulty: intermediate
- Subcategory: Basic Attack
- Tags: ssrf, server-side, request
- Original Extracted Source: original extracted web-security-wiki source/ssrf-basic.md
Description:
Server request forgery foundational attack techniques
Prerequisites:
- ExistenceURLInput Point
- The server will request user-providedURL
Execution Outline:
1. 1. DetectionSSRF
2. 2. Scan internal network ports
3. 3. Access Internal Network Services
4. 4. Read Local Files
## AWSMetadata attack
- ID: ssrf-cloud-aws
- Difficulty: intermediate
- Subcategory: Cloud metadata
- Tags: ssrf, aws, metadata, cloud
- Original Extracted Source: original extracted web-security-wiki source/ssrf-cloud-aws.md
Description:
UtilizeSSRFAccessAWS EC2Metadata service
Prerequisites:
- ExistenceSSRFVulnerability
- The target runs onAWS EC2Up
Execution Outline:
1. 1. Access metadata services
2. 2. ObtainIAMCredentials
3. 3. Obtain user data
4. 4. UseIMDSv2Bypass
## GCPMetadata attack
- ID: ssrf-cloud-gcp
- Difficulty: intermediate
- Subcategory: GCPMetadata
- Tags: ssrf, gcp, cloud, metadata
- Original Extracted Source: original extracted web-security-wiki source/ssrf-cloud-gcp.md
Description:
UtilizeSSRFAttackGoogle CloudMetadata service
Prerequisites:
- ExistenceSSRFVulnerability
- The target runs onGCPEnvironment
Execution Outline:
1. 1. Access metadata services
2. 2. Obtain access token
3. 3. Obtain Service Account Information
4. 4. Obtain project information
## AzureMetadata attack
- ID: ssrf-cloud-azure
- Difficulty: intermediate
- Subcategory: AzureMetadata
- Tags: ssrf, azure, cloud, metadata
- Original Extracted Source: original extracted web-security-wiki source/ssrf-cloud-azure.md
Description:
UtilizeSSRFAttackAzureMetadata service
Prerequisites:
- ExistenceSSRFVulnerability
- The target runs onAzureEnvironment
Execution Outline:
1. 1. Access metadata services
2. 2. Obtain access token
3. 3. Obtain computing information
4. 4. Obtain network information
## SSRFProtocol Exploitation
- ID: ssrf-protocol
- Difficulty: intermediate
- Subcategory: Protocol Exploitation
- Tags: ssrf, protocol, file, gopher
- Original Extracted Source: original extracted web-security-wiki source/ssrf-protocol.md
Description:
Utilize various protocols forSSRFAttack
Prerequisites:
- ExistenceSSRFVulnerability
- The server supports multiple protocols
Execution Outline:
1. 1. FileProtocol
2. 2. DictProtocol
3. 3. GopherProtocol
4. 4. LDAPProtocol
## GopherProtocol Attacks
- ID: ssrf-gopher
- Difficulty: advanced
- Subcategory: GopherAttack
- Tags: ssrf, gopher, redis, mysql
- Original Extracted Source: original extracted web-security-wiki source/ssrf-gopher.md
Description:
UtilizeGopherProtocol attacks on internal network services
Prerequisites:
- ExistenceSSRFVulnerability
- Server supportGopherProtocol
Execution Outline:
1. 1. GopherBasic format
2. 2. AttackRedis
3. 3. AttackMySQL
4. 4. AttackFastCGI
## DictProtocol Attacks
- ID: ssrf-dict
- Difficulty: intermediate
- Subcategory: DictProtocol
- Tags: ssrf, dict, redis, memcached
- Original Extracted Source: original extracted web-security-wiki source/ssrf-dict.md
Description:
UtilizeDictProtocol Detection and Attacking Internal Network Services
Prerequisites:
- ExistenceSSRFVulnerability
- Server supportDictProtocol
Execution Outline:
1. 1. DictProtocol format
2. 2. DetectionRedis
3. 3. DetectionMemcached
4. 4. RedisWrite to file
## FileProtocol Attacks
- ID: ssrf-file
- Difficulty: beginner
- Subcategory: FileProtocol
- Tags: ssrf, file, lfi, read
- Original Extracted Source: original extracted web-security-wiki source/ssrf-file.md
Description:
UtilizeFileProtocol Read Local Files
Prerequisites:
- ExistenceSSRFVulnerability
- Server supportFileProtocol
Execution Outline:
1. 1. LinuxSensitive files
2. 2. WindowsSensitive files
3. 3. WebConfiguration file
4. 4. Cloud environment files
## SSRFBypass techniques
- ID: ssrf-bypass
- Difficulty: intermediate
- Subcategory: Bypass techniques
- Tags: ssrf, bypass, waf, filter
- Original Extracted Source: original extracted web-security-wiki source/ssrf-bypass.md
Description:
Various BypassesSSRFFiltering techniques
Prerequisites:
- ExistenceSSRFVulnerability
- Filtering Mechanism Exists
Execution Outline:
1. 1. IPFormat bypass
2. 2. URLAnalyze differences
3. 3. Redirection bypass
4. 4. DNSRebinding
## DNSRebinding Attack
- ID: ssrf-dns-rebinding
- Difficulty: advanced
- Subcategory: DNSRebinding
- Tags: ssrf, dns, rebinding, bypass
- Original Extracted Source: original extracted web-security-wiki source/ssrf-dns-rebinding.md
Description:
UtilizeDNSRebinding bypassSSRFProtection
Prerequisites:
- ExistenceSSRFVulnerability
- ExistenceDNSParsing verification
Execution Outline:
1. 1. DNSRebinding Principle
2. 2. Use public services
3. 3. Self-builtDNSServer
4. 4. Attack process
## SSRFAttackRedis
- ID: ssrf-redis
- Difficulty: intermediate
- Subcategory: RedisAttack
- Tags: ssrf, redis, rce, webshell
- Original Extracted Source: original extracted web-security-wiki source/ssrf-redis.md
Description:
UtilizeSSRFAttack the internal networkRedisService
Prerequisites:
- ExistenceSSRFVulnerability
- Unauthorized access in the intranetRedis
Execution Outline:
1. 1. DetectionRedis
2. 2. WriteWebShell
3. 3. WriteSSHPublic key
4. 4. WriteCronTask
## SSRFAttackMySQL
- ID: ssrf-mysql
- Difficulty: advanced
- Subcategory: MySQLAttack
- Tags: ssrf, mysql, gopher, database
- Original Extracted Source: original extracted web-security-wiki source/ssrf-mysql.md
Description:
UtilizeSSRFAttack the internal networkMySQLService
Prerequisites:
- ExistenceSSRFVulnerability
- Internal network existsMySQLService
- Know.MySQLUsername
Execution Outline:
1. 1. MySQLProtocol Foundation
2. 2. UseGopherAttackMySQL
3. 3. Tool GeneratedPayload
4. 4. ExecuteSQLCommand

