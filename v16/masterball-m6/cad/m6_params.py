"""PokéDock Master Ball M6: single source of truth for mechanical parameters (mm).

Frame: origin = ball centre, +x right, +y BACK (away from viewer), +z up. Screen faces -y.
Board frame (official Waveshare STEP): glass top z=+1.10, parts grow to -z; USB-C mouth at -x.
Board -> ball (proper rotation, det +1): ball_x = -step_y, ball_z = step_x (USB-C points DOWN),
                ball_y = GLASS_Y + (1.10 - step_z)
"""
import math

# --- sphere -----------------------------------------------------------------------------
R = 69.0            # outer radius (138 mm ball)
WALL = 2.8
RI = R - WALL       # 66.2 inner radius
BASE_Z = -61.0      # flat anti-roll base (outer)
FOOT_TANGENT_Z = -R / 2 ** 0.5   # 45 deg conical foot tangent to the sphere (support-free base-down print)
FOOT_R_AT_BASE = -FOOT_TANGENT_Z - (FOOT_TANGENT_Z - BASE_Z)  # 36.6 -> flat base d73
FEET_R = 31.0       # 6 silicone bumpers on a hexagon
FLOOR_TOP_Z = -58.0
BELT_H = 7.0        # black equator belt height
BH = BELT_H / 2

# --- fits (radial clearances) -------------------------------------------------------------
FIT_PRINT = 0.35    # printed <-> printed sliding fit
FIT_VENDOR = 0.30   # printed <-> vendor part

# --- display module (official STEP, verified 2026-10-24) ------------------------------------
GLASS_R = 23.0                  # cover glass OD 46.00 +/-0.1
ACTIVE_R = 36.75 / 2
GLASS_TO_STANDOFF = 10.22       # glass top -> SMT standoff end (STEP z +1.10 -> -9.12)
STANDOFFS_XZ = [(sx * 15.75, sz * 11.60) for sx in (-1, 1) for sz in (-1, 1)]  # ball x,z
HEADERS_X = 16.25               # J1/J3 2x7 1.27 mm headers at ball x = +/-(14..18.5), |z|<=4.6
SOCKET_BOX = (5.3, 9.2)         # 1.27 mm 2x7 female, no end overhang (x width, z length)
SOCKET_Y = (-61.6, -50.0)       # socket body + wire bend keep-out
KEYS_XZ = [(-17.25, 7.5), (-17.25, -7.5)]  # BOOT / RESET switches (ball -x side)
PLATE_WINDOW = (7.0, 12.5)      # x, z

# --- front button (bezel) ------------------------------------------------------------------
GLASS_Y = -69.30                # glass front face
LIP_GAP = 0.60                  # glass -> lip (0.5 mm soft foam ring optional)
BEZEL_FRONT_Y = -71.4           # 2.4 mm proud of the sphere pole, 2.1 mm in front of glass
WINDOW_CHAMFER = 0.6
BEZEL_R = 29.0
WINDOW_R = 18.8                 # visible black border 0.43 mm nominal
POCKET_R = GLASS_R + 0.50        # rev B: 0.50 (hole undersize + PETG shrink + glass tol); centred by screws
PLATE_FRONT_Y = GLASS_Y + GLASS_TO_STANDOFF  # -59.08 (= bezel rear face)
PLATE_T = 2.5
PLATE_BACK_Y = PLATE_FRONT_Y + PLATE_T        # -56.58
PLATE_R = 29.0                  # flush with bezel OD; 0.35 to shell opening, >=1.3 to inner wall
INSERT_R = 26.10                # M2 PT-screw pilots in bezel rear face (rev B: no heat-set inserts)
M2_PT_PILOT = 1.7               # pilot for M2 self-tapping (PT/plastite) screws in PETG
M2_CLEAR = 2.2                  # clearance for M2 through plate / rib (play 0.10)
INSERT_ANG = {"top_l": 135, "top_r": 45, "bot_l": 225, "bot_r": 315}
OPENING_R = BEZEL_R + 0.60     # rev B: 0.60 (was 0.35) after FDM stack, see tolerance_stack.py
SCREW_PLAY = 0.10               # M2 PT screw in d2.2 clearance hole (rev A: d2.4 -> 0.20)

# --- backstop ribs ------------------------------------------------------------------------
RIB_T = 3.0
LOWER_RIB_Y0 = PLATE_BACK_Y                   # clamped contact (2x M2 screws)
UPPER_RIB_Y0 = PLATE_BACK_Y + 0.40            # 0.4 gap + 0.8 mm foam pad
RIB_WINDOW_R = 20.0

