# RCERemote code execution
English: RCE Remote Code Execution
- Entry Count: 12
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Command injection
- ID: rce-command-injection
- Difficulty: intermediate
- Subcategory: Command injection
- Tags: rce, command, injection, os
- Original Extracted Source: original extracted web-security-wiki source/rce-command-injection.md
Description:
Operating System Command Injection Attack Techniques
Prerequisites:
- System Command Execution Capability Exists
- User input not filtered
Execution Outline:
1. 1. Detect command injection
2. 2. LinuxCommand injection
3. 3. WindowsCommand injection
4. 4. Blind command injection.
## PHPCode execution.
- ID: rce-php
- Difficulty: intermediate
- Subcategory: PHPCode execution.
- Tags: rce, php, code, execution
- Original Extracted Source: original extracted web-security-wiki source/rce-php.md
Description:
PHPCode execution vulnerability exploitation techniques
Prerequisites:
- ExistencePHPCode execution point
- User input can control code
Execution Outline:
1. 1. Common dangerous functions
2. 2. Command execution
3. 3. A one-liner trojan
4. 4. Bypass one-liner
## PHP FilterChainRCE
- ID: rce-php-filter
- Difficulty: advanced
- Subcategory: PHP FilterChain
- Tags: rce, php, filter, chain
- Original Extracted Source: original extracted web-security-wiki source/rce-php-filter.md
Description:
UtilizePHP FilterChain constructionRCE
Prerequisites:
- File inclusion vulnerability exists
- PHPVersion supportFilterChain
Execution Outline:
1. 1. FilterChain Principle
2. 2. Construct.FilterChain
3. 3. Tool Generated
4. 4. Fully utilizing examples
## Blind command injection.
- ID: rce-cmd-blind
- Difficulty: intermediate
- Subcategory: Blind command injection.
- Tags: rce, blind, command, injection
- Original Extracted Source: original extracted web-security-wiki source/rce-cmd-blind.md
Description:
No echo command injection exploitation techniques
Prerequisites:
- There are command injection points
- No direct echo
Execution Outline:
1. 1. Time-based blind injection
2. 2. DNSTakeaway
3. 3. HTTPTakeaway
4. 4. ICMPTakeaway
## Deserialization vulnerability
- ID: rce-deserialize
- Difficulty: advanced
- Subcategory: Deserialization
- Tags: rce, deserialize, java, php
- Original Extracted Source: original extracted web-security-wiki source/rce-deserialize.md
Description:
Achieved through Exploiting Deserialization VulnerabilitiesRCE
Prerequisites:
- Deserialization points exist.
- There are exploitableGadgetChain
Execution Outline:
1. 1. JavaDeserialization
2. 2. PHPDeserialization
3. 3. PythonDeserialization
4. 4. .NETDeserialization
## PHPDeserialization
- ID: rce-deserialize-php
- Difficulty: advanced
- Subcategory: PHPDeserialization
- Tags: rce, php, deserialize, unserialize
- Original Extracted Source: original extracted web-security-wiki source/rce-deserialize-php.md
Description:
PHPDeserialization vulnerability exploitation techniques
Prerequisites:
- ExistenceunserializeCall
- There are exploitable classes
Execution Outline:
1. 1. Magic methods
2. 2. Construct.POPChain
3. 3. PharDeserialization
4. 4. SessionDeserialization
## JavaDeserialization
- ID: rce-deserialize-java
- Difficulty: advanced
- Subcategory: JavaDeserialization
- Tags: rce, java, deserialize, ysoserial
- Original Extracted Source: original extracted web-security-wiki source/rce-deserialize-java.md
Description:
JavaDeserialization vulnerability exploitation techniques
Prerequisites:
- ExistenceJavaDeserialization point
- ExistenceGadgetChain
Execution Outline:
1. 1. CommonGadgetChain
2. 2. Useysoserial
3. 3. JRMPAttack
4. 4. Memory horse injection
## File upload vulnerability
- ID: rce-file-upload
- Difficulty: intermediate
- Subcategory: File upload
- Tags: rce, upload, webshell, file
- Original Extracted Source: original extracted web-security-wiki source/rce-file-upload.md
Description:
Exploit file upload vulnerabilities to obtainRCE
Prerequisites:
- the existence of file upload functionality
- Uploadable executable files
Execution Outline:
1. 1. Basic upload
2. 2. Frontend bypass
3. 3. Backend bypass
4. 4. Image Malware
## File inclusionRCE
- ID: rce-include
- Difficulty: intermediate
- Subcategory: File inclusion
- Tags: rce, include, lfi, rfi
- Original Extracted Source: original extracted web-security-wiki source/rce-include.md
Description:
Exploit file inclusion vulnerabilities to achieve.RCE
Prerequisites:
- File inclusion vulnerability exists
- May contain malicious files
Execution Outline:
1. 1. Log Poisoning
2. 2. SessionFile inclusion
3. 3. /proc/self/environ
4. 4. PHPPseudo-protocol
## Log PoisoningRCE
- ID: rce-log-poison
- Difficulty: intermediate
- Subcategory: Log Poisoning
- Tags: rce, log, poison, lfi
- Original Extracted Source: original extracted web-security-wiki source/rce-log-poison.md
Description:
Achieve by log poisoningRCE
Prerequisites:
- File inclusion vulnerability exists
- Readable Log Files
Execution Outline:
1. 1. ApacheLog Poisoning
2. 2. NginxLog Poisoning
## Image MalwareRCE
- ID: rce-image
- Difficulty: intermediate
- Subcategory: Image Malware
- Tags: rce, image, webshell, upload
- Original Extracted Source: original extracted web-security-wiki source/rce-image.md
Description:
Achieve through image web shellsRCE
Prerequisites:
- File upload exists
- File inclusion exists
Execution Outline:
1. 1. Create image horses
2. 2. Image horse content
3. 3. Remote execution via file inclusion
4. 4. Cooperation.htaccess
## .htaccessUtilize
- ID: rce-htaccess
- Difficulty: intermediate
- Subcategory: .htaccess
- Tags: rce, htaccess, apache, upload
- Original Extracted Source: original extracted web-security-wiki source/rce-htaccess.md
Description:
Utilize.htaccessFile implementationRCE
Prerequisites:
- ApacheServer
- Uploadable.htaccess
Execution Outline:
1. 1. Resolve other extensions
2. 2. Automatic inclusion
3. 3. Pseudo staticRCE
4. 4. Error page includes

