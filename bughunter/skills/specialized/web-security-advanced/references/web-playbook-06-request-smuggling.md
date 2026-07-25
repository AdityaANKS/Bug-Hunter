# Request smuggling
English: Request Smuggling
- Entry Count: 4
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## CL-TERequest smuggling
- ID: smuggling-cl-te
- Difficulty: advanced
- Subcategory: CL-TE
- Tags: smuggling, request, http
- Original Extracted Source: original extracted web-security-wiki source/smuggling-cl-te.md
Description:
Content-LengthWithTransfer-EncodingSmuggling
Prerequisites:
- The target uses a multi-layer proxy
- Front-end and back-end processing differences
Execution Outline:
1. CL-TEBasics
2. TE-CLBasics
3. TE-TE
## CL-CLSmuggling
- ID: smuggling-cl-cl
- Difficulty: advanced
- Subcategory: CL-CL
- Tags: smuggling, cl-cl, http
- Original Extracted Source: original extracted web-security-wiki source/smuggling-cl-cl.md
Description:
Use front-end proxy and back-end server to handle simultaneouslyContent-LengthHeaders but for multipleCLDifferences in header processing implementationHTTPRequest smuggling
Prerequisites:
- Presence of Front-End Proxy(Such asHAProxy/Nginx)+Backend server architecture
- Both ends matchContent-LengthThere are differences in header parsing
- UnderstandingHTTPRequest smuggling principles
Execution Outline:
1. DetectionCL-CLSmuggling conditions
2. CL-CLRequest smugglingPOC
3. UtilizeCL-CLSmuggling bypassing front-end access controls
## TE-CLSmuggling
- ID: smuggling-te-cl
- Difficulty: expert
- Subcategory: TE-CL
- Tags: smuggling, te-cl, http
- Original Extracted Source: original extracted web-security-wiki source/smuggling-te-cl.md
Description:
Exploit using the frontendTransfer-EncodingWhile the backend usesContent-LengthAchieved through differencesHTTPRequest smuggling
Prerequisites:
- Front-end proxy prioritizationTransfer-Encoding
- Backend servers prioritize processingContent-Length
- UnderstandingchunkedEncoding format
Execution Outline:
1. DetectionTE-CLDifferences
2. TE-CLSmugglingPOC
3. TE-CLSmuggling implementation request hijacking
## TE-TESmuggling
- ID: smuggling-te-te
- Difficulty: expert
- Subcategory: TE-TE
- Tags: smuggling, te-te, http
- Original Extracted Source: original extracted web-security-wiki source/smuggling-te-te.md
Description:
Leveraging Frontend and Backend PairsTransfer-EncodingDifferences in handling various obfuscation variants of the head achieve request smuggling
Prerequisites:
- Supported by both front-end and back-endTransfer-Encoding
- Can be accessed throughTEHeader obfuscation leads one end to ignoreTE
- UnderstandchunkedEncoding andHTTPSmuggling principle
Execution Outline:
1. TEObfuscation variant detection
2. TE-TESmuggling exploitation(Frontend ignores obfuscationTE)
3. TE-TECache poisoning attack

