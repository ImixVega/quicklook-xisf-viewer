# QuickLook XISF Viewer — wersja 0.2.1

**Darmowy podgląd plików `.xisf` ze stretchem pod Spacją w Eksploratorze Windows.**

Projekt wykorzystuje QuickLook; działa niezależnie od istniejącej wtyczki FITS. Prawdziwe pliki XISF z kompresją ZSTD zapisane przez PixInsight zostały otwarte poprawnie podczas testów na Windows 10 (październik 2026).

## Pobierz gotową wtyczkę

**[QuickLook XISF Viewer v0.2.1 — pobierz .qlplugin](https://github.com/ImixVega/quicklook-xisf-viewer/releases/download/v0.2.1/QuickLook.Plugin.XisfViewer.qlplugin)** · [Opis wydania](https://github.com/ImixVega/quicklook-xisf-viewer/releases/tag/v0.2.1)

Uruchom QuickLook, zaznacz pobrany plik `.qlplugin` w Eksploratorze, naciśnij **Spację**, wybierz **Install** i zamknij oraz uruchom ponownie QuickLook. **Gotowa wersja nie wymaga .NET SDK ani samodzielnej kompilacji.**

## Co działa

- Liniowe obrazy mono i RGB z automatycznym rozciąganiem zbliżonym do STF (mediana/MAD).
- Popularne formaty próbek całkowitych i zmiennoprzecinkowych, CFA/Bayer.
- `zlib`, `lz4`, `lz4hc`, `zstd`, także `+sh` i podbloki.
- Pliki wejściowe pozostają niezmienione.

## Instalacja

1. Zainstaluj [QuickLook](https://github.com/QL-Win/QuickLook/releases) i [.NET SDK 8+](https://dotnet.microsoft.com/download).
2. Uruchom QuickLook. W katalogu kodu źródłowego wykonaj:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\Build.ps1
   ```

3. Jeśli nie znaleziono `QuickLook.Common.dll`, podaj jego ścieżkę: `-QuickLookCommonDll "C:\sciezka\QuickLook.Common.dll"`.
4. Zaznacz utworzony plik `QuickLook.Plugin.XisfViewer.qlplugin`, naciśnij **Spację**, kliknij **Install**.
5. Zamknij QuickLook przez `Quit` w zasobniku systemowym i uruchom ponownie.
6. Zaznacz `.xisf` → **Spacja**.

Budowanie wymaga jednorazowego pobrania bezpłatnej zależności `ZstdSharp.Port` przez NuGet. To prototyp: nie każda odmiana XISF jest obsługiwana, a stretch nie jest identyczny z PixInsight.

Do miniaturek w folderze służy osobny projekt: [windows-xisf-thumbnails](https://github.com/ImixVega/windows-xisf-thumbnails).

**Licencja:** MIT ([LICENSE.txt](LICENSE.txt)).


## Wersja 0.2.1: duże obrazy Drizzle (testowane w Windows 10)

Gdy obraz po dekompresji ma ponad 1000 MiB, zamiast alokować jedną tablicę w RAM,
wtyczka korzysta z pliku pamięci mapowanej.

- Limit rozmiaru obrazu po dekompresji: 12 GiB.
- Bez kompresji: QuickLook mapuje istniejący plik bez tworzenia kopii.
- ZSTD/ZSTD+SH oraz zlib: dane są dekompresowane strumieniowo do dysku TEMP.
- W miniaturkach Eksploratora źródłem jest IStream, dlatego również dane nieskompresowane
  mogą wymagać pliku tymczasowego.
- Konieczna jest dostępna ilość miejsca na dysku TEMP co najmniej rozmiar obrazu po rozpakowaniu
  plus zapas 256 MiB.
- LZ4/LZ4HC: przy bardzo dużych pojedynczych subblokach (>128 MiB) nadal występuje ograniczenie.
- Tryb dużych obrazów jest nadal eksperymentalny, ale przeszedł test na rzeczywistym M42 Drizzle w Windows 10.
- Dane źródłowe XISF nie są modyfikowane.
