// V14 MAGSAFE READY — 14 Pro + MagSafe case confirmed, landscape 70°.
// WARNING: SAMPLE fit, no structural validation, NOT a final manufacturing drawing.
// Charger is a removable finished factory puck with independent USB-C PD adapter.
// V14: compact iPhone 14 Pro landscape slot; optional detachable MagSafe puck.
// DO NOT PRINT / FLASH / PURCHASE FROM SAMPLE CLEARANCES.
// Confirm manufacturer cased dimensions 116.3 x 79 x 18 mm (SKU 33630).
// PokéDock V14 | Quiet Desk / reversible concept assembly
// OPENSCAD ENGINEERING MOCK - NOT A FINAL PRINT-READY ENCLOSURE.
// mm throughout. Physical OEM screen and iPhone+case measurements required.
// MagSafe-capable case CONFIRMED. Existing case and puck still need measurement.
// Choose PART: "assembly", "base", "screen_frame", "phone_support", "template_2d"
// Poses: "landscape" (space-first default) or "portrait" (concealment-first).
// No front projecting phone tray, no internal Qi RF construction.
// 75 mm "pitch" does NOT prove four 75x75 mounting holes or thread/depth.\n// All dimensions remain conceptual until actual cased 33630 is measured.
$fn = 48;
PART = "assembly";
POSE = "landscape";          // V14 release candidate = LANDSCAPE; portrait is archived V12 study
DISPLAY_MODEL = "sample";    // sample; replace dimensions from OEM 4.3C-BOX
SHOW_SCREEN = true;
SHOW_PHONE = true;
SHOW_PUCK = false;   // Off until physical puck measurement; VISUAL disk ONLY, never a retainer.
SHOW_CABLES = false;
SHOW_MOUNT_MARKERS = false; // NEVER use unverified 75x75 visual markers as drilled holes
PRINT_SPLIT_GAP = 17;

// --------- MEASUREMENT VARIABLES: NOT FINAL MANUFACTURING DIMENSIONS ---------
SCREEN_W = 116.30;              // replace with caliper C-BOX outside width
SCREEN_H = 79.00;               // replace with measured case height
SCREEN_T = 18;               // replace with measured thickest case depth
SCREEN_ANGLE = 76;           // deg above desktop, A/B-test 70/76/80
SCREEN_Y0 = 15;              // front screen bottom, measured rear datum
SCREEN_Z0 = 12;              // raises screen to clear base
OEM_REAR_MOUNT_PITCH = 75;   // manufacturer states rear mounting pitch 75 mm
SCREW_HOLE_D = 0;            // KEEP 0 until exact OEM hole count/XY/thread/depth confirmed
// CONFIRMED iPhone 14 Pro BODY 147.5x71.5x7.85mm; MagSafe case model/dimensions TBD
PHONE_LENGTH = 147.5;
PHONE_WIDTH = 71.5;
CASE_ALLOWANCE_LENGTH = 6;
CASE_ALLOWANCE_WIDTH = 6;
PHONE_CASE_THICKNESS = 12;    // largest camera bump/case thickness; MEASURE
MAGSAFE_DIAMETER = 57;        // SAMPLE ONLY: measure Apple/other finished MagSafe puck
MAGSAFE_THICKNESS = 6;        // SAMPLE ONLY: actual puck thickness and strain relief
MAGSAFE_COIL_FRACTION = .51;  // SAMPLE: calibrate to physical charging center
PHONE_ANGLE_LANDSCAPE = 70;   // test 65 / 70 / 75° with real 14 Pro + case   // deg up from desktop
PHONE_ANGLE_PORTRAIT = 32;    // deg up from desktop
PHONE_Y0 = 42;               // bottom edge distance from front origin
PHONE_Z0 = 7;               // bottom phone edge height
// case/desk architecture
EDGE_MARGIN = 8;
BASE_THICK = 5;
BASE_MIN_DEPTH = 95;   // sample structural/charger clearance; verify real footprint
REAR_CLEARANCE = 22;   // placeholder cable/anti-tip clearance
BASE_CORNER = 9;
ROD_WIDTH = 8;               // physical test: stiffer if necessary
SADDLE_GAP = 1.5;             // compressible rubber interface to be added
OPTIONAL_NFC = false;        // phase-B reversible side pad concept only
NFC_SIDE = "right";          // choose left/right after reach tests
COLOR_SHELL = [0.90,0.88,0.85]; // soft ivory
COLOR_SUPPORT = [0.65,0.61,0.70]; // muted lavender-grey