# --- shell joint ------------------------------------------------------------------------
SPIGOT_R_OUT = 65.0
SPIGOT_R_IN = 63.4
SPIGOT_TOP_Z = BH + 4.0                        # 7.5
COUNTERBORE_R = SPIGOT_R_OUT + 0.55            # rev B: 0.55 (upper shell + belt bore; spigot ring flexes)
SPIGOT_FRONT_CLEAR_R = 38.5
COLUMN_R_POS = 26.0
COLUMN_ANGLES = (90.0, 210.0, 330.0)           # around z from +x, 90 = back
COLUMN_OD = 8.0
M3_CLEAR = 3.8                                  # rev B: long printed bore prints small
M3_HEAD_BORE = 6.5
HEAD_SEAT_Z = -43.0                            # M3x50 DIN912: tip at +7 mm
M3_INSERT_HOLE = 4.0                           # M3 x 5.7 heat-set insert
UPPER_BOSS_DEPTH = 9.0

# --- external USB-C (Adafruit 4090 downstream breakout, Eagle rev B) -----------------------
USB_EL_DEG = -25.0
USB_PCB = (20.32, 13.97, 1.6)                  # width (x), depth (radial), thickness
USB_CONN = (8.94, 7.35, 3.26)                  # receptacle body w, l, h (CUI CUSB31-CFM2AX)
USB_CONN_PROTRUDE = 0.23
USB_HOLES = [(-7.62, 2.54), (7.62, 2.54)]       # x, distance from connector edge, d2.5
USB_POCKET = (14.0, 8.6, 2.3)                  # outer plug pocket w, h, depth (0.5 mm floor)
USB_HOLE = (9.3, 3.7)
USB_SLOT_CLR = 0.45                            # rev B: receptacle / PCB pass-through slot (was 0.30/0.35)

# --- buzzer: Soberton WT-1205 (5 V passive magnetic, d12.0 x H9.5, tolerance +/-0.5) --------------
BUZZER_PART = "Soberton WT-1205"
BUZZER_RAIL_V = 5.0
BUZ_AZ_DEG = 140.0                             # around z from +x (back-left)
BUZ_EL_DEG = -15.0
BUZ_D, BUZ_H = 12.0, 9.5                       # datasheet nominal
BUZ_TOL = 0.5                                  # datasheet: +/-0.5 mm
BUZ_FIT = 0.60                                 # radial: d12.5 max part + undersized hole; hot-melt dab
# buzzer driver perfboard (AO3400A on SOT-23 adapter, 100R, 100k, 1N4148): taped to the lower inner wall
DRV_AZ_DEG, DRV_EL_DEG = -110.0, -28.0
DRV_BOARD = (24.0, 18.0, 10.0)                 # perfboard x, y, height incl. parts and 1.6 mm board
DRV_TAPE = 1.0                                 # board-corner clearance to the raw curved wall
DRV_C0 = math.sqrt(RI ** 2 - (DRV_BOARD[0] ** 2 + DRV_BOARD[1] ** 2) / 4) - DRV_TAPE  # board back-face plane
DRV_PAD_W = 5.0                                # two printed seat pads under the short edges (flat, 5 x 18 mm)
DRV_PAD_GAP = 0.8                              # pad top -> board back; 1.0 mm foam tape compresses 20 %
DRV_FOAM = 1.0

# --- decoration ---------------------------------------------------------------------------
LOBE_AZ = 42.0                                 # from front (-y) toward +/-x
LOBE_EL = 42.0
LOBE_AXES = (13.0, 9.5, 8.0)                   # semi-axes: tangent-horizontal, tangent-vertical, normal
LOBE_SEAT_SAG = 1.0
M_EL = 37.0                                    # clear of the button opening (top at el 25 deg)
M_W, M_H = 26.0, 17.0
M_PLANE_D = 67.0                               # inlay flat bottom plane (from centre)
M_POCKET_GROW, M_INLAY_SHRINK = 0.25, 0.10      # 0.35 total radial, glued

WEIGHT_DISC = (40.0, 6.0)                      # optional steel disc d x h


def unit(az_from_front_deg, el_deg):
    """Direction on the sphere: azimuth measured from -y (front) toward +x, elevation from equator."""
    a, e = math.radians(az_from_front_deg), math.radians(el_deg)
    return (math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))


def board_to_ball(p):
    x, y, z = p
    return (-y, GLASS_Y + (1.10 - z), x)
