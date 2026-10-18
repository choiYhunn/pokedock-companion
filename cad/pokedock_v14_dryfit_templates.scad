// PokéDock V14 — 1:1 cardboard / acrylic dry-fit CUTTING TEMPLATES.
// NOT a structural stand, printed charging cradle or production fastener drawing.
// All lengths are millimeters; export to SVG/DXF at 1:1 and verify 100 mm ruler.
// PRODUCT: iPhone 14 Pro landscape 65/70/75 deg; OEM C-BOX 33630.
// CASE_L/W are *temporary sample values* until physical caliper reading.
// Output choices: "angle_65", "angle_70", "angle_75", "phone", "hmi", "envelope", "all".
// The output is planar (2D) for cardboard trial; it deliberately has NO assumed
// 75x75 mounting holes, no magnetic puck retention, no power/cable cutout.
$fn = 64;
PART = "all";
CASE_L = 153.5;           // SAMPLE (bare 147.5 + total case allowance 6mm)
CASE_W = 77.5;            // SAMPLE (bare 71.5 + total case allowance 6mm)
HMI_W = 116.3;            // OEM published exterior; remeasure delivered product
HMI_H = 79.0;
BASE_W = 169.5;           // V14 visual envelope sample only
BASE_D = 95.0;            // MagSafe-ready sample only, no tip/traction proof
EDGE_LINE = 0.6;          // guide stroke material
MEASURE_BAR = 100;

assert(CASE_L >= 147.5);
assert(CASE_W >= 71.5);
assert(BASE_W > HMI_W);
assert(BASE_D > 0);

// Closed outline of the PHONE PROFILE in the vertical Y/Z plane.
// Lay the phone long edge horizontally (into the sheet/page in the physical jig);
// the short-edge rises at the requested angle. These are *side profile shapes*,
// not load-bearing side walls or safe phone-support geometry.
module angle_profile(theta) {
    run = CASE_W * cos(theta);
    rise = CASE_W * sin(theta);
    polygon([[0,0],[run,0],[run,rise]]);
}
module profile_line(theta) {
    run = CASE_W * cos(theta);
    rise = CASE_W * sin(theta);
    hull() {
        translate([0,0]) circle(d=EDGE_LINE);
        translate([run,rise]) circle(d=EDGE_LINE);
    }
}
module outline_rect(w,h,stroke=0.6) {
    difference() {
        square([w,h], center=false);
        translate([stroke,stroke])
            square([w-2*stroke,h-2*stroke],center=false);
    }
}
module scale_bar() {
    // Calibration ruler: must measure exactly 100.0 mm after export/print.
    square([MEASURE_BAR,1]);
    for(x=[0,10,20,30,40,50,60,70,80,90,100])
        translate([x,0]) square([0.45, x%50==0?8:4]);
}
module angle_sheet(theta) {
    angle_profile(theta);
    // Solid triangle = cardboard side template. Cut two matching strips
    // and attach a removable *independent* anti-tip base. Do not load test
    // a merely-taped triangle: only a stiffened mock is intended.
}
module phone_sheet() { outline_rect(CASE_L, CASE_W); }
module hmi_sheet() { outline_rect(HMI_W,HMI_H); }
module envelope_sheet() { outline_rect(BASE_W, BASE_D); }

if (PART=="angle_65") angle_sheet(65);
else if (PART=="angle_70") angle_sheet(70);
else if (PART=="angle_75") angle_sheet(75);
else if (PART=="phone") phone_sheet();
else if (PART=="hmi") hmi_sheet();
else if (PART=="envelope") envelope_sheet();
else if (PART=="all") {
    // Intentionally spaced independent pieces for 1:1 projection.
    translate([0,0]) angle_sheet(65);
    translate([45,0]) angle_sheet(70);
    translate([85,0]) angle_sheet(75);
    translate([0,92]) phone_sheet();
    translate([0,185]) hmi_sheet();
    translate([0,280]) envelope_sheet();
    translate([0,390]) scale_bar();
}
echo("sample case L/W",CASE_L,CASE_W);
echo("sample 70deg rearward projection",CASE_W*cos(70));
echo("sample 70deg height projection",CASE_W*sin(70));
echo("OUTPUT IS FIT TEMPLATE ONLY — NO STRUCTURAL APPROVAL");
