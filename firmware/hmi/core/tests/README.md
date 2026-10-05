# Host core tests

The portable core is intentionally independent from ESP-IDF/LVGL so timing, reward and progression logic can be validated before the physical board arrives.

## Study engine

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

## Reward engine

```bash
g++ -std=c++17 -Wall -Wextra -Werror \
  ../reward_engine.cpp reward_engine_test.cpp \
  -o reward_engine_test
./reward_engine_test
```

Expected:
```
PokéDock reward tests passed
```

## Trainer progression

```bash
g++ -std=c++17 -Wall -Wextra -Werror \
  ../reward_engine.cpp ../trainer_progress.cpp trainer_progress_test.cpp \
  -o trainer_progress_test
./trainer_progress_test
```

Expected:
```
PokéDock progression tests passed
```

## Verified

On 2026-10-05 the reward and trainer-progression tests were also compiled manually with:

```
-std=c++17 -Wall -Wextra -Werror
```

and both executed successfully.

No recurring GitHub Actions workflow is added for these host tests yet because Pages/design commits should not consume unnecessary Actions minutes. Run the tests locally before firmware milestones and before tagging a hardware build.
