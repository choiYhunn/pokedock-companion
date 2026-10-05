# V4 acceptance matrix

| Area | Test | Pass |
|---|---|---|
| Mechanical | front edge has no tray projection | visually flush / no wasted desk depth |
| Mechanical | phone can be inserted behind screen one-handed | 10/10 attempts |
| Mechanical | phone remains stable during desk bump | no slip/fall |
| Mechanical | side NFC pod does not project forward | pass |
| Qi | target phone charges through normal case | stable |
| Qi | 60 min charging soak | no abnormal heat / resets |
| NFC | scan while Qi active | reliable 10/10 |
| HMI | cold boot without Wi-Fi | usable offline |
| HMI | missing SD | fallback UI, no crash |
| RTC | power cycle | time retained |
| Focus | 25 min session | completion accurate |
| Focus | pause/resume | no time jump |
| Timer | 10 min countdown | completion accurate |
| Stopwatch | lap / pause / resume | stable |
| Storage | focus session persisted | visible after reboot |
| Study | daily total increments once | no double count |
| Web | config read/write | local LAN only |
| Wi-Fi | NTP unavailable | RTC continues |
| Weather | API unavailable | stale badge, no blocking |
| Dock | C3 powered off | HMI core still works |
| ESP-NOW | Dock heartbeat restored | reconnects without reboot |
| Phone | priority test alert in Focus | small overlay only |
| Phone | non-priority synthetic alert | suppressed |
| Privacy | notification body persistence | none |
