# PokéDock — over-the-air UI updates (V9 plan)

## Status

**Design/partition proposal only. Not yet compiled, flashed, provisioned or OTA-tested on Waveshare hardware.**

Board: Waveshare ESP32-S3-Touch-LCD-4.3C-BOX SKU 33630, 800×480 LVGL target, ESP32-S3 + 16 MiB flash + 8 MiB PSRAM, Wi-Fi, microSD. Waveshare vendor BSP still requires physical bring-up.

## What can be updated?

| Change | Mechanism | Cost / impact |
|---|---|---|
| LVGL layout, buttons, navigation, partner logic | **App firmware OTA** | Upload new signed/verified `.bin`; reboot with rollback |
| Animation timing or interpolation code | **App firmware OTA** | Ditto |
| Embedded images / fonts / sprites compiled into app | **App firmware OTA** | Ditto; firmware image size grows |
| Pokémon portraits, spritesheets, sounds stored as external resources | **Asset bundle update** (future, preferably microSD with A/B or atomic swap) | Does not require replacing app if asset contract compatible |
| To-Dos, D-days, private couple message | **User settings/data (NVS or SD)** | Preserve on app OTA, never package personal data in a public firmware release |
| Layout changes that need extra GPIO / power / enclosure space | Physical design change | OTA cannot alter hardware |

## Preliminary 16MiB table

See `partitions_16m_ota_PROPOSED.csv` in this folder.

- 0x000000—0x01FFFF: bootloader/partition metadata/NVS/otadata/PHY/padding
- `ota_0`: 6 MiB, from 0x020000
- `ota_1`: 6 MiB, from 0x620000
- `ui_store`: example 2 MiB `spiffs` partition from 0xC20000 (not yet mounted or used)
- Spare flash remains for revisions / diagnostic storage.

The two OTA app slots can hold the current and the next firmware, but **6 MiB per slot must be validated against the actual built size**. If a large multimedia application needs bigger slots, rebalance app/resource partition sizes before the first release. The partition table offset, bootloader footprint and IDF toolchain settings must be verified first. Do not switch an already flashed layout in-place without a migration/recovery plan.

## OTA first-release contract

1. Device boots with an immutable minimal HOME/recovery path and a valid LVGL display/touch driver.
2. ESP-IDF config enables custom partition CSV and rollback, with **app-controlled confirmation** only after critical LCD, touch, RTC, storage and app state pass health checks. Check exact IDF-version Kconfig names.
3. User opens Settings → Update, sees current/candidate version, size, source, release notes and asks to install. Never surprise-update during Focus/alarms or while battery/power is unstable.
4. Download app image over HTTPS using `esp_https_ota`, validate TLS server identity and (preferably) firmware signing / secure boot. Reject wrong board identity, firmware size, schema or incompatible app version.
5. Write only the inactive OTA app slot, reboot, then verify essential peripherals and app health.
6. On success call `esp_ota_mark_app_valid_cancel_rollback()`; on critical failure call `esp_ota_mark_app_invalid_rollback_and_reboot()`.
7. Keep NVS/private notes/quests outside OTA app slots. Version the data schema and migrate atomically with backup. Never log the private letter.
8. Power loss and invalid binaries must leave the previous image bootable; add a USB recovery SOP.
9. HMI and the separate ESP32-C3 Dock Node use different firmware images and require **separate OTA flows**, not one shared binary.

## Asset updates: do not fake them

MicroSD is a good fit for offline animation assets. A safe future asset manager needs:
- signed or strongly authenticated manifest, compatible `app_api_version`, per-file SHA-256, total size;
- staging to a *different* directory or partition, not the directory currently used by LVGL;
- CRC/hash and completeness checks before flipping a tiny active-pack pointer atomically;
- keep old pack until successful asset initialization, then garbage-collect;
- a built-in low-memory default image/animation theme if card or assets fail;
- a copyright/license decision for Pokémon images before distributing artwork.

**This asset updater is not implemented.** The existing browser simulator uses online sprites and official artwork URLs and is not the device runtime.

## First bench test plan

- OTA over normal Wi-Fi, 5 successive V9→V10→V9→V10 transitions.
- Hard power cut midway through download, flash write, and first boot; recover current or prior valid image.
- Deliberately bad signed/invalid binary to confirm rejection; failing app health check to confirm rollback.
- Test while microSD missing, Wi-Fi absent, bad time/certificate, and no user data.
- Verify alarm/Todo/D-day/romantic private message survive firmware upgrade (and can be erased on demand).
- Confirm 800×480 LVGL input, pet animations and Focus timing after reboot.

## Official references

- Espressif OTA: https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/system/ota.html
- ESP HTTPS OTA: https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/system/esp_https_ota.html
- Waveshare board family: https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3C

## Scope limit

This is a build-ready architecture contract, not deployed OTA functionality. Build the actual ESP-IDF project first, then integrate HTTPS OTA and health-gated rollback and prove it with flash fault injection.
