# Prototype chain pollution
English: Prototype Pollution
- Entry Count: 3
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Server-side Prototype Chain Pollution toRCE
- ID: proto-server-rce
- Difficulty: advanced
- Subcategory: Server-side exploitation
- Tags: Prototype chain, Prototype Pollution, RCE, Node.js, __proto__
- Original Extracted Source: original extracted web-security-wiki source/proto-server-rce.md
Description:
Through contaminationJavaScriptObject prototype chain(__proto__/constructor.prototype)Inject malicious attributes, inNode.jsServer-side exploitationchild_processOrEJS/PugTemplate engines likegadgetChain to achieve remote code execution.
Prerequisites:
- Target usageNode.js
- ExistenceJSONMerge/Deep copy operation
- ControllableJSONInput.
Execution Outline:
1. 1. Detect prototype chain pollution points
2. 2. EJSTemplate engineRCE Gadget
3. 3. PugTemplate engineRCE Gadget
4. 4. GenericDoS/Information leakage.Gadget
## Client-side prototype chain pollution toXSS
- ID: proto-client-xss
- Difficulty: advanced
- Subcategory: Client exploitation
- Tags: Prototype chain, XSS, Client, jQuery, DOM, Prototype Pollution
- Original Extracted Source: original extracted web-security-wiki source/proto-client-xss.md
Description:
PassURLParameters、postMessageOrDOMOperation pollution in the front-endJavaScriptPrototype chain, utilizingjQuery/DOMOperation Library'sgadgetImplement on the client sideXSS. Attackers can use carefully craftedURLLink to induce victims to trigger vulnerabilities.
Prerequisites:
- Target frontend using vulnerableJSLibrary
- ExistenceURLLogic for converting parameters to objects
Execution Outline:
1. 1. Identify client pollution sources
2. 2. jQuery html() Gadget
3. 3. DOMPurifyBypassGadget
4. 4. Automated detection script
## Prototype Chain Pollution CombinationNoSQLInjection
- ID: proto-nosql-injection
- Difficulty: expert
- Subcategory: Combination utilization
- Tags: Prototype chain, NoSQL, MongoDB, Authentication bypass, Combination attack
- Original Extracted Source: original extracted web-security-wiki source/proto-nosql-injection.md
Description:
Prototype chain pollution and.MongoDB/NoSQLInjection of combined utilization. By contaminating the prototype chain attributes of the query object, bypassing authentication logic or constructing malicious query conditions, achieving authentication bypass and data leakage.
Prerequisites:
- Target usageMongoDB
- Prototype chain pollution points exist
- Query construction logic exists
Execution Outline:
1. 1. IdentificationMongoDBQuery injection points
2. 2. Prototype chain pollution bypass query validation
3. 3. Boolean blind injection to extract data
4. 4. Database enumeration and export

