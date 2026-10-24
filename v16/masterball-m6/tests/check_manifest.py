"""Freshness gate for manufacturing approval: logs and CAD reports must come from THIS source tree.
Fails if tests/logs/RUN_MANIFEST.json or cad/out/verify_report.json carry a different (or no)
source fingerprint, if the run was not strict, if any required step was not PASS, or if the STL
files on disk differ from the hashes recorded by the CAD run.
usage: python check_manifest.py
"""
import hashlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from source_fingerprint import ROOT, fingerprint  # noqa: E402

REQUIRED = ["core_regression", "protocol", "ble_e2e_bridge", "harness_check", "buzzer_consistency",
            "schematic_netlist", "adafruit4090_netlist", "tolerance_stack", "pdk_roundtrip", "doc_consistency",
            "cad_build", "cad_fitkit", "cad_verify", "driver_board_check", "ui_sim_probe", "firmware_build"]
fail = []
fp = fingerprint()
man_p = ROOT / "tests" / "logs" / "RUN_MANIFEST.json"
rep_p = ROOT / "cad" / "out" / "verify_report.json"
if not man_p.exists():
    fail.append("no RUN_MANIFEST.json")
else:
    man = json.loads(man_p.read_text(encoding="utf8"))
    if man.get("source_fingerprint") != fp:
        fail.append("RUN_MANIFEST fingerprint differs from the current sources (logs are stale)")
    if man.get("mode") != "strict":
        fail.append("run was not strict")
    for step in REQUIRED:
        if man.get("results", {}).get(step) != "PASS":
            fail.append(f"required step {step}: {man.get('results', {}).get(step, 'MISSING')}")
rep = json.loads(rep_p.read_text(encoding="utf8")) if rep_p.exists() else {}
if rep.get("source_fingerprint") != fp:
    fail.append("verify_report.json is not from the current sources (e.g. an older Rev B report)")
for name, digest in rep.get("stl_sha256", {}).items():
    p = ROOT / "cad" / "out" / name
    if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != digest:
        fail.append(f"{name} on disk differs from the verified mesh")
if not rep.get("stl_sha256"):
    fail.append("verify_report.json has no STL hashes")
print("source fingerprint", fp)
print("PASS" if not fail else "FAIL", fail)
sys.exit(1 if fail else 0)
