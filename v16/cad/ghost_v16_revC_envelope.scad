// V16 Rev C dimensioned optical/mechanical ENVELOPE ONLY.
// The main print can be checked for watertightness, but PCB mounts and actual
// manufacturing fit/USB bending/beam-splitter seating remain UNSIGNED.
$fn=64;MODE="assembly"; // "base", "assembly", "optics"
W=132;D=105;H=54;R=19;WALL=3.2;FLOOR=3.5;
CHW=104;CHD=85;CHH=82;CHR=13;
SOURCE_W=64;SOURCE_D=47.2;SOURCE_T=11.8;
PANEL_W=49.65;PANEL_D=37.22;
CLOCK_W=61.50;CLOCK_H=39.50;CLOCK_ACTIVE_W=55.01;CLOCK_ACTIVE_H=27.49;
WIN_W=56.5;WIN_H=29.0;REF_W=64;REF_H=70;REF_T=1;ANGLE=45;
module round2d(w,d,r){offset(r=r)square([w-2*r,d-2*r],center=true);}
module base(){
 difference(){
  linear_extrude(height=H)round2d(W,D,R);
  translate([0,0,FLOOR])linear_extrude(height=H+1)round2d(W-2*WALL,D-2*WALL,R-WALL);
  translate([-WIN_W/2,-D/2-1,H/2-WIN_H/2])cube([WIN_W,WALL+3,WIN_H]);
  translate([-8,D/2-WALL-2,16])cube([16,WALL+4,12]); // NOT measured USB
  translate([47,-D/2-1,H/2])rotate([-90,0,0])cylinder(d=7.2,h=WALL+4); // shaft placeholder
 }
}
module source(){
 color([.13,.13,.2])translate([-SOURCE_W/2,-SOURCE_D/2,H-SOURCE_T-2])cube([SOURCE_W,SOURCE_D,SOURCE_T]);
 color([.35,.12,.48])translate([-PANEL_W/2,-PANEL_D/2,H-2.1])cube([PANEL_W,PANEL_D,.8]);
}
module clock(){
 color([.14,.14,.2])translate([-CLOCK_W/2,-D/2+WALL+1,H/2-CLOCK_H/2])cube([CLOCK_W,3,CLOCK_H]);
 color([.42,.31,.56])translate([-CLOCK_ACTIVE_W/2,-D/2+.3,H/2-CLOCK_ACTIVE_H/2])cube([CLOCK_ACTIVE_W,.4,CLOCK_ACTIVE_H]);
}
module cover(){
 color([.77,.87,.97,.18])translate([0,0,H+CHH/2])
 difference(){
  linear_extrude(height=CHH,center=true)round2d(CHW,CHD,CHR);
  linear_extrude(height=CHH+.5,center=true)round2d(CHW-2.5,CHD-2.5,CHR-1.25);
 }
}
module reflector(){
 color([.56,.9,1,.36])translate([0,0,H+40])rotate([ANGLE,0,0])cube([REF_W,REF_T,REF_H],center=true);
}
if(MODE=="base")base();
else if(MODE=="optics"){cover();source();reflector();}
else if(MODE=="assembly"){color([.96,.91,.87])base();cover();reflector();source();clock();}
else assert(false,"unknown MODE");
