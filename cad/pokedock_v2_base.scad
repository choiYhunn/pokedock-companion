// PokéDock V2 concept base — dimensions in mm
// HMI uses rear 75 mm mounting holes.
// Qi tray is sized around Samsung EP-P2400 91x91x18.3, with clearance.
$fn=64;

BASE_W=270;
BASE_D=170;
BASE_H=9;
R=9;

QI_W=93.5;
QI_D=93.5;
QI_DEPTH=8;  // shallow top tray: charger remains removable/ventilated

VESA=75;
PLATE_W=118;
PLATE_H=105;
PLATE_T=6;
PLATE_Y=145;

module rbox(w,d,h,r){
 hull() for(x=[r,w-r]) for(y=[r,d-r]) translate([x,y,0]) cylinder(h=h,r=r);
}

difference(){
 union(){
   rbox(BASE_W,BASE_D,BASE_H,R);
   // HMI support plate
   translate([(BASE_W-PLATE_W)/2,PLATE_Y,BASE_H])
     rotate([12,0,0]) cube([PLATE_W,PLATE_T,PLATE_H]);
   // phone front stop around Qi tray
   translate([BASE_W-115,18,BASE_H]) cube([105,7,13]);
 }
 // removable Qi tray
 translate([BASE_W-QI_W-12,36,BASE_H-QI_DEPTH+0.1]) rbox(QI_W,QI_D,QI_DEPTH,8);
 // NFC marker/recess
 translate([52,70,BASE_H-1.2]) cylinder(h=2,d=55);
 // cable channels
 translate([122,-1,-0.1]) cube([18,150,4]);
 translate([BASE_W-65,-1,-0.1]) cube([14,55,4]);
}