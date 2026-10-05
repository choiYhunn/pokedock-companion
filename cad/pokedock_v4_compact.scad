// PokéDock V4 compact concept
// No front tray. Rear sloped phone support. Side NFC pod.
// Dimensions are design targets; verify against physical HMI/phone/Qi puck before printing.
$fn=64;

BASE_W = 126;
BASE_D = 78;
BASE_H = 8;
CORNER = 8;

SCREEN_W = 118;
SCREEN_PLATE_T = 5;
SCREEN_TILT = 12;

PHONE_SUPPORT_W = 82;
PHONE_SUPPORT_H = 82;
PHONE_SUPPORT_T = 4;
PHONE_ANGLE = 70;  // from horizontal

NFC_SIDE = "right"; // "left" or "right"
NFC_POD_W = 40;
NFC_POD_D = 54;
NFC_POD_H = 8;
NFC_RECESS_D = 30;

module rbox(w,d,h,r=5){
  hull() for(x=[r,w-r]) for(y=[r,d-r]) translate([x,y,0]) cylinder(h=h,r=r);
}

module main_base(){
  rbox(BASE_W, BASE_D, BASE_H, CORNER);
}

module nfc_pod(){
  x = (NFC_SIDE=="right") ? BASE_W-2 : -NFC_POD_W+2;
  translate([x, 12, 0])
    difference(){
      rbox(NFC_POD_W, NFC_POD_D, NFC_POD_H, 7);
      translate([NFC_POD_W/2, NFC_POD_D/2, NFC_POD_H-1.1])
        cylinder(h=2,d=NFC_RECESS_D);
    }
}

module screen_support(){
  translate([(BASE_W-SCREEN_W)/2, BASE_D-18, BASE_H])
    rotate([SCREEN_TILT,0,0])
      cube([SCREEN_W, SCREEN_PLATE_T, 72]);
}

module rear_phone_slope(){
  // A simple ramp, not a deep slot.
  translate([(BASE_W-PHONE_SUPPORT_W)/2, BASE_D-13, BASE_H+7])
    rotate([90-PHONE_ANGLE,0,0])
      cube([PHONE_SUPPORT_W, PHONE_SUPPORT_T, PHONE_SUPPORT_H]);

  // Minimal bottom stop only.
  translate([(BASE_W-PHONE_SUPPORT_W)/2, BASE_D-20, BASE_H+5])
    cube([PHONE_SUPPORT_W, 6, 6]);
}

union(){
  main_base();
  nfc_pod();
  screen_support();
  rear_phone_slope();
}

// Keep Qi puck removable on the rear support.
// Do not permanently encapsulate charging electronics.
