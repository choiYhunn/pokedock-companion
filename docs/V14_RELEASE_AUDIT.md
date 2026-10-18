# PokéDock V14 — 제조·구매·포팅 정합성 감사 / Release Gate (2026-10-19)

> **단독 정본**: 이 문서 및 [V14 설계](V14_MAGSAFE_READY_DESIGN.md)가 최신 하드웨어 기준이다. V10 웹 UI와 V11 학습 엔진은 소프트웨어 참조로만 유지한다. **실물 제작 검증 완료 문서가 아니다.**
>
> Audit baseline: `main@edd293f9be1e8c4941ea879a0b4b2f68e6801f31`. 사용자가 확인한 값과 OEM 공시, 아직 없는 실측, 계산 예시를 분리한다.

## 0. 변경 불가능한 요구사항과 결정

| 분류 | 항목 | 상태 |
| --- | --- | --- |
| 사용자 확인 | 상대 휴대폰 iPhone 14 Pro; MagSafe 케이스 | CONFIRMED |
| 제조사 공시 | iPhone 본체 147.5 × 71.5 × 7.85 mm; 206 g | PUBLISHED — 케이스 미포함 |
| 제조사 공시 | Waveshare ESP32-S3-Touch-LCD-4.3C-BOX SKU **33630**, 화면 800 × 480, 외형도 116.3 × 79 × 18 mm | PUBLISHED — 판매 리비전 실측 필요 |
| 디자인 결정 | 폰 **landscape 70°**, 65/70/75° 비교, 디스플레이 뒤 **슬림 수동 받침** | DEFAULT — 실물 게이트 뒤 고정 |
| 디자인 결정 | 완제품 MagSafe puck **탈착형**; 전원 **독립 USB-C PD**; 없어도 수동 거치 가능 | DESIGN FREEZE — 물리 미검증 |
| 사용자 제약 | 전면 트레이·세로 저각도 램프·과대 장식·임의 드릴링 금지 | REQUIRED |
| 제조 미확인 | 폰 케이스 L/W/T와 카메라, MagSafe puck 형상/케이블, C-BOX 체결부 및 포트, 책상, 질량/마찰 | **BLOCKER** |
| 소프트웨어 미확인 | 브라우저 V10을 실기에서 사용 가능, IDF/LVGL 빌드, 16MB OTA 롤백 | **NOT IMPLEMENTED / NOT TESTED** |

## 1. 발견된 불일치 / 우선순위

1. **P0 — HMI 체결부**: V14 SCAD의 `OEM_REAR_MOUNT_PITCH=75`를 양 축으로 가정하여 마커 **4개**를 찍는다. 문헌의 '75mm pitch'만으로 75 × 75 mm 나사 4개를 확정할 수 없다. 실물과 C-BOX 전용 외형도에서 개수/X·Y·나사 규격·유효 체결 깊이를 확인해야 하며, **현재 구멍 가공/나사 주문 금지**.
2. **P0 — 수동 슬롯과 MagSafe의 독립성**: 기존 `pokedock_v14_magsafe_ready.scad`는 puck가 시각용 원판일 뿐, 실물 케이블 클립·고정부·통풍·코일 위치 조절 메커니즘이 아니다. 충전 모듈을 포함한 STL 생산 불가.
3. **P0 — 전원**: Waveshare 4.3C 본체의 광범위 DC 터미널(7~36V)과 USB-C 디버그를 혼용해서는 안 된다. 12V/2A는 **정격 후보**이며 공급장치 인증, 플러그·극성·전압·소비전류 측정 전 통전 금지. MagSafe 20W 이상 USB-C PD는 완전히 다른 전원 도메인.
4. **P0 — 안정성**: 폰 단독 206g + 케이스 질량에 대한 70° 지지력, 책상과 4개 발의 마찰계수, 손가락 터치와 한 손 분리 시 전도 모멘트 검증 없음. 단순 면적 계산으로 안정성을 증명하지 못한다.
5. **P1 — 오래된 기본값**: `README.md`, `docs/V11_EXECUTION_INDEX.md`, `docs/V11_ASSEMBLY_SOP.md`, `cad/README.md`에 V12/V13을 최신처럼 묘사하거나 iPhone 14 **기본형**, 삼성 EP-P2400 Qi, 25~39° 세로 램프를 안내하는 문구가 남는다. **역사적 맥락만 남기고 최신 페이지에서 빼야 한다**.
6. **P1 — 깨진 링크**: `design.html`에서 존재하지 않는 `docs/V14_INDUSTRIAL_DESIGN.md`로 연결되어 있다.
7. **P1 — 계산기의 한계**: `design.html`의 체크박스는 비충전 82mm/충전 95mm **사전 가정값**만 전환한다. 실제 충전기 직경·케이블 꺾임·화면 후면 공간으로 깊이를 계산하지 않는다. 기구치수/실물 면적으로 인용 불가.
8. **P1 — 소프트웨어**: `firmware/hmi/main/idf_component.yml`에 BSP 3.0.1만 선언되어 있으며 **IDF 최상위 프로젝트/CMake + 실제 LVGL 스크린 구현은 없음**. 시뮬레이터 HTML은 MCU 실행파일 아님.
9. **P1 — 리워드 원자성**: `StudyEngine::tick()`의 완료 이벤트는 중복 발생하지 않도록 메모리상 IDLE로 전이하지만, 전원 차단 후 **NVS 원자적 exactly-once 저널**은 없다. 스프라이트 웹 원격 URL도 오프라인 펌웨어 자산이 아님.
10. **P2 — 문서·UI**: V13 SCAD의 `echo("V12 pose")` 등 로그와 V10 BOM 'Phone 14 variant 미확정'을 수정하거나 아카이브 선언해야 한다. 포켓몬 상용 IP의 이미지/울음소리를 공개 저장소에 무단 번들링하지 않는다.

