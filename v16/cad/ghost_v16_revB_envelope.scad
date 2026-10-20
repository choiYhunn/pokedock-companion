// PokéDock Ghost Companion V16 Rev B. Measured module ENVELOPES; not print-qualified mounting.
// Manufacturer: AMOLED 2.41 WITHOUT case PCB 47.2x64.0x11.8mm;
// Waveshare 1.5 SSD1327 OLED PCB 44.5x37.0mm, active square 26.86mm.
// MODE "base" exports one watertight prototype shell; "assembly" for inspection.
$fn=72;
MODE="assembly";
W=132;D=105;H=54;CORNER=19;WALL=3.2;FLOOR=3.5;
AMOLED_W=64;AMOLED_D=47.2;AMOLED_T=11.8;
OLED_PCB_W=44.5;OLED_PCB_H=37.0;OLED_ACTIVE=26.86;
CH_W=104;CH_D=85;CH_H=82;CH_R=13;
PLATE_W=64;PLATE_LEN=70;PLATE_T=1;
ENCODER_HOLE_D=7.2; // MUST verify actual encoder mechanical drawing
module rounded2D(w,d,r){offset(r=r)square([w-2*r,d-2*r],center=true);}
module base(){
 difference(){
  linear_extrude(height=H)rounded2D(W,D,CORNER);
  translate([0,0,FLOOR])linear_extrude(height=H+1)rounded2D(W-2*WALL,D-2*WALL,CORNER-WALL);
  // Aperture fits 26.86x26.86 ACTIVE pixels; PCB goes behind it.
  translate([-OLED_ACTIVE/2-.5,-D/2-1,H/2-OLED_ACTIVE/2-.5])
   cube([OLED_ACTIVE+1,6,OLED_ACTIVE+1]);
  // Rear USB service notch is a PLACEHOLDER, board orientation pending.
  translate([-8,D/2-WALL-2,15])cube([16,7,12]);
  // Encoder shaft hole only; board mounting bracket unverified.
  translate([41,-D/2-1,H/2])rotate([-90,0,0])cylinder(h=8,d=ENCODER_HOLE_D);
 }
}
module amoled_envelope(){
 color([.14,.14,.18])translate([-AMOLED_W/2,-AMOLED_D/2,H-AMOLED_T-2])
  cube([AMOLED_W,AMOLED_D,AMOLED_T]);
 color([.20,.08,.28])translate([-49.65/2,-37.22/2,H-2.1])cube([49.65,37.22,.8]);
}
module oled_envelope(){
 color([.1,.1,.13])translate([-OLED_PCB_W/2,-D/2+WALL+.4,H/2-OLED_PCB_H/2])
  cube([OLED_PCB_W,2.5,OLED_PCB_H]);
 color([.34,.19,.45])translate([-OLED_ACTIVE/2,-D/2+WALL-.5,H/2-OLED_ACTIVE/2])
  cube([OLED_ACTIVE,.5,OLED_ACTIVE]);
}
module chamber(){
 color([.83,.74,.98,.16])translate([0,0,H+CH_H/2])
 difference(){
  linear_extrude(height=CH_H,center=true)rounded2D(CH_W,CH_D,CH_R);
  linear_extrude(height=CH_H+2,center=true)rounded2D(CH_W-2.5,CH_D-2.5,CH_R-1.25);
 }
}
module reflector(){
 // 70mm @ 45deg gives approx +/-24.75mm in Y and Z; fits 85mm depth.
 color([.65,.84,1,.33])
 translate([0,0,H+40])rotate([45,0,0])cube([PLATE_W,PLATE_T,PLATE_LEN],center=true);
}
if(MODE=="base")color([.95,.91,.86])base();
else if(MODE=="assembly"){
 color([.95,.91,.86])base();
 chamber();reflector();amoled_envelope();oled_envelope();
}
else if(MODE=="envelope"){amoled_envelope();oled_envelope();reflector();}
else assert(false,str("Unknown MODE:",MODE));
