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
    Write-BoxRow -Text "$cCross UPDATE FAILED" -Color $Theme.Fail
    Write-BoxDivider -Color $Theme.Fail
    Format-BoxLine -Label "Error: " -Value $Message -Color $Theme.Fail
    Write-BoxBottom -Color $Theme.Fail
    Write-Host ""
}

function Write-CyberSuccessCard {
    param([string]$TargetDir, [string]$Version, [bool]$RestoredProfile, [string]$Elapsed)
    Write-Host ""
    Write-BoxTop -Color $Theme.Success
    Write-BoxRow -Text "$cCheck UPDATE SUCCESSFUL" -Color $Theme.Success
    Write-BoxDivider -Color $Theme.SuccessDim

    Format-BoxLine -Label "Target Directory : " -Value $TargetDir
    Format-BoxLine -Label "Updated Version  : " -Value $Version
    $profileStatus = if ($RestoredProfile) { "Preserved and Restored" } else { "Fresh Default Profile" }
    Format-BoxLine -Label "User Profile     : " -Value $profileStatus
    Format-BoxLine -Label "Duration         : " -Value $Elapsed
    Format-BoxLine -Label "Status           : " -Value "Active and Ready" -Color $Theme.Success

    Write-BoxDivider -Color $Theme.SuccessDim
    Write-BoxRow -Text "Quick Commands:"
    Write-BoxRow -Text " $cArrow In AI Chat UI : '/sast-status' or '/sast-audit file <path>'" -Color $Theme.Muted
    Write-BoxRow -Text " $cArrow In Terminal   : 'python control_plane.py status'" -Color $Theme.Muted
    Write-BoxBottom -Color $Theme.Success
    Write-Host ""
}

function Download-FileWithProgress {
    param(
        [string]$Url,
        [string]$OutputFile,
        [int]$Step,
        [int]$TotalSteps,
        [string]$Message,
        [int]$BasePercent,
        [int]$WeightPercent
    )
    $req = [System.Net.HttpWebRequest]::Create($Url)
    $req.UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    $res = $req.GetResponse()
    $totalBytes = $res.ContentLength
    $inStream = $res.GetResponseStream()
    $outStream = [System.IO.File]::Create($OutputFile)
    $buffer = New-Object byte[] 65536
    $downloaded = 0
    $sw = [System.Diagnostics.Stopwatch]::StartNew()

    try {
        while (($read = $inStream.Read($buffer, 0, $buffer.Length)) -gt 0) {
            $outStream.Write($buffer, 0, $read)
            $downloaded += $read
            if ($sw.ElapsedMilliseconds -gt 80 -or $downloaded -eq $totalBytes) {
                $sw.Restart()
                $stepPct = if ($totalBytes -gt 0) { [math]::Min(100, [math]::Floor(($downloaded / $totalBytes) * 100)) } else { 50 }
                $overallPct = [math]::Min(99, $BasePercent + [math]::Floor($stepPct * ($WeightPercent / 100)))
                $mbDownloaded = [math]::Round($downloaded / 1MB, 2)
                $mbTotal = if ($totalBytes -gt 0) { [math]::Round($totalBytes / 1MB, 2) } else { 0 }
                $sizeStr = if ($mbTotal -gt 0) {
                    ' ({0} MB / {1} MB)' -f $mbDownloaded, $mbTotal
                } else {
                    ' ({0} MB)' -f $mbDownloaded
                }
                $statusMsg = $Message + $sizeStr
                Write-CyberStep -Step $Step -TotalSteps $TotalSteps -Message $statusMsg -Percent $overallPct
            }
        }
    } finally {
        $outStream.Close()
        $inStream.Close()
        $res.Close()
    }
}

