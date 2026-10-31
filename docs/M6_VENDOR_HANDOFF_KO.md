# PokéDock M6 Rev C — 외주 제작업체 전달 안내서

> **상태: 설계/소스 준비 완료, 실물 미검증.** 이 자료는 완제품 제조 승인서가 아닙니다.
> 2026-10-31 점검: Draft PR #21 기준. 저장소 `main`의 이전 V14~V16 설명보다 **이 브랜치의 M6 Rev C**를 우선합니다.
>
> **2026-10-31 턴키 패키지 추가**: 업체에는 **ZIP 하나**만 보내면 됩니다. `v16/masterball-m6/`에서 `python tools/make_vendor_package.py`를 실행하면 `dist/PokeDock_M6_RevC_Vendor_Package_<날짜>.zip`이 생깁니다(문서·BOM·STEP/STL·조립 STEP·배선도·**빌드된 펌웨어 이미지**·검사 양식 포함, 포켓몬 자산·개인정보 자동 차단). 업체용 설명서는 ZIP 안 `00_READ_FIRST_KO.md`와 `vendor/` 폴더입니다. 아래 내용은 그 요약입니다.

## 1. 의뢰 목적과 작업 범위

개인 선물용 Ø138 mm 마스터볼 형태 탁상 장치 **1개**의 시제품 제작입니다. 의뢰인은 전자 납땜과 3D 프린팅을 직접 하지 않습니다.

- **기존 설계 활용**: 신규 제품 기획·기구 재설계·전체 펌웨어 재작성은 기본 견적에서 제외합니다.
- **업체에 요청**: 부품 조달, 실보드 치수·동작검증(G1), 부저 구동기판 제작과 하네스 납땜, 소형 시험 출력·맞춤(G2), 최종 FDM 다색 출력, 체결·배선·조립, 전원·터치·부저·시계 기능 시연 영상.
- 외관: 무광 보라 상단·아이보리 하단·검정 벨트/베젤·분홍 돌기×2·흰색 M, 중앙 원형 AMOLED. **임의 리디자인·도색 금지.**
- 전원: USB-C 5 V 상시 전원. 메인 LiPo/RTC 백업 셀 없음. 보드 USB-C와 후면 연장 포트 동시 연결 금지.

## 2. 제공된 파일 — 실제 GitHub 경로

아래 모든 경로는 저장소 루트 기준으로 `v16/masterball-m6/` 뒤에 이어집니다.

| 분류 | 경로 | 수량/용도 |
|---|---|---|
| 최종 외장 **STEP** | `cad/out/step/*.step` | 8개: `upper_shell_purple`, `lower_shell_ivory`, `belt_black`, `bezel_black`, `display_plate_petg`, `lobe_left_pink`, `lobe_right_pink`, `m_inlay_white` |
| 최종 외장 **STL** | `cad/out/stl/*.stl` | 위 부품 8개의 대응 메쉬 |
| 맞춤 시험편 **STEP/STL** | `cad/out/fitkit/*.{step,stl}` | 5종: `fitkit_belt_segment`, `fitkit_joint_coupon`, `fitkit_opening_coupon`, `fitkit_port_coupon`, `fitkit_upper_segment` |
| 조립 예시·단면 렌더 | `docs/img/m6_*.png` | 조립/분해/단면/배선 참고. **실물 사진 아님** |
| 회로/배선 | `electronics/harness.json`, `electronics/wiring_m6.svg`, `docs/img/m6_wiring.png` | W1~W9 배선, J1/Adafruit 핀, AO3400A/WT-1205 부저 회로 |
| 구매 목록 | `procurement/BOM_M6.csv` | 정확한 품번·수량·Tier. 2026-10-24 가격은 시세 참고치 |
| 출력 조건/견적 의뢰 | `procurement/RFQ_M6_KO.md` | 출력 방향·재료·층고·견적 문의 사항 |
| 실물 검수 | `docs/G1_START_HERE_KO.md`, `docs/G1_G2_INSPECTION_KO.md`, `docs/G1_G2_RECORD_TEMPLATE.csv` | G1 보드·회로, G2 핏 키트 측정·사진/기록 양식 |
| 최신 의사결정 | `docs/REV_C_FINAL_KO.md` | Rev C 변경·안전·미검증 내용 |
| 펌웨어 소스 | `firmware/` 및 `tools/idf_build_wsl.sh`, `tools/flash_windows.ps1` | ESP-IDF 5.3.2/ESP32-S3 컴파일·플래시 절차 |
| 자동 검증 증거 | `tests/logs/RUN_MANIFEST.json`, `cad/out/verify_report.json` | strict 검증 로그, 소스 fingerprint/STL 해시. **실물 검증 아님** |

