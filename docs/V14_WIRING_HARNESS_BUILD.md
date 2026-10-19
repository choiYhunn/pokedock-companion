# V14 실물 배선·하네스 설계 — 연결할 선은 2종, 나머지는 제조사 보드 내부

> **전기 작업 정본 / 2026-10-20.** [전원 토폴로지 SVG](../hardware/v14_wiring_topology.svg) · [벤더 인터페이스 근거](V14_ELECTRICAL_INTERFACE.md). 이 문서는 **어떤 포트를 어떤 전원에 연결할지** 검증한 topology/wire-list이다. 보드 16핀 커넥터에서 **몇 번째 자리가 +인지 등 물리적 핀 위치는 실물 리비전 확인 전 미확정**이며 절대 도면 위 추정 순서로 연결하지 않는다.

## 현재 MVP — 연결해야 하는 것 / 필요 없는 것

| ID | 시작 → 종료 | 준비물 / 케이블 | 실제 연결 | 상태 |
| --- | --- | --- | --- | --- |
| W01 | 안전 인증된 AC/DC 어댑터 → Waveshare **4.3C-BOX SKU 33630**의 전원 입력 | 절연형 **regulated 12V 2A 후보**(본체 입력 7~36V) + 현물 단자에 맞는 절연 피그테일/단자 | **단자에 써 있는 +/VIN와 −/GND를 회로도/실물 표기/DMM 3중 대조**하여 연결. 16핀 terminal의 수직 위치 및 나사 번호는 실측/리비전 전까지 공란 | READY FOR INSPECTION; NOT WIRED |
| W02 | 컴퓨터 USB-C DATA → Waveshare USB-C 포트 | 데이터 지원 USB-C 케이블 | 제조사 권장 플래시/로그/BOOT/RST/Recovery. DC 동시 인가가 안전한지 OEM 지침으로 확인 전 **전원 2개 동시 연결 회피** | PROGRAMMING ONLY |
| W03 | 별도 인증된 20W+ USB-C PD → 완제품 MagSafe 충전기 | Apple A3502 1m 또는 실측된 Qi2 완제품, 분리형 캐리어 | 충전기는 USB-C PD에 **직접** 연결, 아이폰 후면에 접촉. HMI 12V/DC/USB와 어떤 전선도 합선·스플라이스하지 않는다 | OPTIONAL, AFTER FIT |
| W04 | RTC 코인셀 홀더 → PCF85063 | 제조사 지정 **CR927 3V** | 실물 인쇄 극성 및 제품 동봉 여부 확인해 삽입, 리드선 없음 | CONDITIONAL |
| W05 | microSD 슬롯 → 보드 SDMMC | 정품 microSD 16–32GB | 슬롯에 삽입. GPIO/SD_CS 단자를 새로 배선하지 않음 | CONDITIONAL |
| W06 | ES8311 앰프/스피커 커넥터 → 호환 스피커 | **실물 동봉 여부, 커넥터 유형 및 임피던스**가 제조사와 일치하는 경우만 | 보드 전용 speaker 커넥터를 이용. GPIO에 스피커 직접 연결 금지 | CONDITIONAL, DEFER |
| W07 | ESP32-C3 / PN532 / NFC / LED / 별도 전원 | 없음 | **현재 MVP에서는 모두 생략**. 향후 특정 모듈/전기 규격 확인 뒤 다른 설계판으로 분리 | NOT WIRED |

## 전기적 계통도 및 연결 근거

```text
AC 220V 콘센트                              AC 220V 콘센트
    │                                           │
[KC/적합 인증 절연 12V/2A 후보]          [USB-C PD 20W+ 완제품 어댑터]
    │  (DC 저전압 단독)                          │ USB-C
    │                                           ▼
    ├── VIN/+ → OEM C-BOX 지정 DC+         [완제품 MagSafe 충전기]
    └── GND/−→ OEM C-BOX 지정 DC−              ║  자기 정렬 / 충전
                     │                        ▼
             [Waveshare SKU 33630]       [iPhone 14 Pro + 케이스]
              │              ▲
              │ USB-C DATA   │ PC/USB 부트 복구 (서비스 시만)
              ▼              │
       LCD + touch + RTC + SD + codec    ← 보드 내장 연결, 새 GPIO선 0개
```

**서로 다른 전원 두 개의 +/−는 합치지 않는다.** 12V 전원을 HMI USB-C, speaker, GPIO, I2C 센서, MagSafe 입력에 연결하면 안 된다. PC USB와 DC 동시 사용도 제조사 권고를 확인하기 전에는 하지 않는다. AC 220V는 인증 어댑터 내부에만 존재하게 하고 본체에 AC·멀티탭·자가 제작 SMPS를 넣지 않는다.

## OEM 전기 신호: '알아야 하지만 직접 연결할 핀은 아님'

