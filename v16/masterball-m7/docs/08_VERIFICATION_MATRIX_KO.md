# 08. 검증표 (v0.6) — HOST PASS / FAIL / HARDWARE UNVERIFIED

- **HOST PASS**: 컴퓨터 안의 결과입니다(CAD, 공식 회로도 텍스트 대조, 계산, 호스트 시험, ESP-IDF 빌드, 가짜 플래시).
- **HARDWARE UNVERIFIED**: 실제 부품을 연결하거나 출력해야 확인됩니다. 실물 전에는 PASS로 표시하지 않습니다.
- 다시 돌리기:
  - `PY=<python> bash tests/run_m7.sh` (결과 `logs/RUN_MANIFEST.json`)
  - 펌웨어 회귀: `../masterball-m6/tests/run_all.sh --strict` (결과 `../masterball-m6/tests/logs/RUN_MANIFEST.json`)

## 외관

| 항목 | 결과 | 근거 |
|---|---|---|
| 사진 비율 지표 19개 | HOST PASS | `appearance/APPEARANCE_GATE.json` |
| 의뢰인 외관 승인 (2026-11-02 귀 A + 밤 테마, 2026-11-04 그릴·베젤 J10 구멍) | APPROVED. 부품별 출력 파일 해시 13개로 관리 | `appearance/APPROVAL.json` |
| 본 출력 9판이 승인 해시와 같음 (승인 대기 판 0) | HOST PASS | `print/print_manifest.json` (`appearance`, `APPEARANCE_PENDING_PLATES` = {}) |

## 기구

| 항목 | 결과 | 근거 (`logs/verify_report.json`) |
|---|---|---|
| STEP·STL 유효 (14 부품 + 시험편 17) | HOST PASS | 1 |
| 닫힘 전체 간섭 (공식 보드 STEP 부품 + 소리 유닛 + J10 플러그 + J1 소켓 양쪽) | HOST PASS: 설계 접촉 외 0 | 2 |
| 뚜껑 0–110° 연속 스윕 (1° 간격) | HOST PASS: 충돌 0 | 3 |
| 스토퍼 110° | HOST PASS | 4 |
| 무게중심·전도: 110°에서 13.2 mm (최악 10.3), 손가락 2.67 N (최악 1.96, 목표 1.5), 총 약 663 g | HOST PASS (계산) | 5 |
| 화면 시야: 앉은 눈 27곳 100 %, 닫힘 간극 | HOST PASS | 6, 6b |
| 소리 유닛: 그릴이 앉은 눈 0/27에서 보임, 스피커 자리 간섭 0, J10 플러그와 베젤·크래들 간섭 0, 내부 커버 바닥까지 3.9 mm | HOST PASS | 9 |
| 출력 체적 180 mm 이하, 열었을 때 보이는 서포트 0 mm² | HOST PASS | 7 |
| 실제 부품 외형과 CAD | DFR0534(공식 치수도), PUI 스피커(데이터시트), 59155/57155(데이터시트), Waveshare(공식 STEP)는 HOST PASS. 실물 끼움은 **HARDWARE UNVERIFIED** (FK1–FK6) | `fitkit/FIT_MEASUREMENT_FORM.csv` |
| 조립·분해 경로 | HOST PASS (문서 + CAD 순서) / **HARDWARE UNVERIFIED** | `docs/07` |
| 힌지 반복 개폐, 실물 전도 | **HARDWARE UNVERIFIED** | FK2, S18 |

## 전자·전원