**주의:** 빌드 완료한 통합 플래시 파일 `firmware/out/pokedock_m6_merged.bin`(및 `_rotate180`)은 Git에 커밋하지 않고 **턴키 ZIP 안에 SHA-256과 함께** 넣습니다. 업체는 빌드할 필요 없이 esptool로 기록합니다. 공식 제조사 참조 STEP 분해본 등 `vendor_cache/`도 저장소에 없고 `tools/fetch_vendor_refs.sh`로 복구합니다. 실제 포켓몬 8종 애니메이션 자산 팩도 미완료입니다.

## 3. 단계별 발주 승인

**1단계 — 설계 검토 및 실물 G1:** 정확히 Waveshare **ESP32-S3-Touch-AMOLED-1.43 일반형, 케이스 없는 SKU 30106**을 사용합니다. -B/1.43C로 임의 대체하지 않습니다. 부품 조달·회로 조립·공식 데모/M6 플래시·화면/터치·외부 J1 USB·부저·전압/전류·실측을 수행하고 기록합니다.

**2단계 — G2 시험 출력:** G1 합격 후, 먼저 `bezel_black`, `display_plate_petg` 및 핏 키트 5종만 출력합니다. 최종 외장에 사용할 **동일 업체·동일 재료·동일 출력 설정**으로 치수와 조립 간극, 나사산, USB 플러그, 버튼 둘레 외관을 확인합니다. `G1_G2_INSPECTION_KO.md`의 **K11 외관 검사도 본 출력 전 필수**로 취급합니다.

**3단계 — 최종 외장:** G1·G2 합격과 의뢰인의 별도 승인 이후 최종 8부품을 출력합니다. 모든 부품을 조립하고 USB·터치·부저·타이머 기능을 확인합니다. 가능하면 24시간 전원 안정성 테스트를 포함해 견적을 분리합니다.

**4단계 — 선물 콘텐츠/휴대폰 연동:** 실제 마스터볼용 포켓몬 애니메이션, iOS 연결·시간 복구는 별도 미완료 과제입니다. 하드웨어 업체가 이를 개발·보증하는지 견적에 명시하지 않는 한 완료라고 주장하지 않습니다. iPhone Safari GitHub Pages 웹앱은 직접 Web Bluetooth 연결을 제공하지 않습니다.

## 4. 업체에 요청할 견적 구분

1. 부품 **실비**(모델·수량·배송비·대체품 승인 필요)
2. G1 실보드 검사·부저 소형 구동기판 납땜·배선/플래시
3. G2 소형 핏 키트 출력·적합성 확인/불합격 재작업 조건
4. 최종 PLA/PETG 8부품 출력·마감·조립
5. 동작 검수 영상·완제품 배송
6. 기존 자료의 오류 수정이 필요할 때 **사전 승인**을 받는 별도 설계/수정 단가

전체 설계를 새로 설계하는 통합 R&D 패키지가 아니라 **기존 설계 기반의 제작·실물 검수 의뢰**로 견적해 주십시오.

## 5. GitHub에서 받는 방법

- 작업 상태: [M6 Draft PR #21](https://github.com/choiYhunn/pokedock-companion/pull/21) — `main` 미병합.
- 전체 파일: PR에서 **head 작업 브랜치** `design/m6-usb-powered-manufacturable-20261024`로 이동해 `v16/masterball-m6/`를 확인합니다.
- STEP/STL만 필요한 3D 업체에는 **시험 출력 파일만 별도 ZIP으로 압축해** 보내십시오. PR의 diff 화면이나 GitHub 링크만으로 출력 발주가 완료되지는 않습니다.
- 업체가 소스까지 필요하면 해당 브랜치의 ZIP/clone을 제공하고, 이 문서와 `REV_C_FINAL_KO.md`를 첫 번째 읽을거리로 지정합니다.
- 저장소는 **public**입니다. 사적인 편지, 연락처, 비공개 콘텐츠 또는 배포 권한 없는 포켓몬 자산을 공개 저장소에 추가하지 마십시오.

## 6. 미완료/주의사항

- 자동 검증은 2026-10-24 기준이고, 실제 Waveshare 보드/구동 회로/3D 출력물/휴대폰 BLE/열·전류 실측은 수행되지 않았습니다.
- 디스플레이의 첫 부팅·터치 컨트롤러 종류와 연결 방향은 G1에서 실측합니다.
- 부저 MOSFET 회로는 데이터시트 계산과 자동 검사만 완료됐으며 실물은 미검증입니다.
- 정전 후에는 시계를 다시 맞춰야 합니다. iPhone PWA는 마스터볼에 직접 BLE 연결하지 못하므로, 펌웨어 m6-0.3.0부터 **기기 터치로 날짜·시간·알람 시각을 설정**합니다(`v16/masterball-m6/docs/CLOCK_WITHOUT_PHONE_KO.md`, 검사 G1-E10).
- 실제 포켓몬 M6 애니메이션 팩과 완제품 장시간 시험은 별도 검증 항목입니다.
