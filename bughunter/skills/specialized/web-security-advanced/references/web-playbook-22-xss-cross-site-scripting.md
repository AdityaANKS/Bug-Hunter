# XSSCross-site scripting
English: XSS Cross-Site Scripting
- Entry Count: 12
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## ReflectedXSS
- ID: xss-reflected
- Difficulty: beginner
- Subcategory: Reflected
- Tags: xss, reflected, javascript
- Original Extracted Source: original extracted web-security-wiki source/xss-reflected.md
Description:
Reflected cross-site scripting attack technique
Prerequisites:
- User input reflected on the page exists
- Input not filtered or encoded
Execution Outline:
1. 1. DetectionXSSInjection point
2. 2. Event handler bypass
3. 3. Label bypass
4. 4. TheftCookie
## Storage TypeXSS
- ID: xss-stored
- Difficulty: intermediate
- Subcategory: Storage Type
- Tags: xss, stored, persistent
- Original Extracted Source: original extracted web-security-wiki source/xss-stored.md
Description:
Storage-based Cross-Site Scripting Attack Techniques
Prerequisites:
- Presence of Data Storage Function
- Stored data displayed without filtering
Execution Outline:
1. 1. Detect storage points
2. 2. CovertPayload
3. 3. Persistent control
4. 4. BeEF Hook
## DOMTypeXSS
- ID: xss-dom
- Difficulty: intermediate
- Subcategory: DOMType
- Tags: xss, dom, javascript
- Original Extracted Source: original extracted web-security-wiki source/xss-dom.md
Description:
Based onDOMCross-site scripting attacks
Prerequisites:
- ExistenceJavaScriptDynamic OperationDOM
- User Input Written DirectlyDOM
Execution Outline:
1. 1. DetectionDOM XSS
2. 2. CommonSinkPoint
3. 3. location.hashUtilize
4. 4. postMessageUtilize
## CSPBypass
- ID: xss-csp-bypass
- Difficulty: advanced
- Subcategory: CSPBypass
- Tags: xss, csp, bypass
- Original Extracted Source: original extracted web-security-wiki source/xss-csp-bypass.md
Description:
Bypass content security policy(CSP)'sXSSTechnology
Prerequisites:
- ExistenceXSSVulnerability
- ExistenceCSPPolicy but misconfigured
Execution Outline:
1. 1. AnalysisCSPPolicy
2. 2. Utilizeunsafe-inline
3. 3. Utilizeunsafe-eval
4. 4. JSONPBypass
## MutantXSS(mXSS)
- ID: xss-mxss
- Difficulty: advanced
- Subcategory: Mutant
- Tags: xss, mxss, mutation, bypass
- Original Extracted Source: original extracted web-security-wiki source/xss-mxss.md
Description:
Exploiting differences in browser parsing leads toXSSAttack
Prerequisites:
- ExistenceHTMLOutput points
- Browser parsing differences
Execution Outline:
1. 1. BasicsmXSSDetection
2. 2. SVG mXSS
3. 3. Math mXSS
4. 4. DOM clobberingCooperation
## Unicode XSS
- ID: xss-unicode
- Difficulty: intermediate
- Subcategory: UnicodeCode
- Tags: xss, unicode, encoding, bypass
- Original Extracted Source: original extracted web-security-wiki source/xss-unicode.md
Description:
UtilizeUnicodeEncoding feature bypass filtering
Prerequisites:
- ExistenceXSSInjection point
- Filter checks for keywords
Execution Outline:
1. 1. UnicodeEscape
2. 2. HTMLEntity encoding
3. 3. UnicodeNormalization attack
4. 4. UTF-7Code
## XSSFilter bypass
- ID: xss-filter-bypass
- Difficulty: intermediate
- Subcategory: Filter bypass
- Tags: xss, filter, bypass, waf
- Original Extracted Source: original extracted web-security-wiki source/xss-filter-bypass.md
Description:
Various BypassesXSSThe technology of filters
Prerequisites:
- ExistenceXSSInjection point
- Filtering Mechanism Exists
Execution Outline:
1. 1. Case mixing confusion
2. 2. Double write bypass
3. 3. Comment obfuscation
4. 4. Null byte truncation
## XSSEncoding bypass
- ID: xss-encoding
- Difficulty: intermediate
- Subcategory: Encoding bypass
- Tags: xss, encoding, bypass
- Original Extracted Source: original extracted web-security-wiki source/xss-encoding.md
Description:
Use various encoding techniques to bypassXSSFilter
Prerequisites:
- ExistenceXSSInjection point
- There is encoding processing
Execution Outline:
1. 1. URLCode
2. 2. HTMLEntity encoding
3. 3. JavaScriptCode
4. 4. CSSCode
## Polyglot XSS
- ID: xss-polyglot
- Difficulty: intermediate
- Subcategory: Polyglot
- Tags: xss, polyglot, universal
- Original Extracted Source: original extracted web-security-wiki source/xss-polyglot.md
Description:
Multi-environment general purposeXSS payload
Prerequisites:
- ExistenceXSSInjection point
- Uncertain specific environment
Execution Outline:
1. 1. ClassicPolyglot
2. 2. ShortPolyglot
3. 3. Attribute injectionPolyglot
4. 4. URLParametersPolyglot
## XSS CookieTheft
- ID: xss-cookie-theft
- Difficulty: beginner
- Subcategory: CookieTheft
- Tags: xss, cookie, theft, session
- Original Extracted Source: original extracted web-security-wiki source/xss-cookie-theft.md
Description:
UtilizeXSSStealing usersCookie
Prerequisites:
- ExistenceXSSVulnerability
- CookieNot setHttpOnly
Execution Outline:
1. 1. BasicsCookieTheft
2. 2. Fetch APITheft
3. 3. XMLHttpRequestTheft
4. 4. Encoding transmission
## XSSKeyboard logging
- ID: xss-keylogger
- Difficulty: intermediate
- Subcategory: Keyboard logging
- Tags: xss, keylogger, credential
- Original Extracted Source: original extracted web-security-wiki source/xss-keylogger.md
Description:
UtilizeXSSRecord User Keystrokes
Prerequisites:
- There is a storage-typeXSS
- The target page has sensitive input
Execution Outline:
1. 1. Basic keylogging
2. 2. Complete key logging
3. 3. Form stealing
4. 4. Form Submission Hijacking
## BeEFFramework Exploitation
- ID: xss-beef
- Difficulty: advanced
- Subcategory: BeEFUtilize
- Tags: xss, beef, framework, exploitation
- Original Extracted Source: original extracted web-security-wiki source/xss-beef.md
Description:
UseBeEFImplemented by the frameworkXSSUtilize
Prerequisites:
- ExistenceXSSVulnerability
- DeploymentBeEFServer
Execution Outline:
1. 1. DeploymentBeEF
2. 2. InjectionHookScript
3. 3. Common commands
4. 4. Module utilization

