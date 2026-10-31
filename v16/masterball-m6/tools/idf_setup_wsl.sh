#!/usr/bin/env bash
# One-time ESP-IDF v5.3.2 toolchain install inside WSL Ubuntu (user space, no sudo needed).
# Run in WSL:  bash tools/idf_setup_wsl.sh
set -euo pipefail
mkdir -p ~/m6idf && cd ~/m6idf
command -v ~/.local/bin/uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
~/.local/bin/uv python install 3.11
export PATH="$(dirname "$(~/.local/bin/uv python find 3.11)"):$PATH"
[ -d esp-idf ] || git clone -q --depth 1 --branch v5.3.2 --recursive --shallow-submodules https://github.com/espressif/esp-idf.git
cd esp-idf && ./install.sh esp32s3
echo "ESP-IDF v5.3.2 ready in ~/m6idf/esp-idf"
