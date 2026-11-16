# 10. 휴대폰 BLE 실기 시험 (Android V18 앱 ↔ PokeDock-MB)과 iPhone 평가

> 상태 (2026-11-16 자정, 펌웨어 **m7-0.6.6-gift**):
> - **Android 실기**: 의뢰인 폰(V18 1.8.0)으로 페어링, 연결·해제·재연결, 밝기, 파트너가 동작했습니다. 나머지 B항목은 아래 표대로 아직입니다.
> - **해결한 결함 2개**
>   1. 폰 연결 뒤 화면 멈춤: 펌웨어 0.6.5에서 해결(`docs/05` §1).
>   2. 볼 재시작 뒤 앱 슬라이더·값이 안 바뀜: 앱이 예전 상태 번호를 기억해서 새 상태를 버렸습니다. 앱 1.8.2에서 해결했습니다(재현 시험 포함). **1.8.2 설치 전에는 앱을 완전히 껐다 켜면 됩니다.**
> - **PC 자동 반복 시험**: PC를 볼과 본딩한 뒤 `tools/ble_soak_pc.py`로 연결 → 명령 8개 → 상태 확인 → 해제를 반복했습니다. 결과는 `logs/HW_BRINGUP_20261116_KO.md` §3에 있습니다. 이 시험은 프로토콜 수준이며, 폰 앱 화면을 시험한 것은 아닙니다.

## 1. 앱 코드 점검 결과 (main `4c3896c`, `mobile-v18/`)

| 층 | 파일 | 상태 |
|---|---|---|
| 프로토콜 v2 코덱 | `ble/pokedock_ble_protocol.mjs` | 펌웨어 `core/protocol.hpp`와 같은 UUID·명령·범위 |
| 클라이언트 (ACK 대기, 같은 seq 재시도, 재연결, 연결 시 시계 자동 동기화) | `ble/pokedock_ble_client.mjs` | 연결됨 |
| 전송 계층 | `ble/transports.js` | `CapacitorBleTransport`(@capacitor-community/bluetooth-le 7.3.2): requestDevice → connect → **createBond** → MTU → notify<br>`WebBluetoothTransport`(Android Chrome)도 있음 |
| 화면 연결 | `ble/m6.js`, `app.js` | 설정 → "마스터볼 M6 연결" 시트에 다음 버튼이 실제 명령으로 이어집니다:<br>찾기·연결 / 연결 해제 / 상태 새로고침 / 밝기 / 파트너 보내기 / 시간 동기화 / 다음 알람 보내기 / 소리 켜기·끄기 / 반응 / 볼 알람 끄기<br>앱 타이머의 시작·일시정지·재개·초기화는 볼 집중 타이머와 동기화되고, 파트너를 바꾸면 자동으로 전송됩니다 |
| 호스트 시험 | `tests/ble_bridge_app_test.mjs` | **9/9 PASS**: 실제 M7 0.6.1 C++ 엔진, 모의 링크 (펌웨어 버전 고정값만 m6/m7 공통으로 고침) |
| 단위 시험 | `tests/v18_unit.test.mjs` | 32/32 PASS |

**결론**: 통신 기능은 이미 연결되어 있어 새로 구현할 것이 없었습니다.
- 앱에 없는 것은 M7 전용 명령 `audio`(볼륨)·`audio_test`·`lid_sensor`입니다. 볼 화면에서 할 수 있어(밝기 길게 = 소리 크기) 이번 범위에서 뺐습니다.
- 위 판정은 코드와 호스트 시험 기준입니다. **무선 실기는 아래 3절에서 판정합니다.**

## 2. APK

| 항목 | 값 |
|---|---|
| 파일 | `Documents\프로젝트\PokeDock_모바일앱_기록\PokeDock_Mobile_V18_Native_20261025\app_android\PokeDock_V18_1.8.2_debug_20261116.apk` |
| 버전 | **1.8.2** (versionCode 5), 패키지 `com.pokedock.littlemoments`. 1.8.1 + 재연결 시 상태 번호 초기화 수정 |
| 서명 | 디버그 키 SHA-256 `ede9a013…27fc`. V17.1·V18 1.8.0과 같아 **덮어 설치하면 앱 데이터가 유지**됩니다 |
| SHA-256 | `9e7b4dcc…8855` |
| 권한 | BLUETOOTH_SCAN(neverForLocation), BLUETOOTH_CONNECT, 위치는 Android 11 이하만, 알림 |
| 비공개 | 공식 아트 스프라이트가 들어 있는 **개인용 빌드**입니다. 공개 저장소나 공유 링크에 올리지 않습니다 |

**설치 (둘 중 하나)**
- **USB 파일 복사**:
  1. 휴대폰을 PC에 연결하고 "파일 전송"을 고릅니다.
  2. APK를 휴대폰의 `Download`에 복사합니다.
  3. 휴대폰 파일 앱에서 APK를 누릅니다.
  4. "이 출처 허용"을 켜고 설치합니다.
- **adb**: 휴대폰에서 개발자 옵션 → USB 디버깅을 켭니다. 그다음 PC에서 아래 명령을 실행합니다.

