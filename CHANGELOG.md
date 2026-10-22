# Changelog

## 0.2.1 (2026-10-22; large Drizzle support tested on Windows 10)
- Handle XISF images larger than 1000 MiB using memory-mapped disk data.
- Stream ZSTD and zlib compression blocks instead of allocating entire decoded image.
- Bounded 12 GiB decoded-size limit, disk-space checks and cancellation.
- Retain original AutoSTF algorithm for ordinary-sized files.

## 0.2 (2026-10-22)
- Decode `zstd` / `zstd+sh` and uncompressed XISF subblocks.
- Bundle all required managed dependencies into the `.qlplugin` file.
- Added synthetic XISF fixtures and a verification script.
- Real-world PixInsight XISF opened successfully on Windows 10 (user testing).

## 0.1
- Initial QuickLook `.xisf` viewer with STF-like display stretch.
