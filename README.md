# QuickLook XISF Viewer

**Press Space to preview PixInsight `.xisf` files on Windows — with automatic STF-like stretch.**

[Instrukcja po polsku](README_PL.md) · [QuickLook](https://github.com/QL-Win/QuickLook) · MIT license

![Status](https://img.shields.io/badge/status-community%20prototype-blue) ![Windows](https://img.shields.io/badge/Windows-10%2F11%20x64-informational)

## Features

- QuickLook plugin for `.xisf` files (does not replace the FITS viewer).
- Automatic median/MAD screen stretch inspired by PixInsight STF; **the original file is never changed**.
- Mono and RGB, common UInt/Int and Float pixel formats, planar/interleaved layouts.
- Bayer CFA detection where `ColorFilterArray` is present.
- `zlib`, `lz4`, `lz4hc`, `zstd`, `+sh` (byte shuffle), and XISF subblocks.
- Preview up to 1800 px on the longer side, with asynchronous decoding.
- **v0.2.1:** Large Drizzle images (up to 12 GiB decoded) via memory-mapped I/O and streaming ZSTD/zlib to temporary disk storage. Requires adequate free TEMP space; large LZ4 blocks remain limited.

## Requirements

- Windows 10/11 (x64) and [QuickLook for Windows](https://github.com/QL-Win/QuickLook/releases).
- [.NET SDK 8 or later](https://dotnet.microsoft.com/download) to **build** the plugin.
- Internet access for NuGet restore during the first build; uses free `ZstdSharp.Port`.

## Build & install

Open **Windows PowerShell** in the repository directory while QuickLook is running:

```powershell
powershell -ExecutionPolicy Bypass -File .\Build.ps1
```

If the build cannot locate `QuickLook.Common.dll`, specify its path:

```powershell
powershell -ExecutionPolicy Bypass -File .\Build.ps1 -QuickLookCommonDll "C:\path\to\QuickLook.Common.dll"
```

Select the generated `QuickLook.Plugin.XisfViewer.qlplugin` in Windows Explorer, press **Space**, click **Install**, and fully restart QuickLook from its system tray icon. Select any `.xisf` and press Space again.

## Testing and compatibility

Real `.xisf` files saved by PixInsight (including ZSTD and large Drizzle stacks) were successfully opened with v0.2.1 on Windows 10 in October 2026. `tests/` contains **synthetic** XISF fixtures, not personal astrophotos. To verify the fixtures on a system with Python and the `zstd` CLI:

```bash
python tests/verify_test_xisf.py
```

This is a community prototype. The stretch is similar to PixInsight STF but is **not** a byte-for-byte implementation. The large-image streaming mode is still experimental. It does not support every XISF variant; in particular, multidimensional images, distributed XISF, and complex sample types are outside the current scope.

## Related project

[Windows XISF Thumbnails](https://github.com/ImixVega/windows-xisf-thumbnails) creates stretched **Explorer thumbnails**. This repository only implements the **Spacebar preview**.

## Credits and license

Maintainer: [ImixVega](https://github.com/ImixVega). MIT license (see [LICENSE.txt](LICENSE.txt)). Uses [ZstdSharp.Port](https://www.nuget.org/packages/ZstdSharp.Port/) (MIT). QuickLook is a separate open-source project.
