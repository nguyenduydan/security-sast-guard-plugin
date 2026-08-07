$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$cCheck  = [char]0x2713
$cCross  = [char]0x2717
$cBullet = [char]0x2022

$bTL = [char]0x256D # ╭
$bTR = [char]0x256E # ╮
$bBL = [char]0x2570 # ╰
$bBR = [char]0x256F # ╯
$bH  = [char]0x2500 # ─
$bV  = [char]0x2502 # │
$bML = [char]0x251C # ├
$bMR = [char]0x2524 # ┤

function Format-BoxLine {
    param([string]$Label, [string]$Value, [int]$Width = 73)
    $avail = $Width - $Label.Length
    if ($avail -lt 5) { $avail = 5 }
    $valStr = $Value
    if ($valStr.Length -gt $avail) {
        $valStr = "..." + $valStr.Substring($valStr.Length - ($avail - 3))
    }
    $padded = "$Label$valStr".PadRight($Width)
    return "$bV$padded$bV"
}

function Write-CyberHeader {
    param([string]$TargetDir)
    Clear-Host
    Write-Host ""
    Write-Host " ⚡ SECURITY SAST GUARD  │  Zero-Trust Shield for AI Coding Assistants" -ForegroundColor Cyan
    Write-Host " ─────────────────────────────────────────────────────────────────────────────" -ForegroundColor DarkCyan
    if ($TargetDir) {
        Write-Host "  Target : $TargetDir" -ForegroundColor Gray
    }
    Write-Host ""
}

function Write-CyberStep {
    param([int]$Step, [int]$TotalSteps, [string]$Message, [int]$Percent)
    $width = 20
    $filled = [math]::Floor($width * $Percent / 100)
    if ($filled -lt 0) { $filled = 0 }
    if ($filled -gt $width) { $filled = $width }
    $bar = ("▰" * $filled) + ("▱" * ($width - $filled))
    $statusLine = "`r  ⏳ [Step $Step/$TotalSteps]  $bar  {0,3}%  │ {1}" -f $Percent, $Message
    $statusLine = $statusLine.PadRight(85)
    Write-Host $statusLine -NoNewline -ForegroundColor Cyan
}

function Write-CyberPass {
    param([string]$Message)
    $passLine = "`r  $cCheck  {0}" -f $Message
    $passLine = $passLine.PadRight(85)
    Write-Host $passLine -ForegroundColor Green
}

function Write-CyberWarn {
    param([string]$Message)
    $warnLine = "`r  !  {0}" -f $Message
    $warnLine = $warnLine.PadRight(85)
    Write-Host $warnLine -ForegroundColor Yellow
}

function Write-CyberFail {
    param([string]$Message)
    Write-Host ""
    $h = "$bH" * 73
    Write-Host "$bTL$h$bTR" -ForegroundColor Red
    $line1 = "$bV  $cCross REMOVAL FAILED".PadRight(74) + "$bV"
    Write-Host $line1 -ForegroundColor Red
    Write-Host "$bML$h$bMR" -ForegroundColor Red
    $errStr = Format-BoxLine -Label "  Error: " -Value $Message -Width 73
    Write-Host $errStr -ForegroundColor Red
    Write-Host "$bBL$h$bBR" -ForegroundColor Red
    Write-Host ""
}

function Write-CyberRemovalSuccessCard {
    param([string]$TargetDir)
    Write-Host ""
    $h = "$bH" * 73
    Write-Host "$bTL$h$bTR" -ForegroundColor Yellow
    $headerLine = "$bV  $cCheck REMOVAL SUCCESSFUL".PadRight(74) + "$bV"
    Write-Host $headerLine -ForegroundColor Yellow
    Write-Host "$bML$h$bMR" -ForegroundColor DarkYellow

    Write-Host (Format-BoxLine -Label "  Removed Directory: " -Value $TargetDir -Width 73) -ForegroundColor White
    Write-Host (Format-BoxLine -Label "  Status           : " -Value "Uninstalled" -Width 73) -ForegroundColor Gray
    Write-Host "$bBL$h$bBR" -ForegroundColor Yellow
    Write-Host ""
}

# ==============================================================================
# Removal Main Flow
# ==============================================================================

$PluginName = "security-sast-guard"
$InstallDir = Join-Path $HOME ".gemini\config\plugins\$PluginName"

Write-CyberHeader -TargetDir $InstallDir

if (-not (Test-Path $InstallDir)) {
    Write-CyberWarn "Plugin is not installed at $InstallDir"
    Write-Host "  [i] Nothing to remove." -ForegroundColor Gray
    Write-Host ""
    exit 0
}

Write-Host "  [?] Are you sure you want to remove Security SAST Guard and all its files? [y/N]: " -NoNewline -ForegroundColor Yellow
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
    
    try {
        Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*src.mcp.server*" -and $_.CommandLine -like "*security-sast-guard*" } | ForEach-Object {
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Milliseconds 500
    } catch {}

    Remove-Item -Path $InstallDir -Recurse -Force
    Write-CyberPass "Successfully uninstalled plugin files from system"

    Write-CyberRemovalSuccessCard -TargetDir $InstallDir
} catch {
    Write-CyberFail -Message $_.Exception.Message
    exit 1
}
