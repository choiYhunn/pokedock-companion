"""Replays the exact esptool argument lists that tools/flash_gift_windows.ps1 produced in
tests/flash_gift_test.ps1 (saved in build/flash_argv_*.log) against the REAL esptool 4.x, with the
port replaced by a non-existent COM199. A wrong option or command name fails in esptool's argparse
before any port is opened; a correct list fails only at "could not open port".
usage: python flash_cli_compat_test.py [<python with esptool 4.x>]
"""
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
py = sys.argv[1] if len(sys.argv) > 1 else sys.executable
ver = subprocess.run([py, "-m", "esptool", "version"], capture_output=True, text=True)
if ver.returncode != 0:
    sys.exit("FAIL: esptool not installed for " + py + " (python -m pip install \"esptool>=4.7,<5\")")
version = ver.stdout.strip().splitlines()[-1]
if not version.startswith("4."):
    sys.exit(f"FAIL: esptool {version}; the tool is written for the 4.x command names")
logs = sorted((ROOT / "build").glob("flash_argv_*.log"))
if not logs:
    sys.exit("FAIL: no build/flash_argv_*.log (run tests/flash_gift_test.ps1 first)")
tmp = pathlib.Path(tempfile.mkdtemp())
dummy = tmp / "dummy.bin"
dummy.write_bytes(b"\xff" * 4096)
seen, bad = set(), []
for log in logs:
    for line in log.read_text(encoding="utf8").splitlines():
        argv = json.loads(line)  # exactly what the tool passed after "python -m esptool"
        cmd = next(a for a in argv if not a.startswith("-") and a not in ("esp32s3", "460800", "default_reset", "no_reset", "hard_reset") and not a.startswith("COM"))
        fixed, i = [], 0
        while i < len(argv):
            a = argv[i]
            if a == "--port":
                fixed += [a, "COM199"]
                i += 2
                continue
            if a.lower().endswith(".bin"):
                a = str(dummy if cmd in ("write_flash", "verify_flash") else tmp / "out.bin")
            fixed.append(a)
            i += 1
        key = " ".join(x if not x.endswith(".bin") else "<file>" for x in fixed)
        if key in seen:
            continue
        seen.add(key)
        r = subprocess.run([py, "-m", "esptool", *fixed], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
        out = r.stdout + r.stderr
        parse_error = "usage:" in out or "error: argument" in out or "invalid choice" in out or "unrecognized arguments" in out
        port_error = "COM199" in out and ("could not open port" in out.lower() or "does not exist" in out.lower() or "failed to connect" in out.lower())
        ok = (not parse_error) and port_error
        print(("PASS " if ok else "FAIL ") + key)
        if not ok:
            bad.append(key + "\n" + out[-400:])
print(f"{'FAIL' if bad else 'PASS'}: {len(seen) - len(bad)}/{len(seen)} distinct argument lists accepted by esptool {version}")
for b in bad:
    print(b)
sys.exit(1 if bad else 0)