## 2. 공간 산정: 실측 전에는 면적 두 종류로 보고

좌표: X=가로, Y=앞→뒤, Z=바닥↑, 경사는 바닥 기준.
폰의 긴 변은 X, 짧은 변은 경사면에서 Z/Y로 분해된다.

`span_x = 147.5 + case_extra_L`, `run = 71.5 + case_extra_W`,
`run_Y = run × cos(theta)`, `rise_Z = run × sin(theta)`.
가정 예시: case_extra_L/W=각 6mm **총 증가량**, 결과 폰 외형 153.5 × 77.5mm, 받침 하단 Y=42/Z=7, 측면 여유 X=8mm/쪽. 제조 사용 금지.

| 폰 기울기 | Y 투영 | Z 투영 | 상단 Z(하단 7mm 가정) |
| --- | ---: | ---: | ---: |
| 65° | 32.8mm | 70.2mm | 77.2mm |
| **70°** | **26.5mm** | **72.8mm** | **79.8mm** |
| 75° | 20.1mm | 74.9mm | 81.9mm |

기존 V14 모형: `BASE_W = max(116.3+16,153.5+16) = 169.5mm`; `BASE_D = max(95,42+26.5+22) = 95mm`; 직사각형 bounding box **161.0cm²**. 이는 **전체 외곽 상자 추정치**이지 실측 책상 접촉면적·안정성·충전 가능 깊이가 아니다.

휴대폰 긴 변 153.5mm vs HMI 116.3mm로 좌우 **18.6mm/쪽**의 폰 노출이 생긴다. 이것을 감추려고 폭을 더 늘리는 디자인은 금지. 눈높이 가림은 HMI 틸트/시점에 따라 달라져 직접 촬영 필요.

**실제 기록해야 할 세 값**: (1) 바닥 접촉 발/프레임이 차지하는 footprint, (2) 휴대폰 포함 최대 XY bounding rectangle, (3) 사용 중 케이블·손가락 이동을 포함한 후면 clearance. 계산기에는 (2)만 시험값으로 보여 줄 수 있다.

## 3. 최종 권장 기구 아키텍처 — 모듈화

