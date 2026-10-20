/*
PokéDock V15 DESK-ONLY parametric cradle Rev A — 2026-10-20
Made for Waveshare ESP32-S3-Touch-LCD-4.3C-BOX, SKU 33630
Published case: W=116.3 mm H=79.0 mm T=18.0 mm.
No screw-hole dependence; front bottom tabs + rear ribs + optional removable Command strips.
Prototype-ready printable in one piece; NOT physical fit/stability approval.
Export: openscad -o v15_stand_revA.stl -D 'MODE="stand"' cad/pokedock_v15_cradle.scad
Units: mm. Bed-friendly flat bottom; no interior overhead / bridging required.
*/
$fn = 40;
MODE = "assembly"; // stand, assembly, a_stand, b_concept, c_concept, foot_print
CASE_W=116.3; CASE_H=79; CASE_T=18;
FACE_LEAN=15; // from vertical: screen approx 75 deg from tabletop
BASE_W=136; BASE_D=96; BASE_H=6.5;
BASE_RAD=10;
FRONT_Y=17; FRONT_Z=12;
CASE_PADS=1.0; // soft tape bearing interface, deliberately NOT part of print
// Actual case fillet curvature, terminal protrusion, port openings require dry fit.

module roundedplate(w,d,r,h){ linear_extrude(height=h) offset(r=r) square([w-2*r,d-2*r],center=true); }
module yzextrude(xc,width,vertices){
    multmatrix([[0,0,1,xc-width/2], [1,0,0,0], [0,1,0,0], [0,0,0,1]])
        linear_extrude(height=width,convexity=5) polygon(vertices);
}
module stand(){
  color([0.76,0.75,0.70]) union(){
    // Rear-center U-cut allows free DC terminal/cable clearance without
    // closing the side connector ports. Check actual cable bend on receipt.
    difference(){
      translate([0,BASE_D/2,0]) roundedplate(BASE_W,BASE_D,BASE_RAD,BASE_H);
      translate([0,91,-1]) roundedplate(70,118,8,BASE_H+2);
    }
    // Two triangular bearing ribs: only touch case back through removable 1mm pads.
    // Rear terminal area (central +/-35 mm) deliberately unobstructed.
    for(x=[-44,44]) yzextrude(x,11,[
       [35.4,6.1],[88.5,6.1],[88.5,9.2],[56.0,72.8],[53.35,72.8]
    ]);
    // Bottom front retaining lips, completely outside active pixel window.
    // Center 64 mm of the screen bottom and all lateral service edges are OPEN.
    for(x=[-45,45]) yzextrude(x,15,[
       [12.7,6.35],[16.7,6.35],[16.7,13.4],[14.15,13.4]
    ]);
    // Sideways lateral anti-slide guides; phone dock never used.
    for(side=[-1,1])
      translate([side*(CASE_W/2+3.3),28,BASE_H])
        cube([3.3,19.5,6.0],center=true);
  }
}
module case_mock(){
    // Opaque volume: simple rounded case geometry is a visualization proxy.
    translate([0,FRONT_Y,FRONT_Z]) rotate([-FACE_LEAN,0,0]){
      color([0.14,0.15,0.18]) translate([0,CASE_T/2,CASE_H/2])
        minkowski(){cube([CASE_W-4,CASE_T-4,CASE_H-4],center=true); sphere(r=2,$fn=12);}
      color([0.052,0.065,0.089]) translate([0,-.38,CASE_H/2])
        cube([98,.38,56],center=true);
      // original in-device placeholder ghost, not an official Pokémon artwork.
      color([0.67,0.60,0.91])
        translate([-27,-.83,35]) rotate([90,0,0]) linear_extrude(height=.25)
          text("25:00",size=12,font="DejaVu Sans:style=Bold");
      color([0.83,0.83,0.88])
        translate([-25,-.85,23]) rotate([90,0,0]) linear_extrude(height=.25)
          text("FOCUS  /  READY",size=3.1,font="DejaVu Sans");
    }
}
module pad_visuals(){
  for(x=[-44,44]){
    color([.1,.09,.10,.85]) yzextrude(x,9.5,[[53.2,61],[54.5,61],[57.0,72],[55.7,72]]);
  }
  for(x=[-45,45]){
    color([.08,.09,.11]) translate([x,14.5,16]) cube([13,1.0,1],center=true);
  }
}
module feet_visuals(){
  color([.12,.12,.13]) for(x=[-55,55],y=[13,82])
    translate([x,y,-1.4]) cylinder(h=1.4,r=6);
}
module b_concept(){
  // Design comparison only; NOT manufacturing geometry or quote.
  color([.67,.69,.70]){
   translate([0,36,0]) roundedplate(126,72,9,5);
   yzextrude(0,69,[[35,5],[48,5],[58,76],[47,76]]);
  }
}
module c_concept(){
  // Design comparison only; NOT manufacturing geometry or quote.
  color([.75,.75,.75]){
    translate([0,44,0]) roundedplate(136,88,9,6.5);
    yzextrude(0,86,[[26,6],[80,6],[57,74],[48,74]]);
  }
}
if(MODE=="stand"||MODE=="a_stand")stand();
else if(MODE=="assembly"){stand();pad_visuals();feet_visuals();case_mock();}
else if(MODE=="b_concept"){b_concept();case_mock();}
else if(MODE=="c_concept"){c_concept();case_mock();}
else if(MODE=="foot_print")projection(cut=false)stand();
else if(MODE=="clearance_check") intersection(){
  stand();
  translate([0,FRONT_Y,FRONT_Z]) rotate([-FACE_LEAN,0,0])
    translate([-CASE_W/2,0,0]) cube([CASE_W,CASE_T,CASE_H]);
}
else assert(false,"unknown MODE");

echo("REV_A_NOMINAL_CASE",CASE_W,CASE_H,CASE_T);
echo("REV_A_BASE",BASE_W,BASE_D,BASE_H);
echo("ALL FASTENERS=NONE; HAS SOFT PADS; BENCH TEST REQUIRED");
