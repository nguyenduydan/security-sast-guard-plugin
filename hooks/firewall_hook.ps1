param(
    [Parameter(Mandatory=$true)]
    [string]$CommandText
)

$ErrorActionPreference = "Stop"

try {
    # 1. Check Profile & Checksum Integrity (Fail-Closed Guard)
    $RepoRoot = Split-Path $PSScriptRoot -Parent
    $ProfilePath = Join-Path $RepoRoot "profile.json"
    $ChecksumPath = Join-Path $RepoRoot ".profile.sha256"

    if (-not (Test-Path $ProfilePath)) {
        Write-Output "DENY"
        exit 1
    }

    # Compute current profile hash
    $hashAlgorithm = [System.Security.Cryptography.HashAlgorithm]::Create("SHA256")
    $profileBytes = [System.IO.File]::ReadAllBytes($ProfilePath)
    $hashBytes = $hashAlgorithm.ComputeHash($profileBytes)
    $currentHash = [System.BitConverter]::ToString($hashBytes).Replace("-", "").ToUpper()

    if (Test-Path $ChecksumPath) {
        $expectedHash = (Get-Content $ChecksumPath -Raw).Trim().ToUpper()
        if ($currentHash -ne $expectedHash) {
            # Tamper detected!
            Write-Output "DENY"
            exit 1
        }
    } else {
        # Auto-create checksum file on first run if missing
        Set-Content -Path $ChecksumPath -Value $currentHash -Encoding ASCII
    }

    # Parse profile JSON
    $profileJsonStr = [System.Text.Encoding]::UTF8.GetString($profileBytes)
    $profileData = $profileJsonStr | ConvertFrom-Json
    if (-not $profileData -or -not $profileData.command_firewall_overlay) {
        Write-Output "DENY"
        exit 1
    }

    $overlay = $profileData.command_firewall_overlay
    $denyRules = $overlay.deny
    $confirmRules = $overlay.confirm

    # 2. Deobfuscation Helpers
    function Remove-Escapes([string]$text) {
        if ([string]::IsNullOrEmpty($text)) { return $text }
        # Strip CMD caret escapes (e.g. r^m^ -> rm)
        $text = $text -replace '\^', ''
        # Strip PowerShell backtick escapes (e.g. i`e`x -> iex)
        $text = $text -replace '`', ''
        return $text
    }

    function Decode-Base64([string]$text) {
        if ([string]::IsNullOrEmpty($text)) { return $null }
        
        $decodedStrings = [System.Collections.Generic.List[string]]::new()

        # Pattern 1: -enc / -encodedcommand / -e followed by base64 string
        if ($text -match '-(?:e|enc|encodedcommand)\s+([A-Za-z0-9+/=]{4,})') {
            $b64Str = $Matches[1]
            try {
                $bytes = [System.Convert]::FromBase64String($b64Str)
                $decoded = [System.Text.Encoding]::Unicode.GetString($bytes).Replace("`0", "")
                if (-not [string]::IsNullOrWhiteSpace($decoded)) {
                    $decodedStrings.Add($decoded)
                }
            } catch {}
        }

        # Pattern 2: FromBase64String('...') or FromBase64String("...")
        $matchesB64 = [regex]::Matches($text, 'FromBase64String\s*\(\s*[''"]([A-Za-z0-9+/=]{4,})[''"]\s*\)')
        foreach ($m in $matchesB64) {
            $b64Str = $m.Groups[1].Value
            try {
                $bytes = [System.Convert]::FromBase64String($b64Str)
                $decodedUtf16 = [System.Text.Encoding]::Unicode.GetString($bytes).Replace("`0", "")
                $decodedUtf8 = [System.Text.Encoding]::UTF8.GetString($bytes).Replace("`0", "")
                if (-not [string]::IsNullOrWhiteSpace($decodedUtf16)) { $decodedStrings.Add($decodedUtf16) }
                if (-not [string]::IsNullOrWhiteSpace($decodedUtf8)) { $decodedStrings.Add($decodedUtf8) }
            } catch {}
        }

        return $decodedStrings
    }

    # Helper to check rules against a string
    function Check-Rules($text, $rules) {
        if ([string]::IsNullOrWhiteSpace($text)) { return $false }
        foreach ($rule in $rules) {
            if ($text -match $rule) { return $true }
        }
        return $false
    }

    # Prepare texts to evaluate
    $textsToTest = [System.Collections.Generic.List[string]]::new()
    
    # Raw command
    $textsToTest.Add($CommandText)

    # De-escaped command
    $deEscaped = Remove-Escapes $CommandText
    $textsToTest.Add($deEscaped)

    # Decoded Base64 commands
    $decodedList = Decode-Base64 $CommandText
    foreach ($dec in $decodedList) {
        $textsToTest.Add($dec)
        $textsToTest.Add((Remove-Escapes $dec))
    }

    # Also check de-escaped for base64
    $decodedDeEscapedList = Decode-Base64 $deEscaped
    foreach ($dec in $decodedDeEscapedList) {
        $textsToTest.Add($dec)
        $textsToTest.Add((Remove-Escapes $dec))
    }

    $matchedDeny = $false
    $matchedConfirm = $false

    # Evaluate all normalized/decoded string variations
    foreach ($candidate in $textsToTest) {
        if (Check-Rules $candidate $denyRules) {
            $matchedDeny = $true
            break
        }
        if (-not $matchedConfirm -and (Check-Rules $candidate $confirmRules)) {
            $matchedConfirm = $true
        }
    }

    # 3. Check AST elements for all text candidates
    if (-not $matchedDeny) {
        foreach ($candidate in $textsToTest) {
            if ([string]::IsNullOrWhiteSpace($candidate)) { continue }
            $tokens = [System.Management.Automation.Language.Token[]]@()
            $errors = [System.Management.Automation.Language.ParseError[]]@()
            try {
                $ast = [System.Management.Automation.Language.Parser]::ParseInput($candidate, [ref]$tokens, [ref]$errors)
                if ($ast) {
                    $elements = $ast.FindAll({$true}, $true)
                    foreach ($node in $elements) {
                        $textToCheck = $null
                        
                        if ($node -is [System.Management.Automation.Language.CommandAst]) {
                            $textToCheck = $node.GetCommandName()
                        } elseif ($node -is [System.Management.Automation.Language.StringConstantExpressionAst]) {
                            $textToCheck = $node.Value
                        }

                        if ($null -ne $textToCheck) {
                            $nodeClean = Remove-Escapes $textToCheck
                            if ((Check-Rules $textToCheck $denyRules) -or (Check-Rules $nodeClean $denyRules)) {
                                $matchedDeny = $true
                                break
                            }
                            if (-not $matchedConfirm -and ((Check-Rules $textToCheck $confirmRules) -or (Check-Rules $nodeClean $confirmRules))) {
                                $matchedConfirm = $true
                            }
                        }
                    }
                }
            } catch {}
            if ($matchedDeny) { break }
        }
    }

    if ($matchedDeny) {
        Write-Output "DENY"
    } elseif ($matchedConfirm) {
        Write-Output "CONFIRM"
    } else {
        Write-Output "ALLOW"
    }
} catch {
    # Fail-closed fallback
    Write-Output "DENY"
    exit 1
}

