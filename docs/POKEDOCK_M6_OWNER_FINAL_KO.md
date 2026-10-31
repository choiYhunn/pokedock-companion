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

## D. 완제품 수령 후: 선물 콘텐츠 설치 (도구 수정 완료, 실기 미검증)

1. 제조업체가 준 완제품부터 확인합니다. 5 V USB-C 어댑터로 시계·타이머·알람이 정상인지 봅니다.
2. `Documents\프로젝트\PokeDock_Private_Assets\src\`에 8종 GIF가 있는지 확인합니다.
   - 파일명: `94.gif`, `393.gif`, `468.gif`, `448.gif`, `195.gif`, `175.gif`, `417.gif`, `385.gif`(또는 `<번호>_idle.gif`).
   - 없을 때 쓰는 `tools/fetch_private_sprites.py`는 제3자 공식 그림을 내려받습니다. **이용 권리와 사적 용도를 판단한 뒤에만** 선택적으로 사용합니다.
3. 숨겨진 메시지는 같은 폴더의 `src\message.txt`에 UTF-8로 저장합니다(90바이트 이하, 한글 약 30자). 공개 저장소에 올리지 않습니다.
4. PC와 완성품을 후면 USB-C **데이터 케이블**로 연결하고, 장치 관리자에서 `COM` 번호를 확인합니다.
5. 아래 명령을 PowerShell에서 차례로 실행합니다. 예시의 `COM5`는 확인한 번호로 바꿉니다.

```powershell
cd "$env:USERPROFILE\Documents\프로젝트\pokedock-companion-m6"
git switch feature/m6-gift-content-20261031
git pull --ff-only
cd v16\masterball-m6
python -m pip install --user "esptool>=4.7,<5" pillow
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
$PO = "$env:USERPROFILE\Documents\프로젝트\PokeDock_Private_Assets\out"
python tools\make_assets.py "$env:USERPROFILE\Documents\프로젝트\PokeDock_Private_Assets\src" $PO
python tools\make_app_images.py --mfg-zip "$env:USERPROFILE\Documents\프로젝트\PokeDock_M6_RevC_Vendor_20261031\PokeDock_M6_RevC_Vendor_Package_20261031.zip"
.\tools\flash_gift_windows.ps1 -Port COM5 -Action Check
```

6. `Check`가 출력한 `app on the ball:` 줄을 보고 하나만 실행합니다. 도구가 계획을 보여주면 `YES`를 입력합니다.

| `Check` 출력 | 볼 | 실행할 명령 |
|---|---|---|
| `pokedock_m6_mfg_app.bin` | 일반 방향 | `.\tools\flash_gift_windows.ps1 -Port COM5 -Action InstallGift -PrivateOut $PO` |
| `pokedock_m6_mfg_app_rotate180.bin` | 180° 회전 | `.\tools\flash_gift_windows.ps1 -Port COM5 -Action InstallGift -PrivateOut $PO -Rotate180` |

7. 목표 상태 **m6-0.4.0-gift**는 앱(0x10000), 팩(0x610000), 메시지 슬롯(0xFFF000) 세 가지로 이루어집니다. `InstallGift`가 셋을 한 번에 씁니다.
   - 제조 앱 m6-0.3.0에 팩만 넣으면(`-Action UpdateAssets`) 그림은 보입니다.
   - 하지만 잠자기·♥·★·축하·알람 반응·비공개 메시지는 동작하지 않습니다.
8. 적용 후 실제 AMOLED에서 다음을 시험합니다.
   - 팬텀·팽도리 등 8종, 5탭 메시지, 25분 집중 완료, 잠자기·깨기, 알람, 화면 FPS.
   - 설치 전에 정해 둔 알람·밝기가 그대로인지(설정 보존).
   - `RemoveAssets`·`RestoreMfgApp`로 되돌린 뒤 다시 설치되는지.

   이것을 모두 확인한 뒤에만 선물용으로 완성 판정합니다.

### 플래시 도구 안전 문제: 2026-11-01 PR #23에서 수정

| 문제 | 수정 | 검증 수준 |
|---|---|---|
| 병합 RAW BIN을 0x0부터 써서 설정 NVS(0x9000–0xEFFF)를 지울 수 있음 | 앱 전용 이미지를 **0x10000에만** 씁니다. 병합 이미지는 거부합니다. 부트로더·테이블·NVS는 쓰지 않고, 쓴 뒤 다시 읽어 비교합니다. 앱 전용 이미지는 병합 이미지의 0x10000 이후와 바이트 동일하고, 제조·선물 빌드의 파티션 테이블·플래시 헤더·IDF가 같습니다 | 실제 이미지로 검사 23개, 가짜 플래시로 시험 38개 통과 |
| NVS 백업·복원 없음 | 매번 **전체 16 MiB 백업 + NVS 별도 사본 + SHA-256 기록**을 먼저 받습니다. 복원은 `-Action RestoreNvs -From <nvs 백업>`(0x6000 B만) 또는 `-Action RestoreFull -From <전체 백업>`으로 합니다 | 가짜 플래시로 확인 |
| `Esp @(...)` 배열 splatting | 이름 있는 인자 `Invoke-Esp -EspArgs @(...)`와 `& $exe @argList`로 고쳤습니다. 이와 함께 5.1에서 esptool의 stderr가 중단 오류가 되는 문제도 고쳤습니다 | Windows PowerShell 5.1에서 명령 문자열을 정확히 비교. 실제 esptool 4.12.0이 기록된 9개 명령을 해석함 |
| 잘못된 파일·포트·방향, 중간 중단 | 칩·16MB·테이블·앱 종류·방향을 확인하고 틀리면 기록 전에 중단합니다. 중단되면 쓰기 직전 백업으로 `RestoreFull`하라고 정확한 명령을 출력합니다 | 가짜 플래시에서 중단 후 16 MiB 전체 동일 복원 |

**실제 볼에서는 아직 한 번도 실행하지 않았습니다.** 첫 실행은 `Check` → `Backup` 순서로 합니다. 백업 파일(`PokeDock_Private_Assets\backups\`)에는 메시지와 그림이 들어 있으니 공유하지 않습니다. 되돌리기 명령 전체는 `v16/masterball-m6/docs/GIFT_CONTENT_KO.md` §7에 있습니다.

제조용 PR #21, m6-0.3.0 이미지, 업체 ZIP과 그 SHA-256은 바꾸지 않았습니다(`3957049e…`, `0091aafa…`, ZIP `715d6546…`).

## E. 브랜치 운영

- 제조: [PR #21](https://github.com/choiYhunn/pokedock-companion/pull/21) = m6-0.3.0, 그대로 Draft·동결.
- 선물: [PR #23](https://github.com/choiYhunn/pokedock-companion/pull/23) = m6-0.4.0-gift, PR #21 위에 쌓은 별도 Draft. `main`으로 지금 병합하지 않습니다.
- 모바일 V18: 이미 `main`에 병합된 GitHub Pages 웹앱. iPhone Safari PWA의 일반적인 BLE 미지원과 별개로, M6의 **기기 자체 시계 설정**이 가능합니다.

## F. 최종 완료 정의

완제품 실제 사진, 후면 USB 안정성, G1/G2 기록, 기기 내 시간·알람 설정, 24 h 안정성(포함 계약 시), 팬텀 애니메이션 실기 재생, 개인 메시지 표시, 백업·복원·설정 보존을 확인하기 전에는 '선물 준비 완료'로 표기하지 않습니다.

*이 문서는 사용자가 따라 할 작업 안내이며, 제조/선물 펌웨어의 실기 검증 자체를 대신하지 않습니다.*
