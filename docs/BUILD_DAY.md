# Build Day — V4

The build day is for assembly and hardware validation, not feature invention.

## 0. Before build day
Already complete:
- V4 physical layout chosen.
- HMI / Dock split chosen.
- study core logic in repository.
- phone bridge defined as optional.
- local web configuration UX defined.

Must be ready:
- exact target phone + normal case.
- Qi charger tested with that phone.
- all cables cut/labelled.
- Waveshare factory recovery image downloaded.
- HMI and Dock toolchains installed.

## 1. HMI bring-up
Verify with factory firmware first:
- LCD
- touch
- Wi-Fi
- RTC
- microSD
- speaker

Do not flash PokéDock until all pass.

## 2. Rear phone support test
Before final mounting:
- place the actual phone behind the HMI,
- choose 65–75° support angle,
- verify camera bump/case clearance,
- align the Qi coil,
- verify one-hand insertion/removal,
- verify that the phone does not fall when desk is bumped.

The rear support is a slope, not a deep pocket.

## 3. Side NFC pod
- mount on right by default,
- keep front edge flush with main base,
- validate NFC with the phone charging,
- move farther from Qi if scan reliability degrades.

## 4. Dock node
Validate separately:
- BH1750
- VL53L0X phone parked detection
- PN532
- RGB LED
- ESP-NOW heartbeat

## 5. Study functions
Acceptance order:
1. clock / RTC
2. focus 25 min
3. pause/resume
4. timer
5. stopwatch / lap
6. save one study session
7. power-cycle and confirm recovery
8. D-day / todo
9. NTP
10. weather
11. local web settings

## 6. Phone bridge
Do not make this a blocker.
If time remains, only test synthetic priority notifications.
Real Android/iPhone forwarding is V1.1 unless the platform adapter is already stable.

## 7. 60-minute soak
Run:
- screen on,
- Wi-Fi connected,
- phone charging behind,
- Dock sensors active,
- periodic UI updates.

Check:
- charging stability,
- heat around phone/Qi area,
- ESP resets,
- touch responsiveness,
- false phone-presence transitions,
- false NFC reads.
