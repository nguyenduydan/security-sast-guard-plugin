param(
    [switch]$Ascii,
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
} catch {}

$Theme = @{
    Primary    = "Cyan"
    Dim        = "DarkCyan"
    Success    = "Green"
    SuccessDim = "DarkGreen"
    Warn       = "Yellow"
    Fail       = "Red"
    Text       = "White"
    Muted      = "Gray"
}

$script:IsRealConsole = $true
try {
    if ([Console]::IsOutputRedirected) { $script:IsRealConsole = $false }
} catch {}
if ($Host.Name -match 'ISE') { $script:IsRealConsole = $false }

$script:ShowProgressBar = $script:IsRealConsole -and (-not $Quiet.IsPresent)

$script:UseAscii = $Ascii.IsPresent
if (-not $script:UseAscii) {
    try {
        if ([Console]::OutputEncoding.CodePage -ne 65001) { $script:UseAscii = $true }
    } catch {
        $script:UseAscii = $true
    }
}

if ($script:UseAscii) {
    $bTL = '+'; $bTR = '+'; $bBL = '+'; $bBR = '+'
    $bH  = '-'; $bV  = '|'; $bML = '+'; $bMR = '+'
    $cCheck = 'OK'; $cCross = 'X'; $cBullet = '*'; $cArrow = '>'
    $cShield = '[#]'; $cWarn = '!'; $cHourglass = '...'
    $barFilledChar = '#'; $barEmptyChar = '-'
} else {
    $bTL = [char]0x256D # ╭
    $bTR = [char]0x256E # ╮
    $bBL = [char]0x2570 # ╰
    $bBR = [char]0x256F # ╯
    $bH  = [char]0x2500 # ─
    $bV  = [char]0x2502 # │
    $bML = [char]0x251C # ├
    $bMR = [char]0x2524 # ┤
    $cCheck = [char]0x2713   # ✓
    $cCross = [char]0x2717   # ✗
    $cBullet = [char]0x2022
$cZap    = [char]0x26A1
$cBarF   = [char]0x25B0
$cBarE   = [char]0x25B1  # •
    $cArrow  = [char]0x25B8  # ▸
    $cShield = [char]0x26E8  # ⛨
    $cWarn   = [char]0x26A0  # ⚠
    $cHourglass = [char]0x23F3 # ⏳
    $barFilledChar = [char]0x25B0 # $cBarF
    $barEmptyChar  = [char]0x25B1 # $cBarE
}

function Get-BoxInnerWidth {
    $inner = 73
    if ($script:IsRealConsole) {
        try {
            $consoleW = $Host.UI.RawUI.WindowSize.Width
            if ($consoleW -gt 0) {
                $inner = [math]::Max(60, [math]::Min(96, $consoleW - 6))
            }
        } catch {}
    }
    return $inner
}

$script:Inner     = Get-BoxInnerWidth
$script:LineWidth = $script:Inner + 17

function Write-BoxTop {
    param([string]$Color)
    Write-Host "$bTL$([string]$bH * $script:Inner)$bTR" -ForegroundColor $Color
}

function Write-BoxDivider {
    param([string]$Color)
    Write-Host "$bML$([string]$bH * $script:Inner)$bMR" -ForegroundColor $Color
}

function Write-BoxBottom {
    param([string]$Color)
    Write-Host "$bBL$([string]$bH * $script:Inner)$bBR" -ForegroundColor $Color
}

function Write-BoxRow {
    param([string]$Text, [string]$Color = $Theme.Text)
    $padded = " $Text".PadRight($script:Inner)
    Write-Host "$bV$padded$bV" -ForegroundColor $Color
}

function Format-BoxLine {
    param([string]$Label, [string]$Value, [string]$Color = $Theme.Text)
    $avail = $script:Inner - $Label.Length - 1
    if ($avail -lt 5) { $avail = 5 }
    $valStr = $Value
    if ($valStr.Length -gt $avail) {
        $valStr = "..." + $valStr.Substring($valStr.Length - ($avail - 3))
    }
    Write-BoxRow -Text "$Label$valStr" -Color $Color
}

function Write-CyberHeader {
    param([string]$TargetDir)
    if ($script:IsRealConsole) {
        try { Clear-Host } catch {}
    }
    Write-Host ""
    Write-Host " $cShield  SECURITY SAST GUARD" -ForegroundColor Cyan
    Write-Host "    Zero-Trust Shield for AI Coding Assistants" -ForegroundColor DarkCyan
    Write-Host " $([string]$bH * ($script:Inner + 2))" -ForegroundColor DarkCyan
    if ($TargetDir) {
        Write-Host "  Target : $TargetDir" -ForegroundColor Gray
    }
    Write-Host ""
}

