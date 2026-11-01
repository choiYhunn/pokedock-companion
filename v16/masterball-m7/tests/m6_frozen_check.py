"""Guard: the M7 branch must not change the M6 manufacturing deliverables.

usage: python m6_frozen_check.py [vendor_zip]
- vendor/MFG_PIN.json hashes still match the manufacturing merged images in ../masterball-m6/firmware/out
- the vendor ZIP (if given / found) still has the pinned SHA-256
- against the PR #23 head (origin/feature/m6-gift-content-20261031) this branch changes nothing under
  masterball-m6/{cad,electronics,vendor,procurement} (CAD, circuit, BOM, SOP) and never touches PR #21 files there
"""
import hashlib
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
M6 = HERE.parent / "masterball-m6"
fails, n = [], 0


def check(name, cond, detail=""):
    global n
    n += 1
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  {detail}"))
    if not cond:
        fails.append(name)


sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()  # noqa: E731
pin = json.loads((M6 / "vendor/MFG_PIN.json").read_text(encoding="utf8"))
for key, f in (("merged_bin_sha256", "pokedock_m6_merged.bin"), ("rotate180_bin_sha256", "pokedock_m6_merged_rotate180.bin")):
    p = M6 / "firmware/out" / f
    check(f"{f} == MFG_PIN", p.exists() and sha(p) == pin[key], p)
z = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.home() / "Documents/프로젝트/PokeDock_M6_RevC_Vendor_20261031/PokeDock_M6_RevC_Vendor_Package_20261031.zip"
if z.exists():
    want = next((v for k, v in pin.items() if "zip" in k and isinstance(v, str) and len(v) == 64), None)
    check("vendor ZIP SHA-256 == MFG_PIN", want is not None and sha(z) == want, z)
else:
    print(f"SKIP vendor ZIP not on this PC ({z})")
base = "origin/feature/m6-gift-content-20261031"
r = subprocess.run(["git", "diff", "--name-only", base, "--", "v16/masterball-m6"], capture_output=True, text=True,
                   cwd=HERE.parent.parent, encoding="utf8")
changed = [ln for ln in r.stdout.splitlines() if ln.strip()]
frozen = [c for c in changed if any(c.startswith(f"v16/masterball-m6/{d}/") for d in ("cad", "electronics", "vendor", "procurement"))]
check("git diff vs PR #23 head readable", r.returncode == 0, r.stderr)
check("no M6 CAD / circuit / BOM / SOP / vendor file changed on the M7 branch", not frozen, frozen)
print("M6 files this branch changes (firmware + flash tool only):")
for c in changed:
    print("   ", c)
print(f"{'FAIL' if fails else 'PASS'}: {n - len(fails)}/{n} frozen-M6 checks")
sys.exit(1 if fails else 0)
