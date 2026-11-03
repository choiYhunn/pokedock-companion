#!/usr/bin/env bash
# PokéDock M7: every computer-side check, logs in logs/ and a manifest. Nothing here touches a real board,
# a printer or a shop: a PASS means "PASS in CAD / on the host", never "built and tested".
# usage (from v16/masterball-m7):  PY=<python with build123d trimesh manifold3d PyMuPDF lxml> bash tests/run_m7.sh
set -u
cd "$(dirname "$0")/.."
PY=${PY:-python}
M6=../masterball-m6
LOG=logs
mkdir -p "$LOG"
declare -A RES
ORDER=()
run() {
  local name=$1
  shift
  ORDER+=("$name")
  if "$@" > "$LOG/$name.txt" 2>&1; then RES[$name]=PASS; else RES[$name]=FAIL; fi
  echo "${RES[$name]} $name"
}
started=$(date -u +%Y-%m-%dT%H:%M:%SZ)
run cad_build "$PY" -X utf8 cad/build_m7.py cad/out
run cad_verify "$PY" -X utf8 cad/verify_m7.py cad/out "$M6/vendor_cache/parts" cad/out/verify_report.json
run pod_position_sweep "$PY" -X utf8 cad/optimize_pod.py cad/out "$M6/vendor_cache/parts" cad/out/pod_sweep.json
run cad_renders "$PY" -X utf8 cad/render_m7.py cad/out "$M6/vendor_cache/parts" "$M6/tests/logs/gift/gift_01_home_gengar.png" img
run appearance_gate_metrics "$PY" -X utf8 cad/appearance_gate.py cad/out img appearance
# variant B (photo ear position) is archived as a reference since the owner chose A (2026-11-02):
# its last verified files stay in cad/out_variant_B and appearance/variant_B; rebuild with M7_EAR_VARIANT=B
run electrical "$PY" -X utf8 tests/m7_electrical_check.py "$M6/vendor_cache/schematic.pdf" electronics/harness_m7.json
run wiring_pinmap "$PY" -X utf8 electronics/m7_wiring_v06.py img electronics/M7_PINMAP_KO.md
mkdir -p "$M6/build"
run lid_sensor_firmware bash -c "g++ -std=c++17 -O1 -Wall -Wextra -Werror -I $M6 $M6/tests/lid_sensor_test.cpp -o $M6/build/lid_sensor_test && $M6/build/lid_sensor_test"
run audio_firmware bash -c "g++ -std=c++17 -O1 -Wall -Wextra -Werror -I $M6 $M6/tests/audio_director_test.cpp -o $M6/build/audio_director_test && $M6/build/audio_director_test"
run sound_manifest "$PY" -X utf8 audio/check_sound_manifest.py
run sound_pack_tools "$PY" -X utf8 audio/test_audio_tools.py build/audio_tool_test
run purchase_list "$PY" -X utf8 tests/m7_bom_check.py
run print_package bash -c "rm -rf print && $PY -X utf8 cad/make_print_package.py cad/out print"
run m6_frozen "$PY" -X utf8 tests/m6_frozen_check.py
cp cad/out/verify_report.json cad/out/pod_sweep.json cad/out/build_report.json print/print_manifest.json "$LOG/" 2>/dev/null
status=0
json="{\"started_utc\":\"$started\",\"finished_utc\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"git_head\":\"$(git rev-parse HEAD)\",\"uncommitted_source_files\":$(git status --porcelain -- cad/*.py tests electronics audio bom | wc -l),\"results\":{"
sep=""
for k in "${ORDER[@]}"; do
  json+="$sep\"$k\":\"${RES[$k]}\""
  sep=","
  [ "${RES[$k]}" = PASS ] || status=1
done
json+="},\"appearance_gate\":\"$(grep -o '\"gate\": \"[A-Z_]*\"' appearance/APPEARANCE_GATE.json | head -1 | sed 's/.*: //; s/\"//g')\",\"scope\":\"computer-side only: CAD geometry, meshes, ray casts, host firmware tests, schematic text layer. No board, print or 24 h test.\"}"
echo "$json" > "$LOG/RUN_MANIFEST.json"
echo "RESULT=$([ $status = 0 ] && echo PASS || echo FAIL) (${#ORDER[@]} steps)"
exit $status
