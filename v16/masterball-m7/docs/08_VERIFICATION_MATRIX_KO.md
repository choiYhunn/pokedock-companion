# 08. 검증표 — PASS / FAIL / UNVERIFIED

- **PASS(CAD/호스트)** = 컴퓨터 안의 결과입니다. **UNVERIFIED** = 실물이 필요합니다.
- G1 하드웨어, 실제 FDM 맞춤, 장시간 구동은 실물 전에는 PASS로 표시하지 않습니다.
- 다시 돌리기: `PY=<python> bash tests/run_m7.sh` (결과 `logs/RUN_MANIFEST.json`). 펌웨어 회귀는 `../masterball-m6/tests/run_all.sh --strict`입니다.

## 외관 (독립 승인 게이트)

| 항목 | 결과 | 근거 |
|---|---|---|
| 사진 비율 지표 17개 | PASS (CAD, 사진에서 읽은 목표값 기준) | `appearance/APPEARANCE_GATE.json` |
| 의뢰인 외관 승인, 귀 위치 A/B 선택 | **PENDING**: 승인 전 본 출력 잠금 | `appearance/APPROVAL.json`, `APPEARANCE_REVIEW_KO.md` |
| 귀 B안 전체 기구 검증 | PASS (CAD) | `cad/out_variant_B/verify_report.json` |
| 4면 CAD 렌더 (열림, 닫힘, 사용자 눈높이, 측면) + 사진 유사 카메라 | 생성됨 | `img/`, `appearance/review_sheet.png` |

## 기구

| 항목 | 결과 | 근거 |
|---|---|---|
| STEP 형상 유효 (12종 + 시험편 15) | PASS(CAD) | `logs/build_report.json` |
| STL watertight | PASS(CAD) | `verify_report.json` 1, `print/print_manifest.json` |
| 닫힘 전체 간섭 (공식 보드 STEP 295개 부품 포함) | PASS(CAD) 설계 접촉면 외 0 mm³ | 2 |
| 개폐 연속 스윕 0–110°, 1° 간격 | PASS(CAD) 충돌 0 | 3 |
| 스토퍼 110° (111°에서 2.1 mm³) | PASS(CAD) | 4 |
| 열림 유지 (무게중심이 축을 넘는 각 67.1°) | PASS(계산) | 5 |
| 화면과 뚜껑 닫힘 간극 7.6 mm | PASS(CAD) | 6b |
| 앉은 눈 27곳 시야 100 %, 전체가 보이는 최저 눈높이 190 mm | PASS(광선) | 6b |
| 화면 위치 스윕 25 후보 | PASS(CAD) 현 위치 = 가능한 가장 높은 위치 | `logs/pod_sweep.json` |
| 무게중심, 전도 (110° 여유 11.0 / 최악 7.9 mm), 손가락 2.52 / 1.70 N | PASS(계산) | 5 |
| 출력 체적 180 mm 이하, 보이는 서포트 면 0 mm² | PASS(CAD) | 7 |
| 나사, 핀, 인서트 체결 가능성 (구멍 지름, 나사 길이) | PASS(CAD 치수) / **UNVERIFIED(실물)** | `docs/03`, FK2 |
| 공차 누적, FDM 수축 | **UNVERIFIED** → FK1–FK5 측정 | `fitkit/FIT_MEASUREMENT_FORM.csv` |
| 조립·분해 경로 | PASS(문서 + CAD 순서) / **UNVERIFIED** | `docs/07` |
| USB 케이블 삽입 (어댑터 경로, 덱 통과) | PASS(CAD 외형) / **UNVERIFIED(실제 4432/4218)** | 2 |
| 실물 힌지 마찰, 반복 개폐 200회 | **UNVERIFIED** | FK2 |
| 실물 전도 시험 | **UNVERIFIED** | S15 |

## 전기

| 항목 | 결과 | 근거 |
|---|---|---|
| 전원 경로 (J4 VBUS = USB_5V = J1-4, D2 → VCC) | PASS(공식 회로도 텍스트) | `logs/electrical.txt` |
| USB-C CC 5.1 kΩ, D+/D− 경로 | PASS(회로도) | 같은 파일 |
| 부저 구동 전류 131 mA, USB 예산 0.43 A | PASS(계산) | 같은 파일 |
| GPIO 충돌 (IO16 부저, IO17 센서) | PASS(회로도 + 예약 목록) | 같은 파일 |
| 배선 길이, 꺾임 경로 | PASS(문서) / **UNVERIFIED** | `electronics/harness_m7.json` |
| 단락, 발열 | **UNVERIFIED** (S6 멀티미터, S15 온도) | |
| 4218 데이터 통과 | **UNVERIFIED** (판매처 미기재) | B군 |

## 소프트웨어

| 항목 | 결과 | 근거 |
|---|---|---|
| 호스트 단위시험, 시계, 알람, 타이머 회귀 | PASS(호스트) | `../masterball-m6/tests/logs/` |
| 애니메이션 상태 전환, C++–JS 일치 | PASS(호스트) | 같은 곳 |
| 뚜껑 센서 디바운스, 이벤트, 고장 대비 | PASS(호스트) 14/14 | `logs/lid_sensor_firmware.txt` |
| 화면 좌표, 회전 (일반형 그대로) | PASS(설계 논리), **UNVERIFIED(실기 터치)** | `docs/05` |
| ESP-IDF 타깃 빌드 m7-0.5.1-gift | PASS(빌드) | M6 strict `firmware_build` |
| firmware/assets 주소, NVS 보존, 백업·복원, FirstInstall | PASS(가짜 플래시 50/50, 실제 esptool 4.12.0 인자 11/11) | M6 strict `flash_tool`, `flash_cli_compat` |
| 제조용 기존 시험과 호환 | PASS(M6 strict 전체) | `../masterball-m6/tests/logs/RUN_MANIFEST.json` |
| 실제 보드 플래시, 터치 감도, fps | **UNVERIFIED** | |

## 출력·조립

| 항목 | 결과 |
|---|---|
| 프린터 출력 체적 | PASS(CAD): 180 이하 부품, 256 판 |
| 서포트 위치 | PASS(CAD): 숨은 면만 |
| 얇은 벽 (뚜껑 2.0, 하단 2.8, 센서 덮개 0.6) | PASS(설계) / 0.6 덮개는 FK4로 실물 확인 |
| 실제 공차 | **UNVERIFIED** |
| 사용자 조립 공구, 순서 | PASS(문서) |
