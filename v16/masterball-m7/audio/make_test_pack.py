"""Synthetic TEST sound pack for the DFR0534 (public, generated here; no recorded or third-party audio).

usage: python make_test_pack.py <out_dir>
Writes 01_boot.wav .. 16_cry_385.wav (22.05 kHz, 16-bit PCM mono, each shorter than its max_ms in
sound_manifest.json) plus test_pack.json with sizes and SHA-256. The "cry" tracks are plain
placeholder chirps, clearly not Pokémon voices: the gift pack replaces them (make_gift_pack.py).
"""
import hashlib
import json
import math
import pathlib
import struct
import sys
import wave

RATE = 22050
HERE = pathlib.Path(__file__).resolve().parent
MAN = json.loads((HERE / "sound_manifest.json").read_text(encoding="utf8"))


def tone(freqs_ms, vol=0.5, glide=False):
    """freqs_ms: list of (start_hz, end_hz, ms); 0 Hz = silence. 5 ms fades avoid clicks."""
    out = []
    phase = 0.0
    for f0, f1, ms in freqs_ms:
        n = int(RATE * ms / 1000)
        fade = min(int(RATE * 0.005), n // 2)
        for i in range(n):
            f = f0 + (f1 - f0) * i / max(n - 1, 1) if glide or f0 != f1 else f0
            env = min(1.0, i / fade if fade else 1.0, (n - 1 - i) / fade if fade else 1.0)
            if f > 0:
                phase += 2 * math.pi * f / RATE
                s = math.sin(phase) * 0.8 + math.sin(2 * phase) * 0.2
            else:
                s = 0.0
            out.append(int(max(-1.0, min(1.0, s * vol * env)) * 32767))
    return out


SOUNDS = {
    "boot": tone([(523, 523, 180), (0, 0, 40), (784, 784, 320)]),
    "lid_open": tone([(440, 880, 420)], glide=True),
    "lid_close": tone([(880, 440, 380)], glide=True, vol=0.4),
    "tap": tone([(1320, 1320, 70)], vol=0.4),
    "confirm": tone([(988, 988, 80), (0, 0, 50), (1319, 1319, 110)], vol=0.45),
    "pair": tone([(659, 659, 120), (784, 784, 120), (988, 988, 220)]),
    "timer_done": tone([(523, 523, 160), (659, 659, 160), (784, 784, 160), (1047, 1047, 520)]),
    "alarm": tone([(1760, 1760, 140), (0, 0, 90), (1760, 1760, 140), (0, 0, 90), (2093, 2093, 240), (0, 0, 800)], vol=0.55),
}


def cry_placeholder(k):
    base = 600 + 90 * k
    return tone([(base, base * 1.5, 160), (base * 1.5, base * 1.2, 220)], glide=True, vol=0.45)


def main(out):
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.wav"):
        old.unlink()
    meta = []
    for t in MAN["tracks"]:
        k = t["track"]
        if t["cue"] == "cry":
            name, pcm = f"{k:02d}_cry_{t['partner']}.wav", cry_placeholder(k - 9)
        else:
            name, pcm = f"{k:02d}_{t['cue']}.wav", SOUNDS[t["cue"]]
        ms = len(pcm) * 1000 / RATE
        assert ms < t["max_ms"] - 100, f"{name}: {ms:.0f} ms is not below max_ms {t['max_ms']}"
        p = out / name
        with wave.open(str(p), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes(struct.pack(f"<{len(pcm)}h", *pcm))
        data = p.read_bytes()
        meta.append({"track": k, "file": name, "ms": round(ms), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    total = sum(m["bytes"] for m in meta)
    assert total < MAN["module"]["storage_bytes"] * 0.8, "pack does not fit the module flash"
    (out / "test_pack.json").write_text(json.dumps({"kind": "TEST (synthetic tones)", "total_bytes": total, "files": meta}, indent=1),
                                        encoding="utf8")
    print(f"PASS: {len(meta)} files, {total} bytes ({total / MAN['module']['storage_bytes'] * 100:.1f} % of 8 MB) -> {out}")


if __name__ == "__main__":
    main(sys.argv[1])
