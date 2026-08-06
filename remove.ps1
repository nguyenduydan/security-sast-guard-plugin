$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Write-CyberHeader {
    param([string]$Title, [string]$SubTitle)
    Clear-Host
    Write-Host "╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor DarkCyan
    Write-Host "║  ███████╗ █████╗ ███████╗████████╗                                   ║" -ForegroundColor Cyan
    Write-Host "║  ██╔════╝██╔══██╗██╔════╝╚══██╔══╝   SECURITY SAST GUARD             ║" -ForegroundColor Cyan
    Write-Host "║  ███████╗███████║███████╗   ██║      Zero-Trust Shield               ║" -ForegroundColor Cyan
    Write-Host "║  ╚════██║██╔══██║╚════██║   ██║                                      ║" -ForegroundColor Cyan
    $t = if ($Title) { $Title.ToUpper() } else { "UNINSTALLER v0.10.1" }
    $tStr = "║  ███████║██║  ██║███████║   ██║      {0,-31} ║" -f $t
    Write-Host $tStr -ForegroundColor Cyan
    Write-Host "║  ╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝                                      ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════════════╝" -ForegroundColor DarkCyan
    if ($SubTitle) {
        Write-Host " [i] $SubTitle" -ForegroundColor Gray
    }
    Write-Host ""
}

function Write-CyberStep {
    param([int]$Step, [int]$TotalSteps, [string]$Message, [int]$Percent)
    $width = 25
    $filled = [math]::Floor($width * $Percent / 100)
    $bar = ("█" * $filled) + ("░" * ($width - $filled))
    $statusLine = "`r [Step $Step/$TotalSteps] [$bar] {0,3}% {1,-40}" -f $Percent, $Message
    Write-Host $statusLine -NoNewline -ForegroundColor Cyan
}

function Write-CyberPass {
    param([string]$Message)
    $passLine = "`r [✓] {0,-70}" -f $Message
    Write-Host $passLine -ForegroundColor Green
}

function Write-CyberWarn {
    param([string]$Message)
    $warnLine = "`r [!] {0,-70}" -f $Message
    Write-Host $warnLine -ForegroundColor Yellow
}

function Write-CyberFail {
    param([string]$Message)
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║  [✗] REMOVAL FAILED                                                  ║" -ForegroundColor Red
    Write-Host "╠══════════════════════════════════════════════════════════════════════╣" -ForegroundColor Red
    $errLine = "║  Error: {0,-60} ║" -f $Message
    Write-Host $errLine -ForegroundColor Red
    Write-Host "╚══════════════════════════════════════════════════════════════════════╝" -ForegroundColor Red
    Write-Host ""
}

function Write-CyberRemovalSuccessCard {
    param([string]$TargetDir)
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "║  [✓] REMOVAL SUCCESSFUL                                              ║" -ForegroundColor Yellow
    Write-Host "╠══════════════════════════════════════════════════════════════════════╣" -ForegroundColor DarkYellow
    $targetLine = "║  Removed Directory: {0,-48} ║" -f $TargetDir
    $statusLine = "║  Status           : {0,-48} ║" -f "Uninstalled"
    Write-Host $targetLine -ForegroundColor White
    Write-Host $statusLine -ForegroundColor Gray
    Write-Host "╚══════════════════════════════════════════════════════════════════════╝" -ForegroundColor Yellow
    Write-Host ""
}

# ==============================================================================
# Removal Main Flow
# ==============================================================================

$PluginName = "security-sast-guard"
$InstallDir = Join-Path $HOME ".gemini\config\plugins\$PluginName"

Write-CyberHeader -Title "Uninstaller v0.10.1" -SubTitle "Target: $InstallDir"

if (-not (Test-Path $InstallDir)) {
    Write-CyberWarn "Plugin is not installed at $InstallDir"
    Write-Host " [i] Nothing to remove." -ForegroundColor Gray
    Write-Host ""
    exit 0
}

Write-Host " [?] Are you sure you want to remove Security SAST Guard and all its files? [y/N]: " -NoNewline -ForegroundColor Yellow
$Confirmation = Read-Host
if ($Confirmation -notmatch "^[Yy]$") {
    Write-Host ""
    Write-CyberWarn "Removal cancelled by user."
    Write-Host ""
    exit 0
}

try {
    Write-CyberStep -Step 1 -TotalSteps 1 -Message "Removing plugin files and configuration..." -Percent 50
    Set-Location -Path (Split-Path -Path $InstallDir -Parent)
    Remove-Item -Path $InstallDir -Recurse -Force
    Write-CyberPass "Successfully uninstalled plugin files from system"

    Write-CyberRemovalSuccessCard -TargetDir $InstallDir
} catch {
    Write-CyberFail -Message $_.Exception.Message
    exit 1
}
