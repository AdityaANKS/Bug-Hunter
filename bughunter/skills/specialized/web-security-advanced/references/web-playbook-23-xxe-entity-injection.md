# XXEEntity injection
English: XXE Entity Injection
- Entry Count: 9
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## XXEBasic Attack
- ID: xxe-basic
- Difficulty: intermediate
- Subcategory: Basic Attack
- Tags: xxe, xml, external, entity
- Original Extracted Source: original extracted web-security-wiki source/xxe-basic.md
Description:
XMLExternal entity injection basic attack techniques
Prerequisites:
- ExistenceXMLParsing function
- External entities not disabled
Execution Outline:
1. 1. DetectionXXE
2. 2. Read file
3. 3. ReadPHPSource code
4. 4. SSRFAttack
## Blind injectionXXEAttack
- ID: xxe-blind
- Difficulty: intermediate
- Subcategory: Blind injectionXXE
- Tags: xxe, blind, oob, xml
- Original Extracted Source: original extracted web-security-wiki source/xxe-blind.md
Description:
No echoXXEAttack techniques
Prerequisites:
- ExistenceXMLAnalysis
- No direct echo
Execution Outline:
1. 1. External entity detection
2. 2. Parameter entity
3. 3. OOBTakeout data
## XXE OOBTakeaway attack
- ID: xxe-oob
- Difficulty: intermediate
- Subcategory: OOBTakeaway
- Tags: xxe, oob, exfiltration, xml
- Original Extracted Source: original extracted web-security-wiki source/xxe-oob.md
Description:
UtilizeOOBTechnical takeoutXXEData
Prerequisites:
- ExistenceXXEVulnerability
- Can initiate external requests
Execution Outline:
1. 1. HTTPTakeaway
2. 2. FTPTakeaway
3. 3. DNSTakeaway
## XXE+SSRFCombination attack
- ID: xxe-ssrf
- Difficulty: intermediate
- Subcategory: XXE+SSRF
- Tags: xxe, ssrf, combination, xml
- Original Extracted Source: original extracted web-security-wiki source/xxe-ssrf.md
Description:
UtilizeXXEImplementSSRFAttack
Prerequisites:
- ExistenceXXEVulnerability
- Accessible from the intranet
Execution Outline:
1. 1. Scan internal network ports
2. 2. Access Internal Network Services
## XXEToRCE
- ID: xxe-rce
- Difficulty: advanced
- Subcategory: XXEToRCE
- Tags: xxe, rce, php, expect
- Original Extracted Source: original extracted web-security-wiki source/xxe-rce.md
Description:
UtilizeXXEAchieve remote code execution
Prerequisites:
- ExistenceXXEVulnerability
- PHP expectExtension loading
Execution Outline:
1. 1. ExpectExpansionRCE
2. 2. WriteWebShell
## XXEFile reading
- ID: xxe-file-read
- Difficulty: beginner
- Subcategory: File reading
- Tags: xxe, file, read, lfi
- Original Extracted Source: original extracted web-security-wiki source/xxe-file-read.md
Description:
UtilizeXXERead server files
Prerequisites:
- ExistenceXXEVulnerability
- Has File Read Permissions
Execution Outline:
1. 1. ReadLinuxFile
2. 2. ReadWindowsFile
3. 3. ReadWebConfiguration
4. 4. Read source code
## XXEExternalDTDUtilize
- ID: xxe-dtd
- Difficulty: intermediate
- Subcategory: ExternalDTD
- Tags: xxe, dtd, external, xml
- Original Extracted Source: original extracted web-security-wiki source/xxe-dtd.md
Description:
Exploit externalDTDPerform on FileXXEAttack
Prerequisites:
- ExistenceXXEVulnerability
- Accessible externallyDTD
Execution Outline:
1. 1. Hosting maliciousDTD
2. 2. Reference ExternalDTD
3. 3. Multi-step takeaway
4. 4. Error message leakage
## XLSXFileXXE
- ID: xxe-xlsx
- Difficulty: intermediate
- Subcategory: XLSXFileXXE
- Tags: xxe, xlsx, excel, office
- Original Extracted Source: original extracted web-security-wiki source/xxe-xlsx.md
Description:
UtilizeXLSXPerform on FileXXEAttack
Prerequisites:
- Application parsingXLSXFile
- ExistenceXXEVulnerability
Execution Outline:
1. 1. UnzipXLSXFile
2. 2. InjectionXXE Payload
## DOCXFileXXE
- ID: xxe-docx
- Difficulty: intermediate
- Subcategory: DOCXFileXXE
- Tags: xxe, docx, word, office
- Original Extracted Source: original extracted web-security-wiki source/xxe-docx.md
Description:
UtilizeDOCXPerform on FileXXEAttack
Prerequisites:
- Application parsingDOCXFile
- ExistenceXXEVulnerability
Execution Outline:
1. 1. UnzipDOCXFile
2. 2. InjectionXXE Payload

