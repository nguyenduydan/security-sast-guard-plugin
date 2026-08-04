$ErrorActionPreference = "Stop"

$PluginName = "security-sast-guard"
$InstallDir = Join-Path $HOME ".gemini\config\plugins\$PluginName"

Clear-Host
Write-Host "==============================================" -ForegroundColor DarkCyan
$SastLogo = @(
    "  #####  #####  #####  #######",
    " #      #     # #      #    #   ",
    "  ###   #######  ###        #   ",
    "     #  #     #     #       #   ",
    "#####   #     # #####       #   "
)
foreach ($Line in $SastLogo) {
    Write-Host $Line -ForegroundColor Cyan
}
Write-Host "          SECURITY SAST GUARD" -ForegroundColor White
Write-Host "               REMOVER" -ForegroundColor DarkCyan
Write-Host "==============================================" -ForegroundColor DarkCyan
Write-Host "Target: $InstallDir" -ForegroundColor Gray
Write-Host ""

if (-not (Test-Path $InstallDir)) {
    Write-Host "Plugin is not installed at $InstallDir" -ForegroundColor Yellow
    Write-Host "Nothing to remove." -ForegroundColor Yellow
    exit 0
}

$Confirmation = Read-Host "Remove the plugin and all its data? (Y/N)"
if ($Confirmation -notmatch "^[Yy]$") {
    Write-Host "Removal cancelled." -ForegroundColor Yellow
    exit 0
}

try {
    Write-Progress -Activity "Removing Security SAST Guard" -Status "Removing plugin files" -PercentComplete 50
    Write-Host "Deleting $InstallDir ..."
    Remove-Item -Path $InstallDir -Recurse -Force
    Write-Progress -Activity "Removing Security SAST Guard" -Status "Removal complete" -PercentComplete 100 -Completed
    Write-Host ""
    Write-Host "Plugin removed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Error removing plugin: $_" -ForegroundColor Red
    exit 1
}
