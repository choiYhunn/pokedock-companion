#!/usr/bin/env bash
# Run every M6 check and write logs + tests/logs/RUN_MANIFEST.json. No hardware, no GitHub Actions.
#
#   bash tests/run_all.sh            developer mode: missing vendor data -> SKIP (never "approved")
#   bash tests/run_all.sh --strict   manufacturing mode: any SKIP or FAIL -> exit 1; stale CAD
#                                    outputs are deleted first; the ESP-IDF target build is required;
#                                    the manifest is checked against the current source fingerprint
#
# Inputs (strict defaults point at vendor_cache/ created by tools/fetch_vendor_refs.sh):
#   PY=<python with build123d trimesh manifold3d scipy networkx playwright pymupdf>
#   VENDOR_PARTS=<extracted official STEP parts>  SCHEMATIC_PDF=<official schematic>
#   ADAFRUIT_SCH=<Adafruit 4090 rev B .sch>
set -u
cd "$(dirname "$0")/.."
MODE=dev
[ "${1:-}" = "--strict" ] && MODE=strict
PY=${PY:-python}
VENDOR_PARTS=${VENDOR_PARTS:-vendor_cache/parts}
SCHEMATIC_PDF=${SCHEMATIC_PDF:-vendor_cache/schematic.pdf}
ADAFRUIT_SCH=${ADAFRUIT_SCH:-vendor_cache/adafruit4090.sch}
LOG=tests/logs
mkdir -p "$LOG" build
STARTED=$(date -u +%Y-%m-%dT%H:%M:%SZ)
declare -A RES
ORDER=()
status=0
run() {
  local name=$1; shift
  ORDER+=("$name")
  if "$@" > "$LOG/$name.txt" 2>&1; then RES[$name]=PASS; echo "PASS $name"; else RES[$name]=FAIL; echo "FAIL $name"; status=1; fi
  tail -n 2 "$LOG/$name.txt" | sed 's/^/    /'
}
skip() {
  ORDER+=("$1"); RES[$1]=SKIP; echo "SKIP $1 ($2)"
  [ "$MODE" = strict ] && status=1
}
have() { [ -e "$1" ]; }

if [ "$MODE" = strict ]; then
  # never let an older report stand in for this run
  rm -rf cad/out/step cad/out/stl cad/out/purchased cad/out/fitkit cad/out/verify_report.json \
         cad/out/driver_board_report.json cad/out/tolerance_stack.json "$LOG"/RUN_MANIFEST.json
fi

run core_regression bash -c "g++ -std=c++17 -O2 -Wall -Wextra -Werror tests/core_regression_test.cpp -o build/core_reg && ./build/core_reg"
run protocol bash -c "g++ -std=c++17 -O1 -Wall -Wextra -Werror tests/protocol_test.cpp -o build/proto && ./build/proto"
run ble_e2e_bridge bash -c "g++ -std=c++17 -O1 -Wall -Wextra -Werror tests/ble_bridge_host.cpp -o build/ble_bridge && node tests/ble_e2e_bridge_test.mjs build/ble_bridge"
run harness_check "$PY" -X utf8 tests/harness_check.py
run buzzer_consistency "$PY" -X utf8 tests/buzzer_consistency_check.py
run doc_consistency "$PY" -X utf8 tests/doc_consistency_check.py
if have "$SCHEMATIC_PDF"; then run schematic_netlist "$PY" -X utf8 tests/schematic_netlist_check.py "$SCHEMATIC_PDF"
else skip schematic_netlist "no official schematic at $SCHEMATIC_PDF"; fi
if have "$ADAFRUIT_SCH"; then run adafruit4090_netlist "$PY" -X utf8 tests/adafruit4090_netlist_check.py "$ADAFRUIT_SCH"
else skip adafruit4090_netlist "no Adafruit 4090 schematic at $ADAFRUIT_SCH"; fi
run tolerance_stack "$PY" -X utf8 cad/tolerance_stack.py cad/out/tolerance_stack.json
run pdk_roundtrip "$PY" -X utf8 tests/pdk_roundtrip_test.py build/pdk
if have "$VENDOR_PARTS/parts.json"; then
  run cad_build "$PY" -X utf8 cad/build_m6.py cad/out
  if [ "${RES[cad_build]}" = PASS ]; then
    run cad_fitkit "$PY" -X utf8 cad/build_fit_kit.py cad/out
    run cad_verify "$PY" -X utf8 cad/verify_m6.py cad/out "$VENDOR_PARTS" cad/out/verify_report.json
    run driver_board_check "$PY" -X utf8 cad/driver_board_check.py cad/out cad/out/driver_board_report.json
  else
    for s in cad_fitkit cad_verify driver_board_check; do ORDER+=("$s"); RES[$s]=FAIL; echo "FAIL $s (cad_build failed)"; done
    status=1
  fi
else
  for s in cad_build cad_fitkit cad_verify driver_board_check; do skip "$s" "no vendor STEP parts at $VENDOR_PARTS"; done
fi
run ui_sim_probe "$PY" -X utf8 tests/ui_sim_probe.py "$LOG/ui"

# ESP-IDF target build (WSL on Windows, native elsewhere)
if command -v wsl.exe >/dev/null 2>&1; then
  # C:/Users/... or /c/Users/... -> /mnt/c/Users/... (wslpath output is mangled for non-ASCII paths)
  WP=$(git rev-parse --show-toplevel | sed -E 's#^([A-Za-z]):/#/\1/#; s#^/([a-zA-Z])/#/mnt/\L\1/#')
  run firmware_build env MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu-22.04 -- bash -lc "cd '$WP' && bash v16/masterball-m6/tools/idf_build_wsl.sh"
elif [ -d "$HOME/m6idf/esp-idf" ]; then
  run firmware_build bash tools/idf_build_wsl.sh
else
  skip firmware_build "no ESP-IDF toolchain (tools/idf_setup_wsl.sh)"
fi

# manifest: what ran, against which sources
FP=$("$PY" -X utf8 tests/source_fingerprint.py)
RESULTS=""
for k in "${ORDER[@]}"; do RESULTS+="\"$k\":\"${RES[$k]}\","; done
DIRTY=$(git status --porcelain -- . ':!tests/logs' ':!cad/out' | wc -l | tr -d ' ')
cat > "$LOG/RUN_MANIFEST.json" <<EOF
{"mode":"$MODE","started_utc":"$STARTED","finished_utc":"$(date -u +%Y-%m-%dT%H:%M:%SZ)",
 "git_head":"$(git rev-parse HEAD)","uncommitted_source_files":$DIRTY,"source_fingerprint":"$FP",
 "results":{${RESULTS%,}},
 "tools":{"gpp":"$(g++ --version | head -1)","node":"$(node -v)","python":"$("$PY" --version 2>&1)"}}
EOF
if [ "$MODE" = strict ]; then
  run manifest_check "$PY" -X utf8 tests/check_manifest.py
fi
echo "MODE=$MODE  RESULT=$([ $status = 0 ] && echo PASS || echo FAIL)  fingerprint=$FP"
exit $status
