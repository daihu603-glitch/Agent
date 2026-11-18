$ErrorActionPreference = 'Stop'
$output = Join-Path $PSScriptRoot 'outputs'
New-Item -ItemType Directory -Force $output | Out-Null
$apk = Join-Path $output 'smoke.apk'
[System.IO.File]::WriteAllText($apk, 'offline-android-build-smoke')
Write-Output "SMOKE BUILD SUCCESS: $apk"
