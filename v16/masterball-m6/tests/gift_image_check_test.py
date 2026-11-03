"""Real-image checks for the gift flash path (run after firmware_build).

- the pinned manufacturing merged images still have the MFG_PIN SHA-256 (never rebuilt or edited)
- app-only images derived by tools/make_app_images.py are valid and equal merged[0x10000:]
- manufacturing and gift builds carry the SAME partition table, equal to firmware/partitions.csv,
  and the same flash mode/frequency/size header bytes and IDF version (the ball's bootloader stays)
- merged images and non-images are refused as app images
usage: python gift_image_check_test.py
"""
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "firmware/out"
CHK = ROOT / "tools/gift_image_check.py"
PIN = json.loads((ROOT / "vendor/MFG_PIN.json").read_text(encoding="utf8"))
fail, n = [], 0


def check(name, cond, detail=""):
    global n
    n += 1
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  {detail}"))
    if not cond:
        fail.append(name)


def run(*a):
    r = subprocess.run([sys.executable, "-X", "utf8", str(CHK), *map(str, a)], capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()  # noqa: E731
mfg, mfg_rot = OUT / "pokedock_m6_merged.bin", OUT / "pokedock_m6_merged_rotate180.bin"
check("manufacturing merged image = MFG_PIN", mfg.exists() and sha(mfg) == PIN["merged_bin_sha256"])
check("manufacturing rotate180 image = MFG_PIN", mfg_rot.exists() and sha(mfg_rot) == PIN["rotate180_bin_sha256"])
r = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools/make_app_images.py")], capture_output=True, text=True)
check("make_app_images.py", r.returncode == 0, r.stdout + r.stderr)
check("manufacturing images untouched by make_app_images", sha(mfg) == PIN["merged_bin_sha256"] and sha(mfg_rot) == PIN["rotate180_bin_sha256"])
sums = OUT / "SHA256SUMS.txt"
pairs = [("pokedock_m6_merged.bin", "pokedock_m6_mfg_app.bin"), ("pokedock_m6_merged_rotate180.bin", "pokedock_m6_mfg_app_rotate180.bin"),
         ("pokedock_m6_gift.bin", "pokedock_m6_gift_app.bin"), ("pokedock_m6_gift_rotate180.bin", "pokedock_m6_gift_app_rotate180.bin")]
tables, heads = {}, {}
for merged, app in pairs:
    m, a = OUT / merged, OUT / app
    if not m.exists():
        check(f"{merged} present", False, "build it with tools/idf_build_wsl.sh [rotate180]")
        continue
    code, out = run("app", a, "--sums", sums)
    check(f"{app}: valid app image listed in SHA256SUMS", code == 0, out)
    mb = m.read_bytes()
    check(f"{app} == {merged}[0x10000:]", a.read_bytes() == mb[0x10000:])
    tables[merged] = mb[0x8000:0x8C00]
    heads[merged] = (a.read_bytes()[2:4], json.loads(out)["idf"] if code == 0 else None)
    code, out = run("app", m)
    check(f"{merged} refused as an app (merged)", code == 1 and "MERGED" in out, out)
for merged, app in pairs:      # FirstInstall input: whole merged image, app identified by content
    m = OUT / merged
    if m.exists():
        code, out = run("merged", m, "--sums", sums)
        check(f"{merged}: valid merged image carrying {app}", code == 0 and json.loads(out)["app_name"] == app, out)
code, out = run("merged", OUT / "pokedock_m6_gift_app.bin", "--sums", sums)
check("app-only image refused as a merged image", code == 1, out)
tp = OUT / "_ptable_check.bin"
for merged, t in tables.items():
    tp.write_bytes(t)
    code, out = run("ptable", tp)
    check(f"{merged}: partition table == firmware/partitions.csv", code == 0, out)
check("all builds share one partition table (byte-identical)", len(set(tables.values())) == 1)
check("all apps share flash header bytes and IDF (bootloader compatible)", len(set(heads.values())) == 1, str(heads))
tp.unlink(missing_ok=True)
code, out = run("app", ROOT / "tools/make_assets.py")
check("non-image refused", code == 1)
print(f"{'FAIL' if fail else 'PASS'}: {n - len(fail)}/{n} real-image checks")
sys.exit(1 if fail else 0)
