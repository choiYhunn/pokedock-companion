# V4 Design Review Checklist

Use the live UI Lab:
https://choiyhunn.github.io/pokedock-companion/

The purpose of this document is to record decisions after visually reviewing the actual 800×480 mockups.

## A. Physical product

Current canonical:
- [x] no front charging tray
- [x] HMI is the visual center
- [x] phone behind HMI
- [x] simple rear slope rather than deep phone slot
- [x] rear Qi charging
- [x] NFC moved to side pod
- [x] side pod does not extend forward beyond base
- [x] subtle underside light
- [x] 3D print optional

Still to validate with physical parts:
- [ ] exact base depth
- [ ] exact rear slope angle
- [ ] phone camera-bump clearance
- [ ] target phone case + Qi alignment
- [ ] side pod right vs left final preference
- [ ] NFC reliability while Qi is active

## B. HOME
Check:
- [ ] clock large enough
- [ ] character large enough
- [ ] daily study amount useful
- [ ] D-day useful
- [ ] weather useful
- [ ] next todo useful
- [ ] too much information / too little information

## C. FOCUS
Check:
- [ ] timer should dominate enough
- [ ] Lucario size
- [ ] progress bar
- [ ] Pause / +5 / Reset wording
- [ ] whether subject label is needed
- [ ] priority notification overlay size

## D. TIMER / STOPWATCH
Check:
- [ ] separate screens vs one TOOLS screen
- [ ] preset durations
- [ ] lap list density
- [ ] whether timer needs sound selection

## E. TODAY / STATS
Check:
- [ ] max 5 todos is enough
- [ ] D-day placement
- [ ] study target useful
- [ ] streak feels motivating rather than annoying
- [ ] weekly stats should stay lightweight

## F. DEX / NFC
Check:
- [ ] Dex grid density
- [ ] locked silhouette vs text
- [ ] reward mechanic
- [ ] NFC confirmation animation
- [ ] side figure/tag interaction feels worth the hardware

## G. WEATHER / ALARM
Check:
- [ ] weather deserves a full screen
- [ ] alarm list layout
- [ ] bedtime/night transition
- [ ] alarm sound / volume UX

## H. PHONE
Check:
- [ ] phone should remain mostly invisible physically
- [ ] only priority notification summaries
- [ ] no message body by default
- [ ] call/calendar/contact categories are enough
- [ ] phone bridge worth implementing for target phone OS

## I. LIGHT / NIGHT
Check:
- [ ] themed presets are better than raw RGB controls
- [ ] night brightness cap
- [ ] animation reduction
- [ ] Gengar night theme is desirable

## J. BIRTHDAY
Check:
- [ ] amount of romance
- [ ] event duration
- [ ] Jirachi flow
- [ ] whether a secret NFC tag should unlock an additional message

## Review rule
Do not expand hardware merely because a screen looks empty.
Prefer better hierarchy, animation and character behavior before adding another sensor/module.
