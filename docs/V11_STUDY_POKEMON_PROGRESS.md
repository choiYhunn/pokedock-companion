# PokéDock V11 — natural study-to-Pokémon progression (policy, not an implemented web release)

## Product principle
Do not force the recipient to choose between doing useful study and playing a full game. She sees the clock, favorite Gengar and a clear Focus button; **only after a naturally completed Focus session** does a subtle Pokémon response happen. PLAY is an optional place to inspect earned things later.

- Countdown presets: 15 / 25 / 45 min. 5-min break does not earn study credit.
- Study time is granted on completion only once; pause time, resets, abandoned timers, general timer and stopwatch do not earn study credit.
- The **amount of completed minutes** counts, not how often Start is pressed. Fifteen plus forty-five minutes equals sixty.
- Offline-first: accumulate trustworthy monotonic timer time and RTC local date; sync across power cycles with versioned NVS journal and unique committed session IDs.
- Do not reward indefinite screen-on idle time. Physical device version must audit power interruption and exactly-once completion semantics.
- Never punish an off day or reset all progress due to a missed streak. Character bond is capped to +2/day; cumulative study minutes continue to count after the daily cosmetic cap.

## Explicit accumulation milestones — first proposal

| Verified cumulative Focus | Unlock | What she sees | Nonintrusive by default |
| --- | --- | --- | --- |
| each 60 min | +1 star in small Trainer shelf | quiet +1 ✦ after session, not during | yes |
| first 60 min | Gengar playful response | brief Gengar peeking / a short encouraging line | yes |
| 120 min (2h) | Piplup postcard | a cute illustration / optional first encounter card | optional |
| 300 min (5h) | Mystery Egg hatch | special hatch animation, added to souvenir album only on confirmation | optional |
| 600 min (10h) | Focus Badge | one badge, original PokéDock achievement | optional |
| 1200 min (20h) | Room theme | unlock room background/decoration, not critical firmware function | optional |

Later cumulative star counts may decorate the room but **never block clock, alarm or timer**. "Random Shiny" and other mechanics can exist in an opt-in development sandbox, but should not monopolize the primary UX.

## Exact example
- Day 1: Focus 25min → credited total 25min, Gengar smiles and a quiet "잘했어". No star.
- Day 1: Focus 45min → credited total 70min, 1 star and first Gengar milestone. Study minutes credited accurately.
- Day 2: Focus 45min → total 115min (no fabricated 2-hour reward).
- Day 2: Focus 15min → 130min, Piplup postcard unlock at 120min. Do not interrupt timer completion page if user selected "later".
- The plain 3min cooking timer never changes study record.

## Why cumulative, not per-session coin farming
Session-completion-based rewards overvalue repeated 15min starts and discourage realistic 45min study. Credited minute thresholds stay fair. Cosmetic bond +1 for first two completions/day supports delight without pressuring daily long sessions.

## Engineering contract
Portable future firmware policy: \`firmware/hmi/core/study_bond_policy.h\` and \`firmware/hmi/core/tests/study_bond_policy_test.cpp\`.
- Input must come from a verified completed Focus timer only, not arbitrary UI "Demo Clear" callbacks.
- Inputs: monotonically increasing durable session ID, chosen completed duration in {15,25,45}, validated nondecreasing calendar key YYYYMMDD (month/day/leap-year check) from a confirmed RTC/time-sync state.
- Output: accepted, minutes credited, stars crossed, milestone bitmask, bond feedback.
- Ensure NVS journal records the completion atomically before displaying unlock animation. If power loss happens during commit, recover/reconcile ID; no duplicate awarding.
- Future versions may allow custom durations, but then threshold credit based on verified time and validation must be explicit.

## UI integration (later)
- Focus completion: short transition; "누적 공부 1시간 ✦" when milestone crossed; "나중에 보기" always available.
- PLAY / 포켓몬 놀이: small dedicated "별·기념품" shelf where older postcards, eggs and badges are accessible. This is more natural than interrupting work with a full-screen catch every 25min.
- Gengar idle animation and our private note remain available even with zero study time. No coercive "you are falling behind" messages.
- Disable celebration during night/quiet mode; subtle static badge can show next time instead.

## Audio personalization later
- Alarm supports quiet bundled generic sounds plus **imported user-owned PCM WAV** via microSD/local web configuration, only when ES8311 speaker route verified.
- Pokémon game cries/music have copyright; no ripped files bundled into public firmware. No music stream from iPhone without specific legal streaming interface. Voice volume/mute/quiet-hours and stop/snooze prioritized over Pokémon effects.
- See \`docs/V11_ELECTRICAL_WIRING.md\`.

## Current release reality
**This V11 policy is compiled as portable C++ and documented, but not connected to the V10 browser simulator or flashed native LVGL hardware yet.** No claim that EXP thresholds are currently active in the device. User requested careful later development; freeze clear rules first.

## Test from repo root

```bash
g++ -std=c++17 -Wall -Wextra -Werror firmware/hmi/core/tests/study_bond_policy_test.cpp -o /tmp/pokedock_study_policy_test
/tmp/pokedock_study_policy_test
```

This is a host-side portable rule test, not a flashed MCU validation. RTC invalid/rollback dates reject date-dependent credit until the device time is reconciled; the study timer itself must still work independently.
