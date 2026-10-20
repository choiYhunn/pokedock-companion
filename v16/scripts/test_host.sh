#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../"
node v16/tests/engine.test.cjs
node v16/tests/assets.test.cjs
if python3 -c "import PIL" 2>/dev/null; then bash v16/scripts/test_host_codec.sh; else echo "Pillow missing; GHF1 tests SKIPPED, use python3 -m pip install Pillow"; fi
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
g++ -std=c++17 -O2 -Wall -Wextra -Werror -I v16/firmware v16/firmware/ghost_core_test.cpp -o "$tmp/ghost16"
"$tmp/ghost16"
if command -v openscad >/dev/null; then
 openscad -o "$tmp/ghost_v16_base.stl" -D 'MODE="base"' v16/cad/ghost_v16_concept.scad
 test -s "$tmp/ghost_v16_base.stl"
 echo "V16 mock CAD export PASS (NOT print fit approval)"
else echo "OpenSCAD not installed; CAD export SKIPPED"; fi
echo "V16 host-only checks complete; real display/optics/OTA UNTESTED"
