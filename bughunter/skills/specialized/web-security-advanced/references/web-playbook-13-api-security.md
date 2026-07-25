# APISecurity
English: API Security
- Entry Count: 12
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## JWTSecurity vulnerabilities
- ID: jwt-security
- Difficulty: intermediate
- Subcategory: JWT
- Tags: jwt, token, authentication
- Original Extracted Source: original extracted web-security-wiki source/jwt-security.md
Description:
JSON Web TokenExploitation of security vulnerabilities
Prerequisites:
- UseJWTConduct authentication
- JWTThere are issues with configuration or verification
Execution Outline:
1. 1. DecodeJWT
2. 2. NoneAlgorithmic attack
3. 3. Weak key cracking
4. 4. Key obscuring attacks
## GraphQLInjection attack
- ID: graphql-injection
- Difficulty: intermediate
- Subcategory: GraphQL
- Tags: graphql, api, injection, introspection
- Original Extracted Source: original extracted web-security-wiki source/graphql-injection.md
Description:
GraphQL APIInjection and information leakage attack
Prerequisites:
- Target usageGraphQL API
- Exists unauthorized access or injection points
Execution Outline:
1. 1. DetectionGraphQLEndpoints
2. 2. Introspection query
3. 3. Batch query attack
4. 4. SQLInjection
## GraphQLIntrospection attack
- ID: graphql-introspection
- Difficulty: beginner
- Subcategory: GraphQLIntrospection
- Tags: graphql, introspection, enumeration, api
- Original Extracted Source: original extracted web-security-wiki source/graphql-introspection.md
Description:
UtilizeGraphQLIntrospection function acquisitionAPIStructure
Prerequisites:
- Target usageGraphQL
- Introspection feature not disabled
Execution Outline:
1. 1. Basic Introspection
2. 2. Full Introspection
3. 3. Use tools to analyze
## GraphQLBatch query attack
- ID: graphql-batching
- Difficulty: intermediate
- Subcategory: GraphQLBatch query
- Tags: graphql, batching, rate-limit, bypass
- Original Extracted Source: original extracted web-security-wiki source/graphql-batching.md
Description:
UtilizeGraphQLBulk Query Rate Limit Bypass
Prerequisites:
- Target usageGraphQL
- Rate limiting exists
Execution Outline:
1. 1. Alias Batch Query
2. 2. Array Batch Query
3. 3. Brute force cracking
## REST APISecurity testing
- ID: rest-api-security
- Difficulty: intermediate
- Subcategory: REST API
- Tags: rest, api, security, testing
- Original Extracted Source: original extracted web-security-wiki source/rest-api-security.md
Description:
REST APISecurity Testing and Vulnerability Exploitation
Prerequisites:
- Target usageREST API
- UnderstandAPIEndpoints
Execution Outline:
1. 1. APIEndpoint discovery
2. 2. Authentication testing
3. 3. HTTPMethod testing
4. 4. Parameter pollution
## JWT NoneAlgorithmic attack
- ID: jwt-none-alg
- Difficulty: beginner
- Subcategory: JWTSecurity
- Tags: jwt, none, algorithm, bypass
- Original Extracted Source: original extracted web-security-wiki source/jwt-none-alg.md
Description:
UtilizeJWT NoneAlgorithm bypass signature verification
Prerequisites:
- Target usageJWTAuthentication
- The server did not properly validate the algorithm
Execution Outline:
1. 1. DecodeJWT
2. 2. Construct.NoneAlgorithmToken
3. 3. Modify user permissions
4. 4. Send maliciousToken
## JWTKey obscuring attacks
- ID: jwt-key-confusion
- Difficulty: intermediate
- Subcategory: JWTSecurity
- Tags: jwt, algorithm, confusion, rs256
- Original Extracted Source: original extracted web-security-wiki source/jwt-key-confusion.md
Description:
UtilizeJWTAlgorithm obfuscation to achieve signature bypass
Prerequisites:
- Target usageRS256Algorithm
- Obtainable public key
Execution Outline:
1. 1. Obtain public key
2. 2. Algorithm obfuscation attack
3. 3. Send maliciousToken
## IDORInsecure Direct Object Reference
- ID: api-idor
- Difficulty: beginner
- Subcategory: IDOR
- Tags: idor, api, authorization, bypass
- Original Extracted Source: original extracted web-security-wiki source/api-idor.md
Description:
UtilizeIDORVulnerability to access unauthorized resources
Prerequisites:
- Target usageIDReference resources
- the existence of authorization check defects
Execution Outline:
1. 1. IdentificationIDParameters
2. 2. Enumeration.ID
3. 3. Batch detection
4. 4. cross-user access
## APIRate limit bypass
- ID: api-rate-limit
- Difficulty: intermediate
- Subcategory: Rate limit
- Tags: api, rate-limit, bypass, brute-force
- Original Extracted Source: original extracted web-security-wiki source/api-rate-limit.md
Description:
BypassAPIRate Limiting for Brute Force Attacks
Prerequisites:
- Target has rate limiting
- Limit implementation defects
Execution Outline:
1. 1. Detect rate limiting
2. 2. IPBypass
3. 3. Distributed bypass
4. 4. Other bypass techniques
## Bulk assignment vulnerability
- ID: api-mass-assignment
- Difficulty: beginner
- Subcategory: Batch assignment
- Tags: api, mass-assignment, privilege-escalation
- Original Extracted Source: original extracted web-security-wiki source/api-mass-assignment.md
Description:
Exploit bulk assignment vulnerabilities to modify sensitive fields
Prerequisites:
- APIAcceptJSONInput.
- Unfiltered fields exist.
Execution Outline:
1. 1. Identify input fields
2. 2. Add sensitive fields
3. 3. Update Operation
4. 4. Nested objects
## BOLACompromise object-level authorization
- ID: api-bola
- Difficulty: intermediate
- Subcategory: BOLA
- Tags: api, bola, authorization, idor
- Original Extracted Source: original extracted web-security-wiki source/api-bola.md
Description:
UtilizeBOLAUnauthorized access to vulnerabilities
Prerequisites:
- APITarget objectID
- Authorization check flaws
Execution Outline:
1. 1. Identify object access
2. 2. Test authorization
3. 3. Horizontal access
4. 4. Modify/Delete operation
## APIInjection attack
- ID: api-injection
- Difficulty: intermediate
- Subcategory: APIInjection
- Tags: api, injection, sqli, nosqli
- Original Extracted Source: original extracted web-security-wiki source/api-injection.md
Description:
APIVarious injection attacks in endpoints
Prerequisites:
- APIAccept User Input
- Input not correctly filtered
Execution Outline:
1. 1. SQLInjection
2. 2. NoSQLInjection
3. 3. LDAPInjection
4. 4. Command injection

