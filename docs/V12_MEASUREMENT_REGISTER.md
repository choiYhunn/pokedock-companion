# PokéDock V12 — measurement & tolerance register / release blocker

No field may be silently filled with a sample placeholder for production. Record caliper measurement +/- tool accuracy, drawing revision and measurement date.

## 1. Waveshare 4.3C-BOX and desk
| ID | Measure physically / from C-BOX drawing | Unit | Current | Must determine before |
| --- | --- | --- | --- | --- |
| H01 | Actual cased HMI outside width | mm | TBD; CAD sample 132 | base width / print |
| H02 | Actual cased HMI outside height | mm | TBD; CAD sample 86 | face height / phone concealment |
| H03 | Case max rear thickness and profile including terminal | mm | TBD; sample 18 | rear bracket depth |
| H04 | Rear mount hole X and Z positions, **claimed 75mm spacing** confirmed on unit | mm | thread/countersink TBD | bracket drilling |
| H05 | Insert thread/diameter, **safe screw engagement depth**, no PCB impingement | mm | TBD | screw purchase |
| H06 | USB, DC terminal, RTC, SD, reset, microphone, speaker/vent positions | mm | TBD | cable/port clearance |
| H07 | Manufacturer PCB/case revision and STEP/DXF revision | text | TBD | any final CAD |
| H08 | Display angle accepted when seated, 70/76/80° | degrees | default 76° | front mount |
| H09 | Usable desk width × rear depth, edge clearance & nearby books | mm | TBD | fit choice |
| H10 | Loaded board/case/stand mass and contact friction | g | TBD | tipping test |

## 2. iPhone/case and charge assembly
| ID | Measure | Unit | Current | Must determine before |
| --- | --- | --- | --- | --- |
| P01 | iPhone **14/14 Pro/14 Plus/14 Pro Max exact** | model | not confirmed | orientation selection |
| P02 | Actual phone+case long dimension | mm | TBD, do not use bare Apple for manufacturing | phone rail |
| P03 | Actual phone+case short dimension | mm | TBD | rail side support |
| P04 | Camera bump/thickest case dimension | mm | TBD | contact plane |
| P05 | Coil center position from a fixed phone edge while case installed | mm | TBD | puck seat |
| P06 | Selected manufacturer's finished puck diameter and thickness | mm | TBD; CAD sample 57/6 | puck ring |
| P07 | Puck USB cable exit direction and **minimum free bend** | mm | TBD | rear route |
| P08 | Phone landscape magnetic grip/sag and left-right visibility at eye level | photo / force test | TBD | A/B selection |
| P09 | Portrait grip and rear depth/visibility at eye level | photo / force test | TBD | A/B selection |
| P10 | 30 dock/undock and 60 min charging thermal/comfort results | log | TBD | final assembly |
| P11 | Case MagSafe compatibility | yes/no | TBD | design feasibility |

## 3. Small parts and enclosure criteria
| Property | First prototype target | Release criterion |
| --- | --- | --- |
| structural plate | PETG or acrylic concept, sample 4–6mm base | chosen by flex/drop/tipping test; no unverified final strength |
| rails/gusset | open nonconductive support | no wobble, visible cracks, phone camera/puck interference |
| fastening | replaceable screws/pads | sized per OEM inserts; zero protruding metal near PCB |
| external radius | concept 8–12mm | comfort/no sharp edges |
| foot pads | removable high-friction silicone | no scratch/slip while operating touch and docking |
| cable routing | both exit behind, separate supplies | no pinches/hot insulation; reset/SD/USB accessible |
| puck retainer | non-invasive, accessible | flush charge face, cooling, replaceable |
| brightness and sound | soft/dim/mute initially | no unwanted late-night light or audio |
| disassembly | remove phone, puck, screen without glue damage | maintenance test pass |

## 4. Confirmation gates
- Case + exact phone + case measurements documented.
- A/B cardboard or adjustable-stand trial with phone at 39° landscape and 32° portrait.
- Build clearance CAD in Fusion/FreeCAD with manufacturer-supplied 2D/STEP, then resolve screw holes and terminal.
- Mockup passes one-hand 30-cycle, stand tipping, MagSafe 60min thermal and live-screen interference tests.
- Only then produce STL/laser-cut template and final print job.
