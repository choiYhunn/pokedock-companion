# PokéDock V7 — 실사용성·UX 전수점검 (2026-10-18)

## Goal and user-reported preferences
- **압도적 최애: 팬텀 (Gengar)** — main partner, visual identity, subtle ghost animations and hidden Easter eggs.
- **비슷한 2~5순위: 팽도리 / 토게키스 / 루카리오 / 누오** — no forced rank among them.
- Especially likes Generation IV (Sinnoh) and cute collectible goods (plush, mugs, plates, stationery).
- A gift should be both a polished desk object and a useful daily device; being cute must not obstruct the time/timer.

## Current V7 user journey
1. Wake device: clear clock + date + large Gengar.
2. One tap on **NEXT TRAINING** starts the focus countdown.
3. Tap central Poké Ball → **팬텀의 비밀기지**.
4. Four illustrated groups only:
   - 루카리오 / 집중과 수련: Focus, Timer, Stopwatch
   - 팽도리 / 모험과 기록: Quest, Trainer, Egg, Badges, Record, Dex
   - 토게키스 / 책상 생활: Weather, Alarm, Light
   - 누오 / 기기 연결: Phone, NFC, Settings
5. Dex stays one tap away. Secondary activities take two taps after opening Poké Ball.
6. Hidden interaction: tap menu Gengar five times to open a **demo** special event. Production Birthday requires a real date/consent gate and an escape/return route.

The small device should feel like **Sinnoh Pokétch meets Gengar's personal desk hideout**, not a miniature full Pokémon game.

## Utility/value assessment

| Function | Daily value | Status in repository | Priority | Release acceptance |
|---|---|---|---|---|
| Clock / date | Very high | Browser clock works; ESP board integration not verified | P0 | Correct time, RTC holdover, readable at a glance |
| Focus / Pomodoro | High for a regular student; optional for others | Browser demo state + host-side engine, not flashed/soak-tested | P0 | Start/pause/resume/reset; power loss recovery; audible/visual completion |
| Rear phone dock / Qi charging | High if the actual phone fits and aligns | Mechanical concept only; protected charger not tested in assembled dock | P0 conditional | With normal case: stable contact, no slipping, temperature and coil alignment pass |
| Desk display / night brightness | High | Prototype theme; sensor integration pending | P0 | Dim at night; does not disturb sleep or demand attention |
| Alarm | Medium to high | UI simulated; actual RTC/audio path unverified | P1 | Works offline, snooze/dismiss, survives reboot, tolerable volume |
| To-do / D-day | Medium depending on personal routine | Demo data; real simple editor/sync not verified | P1 | Edit from phone browser, persistent storage, no fictional entries |
| Weather | Convenient, not essential | Static sample values in simulator | P2 | Show data age, failure state, location permission, no fake live forecast |
| Study log / charts / EXP | Medium for motivated users | Browser mock + some host core; persistence/integration incomplete | P2 | Save across reboot; accurate session totals; prevent reward abuse |
| Pokémon partner/NFC | High emotional value | Browser interactions only + dock-node scaffold | P1 | Quick and reliable tag scan, theme/art offline, no Qi interference |
| LED ambient themes | Medium emotional value | UI theme preview; physical LED validation pending | P2 | Subtle dimming, off button, no random flashing |
| BLE priority alerts | Uncertain: permission/security friction | Protocol and simulated notifications, no phone OS adapter | P3 | Real phone end-to-end tested, pairing/reconnect, consent and privacy controls |
| Full Dex / Shiny / Badge / Egg | Fun but lower frequency | Demo progression + partial host models | P3 | Optional, no focus distraction, progression never blocks utility |
| Jirachi birthday event | High sentimental value once | Demo event | P2 | Personal message, special trigger, no accidental spoilers, replay/exit |
| OTA | Maintenance convenience | Planned | P2 | Rollback/recovery path and tested safe updates |

Priority meaning: P0 launch blocker, P1 daily usefulness, P2 polish, P3 optional extra.

## Critical reality checks / currently unsupported claims
- Device hardware is **not yet validated as a finished assembly**. Simulated UI does not mean LVGL firmware and dock hardware have been integrated.
- Phone presence from ToF does **not** prove active Qi charging, and does not provide phone battery percentage.
- Standard BLE pairing does **not** by itself expose phone notifications. Android NotificationListenerService helper or iOS ANCS integration is platform-dependent.
- Weather and study statistics in the browser are examples, not network-fetched/live synchronized facts.
- The browsing prototype currently sources Pokémon artwork online, while a real standalone appliance needs **local image assets** and performance tests on microSD/PSRAM.
- Some simulator achievements can be triggered with demo shortcuts; these cannot be treated as verified durable real-device progress.
- Display brightness and ambient LED controls require hardware integration.
- UI text on a physically small 4.3-inch touch panel needs real hand/touch testing at actual size; a desktop full-width simulator can hide small-target problems.
- Physical Qi integration cannot be finalized before confirming phone model/case, actual charger, cable routing, heat, camera bump and anti-slip support.

## Usability risks and mitigations
1. **Too many menus:** show only HOME / Poké Ball / DEX; 4 illustrated sections inside menu.
2. **Cute vs useful:** permanent clock and direct Focus CTA; partner art stays away from primary touch targets.
3. **Focus distraction:** no random popup in an active session; defer encounters/rewards until completion.
4. **Too much RPG progression:** collapse EXP/Bond/Badges to Trainer, not Home; Gengar reaction can be subtle.
5. **Screen sleep/ghost animation:** reduce motion, brightness and LED output at night; give manual disable toggle.
6. **Reboot/power failure:** RTC + persistent user settings, alarm and completed sessions mandatory.
7. **Typing on 4.3-inch:** phone-browser editor for tasks/D-day, touch UI only for short interactions.
8. **Charging hidden behind display:** stable one-handed removal and coil alignment matter more than a compact render.
9. **NFC on the side:** physically demo with representative figure/tag, verify under charging EMI.
10. **Accessibility:** Korean text should not clip; base font and 44-pixel targets verified on real 800×480 display.

## Recommended MVP for birthday gift
**Build first:** clock, Gengar Home, reliable Focus and Timer, normal Qi dock, night mode, one simple personal message, optional local alarm.
**Add only after proven stable:** editable D-day/To-do, NFC character swap, gentle LED, study record.
**Leave post-gift/optional:** full Dex game, Shiny, several badges, always-on BLE notification forwarding, advanced cloud features.

## Testing gates
A. **Browser QA:** boot with empty storage; every Poké Ball group opens; all apps accessible; back/close; Focus starts in one tap; no uncaught JS; no clipped text at 800×480 and 400×240.
B. **Hardware QA:** factory LCD/touch/RTC/SD/audio; C3 ESP-NOW/NFC/ToF/lux; night dim; power cycle; 60 min soak.
C. **Qi QA:** exact target phone in its case with selected protected charger; charge stability and heat check; antislip/bump check.
D. **User acceptance:** without instructions, can she read time and start/pause focus? Does Gengar make the gift feel personal? Does the device remain pleasant when not being interacted with?

## Current evidence limits
This document is a repository/code audit and heuristic UX review, not user research or a physical-device validation. The browser preview is a simulator; unverified integrations must remain labeled.
