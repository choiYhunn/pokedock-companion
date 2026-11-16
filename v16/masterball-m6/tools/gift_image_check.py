"""Validators used by tools/flash_gift_windows.ps1 before anything is written to the ball.

usage: python tools/gift_image_check.py <kind> <file> [options]
  app <file> [--sums SHA256SUMS.txt]   ESP32-S3 app image for the factory slot (0x10000): full header,
                                       segment, checksum and appended-SHA-256 walk, app descriptor
                                       project "pokedock_m6", IDF v5.3.2, 16 MB flash, <= 0x600000.
                                       A merged image (bootloader first) is refused.
  device-app <file>                    first 4 KiB read from the ball at 0x10000: is it a PokéDock app?
  identify <full_backup> --sums <SHA256SUMS.txt>   which listed app image is on the ball (or "unknown")
  compat <device_head> <app>           new app keeps the ball's flash mode/frequency/size and IDF (bootloader stays)
  ptable <file>                        partition table read from 0x8000 equals firmware/partitions.csv
  pack <file>                          PDK1 sprite pack that fits below the message slot
  slot <file>                          4 KiB PDM1 private message slot
  nvs <file>                           NVS backup: exactly 0x6000 bytes, from a PokéDock layout
  full <file>                          16 MiB full-flash backup: bootloader magic + a valid ESP-IDF table
                                       (the app may be foreign, e.g. the Waveshare factory demo)
  merged <file> --sums <SHA256SUMS.txt>  merged image for FirstInstall at 0x0: bootloader, table equal to
                                       firmware/partitions.csv, nothing in NVS/phy, listed app at 0x10000
  extract-app <merged> <out>           cut the app out of a merged image (0x10000..end), validated
  make-ptable <out> [factory] | make-test-app <out> <version> [project] | make-merged <out> <app>
                                       synthetic files for tests
Exit code 0 = OK (one JSON line on stdout), 1 = refused (reason on stdout), 2 = usage.
"""
import csv
import hashlib
import json
import pathlib
import re
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FLASH_BYTES = 16 * 1024 * 1024
APP_OFFSET, APP_MAX = 0x10000, 0x600000
NVS_OFFSET, NVS_SIZE = 0x9000, 0x6000
ASSETS_OFFSET, ASSETS_SIZE = 0x610000, 0x9F0000
SLOT_BYTES = 4096
SLOT_OFFSET = ASSETS_OFFSET + ASSETS_SIZE - SLOT_BYTES  # 0xFFF000
PACK_MAX = ASSETS_SIZE - SLOT_BYTES                      # a pack must never overwrite the message slot
CHIP_ID_ESP32S3 = 9
APP_DESC_MAGIC = 0xABCD5432
PROJECT = "pokedock_m6"
IDF = "v5.3.2"


class Refused(Exception):
    pass


def expected_partitions():
    rows = []
    for line in (ROOT / "firmware/partitions.csv").read_text(encoding="utf8").splitlines():
        line = line.split("#")[0].strip()
        if not line:
            continue
        name, typ, sub, off, size = [c.strip() for c in line.split(",")[:5]]
        t = {"app": 0, "data": 1}[typ]
        s = {"nvs": 2, "phy": 1, "factory": 0}.get(sub, None)
        if s is None:
            s = int(sub, 0)
        rows.append((name, t, s, int(off, 0), int(size, 0)))
    return rows


def parse_ptable(b):
    rows, entries = [], b""
    for i in range(0, len(b), 32):
        e = b[i:i + 32]
        if e[:2] == b"\xaa\x50":
            t, s = e[2], e[3]
            off, size = struct.unpack("<II", e[4:12])
            rows.append((e[12:28].rstrip(b"\0").decode("ascii", "replace"), t, s, off, size))
            entries += e
        elif e[:2] == b"\xeb\xeb":
            if e[16:32] != hashlib.md5(entries).digest():
                raise Refused("partition table MD5 does not match its entries")
            return rows
        else:
            break
    raise Refused("partition table has no MD5 entry (not a valid ESP-IDF table)")


FACTORY_LIKE = [("nvs", 1, 2, 0x9000, 0x6000), ("phy_init", 1, 1, 0xF000, 0x1000),
                ("factory", 0, 0, 0x10000, 0x400000), ("storage", 1, 0x82, 0x410000, 0xBF0000)]   # tests only