| 항목 | 결과 | 근거 |
|---|---|---|
| 새 핀맵과 공식 회로도 일치 (J10-1 GPIO44, J10-3 3V3, J10-4 GND, J1-10 IO17, J1-6 GND, USB-C 경로) | HOST PASS 32/32 | `logs/electrical.txt` |
| GPIO 충돌 없음 (44·17 vs 디스플레이·I2C·SD·USB·스트래핑), GPIO43 미사용 | HOST PASS | 같은 파일 |
| SPI flash·USB 다운로드 간섭 없음 (콘솔 USB-Serial-JTAG, 다운로드는 보드 USB, J10과 무관) | HOST PASS (설정 + 회로도) | `docs/04` §3 |
| 전원 예산: 3V3 최대 0.74 A ≤ MP1605 2 A의 80 %, USB 입력 약 0.63 A | HOST PASS (계산) | `logs/electrical.txt` |
| 3.3 V 신호 호환 (모듈 전원 = 같은 3V3, 모듈 출력 미연결), 공통 GND | HOST PASS (회로 논리) | `docs/04` §4 |
| 하네스 규칙 (교차 TX→RX, 5 V 없음, J10-2 비움, H1 무납땜, 납땜 4점) | HOST PASS | `logs/wiring_pinmap.txt` |
| 3V3 실제 흔들림, 리셋 여부, 단락 시 동작 | **HARDWARE UNVERIFIED** (G-A3) | |
| J10 실제 핀 순서, 플러그 끼움 | **HARDWARE UNVERIFIED** (G-A1, `docs/07` S3a) | |
| 센서 실제 동작 (닫힘·열림) | **HARDWARE UNVERIFIED** (FK4, S3d) | |
| 4218 COM 포트 | **HARDWARE UNVERIFIED** (G-P1) | |

## 펌웨어

| 항목 | 결과 | 근거 |
|---|---|---|
| 소리 드라이버: 프레임(공식 예제 바이트), 부팅 대기, 우선순위, 알람 반복, 최대 길이 정지, 지연 울음소리, 닫힘 소리 끄기, 음소거, 볼륨 상한, 버퍼 한계 | HOST PASS 36/36 | `logs/audio_firmware.txt` |
| 트랙 표 = 펌웨어 표 = 파트너 목록 | HOST PASS 15/15 | `logs/sound_manifest.txt` |
| 소리 팩 도구 (TEST 팩, 선물 팩 길이 검사, MP3 길이, PS 5.1 문법, 저장소에 소리 파일 없음) | HOST PASS 10/10 | `logs/sound_pack_tools.txt` |
| BLE `audio` / `audio_test`, 상태 `vol`/`cls` (MTU 안) | HOST PASS (프로토콜 41/41, BLE 다리 16/16) | M6 strict |
| 뚜껑 센서 디바운스·고장 대비 | HOST PASS 14/14 | `logs/lid_sensor_firmware.txt` |
| 일반 / 180° 빌드 m7-0.6.0-gift | HOST PASS (ESP-IDF 5.3.2) | M6 strict `firmware_build`, `idf_build_wsl.sh rotate180` |
| M6 부저 빌드 옵션 (`PD_AUDIO_BUZZER`) | HOST PASS (빌드) | 이 문서 작성 시 별도 빌드 |
| M6 회귀 전체 (타이머, 알람, 팬텀 애니메이션, BLE, UI 시뮬레이터, 플래시 도구) | HOST PASS (M6 strict) | `../masterball-m6/tests/logs/RUN_MANIFEST.json` |
| 모듈이 없을 때 정상 동작 | HOST PASS (송신 전용 설계 + 시험: 응답을 기다리는 코드 없음) / 실보드 **HARDWARE UNVERIFIED** | |
| 실제 재생, 트랙 순서, 소리 크기 | **HARDWARE UNVERIFIED** (G-A2, G-A4) | |

## 구매

| 항목 | 결과 | 근거 |
|---|---|---|
| 단일 목록, 하네스·CAD와 일치, 링크 = 제품 페이지 또는 DigiKey 품번 조회, DigiKey 합계 ₩83,435 (무료 배송), BLOCKED 0 | HOST PASS 49/49 | `logs/purchase_list.txt` |
| 가격·재고 (2026-11-04) | 판매 페이지에서 확인. 결제 직전 다시 확인 | `bom/M7_FINAL_PURCHASE_KO.md` |
| 고정 M6 원본·제조 패키지 | HOST PASS (m6_frozen) | `logs/m6_frozen.txt` |
