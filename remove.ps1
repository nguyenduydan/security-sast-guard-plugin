$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$cCheck  = [char]0x2713
$cCross  = [char]0x2717
$cBullet = [char]0x2022
$cFull   = [char]0x2588
$cLight  = [char]0x2591

$bTL = [char]0x2554
$bTR = [char]0x2557
$bBL = [char]0x255A
$bBR = [char]0x255D
$bH  = [char]0x2550
$bV  = [char]0x2551
$bML = [char]0x2560
$bMR = [char]0x2563

$bH70 = "$bH" * 70

function Write-CyberHeader {
    param([string]$Title, [string]$SubTitle)
    Clear-Host
    Write-Host "$bTL$bH70$bTR" -ForegroundColor DarkCyan
    Write-Host "$bV  === SECURITY SAST GUARD ===                                       $bV" -ForegroundColor Cyan
    Write-Host "$bV  Zero-Trust Shield for AI Coding Assistants                       $bV" -ForegroundColor Cyan
    $t = if ($Title) { $Title.ToUpper() } else { "UNINSTALLER v0.10.1" }
    $tStr = "$bV  {0,-67} $bV" -f $t
    Write-Host $tStr -ForegroundColor Cyan
    Write-Host "$bBL$bH70$bBR" -ForegroundColor DarkCyan
    if ($SubTitle) {
        Write-Host " [i] $SubTitle" -ForegroundColor Gray
    }
    Write-Host ""
}

function Write-CyberStep {
    param([int]$Step, [int]$TotalSteps, [string]$Message, [int]$Percent)
    $width = 25
    $filled = [math]::Floor($width * $Percent / 100)
    $bar = ("$cFull" * $filled) + ("$cLight" * ($width - $filled))
    $statusLine = "`r [Step $Step/$TotalSteps] [$bar] {0,3}% {1,-40}" -f $Percent, $Message
    Write-Host $statusLine -NoNewline -ForegroundColor Cyan
}

function Write-CyberPass {
    param([string]$Message)
    $passLine = "`r [$cCheck] {0,-70}" -f $Message
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
    Write-Host "$bTL$bH70$bTR" -ForegroundColor Red
    Write-Host "$bV  [$cCross] REMOVAL FAILED                                                  $bV" -ForegroundColor Red
    Write-Host "$bML$bH70$bMR" -ForegroundColor Red
    $errLine = "$bV  Error: {0,-60} $bV" -f $Message
    Write-Host $errLine -ForegroundColor Red
    Write-Host "$bBL$bH70$bBR" -ForegroundColor Red
    Write-Host ""
}

function Write-CyberRemovalSuccessCard {
    param([string]$TargetDir)
    Write-Host ""
    Write-Host "$bTL$bH70$bTR" -ForegroundColor Yellow
    Write-Host "$bV  [$cCheck] REMOVAL SUCCESSFUL                                              $bV" -ForegroundColor Yellow
    Write-Host "$bML$bH70$bMR" -ForegroundColor DarkYellow
    $targetLine = "$bV  Removed Directory: {0,-48} $bV" -f $TargetDir
    $statusLine = "$bV  Status           : {0,-48} $bV" -f "Uninstalled"
    Write-Host $targetLine -ForegroundColor White
    Write-Host $statusLine -ForegroundColor Gray
    Write-Host "$bBL$bH70$bBR" -ForegroundColor Yellow
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
