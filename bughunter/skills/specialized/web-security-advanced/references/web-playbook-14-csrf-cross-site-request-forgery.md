# CSRFCross-site request forgery
English: CSRF Cross-Site Request Forgery
- Entry Count: 8
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## CSRFBasic Attack
- ID: csrf-basic
- Difficulty: beginner
- Subcategory: Basic Attack
- Tags: csrf, cross-site, request, forgery
- Original Extracted Source: original extracted web-security-wiki source/csrf-basic.md
Description:
Cross-site request forgery basic attack techniques
Prerequisites:
- Target has sensitive operations
- Missing.CSRFProtect
Execution Outline:
1. 1. Construct.CSRFForm
2. 2. GETRequestCSRF
3. 3. JSON CSRF
4. 4. Link inducement.
## JSON CSRFAttack
- ID: csrf-json
- Difficulty: intermediate
- Subcategory: JSON CSRF
- Tags: csrf, json, api, post
- Original Extracted Source: original extracted web-security-wiki source/csrf-json.md
Description:
TargetingJSONRequest'sCSRFAttack techniques
Prerequisites:
- Target usageJSONFormat Requests
- Missing.CSRFProtect
- CORSMisconfiguration
Execution Outline:
1. 1. SimpleJSON CSRF
2. 2. Flash JSON CSRF
3. 3. XSSIAttack
4. 4. SWFFile attack
## CSRFBypass techniques
- ID: csrf-bypass
- Difficulty: intermediate
- Subcategory: Bypass techniques
- Tags: csrf, bypass, token, referer
- Original Extracted Source: original extracted web-security-wiki source/csrf-bypass.md
Description:
BypassCSRFVarious protection technologies
Prerequisites:
- Target existsCSRFProtection
- Protection mechanisms have vulnerabilities
Execution Outline:
1. 1. TokenVerification bypass
2. 2. RefererVerification bypass
3. 3. OriginVerification bypass
4. 4. SameSiteBypass
## SameSiteBypass techniques
- ID: csrf-samesite
- Difficulty: intermediate
- Subcategory: SameSiteBypass
- Tags: csrf, samesite, cookie, bypass
- Original Extracted Source: original extracted web-security-wiki source/csrf-samesite.md
Description:
BypassSameSite CookieAttribute'sCSRFAttack
Prerequisites:
- CookieSetSameSiteAttribute
- SameSiteConfiguration is flawed
Execution Outline:
1. 1. SameSite=LaxBypass
2. 2. SameSite=StrictBypass
3. 3. Not setSameSite
4. 4. UtilizeOAuthProcess.
## TokenBypass techniques
- ID: csrf-token-bypass
- Difficulty: intermediate
- Subcategory: TokenBypass
- Tags: csrf, token, bypass, predictable
- Original Extracted Source: original extracted web-security-wiki source/csrf-token-bypass.md
Description:
BypassCSRF TokenVerified techniques
Prerequisites:
- Target usageCSRF Token
- TokenThe mechanism has defects
Execution Outline:
1. 1. TokenPredictable
2. 2. TokenUnbound sessions
3. 3. TokenDisclosure
4. 4. TokenReplay
## RefererBypass techniques
- ID: csrf-referer-bypass
- Difficulty: intermediate
- Subcategory: RefererBypass
- Tags: csrf, referer, bypass, header
- Original Extracted Source: original extracted web-security-wiki source/csrf-referer-bypass.md
Description:
BypassRefererVerifiedCSRFAttack
Prerequisites:
- Target verificationRefererHeader
- Defective Logic Validation
Execution Outline:
1. 1. regex match bypass
2. 2. EmptyRefererBypass
3. 3. Subdomain bypass
4. 4. Referrer-PolicyUtilize
## Flash CSRFAttack
- ID: csrf-flash
- Difficulty: advanced
- Subcategory: Flash CSRF
- Tags: csrf, flash, swf, crossdomain
- Original Extracted Source: original extracted web-security-wiki source/csrf-flash.md
Description:
UtilizeFlashConductCSRFAttack
Prerequisites:
- Target allowsFlashRequest
- crossdomain.xmlMisconfiguration
Execution Outline:
1. 1. crossdomain.xmlUtilize
2. 2. Create maliciousSWF
3. 3. SendJSONRequest
4. 4. CustomHeader
## CORSConfiguration error exploitation
- ID: csrf-cors
- Difficulty: intermediate
- Subcategory: CORSConfiguration error
- Tags: csrf, cors, misconfiguration, api
- Original Extracted Source: original extracted web-security-wiki source/csrf-cors.md
Description:
UtilizeCORSMisconfiguration occurredCSRFAttack
Prerequisites:
- CORSConfiguration error
- Allowing credentials to be carried across domains
Execution Outline:
1. 1. DetectionCORSConfiguration
2. 2. ReflectionOriginAttack
3. 3. nullSource attack
4. 4. Regex bypass

