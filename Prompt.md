<aside>
🎯

**Vision:** A personal, multi-agent security research assistant that hunts for bugs, vulnerabilities, and data-exposure risks — then produces full, proof-backed reports for responsible disclosure through Google Bug Hunters, Google's official Vulnerability Reward Program (VRP).

</aside>

## What it is

Bug Hunter is personal software that orchestrates **multiple AI agents working simultaneously** to discover even small bugs that could seriously impact a company — data leaks, security vulnerabilities, privacy exposures, and similar issues that can be worth a great deal to fix.

The goal: find a real, high-impact issue, document it with airtight proof, and report it to the company through their official channel — ideally earning a bug bounty or job offer.

## How it works (current concept)

- **Multi-agent swarm** — several AI agents run in parallel, each researching from different angles and sources.
- **Deep single-target focus** — given just one link or app, it drills progressively deeper into how that software actually works.
- **Multi-source research** — pulls and cross-checks information across many sources rather than relying on one.
- **Surface probing** — tests entry points and weak spots that could affect the company's critical paths.
- **Persistent memory** — remembers previous research, logs, and the current codebase, then connects everything together into a coherent picture.
- **Evidence capture** — explains every finding with proof: screenshots, code/error output, logs, exposed data, and supporting detail.
- **Responsible reporting** — once a confirmed bug is found, contact the company and report it through their disclosure / bounty program.

## Architecture: how the agents access data

The biggest open question is *how* the AI actually reaches an app's data. There are four layers, from most human-like to most powerful for bug hunting — a strong setup combines them:

### 1. Computer-use (mouse + keyboard control)

