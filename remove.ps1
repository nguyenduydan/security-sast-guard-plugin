$ErrorActionPreference = "Stop"

$ProgressPreference = "SilentlyContinue"

function Write-Stage {
    param([string]$Message, [int]$Percent)
    $width = 30
    $filled = [math]::Floor($width * $Percent / 100)
    $bar = ("█" * $filled) + ("░" * ($width - $filled))
    $line = "[$bar] $Percent% $Message"
    Write-Host ("`r{0,-90}" -f $line) -NoNewline -ForegroundColor Cyan
}
function Write-StageDone { param([string]$Message); Write-Host ("`r{0,-90}" -f "[OK] $Message") -ForegroundColor Green }

$PluginName = "security-sast-guard"
$InstallDir = Join-Path $HOME ".gemini\config\plugins\$PluginName"

Clear-Host
Write-Host "==============================================" -ForegroundColor DarkCyan
$SastLogo = @(
    "███████╗ █████╗ ███████╗████████╗",
    "██╔════╝██╔══██╗██╔════╝╚══██╔══╝",
    "███████╗███████║███████╗   ██║   ",
    "╚════██║██╔══██║╚════██║   ██║   ",
    "███████║██║  ██║███████║   ██║   ",
    "╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝   "
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
    Write-Stage "Removing plugin files" 50
    # Move out of the plugin directory before deleting it on Windows.
    Set-Location -Path (Split-Path -Path $InstallDir -Parent)
    Remove-Item -Path $InstallDir -Recurse -Force
    Write-StageDone "Removal complete"
    Write-Host ""
    Write-Host "Plugin removed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Error removing plugin: $_" -ForegroundColor Red
    exit 1
}