- **A / 기본형**: OEM 케이스를 뜯지 않은 전면 HMI + 얇은 기구 연결 브래킷 + 분리 가능한 후면 폰 랙. 두 개의 넓은 소프트 접점과 하부 lip, 양 끝 작은 정렬 스토퍼. 폰 무게가 마그넷에 의존하지 않는다.
- **B / 선택 충전형**: A와 같은 랙에 코일 중심을 X/Z로 조절할 수 있는 **독립 2-piece 열린 puck holder** 설치. holder는 puck의 앞면을 덮지 않고 뒤·테두리만 잡는다. 충전기를 풀어도 A가 온전해야 한다.
- **상용 부품 우선 대안**: 미끄럼 방지·전도 검증을 통과한 소형 상용 테이블 스탠드+부착형 배면 랙의 조합은 3D 프린트보다 먼저 비교할 가치가 있다. 평판 아크릴 레이저 가공은 3D 곡면 커넥터·정확한 클립 형상이 필요해지기 전까지 유효.
- **재료**: 임시 카드보드/폼보드 → 조절식 볼트/클램프 시제품 → 최종 PETG/PC/가공 아크릴 선택. PETG 4~6mm는 *예제*이며 공정/하중 실험 없이 강도 확정 금지. 접촉부는 교체 가능한 TPU/실리콘 패드, 발 4점, 매입/둥근 모서리.
- **화면 조작 중 안정성**: 손가락 힘/폰 탈착 자석 인력 방향의 실제 최대값을 저울/간이 힘 측정으로 파악하고 해당 위치에서 기구가 들리지 않는지 검사. 안전 규정 없이 임의의 뉴턴 합격 수치를 만들어내지 않는다.
- **열/포트**: HMI DC terminal/BOOT/RST/SD/USB/RTC 및 Wi-Fi 안테나 영역을 가리는 폐쇄형 등판 금지. 케이블은 저전압 외피만 함께 정리하며 독립 규격의 어댑터 출력을 서로 합치지 않는다.

## 4. 실측 등록부 (빈 칸은 0이 아님)

| ID | 항목 | 단위 | 실측값 | 게이트 |
| --- | --- | --- | --- | --- |
| PH-L | iPhone 14 Pro+케이스 긴변 | mm | TBD | CAD 폭 |
| PH-W | 폰+케이스 짧은변 | mm | TBD | 폰 슬롯 |
| PH-T | 접촉면 두께 / 카메라 범프 최대값 | mm | TBD | 레일 간섭 |
| PH-COIL | 실제 충전 코일 중심: 좌/하단 기준 X,Z | mm | TBD | puck carrier |
| PK-D/T | 완제품 puck 직경/높이 | mm | TBD | puck carrier |
| PK-C | puck 일체 케이블의 출구·허용 굽힘·USB-C 플러그 공간 | mm | TBD | 깊이/발열 |
| HMI-O | 실제 C-BOX 외형/포트 돌출 | mm | TBD | 받침 연결 |
| HMI-M | OEM **구멍 개수/XY 위치/나사 규격/깊이** | mm/thread | TBD | 구멍 제작 |
| HMI-I | DC 입력 단자 극성·실제 동작전압/전류 | V/A | TBD | 통전 |
| DESK | 배치 위치 가용 폭/후면 깊이/상부 장애물 | mm | TBD | 전체 |
| TEST-F | 무게중심/미끄럼/한손 착탈 결과 | log | TBD | 최종 |
| TEST-T | 화면 ON + 충전 60분, 실측 온도·충전 유지 | °C/log | TBD | B 승인 |

## 5. 구매 BOM — 수량, 단계 및 불필요한 구매 방지

