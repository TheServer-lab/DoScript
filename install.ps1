# DoScript One-Command Installer
# Usage:
# irm https://raw.githubusercontent.com/TheServer-lab/DoScript/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "        DoScript Installer" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Config
$repo = "TheServer-lab/DoScript"
$releaseUrl = "https://github.com/$repo/releases/download/latest-release/DoScriptSetup.exe"

$tempDir = Join-Path $env:TEMP "DoScriptInstall"
$installer = Join-Path $tempDir "DoScriptSetup.exe"

# Prepare temp folder
if (!(Test-Path $tempDir)) {
    New-Item -ItemType Directory -Path $tempDir | Out-Null
}

Write-Host "[1/5] Downloading latest DoScript..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $releaseUrl -OutFile $installer

Write-Host "[2/5] Running installer silently..." -ForegroundColor Yellow
Start-Process -FilePath $installer -ArgumentList "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART" -Wait

Write-Host "[3/5] Refreshing PATH..." -ForegroundColor Yellow
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
            [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host "[4/5] Checking installation..." -ForegroundColor Yellow

$do = Get-Command do -ErrorAction SilentlyContinue

if ($do) {
    Write-Host "[5/5] DoScript installed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Try these commands:" -ForegroundColor Cyan
    Write-Host "  do --version"
    Write-Host "  do hello.do"
} else {
    Write-Host "Installed, but terminal restart may be required." -ForegroundColor Yellow
    Write-Host "Close and reopen terminal, then run: do --version"
}

Write-Host ""
Write-Host "Thank you for installing DoScript." -ForegroundColor Green
