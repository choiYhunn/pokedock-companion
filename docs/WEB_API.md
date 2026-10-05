# Local Web API contract

Base URL when connected to the same network:

`http://pokedock.local/`

## GET /api/state

Returns current non-sensitive state.

```json
{
  "mode": "focus",
  "focus_remaining_s": 1182,
  "today_focus_s": 6300,
  "sessions": 3,
  "streak_days": 4,
  "wifi": true,
  "phone_bridge": false,
  "phone_parked": true,
  "lux": 18.4
}
```

## GET /api/config

Returns editable settings. Never returns Wi-Fi passwords.

## PUT /api/config

Accepts:
- focus duration
- break duration
- daily target
- night start/end
- notification privacy
- side NFC position
- birthday
- preferred character roles

## GET /api/todos
## PUT /api/todos

Maximum recommended visible items: 5.

## POST /api/timer

Body:
```json
{"action":"start_focus","duration_s":1500}
```

Allowed actions:
- start_focus
- start_countdown
- pause
- resume
- stop
- stopwatch_start
- stopwatch_lap
- stopwatch_stop

## POST /api/phone/test

Injects a synthetic priority notification for UI testing only.

## POST /api/system/reboot

Requires a confirmation token created on-device.

## Security
V1 local-only:
- bind to LAN interface only,
- never expose directly to the public internet,
- no credentials in repository,
- settings writes require a per-device local token after initial setup.
