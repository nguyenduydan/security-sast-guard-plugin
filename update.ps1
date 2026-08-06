$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Configure Output Encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# ==============================================================================
# TUI Helper Functions (Cyber ASCII Theme)
# ==============================================================================

function Write-CyberHeader {
    param([string]$Title, [string]$SubTitle)
    Clear-Host
    Write-Host "+======================================================================+" -ForegroundColor DarkCyan
    Write-Host "|  #######  #####   #####  #######                                     |" -ForegroundColor Cyan
    Write-Host "|  #       #     # #     #    #        SECURITY SAST GUARD             |" -ForegroundColor Cyan
    Write-Host "|  #####   ######  #####      #        Zero-Trust Shield               |" -ForegroundColor Cyan
    Write-Host "|       #  #     #      #     #                                        |" -ForegroundColor Cyan
    $titleStr = "|  #####   #     # #####      #        $($Title.ToUpper())"
    Write-Host ($titleStr.PadRight(71) + "|") -ForegroundColor Cyan
    Write-Host "+======================================================================+" -ForegroundColor DarkCyan
    if ($SubTitle) {
        Write-Host " [i] $SubTitle" -ForegroundColor Gray
    }
    Write-Host ""
}

function Write-CyberStep {
    param([int]$Step, [int]$TotalSteps, [string]$Message, [int]$Percent)
    $width = 25
    $filled = [math]::Floor($width * $Percent / 100)
    $bar = ("=" * $filled) + ("-" * ($width - $filled))
    $statusLine = "`r [Step $Step/$TotalSteps] [$bar] $($Percent.ToString().PadLeft(3))% $($Message.PadRight(40))"
    Write-Host $statusLine -NoNewline -ForegroundColor Cyan
}

function Write-CyberPass {
    param([string]$Message)
    Write-Host "`r [OK] $($Message.PadRight(70))" -ForegroundColor Green
}

function Write-CyberWarn {
    param([string]$Message)
    Write-Host "`r [!] $($Message.PadRight(70))" -ForegroundColor Yellow
}

function Write-CyberFail {
    param([string]$Message)
    Write-Host ""
    Write-Host "+======================================================================+" -ForegroundColor Red
    Write-Host "|  [X] UPDATE FAILED                                                   |" -ForegroundColor Red
    Write-Host "+----------------------------------------------------------------------+" -ForegroundColor Red
    $errStr = "|  Error: $($Message)"
    Write-Host ($errStr.PadRight(71) + "|") -ForegroundColor Red
    Write-Host "+======================================================================+" -ForegroundColor Red
    Write-Host ""
}

function Write-CyberSuccessCard {
    param([string]$TargetDir, [string]$Version, [bool]$RestoredProfile)
    Write-Host ""
    Write-Host "+======================================================================+" -ForegroundColor Green
    Write-Host "|  [OK] UPDATE SUCCESSFUL                                               |" -ForegroundColor Green
    Write-Host "+----------------------------------------------------------------------+" -ForegroundColor DarkGreen
    $targetStr = "|  Target Directory : $($TargetDir)"
    $versionStr = "|  Updated Version  : $($Version)"
    $profileStatus = if ($RestoredProfile) { "Preserved and Restored" } else { "Fresh Default Profile" }
    $profileStr = "|  User Profile     : $($profileStatus)"
    $statusStr = "|  Status           : Active and Ready"
    Write-Host ($targetStr.PadRight(71) + "|") -ForegroundColor White
    Write-Host ($versionStr.PadRight(71) + "|") -ForegroundColor White
    Write-Host ($profileStr.PadRight(71) + "|") -ForegroundColor White
    Write-Host ($statusStr.PadRight(71) + "|") -ForegroundColor Green
    Write-Host "+----------------------------------------------------------------------+" -ForegroundColor DarkGreen
    Write-Host "|  Quick Commands:                                                     |" -ForegroundColor White
    Write-Host "|   * In AI Chat UI : '/sast-status' or '/sast-audit file <path>'      |" -ForegroundColor Gray
    Write-Host "|   * In Terminal   : 'python control_plane.py status'                 |" -ForegroundColor Gray
    Write-Host "+======================================================================+" -ForegroundColor Green
    Write-Host ""
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
