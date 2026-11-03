"""Host tests for the sound-pack tools (no module, no real audio): test pack, gift pack rules, MP3 timing,
PowerShell copy tool syntax, and that no media file is tracked by git anywhere under v16/.

usage: python test_audio_tools.py <scratch_dir>
"""
import json
import pathlib
import shutil
import subprocess
import sys
import wave

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_gift_pack as G  # noqa: E402
import make_test_pack as T  # noqa: E402

tmp = pathlib.Path(sys.argv[1])
shutil.rmtree(tmp, ignore_errors=True)
tmp.mkdir(parents=True)
fails, n = [], 0


def check(name, cond, detail=""):
    global n
    n += 1
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  {detail}"))
    if not cond:
        fails.append(name)


# 1. synthetic test pack
T.main(tmp / "test")
meta = json.loads((tmp / "test" / "test_pack.json").read_text(encoding="utf8"))
check("test pack: 16 files in track order", [m["track"] for m in meta["files"]] == list(range(1, 17)))
check("test pack: every file below its max_ms", all(m["ms"] < t["max_ms"] - 100 for m, t in zip(meta["files"], T.MAN["tracks"])))

# 2. MP3 frame walk: 40 MPEG-1 Layer III frames, 128 kbit/s, 44.1 kHz = 40 x 26.12 ms
hdr = bytes([0xFF, 0xFB, 0x90, 0x00])
frame = hdr + bytes(417 - 4)
mp3 = tmp / "probe.mp3"
mp3.write_bytes(b"ID3\x03\x00\x00\x00\x00\x00\x05" + bytes(5) + frame * 40)
ms = G.mp3_ms(mp3)
check(f"mp3 duration {ms:.1f} ms = 1044.9 ms (ID3 skipped)", abs(ms - 40 * 1152 * 1000 / 44100) < 0.5, ms)

# 3. gift pack: owner files win, missing ones fall back to TEST tones, too-long files are refused
src = tmp / "src"
src.mkdir()
shutil.copy(mp3, src / "cry_94.mp3")
with wave.open(str(src / "boot.wav"), "wb") as w:
    w.setnchannels(1), w.setsampwidth(2), w.setframerate(8000)
    w.writeframes(bytes(2 * 8000))                       # 1.0 s < 2.4 s
rc = G.main(src, tmp / "out", tmp / "test")
gp = json.loads((tmp / "out" / "gift_pack.json").read_text(encoding="utf8"))
by = {f["track"]: f for f in gp["files"]}
check("gift pack builds", rc == 0 and len(gp["files"]) == 16, gp["problems"])
check("owner boot + Gengar cry used", by[1]["from"] == "owner" and by[9]["from"] == "owner" and by[9]["file"] == "09_cry_94.mp3")
check("missing cues fall back to TEST tones", by[2]["from"] == "TEST tone" and by[16]["from"] == "TEST tone")
with wave.open(str(src / "tap.wav"), "wb") as w:
    w.setnchannels(1), w.setsampwidth(2), w.setframerate(8000)
    w.writeframes(bytes(2 * 8000))                       # 1.0 s > tap limit 0.5 s
rc = G.main(src, tmp / "out2", tmp / "test")
gp = json.loads((tmp / "out2" / "gift_pack.json").read_text(encoding="utf8"))
check("too-long owner file refused", rc == 1 and any("track 4" in p for p in gp["problems"]), gp["problems"])

# 4. PowerShell copy tool parses under Windows PowerShell 5.1 (when available)
ps1 = HERE / "copy_sounds_windows.ps1"
check("copy tool saved with a UTF-8 BOM (PowerShell 5.1 reads Korean correctly)", ps1.read_bytes()[:3] == b"\xef\xbb\xbf")
if shutil.which("powershell.exe"):
    cmd = ("$e=$null; [void][System.Management.Automation.Language.Parser]::ParseFile('%s',[ref]$null,[ref]$e); "
           "if ($e.Count) { $e | %% { $_.Message }; exit 1 }" % str(ps1).replace("'", "''"))
    r = subprocess.run(["powershell.exe", "-NoProfile", "-Command", cmd], capture_output=True, text=True)
    check("copy tool parses (PS 5.1)", r.returncode == 0, r.stdout + r.stderr)

# 5. nothing media-like tracked anywhere under v16/ (the private gift pack must never reach git)
root = HERE.parent.parent
ls = subprocess.run(["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "."],
                    capture_output=True, text=True, check=True).stdout.split("\n")
media = []
for rel in filter(None, ls):
    p = root / rel
    if not p.is_file():
        continue
    head = p.open("rb").read(12)
    if p.suffix.lower() in (".mp3", ".wav", ".ogg", ".flac", ".m4a") or head.startswith((b"ID3", b"OggS", b"fLaC")) or \
            (head[:4] == b"RIFF" and head[8:12] == b"WAVE") or (len(head) > 1 and head[0] == 0xFF and (head[1] & 0xE0) == 0xE0 and p.suffix.lower() not in (".bin", ".png", ".jpg")):
        media.append(rel)
check("no audio file tracked or untracked-unignored under v16/", not media, media[:10])

print(f"{'FAIL' if fails else 'PASS'}: {n - len(fails)}/{n} audio tool checks")
sys.exit(1 if fails else 0)
