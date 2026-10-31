"""Build the single ZIP handed to the turnkey manufacturer.

usage: python tools/make_vendor_package.py [--out dist] [--no-assembly]

Collects the vendor documents, procurement BOMs, final/fit-kit STEP+STL, wiring, inspection
procedures and templates, the prebuilt firmware images (+ SHA-256) and the firmware source, then
refuses to write the ZIP if anything that must never leave the project is inside:
  - Pokémon artwork / animation / audio (gif, ogg, mp3, wav, pdk, sprite packs, assets/private)
  - an assets-partition image (firmware images must end before 0x610000)
  - personal data patterns (e-mail addresses, phone numbers) in any text file
  - vendor-redistribution items (vendor_cache/, Waveshare schematic crops)
A MANIFEST.json with every file's SHA-256 is written into the ZIP and next to it.
"""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS_OFFSET = 0x610000  # firmware/partitions.csv: assets partition (Pokémon sprite pack) starts here
TEXT_EXT = {".md", ".csv", ".json", ".txt", ".svg", ".c", ".cpp", ".h", ".hpp", ".py", ".sh", ".ps1", ".cmake", ".yml",
            ".lock", ".defaults", ".html", ".projbuild"}
FORBIDDEN_EXT = {".gif", ".ogg", ".mp3", ".wav", ".pdk", ".apng", ".webm", ".mp4"}
# GIF, Ogg, MP3 (ID3 / frame sync), FLAC, PDK sprite pack: refused whatever the file is named
MEDIA_MAGIC = (b"GIF87a", b"GIF89a", b"OggS", b"ID3", bytes([0xFF, 0xFB]), b"fLaC", b"PDK1")
FORBIDDEN_PATH = re.compile(r"(assets/private|vendor_cache|/sprites?/|vendor_schematic_|pokeapi)", re.I)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?<!\d)01[016789][- ]?\d{3,4}[- ]?\d{4}(?!\d)")
ALLOWED_EMAILS = {"noreply@anthropic.com"}  # none expected; listed so a commit trailer copy would not trip the check

# Package paths mirror the repository (v16/masterball-m6/...), so every path quoted in the SOP and the
# inspection documents resolves inside the ZIP. Only 00_READ_FIRST_KO.md is added at the top.
SAME = [
    "vendor/00_READ_FIRST_KO.md", "vendor/01_PRODUCT_SPEC_1P_KO.md", "vendor/02_RFQ_TURNKEY_KO.md",
    "vendor/03_SOP_BUILD_KO.md", "vendor/04_ACCEPTANCE_GATES_KO.md", "vendor/05_COST_ITEMS_KO.md",
    "vendor/06_SOLDER_REDUCTION_OPTIONS_KO.md", "vendor/BOM_TURNKEY.csv", "vendor/FAT_RECORD_TEMPLATE.csv",
    "vendor/NOTICE_KO.md", "README_KO.md", "procurement/BOM_M6.csv", "procurement/RFQ_M6_KO.md",
    "docs/G1_START_HERE_KO.md", "docs/G1_G2_INSPECTION_KO.md", "docs/G1_G2_RECORD_TEMPLATE.csv",
    "docs/REV_C_FINAL_KO.md", "docs/CLOCK_WITHOUT_PHONE_KO.md", "electronics/harness.json", "electronics/wiring_m6.svg",
    "docs/img/m6_wiring.png", "docs/img/m6_assembled_34.png", "docs/img/m6_exploded.png",
    "docs/img/m6_section_x0_front_detail.png", "docs/img/m6_section_x0_side.png", "docs/img/m6_section_z0_top.png",
    "tests/logs/RUN_MANIFEST.json", "cad/out/verify_report.json", "cad/out/driver_board_report.json",
    "cad/out/tolerance_stack.json", "cad/out/parts_meta.json",
]
DOCS = [("vendor/00_READ_FIRST_KO.md", "00_READ_FIRST_KO.md")] + [(p, p) for p in SAME]
GLOBS = [
    ("cad/out/step/*.step", "cad/out/step"),
    ("cad/out/stl/*.stl", "cad/out/stl"),
    ("cad/out/fitkit/*.step", "cad/out/fitkit"),
    ("cad/out/fitkit/*.stl", "cad/out/fitkit"),
    ("cad/out/purchased/*.stl", "cad/out/purchased"),
    ("tests/logs/ui/m6_*.png", "tests/logs/ui"),
]
FW_SOURCE = ["core", "firmware/main", "firmware/CMakeLists.txt", "firmware/partitions.csv", "firmware/sdkconfig.defaults",
             "firmware/dependencies.lock", "tools/idf_setup_wsl.sh", "tools/idf_build_wsl.sh", "tools/flash_windows.ps1"]
FW_IMAGES = ["pokedock_m6_merged.bin", "pokedock_m6_merged_rotate180.bin"]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception:
        return ""


