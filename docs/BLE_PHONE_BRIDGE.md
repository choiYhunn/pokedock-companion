# BLE Phone Bridge

## Current status

- ESP32-S3 hardware supports BLE.
- UI Lab simulates BLE connect/disconnect plus call/calendar/priority-contact alerts.
- `PhoneEvent` and fragmented BLE frame decoding are defined in core code.
- Real Android/iPhone notification adapters are not yet implemented.

## Two alternative topologies — do not conflate

**iOS ANCS direct notification path (recommended if iPhone notification relay is actually required):**
- The iPhone hosts ANCS as Notification Provider.
- PokéDock must act as ANCS Notification Consumer with GATT client support; pairing/authorization and Service Changed handling are necessary.
- ANCS category-filtered incoming-call / schedule event summaries can be investigated. Selected-person contact filtering is not guaranteed from ANCS alone.
- Use ESP-IDF BLE stack support after confirming controller and ANCS role in a real prototype.

**Custom mobile-app GATT service path:**
- A purpose-built phone app could connect to PokéDock as a BLE peripheral/GATT server.
- A generic iOS app cannot simply read every system notification like Android NotificationListenerService.
- This is NOT interchangeable with ANCS.


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


## iPhone 14 and gift acceptance

See [iPhone V8 integration](IPHONE_14_INTEGRATION_V8.md). Keep notifications optional; prototype direct iOS ANCS, do not claim that BLE connection simulation forwards real notifications.
