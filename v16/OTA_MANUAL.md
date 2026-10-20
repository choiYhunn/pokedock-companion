# V16 — Explicitly User-Initiated Updates
**State: design and reference hooks only. NOT enabled, NOT flashed, NOT physically tested.**
No periodic background network checks, Github Actions schedules, or automatic installation.

## Two distinct update tracks
Firmware: Settings > Check > release notes / version / board ID > Install > inactive OTA app slot > reboot > postboot health mark > confirmation.
Character asset pack: Settings > Add animation > verify **signed** manifest (not just HTTPS or a hash distributed by the same host) > download to inactive directory > validate all files/contract > atomic active pointer switch > retain previous pack and built-in fallback.
OTA cannot replace bad optics, add physical sensors or change the PCB. Plain private messages / settings never go into public firmware images.

## Security / availability requirements before enabling
1. Exact ESP-IDF version and partition CSV; 16MiB flash verified with vendor device and app size < slot (plus reserved space). Back up factory image/USB UART/JTAG recovery procedure.
2. Trusted Wi-Fi, correct clock, TLS hostname and CA bundle/pinned certificate. Avoid arbitrary URL entry and redirect to untrusted host.
3. Signed app or secure-boot verification (not simply checking the URL); controlled release channel and anti-rollback compatible with necessary recovery.
4. Physical or local authenticated confirmation; refuse while focus/alarm is active, while power is uncertain, or memory is too low.
5. Configure bootloader app rollback with **APP-CONTROLLED post-boot confirmation**, never mark valid before display/input/clock/storage state works.
6. Manual update UI includes Cancel. No unattended download/installation or noisy email/CI jobs.
7. Asset manifest: board, asset_api_version, pack_id, version, total max bytes, individually hashed files, signature Ed25519 or supported verified equivalent with trusted key pinned in device. Stage whole pack and atomically swap pointer only after validation.
8. Missing microSD, corrupt media, partial download, bad signature, missing assets, wrong board, TLS failure, and a hard power cut must leave a known-good app and fallback graphics. Repeat 5 update/rollback cycles on physical hardware.
9. User's private notes are stored locally separately from OTA app/asset partitions; redact logs and provide delete control.

## Implementation demarcation
- v16/simulator implements a UI **illustration only**. 'Check for updates' tells the user that there is no OTA service.
- Firmware-specific HTTPS OTA must be integrated with the confirmed panel driver, network, manifest verification, signature policy and board health checks. Avoid claiming compatibility with the old 4.3C BSP.
- Offline USB flashing remains an essential rescue.
- Official API: https://docs.espressif.com/projects/esp-idf/en/v5.5.1/esp32s3/api-reference/system/esp_https_ota.html
