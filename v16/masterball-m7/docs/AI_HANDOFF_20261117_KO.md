# AI 인수인계 — PokéDock M7 (2026-11-17 새벽, Claude → 다음 작업자)

먼저 읽을 것: 이 문서 → `logs/HW_BRINGUP_20261116_KO.md` → `docs/09_USER_CHECKLIST_KO.md` → `docs/11_WEEKEND_PRINT_PLAN_KO.md`.

## 0. 지켜야 할 것 (의뢰인 지시)

- **PR #21·#23 수정 금지.** PR #24(`design/m7-openable-20261101`)는 **Draft를 유지하고 병합하지 않습니다.**
- 승인된 3D 외관과 `print/02_final` STL은 바꾸지 않습니다. 바뀌면 승인 해시가 깨집니다.
- 비공개 자산(그림, 메시지, 소리, 공장 백업)은 저장소에 올리지 않습니다.
  - 위치: `Documents\프로젝트\PokeDock_Private_Assets\`
- 의뢰인에게 멀티미터·캘리퍼를 요구하지 않습니다. 지금 없습니다.
  - 전기 검수와 납땜은 주말(11/21–22)에 경험자에게 맡깁니다(`electronics/HELPER_WORK_ORDER_KO.md`).
- 4424 케이블을 원래 핀 배열 그대로 J10–DFR0534에 꽂으면 안 됩니다. 3V3와 GND가 뒤바뀝니다.
- 펌웨어는 결함이 재현될 때만 최소로 고치고, 불필요하게 다시 쓰지 않습니다. 쓰기 전에는 의뢰인 승인을 받습니다.
- 자동 재시작(멈춤 감시)이 일어나면 정상으로 보지 않습니다.
- 실물로 시험하지 않은 것을 PASS로 적지 않습니다.

## 1. 현재 상태

| 항목 | 상태 |
|---|---|
| 보드 | Waveshare SKU 30106, COM6 (VID 303A/PID 1001). 펌웨어 **m7-0.6.6-gift** |
| 공장 백업 | `PokeDock_Private_Assets\backups\factory_20261116\` (SHA `6fdbb235…`). 복원 방법은 같은 폴더 README |
| 실기 PASS | 화면, 터치, 시계, 알람, 집중 타이머, 파트너, 밝기, Android 페어링·재연결, DFR0534 파일 저장(16트랙 순서) |
| NOT TESTED | 실제 소리 출력, 뚜껑 센서(납땜 전), Android B4·B5·B8·B9·B11, APK 1.8.2 설치 |
| 고친 결함 | 검은 화면(0.6.1), 폰 연결 시 LVGL 멈춤(0.6.5: SPI ISR 코어 1), 밤 밝기 제한 제거(0.6.6), 앱 재연결 상태 번호(앱 1.8.2) |
| 같은 결함이 남은 곳 | PR #21·#23의 `board_display.c:136` 밝기 명령. 수정 금지라 기록만 함 |

## 2. 저장소·파일

- M7 펌웨어 소스: `v16/masterball-m6/firmware`, `core` (M7도 같은 소스 사용).
  - 빌드: WSL `bash v16/masterball-m6/tools/idf_build_wsl.sh` → `python tools/make_app_images.py`
- 앱(V18): 별도 작업트리 `Documents\프로젝트\PokeDock_모바일앱_기록\pokedock-mobile-ble-20261116`.
  - 브랜치 `feature/mobile-v18-ble-live-20261116`. PR은 만들지 않았습니다.
  - APK: `PokeDock_Mobile_V18_Native_20261025\app_android\PokeDock_V18_1.8.2_debug_20261116.apk`
- 출력 추정: `tools/bambu_slice_estimate.py` (Bambu Studio CLI 실제 슬라이스), 결과 `logs/print_estimate/`
- PC BLE 반복 시험: `tools/ble_soak_pc.py`
  - PC가 볼과 본딩돼 있어야 합니다(2026-11-16 완료).
  - Windows에서는 bleak가 winrt 버전 충돌로 깨질 수 있어, 따로 만든 venv에서 실행합니다.
- 워치형 예비안: `v16/watch-e1/` (예비 CAD. 실물 확인 전이라 제작 가능성 확정 아님)

## 3. 남은 일 (우선순위)

1. **의뢰인**: APK 1.8.2 설치 → B4·B5·B8·B9·B11 시험(`docs/10`)
2. **주말 출력**: FK1–FK7 먼저(약 2시간 48분) → 합격하면 본 출력 9판(약 11시간). `docs/11`
3. **주말 경험자**: H1 재배열 + P1–P3 검사, H2·H3 납땜, 이어서 S-1~S-3(시작음, 알람, 뚜껑 센서) 첫 실물 시험. `electronics/HELPER_WORK_ORDER_KO.md`
4. 선물 자산: 개인 메시지와 선물 소리를 아직 넣지 않았습니다(`docs/12_GIFT_POLISH_REVIEW_KO.md` §3)
5. UI 개선 P1–P3는 의뢰인이 고른 것만 반영합니다(`docs/12` §2)
