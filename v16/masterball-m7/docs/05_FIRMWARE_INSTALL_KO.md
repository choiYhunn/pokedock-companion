# 05. 펌웨어 m7-0.5.0-gift와 설치·복원 (실기 미검증)

## 1. 무엇이 바뀌었나

- 바탕은 **m6-0.4.0-gift**(PR #23)이고, 그 위에 뚜껑 센서만 더했습니다.
  - 버전 문자열: `m7-0.5.0-gift`
  - 빌드 파일 이름과 프로젝트 이름은 그대로(`pokedock_m6_gift*.bin`, `pokedock_m6`)라 플래시 도구와 검사기가 그대로 동작합니다.
- **화면 방향**:
  - 보드는 M6 일반형과 같은 방향입니다(USB-C가 화면의 "아래"). 화면 면만 50° 뒤로 눕습니다.
  - 그래서 렌더링과 터치 좌표 회전이 필요 없습니다. 일반형 이미지를 씁니다(`-Rotate180` 쓰지 않음).
- **뚜껑 센서**:
  - `core/lid_sensor.hpp`: 120 ms 디바운스.
  - 닫으면 디스플레이만 꺼지고 시계, 알람, 집중 타이머는 계속 돕니다.
  - 열면 화면이 켜지고 파트너 등장 애니메이션(`PDK_GREET`)이 나옵니다.
  - 알람이 닫힌 상태에서 울리면 부저가 울리고, 열면 알람 화면이 바로 보입니다.
- **오류 대비**:
  - 센서가 "닫힘"인데 화면이 터치되면 센서가 틀린 것입니다. 60초 동안 화면을 켭니다.
  - 그런 터치가 3번이면 다음 진짜 열림까지 센서를 무시합니다.
  - 선이 끊기거나 센서가 없으면 "열림"으로 읽혀 M6처럼 동작합니다.
  - BLE 명령 `lid_sensor {"on":false}`로 끌 수 있습니다(NVS `lid`에 저장).
- **보존**: 기존 NVS 설정(알람, 밝기, 파트너, BLE 메시지)은 업데이트(InstallGift)에서 유지됩니다.
- **시험**:
  - `tests/lid_sensor_test.cpp` 14/14
  - 프로토콜 33/33
  - ESP-IDF 타깃 빌드
  - 실제 보드에서는 미확인입니다.

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

- 이때 보드는 **USB-C를 직접 PC에 연결**합니다(조립 전, 책상 위). 조립 뒤에는 후면 패널 포트로 연결합니다(4218이 데이터를 통과하는지 확인한 경우).
- 순서:
  1. 칩과 16 MB 확인
  2. **공장 펌웨어 전체 16 MiB 백업**
  3. 테이블이 PokéDock이면 거부
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
