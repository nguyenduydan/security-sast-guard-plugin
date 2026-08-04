$ErrorActionPreference = "Stop"

$ProgressPreference = "SilentlyContinue"

function Write-Stage {
    param([string]$Message, [int]$Percent)
    $width = 30
    $filled = [math]::Floor($width * $Percent / 100)
    $bar = ("█" * $filled) + ("░" * ($width - $filled))
    $line = "[$bar] $Percent% $Message"
    Write-Host ("`r{0,-90}" -f $line) -NoNewline -ForegroundColor Cyan
}
function Write-StageDone { param([string]$Message); Write-Host ("`r{0,-90}" -f "[OK] $Message") -ForegroundColor Green }

$PluginName = "security-sast-guard"
$RepoOwner = "nguyenduydan"
$RepoName = "security-sast-guard-plugin"
$InstallDir = Join-Path $HOME ".gemini\config\plugins\$PluginName"

Clear-Host
Write-Host "==============================================" -ForegroundColor DarkCyan
$SastLogo = @(
    "███████╗ █████╗ ███████╗████████╗",
    "██╔════╝██╔══██╗██╔════╝╚══██╔══╝",
    "███████╗███████║███████╗   ██║   ",
    "╚════██║██╔══██║╚════██║   ██║   ",
    "███████║██║  ██║███████║   ██║   ",
    "╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝   "
)
foreach ($Line in $SastLogo) {
    Write-Host $Line -ForegroundColor Cyan
}
Write-Host "          SECURITY SAST GUARD" -ForegroundColor White
Write-Host "               UPDATER" -ForegroundColor DarkCyan
Write-Host "==============================================" -ForegroundColor DarkCyan
Write-Host "Target: $InstallDir" -ForegroundColor Gray
Write-Host ""

if (-not (Test-Path $InstallDir)) {
    Write-Host "Plugin is not installed at $InstallDir" -ForegroundColor Red
    Write-Host "Please use 'install.ps1' to install it first." -ForegroundColor Red
    exit 1
}

$TempDir = Join-Path ([System.IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $TempDir | Out-Null
$ZipPath = Join-Path $TempDir "plugin.zip"
$ExtractPath = Join-Path $TempDir "extracted"
$BackupPath = Join-Path $TempDir "profile.json.bak"
$ProfilePath = Join-Path $InstallDir "profile.json"

# 1. Backup user profile if exists
$HasProfile = $false
if (Test-Path $ProfilePath) {
    Write-Host "Backing up user profile.json..."
    Copy-Item -Path $ProfilePath -Destination $BackupPath -Force
    $HasProfile = $true
}

Write-Host "Fetching latest release information from GitHub API..."
try {
    Write-Stage "Downloading latest release" 20
    $Release = Invoke-RestMethod -Uri "https://api.github.com/repos/$RepoOwner/$RepoName/releases/latest"
    $ZipAsset = $Release.assets | Where-Object { $_.name -like "*.zip" } | Select-Object -First 1
    $ChecksumAsset = $Release.assets | Where-Object { $_.name -eq "checksums.txt" } | Select-Object -First 1
    if (-not $ZipAsset) {
        Write-Host "No release ZIP asset found; falling back to GitHub source archive." -ForegroundColor Yellow
        $ZipAsset = [pscustomobject]@{
            name = "$($Release.tag_name).zip"
            browser_download_url = $Release.zipball_url
        }
    }
    Write-Host "Found release: $($Release.tag_name)" -ForegroundColor Green
    Invoke-WebRequest -Uri $ZipAsset.browser_download_url -OutFile (Join-Path $TempDir $ZipAsset.name)
    if ($ChecksumAsset) { Invoke-WebRequest -Uri $ChecksumAsset.browser_download_url -OutFile (Join-Path $TempDir $ChecksumAsset.name) }
    $ZipPath = Join-Path $TempDir $ZipAsset.name
    $ChecksumPath = Join-Path $TempDir "checksums.txt"

    if (Test-Path $ChecksumPath) {
        Write-Stage "Verifying package integrity" 45
        $ExpectedHashLine = Get-Content $ChecksumPath | Where-Object { $_ -match [regex]::Escape((Split-Path $ZipPath -Leaf)) } | Select-Object -First 1
        if ($ExpectedHashLine) {
            $ExpectedHash = ($ExpectedHashLine -split '\s+')[0].ToUpper()
            $ActualHash = (Get-FileHash -Path $ZipPath -Algorithm SHA256).Hash.ToUpper()
            if ($ExpectedHash -ne $ActualHash) {
                throw "Checksum mismatch! Expected: $ExpectedHash, Actual: $ActualHash. The file might be corrupted or compromised."
            }
            Write-Host "Checksum verified successfully." -ForegroundColor Green
        }
    }



    Write-Stage "Extracting and replacing runtime files" 70
    Expand-Archive -Path $ZipPath -DestinationPath $ExtractPath -Force

    $ExtractedRootFolder = Get-ChildItem -Path $ExtractPath -Directory | Select-Object -First 1

    Write-Host "Removing old version..."
    # The script is commonly launched from $InstallDir. Move out first so
    # Windows does not keep the directory as the process working directory.
    Set-Location -Path $TempDir
    Remove-Item -Path $InstallDir -Recurse -Force

    Write-Host "Installing new version to $InstallDir ..."
    Move-Item -Path $ExtractedRootFolder.FullName -Destination $InstallDir -Force

    # 2. Restore user profile if exists
    if ($HasProfile) {
        Write-Host "Restoring user profile.json..."
        Copy-Item -Path $BackupPath -Destination $ProfilePath -Force
    }

    Write-Host ""
    Write-Host "Update successful!" -ForegroundColor Green
    Write-Host "Plugin updated at: $InstallDir" -ForegroundColor Green
    Write-StageDone "Update complete"
} finally {
    # Leave the temporary directory before deleting it.
    Set-Location -Path ([System.IO.Path]::GetTempPath())
    if (Test-Path $TempDir) {
        Remove-Item -Path $TempDir -Recurse -Force
    }
}

