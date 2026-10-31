# 선물 콘텐츠: 화면 속 파트너 애니메이션 (펌웨어 m6-0.4.0-gift)

> **상태: 코드·도구·시뮬레이터·가짜 플래시 시험 통과, 실물 기기 미검증.** 제작업체 납품 이후 의뢰인이 USB-C 케이블로만 적용하는 별도 단계입니다.

## 1. 제조와 선물 콘텐츠의 분리

| 단계 | 펌웨어 | 플래시 영역 | 누가 | 고정 값 |
|---|---|---|---|---|
| 제조·검수(G1·G2·FAT) | **m6-0.3.0** | 앱(0x0~), 자산 영역은 비어 있음 → 자리표시 | 제작업체 | `vendor/MFG_PIN.json`: 커밋 `23cfd70`, ZIP SHA-256 `715d6546…`, 이미지 `3957049e…` |
| 선물 콘텐츠 | 앱은 그대로 두거나 **m6-0.4.0-gift**로 교체(선택) | **assets 파티션 0x610000** + 메시지 슬롯 0xFFF000 | 의뢰인(USB-C 케이블) | 비공개 팩·메시지는 저장소에 없음 |

- 이 작업은 **별도 브랜치** `feature/m6-gift-content-20261031`에 있습니다. 외주 패키지 브랜치(PR #21)는 바꾸지 않습니다.
- `tools/make_vendor_package.py`는 핀에 적힌 m6-0.3.0이 아니면 ZIP 생성을 거부합니다.
- 선물용 빌드는 `firmware/out/pokedock_m6_gift*.bin`으로 따로 나옵니다(제조 이미지 `pokedock_m6_merged.bin`을 덮어쓰지 않음).
- CAD·회로·BOM·SOP는 바꾸지 않았습니다.

## 2. 상태별 동작 (팬텀 우선)

공식 픽셀 스프라이트(Gen-V)는 포켓몬마다 **대기 애니메이션 하나**뿐입니다. 그래서 펌웨어가 그 프레임에 **움직임 곡선**과 **직접 그린 표시**(♥ ★ Zzz !)를 더해 모든 상태를 만듭니다. 팩에 상태별 클립(`94_sleep.gif` 등)이 있으면 그 클립을 씁니다.

| 상태 | 언제 | 움직임 (팬텀) | 다른 파트너 | 표시 |
|---|---|---|---|---|
| 대기 | 평소 | 유령처럼 위아래로 둥실(±6 px, 3초) | 땅 파트너는 2 px 숨쉬기, 토게키스·지라치는 둥실 | — |
| 등장 | 부팅, 화면 켜짐, 파트너 변경, 잠에서 깸 | **옆에서 쏙 나타나 살짝 지나쳤다 제자리**(0.7초) + 흔들 | 위에서 떨어지며 통통 | ★ |
| 터치 | 홈에서 탭 | **키득키득 좌우 흔들기** + 작은 점프 | 점프 후 착지 | ♥ 올라가며 사라짐 |
| 기쁨 | 집중 완료, 시계 저장 | 두 번 점프 | 같음 | ★ |
| 잠자기 | 23:00–06:59, 1분 동안 안 만지면 | 내려앉아 천천히 숨쉬기 | 같음 | Zzz 올라감 |
| 집중 응원 | 집중 타이머 진행 중 | 숫자 아래에서 좌우로 살랑 + 2초마다 작은 통통 | 같음 | — |
| 알람 반응 | 알람이 울리는 동안 | 제목 자리에서 빠르게 통통·흔들 | 같음 | 깜빡이는 ! |
| 숨은 메시지 | 5번 탭 | 춤 | 같음 | ♥ + 메시지 |

- 잠든 파트너를 탭하면 하트 대신 **깨어나는 인사**를 합니다.
- 25분 동안 손대지 않고 집중을 끝내면 예전에는 그 순간 화면이 꺼져 축하를 못 봤는데, 이제 완료 때 화면을 켜고 10분 타이머를 다시 셉니다.
- 모든 움직임은 **정수배 확대**(홈 ×3, 토게키스만 ×2) 그대로입니다. 픽셀이 뭉개지는 소수배 확대는 쓰지 않습니다.
- 로직: `core/anim_director.hpp`(기기와 호스트 테스트가 같은 코드 사용). 시뮬레이터용 사본은 `ui/m6_anim.js`이고, `tests/anim_parity_test.mjs`가 171,840개 표본에서 C++와 JS 결과가 같은지 확인합니다.

## 3. 파트너 현황 (비공개 팩 기준, 2026-10-31 이 PC에서 생성)

| 순위 | 파트너 | 프레임 | 크기 | 홈 표시 | 프레임 간격 | 상태별 전용 클립 |
|---|---|---|---|---|---|---|
| 1 | 팬텀 #94 | 42 | 74×63 | ×3 = 17.5×14.9 mm | 104 ms | 없음(대기 + 움직임) |
| 2 | 팽도리 #393 | 112 | 30×41 | ×3 = 7.1×9.7 mm | 61 ms | 없음 |
| 2 | 토게키스 #468 | 73 | 86×52 | ×2 = 13.6×8.2 mm | 60 ms | 없음 |
| 2 | 루카리오 #448 | 108 | 47×63 | ×3 = 11.1×14.9 mm | 60 ms | 없음 |
| 2 | 누오 #195 | 41 | 67×58 | ×3 = 15.9×13.7 mm | 104 ms | 없음 |
| 3 | 토게피 #175 · 파치리스 #417 · 지라치 #385 | 54 · 88 · 111 | 40×38 · 53×55 · 55×47 | ×3 | 61–101 ms | 없음 |

팩 크기는 694 KB로 assets 파티션의 6.7 %입니다.

**확보하지 못한 자산(가짜 완료 아님)**
- 상태별 **전용 그림**: 잠든 눈, 놀란 얼굴, 기뻐하는 포즈 등. 공식 스프라이트에는 없습니다. 지금은 대기 프레임에 움직임과 표시를 더해 대신합니다.
- 소리: 포켓몬 울음소리는 쓰지 않습니다. 부저는 자체 제작 멜로디만 냅니다.

## 4. 이용 권한 검토

- 포켓몬 이름·그림·소리의 권리는 Nintendo·Creatures·GAME FREAK에 있습니다. PokeAPI가 스프라이트를 공개 저장소에 올려 둔 것은 **재배포 허락이 아닙니다.**
- 그래서 다음은 **하지 않습니다**:
  - 공개 GitHub에 그림·팩·소리를 커밋하는 것
  - 제작업체 ZIP에 포함하는 것(업체는 자리표시 상태로 검수합니다)
  - 울음소리를 기기에 넣는 것
- 남은 선택지:

| 방법 | 권리 상태 | 이 프로젝트의 지원 |
|---|---|---|
| A. 의뢰인 PC에서 공식 스프라이트를 받아 **개인 선물 1대에만** 비공개로 넣기 | 권리자의 허락은 없음. 공개·판매·재배포하지 않는 개인 용도라는 점만 의뢰인이 판단 | `tools/fetch_private_sprites.py --personal-use`. 이 저장소 안이나 원격이 있는 git 저장소 안에는 쓰지 않음 |
| B. **직접 그리거나 의뢰해 받은 독자 캐릭터 그림**(Gen-V처럼 128 px 이하 GIF) | 그린 사람에게 받은 권리 범위 안에서 깨끗함 | 같은 `make_assets.py` 그대로 사용 |
| C. 그림 없이 자리표시 | 문제 없음 | 기본값 |

이 저장소는 A를 권장하지 않고, **도구와 형식만** 제공합니다. 어떤 방법이든 결과 파일은 비공개 폴더에만 둡니다.
- `tests/private_asset_guard.py`는 git에 추적되거나 추가 예정인 파일 중 PDK1·PDM1·GIF·Ogg 등 시그니처나 `message.txt`가 있으면 실패합니다.
- 외주 ZIP 생성기는 파일 시그니처까지 검사해서 이런 파일이 섞이면 ZIP을 만들지 않습니다.

## 5. 개인 메시지 (공개 소스에 없음)

1. 비공개 폴더(예: `Documents/프로젝트/PokeDock_Private_Assets/src/`)에 `message.txt`를 만듭니다. UTF-8, 90바이트 이하(한글 약 30자).
2. `python tools/make_assets.py <src> <out>` → `message_slot.bin`(4 KiB, `PDM1` 형식)이 만들어집니다.
3. 아래 플래시 절차에서 0xFFF000(assets 파티션의 마지막 4 KiB)에 함께 기록합니다.
4. 우선순위:
   - BLE로 따로 보낸 메시지(NVS에 저장되고 기본 문구와 다름)가 이깁니다.
   - 그다음이 비공개 슬롯입니다.
   - 둘 다 없으면 공개 기본 문구 "오늘도 함께하자"입니다.
   - 슬롯은 **m6-0.4.0-gift 펌웨어부터** 읽습니다.
5. 홈에서 5번 탭하면 춤과 함께 메시지가 4.5초 동안 보입니다.

## 6. 기기에 넣기 (USB-C 케이블만, 납땜 없음)

> **실기기 미검증.** 아래 도구는 Windows PowerShell 5.1에서 가짜 esptool(16 MiB 가상 플래시)로 38개 항목, 실제 esptool 4.12.0 명령 해석으로 9개 명령을 시험했습니다. 실제 볼에서는 아직 한 번도 실행하지 않았습니다. G5에서 처음 실행할 때 `-Action Check`부터 합니다.

### 6.1 무엇을 어디에 쓰는가

| 영역 | 주소 | 이 도구가 쓰는가 |
|---|---|---|
| 부트로더 | 0x0 | **아니오**(`RestoreFull` 제외). 실행 후 다시 읽어 바뀌지 않았는지 비교 |
| 파티션 테이블 | 0x8000 | **아니오**(`RestoreFull` 제외). 쓰기 전에 `firmware/partitions.csv`와 일치해야 진행 |
| 설정 NVS(알람·밝기·파트너·BLE 메시지) | 0x9000–0xEFFF | **아니오**(`RestoreNvs`·`RestoreFull` 제외). 쓰기 전 백업, 쓴 뒤 다시 읽어 백업과 비교 |
| 앱 | 0x10000 | `InstallGift`(선물 앱), `RestoreMfgApp`(제조 앱). **병합 이미지는 거부** |
| 그림 팩 | 0x610000 | `InstallGift`, `UpdateAssets` |
| 메시지 슬롯 | 0xFFF000 | `InstallGift`, `UpdateAssets`(`message_slot.bin`이 있을 때) |

- 예전 방식(병합 RAW BIN을 0x0부터 기록)은 사이 공간 0xFF로 NVS 0x9000–0xEFFF를 지울 수 있어 **없앴습니다.**
- 앱 전용 이미지는 병합 이미지의 0x10000 이후 부분과 바이트 단위로 같습니다(`tests/gift_image_check_test.py`).
- 제조 m6-0.3.0과 선물 m6-0.4.0-gift는 다음이 모두 같습니다. 그래서 볼에 있는 부트로더와 테이블을 그대로 둔 채 앱만 바꿀 수 있습니다.
  - 파티션 테이블(바이트 동일)
  - 앱 헤더의 플래시 모드·속도·크기 바이트(`02 4f`)
  - ESP-IDF v5.3.2

### 6.2 모든 동작이 먼저 하는 일

1. **로컬 파일 검사**:
   - 앱 이미지는 ESP32-S3·16 MB·IDF v5.3.2인지, 세그먼트·체크섬·SHA가 맞는지, `firmware/out/SHA256SUMS.txt`에 있는지 봅니다.
   - 팩은 PDK 형식이고 0x9EF000 이하여야 합니다.
   - 슬롯은 4096 B, `PDM1` 형식, 1–90 B UTF-8이어야 합니다.
   - 틀린 경로·파일은 볼에 접속하기 전에 거부합니다.
2. `flash_id`: ESP32-S3이고 16MB가 아니면 중단합니다(잘못된 COM 포트 방지).
3. **전체 16 MiB 백업**을 받습니다(`pokedock_full_<시각>.bin`). 그리고 NVS·부트로더·테이블·앱 머리를 따로 잘라 `pokedock_backup_<시각>.json`(SHA-256)에 기록합니다.
   - 기본 위치: `-PrivateOut`의 상위 폴더 아래 `backups\`, 없으면 `문서\PokeDock_Backups`.
   - **백업에는 메시지와 그림이 들어 있으니 공유하지 않습니다.**
4. 볼의 파티션 테이블을 검사하고, 볼에 있는 앱이 무엇인지 확인합니다(제조/선물, 일반/180°).
   - 앱을 바꾸는 동작에서는 `-Rotate180`이 볼과 다르면 중단합니다.
   - 목록에 없는 앱이나 깨진 앱이면 중단합니다.
5. 계획을 출력하고 `YES` 입력을 받은 뒤에만 기록합니다. 기록 후 `verify_flash`로 검증합니다.

### 6.3 준비 (한 번)

- Windows PC에 Python 3를 설치합니다.
- `python -m pip install --user "esptool>=4.7,<5" pillow`를 실행합니다.
- 볼 **뒤쪽 외부 USB-C**를 **데이터 케이블**로 PC에 연결하고, 장치 관리자에서 COM 번호를 확인합니다. 볼을 열거나 보드 자체 포트를 쓰지 않습니다.
- 다음 파일이 필요합니다.
  - `firmware/out/`의 제조 병합 이미지 2개: 외주 ZIP의 `firmware/` 폴더와 같은 파일이며 SHA-256은 `vendor/MFG_PIN.json`.
  - 선물 병합 이미지 2개: `tools/idf_build_wsl.sh`, `tools/idf_build_wsl.sh rotate180`으로 만듭니다.
- 이 파일들로 `python tools/make_app_images.py --mfg-zip <외주 ZIP>`를 실행해 앱 전용 이미지 4개와 `SHA256SUMS.txt`를 만듭니다.
  - 핀 해시가 다르면 거부합니다.
  - 제조 이미지와 ZIP은 읽기만 합니다.

### 6.4 실행

PowerShell 창에서(경로는 이 PC 기준):

```powershell
cd "$env:USERPROFILE\Documents\프로젝트\pokedock-companion-m6\v16\masterball-m6"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
$PO = "$env:USERPROFILE\Documents\프로젝트\PokeDock_Private_Assets\out"
python tools\make_assets.py "$env:USERPROFILE\Documents\프로젝트\PokeDock_Private_Assets\src" $PO
.\tools\flash_gift_windows.ps1 -Port COM5 -Action Check
```

`Check`가 출력하는 `app on the ball:` 줄로 방향을 정합니다.

| `Check` 출력 | 볼 | 선물 설치 명령 |
|---|---|---|
| `pokedock_m6_mfg_app.bin` | 일반 방향 | `.\tools\flash_gift_windows.ps1 -Port COM5 -Action InstallGift -PrivateOut $PO` |
| `pokedock_m6_mfg_app_rotate180.bin` | 180° 회전 | `.\tools\flash_gift_windows.ps1 -Port COM5 -Action InstallGift -PrivateOut $PO -Rotate180` |

- `UpdateAssets`(앱은 그대로, 팩·메시지만)도 같은 `-PrivateOut`을 씁니다. 그림·메시지를 바꿀 때 사용합니다.
- 제조 앱 m6-0.3.0에 팩만 넣으면 그림은 보이지만 ×3 고정 크기의 짧은 반응만 나옵니다. 잠자기·응원·알람 반응·비공개 메시지는 동작하지 않습니다.

## 7. 되돌리기와 실패했을 때

| 원하는 것 | 명령 (180° 볼은 앱 관련 명령에 `-Rotate180` 추가) | 쓰는 곳 |
|---|---|---|
| 그림·메시지 지우고 자리표시로 | `.\tools\flash_gift_windows.ps1 -Port COM5 -Action RemoveAssets` | 0x610000–0xFFFFFF 지움 |
| 제조 앱 m6-0.3.0으로(설정 유지) | `.\tools\flash_gift_windows.ps1 -Port COM5 -Action RestoreMfgApp` | 0x10000만 |
| 설정만 백업 시점으로 | `.\tools\flash_gift_windows.ps1 -Port COM5 -Action RestoreNvs -From <backups\pokedock_nvs_<시각>.bin>` | 0x9000–0xEFFF만(정확히 0x6000 B만 받음) |
| 모든 것을 백업 시점으로 | `.\tools\flash_gift_windows.ps1 -Port COM5 -Action RestoreFull -From <backups\pokedock_full_<시각>.bin>` | 0x0–0xFFFFFF 전체 |
| 백업만 | `.\tools\flash_gift_windows.ps1 -Port COM5 -Action Backup` | 쓰지 않음 |

**중간에 케이블이 빠지거나 전원이 끊기면**
- ESP32-S3의 다운로드 모드는 칩 ROM에 있습니다. 앱이 반쯤 써져도 같은 USB-C로 다시 접속할 수 있습니다(후면 포트가 칩의 USB-Serial-JTAG D+/D−에 연결된 설계 기준. G1-E7에서 확인하며 실기 미검증).
- 도구가 출력한 `RestoreFull -From "<쓰기 직전 전체 백업>"` 명령을 그대로 실행합니다.
- 앱을 쓰던 중이었다면 볼의 앱이 깨진 것으로 판정되어 `InstallGift`/`RestoreMfgApp`는 거부됩니다. 의도된 동작입니다.
  - `RestoreFull`로 원래대로 돌린 뒤 다시 설치합니다.
  - `-AllowUnknownApp`은 방향(`-Rotate180`)을 확실히 알 때만 씁니다.
- `RestoreFull` 자체가 중단되면 **같은 `-From` 파일로** 다시 실행합니다(그 직전에 새로 받은 백업이 아님).
- 설정 NVS는 앱·팩 쓰기 중에 건드리지 않습니다. 가짜 플래시 시험에서는 중단 후에도 NVS가 그대로였습니다.

## 8. 성능·메모리 (계산과 브라우저 측정 / 기기 미측정)

| 항목 | 값 | 근거 |
|---|---|---|
| 프레임 디코드 버퍼 | 128×128×3 B × 2 = 96 KiB(PSRAM) + 인덱스 16 KiB | `assets.c` |
| 디코드 | 프레임이 바뀔 때만(대략 10–16 Hz). 위치 갱신은 30 Hz 타이머 | `ui.cpp` |
| 그리기 영역 | 팬텀 홈 222×189 px(×3, 최근접 확대) | `place()` |
| 브라우저 시뮬레이터 | 약 60 fps, 디코드 평균 0.05–0.1 ms | `tests/gift_sim_probe.py`(데스크톱 Edge, **기기 값 아님**) |
| 기기 측정 방법 | 30초마다 시리얼 로그 `pd_anim: N ticks/30s (Hz), decodes, avg/max us, frame WxH zoom` | 실기 G5에서 기록 |

## 9. 검증 현황

| 검사 | 결과 |
|---|---|
| `tests/anim_director_test.cpp`(상태 전환·팬텀 동작·353,600개 배치: 원 안, 시계·집중 라벨·링·알람 시각 침범 없음, 정수배) | 통과 |
| `tests/anim_parity_test.mjs`(C++ ↔ 시뮬레이터 JS 171,840개 표본) | 일치 |
| `tests/gift_sim_probe.py` 공개 시험 팩(기하 도형): 자리표시 → 캐릭터, 8종, 터치·5탭·집중·완료·알람·잠·깨움·메시지 슬롯, 겹침·잘림, 브라우저 fps | 통과 |
| 같은 검사를 비공개 실제 스프라이트 팩으로(결과 캡처는 비공개 폴더에만) | 통과 |
| `tests/pdk_roundtrip_test.py`, 기존 core 회귀·clock_set·protocol·BLE E2E | 통과 |
| ESP-IDF v5.3.2 타깃 빌드(m6-0.4.0-gift) | 통과 |
| `tests/gift_image_check_test.py`: 제조 이미지 SHA-256 = 핀(변경 없음), 앱 전용 이미지 = 병합[0x10000:], 테이블·헤더·IDF 동일, 병합 이미지 거부 | 통과 |
| `tests/flash_gift_test.ps1`(Windows PowerShell 5.1 + 가짜 esptool 16 MiB): 정확한 인자, 백업 선행, 0x10000 미만 무기록, NVS·부트로더·테이블·phy 불변, 방향·칩·테이블·미확인 앱·잘못된 파일 거부, 중단 후 RestoreFull로 16 MiB 동일 복원, RemoveAssets·RestoreMfgApp·RestoreNvs·UpdateAssets | 통과(38) |
| `tests/flash_cli_compat_test.py`: 위 시험이 기록한 esptool 명령을 실제 esptool 4.12.0이 해석(없는 포트에서 연결 단계까지) | 통과 |
| **플래시 도구 실기**: 실제 볼에서 백업 속도, 앱 교체 후 설정 유지, 중단 후 복구 | **미검증**: G5에서 `Check` → `Backup` → `InstallGift` 순으로 |
| **기기 실측**: 실제 fps·디코드 시간, AMOLED 색감, 터치 감도, 0xFFF000 슬롯 읽기, 잠자기 밤 전환 | **미검증**: 제작 완료 후 G5에서 확인 |

G5 실기 확인 순서:
1. 팩만 기록한 m6-0.3.0에서 그림이 보이는지
2. 선물 펌웨어 기록 후 로그의 `gift message loaded`와 `pd_anim` 수치
3. 각 상태 영상 촬영
4. 24시간 연속 동작
