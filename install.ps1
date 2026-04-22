# DoScript Quick Installer
# Run with:
# irm https://raw.githubusercontent.com/TheServer-lab/DoScript/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

$url = "https://github.com/TheServer-lab/DoScript/releases/download/latest-release/DoScriptSetup.exe"
$tempFile = Join-Path $env:TEMP "DoScriptSetup.exe"

Write-Host "Downloading DoScript..." -ForegroundColor Cyan
Invoke-WebRequest -Uri $url -OutFile $tempFile

Write-Host "Launching installer..." -ForegroundColor Yellow
Start-Process -FilePath $tempFile -Wait

Write-Host "Cleaning up..." -ForegroundColor Yellow
Remove-Item $tempFile -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "DoScript installation complete." -ForegroundColor Green
Write-Host "You may need to reopen your terminal before using: do" -ForegroundColor DarkYellow
