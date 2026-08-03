$ErrorActionPreference = "Stop"

$PluginName = "security-sast-guard"
$InstallDir = Join-Path $HOME ".gemini\config\plugins\$PluginName"

Write-Host "Removing $PluginName..." -ForegroundColor Cyan

if (-not (Test-Path $InstallDir)) {
    Write-Host "Plugin is not installed at $InstallDir" -ForegroundColor Yellow
    Write-Host "Nothing to remove." -ForegroundColor Yellow
    exit 0
}

$Confirmation = Read-Host "Are you sure you want to remove the plugin and all its data? (Y/N)"
if ($Confirmation -notmatch "^[Yy]$") {
    Write-Host "Removal cancelled." -ForegroundColor Yellow
    exit 0
}

try {
    Write-Host "Deleting $InstallDir ..."
    Remove-Item -Path $InstallDir -Recurse -Force
    Write-Host ""
    Write-Host "Plugin removed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Error removing plugin: $_" -ForegroundColor Red
    exit 1
}
