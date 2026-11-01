"""PokéDock M7 openable Master Ball: single source of truth for mechanical parameters (mm).

Frame: origin = closed-ball centre, +x right, +y BACK (hinge side), +z up. The user sits at -y.
Pod frame "U" (same convention as the M6 ball frame, origin at the glass-top centre):
  x_u = -step_y, y_u = 1.10 - step_z (depth behind the glass top), z_u = step_x (screen up; USB-C points -z_u).
U -> ball: rotate about +x by POD_ROT_DEG, then translate by POD_C. The screen plane is then
SCREEN_TILT_DEG from the desk and faces the user (normal (0, -sin, cos)).
"""
import math

# --- sphere and parting -------------------------------------------------------------------
R = 69.0                    # 138 mm ball, same as M6 (fits a 180 mm cube printer per half)
WALL_LID = 2.0             # lighter lid: the open lid sits behind the pivot and drives the tip margin
WALL_LOW = 2.8
RI_LID = R - WALL_LID       # 67.0
RI_LOW = R - WALL_LOW       # 66.2
BH = 5.25                   # belt half height: 10.5 mm dark band (concept photo ~10.5 mm); lid sits on z = +5.25
BASE_Z = -60.0              # flat base d75 (M6: -61 / d73): wider support for the open lid, 45 deg cone tangent
FOOT_TANGENT_Z = -R / 2 ** 0.5
FOOT_R_AT_BASE = -FOOT_TANGENT_Z - (FOOT_TANGENT_Z - BASE_Z)
FLOOR_T = 3.0
FEET_R, FEET_N, FEET_D = 33.0, 8, 8.0    # silicone bumpers d8, one exactly at the back (az 180)

# --- belt (black) -------------------------------------------------------------------------
BELT_BORE_R = 62.0
SPIGOT_R_OUT = math.sqrt(RI_LOW ** 2 - (BH + 4.0) ** 2) - 0.35   # 65.42: the sphere narrows below the rim
SPIGOT_R_IN = BELT_BORE_R
SPIGOT_Z0 = -BH - 4.0                    # -7.5

# --- hinge --------------------------------------------------------------------------------
PIVOT_Y = R + 1.0                        # 70.0: axis 1 mm outside the sphere -> lid rim rises from 0 deg
PIVOT_Z = BH + 4.0                       # 7.5: lid knuckle (r 4) tangent to the lid print bed z = 3.5
KNUCKLE_R = 4.0
PIN_D = 3.0                              # ISO 2338 dowel pin d3 x 30, stainless
PIN_L = 30.0
PIN_PRESS_D = 2.90                       # outer (belt) knuckles: press fit, ream to 2.95-3.0 if tight
PIN_RUN_D = 3.30                         # centre (lid) knuckle: running fit
LID_KNUCKLE_HALF = 7.0                   # lid knuckle |x| <= 7.0
KNUCKLE_GAP = 0.4
BELT_KNUCKLE_X = (LID_KNUCKLE_HALF + KNUCKLE_GAP, LID_KNUCKLE_HALF + KNUCKLE_GAP + 8.0)   # 7.4..15.4
LID_NOTCH_R = KNUCKLE_R + 0.6            # lid material keeps >= 0.6 mm from the belt knuckles
OPEN_DEG = 110.0                         # mechanical stop
# Stop: a lug on the lid knuckle (radial sector, angles measured around the pivot from +y in the
# y-z plane) meets a matching radial face on the belt "heel" exactly at OPEN_DEG (face contact).
STOP_FACE_DEG = -48.6                    # heel face direction (back and down from the pivot)
STOP_LUG_SPAN = 25.0
STOP_LUG_ANG0 = STOP_FACE_DEG + OPEN_DEG # 61.4: lug leading face in the closed lid
STOP_LUG_R = (KNUCKLE_R - 0.5, 6.2)
STOP_HEEL_R = (KNUCKLE_R + 0.35, 7.6)
STOP_HALF_X = 6.6
STOP_SHELF_Z = (-BH, -BH + 2.0)          # belt shelf under the separate, screwed stop block
STOP_BLOCK_Y = (66.0, 75.6)
STOP_SCREW_Y = 72.6                      # 2 x M2 PT x 8 from below, behind the sphere (y > R)
STOP_SCREW_X = 3.6

