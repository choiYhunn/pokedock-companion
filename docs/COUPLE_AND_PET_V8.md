# V8: living desk companion and private couple nook

## UI identity
- Gengar is the default partner and visibly floats very slightly on HOME.
- Tap partner art to see one of several short reactions.
- Every fifth touch opens a discreet **우리의 작은 서랍** (Easter egg).
- The menu Gengar also opens it after five taps; secondary entry is available under Desk.
- Reduce movement when OS/device reduced-motion or Night behavior warrants it; no flashing.
- Keep clock, Focus and controls legible. Animation cannot obscure useful text.

## Couple space (browser implementation)
- Actual anniversary date is user-supplied, not hardcoded.
- Days since / days until date use local calendar days with midday normalization.
- Personal note (160 characters), no hardcoded private message.
- User can save/clear anniversary and note in the browser UI.
- All values remain in browser localStorage key `pokedock-private-v8`; they are not sent to GitHub or an application server.
- Local storage is **not encrypted**: anyone with access to that browser profile may see the contents. This is a UI prototype, not high-security secret storage.

## Practical planner (browser implementation)
- Up to five user-entered To-Dos.
- Tap to complete, remove or add a new task.
- Title + date D-day, correctly displayed relative to device-local date.
- Persist across reload in the same local browser profile.
- The current clock refreshes as time passes.
- Browser timers account for background timer throttling by advancing elapsed wall time.

## Firmware-porting requirements (not completed yet)
- Validate LVGL touch hit boxes at 800x480 on the real 4.3-inch panel.
- Persist partner preference, alarms, time and completed focus sessions in NVS/microSD with versioned settings.
- Implement local couple storage/settings with explicit delete and optional privacy lock on the real device.
- Disable animations during Focus/Night and honor reduced-motion preference.
- All Pokémon art required for offline runtime must be licensed/owned/locally provided, asset sized for microSD/PSRAM; online PokeAPI references are browser-demo assets.
- A device should continue working if BLE, weather or Internet never connect.

## UX acceptance scenarios
- Read time without touching, start Focus in one tap, pause/reset clearly.
- Enter two tasks and one D-day, reload UI and confirm both persist.
- Enter anniversary date and short letter, reload and confirm both persist, then clear all private content.
- Tap Gengar five times; secret space opens but can always return to Home.
- Change partner; artwork stays away from essential timer digits/buttons.
- Keep app on desk for a full evening without unwanted noise or distracting motion.
