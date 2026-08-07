$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$cCheck  = [char]0x2713
$cCross  = [char]0x2717
$cBullet = [char]0x2022
$cZap    = [char]0x26A1
$cBarF   = [char]0x25B0
$cBarE   = [char]0x25B1

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
    Write-Host " $cZap SECURITY SAST GUARD  $bV  Zero-Trust Shield for AI Coding Assistants" -ForegroundColor Cyan
    Write-Host ("  " + ("$bH" * 73)) -ForegroundColor DarkCyan
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
    $bar = ("$cBarF" * $filled) + ("$cBarE" * ($width - $filled))
    $statusLine = "`r  ⏳ [Step {0}/{1}]  {2}  {3,3}%  $bV {4}" -f $Step, $TotalSteps, $bar, $Percent, $Message
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
    $line1 = "$bV  $cCross INSTALLATION FAILED".PadRight(74) + "$bV"
    Write-Host $line1 -ForegroundColor Red
    Write-Host "$bML$h$bMR" -ForegroundColor Red
    $errStr = Format-BoxLine -Label "  Error: " -Value $Message -Width 73
    Write-Host $errStr -ForegroundColor Red
    Write-Host "$bBL$h$bBR" -ForegroundColor Red
    Write-Host ""
}

function Write-CyberSuccessCard {
    param([string]$TargetDir, [string]$Version)
    Write-Host ""
    $h = "$bH" * 73
    Write-Host "$bTL$h$bTR" -ForegroundColor Green
    $headerLine = "$bV  $cCheck INSTALLATION SUCCESSFUL".PadRight(74) + "$bV"
    Write-Host $headerLine -ForegroundColor Green
    Write-Host "$bML$h$bMR" -ForegroundColor DarkGreen

    Write-Host (Format-BoxLine -Label "  Target Directory : " -Value $TargetDir -Width 73) -ForegroundColor White
    Write-Host (Format-BoxLine -Label "  Installed Version: " -Value $Version -Width 73) -ForegroundColor White
    Write-Host (Format-BoxLine -Label "  Status           : " -Value "Active and Ready" -Width 73) -ForegroundColor Green
    
    Write-Host "$bML$h$bMR" -ForegroundColor DarkGreen
    Write-Host ("$bV  Quick Commands:".PadRight(74) + "$bV") -ForegroundColor White
    Write-Host ("$bV   $cBullet In AI Chat UI : '/sast-status' or '/sast-audit file <path>'".PadRight(74) + "$bV") -ForegroundColor Gray
    Write-Host ("$bV   $cBullet In Terminal   : 'python control_plane.py status'".PadRight(74) + "$bV") -ForegroundColor Gray
    Write-Host "$bBL$h$bBR" -ForegroundColor Green
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
                    ' ({0} Megabytes / {1} Megabytes)' -f $mbDownloaded, $mbTotal
                } else {
                    ' ({0} Megabytes)' -f $mbDownloaded
                }
                $sizeStr = $sizeStr.Replace('Megabytes', 'MB')
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
# Installation Main Flow
# ==============================================================================

$PluginName = "security-sast-guard"
$RepoOwner = "nguyenduydan"
$RepoName = "security-sast-guard-plugin"
$InstallDir = Join-Path $HOME ".gemini\config\plugins\$PluginName"

Write-CyberHeader -TargetDir $InstallDir

if (Test-Path $InstallDir) {
    Write-CyberWarn "Plugin is already installed at $InstallDir"
    Write-Host "  [i] Use 'update.ps1' to update or 'remove.ps1' to uninstall." -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

$TempDir = Join-Path ([System.IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $TempDir | Out-Null
$ExtractPath = Join-Path $TempDir "extracted"

try {
    Write-CyberStep -Step 1 -TotalSteps 4 -Message "Fetching GitHub release..." -Percent 10
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
    Write-CyberPass "Found latest release: $($Release.tag_name)"

    $ZipPath = Join-Path $TempDir $ZipAsset.name
    $ChecksumPath = Join-Path $TempDir "checksums.txt"

    Download-FileWithProgress -Url $ZipAsset.browser_download_url -OutputFile $ZipPath -Step 2 -TotalSteps 4 -Message "Downloading release archive" -BasePercent 25 -WeightPercent 35

    if ($ChecksumAsset) {
        Download-FileWithProgress -Url $ChecksumAsset.browser_download_url -OutputFile $ChecksumPath -Step 2 -TotalSteps 4 -Message "Downloading checksum file" -BasePercent 60 -WeightPercent 5
    }
    Write-CyberPass "Downloaded release package"

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

    Write-CyberStep -Step 4 -TotalSteps 4 -Message "Deploying plugin files and registering MCP server..." -Percent 75
    Expand-Archive -Path $ZipPath -DestinationPath $ExtractPath -Force
    $ExtractedRootFolder = Get-ChildItem -Path $ExtractPath -Directory | Select-Object -First 1

    $PluginsDir = Split-Path $InstallDir
    if (-not (Test-Path $PluginsDir)) {
        New-Item -ItemType Directory -Path $PluginsDir | Out-Null
    }

    Move-Item -Path $ExtractedRootFolder.FullName -Destination $InstallDir -Force
    Write-CyberPass "Deployed runtime files to target location"

    Register-MCPServer -InstallDir $InstallDir

    Write-CyberSuccessCard -TargetDir $InstallDir -Version $($Release.tag_name)
} catch {
    Write-CyberFail -Message $_.Exception.Message
    exit 1
} finally {
    if (Test-Path $TempDir) {
        Remove-Item -Path $TempDir -Recurse -Force
    }
}