# --- lid sensor (required): Littelfuse 59155-1-S-02-A reed sensor + 57155-000 actuator -------
SENSOR_AZ = -90.0                        # left side; 55 deg from the nearest latch magnet
SENSOR_BOX = (12.7, 9.0, 3.0)            # tangential, radial, height (datasheet 12.70 x 9.00 x 3.00)
ACTUATOR_BOX = (12.7, 9.0, 3.0)          # assumed same envelope: CHECK on the fit-6 coupon before the final print
SENSOR_R = 62.0                          # radial centre of both pockets
SENSOR_SKIN = 0.6                        # belt top skin over the sensor -> ~0.6-1 mm gap closed (operate ~4 mm)
SENSOR_FIT = 0.25

# --- magnets (closing latch): N35 disc 6 x 2, two pairs ------------------------------------
MAG_D, MAG_H = 6.0, 2.0
MAG_POCKET_D, MAG_POCKET_H = 6.2, 2.1    # glued (CA), faces flush; polarity marked before gluing
MAG_R = 64.5
MAG_AZ = (-35.0, 35.0)                   # from front (-y) toward +x
MAG_BOSS_D = 10.0

# --- front button (decorative, white) ------------------------------------------------------
BTN_RING_OD, BTN_RING_ID = 34.0, 24.4     # photo: ring ~34 mm, white button ~23.6 mm
BTN_Z = BH - BTN_RING_OD / 2 - 0.1        # ring top just under the lid rim (photo), no lid notch
BTN_D, BTN_PROUD = 23.6, 5.0              # white button, domed, front 5.0 mm proud of the sphere (photo: clearly 3D)
BTN_DOME = 1.8                            # dome rise of the button face
BTN_RING_PROUD = 2.4
BTN_RING_PEG_R = 14.6

# --- ears (pink) --------------------------------------------------------------------------
EAR_AZ = 48.0                            # +/- from the front
EAR_EL = 58.0                            # high enough that the d28 seat boss stays above the liner
# Variant B = ear position read from the concept photo (ears stand up on the OPEN lid -> upper-front of
# the lid). Select with environment variable M7_EAR_VARIANT=B; the owner picks A or B at the
# appearance gate (appearance/APPROVAL.json).
import os as _os
EAR_VARIANT = _os.environ.get("M7_EAR_VARIANT", "A").upper()
if EAR_VARIANT == "B":
    EAR_AZ, EAR_EL = 36.0, 22.0
EAR_SEAT_DEPTH = 1.6                     # flat seat below the sphere (sag of a d28 seat is 1.44)
EAR_BASE_D, EAR_H, EAR_TIP_R = 28.0, 18.0, 8.0   # gumdrop cat ear (profile build_m7.EAR_SHAPE); tip radius ~8 equivalent
EAR_FLAT = 0.82                          # cross-section flattened along the meridian -> reads as an ear, not a cone
EAR_TILT_OUT = 12.0                      # tilted outward from the surface normal
EAR_PEG_D, EAR_PEG_L = 6.0, 5.0
EAR_SEAT_CLEAR = 0.3

# --- lid liner (hides the support-scarred dome top; 2 visible M2 screws as in the photo) ---
LINER_Z = (44.4, 46.0)                   # 1.6 mm
LINER_SCREW_X = 30.0

# --- display pod --------------------------------------------------------------------------
SCREEN_TILT_DEG = 55.0                   # from the desk: upper end of the 45-55 spec, closest to the upright screen in the photo
POD_ROT_DEG = -(90.0 - SCREEN_TILT_DEG)  # rotation of U about +x
POD_C = (0.0, -12.0, 14.0)               # glass-top centre in the ball frame
GLASS_R = 23.0
ACTIVE_R = 36.75 / 2
GLASS_TO_STANDOFF = 10.22                # glass top -> standoff end (official STEP z +1.10 -> -9.12)
STANDOFFS_XZ = [(sx * 15.75, sz * 11.60) for sx in (-1, 1) for sz in (-1, 1)]   # U x, z (M6 verified)
HEADER_WIN = (13.2, 19.3, 5.4)           # |x_u| range and |z_u| half height of the 2x7 header windows
KEYS_XZ = [(-17.25, 7.5), (-17.25, -7.5)]
KEY_WIN = (7.0, 12.5)
LIP_GAP = 0.6                            # glass top -> bezel lip (no load on the glass)
LIP_T = 2.0
BEZEL_OR = 31.0                          # d62 stepped bezel (photo surround ~62 mm + side brackets ~70 mm)
BEZEL_BORE_R = GLASS_R + 0.5
WINDOW_R = 19.3
PLATE_T = 2.5
PLATE_Y0 = GLASS_TO_STANDOFF             # plate front face = standoff ends
BEZEL_SCREW_R = 26.1
BEZEL_SCREW_ANG = (90.0, 210.0, 330.0)   # around the screen axis from +x_u
M2_PT_PILOT = 1.7
M2_CLEAR = 2.3
M3_PT_PILOT = 2.5
M3_CLEAR = 3.4
USB_OPEN = (7.0, 3.4, 12.0)              # cup-wall opening for the plug: |x_u| <= 7.0, y_u 3.4..12.0

