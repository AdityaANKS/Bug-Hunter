<p align="center">
  <img src="docs/logo.png" alt="BugHunter Logo" width="400"/>
</p>

<h1 align="center">BugHunter</h1>

<p align="center">
  <b>Your AI-powered security research assistant that actually thinks like a pentester.</b><br/>
  <i>Point it at a target. Watch it hack. Get a report.</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12+-blue?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/LLM-NVIDIA%20GLM%205.2-76b900?logo=nvidia&logoColor=white" alt="NVIDIA"/>
  <img src="https://img.shields.io/badge/Kali-Sandbox-557C94?logo=kalilinux&logoColor=white" alt="Kali"/>
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License"/>
</p>

---

## 🤔 What is BugHunter?

BugHunter is an **autonomous AI pentesting agent** that doesn't just run scripts — it *reasons* about targets like a human security researcher would. Give it a domain, IP, or URL, and it will:

- 🔍 **Scan and enumerate** the target using 80+ real Kali Linux tools
- 🧠 **Think and adapt** — analyzing results and deciding what to test next
- 🛡️ **Find vulnerabilities** — from open ports to SQL injection to misconfigurations
- 📝 **Write professional reports** — detailed findings with evidence and remediation
- 🔄 **Keep going** — persistent mode runs overnight across multiple testing cycles

No copy-pasting commands. No switching between terminals. Just tell it what to do in plain English.

---

## ⚡ Quick Start

Get running in under 2 minutes:

```bash
# 1. Install BugHunter
pip install -e .

# 2. Set your API key (NVIDIA is the default provider)
#    Create a .env file or export the variable:
export BUGHUNTER_LLM_API_KEY=your-nvidia-api-key

# 3. Pick your interface:
bughunter repl          # Classic terminal — type commands, get results
bughunter tui           # Interactive workbench with slash commands
bughunter web           # Full Web UI at http://localhost:7788
```

Then just type something like:

```
Perform a full pentest against 192.168.1.100
```

BugHunter takes it from there — launching nmap, nikto, ffuf, sqlmap, and more inside its Kali sandbox, all automatically.

---

## 🎯 Three Ways to Use It

### 1. REPL — The Classic Terminal

```bash
bughunter repl
```

Type natural language or use built-in commands:

| Command | What it does |
|---------|-------------|
| `target 10.10.10.1` | Set your target |
| `sandbox start` | Fire up the Kali Linux sandbox |
| `sandbox nmap -sV 10.10.10.1` | Run nmap directly in Kali |
| `findings` | See all vulnerabilities found so far |
| `pool` | Show your AI model pool |
| `config` | View LLM provider settings |
| `report` | Generate a professional pentest report |
| `persistent` | Run overnight multi-cycle testing |
| `help` | See all commands |

### 2. TUI — The Interactive Workbench

```bash
bughunter tui
```

A full terminal UI with slash commands (`/target`, `/sandbox`, `/run`, `/findings`, `/pool`), mode selection (Quick / Standard / Deep / Continuous), and scope configuration — all without leaving the terminal.

### 3. Web UI — The Visual Dashboard

```bash
bughunter web
```

Opens at `http://localhost:7788` with a modern dark-themed dashboard featuring:
- Live scan console with real-time output
- Findings page with severity-colored results
- Sandbox terminal for direct Kali access
- Report generation and export
- Settings panel for LLM configuration

---

## 🐧 Kali Linux Sandbox

BugHunter ships with a **dedicated Kali Linux Docker container** packed with 80+ security tools. It starts automatically when you launch the REPL or run a task — no setup needed.

### What's Inside

| Category | Tools |
|----------|-------|
| **Scanning** | nmap, masscan, nikto, nuclei, wpscan, whatweb, wafw00f |
| **Enumeration** | ffuf, gobuster, amass, subfinder, dirb, dirsearch, enum4linux |
| **Exploitation** | sqlmap, metasploit, hydra, john, hashcat, searchsploit |
| **Network** | netcat, tcpdump, wireshark-cli, openvpn, proxychains, socat |
| **Web** | curl, wget, httpie, zaproxy |
| **Recon** | whois, dig, nslookup, theHarvester, recon-ng, dnsrecon |

### How It Works

The AI agent **automatically** decides which tools to use based on your target. You don't need to tell it to run nmap — it just does it. When nmap finds open ports, it automatically follows up with the right tools for those services.

```
You:    "Pentest scanme.nmap.org"
Agent:  → runs nmap -sV -sC -A
        → finds port 80 open (Apache)
        → runs nikto -h scanme.nmap.org
        → runs ffuf for directory enumeration
        → runs nuclei for CVE detection
        → compiles findings into a report
```

### Manual Sandbox Access

You can also run commands directly:

```bash
# In the REPL:
sandbox nmap -sV 10.10.10.1
sandbox sqlmap -u "http://target/page?id=1" --batch --dbs
sandbox msfconsole -q -x "search eternalblue; exit"

# In the TUI:
/sandbox nmap -A 10.10.10.1
/sandbox start
/sandbox stop
```

