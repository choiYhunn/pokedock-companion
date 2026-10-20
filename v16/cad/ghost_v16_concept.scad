// PokéDock V16: dimensional LOOK + printable base mock ONLY.
// NOT an approved fit for any actual AMOLED/OLED, beamsplitter, USB or encoder.
// Units: millimetres. OpenSCAD: -D 'MODE="base"' for ONE solid mock base.
$fn=48;
MODE="assembly"; // "base" (printable mock only), "assembly" (concept visualization)
W=132; D=97; H=47; R=20; WALL=3.0;
CHAMBER_W=103;CHAMBER_D=77;CHAMBER_H=82;CHAMBER_R=12;
module rr(w,d,r){offset(r=r) square([w-2*r,d-2*r],center=true);}
module blank_base(){linear_extrude(height=H) rr(W,D,R);}
module base() {
 difference(){
   blank_base();
   // Open top: avoids trapping prototype board; not a PCB mount.
   translate([0,0,WALL]) linear_extrude(height=H+2) rr(W-2*WALL,D-2*WALL,R-WALL);
   // Front CLOCK aperture ONLY; do not infer actual SSD1327 mounting method.
   translate([-22,-D/2-1,8]) cube([44,WALL+3,32]);
   // Rear cable notch; location provisional.
   translate([-8,D/2-WALL-1,12]) cube([16,WALL+3,26]);
 }
}
module chamber_mock(){
 // A rounded, clear outer visual shell -- this is NOT an optical reflector.
 color([0.77,0.67,0.95,0.18])
 translate([0,0,H+CHAMBER_H/2])
 difference(){
   linear_extrude(height=CHAMBER_H,center=true) rr(CHAMBER_W,CHAMBER_D,CHAMBER_R);
   linear_extrude(height=CHAMBER_H+2,center=true) rr(CHAMBER_W-2,CHAMBER_D-2,CHAMBER_R-1);
 }
 // One FLAT 45-degree internal reflector in conceptual position.
 color([0.73,0.89,1,0.22])
 translate([-44,1,H+35]) rotate([45,0,0]) cube([88,1.0,65],center=false);
 // optical source placeholder below chamber
 color([0.1,0.08,0.15]) translate([-24,-17,H+0.4]) cube([48,48,2]);
 // Clock image plane placeholder visible through aperture
 color([0.08,0.07,0.1]) translate([-22,-D/2+0.1,8]) cube([44,1,32]);
}
if (MODE=="base") base();
else if (MODE=="assembly") {color([0.92,0.87,0.84]) base();chamber_mock();}
else assert(false,str("Unknown MODE=",MODE));
