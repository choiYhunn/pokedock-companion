"""Slice the M7 print plates with the installed Bambu Studio CLI and report time and filament per plate.

usage: python bambu_slice_estimate.py <printer: X1C|H2S|A1M> <out_dir> [plate.3mf ...]

Flattens the Bambu system presets (machine / process / filament follow "inherits") into plain JSON,
applies the docs/06 settings (functional: 0.20 mm, 4 walls, 25 % gyroid; look parts: 0.16 mm,
4 walls, 15 % gyroid; tree supports from the build plate only on the plates docs/06 lists), slices
each 3MF without a GUI and reads time and grams from the sliced 3MF (Metadata/slice_info.config).
The estimate is the slicer's; the lid's "support only inside the dome" paint cannot be applied from
the CLI, so its support grams are an upper bound. Nothing in print/ is changed.
"""
import json
import pathlib
import re
import subprocess
import sys
import zipfile

BS = pathlib.Path(r"C:\Program Files\Bambu Studio")
PROF = BS / "resources" / "profiles" / "BBL"
HERE = pathlib.Path(__file__).resolve().parent.parent
PRINTERS = {
    "X1C": ("Bambu Lab X1 Carbon 0.4 nozzle", "@BBL X1C"),
    "H2S": ("Bambu Lab H2S 0.4 nozzle", "@BBL H2S"),
    "A1M": ("Bambu Lab A1 mini 0.4 nozzle", "@BBL A1M"),
}
LOOK = {"C1", "C2", "C3", "C4", "C5", "C6", "C6b"}           # 0.16 mm, 15 % (docs/06 table 1)
SUPPORT = {"C1", "C3", "C7", "FK2", "FK3"}                   # docs/06 table 2: plates that need some support


def find(kind, name):
    p = PROF / kind / f"{name}.json"
    if p.exists():
        return p
    hits = [q for q in (PROF / kind).glob("*.json") if json.loads(q.read_text(encoding="utf8")).get("name") == name]
    if not hits:
        raise FileNotFoundError(f"{kind}/{name}")
    return hits[0]


def flat(kind, name):
    d = json.loads(find(kind, name).read_text(encoding="utf8"))
    if d.get("inherits"):
        base = flat(kind, d["inherits"])
        base.update(d)
        d = base
    d.pop("inherits", None)
    return d


def preset_name(kind, prefer):
    for p in (PROF / kind).glob("*.json"):
        n = json.loads(p.read_text(encoding="utf8")).get("name", "")
        if n == prefer:
            return n
    raise FileNotFoundError(prefer)


def main():
    printer, out = sys.argv[1], pathlib.Path(sys.argv[2])
    plates = [pathlib.Path(p) for p in sys.argv[3:]] or sorted((HERE / "print" / "01_fitkit_first").glob("*.3mf")) + \
        sorted((HERE / "print" / "02_final").glob("*.3mf"))
    mname, tag = PRINTERS[printer]
    out.mkdir(parents=True, exist_ok=True)
    machine = flat("machine", mname)
    machine["type"] = "machine"
    filament = flat("filament", preset_name("filament", f"Bambu PLA Matte {tag}"))
    filament["type"] = "filament"
    rows = []
    for plate in plates:
        key = plate.stem.split("_")[0]
        look = key in LOOK
        fine = f"0.16mm Optimal {tag}" if (PROF / "process" / f"0.16mm Optimal {tag}.json").exists() else f"0.16mm Standard {tag}"
        proc = flat("process", preset_name("process", fine if look else f"0.20mm Standard {tag}"))
        proc.update({"type": "process", "wall_loops": "4", "top_shell_layers": "5", "bottom_shell_layers": "4",
                     "sparse_infill_density": "15%" if look else "25%", "sparse_infill_pattern": "gyroid",
                     "enable_support": "1" if key in SUPPORT else "0", "support_type": "tree(auto)",
                     "support_on_build_plate_only": "1"})
        for d, n in ((machine, "machine.json"), (proc, f"process_{key}.json"), (filament, "filament.json")):
            (out / n).write_text(json.dumps(d), encoding="utf8")
        sliced = out / f"{plate.stem}_{printer}.gcode.3mf"
        cmd = [str(BS / "bambu-studio.exe"), "--slice", "0", "--allow-newer-file",
               "--load-settings", f"{out / 'machine.json'};{out / f'process_{key}.json'}",
               "--load-filaments", str(out / "filament.json"), "--export-3mf", sliced.name, "--outputdir", str(out), str(plate)]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf8", errors="replace", timeout=900)
        row = {"plate": plate.stem, "printer": printer, "layer": "0.16" if look else "0.20", "support": key in SUPPORT,
               "rc": r.returncode}
        if sliced.exists():
            with zipfile.ZipFile(sliced) as z:
                info = z.read("Metadata/slice_info.config").decode("utf8", "replace")
            pred = re.search(r'key="prediction" value="(\d+)"', info)
            wt = re.search(r'key="weight" value="([\d.]+)"', info)
            used_g = re.findall(r'used_g="([\d.]+)"', info)
            row.update(minutes=round(int(pred.group(1)) / 60) if pred else None,
                       grams=float(wt.group(1)) if wt else (sum(map(float, used_g)) if used_g else None))
        else:
            row["error"] = (r.stdout + r.stderr)[-400:]
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
    (out / f"estimate_{printer}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf8")


if __name__ == "__main__":
    main()
