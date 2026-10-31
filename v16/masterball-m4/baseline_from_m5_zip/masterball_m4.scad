// PokéDock Master Ball M4: PARAMETRIC MECHANICAL ENGINEERING PROVISIONAL
// [mm], x=right, y=back (+), z=up. origin ball center; screen faces y=-.
// DO NOT ORDER PRINT UNTIL ACTUAL Waveshare STANDARD /without case 1.43 STEP IS REGISTERED.
// Vendor PCB keepout modeled by conservative envelope only. All retaining parts and
// hardware clearance are REVISION CANDIDATES, not proven solder/component-safe grips.
$fn=64;
PART="assembly";
R=69; wall=2.8; floor_z=-61; joint_z=0;
ring_thickness=4.0; bezel_OD=60; window_ID=38.0;
screen_plane_y=-68.5; board_OD=46.0; board_clearance=0.7; board_depth=13.0;
// nominal 46 mm PCB/profile; official STEP may disagree. No pressure on glass.
function sr(yz) = sqrt(max(0,R*R-yz*yz));
module outside(){ intersection(){ sphere(r=R); translate([-80,-80,floor_z]) cube([160,160,R-floor_z+1]); } }
module inside(){ intersection(){ sphere(r=R-wall); translate([-80,-80,floor_z+wall]) cube([160,160,R-floor_z+1]); } }
module front_through(){ translate([0,-62.5,0]) rotate([90,0,0]) cylinder(d=51.5,h=27,center=true); }
module back_service_through(){translate([0,62,8]) rotate([90,0,0]) cylinder(d=58,h=28,center=true);}
// shell segments, vent/holes at rear 130deg not front for visual preservation
module upper_shell(){intersection(){ difference(){outside(); inside(); front_through(); back_service_through();} translate([-80,-80,joint_z]) cube([160,160,80]); }}
module lower_shell(){intersection(){difference(){outside(); inside(); front_through(); back_service_through();}translate([-80,-80,floor_z-2]) cube([160,160,-floor_z+2]);}}
module belt(){difference(){intersection(){difference(){ sphere(r=R+0.8);sphere(r=R-1.2); }translate([-80,-80,-ring_thickness/2]) cube([160,160,ring_thickness]);}front_through();back_service_through();}}
// Raised button-like bevel / central display sits flush with front face at center,
// but bevel is intentionally thicker at sides; natural poke-ball button appearance.
module bezel(){
  translate([0,-66,0])rotate([90,0,0])difference(){
    union(){cylinder(d=bezel_OD,h=6,center=true);translate([0,0,-4])cylinder(d=54,h=2,center=true);}
    cylinder(d=window_ID,h=12,center=true);
    for(a=[45:90:315])rotate([0,0,a])translate([26,0,-6])cylinder(d=2.1,h=14,center=true);
  }
}
// Retainer opening 47.4+; this ring is outboard of PCB (not touching electronics).
// Inner gasket/seating edge to be completed from official STEP, not assumed.
module retainer(){translate([0,-55.4,0]) rotate([90,0,0]) difference(){cylinder(d=56,h=3,center=true);cylinder(d=47.4,h=5,center=true);for(a=[45:90:315])rotate([0,0,a])translate([26,0,-3])cylinder(d=2.6,h=8,center=true);}}
module screen_keepout(){translate([0,screen_plane_y+board_depth/2,0])rotate([90,0,0])cylinder(d=board_OD+2*board_clearance,h=board_depth,center=true);}
module panel_active(){translate([0,screen_plane_y-.30,0])rotate([90,0,0])cylinder(d=36.75,h=.6,center=true);}
// Battery protected 1S nominal 3.7 V pack reserved 60x40x9mm maximum envelope.
// Slides in from rear SERVICE opening: verify insertion trajectory in supplier STEP.
module battery_keepout(){translate([0,9,-35])cube([60,40,10],center=true);}
module battery_tray(){translate([0,9,-41])difference(){union(){cube([67,47,3],center=true);
 for(x=[-31.0,31.0])translate([x,0,5])cube([3.0,47,10],center=true);
 for(y=[-21,21])translate([0,y,3])cube([62,3,6],center=true);
 }for(x=[-23,23])translate([x,0,0])cube([4,20,8],center=true);}}
// Rear hatch is a thin cosmetic blank - no finalized fixing scheme.
module hatch(){translate([0,69,8])rotate([90,0,0])difference(){cylinder(d=63,h=3,center=true);cylinder(d=9,h=5,center=true);}}
module pink_lobe(s){translate([s*40,-16,54]) rotate([0,0,-s*22])scale([1.07,.72,.45])sphere(r=16);}
module foot(){translate([0,0,floor_z-.8])cylinder(d=62,h=1.6,center=true);}
// External shells and internal tray for modeling only. Real heat/antenna gap unverified.
if(PART=="upper")upper_shell();
else if(PART=="lower")lower_shell();
else if(PART=="belt")belt();
else if(PART=="bezel")bezel();
else if(PART=="retainer")retainer();
else if(PART=="battery_tray")battery_tray();
else if(PART=="hatch")hatch();
else if(PART=="lobe_left")pink_lobe(-1);
else if(PART=="lobe_right")pink_lobe(1);
else if(PART=="screen_keepout")screen_keepout();
else if(PART=="battery_keepout")battery_keepout();
else {
 color([.42,.25,.66])upper_shell();color([.94,.93,.88])lower_shell();
 color([.105,.095,.13])belt();color([.78,.75,.80])bezel();
 color([.96,.94,.88])panel_active();color([.96,.48,.71])pink_lobe(-1);color([.96,.48,.71])pink_lobe(1);
 color([.86,.83,.80])hatch();color([.75,.65,.78])foot();
 if($preview){color([.4,.8,.7,.3])screen_keepout();color([.3,.7,.9,.24])battery_keepout();}
}
