#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
g++ -std=c++17 -Wall -Wextra -Werror -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -I . test_frame.cpp -o /tmp/ghost16_compositor
ASAN_OPTIONS=detect_leaks=1 /tmp/ghost16_compositor
