# 보드 단독 실기 기록 (2026-11-16)

- **범위**: Waveshare ESP32-S3-Touch-AMOLED-1.43(SKU 30106) 보드만 USB-C로 PC에 연결했습니다.
- **연결하지 않은 것**: 스피커, 리드 센서, H1 케이블. DFR0534는 micro-USB로 PC에만 연결했습니다(보드와는 연결하지 않음). 멀티미터·캘리퍼·3D 출력도 없었습니다.
- **비공개로 둔 것**: 백업 파일, 보드 MAC, 스프라이트 팩은 `PokeDock_Private_Assets\backups\`에만 있고 저장소에 넣지 않았습니다.

## 결과

| 항목 | 결과 | 근거 |
|---|---|---|
| 보드 인식 | **PASS** | COM6 "USB 직렬 장치"(VID 303A / PID 1001, USB-Serial/JTAG). ESP32-S3 (QFN56) rev v0.2, PSRAM 8 MB, 플래시 16 MB(제조사 0x20 / 장치 0x4018, quad 3.3 V) |
| 공장 백업 | **PASS** | `read_flash 0x0 0x1000000`을 두 번 따로 읽어 둘 다 16,777,216 B, SHA-256 `6fdbb235…ac8f`로 일치. 공장 앱 `example_qspi_with_ram`(IDF v5.5.4). 0x610000 이후는 모두 0xFF |
| M7 설치 | **PASS (2회차)** | 1회차 FirstInstall m7-0.6.0: 쓰기·검증·테이블 확인은 통과했지만 화면이 까맸습니다. 2회차 InstallGift m7-0.6.1(밝기 명령 수정): 쓰기·검증 통과, 부트로더·테이블·NVS 변경 없음 |
| 화면 및 터치 | **PASS** | 0.6.1에서 의뢰인이 육안으로 확인. 로그: panel RDID=0xff → CO5300, touch FT(chip 0x64), 애니메이션 27 Hz |
| 시계·타이머·알람 | **PASS** | 의뢰인 확인: 기기에서 시계 설정, 2분 뒤 알람(탭 = 5분 뒤, 길게 = 끄기), 집중 타이머 시작·정지, 파트너·밝기 변경 |
| BLE 연동 | **부분** | 광고 PASS: `PokeDock-MB`, 서비스 UUID `edc00001-8148-4b41-9a3e-7bd93d2ab771`, RSSI −38. 페어링(화면 6자리 번호)과 명령은 휴대폰 앱이 필요해 NOT TESTED<br>추가(같은 날): V18 앱 BLE 코드가 화면 버튼까지 연결돼 있음을 확인했고, 실제 M7 0.6.1 엔진과의 브리지 시험 9/9 PASS. APK 1.8.1 빌드. **Android 기기가 PC에 연결되지 않아 무선 실기는 NOT TESTED** (`docs/10_PHONE_BLE_TEST_KO.md`). iPhone 웹앱은 BLE 불가로 평가 |
| MP3 파일 저장 | **PASS** | DFR0534 micro-USB → E:(USB 이름 "JQ8400 uart mp3 player", FAT 8 MB, 이동식). 공장 샘플 16개(01–08.mp3, 09–16.wav, 1,059,712 B)를 비공개 폴더에 백업(해시 일치) → `copy_sounds_windows.ps1 -ClearDrive` → `PASS: 16 tracks copied in order`(338,064 B). 디렉터리 순서 01–16, 16개 내용 해시 일치 → 안전하게 꺼냄. **재생 확인은 아님**(트랙 번호 = 복사 순서는 실제 재생으로 확인해야 함) |
| 실제 소리 출력 | **NOT TESTED** | 안전 조건: 멀티미터 없이 J10과 DFR0534를 연결하지 않음. 로그상 UART1 TX(GPIO44, 9600) 준비 완료 |
| 개폐 센서 | **NOT TESTED** | 리드 센서 미연결(납땜 안 함). 센서가 없으면 "열림"으로 읽혀 화면 유지(설계대로) |

## 발견한 결함과 조치

- **검은 화면 (0.6.0)**
  - 원인: `board_display_brightness()`가 `esp_lcd_panel_io_tx_param(s_io, 0x51, …)`로 명령을 그대로 보냈습니다.
    - QSPI 패널은 `0x02 << 24 | cmd << 8` 형식이어야 합니다. 드라이버의 `tx_param()`도 이 형식을 씁니다.
    - 그래서 명령이 패널에 닿지 않았고, 초기화 표의 `0x51 = 0x00`(밝기 0)이 그대로 남았습니다.
    - 공장 데모는 같은 초기화 표 뒤에 `0x51 = 0xFF`를 따로 보냅니다.
  - 조치: 0.6.1에서 한 줄을 고쳤습니다. 호스트 시험은 protocol 41, core 44, audio 36, lid 14 모두 통과했습니다.
  - 같은 줄이 PR #21(제조 m6-0.3.0)과 PR #23에도 있습니다. 두 PR은 고정 상태라 바꾸지 않았습니다. 실제 보드에 쓰면 같은 증상이 날 것으로 예상합니다.
- **I2C NACK 로그**: 약 15–40초마다 `i2c_master_transmit_receive … unexpected nack`이 찍힙니다.
  - 터치 폴링에서 나는 것으로 보입니다. 터치 반응에는 영향이 없었습니다.
  - 원인 확정과 조치는 남은 일입니다.
- **도구 표시 문구**: `flash_gift_windows.ps1`이 공장 앱을 "BROKEN"으로, 0.6.x 앱을 "m6-0.4.0-gift"로 표시합니다. 동작에는 영향이 없는 표시 문제입니다.

## 백업 위치 (비공개)

| 폴더 (`Documents\프로젝트\PokeDock_Private_Assets\backups\`) | 내용 |
|---|---|
| `factory_20261116\` | 공장 전체 백업 2개(같은 해시) + `README_복원_KO.md`(복원 명령) |
| `firstinstall_20261116\` | FirstInstall 직전 백업(공장과 같은 해시) |
| `install_0.6.1_20261116\` | 0.6.1 설치 직전 백업(0.6.0 상태) |
| `dfr0534_factory_sounds_20261116\` | 모듈에 원래 있던 샘플 소리 16개 |

공장 복원 명령:

```powershell
.\tools\flash_gift_windows.ps1 -Port COM6 -Action RestoreFull -From "<factory_20261116>\waveshare_factory_full_16MiB_read_a.bin"
```
