#!/usr/bin/env bash
# Run every host-side M6 check and write logs to tests/logs/. No hardware, no network services,
# no GitHub Actions. Requirements: g++/gcc (C++17), node >= 20, python with build123d, trimesh,
# manifold3d, scipy, networkx, playwright (+ an installed Edge or Chromium) and the vendor STEP
# parts extracted by tools/vendor_step_to_parts.py.
# usage: PY=<python> VENDOR_PARTS=<dir> tests/run_all.sh
set -u
cd "$(dirname "$0")/.."
PY=${PY:-python}
LOG=tests/logs
mkdir -p "$LOG" build
status=0
run() {
  local name=$1; shift
  if "$@" > "$LOG/$name.txt" 2>&1; then echo "PASS $name"; else echo "FAIL $name"; status=1; fi
  tail -n 2 "$LOG/$name.txt" | sed 's/^/    /'
}
run core_regression bash -c "g++ -std=c++17 -O2 -Wall -Wextra -Werror tests/core_regression_test.cpp -o build/core_reg && ./build/core_reg"
run protocol bash -c "g++ -std=c++17 -O1 -Wall -Wextra -Werror tests/protocol_test.cpp -o build/proto && ./build/proto"
run ble_e2e_bridge bash -c "g++ -std=c++17 -O1 -Wall -Wextra -Werror tests/ble_bridge_host.cpp -o build/ble_bridge && node tests/ble_e2e_bridge_test.mjs build/ble_bridge"
run harness_check "$PY" -X utf8 tests/harness_check.py
run pdk_roundtrip "$PY" -X utf8 tests/pdk_roundtrip_test.py build/pdk
if [ -n "${VENDOR_PARTS:-}" ]; then
  run cad_build "$PY" -X utf8 cad/build_m6.py cad/out
  run cad_fitkit "$PY" -X utf8 cad/build_fit_kit.py cad/out
  run cad_verify "$PY" -X utf8 cad/verify_m6.py cad/out "$VENDOR_PARTS" cad/out/verify_report.json
else
  echo "SKIP cad (set VENDOR_PARTS to the extracted official STEP parts)"
fi
run ui_sim_probe "$PY" -X utf8 tests/ui_sim_probe.py "$LOG/ui"
exit $status