### Prerequisites

- **Docker Desktop** must be running
- Build the sandbox image once: `docker build -t bughunter-kali-sandbox:latest docker/kali-sandbox/`

---

## 🧠 How BugHunter Thinks

Unlike simple automation scripts, BugHunter uses a **Blackboard + OODA** (Observe-Orient-Decide-Act) reasoning architecture:

```
┌─────────────────────────────────────────┐
│            BLACKBOARD GRAPH             │
│  (shared knowledge base of all facts)   │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────┐   ┌──────────┐            │
│  │ Port 80  │──▶│ Apache   │──▶ ...     │
│  │ open     │   │ 2.4.52   │            │
│  └──────────┘   └──────────┘            │
│                                         │
│  ┌──────────┐   ┌──────────┐            │
│  │ Port 22  │──▶│ OpenSSH  │            │
│  │ open     │   │ 8.9      │            │
│  └──────────┘   └──────────┘            │
│                                         │
└─────────────────────────────────────────┘
         │
         ▼
   ┌───────────┐    ┌───────────┐    ┌───────────┐
   │  OBSERVE  │───▶│  ORIENT   │───▶│  DECIDE   │───▶ ACT
   │ Read the  │    │ Analyze   │    │ Pick next │    (Run tools)
   │ board     │    │ gaps      │    │ action    │
   └───────────┘    └───────────┘    └───────────┘
```

1. **OBSERVE** — Read the blackboard graph, check what's known
2. **ORIENT** — Identify gaps in knowledge, prioritize what to test
3. **DECIDE** — Choose the right tool and approach
4. **ACT** — Execute via Kali sandbox, verify results, write facts back

Every finding is **evidence-verified** — no hallucinated vulnerabilities. If a scan says "possible SQLi," the agent actually *tests* it with sqlmap before reporting.

---

## ⚙️ Configuration

### LLM Providers

BugHunter supports **15+ LLM providers** with automatic failover:

```bash
# Switch providers
bughunter config provider nvidia       # NVIDIA (default — uses GLM 5.2)
bughunter config provider openrouter   # OpenRouter (200+ models)
bughunter config provider openai       # OpenAI
bughunter config provider deepseek     # DeepSeek

# List all providers
bughunter config provider --list
```

### Environment Variables

Create a `.env` file in the project root:

```env
# Primary provider (NVIDIA)
BUGHUNTER_LLM_API_KEY=nvapi-xxxxxxxxxxxx
BUGHUNTER_LLM_BASE_URL=https://integrate.api.nvidia.com/v1
BUGHUNTER_LLM_MODEL=z-ai/glm-5.2

# Fallback provider (OpenRouter — optional but recommended)
OPENROUTER_API_KEY=sk-or-xxxxxxxxxxxx
OPENROUTER_API_KEY1=sk-or-yyyyyyyyyyyy   # 2-key rotation for rate limits
```

### Model Pool

BugHunter uses a **tiered model pool** for intelligent failover:

| Tier | Model | Role |
|------|-------|------|
| T1 | GLM 5.2 (NVIDIA) | Primary — handles all requests |
| T2 | DeepSeek V4 Pro | Secondary — first fallback |
| T3 | Kimi K2.6 | Secondary |
| T4 | MiniMax M3 | Secondary |
| T5 | Mistral Medium 3.5 | Fast tasks |
| T10+ | Nemotron / GPT-OSS / Laguna | Last-resort fallback |

After **3 consecutive failures**, the system automatically switches to the next tier.

### Sandbox Settings

```yaml
# In bughunter config:
safety:
  sandbox_auto_start: true    # Auto-start Kali container on launch
  enable_python_execute: true # Allow Python code execution
  tool_parallel: true         # Run independent tools concurrently
  tool_max_concurrent: 5      # Max parallel tool calls
```

---

## 🏗️ Project Structure

```
bughunter/
├── agent/           # AI agent core — reasoning, tools, prompts
│   ├── core.py         # AgentCore — the brain
│   ├── prompts.py      # System prompt builder
│   ├── builtin_tools.py # 20+ built-in security tools
│   └── context.py      # Session state management
├── cli/             # Command-line interfaces
│   ├── main.py         # REPL + CLI sub-commands
│   ├── tui.py          # TUI (prompt_toolkit backend)
│   └── tui_textual.py  # TUI (Textual backend)
├── web/             # Web UI
│   ├── app.py          # FastAPI backend
│   ├── frontend/       # React frontend
│   └── services/       # Sandbox, task orchestration
├── config/          # Configuration schema + settings
├── i18n/            # Translations (English + Chinese)
├── skills/          # 21 penetration testing skills
├── report/          # Report generator (Markdown/HTML)
├── mcp/             # MCP tool chain integration
└── orchestrator.py  # Task orchestration engine
```

---

**License:** MIT — use it, modify it, hack with it.
