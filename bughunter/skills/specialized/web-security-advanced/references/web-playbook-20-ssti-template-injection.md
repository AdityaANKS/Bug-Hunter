# SSTITemplate injection
English: SSTI Template Injection
- Entry Count: 10
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Jinja2Template injection
- ID: ssti-jinja2
- Difficulty: advanced
- Subcategory: Jinja2
- Tags: ssti, jinja2, twig, template
- Original Extracted Source: original extracted web-security-wiki source/ssti-jinja2.md
Description:
Jinja2/TwigTemplate injection attack technique
Prerequisites:
- UseJinja2/TwigTemplate engine
- User input directly rendered to the template
Execution Outline:
1. 1. DetectionSSTI
2. 2. Information gathering
3. 3. Command execution
4. 4. BounceShell
## FreeMarkerTemplate injection
- ID: ssti-freemarker
- Difficulty: intermediate
- Subcategory: FreeMarker
- Tags: ssti, freemarker, java, template
- Original Extracted Source: original extracted web-security-wiki source/ssti-freemarker.md
Description:
FreeMarkerTemplate Engine Injection Attack Techniques
Prerequisites:
- UseFreeMarkerTemplate engine
- User input directly rendered to the template
Execution Outline:
1. 1. DetectionSSTI
2. 2. Information gathering
3. 3. Command execution - new
4. 4. Command execution - api
## VelocityTemplate injection
- ID: ssti-velocity
- Difficulty: advanced
- Subcategory: Velocity
- Tags: ssti, velocity, java, template
- Original Extracted Source: original extracted web-security-wiki source/ssti-velocity.md
Description:
VelocityTemplate Engine Injection Attack Techniques
Prerequisites:
- UseVelocityTemplate engine
- User input directly rendered to the template
Execution Outline:
1. 1. DetectionSSTI
2. 2. Information gathering
3. 3. Command execution - ClassTool
4. 4. Command execution - Reflection
## ThymeleafTemplate injection
- ID: ssti-thymeleaf
- Difficulty: intermediate
- Subcategory: Thymeleaf
- Tags: ssti, thymeleaf, java, spring, template
- Original Extracted Source: original extracted web-security-wiki source/ssti-thymeleaf.md
Description:
ThymeleafTemplate Engine Injection Attack Techniques
Prerequisites:
- UseThymeleafTemplate engine
- SpringFramework
- User input directly rendered to the template
Execution Outline:
1. 1. DetectionSSTI
2. 2. Information gathering
3. 3. Command execution - SpringExpression
4. 4. Command execution - ProcessBuilder
## SmartyTemplate injection
- ID: ssti-smarty
- Difficulty: intermediate
- Subcategory: Smarty
- Tags: ssti, smarty, php, template
- Original Extracted Source: original extracted web-security-wiki source/ssti-smarty.md
Description:
SmartyTemplate Engine Injection Attack Techniques
Prerequisites:
- UseSmartyTemplate engine
- User input directly rendered to the template
Execution Outline:
1. 1. DetectionSSTI
2. 2. Information gathering
3. 3. Command execution - system
4. 4. Command execution - passthru
## MakoTemplate injection
- ID: ssti-mako
- Difficulty: intermediate
- Subcategory: Mako
- Tags: ssti, mako, python, template
- Original Extracted Source: original extracted web-security-wiki source/ssti-mako.md
Description:
MakoTemplate Engine Injection Attack Techniques
Prerequisites:
- UseMakoTemplate engine
- User input directly rendered to the template
Execution Outline:
1. 1. DetectionSSTI
2. 2. Information gathering
3. 3. Command execution - osModule
4. 4. Command execution - subprocess
## TornadoTemplate injection
- ID: ssti-tornado
- Difficulty: intermediate
- Subcategory: Tornado
- Tags: ssti, tornado, python, template
- Original Extracted Source: original extracted web-security-wiki source/ssti-tornado.md
Description:
TornadoTemplate Engine Injection Attack Techniques
Prerequisites:
- UseTornadoTemplate engine
- User input directly rendered to the template
Execution Outline:
1. 1. DetectionSSTI
2. 2. Information gathering
3. 3. Command execution - os
4. 4. Command execution - subprocess
## DjangoTemplate injection
- ID: ssti-django
- Difficulty: intermediate
- Subcategory: Django
- Tags: ssti, django, python, template
- Original Extracted Source: original extracted web-security-wiki source/ssti-django.md
Description:
DjangoTemplate Engine Injection Attack Techniques
Prerequisites:
- UseDjangoTemplate engine
- User input directly rendered to the template
Execution Outline:
1. 1. DetectionSSTI
2. 2. Information gathering
3. 3. Command execution - Passsettings
4. 4. Command execution - Object chain
## ERBTemplate injection
- ID: ssti-erb
- Difficulty: intermediate
- Subcategory: ERB
- Tags: ssti, erb, ruby, template
- Original Extracted Source: original extracted web-security-wiki source/ssti-erb.md
Description:
ERB(Ruby)Template Engine Injection Attack Techniques
Prerequisites:
- UseERBTemplate engine
- User input directly rendered to the template
Execution Outline:
1. 1. DetectionSSTI
2. 2. Information gathering
3. 3. Command execution - Backtick
4. 4. Command execution - system
## Pug/JadeTemplate injection
- ID: ssti-pug
- Difficulty: intermediate
- Subcategory: Pug
- Tags: ssti, pug, jade, nodejs, template
- Original Extracted Source: original extracted web-security-wiki source/ssti-pug.md
Description:
Pug/JadeTemplate Engine Injection Attack Techniques
Prerequisites:
- UsePug/JadeTemplate engine
- User input directly rendered to the template
Execution Outline:
1. 1. DetectionSSTI
2. 2. Information gathering
3. 3. Command execution - child_process
4. 4. Command execution - execSync