def assembly_step(stage):
    """Printed parts in assembly coordinates as one STEP (the per-part STEPs already share one frame)."""
    try:
        from build123d import Compound, export_step, import_step
    except ImportError:
        return "skipped (build123d not installed)"
    parts = []
    for p in sorted((ROOT / "cad/out/step").glob("*.step")):
        shape = import_step(str(p))
        shape.label = p.stem
        parts.append(shape)
    out = stage / "cad/assembly/m6_printed_parts_assembly.step"
    out.parent.mkdir(parents=True, exist_ok=True)
    export_step(Compound(children=parts, label="pokedock_m6_rev_c_printed_parts"), str(out))
    return f"{len(parts)} parts"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dist")
    ap.add_argument("--no-assembly", action="store_true")
    a = ap.parse_args()
    date = dt.date.today().strftime("%Y%m%d")
    name = f"PokeDock_M6_RevC_Vendor_Package_{date}"
    out_dir = (ROOT / a.out).resolve()
    stage = out_dir / name
    shutil.rmtree(stage, ignore_errors=True)
    stage.mkdir(parents=True)
    problems = []

    def put(src, dst):
        s = ROOT / src
        if not s.exists():
            problems.append(f"missing source: {src}")
            return
        d = stage / dst
        d.parent.mkdir(parents=True, exist_ok=True)
        if s.is_dir():
            shutil.copytree(s, d, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "managed_components", "build"))
        else:
            shutil.copy2(s, d)

    for src, dst in DOCS:
        put(src, dst)
    for pattern, dst in GLOBS:
        hits = sorted(ROOT.glob(pattern))
        if not hits:
            problems.append(f"no files for {pattern}")
        for h in hits:
            put(h.relative_to(ROOT).as_posix(), f"{dst}/{h.name}")
    for src in FW_SOURCE:
        put(src, f"firmware/source/{src}")
    sums = []
    for img in FW_IMAGES:
        p = ROOT / "firmware/out" / img
        if not p.exists():
            problems.append(f"missing firmware image firmware/out/{img} (run tools/idf_build_wsl.sh [rotate180])")
            continue
        if p.stat().st_size >= ASSETS_OFFSET:
            problems.append(f"{img} reaches the assets partition (0x{ASSETS_OFFSET:x}): it may contain a sprite pack")
        put(f"firmware/out/{img}", f"firmware/{img}")
        sums.append(f"{sha256(p)}  {img}")
    (stage / "firmware/SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf8")
    asm = "skipped" if a.no_assembly else assembly_step(stage)

    # ---- content checks --------------------------------------------------------------------------
    files = sorted(p for p in stage.rglob("*") if p.is_file())
    for p in files:
        rel = p.relative_to(stage).as_posix()
        if p.suffix.lower() in FORBIDDEN_EXT:
            problems.append(f"forbidden media type in package: {rel}")
        head = p.read_bytes()[:12]
        if head.startswith(MEDIA_MAGIC) or (head[:4] == b"RIFF" and head[8:12] in (b"WAVE", b"WEBP", b"AVI ")):
            problems.append(f"animation/audio/sprite content (by file signature) in package: {rel}")
        if FORBIDDEN_PATH.search(rel):
            problems.append(f"forbidden path in package: {rel}")
        if (p.suffix.lower() in TEXT_EXT or p.name == "CMakeLists.txt") and not p.name.upper().startswith(("OFL", "LICENSE")):
            t = p.read_text(encoding="utf8", errors="ignore")
            for m in EMAIL.findall(t):
                if m.lower() not in ALLOWED_EMAILS and not m.lower().endswith(("@example.com",)):
                    problems.append(f"e-mail address in {rel}: {m}")
            for m in PHONE.findall(t):
                problems.append(f"phone number in {rel}: {m}")
    fw_hdr = (stage / "firmware/source/core/protocol.hpp").read_text(encoding="utf8")
    fw_version = re.search(r'kFirmwareVersion = "([^"]+)"', fw_hdr).group(1)
    pin = json.loads((ROOT / "vendor/MFG_PIN.json").read_text(encoding="utf8"))
    if fw_version != pin["firmware_version"]:
        problems.append(f"firmware {fw_version} is not the pinned manufacturing firmware {pin['firmware_version']} "
                        f"(build the vendor ZIP from commit {pin['commit']}; gift content is a separate step)")

    manifest = {
        "package": name, "created_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_head": git("rev-parse", "HEAD"), "git_branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "uncommitted_files": len(git("status", "--porcelain", "--", ".").splitlines()),
        "firmware_version": fw_version, "assembly_step": asm,
        "content_policy": {"pokemon_art_or_audio": "none", "assets_partition_image": "none",
                           "personal_data": "none found by e-mail/phone scan", "vendor_cache": "excluded"},
        "files": {p.relative_to(stage).as_posix(): {"bytes": p.stat().st_size, "sha256": sha256(p)} for p in files},
        "problems": problems,
    }
    (stage / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf8")
    if problems:
        print("REFUSED:", *problems, sep="\n  ")
        sys.exit(1)
    zpath = out_dir / f"{name}.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(stage.rglob("*")):
            if p.is_file():
                z.write(p, f"{name}/{p.relative_to(stage).as_posix()}")
    shutil.copy2(stage / "MANIFEST.json", out_dir / f"{name}.MANIFEST.json")
    print(f"OK {zpath} ({zpath.stat().st_size / 1e6:.1f} MB, {len(files) + 1} files, firmware {fw_version}, assembly {asm})")
    print(f"zip sha256 {sha256(zpath)}")


if __name__ == "__main__":
    main()