def make_ptable(rows=None):
    entries = b""
    for name, t, s, off, size in (rows or expected_partitions()):
        entries += b"\xaa\x50" + bytes((t, s)) + struct.pack("<II", off, size) + name.encode().ljust(16, b"\0") + b"\0" * 4
    table = entries + b"\xeb\xeb" + b"\xff" * 14 + hashlib.md5(entries).digest()
    return table + b"\xff" * (0xC00 - len(table))


def app_desc(b, at=0x20):
    d = b[at:at + 256]
    if len(d) < 176 or struct.unpack("<I", d[:4])[0] != APP_DESC_MAGIC:
        return None
    s = lambda a, n: d[a:a + n].split(b"\0")[0].decode("ascii", "replace")  # noqa: E731
    return {"version": s(16, 32), "project": s(48, 32), "time": s(80, 16), "date": s(96, 16), "idf": s(112, 32)}


def check_header(b, what):
    if len(b) < 0x200 or b[0] != 0xE9:
        raise Refused(f"{what}: not an ESP image (magic 0x{b[0] if b else 0:02x})")
    chip = struct.unpack("<H", b[12:14])[0]
    if chip != CHIP_ID_ESP32S3:
        raise Refused(f"{what}: built for chip id {chip}, not ESP32-S3")
    desc = app_desc(b)
    if desc is None:
        raise Refused(f"{what}: no app descriptor at 0x20 - this looks like a MERGED image (bootloader first). "
                      "Use the *_app.bin file that goes to 0x10000.")
    if desc["project"] != PROJECT:
        raise Refused(f"{what}: project '{desc['project']}' is not {PROJECT}")
    if (b[3] >> 4) != 4:
        raise Refused(f"{what}: header flash size code {b[3] >> 4} is not 16 MB")
    return desc


def walk_app(b):
    """Full esptool-style walk: segments, checksum byte at the 16-byte boundary, appended SHA-256."""
    nseg = b[1]
    pos, cks = 24, 0xEF
    for _ in range(nseg):
        if pos + 8 > len(b):
            raise Refused("app image truncated in a segment header")
        _, length = struct.unpack("<II", b[pos:pos + 8])
        pos += 8
        if pos + length > len(b):
            raise Refused("app image truncated inside a segment")
        for x in b[pos:pos + length]:
            cks ^= x
        pos += length
    pos += 15 - (pos % 16)  # checksum is the last byte of the 16-byte block
    if pos >= len(b) or b[pos] != cks:
        raise Refused("app image checksum mismatch (corrupt or truncated)")
    pos += 1
    if b[23] == 1:
        if pos + 32 > len(b) or hashlib.sha256(b[:pos]).digest() != b[pos:pos + 32]:
            raise Refused("app image appended SHA-256 mismatch (corrupt or truncated)")
        pos += 32
    return pos


