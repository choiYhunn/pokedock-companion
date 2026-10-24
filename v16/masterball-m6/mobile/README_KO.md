# V17 앱 ↔ 마스터볼 BLE 연동 (M6)

## 구성

| 파일 | 역할 | 검증 |
|---|---|---|
| `pokedock_ble_protocol.mjs` | 명령 인코딩, 입력 검증, ACK·상태 디코딩 (기기 `core/protocol.hpp`와 같은 규격) | `tests/ble_e2e_bridge_test.mjs` |
| `pokedock_ble_client.mjs` | 세션 ID, seq, ACK 대기(2초), 재시도 3회(같은 seq), 재연결 백오프, 상태 재동기화 | 위 E2E 12/12 PASS (시뮬레이션 링크) |
| `capacitor_transport.mjs` | Android/iOS 네이티브 BLE (`@capacitor-community/bluetooth-le`) | **실기기 미검증** |

## 기기가 기준(source of truth)

- 타이머·알람·설정은 기기가 독립적으로 실행합니다. 앱이 없어도, 인터넷이 없어도 동작합니다.
- 앱은 연결될 때마다 상태를 다시 읽고, 시계를 동기화합니다(`syncClock()`).
- 앱이 백그라운드에 있을 때 연결을 계속 유지한다고 가정하지 않습니다.

## 보안

- 명령 쓰기(write)와 상태 읽기(read)는 **암호화 + 인증된 본딩 링크**에서만 허용됩니다(NimBLE GATT 플래그와 엔진에서 이중 확인).
- 페어링 절차:
  1. 볼에서 메뉴 → "페어링"을 누르면 2분간 페어링 창이 열립니다. 본딩된 폰이 없는 첫 설정 때는 부팅 후 10분간 자동으로 열립니다.
  2. 볼 화면에 6자리 번호가 표시되면 폰에 그 번호를 입력합니다(LE Secure Connections, MITM).
- 페어링 창이 닫혀 있으면 새 페어링 요청은 연결이 끊어집니다.

## V17 Android 프로젝트에 넣는 법 (로컬 작업본, 아직 적용 안 함)

1. 패키지를 설치하고 네이티브 프로젝트에 동기화합니다.
   ```
   npm i @capacitor-community/bluetooth-le@^7
   npx cap sync android
   ```
2. `android/app/src/main/AndroidManifest.xml`에 아래 권한을 추가합니다.
   ```xml
   <uses-permission android:name="android.permission.BLUETOOTH_SCAN" android:usesPermissionFlags="neverForLocation" />
   <uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />
   <uses-permission android:name="android.permission.BLUETOOTH" android:maxSdkVersion="30" />
   <uses-permission android:name="android.permission.BLUETOOTH_ADMIN" android:maxSdkVersion="30" />
   ```
3. iOS는 `Info.plist`에 `NSBluetoothAlwaysUsageDescription`을 추가합니다.
4. 앱 코드에서 다음과 같이 연결합니다.
   ```js
   new PokeDockClient(new CapacitorTransport())
   ```
   기존 V17 화면의 파트너, 타이머, 알람, 밝기, 소리, 메시지 동작에 `client.setPartner()` 등을 연결합니다.

## 미완료 (사실대로)

- V17 화면 코드와 아직 연결하지 않았습니다(기존 오프라인 UI 보존).
- 이 PC에는 Android SDK가 없어 APK를 다시 빌드하지 못했습니다.
- iOS 빌드도 하지 않았습니다.
- 실제 무선(BLE radio) 연결, 본딩, MTU 협상, 끊김 복구는 보드와 실제 휴대폰으로 검증해야 합니다(게이트 G3).
