# PokéDock V14 — 2026-10-20 비용/완성 리스크 재평가와 구매처 조사

**현재 결론: 기존 4.3C-BOX 33630 유지, 고액 일괄구매 금지. 무료 기구 목업 → 정확한 보드 1대만 확보·기초 검증 → LVGL 화면과 터치 증명 → 나머지 구매. 100% 완성 보장 불가.** 이 문서는 리서치 스냅샷으로 가격·배송·재고는 결제 단계에서 재확인. 원래 BOM [V14_PURCHASE_AND_BUDGET.md](V14_PURCHASE_AND_BUDGET.md)의 기준 모델·소스는 유지한다.

## 실제 목표와 리스크
| Feature | 분류 | 근거 / 남은 결함 |
| --- | --- | --- |
| 정확한 4.3C 800×480 터치, 시계, Focus/timer | 구현 가능성 높은 핵심 | 벤더 BSP/LVGL native build PASS; real 33630 LCD/touch flash & fallback/NTP/RTC untested |
| 팬텀/팽도리 등 로컬 애니메이션 + 단계별 성장 | 구현 가능하나 시각 품질/부드러움/자산 이슈 | 동작 정책 C++ 호스트테스트 PASS; 화질/SD load/RAM/프레임레이트 없음 |
| 메모·DDay·일정·미니게임 | 대부분 가능, 범위 통제 필요 | 웹 UI는 native MCU와 다름, 수동 입력·NVS schema/history & UI 작성 필요 |
| iPhone 실시간 알림·원격 동기화·충전 상태 MCU 표시 | **현재의 MVP promise에서 제외** | iOS 연동 추가 앱/권한/ANCS 프로토콜 및 검증 데이터 없음. MagSafe는 독립형 |
| 가로 70° 폰 거치, 작고 예쁜 기구 | 가능하지만 실측 주요 리스크 | iPhone case+camera/puck/housing insert/desk depth 전부 무측정, OpenSCAD DFM 출력만 통과 |
| Qi2/MagSafe 실제 충전 | 제조사가 완제품이면 가능, **충전형 통합은 미검증** | 60분 heat/alignment/magnet/cable exit 테스트 필수 |
| 소비재 수준 매일 사용할 완제품 | **아직 검증 안 됨** | 보드 수령/원장 NVS/실제 조립·인수검사 필요 |

**실패해도 감당할 자본 제한:** (0) cardboard 65°/70°/75° 모형(기보유품) → (1) Waveshare 정확한 SKU 33630 보드 하나. 한국 착지가 9만원 이상이면 재비교하고 무작정 주문하지 않는다. SD/전원/충전기/3D 가공은 우선 보류. 보드 한 개가 가장 중요한 선행 투자이고, 유사 4.3B나 케이스 미포함 33799로 바꾸면 설계 및 보드 드라이버 검증을 다시 해야 한다.

