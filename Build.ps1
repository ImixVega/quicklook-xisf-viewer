#Requires -Version 5.1
[CmdletBinding()]
param(
    [string]$QuickLookCommonDll = ""
)
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$lib = Join-Path $root 'lib'
New-Item -ItemType Directory -Path $lib -Force | Out-Null
$destinationDll = Join-Path $lib 'QuickLook.Common.dll'

if ($QuickLookCommonDll) {
    if (-not (Test-Path -LiteralPath $QuickLookCommonDll)) {
        throw "Nie znaleziono pliku: $QuickLookCommonDll"
    }
    Copy-Item -LiteralPath $QuickLookCommonDll -Destination $destinationDll -Force
}
elseif (-not (Test-Path $destinationDll)) {
    $found = @()
    $running = @(Get-Process -Name QuickLook -ErrorAction SilentlyContinue)
    foreach ($process in $running) {
        try {
            if ($process.Path) {
                $base = Split-Path -Parent $process.Path
                $found += Join-Path $base 'QuickLook.Common.dll'
                $found += Join-Path $base 'QuickLook.Common\QuickLook.Common.dll'
            }
        } catch { }
    }
    $found += @( 
        "$env:LOCALAPPDATA\Programs\QuickLook\QuickLook.Common.dll",
        "$env:ProgramFiles\QuickLook\QuickLook.Common.dll",
        "${env:ProgramFiles(x86)}\QuickLook\QuickLook.Common.dll"
    )
    $match = $found | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
    if (-not $match) {
        throw @'
Nie znaleziono QuickLook.Common.dll.
Uruchom QuickLook i sprobuj ponownie.
Alternatywnie: .\Build.ps1 -QuickLookCommonDll "C:\sciezka\do\QuickLook.Common.dll"
'@
    }
    Copy-Item -LiteralPath $match -Destination $destinationDll -Force
    Write-Host "Biblioteka QuickLook: $match"
}

if (-not (Get-Command dotnet -ErrorAction SilentlyContinue)) {
    throw 'Brak dotnet SDK. Zainstaluj darmowy .NET SDK 8 (lub nowszy) ze strony dotnet.microsoft.com/download.'
}

Write-Host 'Kompilowanie XISF Viewer (.NET Framework 4.6.2)...'
& dotnet build (Join-Path $root 'QuickLook.Plugin.XisfViewer.csproj') `
    -c Release -p:Platform=AnyCPU --nologo
if ($LASTEXITCODE -ne 0) { throw 'Kompilacja nieudana. Wyslij nam blad z konsoli.' }

$output = Join-Path $root 'bin\Release'
$dll = Join-Path $output 'QuickLook.Plugin.XisfViewer.dll'
$meta = Join-Path $output 'QuickLook.Plugin.Metadata.config'
if (-not (Test-Path $dll) -or -not (Test-Path $meta)) {
    throw "Brakuje skompilowanych plikow: $dll / $meta"
}
$archive = Join-Path $root 'QuickLook.Plugin.XisfViewer.qlplugin'
if (Test-Path $archive) { Remove-Item $archive -Force }

# v0.2 uses the managed ZstdSharp.Port NuGet package. A .NET Framework
# QuickLook plugin has no automatic NuGet assembly probing; therefore the
# package must contain ALL runtime libraries (not just our plugin DLL).
$runtimeDlls = @(Get-ChildItem -LiteralPath $output -Filter '*.dll' -File | Where-Object {
    $_.Name -ne 'QuickLook.Common.dll'
})
if (-not ($runtimeDlls | Where-Object { $_.Name -eq 'ZstdSharp.dll' })) {
    throw @'
Nie znaleziono ZstdSharp.dll w folderze builda.
Sprawdz, czy pakiet NuGet ZstdSharp.Port zostal pobrany (dotnet restore).
'@
}
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::Open($archive, 'Create')
try {
    foreach ($file in $runtimeDlls) {
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $file.FullName, $file.Name) | Out-Null
    }
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $meta, 'QuickLook.Plugin.Metadata.config') | Out-Null
}
finally { $zip.Dispose() }
Write-Host ("Biblioteki w paczce: " + ($runtimeDlls.Name -join ', '))
Write-Host ''
Write-Host "GOTOWE: $archive" -ForegroundColor Green
Write-Host 'QuickLook: zaznacz .qlplugin -> Spacja -> Install -> zrestartuj QuickLook.'