```powershell
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" install -r "$env:USERPROFILE\Documents\프로젝트\PokeDock_모바일앱_기록\PokeDock_Mobile_V18_Native_20261025\app_android\PokeDock_V18_1.8.2_debug_20261116.apk"
```

## 3. 실기 시험 순서 (보드는 PC USB에 연결해 두면 시리얼 로그로 함께 확인)

| # | 할 일 | 합격 | 결과 |
|---|---|---|---|
| B1 | 앱 → 설정 → **마스터볼 M6 연결 →** → "마스터볼 찾기". 근처 기기 권한 허용 | 목록에 `PokeDock-MB` | PASS (의뢰인 보고) |
| B2 | 볼 메뉴(아래로 끌기) → **페어링** (2분 창. 저장된 짝이 없으면 부팅 후 10분 자동) → 앱에서 PokeDock-MB 선택 | 볼 화면에 6자리 번호, 휴대폰에 입력창 | PASS (의뢰인 보고) |
| B3 | 6자리 입력 | 앱 "연결됨", 상태 칸에 파트너·밝기·펌웨어 **m7-0.6.6-gift** | PASS (의뢰인 보고) |
| B4 | 연결 직후 볼 시계 | 볼의 "시간 맞춰줘"가 사라지고 휴대폰 시각과 같음 (연결 시 자동 time_sync) | 부분: 0.6.3 로그에 폰의 time_sync 수신. 볼 시각 육안 확인은 기록 없음 → **NOT TESTED** |
| B5 | "시간 동기화" 버튼 | "시간 동기화 완료" | |
| B6 | 앱에서 파트너를 팽도리로 바꾸고 "보내기" | 볼 화면 파트너가 바뀜 | PASS (의뢰인 보고, 0.6.3 로그에 partner 명령 수신·적용) |
| B7 | 밝기 슬라이더 30 → 100 | 볼 밝기가 바뀜 | **PASS (0.6.6, 의뢰인)**. 이전 FAIL은 화면 멈춤(0.6.5에서 해결)과 밤 15 % 제한(0.6.6에서 제거) 때문 |
| B8 | 앱 홈 타이머 시작 → 일시정지 → 재개 → 초기화 | 볼 집중 화면이 같이 바뀜 | |
| B9 | 앱 알람을 2분 뒤로 추가 → "다음 알람 보내기" | 볼 메뉴 알람이 같은 시각, 2분 뒤 볼에서 울림 | |
| B10 | "연결 해제" → "마스터볼 찾기" | 번호를 다시 묻지 않고 재연결 (본딩 유지) | PASS (23:18:52 해제 → 23:18:53 재연결, 암호화 status=0, 번호 입력 없음) |
| B11 | 볼 USB를 뺐다 다시 꽂기 | 앱 "연결 끊김" → "다시 연결"로 복구, 볼 시계가 다시 동기화됨 | |

- 시리얼 로그(보드가 PC에 연결돼 있을 때): `pd_ble: MTU …`, `pairing refused`(창이 닫혀 있을 때)를 확인합니다.
- 실패하면 앱 시트의 "최근 통신 기록"을 캡처합니다.

## 4. iPhone 평가 (Android 결과와 별개)

| 방법 | BLE 제어 | 근거 / 조건 | 상태 |
|---|---|---|---|
| **오프라인 웹앱 (Safari·홈 화면 PWA)** | **불가** | iPhone의 모든 브라우저는 WebKit 엔진을 써야 하고, WebKit은 Web Bluetooth를 지원하지 않습니다.<br>앱의 `detectSupport()`도 iPhone에서 "Web Bluetooth를 지원하지 않아요"라고 표시하도록 되어 있습니다(코드 확인). | 실기 미확인 |
| 네이티브 iOS 앱 (같은 Capacitor 프로젝트, `@capacitor/ios` + bluetooth-le iOS) | 가능할 것으로 예상 | 전송 계층 코드는 같습니다. iOS는 createBond가 없어 첫 암호화 접근 때 시스템 페어링 창이 뜹니다.<br>필요한 것: Mac + Xcode, Info.plist `NSBluetoothAlwaysUsageDescription`, Apple ID 서명(무료는 7일마다 재설치, 유료 개발자 계정은 TestFlight) | 빌드 안 함 |
| Web Bluetooth를 넣은 타사 iOS 브라우저 | 불확실 | 앱스토어의 일부 브라우저가 자체 BLE 다리를 제공한다고 알려져 있습니다. 동작·지속성·개인정보를 확인하지 않았습니다 | 평가 안 함 |
| **휴대폰 없이 볼만 사용** | 해당 없음 | 시계 설정·알람·타이머·파트너·밝기를 볼 화면에서 모두 할 수 있습니다 | **실기 PASS (11-16)** |

**결론**
- iPhone 오프라인 웹앱으로는 마스터볼을 BLE로 제어할 수 없습니다.
- iPhone 사용자는 볼을 단독으로 쓰고, 정전 뒤 시계는 볼에서 직접 맞춥니다.
- iPhone에서 BLE가 꼭 필요하면 Mac에서 네이티브 iOS 앱을 빌드해야 합니다(별도 작업, 미시험).
- **Android에서 성공해도 iPhone 성공으로 기록하지 않습니다.**
