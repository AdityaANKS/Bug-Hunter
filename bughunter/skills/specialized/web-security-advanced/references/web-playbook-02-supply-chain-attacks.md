# Supply chain attack
English: Supply Chain Attacks
- Entry Count: 3
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## NPMPackage name spoofing(Typosquatting)
- ID: supply-typosquat
- Difficulty: intermediate
- Subcategory: Package manager poisoning
- Tags: Supply chain, NPM, Typosquatting, Package poisoning, postinstall
- Original Extracted Source: original extracted web-security-wiki source/supply-typosquat.md
Description:
Through Registration and PopularityNPMMalicious packages with highly similar package names(Such aslodash→1odash, colors→co1ors), inducing developers to mistakenly install. Malicious package ininstall/postinstallExecute reverse shell in hooksShell、Stealing environment variables or implanting backdoors.
Prerequisites:
- NPMAccount
- Understand target project dependencies
- Malicious packet infrastructure
Execution Outline:
1. 1. Reconnaissance target dependencies
2. 2. Generate Spoofed Package Name
3. 3. Construct malicious packages
4. 4. Detection and forensics
## CI/CDPipeline poisoning
- ID: supply-ci-poison
- Difficulty: advanced
- Subcategory: CI/CDAttack
- Tags: Supply chain, CI/CD, GitHub Actions, Jenkins, Pipeline
- Original Extracted Source: original extracted web-security-wiki source/supply-ci-poison.md
Description:
Through MaliciousPull Request、ActionsInjection or construction of script tampering to attackCI/CDPipeline. Attackers can steal the constructed keys、Poison build artifacts or implant backdoor code during the deployment process.
Prerequisites:
- The target uses openCI/CD
- Can be submittedPROrFork
Execution Outline:
1. 1. IdentificationCI/CDConfiguration
2. 2. PRTriggered workflow injection
3. 3. ActionsExpression injection
4. 4. Build artifact poisoning
## Dependency confusion attack
- ID: supply-dependency-confusion
- Difficulty: intermediate
- Subcategory: Dependency obfuscation
- Tags: Supply chain, Dependency obfuscation, NPM, PyPI, Dependency Confusion
- Original Extracted Source: original extracted web-security-wiki source/supply-dependency-confusion.md
Description:
Exploit the vulnerability in the resolution priority between public and private registries when using package managers. When enterprises use internal package names, attackers exploit publicNPM/PyPIRegister a higher version number of the same name package, the package manager will prioritize installing the public high version package thus executing malicious code.
Prerequisites:
- Known target internal package name
- Public registry account
Execution Outline:
1. 1. Discover internal package names
2. 2. Registering identically named packages in the public registry
3. 3. MonitoringDNSCallback confirmation hits.
4. 4. Impact assessment and reporting.

