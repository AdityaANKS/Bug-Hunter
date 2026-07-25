# Tool Usage Guide — Bug Hunter Agent

> Reference guide for choosing and chaining security tools effectively.
> Load via: `load_skill_reference("pentest-tools", "tool-guide.md")`

## Tool Selection Matrix

Use this table to pick the right tool for each task:

| Task | First Choice | Fallback | When to Use |
|------|-------------|----------|-------------|
| **Known CVEs/Misconfigs** | `nuclei_scan` | `kali_sandbox_execute` (nikto) | Always run early — catches low-hanging fruit |
| **SQL Injection** | `sqlmap_scan` | `python_execute` (manual) | When you find a parameter that reflects DB errors |
| **XSS Testing** | `xss_scan` (Dalfox) | `python_execute` (manual payloads) | When you find reflected/stored user input |
| **Directory/File Discovery** | `ffuf_fuzz` | `dir_enum` (built-in) | Use ffuf for advanced filtering, dir_enum for quick scans |
| **URL/Endpoint Collection** | `crawl_urls` + `js_recon` | `kali_sandbox_execute` (gospider) | Always run during recon before testing |
| **Hidden Parameters** | `param_discover` (Arjun) | `ffuf_fuzz` (param fuzzing) | When endpoints accept unknown params |
| **Live Host Probing** | `httpx_probe` | `kali_sandbox_execute` (httprobe) | After subdomain enumeration |
| **WordPress Sites** | `wpscan_scan` | `nuclei_scan` (wp templates) | When target is WordPress |
| **Port Scanning** | `nmap_scan` | `kali_sandbox_execute` (masscan) | Use masscan for speed, nmap for accuracy |
| **Subdomain Discovery** | `subdomain_enum` | `kali_sandbox_execute` (amass) | Use built-in first, amass for deeper results |
| **Brute Force** | `brute_force_login` | `kali_sandbox_execute` (hydra) | Built-in handles CSRF; hydra for non-web |
| **SSL/TLS Analysis** | `kali_sandbox_execute` (testssl.sh) | sslscan, sslyze | Always check TLS configuration |

## Recommended Workflow Chains

### 1. Full Reconnaissance Pipeline
```
subdomain_enum → httpx_probe → crawl_urls → js_recon → nuclei_scan
```
1. `subdomain_enum(domain="target.com")` — Discover subdomains
2. `httpx_probe(targets=[...subdomains...])` — Filter to live hosts
3. `crawl_urls(target=live_host, include_wayback=true)` — Collect all URLs
4. `js_recon(url=live_host)` — Extract JS endpoints and secrets
5. `nuclei_scan(target=live_host)` — Scan for known vulns

### 2. Web Application Attack Pipeline
```
crawl_urls → param_discover → xss_scan / sqlmap_scan → nuclei_scan
```
1. `crawl_urls(target="https://app.target.com")` — Discover pages
2. `param_discover(url=interesting_endpoint)` — Find hidden params
3. `xss_scan(url=endpoint_with_params)` — Test for XSS
4. `sqlmap_scan(url=endpoint_with_params)` — Test for SQLi
5. `nuclei_scan(target="https://app.target.com", tags="rce,ssrf,lfi")` — Check for more

### 3. Directory & Content Discovery Pipeline
```
ffuf_fuzz → nuclei_scan (exposed-panels) → unauth_test
```
1. `ffuf_fuzz(url="https://target.com/FUZZ", wordlist="big")` — Find hidden dirs
2. `nuclei_scan(target="https://target.com", templates="exposed-panels")` — Find admin panels
3. `unauth_test(base_url="https://target.com", endpoints=[...discovered...])` — Check auth

### 4. WordPress Attack Pipeline
```
wpscan_scan → nuclei_scan → ffuf_fuzz
```
1. `wpscan_scan(url="https://wp-site.com", enumerate="u,ap,at")` — Full WP enum
2. `nuclei_scan(target="https://wp-site.com", tags="wordpress")` — WP-specific vulns
3. `ffuf_fuzz(url="https://wp-site.com/FUZZ", wordlist="common")` — Find backup files

## Piping Patterns (Kali Sandbox)

For advanced workflows, chain tools in the sandbox:

```bash
# Subdomain → probe → crawl → nuclei
subfinder -d target.com -silent | httpx-toolkit -silent | katana -silent | nuclei -silent

# Collect URLs → test for XSS
echo "https://target.com" | katana -silent | kxss | dalfox pipe

# Find params from archives → test
echo "target.com" | gau --subs | qsreplace "FUZZ" | ffuf -w - -u FUZZ -mc 200

# Secret scanning in JS files
echo "https://target.com" | katana -jc -silent | grep "\.js$" | while read url; do
  python3 /opt/SecretFinder/SecretFinder.py -i "$url" -o cli
done

# Wayback URL collection → filter interesting
echo "target.com" | gau | unfurl -u keys | sort -u
```

## Tool-Specific Tips

### Nuclei
- Update templates first: `nuclei -ut` in sandbox
- Use `-severity critical,high` for quick wins
- Tag filtering is powerful: `-tags cve,rce,sqli,xss,ssrf,lfi`

### SQLMap
- Always use `--batch` (non-interactive)
- Start with `--level 1 --risk 1`, increase if no results
- For WAF bypass: `--tamper space2comment,between,randomcase`
- Specify `--dbms` if you know the backend to speed up detection

### Ffuf
- Always use `-ac` (auto-calibration) to filter noise
- For vhost discovery: `-H "Host: FUZZ.target.com"`
- Combine `-fc` (filter code) and `-fs` (filter size) for precision

### Dalfox (XSS)
- Pipe from parameter discovery: `cat params.txt | dalfox pipe`
- Use `--blind` with your OOB server for blind XSS
- Check DOM-based XSS with `-X POST` for form inputs

### Katana (Crawler)
- Use `-jc` flag for JavaScript crawling (finds more but slower)
- Depth 3 is usually sufficient; increase for complex apps
- Scope with `-fs=sdn` to stay on same domain
