---
name: recon
description: Information collection process — passive+active reconnaissance
---

# Information collection Skill

Perform passive and active information collection to build target profiles and attack surface maps.

## Execution steps

### 1. passive reconnaissance
- pass fetch Tool access target, collect HTTP response header
- Identify server type、Version、WAF
- analyze HTML Technology stack identification in source code

### 2. active reconnaissance
- Detection common Web port
- Enumerate directories and paths
- Check sensitive files (robots.txt, .env, .git)
- Discover API endpoint

### 3. Technology stack identification
- Front-end framework (React/Vue/Angular/jQuery)
- backend framework (Express/Django/Flask/Spring)
- CMS system(WordPress/Joomla/Customized)
- Database type

### 4. output
- target image (IP/domain name/port/Serve/technology stack)
- Attack surface map (accessible paths、API、Management entrance)
