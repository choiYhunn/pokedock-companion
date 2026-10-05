# BLE Phone Bridge

## Current status

- ESP32-S3 hardware supports BLE.
- UI Lab simulates BLE connect/disconnect plus call/calendar/priority-contact alerts.
- `PhoneEvent` and fragmented BLE frame decoding are defined in core code.
- Real Android/iPhone notification adapters are not yet implemented.

## Recommended topology

- PokéDock: BLE Peripheral / GATT Server.
- Phone: BLE Central.
- Use ESP-IDF NimBLE.

ESP-IDF 5.5 supports NimBLE roles and GATT server operation, and also provides BLE UART examples that are useful for initial bring-up.

## Why an adapter is needed

A BLE connection by itself does not grant generic access to all phone notifications.

### Android

1. Small helper app.
2. `NotificationListenerService` permission.
3. Local allowlist/privacy filtering.
4. Sanitized `PhoneEvent` sent over BLE.

### iPhone

Later adapter:
- ANCS-based accessory integration,
- pairing/bonding,
- selected categories mapped into `PhoneEvent`.

## Privacy defaults

- no full message body,
- no phone-notification persistence to SD,
- allow call/calendar/selected contact only,
- 8-12 second overlay,
- bridge can be disabled completely.

## Bring-up order

Start from the official ESP-IDF NimBLE / BLE UART example to validate:
- advertising,
- pairing/bonding,
- reconnect,
- ATT/MTU behavior,
- Wi-Fi coexistence,
- fragmented writes.

Then route received fragments through `PhoneFrameDecoder`.

## Gift V1 rule

Phone Bridge must never be a blocker. If BLE is disabled or pairing fails, all local study tools and Qi charging still work.
