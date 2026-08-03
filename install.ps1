$ErrorActionPreference = "Stop"

$PluginName = "security-sast-guard"
$RepoOwner = "nguyenduydan"
$RepoName = "security-sast-guard-plugin"
$InstallDir = Join-Path $HOME ".gemini\config\plugins\$PluginName"

Write-Host "Installing $PluginName..." -ForegroundColor Cyan

if (Test-Path $InstallDir) {
    Write-Host "Plugin is already installed at $InstallDir" -ForegroundColor Yellow
    Write-Host "Please use 'update.ps1' to update it, or 'remove.ps1' to uninstall." -ForegroundColor Yellow
    exit 1
}

Write-Host "Fetching latest release information..."
$ApiUrl = "https://api.github.com/repos/$RepoOwner/$RepoName/releases/latest"
try {
    $Release = Invoke-RestMethod -Uri $ApiUrl
    
    $ZipAsset = $Release.assets | Where-Object { $_.name -like "*.zip" } | Select-Object -First 1
    $ChecksumAsset = $Release.assets | Where-Object { $_.name -eq "checksums.txt" } | Select-Object -First 1
    
    if ($null -ne $ZipAsset) {
        $ZipUrl = $ZipAsset.browser_download_url
        $ChecksumUrl = if ($null -ne $ChecksumAsset) { $ChecksumAsset.browser_download_url } else { $null }
    } else {
        $ZipUrl = $Release.zipball_url
        $ChecksumUrl = $null
    }
    Write-Host "Found release: $($Release.tag_name)"
} catch {
    Write-Host "Failed to fetch release info. Trying to download main branch zip..." -ForegroundColor Yellow
    $ZipUrl = "https://github.com/$RepoOwner/$RepoName/archive/refs/heads/main.zip"
    $ChecksumUrl = $null
}

$TempDir = Join-Path ([System.IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $TempDir | Out-Null
$ZipPath = Join-Path $TempDir "plugin.zip"
$ExtractPath = Join-Path $TempDir "extracted"

try {
    Write-Host "Downloading $ZipUrl ..."
    Invoke-WebRequest -Uri $ZipUrl -OutFile $ZipPath

    if ($null -ne $ChecksumUrl) {
        Write-Host "Downloading checksums.txt..."
        $ChecksumPath = Join-Path $TempDir "checksums.txt"
        Invoke-WebRequest -Uri $ChecksumUrl -OutFile $ChecksumPath
        
        $ExpectedHashLine = (Get-Content $ChecksumPath) | Where-Object { $_ -match "\.zip$" } | Select-Object -First 1
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
    Expand-Archive -Path $ZipPath -DestinationPath $ExtractPath -Force

    # GitHub zipballs have a single root folder containing the repo name and commit hash
    $ExtractedRootFolder = Get-ChildItem -Path $ExtractPath -Directory | Select-Object -First 1

    Write-Host "Installing to $InstallDir ..."
    # Create parent plugins directory if not exists
    $PluginsDir = Split-Path $InstallDir
    if (-not (Test-Path $PluginsDir)) {
        New-Item -ItemType Directory -Path $PluginsDir | Out-Null
    }

    Move-Item -Path $ExtractedRootFolder.FullName -Destination $InstallDir -Force

    Write-Host ""
    Write-Host "Installation successful!" -ForegroundColor Green
    Write-Host "Plugin installed at: $InstallDir" -ForegroundColor Green
} finally {
    if (Test-Path $TempDir) {
        Remove-Item -Path $TempDir -Recurse -Force
    }
}
