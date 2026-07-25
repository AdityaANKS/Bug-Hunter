# LFI/RFIFile inclusion
English: LFI/RFI File Inclusion
- Entry Count: 12
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Local file inclusion
- ID: lfi-basic
- Difficulty: intermediate
- Subcategory: Local inclusion
- Tags: lfi, local, file, inclusion
- Original Extracted Source: original extracted web-security-wiki source/lfi-basic.md
Description:
Local File Inclusion Exploit Technique
Prerequisites:
- File inclusion functionality exists
- User Controllable Include Path
Execution Outline:
1. 1. DetectionLFI
2. 2. Read sensitive files
3. 3. PHPPseudo-protocol
4. 4. Log Poisoning
## Remote file inclusion
- ID: rfi-basic
- Difficulty: intermediate
- Subcategory: Remote inclusion
- Tags: rfi, remote, file, inclusion
- Original Extracted Source: original extracted web-security-wiki source/rfi-basic.md
Description:
Remote file inclusion vulnerability exploitation techniques
Prerequisites:
- File inclusion functionality exists
- allow_url_include=On
- User Controllable Include Path
Execution Outline:
1. 1. DetectionRFI
2. 2. Hosting malicious files
3. 3. BounceShell
4. 4. UsedataProtocol
## Log PoisoningLFI
- ID: lfi-log-poison
- Difficulty: intermediate
- Subcategory: Log Poisoning
- Tags: lfi, log, poison, rce
- Original Extracted Source: original extracted web-security-wiki source/lfi-log-poison.md
Description:
Achieve via log poisoningLFIToRCE
Prerequisites:
- ExistenceLFIVulnerability
- May contain log files
- Log file writable
Execution Outline:
1. 1. Probe log file locations
2. 2. PoisoningUser-Agent
3. 3. Poisoning Request Path
4. 4. Execute Command
## PHPPseudo Protocol Exploitation
- ID: lfi-wrapper
- Difficulty: intermediate
- Subcategory: Pseudo-protocol
- Tags: lfi, wrapper, php, protocol
- Original Extracted Source: original extracted web-security-wiki source/lfi-wrapper.md
Description:
UtilizePHPPseudo-protocol forLFIAttack
Prerequisites:
- ExistenceLFIVulnerability
- PHPEnvironment
- Pseudo Protocol Not Disabled
Execution Outline:
1. 1. php://filter
2. 2. php://input
3. 3. data://Protocol
4. 4. phar://Protocol
## Directory traversal technique
- ID: lfi-traversal
- Difficulty: beginner
- Subcategory: Directory traversal
- Tags: lfi, traversal, bypass, path
- Original Extracted Source: original extracted web-security-wiki source/lfi-traversal.md
Description:
LFIDirectory traversal bypass technique
Prerequisites:
- ExistenceLFIVulnerability
- Existing path filtering
Execution Outline:
1. 1. Basic traversal
2. 2. Bypass deletion../
3. 3. URLEncoding bypass
4. 4. UnicodeEncoding bypass
## PHP FilterChain Attack
- ID: lfi-php-filter
- Difficulty: intermediate
- Subcategory: PHP Filter
- Tags: lfi, php, filter, chain
- Original Extracted Source: original extracted web-security-wiki source/lfi-php-filter.md
Description:
UtilizePHP FilterChain proceedLFIAttack
Prerequisites:
- ExistenceLFIVulnerability
- PHPEnvironment
- filterPseudo Protocol Available
Execution Outline:
1. 1. Read source code
2. 2. Multiple filters
3. 3. FilterChainRCE
4. 4. Read configuration files
## PHP InputExecute
- ID: lfi-php-input
- Difficulty: intermediate
- Subcategory: PHP Input
- Tags: lfi, php, input, rce
- Original Extracted Source: original extracted web-security-wiki source/lfi-php-input.md
Description:
Utilizephp://inputExecutePHPCode
Prerequisites:
- ExistenceLFIVulnerability
- allow_url_include=On
- POSTMethods available.
Execution Outline:
1. 1. Basic execution
2. 2. Command execution
3. 3. File operation
4. 4. BounceShell
## PHP DataProtocol Attacks
- ID: lfi-php-data
- Difficulty: intermediate
- Subcategory: PHP Data
- Tags: lfi, php, data, protocol
- Original Extracted Source: original extracted web-security-wiki source/lfi-php-data.md
Description:
Utilizedata://Protocol execution.PHPCode
Prerequisites:
- ExistenceLFIVulnerability
- allow_url_include=On
- dataProtocol Available
Execution Outline:
1. 1. Basic execution
2. 2. Base64Code
3. 3. Command execution
4. 4. BounceShell
## PHP ZipProtocol Attacks
- ID: lfi-php-zip
- Difficulty: intermediate
- Subcategory: PHP Zip
- Tags: lfi, php, zip, archive
- Original Extracted Source: original extracted web-security-wiki source/lfi-php-zip.md
Description:
Utilizezip://Protocols forLFIAttack
Prerequisites:
- ExistenceLFIVulnerability
- UploadablezipFile
- zipProtocol Available
Execution Outline:
1. 1. Create maliciousZip
2. 2. UploadZipFile
3. 3. ContainZipFile
4. 4. Image Malware
## PharDeserialization attack
- ID: lfi-phar
- Difficulty: advanced
- Subcategory: PharDeserialization
- Tags: lfi, phar, deserialization, rce
- Original Extracted Source: original extracted web-security-wiki source/lfi-phar.md
Description:
UtilizePharPerform deserializationRCE
Prerequisites:
- ExistenceLFIVulnerability
- PHPEnvironment
- pharExtendable
Execution Outline:
1. 1. CreatePharFile
2. 2. Trigger deserialization
3. 3. Image MalwarePhar
4. 4. CommonGadgetChain
## SessionFile inclusion
- ID: lfi-session
- Difficulty: intermediate
- Subcategory: SessionContain
- Tags: lfi, session, file, inclusion
- Original Extracted Source: original extracted web-security-wiki source/lfi-session.md
Description:
UtilizeSessionPerform on FileLFIAttack
Prerequisites:
- ExistenceLFIVulnerability
- ControllableSessionContent
- Know.SessionPath
Execution Outline:
1. 1. DetectionSessionPath
2. 2. ControlSessionContent
3. 3. ContainSessionFile
4. 4. SessionCompetitive conditions
## ProcFile system exploitation
- ID: lfi-proc
- Difficulty: intermediate
- Subcategory: ProcFile system
- Tags: lfi, proc, linux, environ
- Original Extracted Source: original extracted web-security-wiki source/lfi-proc.md
Description:
Utilize/procFile system forLFIAttack
Prerequisites:
- ExistenceLFIVulnerability
- LinuxSystem
- /procAccessible
Execution Outline:
1. 1. Read process information
2. 2. Reading environment variables
3. 3. PassfdRead logs
4. 4. Read other processes

