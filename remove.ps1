$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Configure Console Output Encoding for UTF-8 Symbols
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# ==============================================================================
# TUI Helper Functions (Cyber / Neo-Brutalist Theme)
# ==============================================================================

function Write-CyberHeader {
    param([string]$Title, [string]$SubTitle)
    Clear-Host
    Write-Host "╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor DarkCyan
    Write-Host "║  ███████╗ █████╗ ███████╗████████╗                                   ║" -ForegroundColor Cyan
    Write-Host "║  ██╔════╝██╔══██╗██╔════╝╚══██╔══╝   SECURITY SAST GUARD             ║" -ForegroundColor Cyan
    Write-Host "║  ███████╗███████║███████╗   ██║      Zero-Trust Shield               ║" -ForegroundColor Cyan
    Write-Host "║  ╚════██║██╔══██║╚════██║   ██║                                      ║" -ForegroundColor Cyan
    Write-Host ("║  ███████║██║  ██║███████║   ██║      {0,-31} ║" -f $Title.ToUpper()) -ForegroundColor Cyan
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
    $statusLine = ("`r [Step $Step/$TotalSteps] [$bar] {0,3}% {1,-40}" -f $Percent, $Message)
    Write-Host $statusLine -NoNewline -ForegroundColor Cyan
}

function Write-CyberPass {
    param([string]$Message)
    $chk = [char]0x2713
    Write-Host ("`r [$chk] {0,-70}" -f $Message) -ForegroundColor Green
}

function Write-CyberWarn {
    param([string]$Message)
    Write-Host ("`r [!] {0,-70}" -f $Message) -ForegroundColor Yellow
}

function Write-CyberFail {
    param([string]$Message)
    $cross = [char]0x2717
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host ("║  [$cross] REMOVAL FAILED                                                  ║") -ForegroundColor Red
    Write-Host "╠══════════════════════════════════════════════════════════════════════╣" -ForegroundColor Red
    Write-Host ("║  Error: {0,-60} ║" -f $Message) -ForegroundColor Red
    Write-Host "╚══════════════════════════════════════════════════════════════════════╝" -ForegroundColor Red
    Write-Host ""
}

function Write-CyberRemovalSuccessCard {
    param([string]$TargetDir)
    $chk = [char]0x2713
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host ("║  [$chk] REMOVAL SUCCESSFUL                                              ║") -ForegroundColor Yellow
    Write-Host "╠══════════════════════════════════════════════════════════════════════╣" -ForegroundColor DarkYellow
    Write-Host ("║  Removed Directory: {0,-48} ║" -f $TargetDir) -ForegroundColor White
    Write-Host ("║  Status           : {0,-48} ║" -f "Uninstalled") -ForegroundColor Gray
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
