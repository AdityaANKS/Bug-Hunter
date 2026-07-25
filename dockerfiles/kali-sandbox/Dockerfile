FROM kalilinux/kali-rolling:latest

# =============================================================================
# Bug Hunter – Kali Linux Sandbox
# Comprehensive bug bounty & penetration testing toolkit
# =============================================================================
#
# Tool count: 80+ packages across 10 categories
# Estimated image size: ~3-4 GB (with Metasploit + wordlists)
#
# Each category is a separate Docker layer for efficient caching.
# If you add/remove a tool in one layer, Docker re-uses cached layers above.
# =============================================================================

# ── Layer 1: System Essentials & SSH ─────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server \
    ca-certificates \
    curl \
    wget \
    git \
    jq \
    tree \
    vim \
    tmux \
    net-tools \
    iputils-ping \
    locales \
    python3 \
    python3-pip \
    python3-venv \
    ruby \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ── Layer 2: Reconnaissance & OSINT ─────────────────────────────────────────
# Subdomain discovery, DNS enum, email harvest, asset mapping
RUN apt-get update && apt-get install -y --no-install-recommends \
    amass \
    subfinder \
    assetfinder \
    theharvester \
    recon-ng \
    spiderfoot \
    dnsenum \
    dnsrecon \
    dnsutils \
    fierce \
    sublist3r \
    massdns \
    whois \
    enum4linux \
    httprobe \
    gospider \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ── Layer 3: Web Application Testing ────────────────────────────────────────
# Vuln scanning, SQL/XSS/cmd injection, CMS scanning, param discovery
RUN apt-get update && apt-get install -y --no-install-recommends \
    nikto \
    sqlmap \
    wpscan \
    commix \
    xsser \
    whatweb \
    wafw00f \
    arjun \
    httpx-toolkit \
    nuclei \
    wapiti \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ── Layer 4: Brute Force & Password Attacks ─────────────────────────────────
# Online/offline cracking, hash attacks, wordlist generation
RUN apt-get update && apt-get install -y --no-install-recommends \
    hydra \
    john \
    hashcat \
    medusa \
    ncrack \
    cewl \
    crunch \
    hash-identifier \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ── Layer 5: Network & Port Scanning ────────────────────────────────────────
# Port scanning, packet capture, traffic analysis, network discovery, VPN
RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap \
    masscan \
    netcat-openbsd \
    tcpdump \
    wireshark-common \
    tshark \
    arp-scan \
    hping3 \
    traceroute \
    openvpn \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ── Layer 6: Exploitation Frameworks ────────────────────────────────────────
# This is the largest layer (~800 MB for Metasploit alone)
RUN apt-get update && apt-get install -y --no-install-recommends \
    metasploit-framework \
    exploitdb \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ── Layer 7: Web Fuzzing & Proxying ─────────────────────────────────────────
# Directory/file brute-forcing, HTTP proxying, content discovery
RUN apt-get update && apt-get install -y --no-install-recommends \
    gobuster \
    ffuf \
    feroxbuster \
    dirb \
    wfuzz \
    mitmproxy \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ── Layer 8: SSL/TLS & Crypto ───────────────────────────────────────────────
# Certificate analysis, cipher suite auditing, TLS configuration testing
RUN apt-get update && apt-get install -y --no-install-recommends \
    sslscan \
    sslyze \
    testssl.sh \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ── Layer 9: Mobile & Reverse Engineering ───────────────────────────────────
# APK decompilation, binary analysis, firmware extraction
RUN apt-get update && apt-get install -y --no-install-recommends \
    apktool \
    dex2jar \
    jadx \
    radare2 \
    binwalk \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ── Layer 10: Post-Exploitation & Pivoting ──────────────────────────────────
# Tunneling, lateral movement, SMB/WinRM attacks, AD exploitation
RUN apt-get update && apt-get install -y --no-install-recommends \
    socat \
    proxychains4 \
    chisel \
    responder \
    impacket-scripts \
    evil-winrm \
    netexec \
    smbclient \
    smbmap \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ── Layer 11: Wordlists ────────────────────────────────────────────────────
# SecLists (~500 MB) + Kali default wordlists
RUN apt-get update && apt-get install -y --no-install-recommends \
    seclists \
    wordlists \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ── Layer 12: Go-based Bug Bounty Tools (0xHunterTools) ─────────────────────
# Tools from the bug bounty community not available via Kali apt repos.
# Requires golang to be installed first.
RUN apt-get update && apt-get install -y --no-install-recommends golang \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV GOPATH=/opt/go
ENV PATH="${GOPATH}/bin:/usr/local/go/bin:${PATH}"

RUN go install github.com/projectdiscovery/katana/cmd/katana@latest ; \
    go install github.com/lc/gau/v2/cmd/gau@latest ; \
    go install github.com/hahwul/dalfox/v2@latest ; \
    go install github.com/tomnomnom/waybackurls@latest ; \
    go install github.com/tomnomnom/qsreplace@latest ; \
    go install github.com/tomnomnom/unfurl@latest ; \
    go install github.com/tomnomnom/anew@latest ; \
    go install github.com/tomnomnom/gf@latest ; \
    go install github.com/hakluke/hakrawler@latest ; \
    go install github.com/edoardottt/cariddi/cmd/cariddi@latest ; \
    go install github.com/sensepost/gowitness@latest ; \
    go install github.com/dwisiswant0/cf-check@latest ; \
    rm -rf /opt/go/pkg /root/.cache/go-build

# Symlink Go binaries into /usr/local/bin for all users
RUN ln -sf /opt/go/bin/* /usr/local/bin/ 2>/dev/null || true

# ── Layer 13: Pip & Git Bug Bounty Tools ────────────────────────────────────
# Python/git-based tools from the bug bounty ecosystem
RUN pip3 install --no-cache-dir --break-system-packages \
    paramspider \
    uro \
    && git clone --depth 1 https://github.com/m4ll0k/SecretFinder.git /opt/SecretFinder \
    && pip3 install --no-cache-dir --break-system-packages -r /opt/SecretFinder/requirements.txt 2>/dev/null || true \
    && git clone --depth 1 https://github.com/GerbenJavado/LinkFinder.git /opt/LinkFinder \
    && pip3 install --no-cache-dir --break-system-packages -r /opt/LinkFinder/requirements.txt 2>/dev/null || true \
    && git clone --depth 1 https://github.com/devanshbatham/paramspider /opt/paramspider 2>/dev/null || true

# ── Final cleanup: strip docs, man pages, locale data ──────────────────────
RUN rm -rf /usr/share/doc/* \
           /usr/share/man/* \
           /usr/share/info/* \
           /var/cache/* \
           /var/log/* \
    && mkdir -p /var/log

# ── SSH configuration ──────────────────────────────────────────────────────
RUN mkdir -p /run/sshd \
    && sed -i 's/#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config \
    && sed -i 's/#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config

# ── Non-root user (least privilege) ────────────────────────────────────────
RUN useradd -ms /bin/bash agentuser \
    && echo "agentuser:bughunter_sandbox_2024" | chpasswd

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