# Right-angle USB-C adapter (Adafruit 4432, 23.7 x 19.0 x 6.0 mm) in U: plug axis -z_u from the mouth
USB_MOUTH_ZU = -22.5
USB_YU = (4.4, 10.4)
USB_ADAPTER = (19.0, 23.7, 9.0)          # leg along -z_u, leg along +x_u (turn direction set at fit), width

# --- deck (lavender floor that hides the electronics) ---------------------------------------
DECK_TOP_Z = -9.0                        # inner cover (tray) floor top
DECK_T = 2.0
TRAY_R = 61.4                            # must pass the belt spigot bore (r 62) when it goes in
TRAY_WALL_R = (51.6, 53.2)               # lavender inner wall (photo) with 2.8 mm for the reed leads outside it
TRAY_LIP_TOP = BH - 0.6                  # lavender rim lip just below the lid rim
TRAY_LIP_T = 1.0
SHROUD_Y1, SHROUD_T = 24.0, 1.6           # back shroud: the pod reads as one solid pedestal (photo), wires inside
WING_X = (31.4, 34.4)                    # cradle side brackets beside the bezel (U frame |x|)
WING_TAB_Y = (-24.5, -15.5)              # bracket feet on the tray floor (ball y), visible M3 screws like the photo
WING_SCREW = (35.0, -20.0)          # nut stays clear of the USB extension plug under the floor
DECK_CLEAR = 0.8                          # around the pod where it passes through
DECK_SCREW_R, DECK_SCREW_ANG = 48.0, (30.0, 150.0, 270.0)   # inside the tray wall; the back (90) holds the USB port
FOOT_T = 3.0
FOOT_Y = (16.0, 34.0)                     # cradle foot slab on the deck (ball y range)
FOOT_HALF_X = 20.0
FOOT_SCREW_X = 14.0
CABLE_HOLE = (12.0, 9.0)                  # deck hole for the J1 harness behind the plate (x, y)

# --- rear USB-C panel port (option B: board's own USB-C via right-angle adapter + extension) --
PORT_EL = -28.0                           # elevation at the back (az 180)
PORT_HOLE_D = 22.0                        # Adafruit 4218 needs 21.5..27 mm
PORT_FLAT_D = 34.0                        # flat spot-face for the nut

# --- buzzer and driver (M6 values reused) ---------------------------------------------------
BUZ_AZ, BUZ_EL = 140.0, -24.0
BUZ_D, BUZ_H, BUZ_FIT = 12.0, 9.5, 0.6
DRV_AZ, DRV_EL = -110.0, -30.0
DRV_BOARD = (24.0, 18.0, 10.0)

# --- weight -------------------------------------------------------------------------------
WEIGHT_D, WEIGHT_H = 60.0, 12.0           # 3 x ISO 7093-1 M20 large washers (d60 x 4, ~78 g each), glued in the floor pocket

FIT_PRINT = 0.35


def unit(az_from_front_deg, el_deg):
    a, e = math.radians(az_from_front_deg), math.radians(el_deg)
    return (math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))


def u_to_ball(p):
    """U frame point -> ball frame point."""
    x, y, z = p
    t = math.radians(POD_ROT_DEG)
    return (x + POD_C[0], y * math.cos(t) - z * math.sin(t) + POD_C[1], y * math.sin(t) + z * math.cos(t) + POD_C[2])


def step_to_u(p):
    x, y, z = p
    return (-y, 1.10 - z, x)


def lid_rot(p, deg):
    """Rotate a ball-frame point with the lid by `deg` (opening, front rim goes up)."""
    x, y, z = p
    t = math.radians(deg)
    dy, dz = y - PIVOT_Y, z - PIVOT_Z
    return (x, PIVOT_Y + dy * math.cos(t) + dz * math.sin(t), PIVOT_Z - dy * math.sin(t) + dz * math.cos(t))