## 판매처 가격 교차 확인 (10월 20일 공개 페이지 기반)
| Part/offer | Listed price | Source | Verified match? | Interpretation |
| --- | --- | --- | --- | --- |
| Waveshare 4.3C family, **With plastic case** SKU 33630 | USD **$39.99–$45.99** family variants, before shipping & conversion | https://www.waveshare.com/product/esp32-s3-touch-lcd-4.3c.htm | **YES when selecting with case; selected-option final checkout unavailable** | First purchase channel for OEM. Need Korea delivery quote and returns. |
| Eleparts 4.3C | **₩86,020 VAT incl** (+ shipping may apply) | https://eleparts.co.kr/goods/view?no=18220907 | **NO: no plastic case, 33799** | Not an equivalent price and limited foreign-stock returns. Don't buy to save money. |
| Coupang 4.3 inch listing | **₩63,600**, free shipping displayed at crawl | https://www.coupang.com/vp/products/8555295527 | **SKU/boxed variant not confirmed** | Cheap, but seller not verified for exact 33630 and 0 product reviews at time indexed. Must get photo of vendor SKU if considered. |
| Fruugo KR 4.3 with case | **₩158,190 + ₩1,049** shipping | https://www.fruugo.kr/waveshare-touchscreen-development-board-43-inch-with-case/p-506129890-1035518461 | model not fully verified | Too expensive to recommend relative to manufacturer family price. |
| Apple original A3502 1m | **₩65,000** | https://www.apple.com/kr/shop/product/mgd74kh/a | YES iPhone 14 Pro listed | Thin/verified ecosystem option, but too expensive to order before design. |
| Anker Zolo Qi2 A25M2 15W | **₩22,900 shipped** via price comparison pointing to official Naver store | https://prod.danawa.com/info/?pcode=104223722 | YES exact A25M2; real case needs test | Better value if 60×60×10.5mm fits. Thickness, retention and thermal risk. Manufacturer shop lists ₩24,900 sale but may be sold out: https://ankerkorea.co.kr/product/앤커-졸로-qi2-15w-고속-무선충전기-패드-a25m2/126/ |
| Samsung EP-T2510 25W USB-C PD no cable | **₩15,030 shipping included** per Danawa; Olive Young **₩16,500 free shipping** but shipping duration can be long | https://prod.danawa.com/info/?pcode=28885547 ; https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=B000000261686 | YES exact adapter family; confirm seller and stock | Reuse an existing reputable 20W+ compatible PD first; no additional cable necessary for fixed-cable puck |
| KC/matching 12V 2A adapter | Coms candidate **₩9,570** DeviceMart | https://chatgpt.com/?hints=search&q=Coms%2012V%202A%20DC%20adapter | 12V/2A rating candidate ONLY | No certainty barrel/terminal fit or certification documentation: DO NOT ORDER until board terminal/power behavior proven. |
| CR927 cell | HITAKA **₩150 + ₩3,000 shipping** single-unit comparison | https://price.enuri.com/catalog/55470791 | CR927 3V | Only if 33630 does not include coin cell; 10-pack is false economy |
| 32GB genuine microSD | SanDisk 32GB **₩15,000** Gmarket in indexed shopping result; old Samsung 32GB **₩10,300** YES24 but stock uncertain | https://www.yes24.com/product/goods/44012910 | Only if storage is needed | Build text/basic static sprites in flash first; microSD optional until heavy assets |

## Cost scenarios from 2026-10-19 17-row initial CSV and 10/20 price check
Existing source scenario: **A passive ₩129,000–243,500**, **B Apple original ₩213,030–348,800**. Replace Apple ₩65,000 with Anker Qi2 verified price ₩22,900 = **₩170,930–306,700** for B, with identical assumed printed holder and PD budget. Additive savings **₩42,100**; this is a calculation, not revised final cart. More savings by reusing SD/USB/PD and printing just two small brackets. More expensive reprint/air shipping remains unbudgeted.

**User-facing practical targets:** No separate power/SD purchase at start; stay under approximately ₩90,000 landed for one cased board (this is a voluntary purchase cap, not a verified market price). If actual landed Waveshare quote exceeds cap, pause, re-shop identical SKU or reconsider minimal design rather than buying a different PCB. If full system passes HMI/timer/geometry tests, proceed to **working budget ₩20만–25만** with Qi2 and light fixture, with worst-case BOM up to ₩30.7만. Do not promise a ₩20만원 all-in turnkey complete unit.

## Implementation gate before incremental spend
- **G0 zero cost**: actual phone+case photos/dimensions; simple 70° cardboard jig and desk occupancy; no phone fall, no occlusion/port conflict.
- **G1 ~≤₩90k board cap**: actual box SKU 33630, USB debug/vendor power test, real touch corners ×5 and 60min operation; hardware return window protection. Only at this stage see if manufacturer-sanctioned USB 5V supply can drive full unit; **4.3C USB-C currently described for flashing/debug; do not assume USB-only production power until OEM schematic/spec proof**, and do not borrow 4.3B/4.3 pinouts.
- **G2 native app proof**: LVGL touch HOME→FOCUS→BREAK, reset and restart, RTC trust, durable progress NVS rollback; benchmark smooth on-device animation.
- **G3 exact case/puck fitting**: trial cheaper finished Qi2 first only after G0/G1/G2 and measured puck, 60min charge with actual case. If poor heat/depth/force, return/refund if possible, then choose original Apple or omit wireless charging.
- **G4 final fabrication and gift**: exact OEM rear mounts + small PETG adapter → 30 dock cycles & 4h supervised soak + rescue binary.

### User decision
**GO**: If goal is working quiet Gengar clock/Focus/timer + cute private assets + landscape holder, accept 2-stage build and spend the first tranche. **NO-GO on 'guaranteed feature-complete consumer-grade product for ₩30만'**: impossible to assert before hardware tests, especially full smartphone integration and thin MagSafe fit. On failure before G2 stop spending; preserve board for resale/other MCU HMI projects (resale value not guaranteed).

Research provenance: all prices refer to public vendor or price-comparison pages inspected 2026-10-20, **not live verified checkout**. Return/refund policies for overseas electronics must be checked before payment. New GitHub Actions automation is not needed.