PHONE_L = PHONE_LENGTH + CASE_ALLOWANCE_LENGTH;
PHONE_W = PHONE_WIDTH + CASE_ALLOWANCE_WIDTH;
IS_LANDSCAPE = POSE=="landscape";
PHONE_XSPAN = IS_LANDSCAPE ? PHONE_L : PHONE_W;
PHONE_RUN = IS_LANDSCAPE ? PHONE_W : PHONE_L;
PHONE_ANGLE = IS_LANDSCAPE ? PHONE_ANGLE_LANDSCAPE : PHONE_ANGLE_PORTRAIT;
REAR_Y = PHONE_Y0 + PHONE_RUN*cos(PHONE_ANGLE);
PHONE_TOP_Z = PHONE_Z0 + PHONE_RUN*sin(PHONE_ANGLE);
SCREEN_TOP_Z = SCREEN_Z0 + SCREEN_H*sin(SCREEN_ANGLE);
BASE_W = max(SCREEN_W + 2*EDGE_MARGIN, PHONE_XSPAN + 2*EDGE_MARGIN);
BASE_D = max(BASE_MIN_DEPTH,REAR_Y + REAR_CLEARANCE);
FOOTPRINT_MM2 = BASE_W * BASE_D;
HIDE_HEIGHT_MARGIN = SCREEN_TOP_Z - PHONE_TOP_Z;

echo("V14 MagSafe-case confirmed; charger mock ONLY, NOT final hardware.");
echo("V14 pose:",POSE);
echo("V14 estimated footprint W x D mm:",BASE_W,BASE_D);
echo("V14 estimated footprint cm2:",FOOTPRINT_MM2/100);
echo("V14 phone tip Z / display top Z mm:",PHONE_TOP_Z,SCREEN_TOP_Z);
echo("V14 front-view height margin mm (+ may hide horizontally):",HIDE_HEIGHT_MARGIN);
echo("Phone 14 Pro case MAGSAFE yes, brand/thickness/coil center TBD.");
echo("Charging puck is OPTIONAL removable; do not assume charging performance.");
echo("NOT accounting for seated downward sightline, camera bump, cable, mount tolerances.");
assert(POSE=="landscape", "V14 manufacturing baseline is landscape only; use V12 for portrait study");
assert(PHONE_ANGLE>5 && PHONE_ANGLE<80);
assert(SCREEN_ANGLE>=60 && SCREEN_ANGLE<=88);
assert(BASE_W>SCREEN_W);
assert(MAGSAFE_DIAMETER<PHONE_XSPAN);

module rr(w,d,h,r=7) {
  hull()
    for(x=[-w/2+r,w/2-r]) for(y=[r,d-r])
      translate([x,y,0]) cylinder(r=r,h=h);
}
module mount_screen_axis(){
  translate([0,SCREEN_Y0,SCREEN_Z0])
    rotate([-(90-SCREEN_ANGLE),0,0]) children();
}
module phone_axis(){
  translate([0,PHONE_Y0,PHONE_Z0])
    rotate([-(90-PHONE_ANGLE),0,0]) children();
}

