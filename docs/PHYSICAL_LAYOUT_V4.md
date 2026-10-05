# Physical Layout V4

## Front
The screen is the product. There is no tray extending toward the user.

```text
front view

┌──────────────────────────────┐
│        4.3" HMI screen       │
│                              │
└──────────────────────────────┘
┌──────────────────────────────┐──┐
│ slim base / ambient underglow│  │ side NFC pod
└──────────────────────────────┘──┘
```

## Side

```text
side view

     PHONE
       ╱
      ╱  <- simple rear slope + removable Qi puck
 ┌───╱──────────┐
 │ HMI display  │
 └──────────────┘
 ────────────────  <- shallow base
```

No deep slot is required. The rear slope only needs:
- a bottom stop of a few millimeters,
- non-slip surface,
- correct Qi coil alignment,
- enough clearance for the phone camera bump/case.

## Top

```text
top view

               rear
      ┌─────────────────┐
      │  parked phone   │
      ├─────────────────┤
      │   HMI display   │
      └─────────────────┘───┐
      │      base       │NFC│
      └─────────────────┴───┘
               front
```

The NFC pod never extends farther toward the user than the base front edge.

## Manufacturing fallback
The exact same geometry can be prototyped without 3D printing:
- commercial angled display stand,
- thin acrylic/polycarbonate rear phone support,
- adhesive Qi pad/puck,
- small acrylic side NFC plate.

Firmware is independent of enclosure method.
