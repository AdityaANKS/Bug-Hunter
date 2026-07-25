# Build the Bug Hunter Kali sandbox Docker image
param(
    [switch]$NoCache
)

$buildArgs = @("build", "-t", "bughunter-kali-sandbox:latest", "--progress=plain")

if ($NoCache) {
    $buildArgs += "--no-cache"
    Write-Host "Building with --no-cache (full rebuild)..." -ForegroundColor Yellow
}

$buildArgs += "$PSScriptRoot"

Write-Host "Building bughunter-kali-sandbox image..." -ForegroundColor Cyan
Write-Host "This may take 15-30 minutes on first build (downloading 80+ tools)." -ForegroundColor DarkGray
Write-Host ""

& docker @buildArgs

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Image built successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "── Image Details ──" -ForegroundColor Cyan
    docker images bughunter-kali-sandbox:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"
    Write-Host ""
    Write-Host "── Quick Smoke Test ──" -ForegroundColor Cyan
    docker run --rm bughunter-kali-sandbox:latest bash -c "echo 'Tools available:' && which nmap sqlmap nuclei ffuf hydra amass subfinder metasploit-framework 2>/dev/null | wc -l && echo 'tool binaries found on PATH'"
} else {
    Write-Host ""
    Write-Host "Build failed with exit code $LASTEXITCODE" -ForegroundColor Red
    Write-Host "Tip: Run with -NoCache to force a clean rebuild." -ForegroundColor Yellow
    exit $LASTEXITCODE
}