def check_app(path, sums=None, data=None):
    b = pathlib.Path(path).read_bytes() if data is None else data
    name = pathlib.Path(path).name
    desc = check_header(b, "app image")
    end = walk_app(b)
    if b[end:].strip(b"\xff"):
        raise Refused("app image has data after its end (merged or wrong file)")
    if end > APP_MAX:
        raise Refused(f"app image {end} B does not fit the 0x{APP_MAX:X} factory slot")
    if desc["idf"] != IDF:
        raise Refused(f"app built with IDF {desc['idf']}, the ball's bootloader came from {IDF}")
    digest = hashlib.sha256(b).hexdigest()
    listed = None
    if sums:
        table = {}
        for line in pathlib.Path(sums).read_text(encoding="utf8").splitlines():
            m = re.match(r"([0-9a-f]{64})\s+\*?(\S+)", line.strip())
            if m:
                table[m.group(2)] = m.group(1)
        if data is not None:   # app cut from a merged image: find it by content
            name = next((n for n, h in table.items() if h == digest), None)
            if name is None:
                raise Refused(f"the app inside the merged image is not listed in {sums}")
        listed = table.get(name)
        if listed is None:
            raise Refused(f"{name} is not listed in {sums}")
        if listed != digest:
            raise Refused(f"SHA-256 differs from {sums} (file changed or corrupt)")
    return {"kind": "app", "name": name, "bytes": len(b), "image_end": end, "sha256": digest, **desc, "listed": bool(listed)}


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    kind, f = argv[0], argv[1]
    try:
        if kind == "app":
            sums = argv[argv.index("--sums") + 1] if "--sums" in argv else None
            out = check_app(f, sums)
        elif kind == "device-app":
            b = pathlib.Path(f).read_bytes()
            out = {"kind": "device-app", **check_header(b, "app on the ball")}
        elif kind == "identify":
            b = pathlib.Path(f).read_bytes()
            app = b[APP_OFFSET:APP_OFFSET + APP_MAX]
            try:  # a broken app (e.g. a cable pulled mid-write) must not block the restore paths
                desc = check_header(app[:0x1000], "app on the ball")
                end = walk_app(app)
            except Refused as e:
                print(json.dumps({"kind": "identify", "name": "broken", "reason": str(e), "sha256": "", "date": "", "time": ""}))
                return 0
            digest = hashlib.sha256(app[:end]).hexdigest()
            name = "unknown"
            if "--sums" in argv and pathlib.Path(argv[argv.index("--sums") + 1]).exists():
                for line in pathlib.Path(argv[argv.index("--sums") + 1]).read_text(encoding="utf8").splitlines():
                    m = re.match(r"([0-9a-f]{64})\s+\*?(\S+)", line.strip())
                    if m and m.group(1) == digest:
                        name = m.group(2)
            out = {"kind": "identify", "name": name, "sha256": digest, **desc}
        elif kind == "compat":
            dev = pathlib.Path(f).read_bytes()
            new = pathlib.Path(argv[2]).read_bytes()
            d, n = check_header(dev, "app on the ball"), check_header(new, "new app")
            if dev[2:4] != new[2:4]:
                raise Refused(f"flash mode/frequency/size bytes differ: ball {dev[2:4].hex()} vs new {new[2:4].hex()}")
            if d["idf"] != n["idf"]:
                raise Refused(f"IDF differs: ball app {d['idf']} vs new {n['idf']} (bootloader is not rewritten)")
            out = {"kind": "compat", "ball": d, "new": n}
        elif kind == "ptable":
            b = pathlib.Path(f).read_bytes()
            got, want = parse_ptable(b), expected_partitions()
            if got != want:
                raise Refused(f"partition table on the ball {got} differs from firmware/partitions.csv {want}")
            out = {"kind": "ptable", "partitions": [r[0] for r in got]}
        elif kind == "pack":
            b = pathlib.Path(f).read_bytes()
            if b[:4] != b"PDK1" or struct.unpack("<H", b[4:6])[0] != 1:
                raise Refused("not a PDK1 sprite pack")
            n = struct.unpack("<H", b[6:8])[0]
            if 8 + 20 * n > len(b):
                raise Refused("pack header points past the end of the file")
            if len(b) > PACK_MAX:
                raise Refused(f"pack {len(b)} B would overwrite the message slot (max {PACK_MAX})")
            out = {"kind": "pack", "bytes": len(b), "clips": n, "sha256": hashlib.sha256(b).hexdigest()}
        elif kind == "slot":
            b = pathlib.Path(f).read_bytes()
            if len(b) != SLOT_BYTES or b[:4] != b"PDM1":
                raise Refused("not a 4096-byte PDM1 message slot")
            n = struct.unpack("<H", b[4:6])[0]
            if not 0 < n <= 90:
                raise Refused("message length outside 1..90 bytes")
            b[6:6 + n].decode("utf-8")
            out = {"kind": "slot", "text_bytes": n}  # the text itself is private: never printed
        elif kind == "nvs":
            b = pathlib.Path(f).read_bytes()
            if len(b) != NVS_SIZE:
                raise Refused(f"NVS backup must be exactly 0x{NVS_SIZE:X} bytes, got {len(b)}")
            out = {"kind": "nvs", "sha256": hashlib.sha256(b).hexdigest()}
        elif kind == "full":
            b = pathlib.Path(f).read_bytes()
            if len(b) != FLASH_BYTES:
                raise Refused(f"full backup must be exactly 16 MiB, got {len(b)}")
            if b[0] != 0xE9 or struct.unpack("<H", b[12:14])[0] != CHIP_ID_ESP32S3:
                raise Refused("full backup does not start with an ESP32-S3 bootloader")
            rows = parse_ptable(b[0x8000:0x8C00])
            try:   # a factory-demo backup (taken before FirstInstall) is a valid thing to restore
                desc = check_header(b[APP_OFFSET:APP_OFFSET + 0x1000], "app in the backup")
            except Refused as e:
                desc = {"project": "foreign", "note": str(e)[:80]}
            out = {"kind": "full", "sha256": hashlib.sha256(b).hexdigest(), "pokedock_layout": rows == expected_partitions(), **desc}
        elif kind == "merged":
            b = pathlib.Path(f).read_bytes()
            if "--sums" not in argv:
                raise Refused("merged needs --sums")
            sums = argv[argv.index("--sums") + 1]
            if len(b) < APP_OFFSET + 0x200 or b[0] != 0xE9 or struct.unpack("<H", b[12:14])[0] != CHIP_ID_ESP32S3:
                raise Refused("not a merged ESP32-S3 image (no bootloader at 0x0)")
            if (b[3] >> 4) != 4:
                raise Refused("bootloader header flash size is not 16 MB")
            if walk_app(b[:0x8000]) > 0x8000:
                raise Refused("bootloader runs into the partition table")
            if parse_ptable(b[0x8000:0x8C00]) != expected_partitions():
                raise Refused("merged image table differs from firmware/partitions.csv")
            if b[NVS_OFFSET:APP_OFFSET].strip(b"\xff"):
                raise Refused("merged image carries data in NVS/phy (0x9000-0xFFFF)")
            app = check_app(f, sums, data=b[APP_OFFSET:])
            out = {"kind": "merged", "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest(), "app_name": app["name"],
                   "app_sha256": app["sha256"], "version": app["version"], "idf": app["idf"]}
        elif kind == "extract-app":
            b = pathlib.Path(f).read_bytes()
            got = parse_ptable(b[0x8000:0x8C00])
            if got != expected_partitions():
                raise Refused("merged image has a different partition table")
            app = b[APP_OFFSET:]
            pathlib.Path(argv[2]).write_bytes(app)
            out = check_app(argv[2])
            out["from_merged_sha256"] = hashlib.sha256(b).hexdigest()
        elif kind == "make-ptable":
            pathlib.Path(f).write_bytes(make_ptable(FACTORY_LIKE if "factory" in argv[2:] else None))
            out = {"kind": "make-ptable"}
        elif kind == "make-merged":
            app = pathlib.Path(argv[2]).read_bytes()   # any walkable ESP32-S3 image stands in for the bootloader
            img = app.ljust(0x8000, b"\xff") + make_ptable() + b"\xff" * (APP_OFFSET - 0x8C00) + app
            pathlib.Path(f).write_bytes(img)
            out = {"kind": "make-merged", "bytes": len(img)}
        elif kind == "make-test-app":
            ver = argv[2] if len(argv) > 2 else "test"
            proj = argv[3] if len(argv) > 3 else PROJECT
            desc = struct.pack("<II8x", APP_DESC_MAGIC, 0) + ver.encode().ljust(32, b"\0") + proj.encode().ljust(32, b"\0")
            desc += b"00:00:00".ljust(16, b"\0") + b"Nov  1 2026".ljust(16, b"\0") + IDF.encode().ljust(32, b"\0")
            seg = desc.ljust(0x400, b"\0") + hashlib.sha256(ver.encode()).digest() * 64  # deterministic filler
            hdr = bytes((0xE9, 1, 2, 0x4F)) + struct.pack("<I", 0x40370000) + bytes((0xEE, 0, 0, 0)) + struct.pack("<H", CHIP_ID_ESP32S3) + bytes((0, 0, 0, 0xFF, 0xFF, 0, 0, 0, 0, 1))
            body = hdr + struct.pack("<II", 0x3C000020, len(seg)) + seg
            cks = 0xEF
            for x in seg:
                cks ^= x
            body += b"\0" * (15 - len(body) % 16) + bytes((cks,))
            body += hashlib.sha256(body).digest()
            pathlib.Path(f).write_bytes(body)
            out = check_app(f) if proj == PROJECT else {"kind": "make-test-app", "project": proj}
        else:
            print(__doc__)
            return 2
    except Refused as e:
        print(f"REFUSED: {e}")
        return 1
    except (OSError, UnicodeDecodeError, struct.error, IndexError) as e:
        print(f"REFUSED: cannot read {f}: {e}")
        return 1
    print(json.dumps(out, ensure_ascii=True))  # ASCII only: PowerShell 5.1 reads native output in the ANSI code page
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
