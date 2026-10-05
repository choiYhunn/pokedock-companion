# 제작일 이전에 끝내야 하는 것

하루 완성이 목표면 **이 문서의 항목은 제작일에 하면 안 된다.**

## 1. 주문
- HMI 정확한 SKU 33630
- Dock MCU + 3 sensors + LED
- Qi pad
- microSD + RTC cell
- base 3D print or laser-cut (optional; commercial stand is acceptable)

## 2. PC 준비
- VS Code
- Espressif ESP-IDF extension
- ESP-IDF 5.5 권장
- Arduino IDE optional (Dock Node 빠른 bring-up용)
- USB driver 확인
- `idf.py --version` 확인

## 3. Asset 준비
`assets/fetch_pokeapi_assets.py`를 실행해 개인 프로젝트용 로컬 이미지를 내려받는다.
최종 microSD:
```
/pokemon/full/
/pokemon/thumb/
/audio/
/config/pokemon.json
```

## 4. UI 문구 결정
여자친구 이름/생일은 config 파일에만 넣는다.
코드에 박아 넣지 않는다.

## 5. NFC 카드 매핑
최소 6장:
- Gengar
- Togepi
- Togekiss
- Pachirisu
- Lucario
- Jirachi

카드/스티커 겉 디자인은 나중에 바꿔도 UID mapping은 유지.

## 6. 외형 선택
둘 중 하나만 고른다.
- 빠른 경로: 기성 태블릿/디스플레이 스탠드 + Qi pad + 아크릴/폼보드 마감
- 커스텀 경로: `cad/pokedock_v2_base.scad` 수정 후 3D 출력

## 7. 공장 펌웨어 백업
HMI 수령 즉시 factory firmware가 정상인지 먼저 확인하고,
공식 recovery binary 위치를 따로 저장한다.