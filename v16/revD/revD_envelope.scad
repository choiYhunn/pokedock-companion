// Rev D dimensional envelope and trial optical rails. NOT approved final-fit print.
$fn=64; MODE="assembly";
W=132;D=105;H=54;R=19;WALL=3.2;FLOOR=3.5;
CW=104;CD=91;CH=82; // clear 5-face canopy TARGET, not vendor-quoted
PLATE_W=82;PLATE_LEN=88;PLATE_T=1;PLATE_Y=-7;PLATE_Z=94;ANGLE=45;
OLED_PCB_W=61.5;OLED_PCB_H=39.5;OLED_ACTIVE_W=55.01;OLED_ACTIVE_H=27.49;
AMOLED_W=64;AMOLED_D=47.2;AMOLED_H=11.8;
module rr(w,d,r){offset(r=r)square([w-2*r,d-2*r],center=true);}
module base(){difference(){
linear_extrude(height=H)rr(W,D,R);
translate([0,0,FLOOR])linear_extrude(height=H+2)rr(W-2*WALL,D-2*WALL,R-WALL);
translate([-28.25,-D/2-1,H/2-14.5])cube([56.5,WALL+3,29]);
translate([-10,D/2-WALL-1,17])cube([20,WALL+3,13]); // USB notch NOT measured
translate([48,-D/2-1,H/2])rotate([-90,0,0])cylinder(h=WALL+3,d=7.2); // encoder TBD
}}
module source(){color([.11,.12,.15])translate([-AMOLED_W/2,-AMOLED_D/2,H-AMOLED_H-2])cube([AMOLED_W,AMOLED_D,AMOLED_H]);color([.4,.2,.6])translate([-49.65/2,-37.22/2,H-2])cube([49.65,37.22,1]);}
module oled(){color([.1,.1,.16])translate([-OLED_PCB_W/2,-D/2+WALL+.5,H/2-OLED_PCB_H/2])cube([OLED_PCB_W,2.5,OLED_PCB_H]);color([.6,.65,.7])translate([-OLED_ACTIVE_W/2,-D/2+.4,H/2-OLED_ACTIVE_H/2])cube([OLED_ACTIVE_W,.4,OLED_ACTIVE_H]);}
module optics(){color([.63,.8,.92,.28])translate([0,PLATE_Y,PLATE_Z])rotate([ANGLE,0,0])cube([PLATE_W,PLATE_T,PLATE_LEN],center=true);}
module transparent_cover(){color([.75,.84,1,.2])translate([0,0,H+CH/2])difference(){linear_extrude(height=CH,center=true)rr(CW,CD,13);linear_extrude(height=CH+1,center=true)rr(CW-2.5,CD-2.5,11.75);}}
module rail(x){color([.93,.89,.86])difference(){union(){
translate([x,PLATE_Y,PLATE_Z])rotate([ANGLE,0,0])cube([5,5,PLATE_LEN+4],center=true);
translate([x-3,22,H+.4])cube([6,8,10]);}
translate([x,PLATE_Y,PLATE_Z])rotate([ANGLE,0,0])cube([2.5,2.0,PLATE_LEN+8],center=true);}}
if(MODE=="base")base();
else if(MODE=="rails"){rail(-PLATE_W/2-2);rail(PLATE_W/2+2);}
else if(MODE=="optics"){optics();rail(-PLATE_W/2-2);rail(PLATE_W/2+2);}
else if(MODE=="assembly"){color([.95,.91,.85])base();source();oled();transparent_cover();optics();rail(-PLATE_W/2-2);rail(PLATE_W/2+2);}
else assert(false,"unknown MODE");
