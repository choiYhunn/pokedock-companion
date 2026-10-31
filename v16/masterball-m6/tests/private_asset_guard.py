"""Fails if anything private could be committed: Pokémon sprite packs (PDK1), private message slots
(PDM1), animation/audio files or a message.txt anywhere in the M6 tree tracked by git or staged.
usage: python private_asset_guard.py
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAGIC = (b"PDK1", b"PDM1", b"GIF87a", b"GIF89a", b"OggS", b"ID3", b"fLaC")
NAMES = {"message.txt", "assets_pack.bin", "message_slot.bin"}
out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--cached", "--others", "--exclude-standard", "."],
                     capture_output=True, text=True, check=True).stdout.split("\n")
bad = []
for rel in filter(None, out):
    p = ROOT / rel
    if not p.is_file():
        continue
    if p.name.lower() in NAMES:
        bad.append(f"{rel}: private file name")
        continue
    with open(p, "rb") as f:
        head = f.read(8)
    if head.startswith(MAGIC):
        bad.append(f"{rel}: private/media signature {head[:4]!r}")
print("PASS" if not bad else "FAIL", bad)
sys.exit(1 if bad else 0)
