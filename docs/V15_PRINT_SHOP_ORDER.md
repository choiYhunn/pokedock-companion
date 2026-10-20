# V15 PETG one-piece stand — send-to-printer instructions

**Only print stand**. Source [OpenSCAD](../cad/pokedock_v15_cradle.scad); open the file in OpenSCAD and export **STL with MODE="stand"**:
```bash
openscad -o PokeDock_V15_Stand_RevA.stl -D 'MODE="stand"' cad/pokedock_v15_cradle.scad
```
The downloadable conversation engineering package also contains a prebuilt watertight STL (136×96×72.8mm, 1 body) and a multi-angle design board. The black LCD *must not* be printed; buyer orders actual Waveshare C-BOX model 33630 separately.

## Supplier brief (Korean)
> 안녕하세요. 탁상형 LCD 받침대의 **첫 시제품 1개** 출력 및 배송 포함 견적 부탁드립니다. STL 첨부, 단위 mm, 136×96×72.8mm, 한 덩어리 U자형 PETG 구조입니다. 실제 디스플레이는 완제품으로 따로 구매합니다.
>
> 색상: 웜그레이 또는 아이보리 계열, 무광에 가까운 표면 선호. FDM 표준층 0.20mm, 0.4mm 노즐, 외벽 4줄, 상하 5층 이상, gyroid 25–30% infill 우선 검토(출력업체가 강도/설정 최종 판단). 반드시 넓고 평평한 바닥 Z=0을 베드에 놓고 출력. U자 중앙 개방, 두 뒤쪽 경사 지지대, 앞쪽 작은 걸림턱 보존. 모델을 임의로 스케일하거나 장식 후가공으로 접촉 치수를 바꾸지 말아주세요.
>
> 베드 제거/기본 서포트 제거/손 닿는 버 제거 포함, 완성 사진과 제품 최대 외형, 부가세·택배비 포함 최종금액 및 납기 알려주세요. **실물 LCD 케이스에 끼워본 적 없는 Rev A 시제품**이므로 케이스 결합 보증은 요구하지 않고, 출력 불가능한 얇은 구조나 휨 우려를 사전에 알려주세요.

**Candidate:** [3DFARM upload](https://3dfarm.co.kr/3d-printing-service/) (STL/PETG/quantity 1). [Public quote methodology](https://3dfarm.co.kr/3d-printing-price/) lists basic charge ₩5k + material/machine/finishing + delivery, sample ~100cm³ PLA print ₩34k, not the PETG quote for this actual STL. **Do not claim shop checkout has been completed.**

## Fit/retention
- Soft rear contact felt/TPU 0.8–1.0mm on two ribs; lower case edge two support pads; four sticky rubber feet 10–12mm diameter.
- Test stable touch with screen held from front. If it can tip forward, do not gift it; apply compatible removable attachment strips to **rear plastic housing, never glass, terminal, or PCB** or revise print.
- Hardware 33630 published case W116.3×H79×T18, 163g; unpublished case radius, cable bend and print tolerances mean no unconditional guarantee.
