#!/usr/bin/env bash
# Download the vendor references needed by `tests/run_all.sh --strict` into vendor_cache/ (git-ignored)
# and extract the official board STEP into per-component STLs. Nothing vendor-owned is committed.
# usage: PY=<python with OCP/cadquery-ocp> bash tools/fetch_vendor_refs.sh
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-python}
C=vendor_cache
mkdir -p "$C"
WS=https://files.waveshare.com/wiki/ESP32-S3-Touch-AMOLED-1.43
[ -f "$C/schematic.pdf" ] || curl -fsSL -o "$C/schematic.pdf" "$WS/ESP32-S3-Touch-AMOLED-1.43-Schematic.pdf"
[ -f "$C/3d.zip" ] || curl -fsSL -o "$C/3d.zip" "$WS/ESP32-S3-Touch-AMOLED-1.43-3DFile.zip"
[ -f "$C/adafruit4090.sch" ] || curl -fsSL -o "$C/adafruit4090.sch" \
  "https://raw.githubusercontent.com/adafruit/Adafruit-USB-C-Downstream-Breakout/master/Adafruit%20USB%20Type%20C%20Downstream%20Breakout%20rev%20B.sch"
rm -rf "$C/3d" && mkdir -p "$C/3d" && (cd "$C/3d" && unzip -q -o ../3d.zip)
STEP=$(find "$C/3d" -name "ESP32-S3-Touch-AMOLED-1_43.stp" | head -1)
[ -n "$STEP" ] || { echo "board STEP not found in 3d.zip"; exit 1; }
if [ ! -f "$C/parts/parts.json" ]; then
  rm -rf "$C/parts"
  "$PY" -I -X utf8 tools/vendor_step_to_parts.py "$STEP" "$C/parts" > "$C/parts.log" 2>&1
fi
n=$(ls "$C/parts"/*.stl | wc -l)
sha256sum "$C/schematic.pdf" "$STEP" "$C/adafruit4090.sch" > "$C/SHA256SUMS"
echo "vendor_cache ready: $n board component meshes"
cat "$C/SHA256SUMS"
