# Framework vulnerabilities.
English: Framework Vulnerabilities
- Entry Count: 18
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Log4j RCE (Log4Shell)
- ID: log4j-rce
- Difficulty: intermediate
- Subcategory: Log4j
- Tags: log4j, rce, cve-2021-44228, log4shell
- Original Extracted Source: original extracted web-security-wiki source/log4j-rce.md
Description:
Apache Log4jRemote code execution vulnerability
Prerequisites:
- UseLog4j 2.xVersion
- User input is logged
Execution Outline:
1. 1. Detect vulnerabilities
2. 2. DNSTakeaway Testing
3. 3. Construct maliciousLDAPServer
4. 4. ObtainShell
## Spring ActuatorVulnerability
- ID: spring-actuator
- Difficulty: intermediate
- Subcategory: Spring
- Tags: spring, actuator, rce, java
- Original Extracted Source: original extracted web-security-wiki source/spring-actuator.md
Description:
Spring Boot ActuatorEndpoint security vulnerabilities
Prerequisites:
- Spring BootApplication
- ActuatorEndpoint exposure
Execution Outline:
1. 1. DetectionActuatorEndpoints
2. 2. Obtain Sensitive Information
3. 3. Download heap dump
4. 4. envEndpointsRCE
## Fastjson RCE
- ID: fastjson-rce
- Difficulty: advanced
- Subcategory: Fastjson
- Tags: fastjson, rce, deserialization, java
- Original Extracted Source: original extracted web-security-wiki source/fastjson-rce.md
Description:
Alibaba FastjsonDeserialization remote code execution
Prerequisites:
- UseFastjsonLibrary
- Deserialization points exist.
Execution Outline:
1. 1. DetectionFastjson
2. 2. JNDIInjection
3. 3. Build malicious services
4. 4. BypassAutoTypeCheck
## Spring SpELInjection
- ID: spring-spel
- Difficulty: intermediate
- Subcategory: Spring SpEL
- Tags: spring, spel, expression, rce
- Original Extracted Source: original extracted web-security-wiki source/spring-spel.md
Description:
SpringExpression Language Injection Attack
Prerequisites:
- UseSpringFramework
- ExistenceSpELInjection point
Execution Outline:
1. 1. DetectionSpELInjection
2. 2. Command execution
3. 3. File reading
4. 4. DNSTakeaway
## Spring CloudVulnerability
- ID: spring-cloud
- Difficulty: advanced
- Subcategory: Spring Cloud
- Tags: spring, cloud, rce, deserialization
- Original Extracted Source: original extracted web-security-wiki source/spring-cloud.md
Description:
Spring CloudRelevant vulnerability exploitation
Prerequisites:
- UseSpring Cloud
- Vulnerable version exists
Execution Outline:
1. 1. Spring Cloud Gateway RCE
2. 2. Spring Cloud Function SpEL
3. 3. Spring Cloud Netflix
## Struts2Remote code execution
- ID: struts2-rce
- Difficulty: intermediate
- Subcategory: Struts2
- Tags: struts2, rce, java, apache
- Original Extracted Source: original extracted web-security-wiki source/struts2-rce.md
Description:
Apache Struts2FrameworkRCEVulnerability
Prerequisites:
- UseStruts2Framework
- Vulnerable version exists
Execution Outline:
1. 1. S2-045Vulnerability
2. 2. S2-046Vulnerability
3. 3. S2-057Vulnerability
4. 4. S2-061/S2-062Vulnerability
## Struts2 OGNLExpression injection
- ID: struts2-ognl
- Difficulty: advanced
- Subcategory: Struts2 OGNL
- Tags: struts2, ognl, expression, injection
- Original Extracted Source: original extracted web-security-wiki source/struts2-ognl.md
Description:
Struts2 OGNLDetailed Explanation of Expression Injection Techniques
Prerequisites:
- UseStruts2Framework
- ExistenceOGNLInjection point
Execution Outline:
1. 1. OGNLBasic syntax.
2. 2. Bypass security restrictions
3. 3. Command execution techniques
4. 4. File operation
## WebLogicRemote code execution
- ID: weblogic-rce
- Difficulty: advanced
- Subcategory: WebLogic
- Tags: weblogic, rce, java, oracle
- Original Extracted Source: original extracted web-security-wiki source/weblogic-rce.md
Description:
Oracle WebLogic Server RCEVulnerability
Prerequisites:
- UseWebLogic Server
- Vulnerable version exists
Execution Outline:
1. 1. CVE-2017-10271
2. 2. CVE-2019-2725
3. 3. CVE-2020-14882
## WebLogic T3Protocol Attacks
- ID: weblogic-t3
- Difficulty: advanced
- Subcategory: WebLogic T3
- Tags: weblogic, t3, deserialization, java
- Original Extracted Source: original extracted web-security-wiki source/weblogic-t3.md
Description:
WebLogic T3Protocol deserialization vulnerability
Prerequisites:
- WebLogicOpenT3Port
- Vulnerable version exists
Execution Outline:
1. 1. DetectionT3Service
2. 2. Use tools to attack
3. 3. Construct maliciousT3Request
## WebLogic IIOPProtocol Attacks
- ID: weblogic-iiop
- Difficulty: advanced
- Subcategory: WebLogic IIOP
- Tags: weblogic, iiop, deserialization, corba
- Original Extracted Source: original extracted web-security-wiki source/weblogic-iiop.md
Description:
WebLogic IIOPProtocol deserialization vulnerability
Prerequisites:
- WebLogicOpenIIOPPort
- Vulnerable version exists
Execution Outline:
1. 1. DetectionIIOPService
2. 2. CVE-2020-2551
3. 3. Construct.IIOPRequest
## ThinkPHPRemote code execution
- ID: thinkphp-rce
- Difficulty: intermediate
- Subcategory: ThinkPHP
- Tags: thinkphp, rce, php, framework
- Original Extracted Source: original extracted web-security-wiki source/thinkphp-rce.md
Description:
ThinkPHPFrameworkRCEVulnerability
Prerequisites:
- UseThinkPHPFramework
- Vulnerable version exists
Execution Outline:
1. 1. ThinkPHP 5.x RCE
2. 2. ThinkPHP 5.1.x RCE
3. 3. ThinkPHP 5.0.23 RCE
4. 4. Information gathering
## LaravelRemote code execution
- ID: laravel-rce
- Difficulty: intermediate
- Subcategory: Laravel
- Tags: laravel, rce, php, framework
- Original Extracted Source: original extracted web-security-wiki source/laravel-rce.md
Description:
LaravelFrameworkRCEVulnerability
Prerequisites:
- UseLaravelFramework
- Vulnerable versions or configurations exist
Execution Outline:
1. 1. CVE-2021-3129
2. 2. Debug mode information leakage
3. 3. .envFile Leakage
4. 4. APP_KEYUtilize
## Apache ShiroDeserialization
- ID: shiro-deserialize
- Difficulty: intermediate
- Subcategory: Apache Shiro
- Tags: shiro, deserialization, java, rememberme
- Original Extracted Source: original extracted web-security-wiki source/shiro-deserialize.md
Description:
Apache Shiro RememberMeDeserialization vulnerability
Prerequisites:
- UseApache Shiro
- Vulnerable version exists
Execution Outline:
1. 1. DetectionShiro
2. 2. UseysoserialGeneratepayload
3. 3. Send malicious requests
4. 4. Common key list
## JBossVulnerability exploitation
- ID: jboss-vuln
- Difficulty: intermediate
- Subcategory: JBoss
- Tags: jboss, rce, java, deserialization
- Original Extracted Source: original extracted web-security-wiki source/jboss-vuln.md
Description:
JBossApplication server vulnerabilities
Prerequisites:
- UseJBossServer
- Vulnerable version exists
Execution Outline:
1. 1. JMXInvokerServletDeserialization
2. 2. JMX ConsoleDeploymentWarPackage
3. 3. BSHDeployerDeployment
4. 4. Use tools
## Apache TomcatVulnerability
- ID: tomcat-vuln
- Difficulty: intermediate
- Subcategory: Tomcat
- Tags: tomcat, rce, java, manager
- Original Extracted Source: original extracted web-security-wiki source/tomcat-vuln.md
Description:
Apache TomcatServer vulnerability exploitation
Prerequisites:
- UseTomcatServer
- Vulnerable versions or configurations exist
Execution Outline:
1. 1. Manager AppWeak Passwords
2. 2. DeploymentWarPackage
3. 3. CVE-2020-1938 Ghostcat
4. 4. PUTArbitrary file write method
## DjangoFramework vulnerabilities.
- ID: django-vuln
- Difficulty: intermediate
- Subcategory: Django
- Tags: django, python, framework, sql
- Original Extracted Source: original extracted web-security-wiki source/django-vuln.md
Description:
DjangoFramework security vulnerabilities
Prerequisites:
- UseDjangoFramework
- Vulnerable version exists
Execution Outline:
1. 1. SQLInjection
2. 2. Debug mode information leakage
3. 3. SECRET_KEYUtilize
4. 4. Path traversal
## FlaskFramework vulnerabilities.
- ID: flask-vuln
- Difficulty: intermediate
- Subcategory: Flask
- Tags: flask, python, framework, ssti
- Original Extracted Source: original extracted web-security-wiki source/flask-vuln.md
Description:
FlaskFramework security vulnerabilities
Prerequisites:
- UseFlaskFramework
- Vulnerable configuration exists
Execution Outline:
1. 1. SSTITemplate injection
2. 2. SECRET_KEYUtilize
3. 3. Debug ModeRCE
4. 4. PINCode bypass
## WebLogic XMLDecoder
- ID: weblogic-xmldecoder
- Difficulty: intermediate
- Subcategory: WebLogic
- Tags: weblogic, xmldecoder, rce
- Original Extracted Source: original extracted web-security-wiki source/weblogic-xmldecoder.md
Description:
UtilizeWebLogic ServerInXMLDecoderDeserialization vulnerability(CVE-2017-10271/CVE-2017-3506)Achieve remote code execution
Prerequisites:
- Target executionWebLogic Server
- Existence/wls-wsat/Or/_async/Path
- XMLDecoderComponent was not disabled
- WebLogicVulnerabilities exist in versions(10.3.6.0/12.1.3.0Etc.)
Execution Outline:
1. DetectionWebLogicVersion and path
2. CVE-2017-10271 XMLDecoder RCE
3. CVE-2019-2725 DeserializationRCE
4. WriteWebshellObtain persistent permissions

