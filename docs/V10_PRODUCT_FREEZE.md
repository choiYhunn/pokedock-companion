# PokéDock V10 — Product and UX freeze (2026-10-18)

## Decision
A **useful desk appliance with a hidden Pokémon playground**, not a productivity dashboard with too many equal-priority apps. No separate game-mode toggle needed.

## Always-visible controls
1. HOME: clock, Gengar partner, one-tap Focus, daily tasks and D-day.
2. 집중: timed Focus session and subsequent rest.
3. Poké Ball: opens only two primary categories **매일 쓰는 도구** and **포켓몬 놀이**. Additional utilities/settings are in a quieter secondary category.

### 매일 쓰는 도구
Today To-Do / D-day, plain countdown timer, alarm, our private couple nook.

### 포켓몬 놀이
Party selection, Dex, Egg, Trainer, Badge, Record. A deferred encounter is explicitly accessible here.

### 추가 기능 · 설정
Night/brightness, ambient lighting, sample weather, phone-presence demo, NFC demo and stopwatch. Low priority until independently implemented.

## Essential distinction
- **Focus:** user chooses 15/25/45 min; study completed ONCE -> Study EXP + one reward decision -> 5 min rest. Rest NEVER awards EXP. Pause and restart controls visible. Works in background inside web demo.
- **Plain timer:** 3/5/10/30 min preset countdown for cooking/stretching, does not update study metrics or Pokémon rewards.
- **Stopwatch:** counts upwards and supports lap, tucked into additional tools.

## Reward contract
Encounter is not added to caught list until user explicitly taps **도감에 기록**. Pressing **나중에** defers the encounter; it can be resumed from the Poké Ball PLAY group. Back from reward defers it rather than auto-catching. Confirming opens Dex and shows the new entry (including previously absent encounter IDs).

## Back stack
A secondary screen has upper-left **← 뒤로**. If entered via menu group, Back returns to that group, then root menu, then HOME. HOME clears history. During Focus, leaving the screen does not automatically pause the running timer. Party selector provides ×/Esc. Browser demo panel remains hidden unless enabled for testing.

## Minimum birthday gift
**Must work physically:** clock + RTC, clear Focus and plain timer, working touch/back, stable protected MagSafe charger with external power, safe/dim night mode, Gengar living-idle. Local private note/date and 1-page todo are valuable P1 features.
**Nice to have after:** offline party animation, NFC figurines, gentle light, self-reported charging presence.
**Not gift blockers:** Shiny, full game economy, iOS ANCS, complex weather/graphs, second MCU, over-the-air asset pack downloader.

## Caveats
V10 is a browser simulator plus portable C++ core. Some status/forecast/logging remains demo data. Weather sync, LVGL device UI, real iPhone ANCS, charging verification, firmware OTA and sensor bridge are not yet proven on the physical board. Browser data is localStorage, not encrypted.
