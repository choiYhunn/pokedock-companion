"""Builds the PRIVATE gift sound pack from the owner's own files (never committed, never downloaded).

usage: python make_gift_pack.py <src_dir> <out_dir> [<test_pack_dir>]
  src_dir:  Documents\\프로젝트\\PokeDock_Private_Assets\\audio\\src  with files named after the cue:
            boot.wav|mp3, lid_open, lid_close, tap, confirm, pair, timer_done, alarm,
            cry_94, cry_393, ... (partner national dex numbers, see sound_manifest.json)
  out_dir:  ...\\PokeDock_Private_Assets\\audio\\out   (01_boot.mp3 .. 16_cry_385.mp3 + gift_pack.json)
  test_pack_dir: any cue without an owner file falls back to the synthetic TEST tone from here.
Every file must be shorter than its max_ms (WAV: exact; MP3: frame-header estimate) - the firmware
stops each sound at max_ms. Copy the result with copy_sounds_windows.ps1.
"""
import json
import pathlib
import shutil
import sys
import wave

HERE = pathlib.Path(__file__).resolve().parent
MAN = json.loads((HERE / "sound_manifest.json").read_text(encoding="utf8"))
BITRATES = {1: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320],     # MPEG-1 Layer III
            2: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160]}          # MPEG-2/2.5 Layer III
RATES = {3: [44100, 48000, 32000], 2: [22050, 24000, 16000], 0: [11025, 12000, 8000]}


def mp3_ms(path):
    """Duration by walking the MPEG audio frames (CBR or VBR). Skips an ID3v2 tag."""
    b = path.read_bytes()
    i = 0
    if b[:3] == b"ID3":
        i = 10 + ((b[6] & 0x7F) << 21 | (b[7] & 0x7F) << 14 | (b[8] & 0x7F) << 7 | (b[9] & 0x7F))
    ms, frames = 0.0, 0
    while i + 4 <= len(b):
        if b[i] != 0xFF or (b[i + 1] & 0xE0) != 0xE0:
            i += 1
            continue
        ver = (b[i + 1] >> 3) & 3          # 3 = MPEG-1, 2 = MPEG-2, 0 = MPEG-2.5
        layer = (b[i + 1] >> 1) & 3       # 1 = Layer III
        br_i, sr_i, pad = b[i + 2] >> 4, (b[i + 2] >> 2) & 3, (b[i + 2] >> 1) & 1
        if ver == 1 or layer != 1 or br_i in (0, 15) or sr_i == 3:
            i += 1
            continue
        br = BITRATES[1 if ver == 3 else 2][br_i] * 1000
        sr = RATES[ver][sr_i]
        spf = 1152 if ver == 3 else 576
        size = (spf // 8) * br // sr + pad
        ms += spf * 1000.0 / sr
        frames += 1
        i += max(size, 1)
    if not frames:
        raise ValueError(f"{path.name}: no MPEG Layer III frames found")
    return ms


def wav_ms(path):
    with wave.open(str(path), "rb") as w:
        return w.getnframes() * 1000.0 / w.getframerate()


def main(src, out, test=None):
    src, out = pathlib.Path(src), pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for old in list(out.glob("*.mp3")) + list(out.glob("*.wav")):
        old.unlink()
    report, problems = [], []
    for t in MAN["tracks"]:
        key = f"cry_{t['partner']}" if t["cue"] == "cry" else t["cue"]
        cand = [p for ext in ("mp3", "wav") for p in src.glob(f"{key}.{ext}")]
        origin = "owner"
        if not cand and test:
            cand = sorted(pathlib.Path(test).glob(f"{t['track']:02d}_*.wav"))
            origin = "TEST tone"
        if not cand:
            problems.append(f"track {t['track']} ({key}): no file")
            continue
        p = cand[0]
        ms = mp3_ms(p) if p.suffix.lower() == ".mp3" else wav_ms(p)
        if ms > t["max_ms"] - 100:
            problems.append(f"track {t['track']} ({key}): {ms:.0f} ms, must be under {t['max_ms'] - 100} ms - trim it")
            continue
        dst = out / f"{t['track']:02d}_{key}{p.suffix.lower()}"
        shutil.copyfile(p, dst)
        report.append({"track": t["track"], "file": dst.name, "from": origin, "ms": round(ms), "bytes": dst.stat().st_size})
    total = sum(r["bytes"] for r in report)
    if total > MAN["module"]["storage_bytes"] * 0.9:
        problems.append(f"pack is {total} bytes: more than 90 % of the 8 MB module flash")
    (out / "gift_pack.json").write_text(json.dumps({"kind": "PRIVATE gift pack", "total_bytes": total, "files": report,
                                                    "problems": problems}, ensure_ascii=False, indent=1), encoding="utf8")
    for r in report:
        print(f"{r['file']:24s} {r['ms']:5d} ms  {r['from']}")
    print("FAIL" if problems else "PASS", problems or f"{len(report)} files, {total} bytes -> {out}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
