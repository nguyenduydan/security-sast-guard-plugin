$ErrorActionPreference = "Stop"

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

Write-Host "Fetching latest release information using GitHub CLI..."
try {
    Write-Progress -Activity "Updating Security SAST Guard" -Status "Downloading latest release" -PercentComplete 20
    # Download zip and checksums using gh CLI (handles authentication automatically)
    gh release download --repo "$RepoOwner/$RepoName" --pattern "*.zip" --dir $TempDir
    gh release download --repo "$RepoOwner/$RepoName" --pattern "checksums.txt" --dir $TempDir
    
    # Get the downloaded zip file path
    $ZipPath = (Get-ChildItem -Path $TempDir -Filter "*.zip" | Select-Object -First 1).FullName
    $ChecksumPath = Join-Path $TempDir "checksums.txt"

    if (Test-Path $ChecksumPath) {
        Write-Progress -Activity "Updating Security SAST Guard" -Status "Verifying package integrity" -PercentComplete 45
        if ($ExpectedHashLine) {
            $ExpectedHash = ($ExpectedHashLine -split '\s+')[0].ToUpper()
            $ActualHash = (Get-FileHash -Path $ZipPath -Algorithm SHA256).Hash.ToUpper()
            if ($ExpectedHash -ne $ActualHash) {
                throw "Checksum mismatch! Expected: $ExpectedHash, Actual: $ActualHash. The file might be corrupted or compromised."
            }
            Write-Host "Checksum verified successfully." -ForegroundColor Green
        }
    }



    Write-Host "Extracting..."
    Write-Progress -Activity "Updating Security SAST Guard" -Status "Replacing runtime files" -PercentComplete 70
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
    Write-Progress -Activity "Updating Security SAST Guard" -Status "Update complete" -PercentComplete 100 -Completed
} finally {
    # Leave the temporary directory before deleting it.
    Set-Location -Path ([System.IO.Path]::GetTempPath())
    if (Test-Path $TempDir) {
        Remove-Item -Path $TempDir -Recurse -Force
    }
}
