# Product V3 — Pokémon Study / Desk Companion

## Product identity
PokéDock is no longer defined as a decorative smart clock. It is a **daily-use study and desk companion** whose utilities are expressed through Pokémon characters.

## Hardware capability baseline
The Waveshare ESP32-S3-Touch-LCD-4.3C provides:
- 2.4 GHz Wi-Fi and BLE
- 4.3-inch 800×480 capacitive touch display
- ESP32-S3R8 at up to 240 MHz
- 8 MB PSRAM and 16 MB Flash
- PCF85063 RTC
- microSD / TF slot
- ES8311 audio codec + ES7210 audio ADC

## V1 core
- Clock / date
- RTC + NTP sync
- Alarm
- Pomodoro / focus presets and custom sessions
- Countdown timer
- Stopwatch + lap
- Study-session logging to microSD
- Daily / weekly total and streak
- D-day / small to-do list
- Weather summary over Wi-Fi
- Local web settings from phone
- Ambient / night mode
- Qi charging
- NFC Pokémon mode
- Study EXP / encounter rewards
- Birthday special event

## Connectivity policy
Offline-critical:
- clock
- timer
- stopwatch
- alarms
- study log
- NFC / lighting

Wi-Fi-enhanced:
- NTP
- weather
- local web settings
- OTA
- later: calendar relay / remote messages

## UX rule
Device touch UI is for quick actions.
Phone web UI is for text-heavy configuration.

## Pokémon role mapping
- Lucario: Focus
- Togepi: morning / positive start
- Pachirisu: charging
- Gengar: night
- Togekiss: calm / daily summary
- Jirachi: birthday / wishes
- Future additions can map to weather, break mode, achievement and subject themes.

## V2 candidates
- iCal / Google Calendar relay
- remote message sync
- white-noise / local audio scenes
- timetable sync
- richer study analytics
