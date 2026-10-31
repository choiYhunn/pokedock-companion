# PokéDock M6 — 사용자용 최종 실행 안내서 (2026-11-01)

> **읽는 대상: 의뢰인.** CAD 재설계나 직접 납땜을 할 필요가 없습니다. **제조용 ZIP은 업체에**, **포켓몬 GIF·개인 메시지는 의뢰인의 PC에만** 둡니다.
> 검증 기준: 제조 PR #21 / 선물 PR #23 (둘 다 Draft). 테스트 통과는 실물 검증이 아닙니다.

## A. 파일 3종 구분 — 가장 중요

| 구분 | 실제 파일/위치 | 사용 목적 | 외부 업체 전달 |
|---|---|---|---|
| **제조 ZIP** | `Documents\프로젝트\PokeDock_M6_RevC_Vendor_20261031\PokeDock_M6_RevC_Vendor_Package_20261031.zip` (Claude가 보고한 Windows 경로, 이 문서를 작성한 ChatGPT가 PC 파일 자체를 확인한 것은 아님) | 기존 STEP/STL, BOM, 회로/배선, 펌웨어 m6-0.3.0, G1/G2/FAT 검사 | **예. 이 ZIP만 전달** |
| **선물용 공개 코드** | GitHub [PR #23](https://github.com/choiYhunn/pokedock-companion/pull/23) / `feature/m6-gift-content-20261031` | 애니메이션 기능이 추가된 m6-0.4.0-gift, 빌드·플래시 도구, 설명서 | **업체에 기본 전달 불필요** |
| **비공개 포켓몬 자산** | `Documents\프로젝트\PokeDock_Private_Assets\src\`, `...\out\`(로컬 경로, 실제 파일은 PC에서 확인) | 8종 GIF, `assets_pack.bin`, `message.txt`, `message_slot.bin` | **아니오. 공유·Git 커밋 금지** |

제조 ZIP에는 `00_READ_FIRST_KO.md`, `MANIFEST.json`, `vendor/02_RFQ_TURNKEY_KO.md`, `vendor/BOM_TURNKEY.csv`, `cad/out/step/`, `cad/out/stl/`, `cad/out/fitkit/`, `electronics/`, `firmware/pokedock_m6_merged.bin`, `firmware/SHA256SUMS.txt`가 있어야 합니다.

제조 ZIP의 기대 SHA-256 (제작자 보고, `vendor/MFG_PIN.json`):
`715d65469f6e81dbdd9cecaeca02150b785168629ba1d044166bd73f3f32a88d`.
실제 PC에서 계산한 값과 일치하는지 확인하고, 다르면 송부 전에 중단합니다. *제조 ZIP을 PR #23 브랜치에서 새로 빌드하지 않습니다.*

## B. 지금 바로 할 일 (기기 없이 가능)

1. PC에서 위 제조 ZIP이 실제 있는지 확인합니다. 압축을 풀지 않아도 파일 목록을 열어 `00_READ_FIRST_KO.md`, `firmware/`와 STEP/STL 포함 여부를 볼 수 있습니다.
2. 가능하면 PowerShell에서 `Get-FileHash -Algorithm SHA256 -LiteralPath "<ZIP의 전체 경로>"`를 실행해 위 SHA-256과 비교합니다. 계산한 값이 다르면 기존 제조용 브랜치에서 Claude Code가 해당 ZIP을 확인/재생성하도록 합니다.
3. 업체 2곳에 **같은 ZIP과 같은 견적 요구사항**을 전달합니다. 견적은 부품 실비, G1 보드/전기, G2 시험 출력, 본 출력, 조립/검수, 배송비를 분리해 받습니다. 신규 디자인·전체 회로 재설계 비용은 기본 범위에서 제외하고, 필요한 수정은 사전 동의로 제한합니다.
4. 업체 선정 전에는 직접 전자부품을 따로 사거나 3D 본 출력을 주문하지 않습니다. **G1 실물 검사 → G2 핏 키트 → 본 출력** 단계를 계약에 넣습니다.
5. 업체에 전달할 수 있는 설명서: [제조 PR #21](https://github.com/choiYhunn/pokedock-companion/pull/21) / ZIP 첫 문서 `00_READ_FIRST_KO.md`; 제조 문서의 화면에는 '포켓몬 이미지 필요'라는 문구가 정상이고 GIF는 포함되지 않습니다.

**견적 문의 문구 (붙여 넣기):**
> 지름 약 138 mm 원형 AMOLED 탁상 장치 1개를 기존 CAD/회로/펌웨어 그대로 턴키 제작하려고 합니다. 첨부 ZIP에 STEP/STL, BOM, 배선도, 검수 SOP와 펌웨어가 있습니다. 부품 구매대행, 납땜·배선, G1 실보드 검사, G2 시험 출력, 최종 FDM 출력, 조립·검수·배송 일괄 견적을 항목별로 부탁드립니다. 각 단계에서 측정·사진·영상 보고를 받고 승인 후 다음 단계로 진행하고 싶습니다. 신규 제품 개발/재설계는 기본 견적에서 제외해 주세요.

## C. 업체 진행 중 승인할 것

| 시점 | 업체 증거 | 사용자 판단 |
|---|---|---|
| S1 부품 입고 | 보드 **Waveshare SKU 30106** 사진, 부품 목록과 영수증 | 모델·수량 승인. 보드는 1대 제작 + 예비 1대 선택 견적 |
| S2/G1 전자 시험 | 전원·화면·터치·부저·후면 USB·기기 자체 시간 설정 동영상, 소비전류, 치수·로그 | 기록·검사표 통과 전 G2 불가 |
| S3/G2 맞춤 출력 | 베젤/USB/나사/쉘 조인트 맞춤 사진, **버튼 틈 K11**, 무광 재료·색 견본 | 틈·치수·색감이 만족스러우면 본 출력 승인 |
| S4 최종 3D/조립 | 조립 중 사진, 외관 사진 | 외관·나사/배선 상태 |
| S5 완제품 검수 | 6방향 사진, 전원→시계→타이머→알람 시연 영상, 최종 검사표 | 통과 후 배송 승인. **24시간 시험 포함 여부를 견적서에 명확히 명시** |

제조용 제품은 **선물용 포켓몬 애니메이션이 없어도** G1/G2/FAT를 진행할 수 있습니다. 제조사에 포켓몬 GIF/개인 메시지를 보내지 않습니다.

## D. 완제품 수령 후: 선물 콘텐츠 설치 (지금은 실행 금지)

1. 제조업체가 준 완제품의 정상 동작부터 확인하고, 5 V USB-C 어댑터로 시계/타이머/알람 테스트.
2. **선물용 플래시 도구의 아래 안전 문제를 먼저 수정·재검증해야 합니다.** GitHub PR #23에 수정 요구를 기록합니다.
3. 수정 뒤 `Documents\프로젝트\PokeDock_Private_Assets\src\`에 8종 GIF가 있는지 확인합니다. 파일명은 `94.gif`, `393.gif`, `468.gif`, `448.gif`, `195.gif`, `175.gif`, `417.gif`, `385.gif`(또는 `<번호>_idle.gif`). 없는 경우 `tools/fetch_private_sprites.py`는 제3자 공식 그림을 내려받으므로 **이용 권리 및 사적 용도 판단 후에만** 선택적으로 사용합니다.
4. 숨겨진 메시지는 같은 `src\message.txt`에 UTF-8 텍스트로 저장합니다(90바이트 이하; 한글 약 30자). 사적인 문장은 직접 작성하고 공개 저장소에 올리지 않습니다.
5. 해당 선물용 브랜치에서 Python과 Pillow를 준비한 뒤 `python tools/make_assets.py "<비공개 src 경로>" "<비공개 out 경로>"`로 `assets_pack.bin`과 `message_slot.bin`을 생성합니다.
6. 수정·검증된 안전한 플래시 도구를 사용해 PC와 완성품을 후면 USB-C **데이터 케이블**로 연결하고 `COM` 번호를 확인합니다. **현재 버전의 `flash_gift_windows.ps1`을 그대로 실행하지 마세요.**
7. 제조용 앱 m6-0.3.0은 GIF를 표시할 수 있으나 선물 동작(잠자기·♥·★·축하·알람 반응·비공개 메시지)을 모두 제공하지는 않습니다. 목표 상태가 **m6-0.4.0-gift**라면 **애플리케이션 펌웨어 + assets 팩 + 메시지 슬롯** 모두 필요합니다.
8. 적용 후에는 실제 AMOLED에서 팬텀·팽도리 등 8종, 5탭 메시지, 25분 집중 완료, 잠자기/깨기, 알람, 화면 FPS를 시험합니다. 설정 보존과 복원까지 확인한 뒤에만 선물용으로 완성 판정합니다.

### 선물용 플래시 도구에서 수정해야 할 두 가지 중대한 문제

**1. 설정(NVS) 소실 위험 — 확정된 설계 결함**

현재 `tools/flash_gift_windows.ps1`은 `-GiftFirmware` 또는 `-RestoreFirmware`에 지정된 **병합 RAW BIN을 0x0부터 연속으로** 씁니다. ESP-IDF `firmware/partitions.csv`의 `nvs`는 `0x9000~0xEFFF`입니다. Espressif 문서에 따르면 RAW merge 이미지의 사이 공간은 0xFF로 채워지고 단일 이미지를 기록할 때 해당 영역도 지워집니다. 따라서 "NVS가 보존된다"는 기존 안내는 사실이 아닙니다.

- **권고:** 선물/복원 펌웨어는 가능하면 **앱 바이너리만 0x10000**에 플래시(부트로더·파티션 테이블 변경 없음 검증), 또는 최소한 NVS와 필요한 설정 영역을 백업/복원하는 안전 절차를 마련하세요.
- 일단 `-GiftFirmware`와 `-RestoreFirmware`를 실행하지 않습니다. **기존 설정 보존을 실제 기기에서 시험한 뒤** 사용자에게 배포합니다.

**2. PowerShell 함수 인자 전달 재검증**

`function Esp([string[]]$ArgsList)`에 `Esp @("read_flash", ...)` 같은 **배열 splatting**을 사용합니다. PowerShell은 배열 splatting을 위치 인자로 나누므로 단일 `ArgsList` 파라미터에 인자 전부가 묶이는지 검증해야 합니다. `Esp -ArgsList @("read_flash",...)`처럼 명시적 인자 전달로 수정하고 실제 Windows PowerShell 5.1 환경의 mock/esptool 명령 출력으로 검증하세요.

스크립트 수정은 **선물용 PR #23에서만** 진행하고 제조용 PR #21·업체 ZIP/펌웨어 PIN은 변경하지 않습니다. 코드 수정 뒤 strict 재검증을 통과해야 합니다.

## E. 브랜치 운영

- 제조: [PR #21](https://github.com/choiYhunn/pokedock-companion/pull/21) = m6-0.3.0, 그대로 Draft·동결.
- 선물: [PR #23](https://github.com/choiYhunn/pokedock-companion/pull/23) = m6-0.4.0-gift, PR #21 위에 쌓은 별도 Draft. `main`으로 지금 병합하지 않습니다.
- 모바일 V18: 이미 `main`에 병합된 GitHub Pages 웹앱. iPhone Safari PWA의 일반적인 BLE 미지원과 별개로, M6의 **기기 자체 시계 설정**이 가능합니다.

## F. 최종 완료 정의

완제품 실제 사진, 후면 USB 안정성, G1/G2 기록, 기기 내 시간·알람 설정, 24 h 안정성(포함 계약 시), 팬텀 애니메이션 실기 재생, 개인 메시지 표시, 백업·복원·설정 보존을 확인하기 전에는 '선물 준비 완료'로 표기하지 않습니다.

*이 문서는 사용자가 따라 할 작업 안내이며, 제조/선물 펌웨어의 실기 검증 자체를 대신하지 않습니다.*
