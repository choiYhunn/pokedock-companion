"""Small, cheap fit-check prints cut from the real M6 geometry (print these before the full ball).

usage: python build_fit_kit.py <cad_out_dir>
  fitkit_port_coupon   : lower-shell window around the USB-C port + breakout block (Adafruit 4090 fit)
  fitkit_joint_coupon  : 40 mm arc of lower rim + spigot (belt + upper counterbore fit)
  fitkit_belt_segment  : matching 40 mm belt arc
  fitkit_upper_segment : matching 40 mm upper-rim arc
The bezel and display plate are printed as-is (they are small) to fit the real board.
"""
import os
import sys

from build123d import Box, Plane, Pos, export_step, import_step

sys.path.insert(0, os.path.dirname(__file__))
import build_m6 as B  # noqa: E402
import m6_params as P  # noqa: E402

OUT = sys.argv[1]
os.makedirs(f"{OUT}/fitkit", exist_ok=True)
lower = import_step(f"{OUT}/step/lower_shell_ivory.step")
belt = import_step(f"{OUT}/step/belt_black.step")
upper = import_step(f"{OUT}/step/upper_shell_purple.step")

u = P.unit(180, P.USB_EL_DEG)
pl = Plane(origin=(0, 0, 0), x_dir=(1, 0, 0), z_dir=u)
port_box = B.local_box(pl, -16, 16, -10, 14, 48, P.R + 1)
arc_box = Pos(P.R - 6, 0, 0) * Box(16, 40, 30)   # +x side, away from the button and columns

kit = {
    "fitkit_port_coupon": lower & port_box,
    "fitkit_joint_coupon": lower & arc_box,
    "fitkit_belt_segment": belt & arc_box,
    "fitkit_upper_segment": upper & arc_box,
}
for name, shp in kit.items():
    export_step(shp, f"{OUT}/fitkit/{name}.step")
    B.export_clean_stl(shp, f"{OUT}/fitkit/{name}.stl")
    print(name, round(shp.volume, 1), "mm3")
