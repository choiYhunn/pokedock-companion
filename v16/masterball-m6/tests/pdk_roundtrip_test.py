"""Round-trip test of the PDK1 sprite format: Python encoder (tools/make_assets.py) -> C decoder
(core/pdk_format.h compiled on the host). Uses synthetic geometric frames, never Pokémon art.
usage: python pdk_roundtrip_test.py <work_dir>
"""
import os
import pathlib
import random
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
import make_assets as M  # noqa: E402

work = pathlib.Path(sys.argv[1])
work.mkdir(parents=True, exist_ok=True)
random.seed(1024)
entries, expect = [], []
for dex, anim, w, h, n in [(94, 0, 96, 96, 4), (94, 5, 96, 96, 3), (385, 0, 80, 72, 2), (175, 7, 128, 128, 1)]:
    pal = [(0, 0, 0, 0)] + [(random.randrange(256), random.randrange(256), random.randrange(256), 255) for _ in range(40)]
    frames = []
    for k in range(n):
        cx, cy, r = w // 2 + k, h // 2 - k, min(w, h) // 3
        frames.append([0 if (x - cx) ** 2 + (y - cy) ** 2 > r * r else 1 + (x * 7 + y * 3 + k) % 40 for y in range(h) for x in range(w)])
    entries.append((dex, anim, w, h, 90 + anim, pal, frames))
    expect.append((dex, anim, w, h, frames, pal))
blob = M.build(entries)
(work / "pack.bin").write_bytes(blob)
with open(work / "expect.txt", "w") as f:
    for dex, anim, w, h, frames, pal in expect:
        for k, fr in enumerate(frames):
            px = [M.rgb565(*pal[i][:3]) if i else 0 for i in fr]
            f.write(f"{dex} {anim} {k} {w} {h} {sum(px) & 0xFFFFFFFF} {sum(1 for i in fr if i)}\n")

src = work / "pdk_decode_host.c"
src.write_text(r'''
#include <stdio.h>
#include <stdlib.h>
#include "pdk_format.h"
int main(int argc, char **argv) {
  if (argc < 2) return 2;
  FILE *f = fopen(argv[1], "rb"); fseek(f, 0, SEEK_END); long n = ftell(f); rewind(f);
  uint8_t *b = malloc(n); fread(b, 1, n, f); fclose(f);
  int count = pdk_header(b, (size_t)n); if (count < 0) { puts("BAD HEADER"); return 1; }
  uint8_t idx[128 * 128];
  for (int i = 0; i < count; i++) {
    pdk_entry_t e; pdk_entry(b, i, &e);
    const uint8_t *fr = b + e.frames_off;
    for (int k = 0; k < e.frames; k++) {
      uint32_t len = pdk_u32(fr);
      if (!pdk_rle_decode(fr + 4, len, idx, (size_t)e.w * e.h)) { printf("DECODE FAIL %d %d\n", e.dex, k); return 1; }
      uint32_t sum = 0, opaque = 0;
      for (int p = 0; p < e.w * e.h; p++) {
        const uint8_t *c = b + e.palette_off + 3 * idx[p];
        if (c[2]) { sum += pdk_u16(c); opaque++; }
      }
      printf("%d %d %d %d %d %u %u\n", e.dex, e.anim, k, e.w, e.h, sum, opaque);
      fr += 4 + len;
    }
  }
  /* corrupted stream must be rejected */
  uint8_t bad[4] = {200, 1, 200, 1};
  if (pdk_rle_decode(bad, 4, idx, 300)) { puts("OVERRUN NOT DETECTED"); return 1; }
  return 0;
}
''')
exe = work / ("pdk_decode_host.exe" if os.name == "nt" else "pdk_decode_host")
subprocess.run(["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", str(HERE.parent / "core"), str(src), "-o", str(exe)], check=True)
got = subprocess.run([str(exe), str(work / "pack.bin")], capture_output=True, text=True, check=True).stdout.split("\n")
want = (work / "expect.txt").read_text().split("\n")
ok = [g.strip() for g in got if g.strip()] == [w.strip() for w in want if w.strip()]
print(f"pack {len(blob)} bytes, {sum(len(e[6]) for e in entries)} frames;", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