function Get-ProgressColor {
    param([int]$Percent)
    if ($Percent -lt 34)      { return $Theme.Fail }
    elseif ($Percent -lt 67)  { return $Theme.Warn }
    else                      { return $Theme.Success }
}

function Write-CyberStep {
    param([int]$Step, [int]$TotalSteps, [string]$Message, [int]$Percent)
    if (-not $script:ShowProgressBar) { return }

    $barWidth = 24
    $filled = [math]::Floor($barWidth * $Percent / 100)
    if ($filled -lt 0) { $filled = 0 }
    if ($filled -gt $barWidth) { $filled = $barWidth }
    $bar = ([string]$barFilledChar * $filled) + ([string]$barEmptyChar * ($barWidth - $filled))
    $barColor = Get-ProgressColor -Percent $Percent

    Write-Host ("`r  {0} [{1}/{2}]  " -f $cHourglass, $Step, $TotalSteps) -NoNewline -ForegroundColor DarkCyan
    Write-Host $bar -NoNewline -ForegroundColor $barColor
    $msg = ("  {0,3}%  $bV  {1}" -f $Percent, $Message)
    Write-Host $msg.PadRight(60) -NoNewline -ForegroundColor White
}

function Write-CyberPass {
    param([string]$Message)
    $prefix = if ($script:IsRealConsole) { "`r" } else { "" }
    $line = "$prefix  $cCheck  $Message"
    if ($script:IsRealConsole) { $line = $line.PadRight($script:LineWidth + 25) }
    Write-Host $line -ForegroundColor Green
}

function Write-CyberWarn {
    param([string]$Message)
    $prefix = if ($script:IsRealConsole) { "`r" } else { "" }
    $line = "$prefix  $cWarn  $Message"
    if ($script:IsRealConsole) { $line = $line.PadRight($script:LineWidth + 25) }
    Write-Host $line -ForegroundColor Yellow
}

function Write-CyberFail {
    param([string]$Message)
    Write-Host ""
    Write-BoxTop -Color $Theme.Fail
    Write-BoxRow -Text "$cCross REMOVAL FAILED" -Color $Theme.Fail
    Write-BoxDivider -Color $Theme.Fail
    Format-BoxLine -Label "Error: " -Value $Message -Color $Theme.Fail
    Write-BoxBottom -Color $Theme.Fail
    Write-Host ""
}

function Write-CyberRemovalSuccessCard {
    param([string]$TargetDir, [string]$Elapsed)
    Write-Host ""
    Write-BoxTop -Color $Theme.Warn
    Write-BoxRow -Text "$cCheck REMOVAL SUCCESSFUL" -Color $Theme.Warn
    Write-BoxDivider -Color $Theme.Warn

    Format-BoxLine -Label "Removed Directory: " -Value $TargetDir
    Format-BoxLine -Label "Duration         : " -Value $Elapsed
    Format-BoxLine -Label "Status           : " -Value "Uninstalled" -Color $Theme.Muted

    Write-BoxBottom -Color $Theme.Warn
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
if ($Confirmation -notmatch '^[Yy]$') {
    Write-Host ""
    Write-CyberWarn "Removal cancelled by user."
    Write-Host ""
    exit 0
}

$RemoveTimer = [System.Diagnostics.Stopwatch]::StartNew()

try {
    Write-CyberStep -Step 1 -TotalSteps 1 -Message "Removing plugin files and configuration..." -Percent 50
    Set-Location -Path (Split-Path -Path $InstallDir -Parent)
    
    try {
        Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*src.mcp.server*' -and $_.CommandLine -like '*security-sast-guard*' } | ForEach-Object {
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Milliseconds 500
    } catch {}

    Remove-Item -Path $InstallDir -Recurse -Force
    Write-CyberPass "Successfully uninstalled plugin files from system"

    $RemoveTimer.Stop()
    $ElapsedStr = "{0:0.0}s" -f $RemoveTimer.Elapsed.TotalSeconds
    Write-CyberRemovalSuccessCard -TargetDir $InstallDir -Elapsed $ElapsedStr
} catch {
    Write-CyberFail -Message $_.Exception.Message
    exit 1
}
