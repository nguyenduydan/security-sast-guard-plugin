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
    $t = if ($Title) { $Title.ToUpper() } else { "UPDATER v0.10.1" }
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
    Write-Host "║  [✗] UPDATE FAILED                                                   ║" -ForegroundColor Red
    Write-Host "╠══════════════════════════════════════════════════════════════════════╣" -ForegroundColor Red
    $errLine = "║  Error: {0,-60} ║" -f $Message
    Write-Host $errLine -ForegroundColor Red
    Write-Host "╚══════════════════════════════════════════════════════════════════════╝" -ForegroundColor Red
    Write-Host ""
}

function Write-CyberSuccessCard {
    param([string]$TargetDir, [string]$Version, [bool]$RestoredProfile)
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  [✓] UPDATE SUCCESSFUL                                               ║" -ForegroundColor Green
    Write-Host "╠══════════════════════════════════════════════════════════════════════╣" -ForegroundColor DarkGreen
    $targetLine = "║  Target Directory : {0,-48} ║" -f $TargetDir
    $versionLine = "║  Updated Version  : {0,-48} ║" -f $Version
    $profileStatus = if ($RestoredProfile) { "Preserved and Restored" } else { "Fresh Default Profile" }
    $profileLine = "║  User Profile     : {0,-48} ║" -f $profileStatus
    $statusLine = "║  Status           : {0,-48} ║" -f "Active and Ready"
    Write-Host $targetLine -ForegroundColor White
    Write-Host $versionLine -ForegroundColor White
    Write-Host $profileLine -ForegroundColor White
    Write-Host $statusLine -ForegroundColor Green
    Write-Host "╠══════════════════════════════════════════════════════════════════════╣" -ForegroundColor DarkGreen
    Write-Host "║  Quick Commands:                                                     ║" -ForegroundColor White
    Write-Host "║   • In AI Chat UI : '/sast-status' or '/sast-audit file <path>'      ║" -ForegroundColor Gray
    Write-Host "║   • In Terminal   : 'python control_plane.py status'                 ║" -ForegroundColor Gray
    Write-Host "╚══════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
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

    $ServerConfig = [PSCustomObject]@{
        command = "python"
        args    = @("-m", "src.mcp.server")
        cwd     = $NormPath
        env     = [PSCustomObject]@{ PYTHONPATH = $NormPath }
    }

    if ($JsonObj.mcpServers.PSObject.Properties['security-sast-guard']) {
        $JsonObj.mcpServers.'security-sast-guard' = $ServerConfig
    } else {
        $JsonObj.mcpServers | Add-Member -NotePropertyName "security-sast-guard" -NotePropertyValue $ServerConfig -Force
    }

    $JsonObj | ConvertTo-Json -Depth 10 | Set-Content -Path $ConfigFile -Encoding UTF8
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

    Set-Location -Path $TempDir
    Remove-Item -Path $InstallDir -Recurse -Force
    Move-Item -Path $ExtractedRootFolder.FullName -Destination $InstallDir -Force

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
