# iPhone 14-family integration — V8 hardware/firmware decision

## Assumption, not confirmation
The recipient uses an iPhone, reportedly "14" (exact iPhone 14/14 Plus/14 Pro/Pro Max uncertain). Do not machine the final phone slope, camera clearance, magnet holder or chassis before checking the precise model and case.

## Charging source of truth
Apple iPhone 14 technical specs: MagSafe wireless charging up to 15 W; generic Qi wireless charging up to 7.5 W. Use a reputable protected MagSafe charger with the specified compatible USB-C power adapter, not a custom Qi transmitter board. Real-world speed/thermal limits may differ.

- Apple iPhone 14 specs: https://support.apple.com/ko-kr/111850
- Apple MagSafe usage: https://support.apple.com/ko-kr/105047

## Placement
- Screen remains forward. Phone is fully/mostly behind screen on a simple, stable rear ramp.
- A commercial MagSafe puck handles magnetic alignment. Build an anti-slip ledge and cable strain relief.
- The phone must be removable with one hand, with case/camera-bump clearance.
- Independently power/protect the charging puck; leave airflow and separation from PN532 NFC, MCU and RGB wiring.
- Side NFC target must be tested while the phone is charging; avoid EMI-based assumptions.
- Do not treat VL53L0X phone presence as verified active charging or remaining battery %.

## BLE/iOS notifications: correctly defined architecture
Apple Notification Center Service (ANCS) is hosted by the iOS device. PokéDock is the Notification Consumer (NC): it needs a BLE GATT client for ANCS, authorization, subscriptions and reconnection logic. Prior suggestions to implement only a PokéDock GATT server with phone GATT client are insufficient for direct ANCS.

- Apple ANCS: https://developer.apple.com/library/archive/documentation/CoreBluetooth/Reference/AppleNotificationCenterServiceSpecification/Specification/Specification.html
- iOS categories include IncomingCall, Schedule, Social etc., with GATT Notification Source and optional Control/Data Source features.
- Filter *category* before retrieving metadata. Incoming calls/calendar/schedule may be shown as short privacy-preserving notifications if permitted.
- Selecting arbitrary specific contacts is NOT guaranteed from basic ANCS alone. Do not claim contact allowlist works before proving the actual fields and OS behavior.
- ANCS can appear/disappear; subscriptions must respect Service Changed.
- Pairing/bonding and unauthorized states must be handled. No full message bodies stored.
- The initial gift can omit BLE notifications with zero loss of clock, timer, Qi and locally configured couple features.

## Release acceptance
1. Confirm actual iPhone model and case dimensions.
2. MagSafe alignment and repeated dock/undock for 30+ cycles; no slipping.
3. Charging stability and phone/chassis temperature during 60-minute run.
4. Display/NFC/ESP-NOW survive charging active.
5. Night brightness, silent mode and overnight stability.
6. ANCS end-to-end proof only if pursued later; otherwise keep app toggles explicitly in demo mode.

The GitHub Pages UI is a *simulator*, not evidence that the complete assembly works.
