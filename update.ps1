$ErrorActionPreference = "Stop"

$PluginName = "security-sast-guard"
$RepoOwner = "nguyenduydan"
$RepoName = "security-sast-guard-plugin"
$InstallDir = Join-Path $HOME ".gemini\config\plugins\$PluginName"

Write-Host "Updating $PluginName..." -ForegroundColor Cyan

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

Write-Host "Fetching latest release information..."
$ApiUrl = "https://api.github.com/repos/$RepoOwner/$RepoName/releases/latest"
try {
    $Release = Invoke-RestMethod -Uri $ApiUrl
    $ZipUrl = $Release.zipball_url
    Write-Host "Found release: $($Release.tag_name)"
} catch {
    Write-Host "Failed to fetch release info. Trying to download main branch zip..." -ForegroundColor Yellow
    $ZipUrl = "https://github.com/$RepoOwner/$RepoName/archive/refs/heads/main.zip"
}

try {
    Write-Host "Downloading $ZipUrl ..."
    Invoke-WebRequest -Uri $ZipUrl -OutFile $ZipPath

    Write-Host "Extracting..."
    Expand-Archive -Path $ZipPath -DestinationPath $ExtractPath -Force

    $ExtractedRootFolder = Get-ChildItem -Path $ExtractPath -Directory | Select-Object -First 1

    Write-Host "Removing old version..."
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
} finally {
    if (Test-Path $TempDir) {
        Remove-Item -Path $TempDir -Recurse -Force
    }
}