공식 가격/제원은 발주일 재검증: [Waveshare C-BOX](https://www.waveshare.com/product/esp32-s3-touch-lcd-4.3c.htm) (패밀리 표시 US$39.99–45.99, 옵션별 수수료/배송 별도), [Apple KR MagSafe 1m A3502](https://www.apple.com/kr/shop/product/mgd74kh/a) (2026-10-19 조회 ₩65,000; 단품, PD 어댑터 별도). 국내 재고/배송·가공비는 미확인: 확정 원화 합산 금지.

| 단계 | 수량 | 부품/품명 | 구매 기준 / 선행 조건 |
| --- | ---: | --- | --- |
| P1 필수 | 1 | Waveshare 4.3C-BOX **SKU 33630** | bare 33799, 4.3B, 구형 4.3 반품 |
| P1 조건 | 1 | **인증된 절연형 안정화 DC 12V/2A 후보** 및 단자용 절연배선 | **보드 DC 단자·극성 사진/공식 회로와 실물** 확인하고 선택; 어댑터 12V가 USB-C로 들어가면 안 됨 |
| P1 재사용 | 1 | 데이터 가능한 USB-C 케이블 | PC 인식 확인 |
| P1 조건 | 1 | CR927 RTC 셀 | 동봉 여부와 극성 확인 |
| P1 조건 | 1 | microSD 16–32GB | FAT 포맷은 벤더 예제 설정 확인 |
| P0 재사용 | 1set | 캘리퍼, 멀티미터, 자/각도기, 폼보드, 작은 클램프 | 시제품 우선 |
| P2 조건 | 1 | Apple 1m MagSafe 충전기 A3502 또는 **기존 완제품 충전기** | P0 실측·폰+케이스 무료 결합 테스트 후 |
| P2 조건 | 1 | 인증된 USB-C PD 20W+ 어댑터 | 기존 호환품 재사용 우선; 별도 전원 |
| P3 지연 | 1set | 최종 브래킷/받침 가공 (PETG 또는 PC/아크릴), 4개 발, 패드, 배선 클립, 체결구 | **HMI-M/PH-L/PH-W/PK-D/T** 확보 및 목업 게이트 후 |
| P3 지연 | 1 | 완제품 puck 후면 개방형 탈착 캐리어 | puck 실측 후에만 |
| P4 지연 | 0 | ESP32-C3, PN532, BH1750, VL53L0X, LED, 추가 충전코일, 배터리, 추가 RTC | MVP 동작 전 구매 금지 |
| P4 지연 | 0 | 별도 스피커 | 동봉품/코덱 출력 커넥터/임피던스 확인 뒤 결정 |

**총액 계산 방식**: (선택한 33630 실제 공급가×현찰환율+운송·세금) + 국내 인증 DC 부품 + 필요한 소모품 + (선택형 충전 65,000원+PD 어댑터) + 현장 가공 견적. 미확정 합계는 숫자로 고정하지 않는다.

## 6. SOP — 정확한 진행 순서 / 결과물 / 실패 시 분기

| Gate | 실행 | 기대 결과 | PASS / FAIL |
| --- | --- | --- | --- |
| G0 | 위 등록부에서 휴대폰+케이스 실측; 65/70/75° 폼보드 시제품 제작 | 종이치수 + 각도별 실제 사진 | 후면 깊이·폰 카메라·케이블 동선 확인; 미측정이면 최종 가공 FAIL |
| G1 | 33630 모델/리비전/패키징 확인, 포트 사진/공식 회로 확보 | 보드·명세치 일치 | 다른 SKU/극성 불명 → 전원 인가 FAIL |
| G2 | 절연된 DC 전원 단독 인가, USB 데이터 연결, Factory Demo 백업/복구 방법 확보 | 켜짐, LCD/GT911 touch 모든 가장자리, 60분 리셋 없음 | 전압 드롭/과열/터치 뒤집힘 → 배선·벤더 예제부터 |
| G3 | RTC PCF85063A + CR927 껐다 켜기 5회, microSD read/write 10회, 볼륨을 제한한 OEM 오디오 예제(스피커 장착 시) | 날짜 보존, SD 오류 0, 오디오 연결 검증 | 셀 극성/포맷/케이블 재점검 |
| G4 | 임시 폰 받침 제작 후 실제 폰을 한손으로 30회 거치·분리, 화면 터치와 책상 흔들림 실험 | 손가락 동작 동안 전도 없음, 카메라/버튼 간섭 없음 | 실패 시 바닥 폭/후면 발/고정 방식 우선 재설계 |
| G5 | 분리형 MagSafe를 **외부 독립 PD**에 연결해 60분 충전, HMI도 켠 상태에서 기록 | 실제 아이폰 충전 표시 지속, 불규칙한 멈춤/과열 없음 | 미달 시 puck 설계·통풍을 개선하거나 A형 패시브로 출고 |
| G6 | 캘리퍼 실측 기반 최종 CAD: 케이스 마운트/USB/DC/RST/SD 통로/단자와 펌웨어 복구 통로 확보 | CAD 간섭 점검과 도면/출력/견적 | 체결 나사 정보/결정적 여유가 비면 발주 FAIL |
| G7 | 벤더 지정 커밋+IDF 버전 lock → factory example build → 800×480 LVGL HOME → 실제 Focus Timer | 실제 실기 화면에서 눌림, 휴식/일반 타이머는 보상 0 | **웹 시뮬레이터 PASS는 이 Gate 통과 아님** |
| G8 | StudyEngine 검증 + 버전 NVS journal(세션 ID), 5회 재부팅/전원 차단, SD 없음/와이파이 없음 | 한 번의 완료만 적립, 결손 시 조용한 복구 | 중복 적립/오프라인 먹통이면 FAIL |
| G9 | 스프라이트 로컬화, night/focus animation freeze, private note 소거, 60분 메모리/터치 부하, 최종 나사 분해 | 유지보수 가능한 선물 MVP | 오디오/NFC/OTA/ANCS는 미구현이어도 MVP 통과 가능 |

선물 포장 직전: 실측 제품 폭/깊이/높이 및 충전기 유무를 최종 기록하고, 케이블은 날카로운 절단면/핀치 포인트에서 보호한다. RTC 실패시 '시계 미동기화'로 표시하고 타이머는 별도 단조시간 기반으로 유지한다.

## 7. 펌웨어 실기 포팅 의존성

1. **Vendor baseline**: Waveshare 4.3C official `examples/esp-idf`에서 실제 33630 PCB 리비전에 맞는 demo를 선택, SHA 및 ESP-IDF/sdconfig/LVGL 버전/원본 bin 백업. 관리 BSP `waveshare/esp32_s3_touch_lcd_4_3c@3.0.1`는 후보. 로컬 예제 CH422G vs 관리 BSP CH32V003 IO expander 명칭 차이를 임의 혼합하지 않는다.
2. **Native MVP**: ESP-IDF project CMake를 만들고 vendor LCD/touch를 검증한 후 `HOME -> FOCUS -> TIMER -> MENU` 순서로 LVGL screen을 만든다. `StudyEngine`은 portable C++로 연결하고 LVGL task가 UI 소유; RTC read/NTP sync 실패와 monotonic time을 분리.
3. **Persistent state**: NVS 버전 schema와 atomic session-ID commit/idempotency. 데이터 크기가 큰 사용자 자산과 저작권 적법한 이미지/PCM은 SD 사용; 내부 flash에 Gengar fallback 한 프레임.
4. **Power failure**: 재시작 뒤 완료되지 않은 타이머에 임의의 집중시간 적립 금지. 충전·와이파이·microSD·선택 C3 오류로 HOME/Focus가 중단되면 FAIL.
5. **USB first**: 최초 복구는 USB/BOOT/RESET 가능한 구조. 16MB dual-slot CSV는 **미검증 예제**이므로 사전 앱 크기/부트 오프셋 확인·전원 차단·롤백 테스트 없이는 OTA 기능을 켜지 않는다.
6. **검증 증거**: 빌드 콘솔 로그, 빌드 해시, config, 벤더 baseline SHA, 전압/전류, 핀맵, 30회 착탈, 60분 충전, 실제 사진. 모든 미실시 항목은 OPEN.

## 8. 제조 가능 판정 (2026-10-19)

- **GO**: 측정용 목업, 33630 정확한 SKU 주문, 인증 정격 DC 전원 검토, 제조사 factory firmware 개발환경.
- **CONDITIONAL**: 완제품 MagSafe/PD 어댑터 구매 — 기보유 여부 및 스마트폰 실제 테스트 후.
- **NO-GO**: 현재 SCAD 그대로 STL 출고, 75×75mm 홀 가공, 스피커/센서/NFC/LED 선구매, MagSafe로 MCU 직접 공급, 기존 V10 HTML MCU에 업로드, OTA 기능 배송.

참조: [V14 design](V14_MAGSAFE_READY_DESIGN.md) · [BOM](V14_PURCHASING_BOM.md) · [SOP](V14_ASSEMBLY_SOP.md) · [V14 verified electrical map](V14_ELECTRICAL_INTERFACE.md) · [measurement register](V12_MEASUREMENT_REGISTER.md) · [vendor 4.3C documentation](https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3C) · [Apple MagSafe 1m](https://www.apple.com/kr/shop/product/mgd74kh/a).
