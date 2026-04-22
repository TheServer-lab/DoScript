# DoScript Quick Installer
# Run with:
# irm https://raw.githubusercontent.com/TheServer-lab/DoScript/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

$url = "https://github.com/TheServer-lab/DoScript/releases/download/latest-release/DoScriptSetup.exe"
$tempFile = Join-Path $env:TEMP "DoScriptSetup.exe"

try {
    Write-Host "Downloading DoScript..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $url -OutFile $tempFile

    Write-Host "Launching installer..." -ForegroundColor Yellow

    # Wait for installer to close
    $proc = Start-Process -FilePath $tempFile -PassThru -Wait

    Write-Host "Cleaning up..." -ForegroundColor Yellow
}
catch {
    Write-Host "Installation failed or was cancelled." -ForegroundColor Red
}
finally {
    Start-Sleep -Seconds 1

    if (Test-Path $tempFile) {
        Remove-Item $tempFile -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host "Installer closed." -ForegroundColor Green
Write-Host "If DoScript was installed, reopen your terminal and run: do" -ForegroundColor DarkYellow
