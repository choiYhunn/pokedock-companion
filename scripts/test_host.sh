#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo "PokéDock V14 host-only validation (not ESP-IDF flashing)"
command -v node >/dev/null
command -v g++ >/dev/null
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
node tests/v10_navigation_smoke.cjs
node tests/party_game_smoke.cjs
node tests/v14_geometry_smoke.cjs
node tests/v14_contract_sanity.cjs
flags=(-std=c++17 -O2 -Wall -Wextra -Werror)
src=firmware/hmi/core
tests="$src/tests"
g++ "${flags[@]}" "$src/study_engine.cpp" "$tests/study_engine_test.cpp" -o "$tmp/study"
"$tmp/study"
g++ "${flags[@]}" "$src/study_engine.cpp" "$tests/study_engine_edge_test.cpp" -o "$tmp/study_edge"
"$tmp/study_edge"
g++ "${flags[@]}" "$src/reward_engine.cpp" "$tests/reward_engine_test.cpp" -o "$tmp/reward"
"$tmp/reward"
g++ "${flags[@]}" "$src/reward_engine.cpp" "$src/trainer_progress.cpp" "$tests/trainer_progress_test.cpp" -o "$tmp/progress"
"$tmp/progress"
g++ "${flags[@]}" "$tests/study_bond_policy_test.cpp" -o "$tmp/bond"
"$tmp/bond"
g++ "${flags[@]}" "$tests/focus_ledger_test.cpp" -o "$tmp/ledger"
"$tmp/ledger"
g++ "${flags[@]}" "$tests/partner_motion_test.cpp" -o "$tmp/motion"
"$tmp/motion"
if command -v openscad >/dev/null; then
  echo "OpenSCAD syntax and profile mesh validation"
  openscad -o "$tmp/angle70.svg" -D 'PART="angle_70"' cad/pokedock_v14_dryfit_templates.scad 2>"$tmp/angle70.log"
  test -s "$tmp/angle70.svg"
  openscad -o "$tmp/v14.stl" cad/pokedock_v14_magsafe_ready.scad 2>"$tmp/v14.log"
  test -s "$tmp/v14.stl"
  echo "OpenSCAD sample geometries parse/export PASS (NOT DFM approval)"
else
  echo "OpenSCAD not installed: SCAD compile BLOCKED (host tests still run)"
fi
echo "V14 host validation complete; ESP-IDF cross-build/real hardware/NVS backend BLOCKED."
