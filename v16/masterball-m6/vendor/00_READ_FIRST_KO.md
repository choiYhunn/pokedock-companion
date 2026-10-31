# PokéDock M6 Rev C — 제작업체 전달 패키지 (먼저 읽어 주세요)

이 ZIP 하나에 **완성품 1대**를 만드는 데 필요한 자료가 모두 들어 있습니다. 부품 구매, 납땜, 펌웨어 기록, 3D 출력, 조립, 검수를 한 업체가 맡는 **턴키 제작**을 요청합니다. 의뢰인은 납땜·배선·출력·조립을 직접 하지 않습니다.

> 상태: **설계·소스·자동 검증 완료, 실물 미검증.** 실물 확인은 이 패키지의 G1·G2 단계에서 업체가 처음 수행합니다. 각 단계 끝에서 의뢰인 승인을 받아 주세요.

## 읽는 순서

| 순서 | 파일 | 내용 |
|---|---|---|
| 1 | `vendor/01_PRODUCT_SPEC_1P_KO.md` | 1페이지 제품 사양·단계·납품물 |
| 2 | `vendor/02_RFQ_TURNKEY_KO.md` | 견적 요청 항목·질문·조건 |
| 3 | `vendor/03_SOP_BUILD_KO.md` | **작업 절차서**: 조달 → G1 → G2 → 출력·조립 → 최종 검수 |
| 4 | `vendor/04_ACCEPTANCE_GATES_KO.md` | 단계별 승인 기준, 최종 합격 기준 F1–F14 |
| 5 | `vendor/BOM_TURNKEY.csv` | 구매 목록: 제조사·품번·수량·대체 가능 여부 |
| 6 | `vendor/05_COST_ITEMS_KO.md` | 비용 항목(확인된 단가와 견적 칸) |
| 7 | `vendor/06_SOLDER_REDUCTION_OPTIONS_KO.md` | 납땜을 줄이는 기성품 대안 비교 |

## 들어 있는 파일

| 폴더 | 내용 |
|---|---|
| `cad/out/step/`, `cad/out/stl/` | 최종 외장 8부품(상단·하단 쉘, 벨트, 베젤, 플레이트, 돌기 2, M) |
| `cad/out/fitkit/` | G2용 소형 맞춤 시험편 5종(STEP·STL) |
| `cad/assembly/m6_printed_parts_assembly.step` | 출력 부품 전체를 조립 위치에 놓은 STEP(확인용) |
| `cad/out/purchased/` | 구매품 자리(부저, 구동기판, 나사, 소켓, USB 보드, 웨이트)의 **외곽 모형**. 제조사 모델 아님 |
| `docs/img/` | 조립 렌더·분해도·단면도·배선도(실물 사진 아님) |
| `electronics/` | 배선표 `harness.json`(W1–W9, 핀 번호), 배선도 `wiring_m6.svg` |
| `firmware/` | **바로 기록할 이미지** `pokedock_m6_merged.bin`(0x0), 화면이 뒤집힌 경우 `pokedock_m6_merged_rotate180.bin`, `SHA256SUMS.txt`, 빌드용 소스 `firmware/source/` |
| `docs/` | G1·G2 검사 절차와 기록 양식, Rev C 결정 사항, 휴대폰 없이 시계 맞추기 |
| `procurement/` | 설계 BOM 원본, 3D 출력 조건(`RFQ_M6_KO.md`) |
| `tests/logs/`, `cad/out/*.json` | 자동 검증 기록(소스 지문, 간섭·공차 보고서, 화면 시뮬레이터 캡처) |
| `MANIFEST.json` | 모든 파일의 SHA-256, Git 커밋, 펌웨어 버전, 내용 점검 결과 |

## 꼭 지켜 주세요

1. 보드는 **Waveshare ESP32-S3-Touch-AMOLED-1.43, 케이스 없음, SKU 30106**만 사용합니다.
2. **보드에 직접 납땜하지 않습니다.** J1에는 소켓을 끼우고, 보드 자체 USB-C와 외부 USB-C를 동시에 연결하지 않습니다.
3. **G1 합격 → 의뢰인 승인 → 핏 키트(G2) → 의뢰인 승인 → 본 출력** 순서입니다. 본 외장을 먼저 출력하지 않습니다.
4. 설계 파일을 수정하지 않습니다. 맞지 않으면 측정값과 사진을 보내 주세요.
5. 포켓몬 그림·소리·로고를 넣지 않습니다. 화면 가운데 "포켓몬 이미지 필요" 자리표시가 정상입니다. 의뢰인의 개인 메시지도 입력하지 않습니다.

## 공식 참고 자료 (패키지에 포함하지 않음)

- Waveshare 보드 위키·회로도·STEP: waveshare.com에서 "ESP32-S3-Touch-AMOLED-1.43" 검색(SKU 30106 페이지)
- Adafruit 4090 회로도: learn.adafruit.com의 "Adafruit USB Type C Breakout" 문서
- 부품 데이터시트: Digi-Key 각 품번 페이지(WT-1205, AO3400A, MF-R075, 1N4148)

문의는 견적서와 함께 의뢰인에게 보내 주세요.