module cable_exit(){
  // Recessed shallow cable lane, final wires routed only after port check.
  translate([-5,BASE_D-26,BASE_THICK-1.6]) cube([10,28,2]);
}
module base_plate(){
  color(COLOR_SHELL)
  difference() {
    rr(BASE_W, BASE_D,BASE_THICK,BASE_CORNER);
    cable_exit();
  }
}
module screen_frame(){
  // OEM case rear bracket only. Screws are disabled until real measurement.
  color(COLOR_SUPPORT)
  mount_screen_axis() {
    for(x=[-SCREEN_W/2+14,SCREEN_W/2-22])
      translate([x,SCREEN_T+2,4])
        cube([8,5,SCREEN_H-8]);
    translate([-SCREEN_W/2+14,SCREEN_T+2,SCREEN_H/2-5])
      cube([SCREEN_W-28,5,10]);
    // Screw markers are visual guide dots, NOT drilled mounting holes.
    if(SHOW_MOUNT_MARKERS)
      for(x=[-OEM_REAR_MOUNT_PITCH/2,OEM_REAR_MOUNT_PITCH/2])
        for(z=[SCREEN_H/2-OEM_REAR_MOUNT_PITCH/2,
               SCREEN_H/2+OEM_REAR_MOUNT_PITCH/2])
          color([.6,.3,.4]) translate([x,SCREEN_T+7,z])
            rotate([90,0,0]) cylinder(h=1.2,d=3.0);
  }
  // Anti-tip struts connect bracket towards the base on both sides.
  color(COLOR_SUPPORT)
  for(x=[-29,29])
    hull() {
      translate([x,SCREEN_Y0+SCREEN_T+16,
                 SCREEN_Z0+SCREEN_H*.56]) sphere(r=4);
      translate([x,min(BASE_D-14,SCREEN_Y0+59),
                 BASE_THICK+1]) sphere(r=5);
    }
  // Screen lip is a *small* removable cradle, not a phone tray.
  color(COLOR_SUPPORT)
  for(x=[-SCREEN_W/2+8,SCREEN_W/2-21])
    translate([x,SCREEN_Y0-6,BASE_THICK])
      cube([13,12,7]);
}
module phone_support(){
  color(COLOR_SUPPORT)
  phone_axis() {
    // Two open stiffening rails behind the phone.
    for(x=[-PHONE_XSPAN/2+10,PHONE_XSPAN/2-18]){
      translate([x,-8,4]) cube([8,5,PHONE_RUN-12]);
    }
    // Low foam-lined edge stop. Never extends forward of display face.
    translate([-PHONE_XSPAN/2-1,-9,-5])
      cube([PHONE_XSPAN+2,11,8]);
    // Small removable rear cross bar (avoid trapping charger).
    translate([-PHONE_XSPAN/2+10,-8,PHONE_RUN-15])
      cube([PHONE_XSPAN-20,5,7]);
  }
  // Rear gussets tie phone rails into base; avoid a fragile unsupported arm.
  for(x=[-min(PHONE_XSPAN/2-12,52),min(PHONE_XSPAN/2-12,52)])
    color(COLOR_SUPPORT) hull(){
      translate([x,PHONE_Y0+PHONE_RUN*.64*cos(PHONE_ANGLE),
                    PHONE_Z0+PHONE_RUN*.64*sin(PHONE_ANGLE)-4]) sphere(r=4);
      translate([x,BASE_D-16,BASE_THICK+1]) sphere(r=5);
    }
  // Puck is a concept disk ONLY. Position is approximate phone short-axis midpoint.
  // Actual receiver must permit 2-axis alignment and open-backed, serviceable mounting.
  if(SHOW_PUCK) color([.91,.72,.48,.75]) phone_axis()
    translate([0,-MAGSAFE_THICKNESS/2,PHONE_RUN*MAGSAFE_COIL_FRACTION])
      rotate([90,0,0]) cylinder(h=MAGSAFE_THICKNESS,d=MAGSAFE_DIAMETER,center=true);
}
module screen_reference(){
  color([.16,.18,.21,.80])
  mount_screen_axis()
    translate([-SCREEN_W/2,0,0]) cube([SCREEN_W,SCREEN_T,SCREEN_H]);
  color([.94,.92,.88,.55])
  mount_screen_axis()
    translate([-SCREEN_W/2+7,-.5,8])
      cube([SCREEN_W-14,.5,SCREEN_H-16]);
}
module phone_reference(){
  color([.25,.32,.45,.32])
  phone_axis()
    translate([-PHONE_XSPAN/2,0,0])
      cube([PHONE_XSPAN,PHONE_CASE_THICKNESS,PHONE_RUN]);
}
module future_nfc(){
  if(OPTIONAL_NFC)
    color([.74,.68,.80])
      translate([(NFC_SIDE=="right"?1:-1)*(BASE_W/2+13),24,BASE_THICK])
        cylinder(d=28,h=3);
}
module assembly(){
  base_plate();
  screen_frame();
  phone_support();
  future_nfc();
  if(SHOW_SCREEN) screen_reference();
  if(SHOW_PHONE) phone_reference();
}
if(PART=="assembly") assembly();
else if(PART=="base") base_plate();
else if(PART=="screen_frame") screen_frame();
else if(PART=="phone_support") phone_support();
else if(PART=="template_2d"){
  projection(cut=false) {
    base_plate();
    // Projection is ONLY an outline check. Requires hole and cutout measurements.
  }
}

// This model is deliberately a **design envelope** not a build-certified CAD.
// Validated assembly needs port openings, fastener sizes, wall thickness, full
// FDM support checks, safety fillets, case contact pads, puck fit and heat tests.
