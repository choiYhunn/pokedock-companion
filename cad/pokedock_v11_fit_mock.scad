// PokéDock V11 adjustable *fit mockup*, NOT production tooling.
// Coordinates: x = width, y = rear, z = height, millimeters.
// IMPORTANT: replace all SAMPLE dimensions using actual 4.3C-BOX,
// iPhone+case and protected MagSafe puck measurements before fabrication.
// This preview deliberately does not model USB/power/RTC/antenna holes.
// Do not glue, drill or encapsulate the charger using these sample values.
$fn=48;

// SAMPLE / NOT MEASURED. Verify each before manufacturing.
CASE_W = 132;          // measured widest 4.3C-BOX plastic outside width
CASE_H = 84;           // measured plastic case outside height
CASE_D = 18;           // measured plastic case thickness
PHONE_W = 78;          // actual phone with everyday case width
PHONE_H = 153;         // actual phone with everyday case height
PHONE_T = 12;          // actual phone with case/camera thickness max
PHONE_ANGLE = 30;      // degrees up from desk, low enough to tuck behind screen
CHARGER_D = 57;        // actual complete MagSafe puck outside diameter
CHARGER_T = 6;         // actual puck thickness incl. relief
MARGIN_X = 5;          // side margin
CLEARANCE = 2;         // mechanical prototype spacing allowance
BASE_FRONT_D = 78;     // shallow main front footprint, not overall depth
BASE_THICK = 5;
BASE_W = max(CASE_W+2*MARGIN_X,PHONE_W+2*MARGIN_X);
FRONT_PANEL_ANGLE = 80; // from desk; visual placeholder
PHONE_BOTTOM_Y = 58;   // where phone lower edge rests; measure USB access
PHONE_BOTTOM_Z = 10;
SUPPORT_T = 3;
SHOW_PHONE_MOCK = true;
SHOW_HMI_MOCK = true;
SHOW_QI_GUIDE = true;
SHOW_OPTIONAL_NFC = false; // optional side module deferred until phase B

// Derived geometry: tall upright portrait iPhone will stick above the screen.
PHONE_REAR_EXTENSION = PHONE_H*cos(PHONE_ANGLE);
PHONE_TOP_Z = PHONE_BOTTOM_Z + PHONE_H*sin(PHONE_ANGLE);
PHONE_REAR_Y = PHONE_BOTTOM_Y + PHONE_REAR_EXTENSION;
TOTAL_DESK_DEPTH_APPROX = max(BASE_FRONT_D,PHONE_REAR_Y+8);

echo("PHONE TOP HEIGHT ABOVE DESK (sample)=",PHONE_TOP_Z);
echo("PHONE REAR EXTENT FROM FRONT DATUM (sample)=",PHONE_REAR_Y);
echo("TOTAL DESK DEPTH / NO FRONT TRAY (sample)=",TOTAL_DESK_DEPTH_APPROX);
echo("CASE HEIGHT SAMPLE=",CASE_H);
if(PHONE_TOP_Z > CASE_H+10)
  echo("WARNING: upright phone likely protrudes above front HMI; prototype first.");
if(CHARGER_D>PHONE_W-2*CLEARANCE)
  echo("WARNING: charger puck wider than phone surface allowance.");

module rounded_plate(w,d,h,r=6){
  hull() for(x=[-w/2+r,w/2-r]) for(y=[r,d-r])
    translate([x,y,0]) cylinder(h=h,r=r);
}

// A simple rear-reaching stabilizer frame, NOT a sized structural design.
module rear_foot(){
  color([.37,.31,.45])
  translate([0,PHONE_REAR_Y-13,0]) rounded_plate(BASE_W-18,25,BASE_THICK,6);
  for(x=[-BASE_W/2+8,BASE_W/2-15])
    color([.4,.35,.49]) translate([x,BASE_FRONT_D-12,0])
    cube([7,max(1,PHONE_REAR_Y-BASE_FRONT_D),BASE_THICK]);
}

module front_base(){
  color([.39,.32,.5]) rounded_plate(BASE_W,BASE_FRONT_D,BASE_THICK,7);
  rear_foot();
}

// Simple tablet-style front display visual mock — NO fastening holes defined.
module hmi_mock(){
  color([.15,.14,.19,.85])
  translate([-CASE_W/2,14,BASE_THICK+4])
    rotate([-(90-FRONT_PANEL_ANGLE),0,0])
    cube([CASE_W,CASE_D,CASE_H]);
  color([.30,.32,.35,.8])
  translate([-CASE_W/2-1,12,BASE_THICK+3]) cube([CASE_W+2,8,9]);
}

// Rear phone plane: local z axis is along long phone side.
module phone_axis() {
  translate([0,PHONE_BOTTOM_Y,PHONE_BOTTOM_Z])
    rotate([-(90-PHONE_ANGLE),0,0])
      children();
}

module rear_support(){
  phone_axis(){
    // Two rails keep a removable MagSafe puck open and accessible.
    color([.62,.54,.72])
    for(x=[-PHONE_W/2+4,PHONE_W/2-10]) translate([x,-SUPPORT_T,-1])
      cube([6,SUPPORT_T,PHONE_H-6]);
    // lower stop only. It must not obstruct phone port or press screen.
    color([.38,.32,.5]) translate([-PHONE_W/2-1,-SUPPORT_T-4,-3])
      cube([PHONE_W+2,SUPPORT_T+5,6]);
    // top bridging strap is a conceptual guide; final requires access.
    color([.55,.48,.66]) translate([-PHONE_W/2+4,-SUPPORT_T,PHONE_H-12])
      cube([PHONE_W-8,SUPPORT_T,7]);
  }
  // Supports need engineering based on actual device mass and moment,
  // not just a single visual brace. Leave them open and removable.
}

module phone_mock(){
  phone_axis() color([.23,.27,.37,.35])
    translate([-PHONE_W/2,0,0]) cube([PHONE_W,PHONE_T,PHONE_H]);
}

module qi_reference(){
  phone_axis(){
    translate([0,-CHARGER_T/2,PHONE_H*0.53])
      rotate([90,0,0])
      color([.92,.72,.25,.6]) cylinder(d=CHARGER_D,h=CHARGER_T,center=true);
  }
}

module nfc_future(){
  // Not purchased/installed until electrical noise and range validated.
  color([.25,.61,.75,.45])
  translate([BASE_W/2+14,21,BASE_THICK]) cylinder(d=28,h=3);
}

front_base();
if(SHOW_HMI_MOCK) hmi_mock();
rear_support();
if(SHOW_PHONE_MOCK) phone_mock();
if(SHOW_QI_GUIDE) qi_reference();
if(SHOW_OPTIONAL_NFC) nfc_future();

// This preview intentionally has no permanent attachment holes, no mains
// components, no battery, and no precise camera/cable/antenna relief.