function Register-MCPServer {
    param([string]$InstallDir)
    $ConfigDir = Join-Path $HOME ".gemini\config"
    if (-not (Test-Path $ConfigDir)) {
        New-Item -ItemType Directory -Path $ConfigDir | Out-Null
    }
    $ConfigFile = Join-Path $ConfigDir "mcp_config.json"
    $NormPath = $InstallDir.Replace("\", "/")

    $JsonObj = $null
    if (Test-Path $ConfigFile) {
        try {
            $JsonObj = Get-Content -Path $ConfigFile -Raw | ConvertFrom-Json
        } catch {
            Write-CyberWarn "Could not parse existing mcp_config.json; creating new configuration."
        }
    }
    if (-not $JsonObj) {
        $JsonObj = [PSCustomObject]@{ mcpServers = [PSCustomObject]@{} }
    }
    if (-not $JsonObj.mcpServers) {
        $JsonObj | Add-Member -NotePropertyName "mcpServers" -NotePropertyValue ([PSCustomObject]@{}) -Force
    }

    $PyCmd = (Get-Command python -ErrorAction SilentlyContinue).Source
    if ($PyCmd) { $PyCmd = $PyCmd.Replace("\", "/") } else { $PyCmd = "python" }

    $ServerConfig = [PSCustomObject]@{
        command = $PyCmd
        args    = @("-m", "src.mcp.server")
        cwd     = $NormPath
        env     = [PSCustomObject]@{ PYTHONPATH = $NormPath }
    }

    if ($JsonObj.mcpServers.PSObject.Properties['security-sast-guard']) {
        $JsonObj.mcpServers.'security-sast-guard' = $ServerConfig
    } else {
        $JsonObj.mcpServers | Add-Member -NotePropertyName "security-sast-guard" -NotePropertyValue $ServerConfig -Force
    }

    $JsonStr = $JsonObj | ConvertTo-Json -Depth 10
    $Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($ConfigFile, $JsonStr, $Utf8NoBom)
    Write-CyberPass "Registered MCP Server 'security-sast-guard' in $ConfigFile"
}

# ==============================================================================
# Update Main Flow
# ==============================================================================

$PluginName = "security-sast-guard"
$RepoOwner = "nguyenduydan"
$RepoName = "security-sast-guard-plugin"
$InstallDir = Join-Path $HOME ".gemini\config\plugins\$PluginName"

Write-CyberHeader -TargetDir $InstallDir

if (-not (Test-Path $InstallDir)) {
    Write-CyberWarn "Plugin is not installed at $InstallDir"
    Write-Host "  [i] Use 'install.ps1' to install first." -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

$UpdateTimer = [System.Diagnostics.Stopwatch]::StartNew()
$TempDir = Join-Path ([System.IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $TempDir | Out-Null
$ZipPath = Join-Path $TempDir "plugin.zip"
$ExtractPath = Join-Path $TempDir "extracted"
$BackupPath = Join-Path $TempDir "profile.json.bak"
$ProfilePath = Join-Path $InstallDir "profile.json"

$HasProfile = $false
if (Test-Path $ProfilePath) {
    Copy-Item -Path $ProfilePath -Destination $BackupPath -Force
    $HasProfile = $true
}

try {
    Write-CyberStep -Step 1 -TotalSteps 4 -Message "Backing up config and checking release..." -Percent 10
    $Release = Invoke-RestMethod -Uri "https://api.github.com/repos/$RepoOwner/$RepoName/releases/latest"
    $ZipAsset = $Release.assets | Where-Object { $_.name -like "*.zip" } | Select-Object -First 1
    $ChecksumAsset = $Release.assets | Where-Object { $_.name -eq "checksums.txt" } | Select-Object -First 1

    if (-not $ZipAsset) {
        Write-CyberWarn "Release ZIP asset not found; falling back to source archive."
        $ZipAsset = [pscustomobject]@{
            name = "$($Release.tag_name).zip"
            browser_download_url = $Release.zipball_url
        }
    }
    Write-CyberPass "User profile backed up and found release: $($Release.tag_name)"

    $ZipPath = Join-Path $TempDir $ZipAsset.name
    $ChecksumPath = Join-Path $TempDir "checksums.txt"

    Download-FileWithProgress -Url $ZipAsset.browser_download_url -OutputFile $ZipPath -Step 2 -TotalSteps 4 -Message "Downloading release archive" -BasePercent 25 -WeightPercent 35

    if ($ChecksumAsset) {
        Download-FileWithProgress -Url $ChecksumAsset.browser_download_url -OutputFile $ChecksumPath -Step 2 -TotalSteps 4 -Message "Downloading checksum file" -BasePercent 60 -WeightPercent 5
    }
    Write-CyberPass "Downloaded latest release package"

    Write-CyberStep -Step 3 -TotalSteps 4 -Message "Verifying SHA-256 checksum..." -Percent 65
    if (Test-Path $ChecksumPath) {
        $ExpectedHashLine = Get-Content $ChecksumPath | Where-Object { $_ -match [regex]::Escape((Split-Path $ZipPath -Leaf)) } | Select-Object -First 1
        if ($ExpectedHashLine) {
            $ExpectedHash = ($ExpectedHashLine -split '\s+')[0].ToUpper()
            $ActualHash = (Get-FileHash -Path $ZipPath -Algorithm SHA256).Hash.ToUpper()
            if ($ExpectedHash -ne $ActualHash) {
                throw "Checksum mismatch! Expected: $ExpectedHash, Actual: $ActualHash"
            }
            Write-CyberPass "Package integrity verified (SHA-256 Match)"
        }
    } else {
        Write-CyberPass "Package checksum step skipped (checksums.txt unavailable)"
    }

    Write-CyberStep -Step 4 -TotalSteps 4 -Message "Replacing runtime files and restoring profile..." -Percent 75
    Expand-Archive -Path $ZipPath -DestinationPath $ExtractPath -Force
    $ExtractedRootFolder = Get-ChildItem -Path $ExtractPath -Directory | Select-Object -First 1

    try {
        Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*src.mcp.server*" -and $_.CommandLine -like "*security-sast-guard*" } | ForEach-Object {
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Milliseconds 500
    } catch {}

    $filesToCopy = Get-ChildItem -Path $ExtractedRootFolder.FullName -Recurse
    $totalFiles = [math]::Max(1, $filesToCopy.Count)
    $copiedCount = 0

    Get-ChildItem -Path $ExtractedRootFolder.FullName | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination $InstallDir -Recurse -Force
        $copiedCount++
        $copyPct = 75 + [math]::Floor(($copiedCount / $totalFiles) * 20)
        Write-CyberStep -Step 4 -TotalSteps 4 -Message "Deploying runtime files ($copiedCount/$totalFiles)..." -Percent $copyPct
    }

    if ($HasProfile) {
        Copy-Item -Path $BackupPath -Destination $ProfilePath -Force
        Write-CyberPass "Restored user configuration profile.json"
    } else {
        Write-CyberPass "Installed default configuration profile.json"
    }

    Register-MCPServer -InstallDir $InstallDir

    $UpdateTimer.Stop()
    $ElapsedStr = "{0:0.0}s" -f $UpdateTimer.Elapsed.TotalSeconds
    Write-CyberSuccessCard -TargetDir $InstallDir -Version $($Release.tag_name) -RestoredProfile $HasProfile -Elapsed $ElapsedStr
} catch {
    Write-CyberFail -Message $_.Exception.Message
    exit 1
} finally {
    Set-Location -Path ([System.IO.Path]::GetTempPath())
    if (Test-Path $TempDir) {
        Remove-Item -Path $TempDir -Recurse -Force
    }
}
