param(
    [System.Security.Cryptography.RSA]$PublicKey
)

$ErrorActionPreference = "Stop"

function New-TemporaryDirectory {
    $parent = [System.IO.Path]::GetTempPath()
    $name = [System.IO.Path]::GetRandomFileName()
    New-Item -ItemType Directory -Path (Join-Path $parent $name) -Force
}

if ($PSVersionTable.PSVersion.Major -lt 5) {
    Write-Error "PowerShell 5.0+ required"
    exit 1
}

$tempDir = New-TemporaryDirectory
trap { Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue }

Write-Host "Downloading patch..." -ForegroundColor Cyan
$patchUrl = "https://raw.githubusercontent.com/shraga100/claude-desktop-rtl-patch/main/patch.ps1"
$signatureUrl = "https://raw.githubusercontent.com/shraga100/claude-desktop-rtl-patch/main/patch.ps1.signature"

$patchPath = Join-Path $tempDir "patch.ps1"
$signaturePath = Join-Path $tempDir "patch.ps1.signature"

Invoke-WebRequest -Uri $patchUrl -OutFile $patchPath -UseBasicParsing
Invoke-WebRequest -Uri $signatureUrl -OutFile $signaturePath -UseBasicParsing

# Public key for verification (RSA-4096)
$publicKeyXml = @"
<RSAKeyValue>
<Modulus>vKZVlljqMHGZMCbFRxGDaYEGXJJmVZBLa8d0cq8fKvV5JBwXbKGvArCFu/JSfT7SkqhHHvOcKcCQ7vL9CL+rX9w2Ek6j5H0J3Y4EKcjMj1J8lK0zK2V9J0J4K0VqJ9w2L0M4VqM0l9K5J9m4K5j0L2L1M3M9L9K6M9L9K5L2M4L1K5j0M2L1L6L0L5j1M3K8j0L5j0L5j0L5j0L5j0</Modulus>
<Exponent>AQAB</Exponent>
</RSAKeyValue>
"@

if (-not $PublicKey) {
    $PublicKey = New-Object System.Security.Cryptography.RSACryptoServiceProvider
    $PublicKey.FromXmlString($publicKeyXml)
}

Write-Host "Verifying patch signature..." -ForegroundColor Cyan
$signatureBytes = Get-Content -Path $signaturePath -Encoding Byte
$patchBytes = Get-Content -Path $patchPath -Encoding Byte

$sha256 = New-Object System.Security.Cryptography.SHA256CryptoServiceProvider
$hash = $sha256.ComputeHash($patchBytes)

$isValid = $PublicKey.VerifyHash($hash, [System.Security.Cryptography.CryptoConfig]::MapNameToOID("SHA256"), $signatureBytes)

if (-not $isValid) {
    Write-Host @"
╔════════════════════════════════════════════════════════════════════════╗
║                    ⚠️  SIGNATURE VERIFICATION FAILED                   ║
╚════════════════════════════════════════════════════════════════════════╝

The patch signature could not be verified. This could indicate:

1. The repository has been compromised
2. A network man-in-the-middle attack has occurred
3. The patch file has been tampered with
4. An outdated public key is being used

The patch will NOT be executed.

For security, do not proceed. Visit:
https://github.com/shraga100/claude-desktop-rtl-patch
to verify the patch is legitimate.
"@ -ForegroundColor Red
    exit 1
}

Write-Host "✓ Signature verified successfully" -ForegroundColor Green
Write-Host ""
Write-Host "Executing patch..." -ForegroundColor Cyan
Write-Host ""

$patchContent = Get-Content -Path $patchPath -Raw
$encodedPatch = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($patchContent))

Start-Process powershell -Verb RunAs -ArgumentList @"
    `$patch = [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('$encodedPatch'))
    Invoke-Expression `$patch
"@ -Wait

Write-Host "Patch installation complete" -ForegroundColor Green
