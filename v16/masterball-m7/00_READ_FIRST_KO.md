# PokéDock M7 — 열리는 마스터볼 데스크 펫: 처음 읽는 제작 안내서

> **상태 (2026-11-02): CAD·호스트 검증 PASS / 외관 승인 대기 (본 출력 잠금) / 실물 미검증 / 제작 NO-GO 항목 남음.**
>
> - 이 폴더의 PASS는 모두 컴퓨터 안의 결과입니다.
>   - CAD 형상, 메시, 광선 추적
>   - 공식 회로도 텍스트 대조
>   - 호스트 펌웨어 시험
>   - 가짜 플래시 시험
> - 아직 아무것도 출력하지 않았고, 실제 보드에 조립하거나 플래시하지도 않았습니다.
> - **외관은 의뢰인이 직접 승인해야 확정됩니다**(`appearance/`). 승인 전에는 `print/02_final_LOCKED_until_appearance_approval/`을 출력하지 않습니다.
> - 실물 시험(§6)을 통과하기 전에는 "제조 가능"으로 확정하지 않습니다.
>
> 브랜치: `design/m7-openable-20261101` (Draft PR #24, base = PR #23 브랜치). 제조용 PR #21, 선물용 PR #23, 제조 ZIP과 고정 해시는 바꾸지 않았습니다(`tests/m6_frozen_check.py`).

## 1. 무엇을 만들었나

| 영역 | 결과 | 위치 |
|---|---|---|
| 기구 CAD | 부품 12종 STEP/STL, 열림 110°·닫힘 조립 STEP, 시험편 15종. 귀 위치는 두 안(A 위쪽 / B 사진 위치) | `cad/out/`, `cad/out_variant_B/` |
| CAD 생성 코드 | build123d 매개변수형. 제3자 CAD는 쓰지 않음 | `cad/build_m7.py`, `cad/m7_params.py`, `cad/ear_shape.py` |
| 기구 검증 | 간섭, 0–110° 연속 스윕, 스토퍼, 전도, 시야 광선, 닫힘 간극, 센서, 출력성. 귀 A·B 모두 | `cad/verify_m7.py` → `logs/verify_report.json` |
| **외관 승인 게이트** | 사진 비율 지표 17개, 구조상 불가 항목, 4면 리뷰 시트, 의뢰인 승인 파일 | `appearance/` |
| 화면 위치 최적화 | 높이·앞뒤 25개 후보 비교 | `cad/optimize_pod.py` → `logs/pod_sweep.json` |
| 출력 파일 | 시험편 5판(지금 출력 가능) + 색상별 본 출력 7판(**잠금**) + 귀 B안 뚜껑·귀 | `print/` |
| 전자 | 전원 B안(보드 자체 USB-C), 부저 IO16, 뚜껑 리드 센서 IO17 | `electronics/`, `docs/04_ELECTRONICS_KO.md`, `bom/ELECTRONICS_CONFIRMED_KO.md` |
| 펌웨어 | m7-0.5.0-gift: 닫힘 = 화면 끔, 열림 = 화면 켬 + 팬텀 등장. 새 보드용 FirstInstall | `../masterball-m6/core/lid_sensor.hpp`, `docs/05_FIRMWARE_INSTALL_KO.md` |
| 렌더링 | 실제 메시 렌더(열림, 닫힘, 사용자 눈높이, 측면, 사진 유사 카메라). 화면은 실제 Ø36.75 mm. AI 이미지 아님 | `img/`, `appearance/variant_B/` |

전체 검사 다시 돌리기: `PY=<python> bash tests/run_m7.sh` (결과 `logs/RUN_MANIFEST.json`).

## 2. 가장 먼저 할 일

1. **외관 확인과 승인**:
   - 볼 것: `appearance/APPEARANCE_REVIEW_KO.md`, `appearance/review_sheet.png`, `appearance/variant_B/`, PC 전용 사진 비교 그림 `Documents\프로젝트\PokeDock_Private_Assets\review\M7_photo_vs_cad_A_B_20261102.png`.
   - 귀 위치 A/B를 고르고, 마음에 들면 `appearance/APPROVAL.json`을 채웁니다.
   - 마음에 들지 않는 부분은 그대로 알려 주세요.
2. **먼저 살 것**(지금 주문해도 안전): Waveshare SKU 30106 × 1 + `bom/ELECTRONICS_CONFIRMED_KO.md` §1의 9개 품목(Digi-Key 1회).
   - 액추에이터 57155-000은 재고부터 확인합니다(리드타임이 길 수 있음).
3. **먼저 출력할 것**: 아무 색 PLA로 시험편을 출력합니다. 외관 승인과 관계없이 지금 출력해도 됩니다.
   - `print/01_fitkit_first/FK1_display_cradle.3mf` (46 mm 유리, M2 스탠드오프)
   - `FK2_hinge_stop.3mf` (Ø3 핀, 110° 스토퍼)
   - 결과는 `fitkit/FIT_MEASUREMENT_FORM.csv`에 적습니다.

## 3. 최종 질문에 대한 답

| 질문 | 답 | 근거 |
|---|---|---|
| 디자인 사진과 CAD가 얼마나 일치하나? | 사진에서 읽은 비율 지표 17/17이 허용 범위 안입니다. 주관적 유사도는 **약 75 %**입니다.<br>닫힌 외관(색, 10.5 mm 띠, 돔형 버튼 Ø23.6, 둥근 귀): 약 85 %.<br>열린 내부(라벤더 내부, 짙은 보라 받침대, 브래킷 나사): 약 70 %.<br>다른 점: 힌지가 뒷면 바깥, 검정 띠 윗면이 보임, 받침대가 원통형, 귀 위치(A/B 선택), 바닥 평면. **외관은 의뢰인 승인 전까지 미확정** | `appearance/APPEARANCE_REVIEW_KO.md` |
| 뚜껑이 구조상 열리고 닫히나? | **CAD상 예.** 0→110°(1° 간격) 충돌 0 mm³. 교체형 스토퍼 블록에 110°에서 면 접촉, 111°에서 2.2 mm³가 겹쳐 멈춤 확인. 67.7°부터 열린 채 유지. 자석 2쌍으로 닫힘. 열린 뚜껑과 귀가 책상에 닿지 않음 | `logs/verify_report.json` |
| 화면이 기울어진 상태로 안전하게 고정되나? | **CAD상 예.** 55°(지정 45–55의 위쪽 끝).<br>보드는 자체 M2 스탠드오프로 크래들에 고정하고, 유리는 립과 0.6 mm 떨어져 하중이 없습니다.<br>크래들(판 + 뒤 슈라우드 + 측면 브래킷)은 내부 커버에 M3 나사 4개(너트)로 체결. 닫힘 간극 3.6 mm | `img/section_display_x0.png` |
| 138 mm 안에 보드·USB·부저·배선이 들어가나? | **CAD상 예.** 공식 STEP 부품, USB 어댑터와 연장 커넥터, 부저, 구동 기판, 센서, 와셔 사이 간섭 0. 배선은 모두 내부 커버 아래 | `logs/verify_report.json` |
| 열었을 때 넘어지지 않나? | **계산상 넘어지지 않음.** 110°에서 무게중심이 발 안쪽 13.1 mm(최악 10.2 mm). 화면 중앙을 수직으로 누를 때 2.61 N(최악 1.90 N)까지 견딤(와셔 3장 + 발 8개). **실물 전도 시험 필요** | 같은 파일 5 |
| 학교 3D 프린터로 출력 가능한가? | **CAD상 예.** 전 부품 PLA, AMS 없이 색상별 7판. 모든 부품이 180 mm 정육면체 안(판은 256 기준). 열었을 때 보이는 서포트 면 0 mm² | `print/print_manifest.json`, `docs/06` |
| 정확히 무엇을 몇 개 주문하나? | `bom/ELECTRONICS_CONFIRMED_KO.md`: §1 확정(Waveshare, Digi-Key, 국내 기구), §2 실측 후(J1 소켓 Harwin M50-3000745, Adafruit 4432, 4218), §3 대체 설계(57155-000 → Ø8×3 자석 + FK4 시험) | `bom/BOM_M7.csv` |
| 납땜 없이 어디까지 직접 할 수 있나? | **의뢰인은 납땜하지 않습니다.** 도우미(학교·외주)가 `electronics/HELPER_BUILD_KO.md`대로 인터페이스 모듈(구동 회로, PTC, 나사 단자 2개, J1 소켓 피그테일)과 부저 리드선을 만들어 줍니다. 의뢰인은 단자 나사 조이기, J1 꽂기, 테이프, 나사 체결, 접착만 합니다 | `docs/07`, `img/module_schematic.png` |
| 펌웨어와 팬텀 애니메이션 설치는? | 새 보드에 `-Action FirstInstall` 1회(공장 백업 먼저). 이후 업데이트는 `InstallGift`(설정 유지) | `docs/05` |
| 첫 출력에서 확인할 공차는? | 유리 포켓과 립 0.6 mm, M2 스탠드오프, 핀 압입 2.9/회전 3.3, 스토퍼 110°, 벨트–하단 맞물림 0.35, 자석 Ø6.2, 센서와 액추에이터 포켓, 귀·버튼 자리 | `fitkit/FIT_MEASUREMENT_FORM.csv` |
| 최종 제작비는? | 필라멘트를 학교에서 제공받으면 약 14–19만 원, 직접 사면 약 27–32만 원(예비비 25 % 포함, 추정) | `bom/PURCHASE_PLAN_KO.md` |
| 남은 NO-GO는? | **외관 승인** + 아래 §6 | `docs/08` |

## 4. 핵심 치수

| 항목 | 값 |
|---|---|
| 외경 | 138 mm. 바닥 평면 Ø75, 높이 129 mm (귀 포함 약 133 mm) |
| 분할 | 뚜껑은 z +5.25 위(보라), 검정 띠 10.5 mm, 하단 아이보리 |
| 버튼 | 흰 돔형 Ø23.6 (돔 2.6), 5.0 mm 돌출. **짙은 보라 링** Ø34, 링 윗변이 띠 윗변과 맞음 |
| 띠 윗면 | 라벤더 림 링(별도 부품, 1.2 mm 계단에 접착). 검정은 바깥 3.4 mm만 |
| 귀 | 분홍 검드롭 Ø28 × 18 (끝 곡률 0.58 r₀). **A안 확정**: 고도 58°, 방위 ±48°. B안(사진 위치)은 비교 자료로만 보관 |
| 힌지 | 축 y 70 / z 9.25. Ø3×30 SUS 평행핀. 110° 교체형 스토퍼 블록 |
| 화면 | 유리 윗면 중심 (0, −12, 14), 55°. 유리 Ø46, 활성 영역 Ø36.75(실제 비율). 창 Ø44.8로 유리의 검은 테까지 보임. 계단형 베젤 Ø62 + 받침대 슈라우드 + 측면 브래킷 |
| 내부 | 라벤더 내부 커버: 바닥 z −9, 벽, 띠보다 0.6 mm 낮은 립. 최대 Ø122.8이라 벨트 구멍 Ø124로 들어감 |
| 뚜껑 센서 | Littelfuse 59155-1-S-02-A + 57155-000 (12.7×9×3). 닫힘 간극 0.7 mm, 3.9° 열림에서 해제, IO17 |
| 무게 | 약 652 g (와셔 3장 약 234 g 포함, 출력물은 100 % 밀도 상한) |

## 5. 폴더 안내

```
00_READ_FIRST_KO.md            이 문서
appearance/                    외관 승인 게이트 (APPEARANCE_REVIEW_KO.md, review_sheet.png, APPROVAL.json, variant_B/)
docs/01..09_*.md               요구사항·감사·기구·전자·펌웨어·출력·조립·검증·체크리스트
bom/                           ELECTRONICS_CONFIRMED_KO.md, BOM_M7.csv, PURCHASE_PLAN_KO.md
cad/                           생성·검증·외관·렌더 코드;  out/ (A), out_variant_B/ (B 뚜껑·귀)
print/01_fitkit_first/         시험 출력 (지금 가능)
print/02_final_LOCKED_until_appearance_approval/   본 출력 (외관 승인 후)
print/variant_B_ears_photo_position/              귀 B안 뚜껑·귀
electronics/, fitkit/, img/, logs/, tests/
```

## 6. 실물 제작 전 NO-GO

0. **외관 승인**: 귀 위치 A/B와 전체 외관.
1. 실제 SKU 30106 보드를 FK1 크래들에 체결: 스탠드오프, 유리와 립 0.6 mm, 헤더 창, BOOT/RESET.
2. 4432 어댑터 끼움 방향과 공간. 4218 연장 케이블의 **데이터 통과**(COM 포트).
3. FK2 힌지와 스토퍼: 핀 압입, 110° 정지, 200회 개폐.
4. FK3 자석 흡착, 벨트–하단 맞물림.
5. FK4 센서: 실제 액추에이터 끼움, 닫힘 감지, 3–5° 열림 해제.
6. 실물 전도 시험: 110°, 화면 중앙 1.5 N.
7. 납땜 후 단락 검사, 부저, 센서로 화면 켜짐/꺼짐.
8. 24시간 연속 동작, 닫힌 상태 내부 온도(PLA 안전 범위).

## 7. 참고와 권리

- MakerWorld의 개폐형 Pokéball 모델들은 재배포나 수정본 공개가 허용되지 않는 라이선스라 **형상을 가져오지 않았습니다**.
- 포켓몬 이미지, 개인 메시지, 콘셉트 사진은 저장소에 없습니다. 콘셉트 사진 비교는 의뢰인 PC의 비공개 폴더에만 있습니다.
