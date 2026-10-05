# LVGL Screen Build Plan

The Pages UI Lab is the visual target for the embedded 800×480 UI.

## Shared components
- TopStatusBar
- BottomNav
- Card
- CharacterArt
- ProgressBar
- PriorityNoticeOverlay
- EmptyState
- Error/StaleBadge

## Screen inventory
1. HomeScreen
2. FocusScreen
3. TimerScreen
4. StopwatchScreen
5. TodayScreen
6. StatsScreen
7. DexScreen
8. NfcScreen
9. WeatherScreen
10. AlarmScreen
11. PhoneScreen
12. LightScreen
13. SettingsScreen
14. BirthdayScreen
15. NightSkin

## Contract
Screens consume immutable view-model snapshots.

Screens do not:
- write SD,
- call weather APIs,
- own timer logic,
- parse phone notifications,
- call ESP-NOW directly.

Flow:
UiAction -> Controller -> Engine/Service -> ViewModel -> LVGL render.

## Performance
- Load character assets from microSD.
- Use small thumbnails in Dex.
- Cache current/next art in PSRAM when practical.
- Timer/clock text can refresh at 1 Hz.
- Network callbacks post messages/queues; they never manipulate LVGL directly.
