# 05. 펌웨어 m7-0.6.0-gift와 설치·복원 (실기 미검증)

## 1. 무엇이 바뀌었나

- 바탕은 **m6-0.4.0-gift**(PR #23)입니다. 그 위에 뚜껑 센서(0.5), 밤 테마(0.5.1), **소리 모듈(0.6)**이 더해졌습니다.
  - 버전 문자열: `m7-0.6.0-gift`
  - 빌드 파일 이름과 프로젝트 이름은 그대로입니다(`pokedock_m6_gift*.bin`, `pokedock_m6`). 플래시 도구와 검사기가 그대로 동작합니다.
- **화면 방향**: 보드는 M6 일반형과 같은 방향입니다(USB-C가 화면의 "아래"). 일반형 이미지를 씁니다(`-Rotate180` 쓰지 않음). 180° 이미지도 함께 빌드합니다.

### 1-1. 소리 (DFRobot DFR0534, v0.6)

| 항목 | 내용 |
|---|---|
| 구조 | `core/audio_director.hpp`(호스트 시험 36/36)가 바이트 프레임과 재생 순서를 정합니다.<br>`firmware/main/board_audio.c`가 UART1(GPIO44, 9600 8N1)로 보내기만 합니다. 모듈의 응답은 받지 않습니다. |
| 프레임 | `AA cmd len data… sum`(DFRobot 공식 Reference). 재생 `07`, 정지 `04`, 볼륨 `13`. 공식 예제 바이트와 같은지 시험합니다. |
| 소리 | 켜짐, 뚜껑 열림(0.7초 뒤 파트너 울음소리), 뚜껑 닫힘(끌 수 있음), 탭, 확인, 페어링, 집중 완료, **알람(끌 때까지 반복)**, 파트너 바꿀 때 울음소리, 5번 탭 메시지 때 울음소리 |
| 우선순위 | 알람 > 집중 완료 > 울음소리·페어링·닫힘 > 켜짐·열림·확인 > 탭. 알람이 울리는 동안 탭 소리는 무시됩니다. |
| 길이 | 소리마다 최대 길이(펌웨어 표)에서 정지 명령을 보냅니다. 모듈의 반복 모드 설정과 관계없이 소리가 끝납니다. 알람은 재생 명령을 다시 보내 반복합니다. |
| 볼륨 | 0–30. 기본 20, 펌웨어 상한 **24**(Kconfig `PD_AUDIO_MAX_VOLUME`, 3V3 측정 전까지).<br>화면에서 **밝기 버튼을 길게** 누르면 끔 → 작게(10) → 보통(18) → 크게(24) 순서로 바뀝니다.<br>BLE `audio {"vol":0..30}`, `audio {"close":false}`(닫힘 소리 끄기), `audio_test {"cue":0..8}`.<br>음소거는 BLE `sound {"on":false}`(전체) 또는 볼륨 0입니다. |
| 저장 | NVS `vol`, `cls` (업데이트 InstallGift에서 유지) |
| 모듈이 없을 때 | 송신 전용이라 아무것도 기다리지 않습니다. 화면, 타이머, RTC, BLE는 그대로 동작하고 소리만 나지 않습니다.<br>UART 설정이 실패해도 로그만 남기고 나머지는 계속 돕니다. |
| 부팅 | 모듈이 켜지는 시간(0.8초)을 기다린 뒤 볼륨과 정지를 보내고, 1.2초에 시작음을 냅니다. |
| 배선 시험 | 전원을 넣고 **10초 안에 화면을 길게** 누르면 60초 동안 J10-1(GPIO44)을 0 V로 잡습니다. 그동안 화면에 뚜껑 센서 상태가 나옵니다(`docs/07` S3a). |
| M6 하드웨어 | Kconfig `PD_AUDIO_BUZZER`를 고르면 예전 부저 4가지 곡으로 빌드됩니다(빌드 확인). 소리 개정은 M6 동작을 바꾸지 않습니다. |

### 1-2. 뚜껑 센서 (v0.5, 그대로)

- `core/lid_sensor.hpp`: 120 ms 디바운스.
- 닫으면 화면만 꺼지고 시계, 알람, 집중 타이머는 계속 돕니다. 닫힘 소리는 끌 수 있습니다.
- 열면 화면이 켜지고 파트너가 등장합니다(애니메이션 + 열림 소리 + 울음소리).
- 센서가 "닫힘"인데 화면이 터치되면 센서가 틀린 것으로 보고 60초 동안 화면을 켭니다. 그런 터치가 3번이면 다음 진짜 열림까지 센서를 무시합니다.
- 선이 끊기거나 센서가 없으면 "열림"으로 읽혀 M6처럼 동작합니다.
- BLE `lid_sensor {"on":false}`로 끌 수 있습니다(NVS `lid`).

### 1-3. 시험 (호스트)

| 시험 | 결과 |
|---|---|
| 소리 | `tests/audio_director_test.cpp` 36/36 |
| 프로토콜 | 41/41 (상태 JSON 144바이트, MTU 185 안) |
| 뚜껑 | 14/14 |
| BLE 다리 | 16/16 |
| 빌드 | ESP-IDF 5.3.2 일반·180°, M6 부저 옵션 빌드 |
| 실제 보드 | **미확인** |

## 2. 새 보드에 처음 설치 (FirstInstall)

새 Waveshare 보드에는 공장 데모와 공장 파티션 테이블이 들어 있습니다. 앱만 바꾸는 `InstallGift`는 이 보드를 거부합니다(테이블이 다름). 이런 보드에만 **한 번** `FirstInstall`을 씁니다.

```powershell
cd "$env:USERPROFILE\Documents\프로젝트\pokedock-companion-m6"
git switch design/m7-openable-20261101
git pull --ff-only
cd v16\masterball-m6
python -m pip install --user "esptool>=4.7,<5" pillow
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
$PO = "$env:USERPROFILE\Documents\프로젝트\PokeDock_Private_Assets\out"
python tools\make_assets.py "$env:USERPROFILE\Documents\프로젝트\PokeDock_Private_Assets\src" $PO
python tools\make_app_images.py
.\tools\flash_gift_windows.ps1 -Port COM5 -Action Check
.\tools\flash_gift_windows.ps1 -Port COM5 -Action FirstInstall -PrivateOut $PO
```

- 이때 보드는 **USB-C를 직접 PC에 연결**합니다(조립 전, 책상 위). 조립 뒤에는 뒤 패널 포트로 연결합니다(4218).
- 소리 팩은 보드가 아니라 **DFR0534 자체**에 넣습니다(`audio/README_KO.md`).
- 순서:
  1. 칩과 16 MB 확인
  2. **공장 펌웨어 전체 16 MiB 백업**
  3. 테이블이 이미 PokéDock이면 거부
  4. 병합 이미지를 0x0에 쓰고, 팩을 0x610000, 메시지를 0xFFF000에 씀
  5. 검증
  6. 테이블 재확인
- 공장 상태로 되돌리기: `-Action RestoreFull -From "<백업 폴더>\pokedock_full_<시각>.bin"`.

## 3. 이후 업데이트와 복원

| 원하는 것 | 명령 |
|---|---|
| 상태 확인(읽기만) | `.\tools\flash_gift_windows.ps1 -Port COM5 -Action Check` |
| 펌웨어 업데이트(설정 유지) | `... -Action InstallGift -PrivateOut $PO` |
| 그림·메시지만 교체 | `... -Action UpdateAssets -PrivateOut $PO` |
| 그림·메시지 지우기 | `... -Action RemoveAssets` |
| 설정만 되돌리기 | `... -Action RestoreNvs -From <pokedock_nvs_시각.bin>` |
| 전부 되돌리기 | `... -Action RestoreFull -From <pokedock_full_시각.bin>` |

- 중간에 실패하면 도구가 출력하는 `RestoreFull` 명령을 그대로 실행합니다. 백업은 비공개 폴더에 두고 공유하지 않습니다.
- **정전 뒤 시간 설정**: RTC 백업 셀이 없습니다(설계상 제외). 전원이 다시 들어오면 화면 메뉴의 시계 설정으로 시간을 직접 맞춥니다(M6 기능 그대로).
