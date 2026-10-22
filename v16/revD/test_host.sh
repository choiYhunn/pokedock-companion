#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 optics_3d.py > optics_results.json
g++ -std=c++17 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer -I. test_host.cpp -o /tmp/ghost16_revd_test
/tmp/ghost16_revd_test
if command -v openscad >/dev/null; then
 openscad -o /tmp/ghost16_revd_shell.stl -D 'MODE="base"' revD_envelope.scad
 echo 'OpenSCAD shell output created; check watertight/fit before manufacturing'
fi
echo 'HOST VERIFIED ONLY; NOT AN ACTUAL WAVESHARE BOARD OR OTA QUALIFICATION'
