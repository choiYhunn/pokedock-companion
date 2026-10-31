"""Helpers for tests/flash_gift_test.ps1 (synthetic device images and region checks; no real ball).

  make-device <img> <app.bin>       16 MiB: random bootloader 0x0-0x7FFF, real-format partition table 0x8000,
                                    random "settings" NVS 0x9000-0xEFFF and phy 0xF000, app at 0x10000
  sha <img> <off> <len>             SHA-256 of a region
  same <img> <off> <file>           region equals file (prints OK / DIFF)
  allff <img> <off> <len>           region erased (OK / DIFF)
  poke <img> <off> <hex>            overwrite bytes (to corrupt a table or change settings)
  cmds <log>                        esptool commands seen by the mock, one per line, arguments joined by |
"""
import hashlib
import json
import pathlib
import random
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main(a):
    cmd = a[0]
    if cmd == "make-device":
        img, app = pathlib.Path(a[1]), pathlib.Path(a[2]).read_bytes()
        rnd = random.Random(7)
        b = bytearray(b"\xff" * (16 * 1024 * 1024))
        b[0:0x7000] = bytes(rnd.randrange(256) for _ in range(0x7000))
        b[0:24] = bytes.fromhex("e904024f30893c40ee000000090000000063000000000001")  # real ESP32-S3 bootloader header (from the m6 image)
        table = ROOT / "build" / "_test_ptable.bin"
        table.parent.mkdir(exist_ok=True)
        subprocess.run([sys.executable, str(ROOT / "tools/gift_image_check.py"), "make-ptable", str(table)], check=True, capture_output=True)
        b[0x8000:0x8C00] = table.read_bytes()
        b[0x9000:0xF000] = bytes(rnd.randrange(256) for _ in range(0x6000))
        b[0xF000:0x10000] = bytes(rnd.randrange(256) for _ in range(0x1000))
        b[0x10000:0x10000 + len(app)] = app
        img.write_bytes(bytes(b))
    elif cmd == "sha":
        b = pathlib.Path(a[1]).read_bytes()
        off, n = int(a[2], 0), int(a[3], 0)
        print(hashlib.sha256(b[off:off + n]).hexdigest())
    elif cmd == "same":
        b, f = pathlib.Path(a[1]).read_bytes(), pathlib.Path(a[3]).read_bytes()
        off = int(a[2], 0)
        print("OK" if b[off:off + len(f)] == f else "DIFF")
    elif cmd == "allff":
        b = pathlib.Path(a[1]).read_bytes()
        off, n = int(a[2], 0), int(a[3], 0)
        print("OK" if b[off:off + n] == b"\xff" * n else "DIFF")
    elif cmd == "poke":
        p = pathlib.Path(a[1])
        b = bytearray(p.read_bytes())
        data = bytes.fromhex(a[3])
        off = int(a[2], 0)
        b[off:off + len(data)] = data
        p.write_bytes(bytes(b))
    elif cmd == "cmds":
        for line in pathlib.Path(a[1]).read_text(encoding="utf8").splitlines():
            argv = json.loads(line)
            rest, i = [], 0
            while i < len(argv):
                if argv[i] in ("--chip", "--port", "--baud", "--before", "--after"):
                    i += 2
                else:
                    rest.append(argv[i])
                    i += 1
            print("|".join(rest))


if __name__ == "__main__":
    main(sys.argv[1:])
