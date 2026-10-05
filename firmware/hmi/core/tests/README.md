# Host core tests

The study/timer and notification-policy core is intentionally independent from ESP-IDF/LVGL.

Run on any machine with g++:

```bash
cd firmware/hmi/core/tests
g++ -std=c++17 -Wall -Wextra -Werror \
  ../study_engine.cpp study_engine_test.cpp \
  -o study_engine_test
./study_engine_test
```

Expected:
```
PokéDock core tests passed
```

Verified once during V4 design on 2026-10-05.

No GitHub Actions workflow is added for this test yet because this personal project does not need to consume recurring CI minutes for every Pages/design commit. Run it locally before firmware milestones.
