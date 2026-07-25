# Cache andCDNSecurity
English: Cache & CDN Security
- Entry Count: 3
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Cache poisoning
- ID: cache-poisoning
- Difficulty: advanced
- Subcategory: Cache poisoning
- Tags: cache, poisoning, web-cache
- Original Extracted Source: original extracted web-security-wiki source/cache-poisoning.md
Description:
WebCache poisoning attack
Prerequisites:
- Target uses cache
- Improperly configured cache keys
Execution Outline:
1. Cache Detection
2. Untyped Header
3. Cache poisoning
4. Fat GET
## Cache deception
- ID: cache-deception
- Difficulty: intermediate
- Subcategory: Deception
- Tags: cache, deception, auth
- Original Extracted Source: original extracted web-security-wiki source/cache-deception.md
Description:
UtilizeWebDifferences in caching and server path resolution, inducingCDN/Cache layer caches dynamic pages containing sensitive information
Prerequisites:
- Target usageCDNOr reverse proxy cache
- Path resolution differences(Backend ignores path suffix)
- Cache strategy based onURLExtension
Execution Outline:
1. Probe Cache Behavior
2. Path obfuscation cache deception
3. Advanced cache deception variants
4. Complete attack process verification.
## CDNBypass
- ID: cdn-bypass
- Difficulty: intermediate
- Subcategory: CDN
- Tags: cdn, bypass, recon
- Original Extracted Source: original extracted web-security-wiki source/cdn-bypass.md
Description:
BypassCDNFind trueIP
Prerequisites:
- Target usageCDN
Execution Outline:
1. HistoryDNS
2. Email header
3. DNSHistory and certificate transparency query
4. Subdomain and related services probe the realIP

