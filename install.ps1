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
Write-Host "              INSTALLER" -ForegroundColor DarkCyan
Write-Host "==============================================" -ForegroundColor DarkCyan
Write-Host "Target: $InstallDir" -ForegroundColor Gray
Write-Host ""

if (Test-Path $InstallDir) {
    Write-Host "Plugin is already installed at $InstallDir" -ForegroundColor Yellow
    Write-Host "Please use 'update.ps1' to update it, or 'remove.ps1' to uninstall." -ForegroundColor Yellow
    exit 1
}

Write-Host "Fetching latest release information using GitHub CLI..."

$TempDir = Join-Path ([System.IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $TempDir | Out-Null
$ExtractPath = Join-Path $TempDir "extracted"

try {
    Write-Progress -Activity "Installing Security SAST Guard" -Status "Downloading latest release" -PercentComplete 20
    # Download zip and checksums using gh CLI (handles authentication automatically)
    gh release download --repo "$RepoOwner/$RepoName" --pattern "*.zip" --dir $TempDir
    gh release download --repo "$RepoOwner/$RepoName" --pattern "checksums.txt" --dir $TempDir
    
    # Get the downloaded zip file path
    $ZipPath = (Get-ChildItem -Path $TempDir -Filter "*.zip" | Select-Object -First 1).FullName
    $ChecksumPath = Join-Path $TempDir "checksums.txt"

    if (Test-Path $ChecksumPath) {
        Write-Progress -Activity "Installing Security SAST Guard" -Status "Verifying package integrity" -PercentComplete 45
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
    Write-Progress -Activity "Installing Security SAST Guard" -Status "Extracting runtime files" -PercentComplete 70
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
    Write-Progress -Activity "Installing Security SAST Guard" -Status "Installation complete" -PercentComplete 100 -Completed

    Write-Host ""
    Write-Host "Installation successful!" -ForegroundColor Green
    Write-Host "Plugin installed at: $InstallDir" -ForegroundColor Green
} finally {
    if (Test-Path $TempDir) {
        Remove-Item -Path $TempDir -Recurse -Force
    }
}