| Peripheral | 4.3C family published/example | Work instruction |
| --- | --- | --- |
| I2C: touch, RTC, ES8311, IO expander | GPIO8 SDA, GPIO9 SCL | 공유 버스. 새 모듈을 독자적으로 붙이지 않는다 |
| Touch GT911 | GPIO4 IRQ, IO expander reset | BSP 사용 |
| LCD RGB, backlight | 20+ published GPIO / expander | GPIO 리매핑 금지 |
| SDMMC TF 1bit | GPIO12 CLK, GPIO11 CMD, GPIO13 D0 (벤더 `05_sd` 예제) | 11/12/13을 임의 SPI/MOSI/MISO로 사용하지 않음 |
| Codec ES8311 I2S | MCLK GPIO6, LRCK16, BCLK44, TX15, RX43 | 베이스 BSP 처리. 스피커 단자/임피던스 확인 후 OEM 데모 |
| RTC PCF85063 | I2C+전용 CR927 홀더 | 재부팅 및 backup 5회 확인 |
| USB | GPIO19/20 native USB | PC USB-C 포트, recovery 접근 유지 |
| 16핀 후면 터미널 | OEM published DC 7~36V, IO/isolated outputs | **물리 pin numbering, +/− 배치, 단자 피치 미확정. 잘못된 모델(4.3B/4.3/4) 핀을 복사하지 않음** |

**주의:** 제조사 일반 위키는 IO expander **EXIO4**를 SD_CS와 PA_CTRL 모두로 표기하는 반면, 4.3C V1.1 하드웨어 참조에서는 PA enable을 IO3, SD control을 IO4로 기록한다. 이 충돌은 소스/실물 PCB 확인 전 해결된 GPIO 약속으로 간주하지 않는다. 임의 접근 없이 vendor 예제를 사용한다.

## W01 물리 전원 연결 검증 SOP (최초 통전 전)

1. Waveshare 박스와 납품서에서 **4.3C-BOX 33630** 확인. PWR, DC 입력 7~36V와 표시된 **VIN/+와 GND/−의 실제 글자/커넥터 방향**을 사진으로 남긴다. 드라이버와 맞는 나사 터미널 타입을 기록한다.
2. 공급기기 제조사 라벨에서 입력 AC, 출력 DC, 12V/2A 안정화, 플러스/마이너스 정격, 한국 인증 표시 확인. 노출 220V 연결 금지.
3. 전원선을 어댑터에 연결하지 않은 상태에서 피그테일/페룰 단선·피복·물림·단자 규격을 확인한다. DC barrel을 screw terminal에 억지로 꽂지 않는다. 전원 어댑터는 절연되어야 하고 전원선 끝을 임의로 꼬아 접촉시키지 않는다.
4. **어댑터만 전원에 연결하고 보드는 미연결 상태**에서 DMM DC 모드로 +/− 출력 극성과 전압을 측정한다. 정상 측정 후 어댑터를 콘센트에서 뽑는다.
5. 실물 C-BOX에서 식별한 DC+ ↔ 측정 +, DC− ↔ 측정 −에 확실한 절연 커넥터를 체결한다. 실제 단자 피치와 safe screw contact/strip length는 제품·리비전 명세에 따른다. 보드에 금속 가닥이나 이물질이 남지 않아야 한다.
6. HMI만 단독 통전, 제조사 factory firmware·PWR/열/냄새/리셋 확인, LCD 터치 4코너 ×5, 60분 감시. 불안정/냄새/고열 발생 즉시 전원 분리.
7. 플래싱은 제조사 USB/DC 동시 전원 경로 지침 확인 후 시작. USB-C 포트는 메인 12V 전원 입력이 **절대 아님**.

## 배선/서비스/열 설계

- 후면에 서로 독립된 **HMI 절연 DC 배선**과 **MagSafe 제조사 USB-C 케이블**을 지나가게 한다. 도킹 시 당겨지는 힘이 터미널이나 MagSafe 케이블 몰딩으로 전달되지 않도록 외부 클립으로 strain relief한다.
- 핸드폰 후면 puck는 개방형 holder이며 케이블 휨과 탈착을 방해하면 안 된다. 충전면 위에 3D 프린트 커버, 금속판, 두꺼운 단열판 금지. 폰은 하단 지지 립으로 중력을 받는다.
- BOOT/RST/USB/SD/RTC/스피커 접근을 유지한다. 후면의 여유 공간과 실측 케이블 굽힘이 95mm 목표 깊이를 넘으면 케이스를 늘리기 전에 충전기 제거를 검토한다.
- PC 플래싱/다시 복구할 때 뜯어야 하는 밀봉형 후면 커버는 부적합. 외장 전선 한가운데 자가 제작 AC 배선은 금지.
- 충전형만 60분 실제 아이폰 충전/온도 유지·30회 착탈 후 사용 승인. 본체 일반 타이머/시계는 충전기 없이 작동해야 한다.

## 판단 보류 사항: '완성 도면'으로 속여서는 안 됨

실물 33630의 DC terminal 방향/실제 +/− 핀 번호/커넥터 피치, 프로그래밍 시 USB와 DC 동시 연결 허용 경로, 호환 speaker 임피던스 및 실제 case 안쪽 나사 길이는 OEM 원본 리비전 확인 전 빈칸이다. 따라서 **물리 단자 순서를 적은 배선도는 지금 발행하지 않는다.** 이것이 사고 예방을 위한 명시적인 release gate이다.

Official board hardware: https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3C ; https://www.waveshare.com/product/esp32-s3-touch-lcd-4.3c.htm ; https://github.com/waveshareteam/ESP32-S3-Touch-LCD-4.3C/blob/main/HARDWARE_REFERENCE.md .
