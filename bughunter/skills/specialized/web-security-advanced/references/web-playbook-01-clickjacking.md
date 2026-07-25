# Clickjacking
English: Clickjacking
- Entry Count: 2
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Basic clickjacking
- ID: clickjacking-basic
- Difficulty: beginner
- Subcategory: Basics
- Tags: clickjacking, ui-redressing, iframe
- Original Extracted Source: original extracted web-security-wiki source/clickjacking-basic.md
Description:
Through transparencyiframeCovering prompts that entice users to click hidden malicious buttons or links without their knowledge
Prerequisites:
- The target site allows beingiframeNested
- Target not setX-Frame-OptionsResponse headers
- Target not configuredCSP frame-ancestorsPolicy
- HTML/CSSBasics
Execution Outline:
1. DetectionX-Frame-OptionsandCSP
2. Basic TransparencyiframeOverwritePOC
3. Multi-step drag-and-drop hijacking(Drag-and-Drop)
4. UtilizeCSS pointer-eventsBypass
## Clickjacking+XSS
- ID: clickjacking-xss
- Difficulty: intermediate
- Subcategory: XSS
- Tags: clickjacking, xss
- Original Extracted Source: original extracted web-security-wiki source/clickjacking-xss.md
Description:
Clickjacking andXSSAttack combination, first triggered by click hijackingXSSAttack Vector for Deeper Control
Prerequisites:
- Target existsXSSVulnerability
- Target allowed to beiframeNested
- XSS payloadClickable trigger
Execution Outline:
1. Identify exploitableXSSandClickjackingCombination
2. Self-XSS + ClickjackingCombination utilization
3. ReflectedXSS + iframeNested exploitation

