# 소리 팩 (DFR0534) 만들기와 넣기

## 공개 시험음과 비공개 선물음

| 구분 | 어디에 | 내용 |
|---|---|---|
| **TEST 팩** (공개) | `audio/make_test_pack.py`가 만듭니다(저장소에는 생성 코드만 있고 소리 파일은 없음) | 합성한 비프음 16개. 울음소리 트랙(9–16)도 단순한 짹짹 소리 |
| **선물 팩** (비공개) | `Documents\프로젝트\PokeDock_Private_Assets\audio\` | 의뢰인이 직접 준비한 파일. **저장소에 넣지 않고, 자동으로 내려받지도 않습니다** |

`audio/test_audio_tools.py`가 저장소 안에 소리 파일이 없음을 매번 검사합니다.

## 트랙 표 (`audio/sound_manifest.json` = 펌웨어 `core/audio_director.hpp`)

| 트랙 | 이벤트 | 최대 길이 |
|---|---|---|
| 1 | 켜짐 | 2.5 s |
| 2 | 뚜껑 열림 | 1.5 s |
| 3 | 뚜껑 닫힘 (BLE `audio {"close":false}`로 끌 수 있음) | 1.5 s |
| 4 | 화면 탭 | 0.6 s |
| 5 | 저장·확인 | 1.0 s |
| 6 | 페어링 | 1.5 s |
| 7 | 집중 타이머 완료 | 4.0 s |
| 8 | 알람 (끌 때까지 반복) | 3.0 s |
| 9–16 | 파트너 울음소리: 팬텀(94), 팽도리(393), 토게키스(468), 루카리오(448), 누오(195), 토게피(175), 파치리스(417), 지라치(385) | 3.0 s |

- 펌웨어는 각 소리를 최대 길이에서 멈춥니다. 그래서 파일은 최대 길이보다 0.1초 이상 짧아야 합니다.
- **우선순위**: 알람 > 타이머 완료 > 울음소리·페어링·닫힘 > 켜짐·열림·확인 > 탭. 낮은 소리는 높은 소리를 끊지 못합니다.

## 1. 선물 팩 만들기 (PC)

1. `PokeDock_Private_Assets\audio\src\`에 파일을 둡니다. 이름 규칙:
   - `boot`, `lid_open`, `lid_close`, `tap`, `confirm`, `pair`, `timer_done`, `alarm`
   - `cry_94`, `cry_393`, … (도감 번호)
   - 확장자는 `.mp3` 또는 `.wav`입니다.
   - 없는 항목은 TEST 소리로 채워집니다.
2. 명령:

```powershell
cd "$env:USERPROFILE\Documents\프로젝트\pokedock-companion-m6\v16\masterball-m7"
python audio\make_test_pack.py build\audio_test_pack
python audio\make_gift_pack.py "$env:USERPROFILE\Documents\프로젝트\PokeDock_Private_Assets\audio\src" "$env:USERPROFILE\Documents\프로젝트\PokeDock_Private_Assets\audio\out" build\audio_test_pack
```

## 2. 모듈에 넣기 (모듈만 PC에, 보드와는 분리)

1. DFR0534의 micro-USB를 PC에 꽂습니다. 약 8 MB짜리 드라이브가 나타납니다(예: `E:`).
2. 명령:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\audio\copy_sounds_windows.ps1 -Drive E: -Pack "$env:USERPROFILE\Documents\프로젝트\PokeDock_Private_Assets\audio\out" -ClearDrive
```

- 16 MB보다 큰 드라이브나 이동식이 아닌 드라이브는 거부합니다. 일반 USB 메모리는 건드리지 않습니다.
- 기존 파일이 있으면 목록을 보여 주고, `yes`를 입력해야 지웁니다.
- 파일을 01–16 순서로 하나씩 복사한 뒤, 드라이브의 디렉터리 순서가 그와 같은지 다시 확인합니다.

3. 드라이브를 꺼내고 micro-USB를 뺍니다.

**실물 미검증**:
- "트랙 번호 = 복사 순서"는 제조사 프로토콜 설명(지정 번호 재생)에 근거합니다.
- 실제 모듈에서 트랙 1–16을 재생해 확인해야 합니다: BLE `audio_test` 0–8, 그리고 파트너를 바꿔 가며 9–16.
