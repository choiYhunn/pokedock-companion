# Build Day — 실제 하루

## 09:00–09:45 HMI factory check
- display
- touch
- Wi-Fi
- RTC
- SD
- speaker
모두 공장 firmware에서 확인.

## 09:45–10:30 Dock Node bench
1. C3 flash test
2. BH1750
3. VL53L0X
4. PN532
5. LEDs
개별 확인 후 모두 연결.

## 10:30–11:15 ESP-NOW
- HMI MAC / Dock MAC 기록
- heartbeat 확인
- phone_docked boolean
- lux
- nfc pokemon id
3개 값이 HMI serial에 찍히면 다음.

## 11:15–13:00 HMI app
- official Waveshare LVGL example/BSP 기반
- custom home screen
- app_state resolver
- local SD artwork
- touch nav
- NTP → RTC
- audio cues

## 13:00–14:00 lunch + Qi thermal test
대상 폰을 45분 이상 충전.
- 비정상 발열
- 충전 끊김
- 폰 위치 민감도
확인.
문제 있으면 cradle을 닫지 말고 open-pad 방식 유지.

## 14:00–15:30 mechanics
- HMI stand/mount
- Qi pad
- NFC zone
- ToF angle
- C3/perfboard
- cable channel
- LED diffuser

3D printed base is optional. If using a commercial stand, spend this block on cable hiding and sensor placement instead.

## 15:30–17:30 behavior integration
다음 순서로:
1. phone placed → Pachirisu
2. dark → Gengar
3. focus → Lucario
4. NFC → selected Pokémon
5. birthday override → Jirachi
6. random encounter
7. Dex count

## 17:30–18:30 fail test
- Wi-Fi off
- SD remove
- Dock C3 power off
- repeated reboot
- low light
- NFC repeated scan
- phone case attached
- charging while NFC scanning

## 18:30–19:00 finish
- volume cap
- night brightness cap
- remove serial debug visual artifacts
- cable sleeve
- fingerprints clean
- firmware binary/source backup