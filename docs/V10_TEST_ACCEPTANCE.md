# PokéDock V10 — QA / release gate

## Browser test matrix: test the actual public page, not just JS syntax

1. HOME boots with current local clock, Gengar, prominent Focus action, task/D-day; refresh doesn't erase local entries.
2. Persistent HOME / 집중 / Poké Ball controls only. Main Poké Ball shows DAILY / PLAY as primary, MORE secondary.
3. Enter PLAY -> Dex -> Back should restore PLAY submenu -> Back root -> Back closes drawer.
4. Enter DAILY -> regular timer; labels explicitly state "countdown only / no study reward"; preset controls only affect ordinary timer.
5. Focus 25 min + 5 min rest: pause/resume; choose 15/25/45 before starting; Focus completion exactly once; break completion yields no EXP.
6. Reward has "도감에 기록" and "나중에"; the latter saves a pending encounter; revisit it from PLAY; registration changes caught count and new-entry Dex row.
7. Party selection opens, keyboard/touch select/confirm updates partner, close returns; Back from other pages remains available.
8. Todo add/complete/delete, D-day title/date, couple note/date and partner selection survive page reload in same browser profile.
9. 800x480 in Chromium: capture each major screen with actual physical-size dimensions, check no clipped Korean text/crowded 44px-equivalent touch targets; screen reader focus/contrast also needs review.
10. Browser weather, BLE, charging and study totals remain explicitly labeled demo where unconnected.

## Completed in V10 development
- [x] Embedded simulator JavaScript syntax parse.
- [x] Mocked HOME -> Poké Ball -> PLAY -> Dex -> Back to PLAY -> root -> close.
- [x] Mocked 25-minute Focus -> 5-minute rest -> return to study.
- [x] Mocked reward later -> pending entry -> explicit register -> Dex displays Vulpix and persists to browser storage.
- [x] Focus rewards not granted for plain countdown/rest in the tested flow.
- [ ] Real browser screenshot/pixel audit at 800x480 (not yet performed in V10).
- [ ] Hardware LVGL implementation (not yet).
- [ ] Device touch/charging/night use with intended user (not yet).

## Real-device blockers
- Correct SKU 33630 + PCB revision, voltage/polarity and insulation confirmed.
- Factory LCD/touch/RTC/SD/audio interface smoke on board.
- Native Focus 25/5 with NVS saved sessions/time across 5 power cycles.
- Real MagSafe charger 60min, verified iPhone 14 model and case; 30 safe one-hand docking cycles.
- Hardware UI all screens reachable with reliable back path and legibility.
- Optional OTA requires rollback and recovery fault-injection; if not validated, launch supports USB updates only.
- All private notes erased on request without appearing in serial logs.
- If Wi-Fi absent, offline clock (RTC) and timer remain functional.

## Nonblocking extras
iOS ANCS notifications, NFC figures, 3D printed enclosure, Shiny rewards, full animated Dex, fancy night LEDs and live weather can ship as later experiments without delaying the useful gift.
