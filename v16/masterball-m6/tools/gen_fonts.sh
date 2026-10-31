#!/usr/bin/env bash
# Regenerate the LVGL fonts from Pretendard Bold (SIL OFL 1.1).
# usage: tools/gen_fonts.sh <dir containing node_modules with pretendard@1.3.9 and lv_font_conv@1.5.2>
# The UI font subset is extracted from every Hangul syllable used in firmware/main/ui.cpp, so
# adding a Korean string to the UI requires re-running this script.
set -euo pipefail
NODE_DIR=$1
HERE=$(cd "$(dirname "$0")/.." && pwd)
OUT=$HERE/firmware/main/fonts
TTF=$NODE_DIR/node_modules/pretendard/dist/public/static/alternative/Pretendard-Bold.ttf
cd "$NODE_DIR"
UI_SYMS=$(python3 -X utf8 -c "import sys,re;s=open(sys.argv[1],encoding='utf8').read();print(''.join(sorted(set(c for c in s if 0xAC00<=ord(c)<=0xD7A3))))" "$HERE/firmware/main/ui.cpp")
MSG_SYMS=$(python3 -X utf8 -c "print(''.join(chr(c) for c in range(0xAC00,0xD7A4) if len(chr(c).encode('euc-kr'))==2))")
conv() { npx --no-install lv_font_conv --font "$TTF" --size "$1" --bpp 4 --format lvgl --lv-include lvgl.h --no-compress "${@:3}" -o "$OUT/$2.c"; }
conv 210 pd_digits_210 -r 0x30-0x39
conv 140 pd_digits_140 -r 0x30-0x3A
conv 120 pd_digits_120 -r 0x30-0x3A
conv 80 pd_digits_80 -r 0x30-0x3A
conv 48 pd_ui_48 -r 0x20-0x7E --symbols "$UI_SYMS"
conv 40 pd_ui_40 -r 0x20-0x7E --symbols "$UI_SYMS"
conv 30 pd_msg_30 -r 0x20-0x7E --symbols "${MSG_SYMS}♥★♡~…·"
cp "$NODE_DIR/node_modules/pretendard/dist/LICENSE.txt" "$OUT/OFL-Pretendard.txt"
echo "fonts regenerated: UI syllables=${#UI_SYMS}"
