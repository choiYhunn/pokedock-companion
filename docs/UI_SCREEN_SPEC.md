# UI Screen Specification — V4

The Pages UI Lab is the visual source of truth for screen-level review.

Live:
- https://choiyhunn.github.io/pokedock-companion/

## Global rules
- Native target: **800×480 landscape**.
- Touch targets should be comfortably tappable at arm's length.
- Default screen is glanceable within 1–2 seconds.
- Long text editing belongs to the phone web UI.
- Focus mode suppresses non-priority visual interruptions.
- Night mode reduces brightness, motion and contrast spikes.
- Pokémon character art is decorative/semantic; critical information never depends on the artwork loading.

## Screens

### 1. HOME
Purpose: ambient clock + daily glance.
Shows:
- time/date
- current companion
- today's focus total / goal
- nearest D-day
- weather
- next action

### 2. FOCUS
Purpose: Pomodoro.
Shows:
- large remaining time
- progress
- pause/+5/reset
- focus buddy
- only priority notification overlay

### 3. TIMER
Purpose: general countdown.
Presets:
- 5 / 10 / 30 min
- custom from web UI or device picker

### 4. STOPWATCH
Purpose: study, exercise, cooking.
Actions:
- start/pause
- lap
- reset

### 5. TODAY
Purpose: current-day execution.
Shows max 5 tasks plus daily study progress.

### 6. STATS
Purpose: lightweight motivation.
Shows:
- week total
- sessions
- streak
- daily breakdown
Avoid dense analytics on the 4.3-inch screen.

### 7. DEX
Purpose: reward/progression.
Sources:
- study session rewards
- NFC
- birthday events
- streak milestones

### 8. NFC
Purpose: confirm side-pod scan and show mapped character/theme.
Must clearly indicate unknown tags vs enrolled tags.

### 9. WEATHER
Purpose: useful ambient info.
Network failure: show stale badge, never block HOME.

### 10. ALARM
Purpose: bedside use.
Alarm engine is offline RTC-based.

### 11. PHONE
Purpose: rear-phone and priority notification status.
Never show full chat content by default.

### 12. LIGHT
Purpose: ambient presets.
Themes map to companion roles, not arbitrary RGB sliders first.

### 13. SETTINGS
Purpose: quick toggles only.
Text-heavy settings redirect to local web UI.

### 14. BIRTHDAY
Purpose: one-day secret event.
Priority above Focus/Dock/Night except alarm/safety.

### 15. NIGHT
Purpose: global low-stimulation skin, not a separate normal navigation tab.

## Navigation
Primary persistent tabs:
- HOME
- FOCUS
- TOOLS
- TODAY
- DEX

Secondary:
- WEATHER / ALARM / PHONE / LIGHT / SETTINGS from HOME cards or gear.

This keeps the bottom bar from becoming crowded.
