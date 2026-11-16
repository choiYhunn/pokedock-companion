# M7 v0.6 핀맵 (자동 생성: electronics/m7_wiring_v06.py ← harness_m7.json)

공식 회로도 대조는 `tests/m7_electrical_check.py`가 합니다. 이 표를 손으로 고치지 말고 JSON을 고친 뒤 다시 생성합니다.

## 보드 커넥터

| 커넥터 | 핀 | 신호 | M7 사용 |
|---|---|---|---|
| J10 | 1 | RXD = GPIO44 (UART0 RX pad, used as UART1 TX by M7) | 예 |
| J10 | 2 | TXD = GPIO43 (ROM boot log: NOT wired) | 아니오 (비움) |
| J10 | 3 | 3V3 (MP1605 buck, 2 A) | 예 |
| J10 | 4 | GND | 예 |
| J1 | 6 | GND | 예 |
| J1 | 10 | IO17 | 예 |
| J1 | 1 | U_P (USB D+) | 아니오 |
| J1 | 3 | U_N (USB D-) | 아니오 |
| J1 | 4 | USB_5V | 아니오 |
| J1 | 8 | IO16 (v0.5 buzzer) | 아니오 |

## 하네스

### H1 sound cable J10 -> DFR0534
- 제작: commercial cables only: no solder, no crimp tool
- 부품: Adafruit 4397 (JST SH 4-pin plug -> 4 premium female sockets, 150 mm, 28 AWG (STEMMA QT / Qwiic cable)); Adafruit 3955 (JST PH 4-pin plug -> 4 premium male pins, 200 mm, 26 AWG (STEMMA cable))
- 연결: j10_pin=1, net=GPIO44, module_pin=R, how=4397 socket of J10-1 onto the 3955 pin that rings out to the module RX pad
- 연결: j10_pin=3, net=3V3, module_pin=+, how=4397 socket of J10-3 onto the 3955 pin that rings out to the module VCC pad
- 연결: j10_pin=4, net=GND, module_pin=-, how=4397 socket of J10-4 onto the 3955 pin that rings out to the module GND pad
- 연결: j10_pin=2, net=GPIO43, module_pin=None, how=4397 socket of J10-2 stays empty: cover it with tape
- 연결: j10_pin=None, net=module T, module_pin=T, how=3955 pin of the module T stays unused: cover it with tape
- identify: Never trust wire colours: the Qwiic colour code (black GND, red 3V3, blue SDA, yellow SCL) does not describe the Waveshare J10 order. J10 side: board powered, GND = socket with continuity to the USB-C shell, 3V3 = 3.25-3.35 V, GPIO44 = the socket that drops to 0 V during the firmware wiring test (long press within 10 s of power-up). Module side: module unplugged from everything, continuity from each 3955 pin to the labelled VCC / GND / RX / TX pads.
- strain_relief: the 3 joined pin pairs side by side under 30 mm of 3:1 heat-shrink (or two wraps of electrical tape), tied to an adhesive cable-tie mount on the lower shell floor; the Gravity plug latches in the module
- reverse_risk: JST SH and PH plugs are keyed; the only mistake possible is in the pin-to-socket join, which the multimeter steps rule out before the module is powered
- length_mm: 350

### H2 lid sensor lead -> J1
- 제작: helper / school: 2 solder joints (the 59155 has tinned leads only; no connector option exists)
- 부품: Littelfuse 59155-1-S-02-A (reed sensor, NO, 300 mm 26 AWG PVC UL1569 leads, tinned 6.4 mm); Harwin M50-3000745 (1.27 mm 2x7 through-hole female socket, gold)
- 연결: socket_pin=10, net=IO17, from=either reed lead (not polarised)
- 연결: socket_pin=6, net=GND, from=the other reed lead
- strain_relief: 1.5 mm heat-shrink over each soldered tail, a small bead of hot glue on the socket back only (not between pins); pin-1 corner marked with a white dot
- reverse_risk: socket keyed only by the pin-1 dot: plugged 180 deg the reed lands on J1-5 (IO6) and J1-9 (IO3) = no lid events, no damage (no power pins in use)
- length_mm: 300

### H3 speaker leads -> DFR0534
- 제작: helper / school: 2 solder joints on the module pads
- 부품: PUI Audio AS02808MR-LW152-R (28 mm 8 ohm 1 W (1.5 W max) speaker, 152 mm leads)
- 연결: pad=SP+, from=speaker + lead (red / marked +)
- 연결: pad=SP-, from=speaker - lead
- strain_relief: leads looped once and held by the sound bracket lead slot
- length_mm: 152

### P1 USB-C power and data
- 제작: commercial, plug-in
- 부품: Adafruit 4432; Adafruit 4218

## 보호

v0.5 needed the PTC because the buzzer tapped USB_5V directly (J1-4, no current limit but the adapter). v0.6 takes no power from J1-4 at all: the sound module hangs on the board 3V3 rail, which the MP1605 buck already limits, so no extra fuse is needed. A short in H1 drops the 3V3 rail and resets the ESP32 until it is removed (HARDWARE UNVERIFIED: not tested on a real board).

## 배선 경로

H1: J10 plug beside the USB-C plug at the bottom edge of the board, out through the widened bezel cup opening, down the left deck cable hole (x -16), across the lower shell to the sound bracket (left side). H2: reed in the belt pocket (az -90), leads down outside the inner cover wall, under the floor to the right deck cable hole (x +16), up to J1 behind the cradle plate. H3: inside the sound bracket. Nothing crosses the lid sweep.
