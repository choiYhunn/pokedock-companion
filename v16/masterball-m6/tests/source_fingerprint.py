"""Content fingerprint of every M6 source file (CAD scripts, params, firmware, core, mobile, tests,
docs, procurement, electronics) - generated outputs and logs excluded. Reports and run manifests
store it; `check_manifest.py` refuses logs/reports whose fingerprint differs from the tree.
usage: python source_fingerprint.py   -> prints the hex digest
"""
import hashlib
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {"tests/logs", "cad/out", "firmware/out", "vendor_cache", "build", "docs/img"}
EXCLUDE_PARTS = {"__pycache__", "node_modules", "managed_components"}


def files():
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT).as_posix()
        if any(rel == d or rel.startswith(d + "/") for d in EXCLUDE_DIRS):
            continue
        if any(part in EXCLUDE_PARTS for part in p.parts) or p.suffix in (".pyc",):
            continue
        yield rel, p


def fingerprint():
    h = hashlib.sha256()
    for rel, p in files():
        data = p.read_bytes().replace(b"\r\n", b"\n")  # CRLF/LF checkouts hash the same
        h.update(rel.encode() + b"\0" + hashlib.sha256(data).digest())
    return h.hexdigest()


if __name__ == "__main__":
    print(fingerprint())
