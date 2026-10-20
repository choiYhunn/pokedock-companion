#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
command -v python3 >/dev/null && command -v g++ >/dev/null
python3 "$root/tests/test_ghf_codec.py"
tmp="$(mktemp -d)";trap 'rm -rf "$tmp"' EXIT
python3 - "$root" "$tmp" <<'PY'
from pathlib import Path
import sys
from PIL import Image
sys.path.insert(0,str(Path(sys.argv[1])/'tools'))
from ghf_codec import pack
out=Path(sys.argv[2]);im=Image.new('RGBA',(64,64),(0,0,0,0))
for x in range(12,48):
    for y in range(7,53): im.putpixel((x,y),(120,35,169,255))
im.save(out/'in.png')
pack(out/'in.png',out/'pack','gengar',64,64,12,10)
PY
g++ -std=c++17 -O2 -Wall -Wextra -Werror -I "$root/firmware" "$root/tests/test_decoder.cpp" -o "$tmp/dec"
"$tmp/dec" "$tmp/pack/gengar_0000.ghf"
echo 'V16 GHF1 offline tests PASS'
