"""Prepare the app-only images the gift flash tool writes at 0x10000, plus SHA256SUMS.txt.

usage: python tools/make_app_images.py [--mfg-zip <vendor ZIP>]
- Manufacturing m6-0.3.0: cut from the pinned merged images (vendor/MFG_PIN.json hashes are checked
  first; the ZIP, the pin and the merged files are only read, never changed):
    firmware/out/pokedock_m6_mfg_app.bin, pokedock_m6_mfg_app_rotate180.bin
- Gift m6-0.4.0-gift: cut from firmware/out/pokedock_m6_gift[_rotate180].bin (tools/idf_build_wsl.sh):
    firmware/out/pokedock_m6_gift_app.bin, pokedock_m6_gift_app_rotate180.bin
Every output passes tools/gift_image_check.py app; firmware/out/SHA256SUMS.txt lists them.
"""
import hashlib
import json
import pathlib
import subprocess
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "firmware/out"
PIN = json.loads((ROOT / "vendor/MFG_PIN.json").read_text(encoding="utf8"))
sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()  # noqa: E731


def extract(src, dst):
    r = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools/gift_image_check.py"), "extract-app", str(src), str(dst)],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"{src.name}: {r.stdout.strip()}")
    return json.loads(r.stdout)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if "--mfg-zip" in sys.argv:  # take the pinned merged images straight from the vendor ZIP
        z = pathlib.Path(sys.argv[sys.argv.index("--mfg-zip") + 1])
        if sha(z) != PIN["vendor_zip_sha256"]:
            sys.exit("vendor ZIP SHA-256 differs from vendor/MFG_PIN.json - stop")
        with zipfile.ZipFile(z) as zf:
            for n in zf.namelist():
                if n.endswith(("firmware/pokedock_m6_merged.bin", "firmware/pokedock_m6_merged_rotate180.bin")):
                    (OUT / pathlib.Path(n).name).write_bytes(zf.read(n))
    lines = []
    for merged, pin_key, app in (("pokedock_m6_merged.bin", "merged_bin_sha256", "pokedock_m6_mfg_app.bin"),
                                 ("pokedock_m6_merged_rotate180.bin", "rotate180_bin_sha256", "pokedock_m6_mfg_app_rotate180.bin")):
        src = OUT / merged
        if not src.exists():
            sys.exit(f"missing {src} (use --mfg-zip <vendor ZIP>)")
        if sha(src) != PIN[pin_key]:
            sys.exit(f"{merged} SHA-256 differs from vendor/MFG_PIN.json - this is not the manufacturing image")
        info = extract(src, OUT / app)
        lines.append(f"{info['sha256']}  {app}")
        print(f"{app}: m6 manufacturing app, {info['bytes']} B, built {info['date']} {info['time']}")
    for merged, app in (("pokedock_m6_gift.bin", "pokedock_m6_gift_app.bin"), ("pokedock_m6_gift_rotate180.bin", "pokedock_m6_gift_app_rotate180.bin")):
        src = OUT / merged
        if not src.exists():
            print(f"note: {merged} not built yet (tools/idf_build_wsl.sh{' rotate180' if 'rotate' in merged else ''})")
            continue
        info = extract(src, OUT / app)
        lines.append(f"{info['sha256']}  {app}")
        print(f"{app}: gift app, {info['bytes']} B, built {info['date']} {info['time']}")
    (OUT / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf8")
    print(f"wrote {OUT / 'SHA256SUMS.txt'} ({len(lines)} app images)")


if __name__ == "__main__":
    main()
