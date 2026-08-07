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
    $t = if ($Title) { $Title.ToUpper() } else { "UPDATER v0.10.1" }
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
    Write-Host "$bV  [$cCross] UPDATE FAILED                                                   $bV" -ForegroundColor Red
    Write-Host "$bML$bH70$bMR" -ForegroundColor Red
    $errLine = "$bV  Error: {0,-60} $bV" -f $Message
    Write-Host $errLine -ForegroundColor Red
    Write-Host "$bBL$bH70$bBR" -ForegroundColor Red
    Write-Host ""
}

function Write-CyberSuccessCard {
    param([string]$TargetDir, [string]$Version, [bool]$RestoredProfile)
    Write-Host ""
    Write-Host "$bTL$bH70$bTR" -ForegroundColor Green
    Write-Host "$bV  [$cCheck] UPDATE SUCCESSFUL                                               $bV" -ForegroundColor Green
    Write-Host "$bML$bH70$bMR" -ForegroundColor DarkGreen
    $targetLine = "$bV  Target Directory : {0,-48} $bV" -f $TargetDir
    $versionLine = "$bV  Updated Version  : {0,-48} $bV" -f $Version
    $profileStatus = if ($RestoredProfile) { "Preserved and Restored" } else { "Fresh Default Profile" }
    $profileLine = "$bV  User Profile     : {0,-48} $bV" -f $profileStatus
    $statusLine = "$bV  Status           : {0,-48} $bV" -f "Active and Ready"
    Write-Host $targetLine -ForegroundColor White
    Write-Host $versionLine -ForegroundColor White
    Write-Host $profileLine -ForegroundColor White
    Write-Host $statusLine -ForegroundColor Green
    Write-Host "$bML$bH70$bMR" -ForegroundColor DarkGreen
    Write-Host "$bV  Quick Commands:                                                     $bV" -ForegroundColor White
    $cmdLine = "$bV   $cBullet In AI Chat UI : '/sast-status' or '/sast-audit file <path>'      $bV"
    Write-Host $cmdLine -ForegroundColor Gray
    $termLine = "$bV   $cBullet In Terminal   : 'python control_plane.py status'                 $bV"
    Write-Host $termLine -ForegroundColor Gray
    Write-Host "$bBL$bH70$bBR" -ForegroundColor Green
    Write-Host ""
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

Write-CyberHeader -Title "Updater v0.10.1" -SubTitle "Target: $InstallDir"

if (-not (Test-Path $InstallDir)) {
    Write-CyberWarn "Plugin is not installed at $InstallDir"
    Write-Host " [i] Use 'install.ps1' to install first." -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

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
    Write-CyberStep -Step 1 -TotalSteps 4 -Message "Backing up user config and fetching release..." -Percent 15
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

    Write-CyberStep -Step 2 -TotalSteps 4 -Message "Downloading release archive..." -Percent 40
    Invoke-WebRequest -Uri $ZipAsset.browser_download_url -OutFile (Join-Path $TempDir $ZipAsset.name)
    if ($ChecksumAsset) {
        Invoke-WebRequest -Uri $ChecksumAsset.browser_download_url -OutFile (Join-Path $TempDir $ChecksumAsset.name)
    }
    $ZipPath = Join-Path $TempDir $ZipAsset.name
    $ChecksumPath = Join-Path $TempDir "checksums.txt"
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

    Write-CyberStep -Step 4 -TotalSteps 4 -Message "Replacing runtime files and restoring profile..." -Percent 90
    Expand-Archive -Path $ZipPath -DestinationPath $ExtractPath -Force
    $ExtractedRootFolder = Get-ChildItem -Path $ExtractPath -Directory | Select-Object -First 1

    try {
        Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*src.mcp.server*" -and $_.CommandLine -like "*security-sast-guard*" } | ForEach-Object {
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Milliseconds 500
    } catch {}

    Get-ChildItem -Path $ExtractedRootFolder.FullName | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination $InstallDir -Recurse -Force
    }

    if ($HasProfile) {
        Copy-Item -Path $BackupPath -Destination $ProfilePath -Force
        Write-CyberPass "Restored user configuration profile.json"
    } else {
        Write-CyberPass "Installed default configuration profile.json"
    }

    Register-MCPServer -InstallDir $InstallDir

    Write-CyberSuccessCard -TargetDir $InstallDir -Version $($Release.tag_name) -RestoredProfile $HasProfile
} catch {
    Write-CyberFail -Message $_.Exception.Message
    exit 1
} finally {
    Set-Location -Path ([System.IO.Path]::GetTempPath())
    if (Test-Path $TempDir) {
        Remove-Item -Path $TempDir -Recurse -Force
    }
}
