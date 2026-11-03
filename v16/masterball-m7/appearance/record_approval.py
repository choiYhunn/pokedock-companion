"""Record the owner's approval of the CURRENT final print files (run only after the owner said so).

usage: python record_approval.py "<who>" <YYYY-MM-DD> "<what was approved>"
Reads print/print_manifest.json (written by cad/make_print_package.py), stores the SHA-256 of every
exterior final part - including the plates waiting in 02_final_PENDING_owner_approval - into
appearance/APPROVAL.json, and records who/when/what. Re-run tests/run_m7.sh afterwards: the pending
plates then move back into print/02_final.
"""
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
who, date, what = sys.argv[1:4]
man = json.loads((HERE.parent / "print" / "print_manifest.json").read_text(encoding="utf8"))
appr = json.loads((HERE / "APPROVAL.json").read_text(encoding="utf8"))
internal = set(appr.get("internal_parts_no_appearance_approval", []))
new = {"_note": appr["approved_print_sha256"].get("_note", "")}
for k, v in man.items():
    if isinstance(v, dict) and "sha256" in v and k not in internal:
        new[k] = v["sha256"]
missing = [k for k in appr["approved_print_sha256"] if k != "_note" and k not in new]
if missing:
    sys.exit(f"parts missing from the manifest (run tests/run_m7.sh first): {missing}")
head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=HERE).stdout.strip()
appr.update({"approved": True, "approved_by": who, "date": date, "approved_revision": what, "approved_commit": head,
             "approved_print_sha256": new})
(HERE / "APPROVAL.json").write_text(json.dumps(appr, ensure_ascii=False, indent=1) + "\n", encoding="utf8")
print(f"recorded {len(new) - 1} part hashes at {head} for {who} {date}")