- The AI sees the screen via screenshots and controls the mouse/keyboard inside a sandboxed VM (e.g. Claude Computer Use, OpenAI's computer-using agent, open-source `browser-use`).
- **Best for:** visual proof screenshots, apps that block automation, replicating a real user flow.
- **Weak for:** speed and reliability — brittle and overkill for most web bugs.

### 2. Browser automation (headless browser)

- The AI drives a real browser programmatically (Playwright / Puppeteer / Selenium): load pages, click, read the full DOM, capture network requests, take screenshots.
- Faster and more reliable than pixel-level mouse control — the default for navigating an app.

### 3. HTTP / network layer — where most bugs live ⭐

- Most web vulnerabilities are found by inspecting and **modifying raw HTTP requests/responses**, not by clicking.
- Use an intercepting proxy: **Burp Suite**, **OWASP ZAP**, or **mitmproxy**. The AI reads intercepted traffic, tampers with parameters, replays requests, and inspects responses, headers, and tokens.

### 4. Recon + API layer — finding the data we're missing

The important, easily-missed data lives in places humans don't look:

- JavaScript source files (often leak API endpoints, keys, hidden parameters)
- API responses and undocumented endpoints
- Cookies, auth tokens, response headers
- Subdomains, sitemaps, and crawled links

Tooling like `ffuf`, `nuclei`, subdomain enumeration, and JS analysis surfaces these; the AI orchestrates them and reads the output.

### Recommended setup

<aside>
🧰

Run the agents inside a **sandboxed environment (VM or container)** with a **headless browser + intercepting proxy**, and have them work primarily at the network / JS / API layer. Add **computer-use (mouse/keyboard)** only as an extra for screenshots and automation-resistant apps. You do **not** strictly need to hand over mouse/keyboard control for most web testing.

</aside>

<aside>
🚫

Whatever access the environment is given, the agents must **only ever operate against your own accounts and test targets** — never real users' data. This is both a Google VRP rule and the line between research and abuse.

</aside>

## Future roadmap

- **Agents that question each other** — multiple agents debate and challenge each other's findings in a loop until they converge on a verified answer.
- **Live web research** — browse the web and gather data from trusted providers to validate and enrich findings.
- **Automated evidence collection** — take screenshots, capture the specific code related to a bug, and collect relevant logs, errors, and confidential-data exposure.
- **Auto-generated proof documentation** — build a complete proof doc on a documentation platform, writing every detail with the connected images and evidence for each bug.
- **Time-stamped evidence trail** — every piece of data and its source is recorded and timestamped.
- **Fix recommendations** — propose a solution for each bug and include it in the documentation.
- **System understanding** — develop a working model of how the company and its website/app actually operate, to find deeper and more meaningful issues.

## Deliverable: the proof report

Each finding produces a full, structured report containing:

- [ ]  Clear description of the bug and its impact
- [ ]  Affected target (link / app / endpoint)
- [ ]  Step-by-step reproduction
- [ ]  Proof: screenshots, code, errors, logs, exposed data
- [ ]  Severity / potential business impact
- [ ]  Recommended fix / solution
- [ ]  Timeline with timestamps for every piece of evidence

## 🎯 Tailored for Google Bug Hunters (VRP)

Bug Hunter is pointed at Google's Vulnerability Reward Program — an official, authorized program for external researchers. A few program specifics should shape how the tool behaves:

### Which program to report under

Reports are filed through one portal, but you pick the right sub-program / bug location:

- **Google & Alphabet VRP** — general Google web apps and services.
- **Chrome VRP** — Chrome / Chromium (top rewards have reached **$250,000** for a sandbox escape).
- **Android & Google Devices** — mobile OS and hardware.
- **Cloud VRP** — Google Cloud products (top award **$101,010**).
- **AI VRP** — AI products like Gemini (base rewards up to **$30,000**); note many model misbehavior / incorrect-output cases are **out of scope** unless there's a real attack path.
- **Abuse VRP** — product abuse / logic flaws.

### Key program rules that change how Bug Hunter must operate

<aside>
🚫

**Only ever target your own accounts.** Google's rules explicitly prohibit accessing anyone else's data or doing anything disruptive or damaging to other users or to Google. Bug Hunter must demonstrate impact using *your own* test accounts only — never by snooping real user/confidential data.

</aside>

- **A valid attack scenario is required.** A bug with no realistic exploitation path won't qualify; reward is based on maximum demonstrated impact.
- **Be succinct.** Triage engineers prefer a short, working proof-of-concept link over a long video or write-up. Optimize Bug Hunter's report output for a tight repro, not volume.
- **Include repro essentials** — version numbers, OS, and (for Chrome) a bisection where possible.
- **Encrypted comms available** — Google offers a PGP key for sensitive reports; you get a tracking ID on submission.

### Useful resources

- Report portal: `bughunters.google.com/report`
- Bug Hunter University / Learn (writing good reports)
- Public VRP write-ups (community) for calibrating what qualifies

## ⚠️ Responsible use & scope

<aside>
🛡️

This only works as a legitimate, valuable tool if it stays inside the lines of authorized security research.

</aside>

- **Only test what you're allowed to test.** Stay within the scope of an official bug bounty program (e.g. HackerOne, Bugcrowd) or explicit written permission from the target.
- **Follow responsible disclosure.** Report privately to the company first; don't publish, sell, or exploit findings.
- **Handle exposed data carefully.** Don't exfiltrate, store, or share real confidential/personal data beyond the minimum needed to prove the issue, and delete it after.
- **Respect program rules.** Avoid actions that disrupt service, and honor each program's rules of engagement.

Unauthorized probing, accessing systems without permission, or extracting confidential data outside a sanctioned program can be illegal — keeping Bug Hunter pointed only at authorized targets is what makes it a career asset instead of a liability.

## Next steps

1. Pick the first authorized target (a public bug bounty program is a safe start).
2. Define the agent roles (researcher, prober, verifier, evidence collector, reporter).
3. Build the shared memory store for logs, code, and past findings.
4. Design the proof-report template.
5. Run a small end-to-end test on a single in-scope target.

## How to use nvidia api key 

import requests

invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
stream = False

headers = {
  "Authorization": "Bearer $NVIDIA_API_KEY",
  "Accept": "text/event-stream" if stream else "application/json"
}

payload = {
  "model": "minimaxai/minimax-m3",
  "messages": [{"role":"user","content":""}],
  "max_tokens": 8192,
  "temperature": 1.00,
  "top_p": 0.95,
  "stream": stream,
  
}

# MiniMax-M3 is multimodal. To send images or video, set a message's
# "content" to a list of parts (a public URL or a base64 data URI):
#   payload["messages"] = [{"role": "user", "content": [
#       {"type": "text", "text": "Describe this."},
#       {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}},
#       {"type": "video_url", "video_url": {"url": "https://example.com/video.mp4"}},
#   ]}]
# To use base64 instead of a URL:
#   import base64
#   b64 = base64.b64encode(open("image.png", "rb").read()).decode()
#   {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}

response = requests.post(invoke_url, headers=headers, json=payload, stream=stream)
if stream:
    for line in response.iter_lines():
        if line:
            print(line.decode("utf-8"))
else:
    print(response.json())

# How to use Playwright Use what is best for the task
# Playwright CLI
Token-efficient browser automation for coding agents like Claude Code and GitHub Copilot. Skill-based workflows without large context overhead.

npm i -g @playwright/cli@latest

# Playwright MCP
Model Context Protocol server that gives AI agents full browser control through structured accessibility snapshots.

npx @playwright/mcp@latest

# How to use mitmproxy
from mitmproxy import http

def request(flow: http.HTTPFlow):
    # redirect to different host
    if flow.request.pretty_host == "example.com":
        flow.request.host = "mitmproxy.org"
    # answer from proxy
    elif flow.request.path.endswith("/brew"):
    	flow.response = http.Response.make(
            418, b"I'm a teapot",
        )