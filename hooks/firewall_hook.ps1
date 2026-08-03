param(
    [Parameter(Mandatory=$true)]
    [string]$CommandText
)

$ErrorActionPreference = "Stop"
$ProfilePath = Join-Path $PSScriptRoot "..\profile.json"
if (-not (Test-Path $ProfilePath)) {
    Write-Output "ALLOW"
    exit 0
}

$profileData = Get-Content $ProfilePath -Raw | ConvertFrom-Json
$overlay = $profileData.command_firewall_overlay
$denyRules = $overlay.deny
$confirmRules = $overlay.confirm

$tokens = $null
$errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseInput($CommandText, [ref]$tokens, [ref]$errors)

$matchedDeny = $false
$matchedConfirm = $false

# Helper to check rules
function Check-Rules($text, $rules) {
    if ([string]::IsNullOrWhiteSpace($text)) { return $false }
    foreach ($rule in $rules) {
        if ($text -match $rule) { return $true }
    }
    return $false
}

# 1. Check raw command text
if (Check-Rules $CommandText $denyRules) { $matchedDeny = $true }
if (-not $matchedDeny -and (Check-Rules $CommandText $confirmRules)) { $matchedConfirm = $true }

# 2. Check AST elements (Commands and string arguments) to bypass simple obfuscation
if (-not $matchedDeny) {
    $elements = $ast.FindAll({$true}, $true)
    foreach ($node in $elements) {
        $textToCheck = $null
        
        if ($node -is [System.Management.Automation.Language.CommandAst]) {
            $textToCheck = $node.GetCommandName()
        } elseif ($node -is [System.Management.Automation.Language.StringConstantExpressionAst]) {
            $textToCheck = $node.Value
        }

        if ($null -ne $textToCheck) {
            if (Check-Rules $textToCheck $denyRules) {
                $matchedDeny = $true
                break
            }
            if (-not $matchedConfirm -and (Check-Rules $textToCheck $confirmRules)) {
                $matchedConfirm = $true
            }
        }
    }
}

if ($matchedDeny) {
    Write-Output "DENY"
} elseif ($matchedConfirm) {
    Write-Output "CONFIRM"
} else {
    Write-Output "ALLOW"
}
