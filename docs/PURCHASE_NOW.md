# 구매 리스트 — 그대로 사면 되는 V1

## A. 핵심
### 1) Waveshare ESP32-S3-Touch-LCD-4.3C-BOX
- **정확한 모델:** ESP32-S3-Touch-LCD-4.3C-BOX
- **SKU:** 33630
- **주의:** 4.3B, 4.3, case 없는 33799를 잘못 사지 말 것.
- 이유: 800×480 터치 + RTC + microSD + audio + case + 75mm rear mount를 한 번에 해결.

### 2) ESP32-C3 SuperMini — 헤더 납땜 버전 권장
- 국내에서 헤더 납땜 버전이 있으면 그걸 선택.
- 하루 제작 목표라 직접 핀헤더 납땜 시간을 아끼는 것이 좋음.

## B. 센서
### 3) PN532 NFC module
- SPI / I2C / UART 전환 가능한 보드.
- V1에서는 **Dock Node의 I2C**에 연결.
- NFC tag 6–10장도 같이 구매.

### 4) VL53L0X ToF
- 폰이 놓였는지 감지.
- 단순 IR reflective sensor보다 케이스/색상 영향이 적고 threshold tuning이 쉬움.

### 5) BH1750
- 방 밝기 측정.
- Night mode / brightness 자동화.

### 6) WS2812B or SK6812 LED ring/short strip
- 8~12 LED면 충분.
- 화면 뒤/베이스 underside glow용.
- 너무 많은 LED는 전류와 발열만 늘림.

## C. 충전
### 7) Samsung EP-P2400 또는 동급의 완제품 Qi pad
- 기준 치수: **91 × 91 × 18.3 mm**
- Qi certified
- Galaxy 호환 시 최대 15W, 타 제조사는 기기별 출력 제한 가능.
- 장점: RF/발열/보호회로를 직접 설계하지 않아도 됨.
- **충전기를 분해하지 않고 cradle에 끼우는 방식**이 가장 안전.

## D. 저장/전원
- microSD 16–32GB
- CR927 RTC cell
- USB-C data cable ×2
- HMI 전용 권장 어댑터/전원
- C3 + LED용 5V USB supply
- Qi pad용 제조사 권장 PD/AFC adapter

## E. 조립 소모품
- 330Ω resistor ×2
- 1000µF electrolytic capacitor ×1
- Dupont/JST wires
- perfboard small ×1
- heat-shrink
- VHB tape
- rubber feet
- braided sleeve
- M4 bolts/nuts for 75×75 mount (only if using that mount path)
- M3 assortment
- optional white/cream PETG or PLA+

## 예상 지출 감각
- HMI: 대략 5~9만원대(해외/국내 수입 차이 큼)
- Dock MCU + sensors + LED: 대략 4~7만원
- Qi charger: 2~5만원
- 출력/소모품: 1~3만원
- **총 목표: 12~20만원 정도**
  - 이미 가진 microSD/전원/공구가 있으면 더 낮아짐.

## 절대 구매하지 말 것
- generic bare Qi transmitter coil + unknown driver board
- Arduino UNO
- separate TFT
- DFPlayer
- separate RTC
- 50+ LED strip
- random LiPo pouch for first build