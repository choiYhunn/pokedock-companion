#!/usr/bin/env bash
# Build the M6 firmware in WSL and leave ONE merged image for flashing from Windows.
# usage (in WSL, from the repo):  bash v16/masterball-m6/tools/idf_build_wsl.sh [rotate180]
# output: v16/masterball-m6/firmware/out/pokedock_m6_merged.bin  (flash at 0x0)
set -euo pipefail
SRC="$(cd "$(dirname "$0")/.." && pwd)"
DST=~/m6build
rm -rf "$DST/core" "$DST/firmware/main" && mkdir -p "$DST/firmware"
cp -r "$SRC/core" "$DST/"
cp -r "$SRC/firmware/main" "$SRC/firmware/CMakeLists.txt" "$SRC/firmware/partitions.csv" \
      "$SRC/firmware/sdkconfig.defaults" "$SRC/firmware/dependencies.lock" "$DST/firmware/"
export PATH="$(dirname "$(~/.local/bin/uv python find 3.11)"):$PATH"
. ~/m6idf/esp-idf/export.sh >/dev/null
cd "$DST/firmware"
if [ "${1:-}" = "rotate180" ]; then
  rm -f sdkconfig && echo "CONFIG_PD_SCREEN_ROTATION_180=y" >> sdkconfig.defaults
fi
idf.py set-target esp32s3 >/dev/null
idf.py build
(cd build && python -m esptool --chip esp32s3 merge_bin -o pokedock_m6_merged.bin @flash_args)
mkdir -p "$SRC/firmware/out"
cp build/pokedock_m6_merged.bin "$SRC/firmware/out/"
sha256sum "$SRC/firmware/out/pokedock_m6_merged.bin"
echo "flash from Windows: tools\\flash_windows.ps1 -Port COMx"
