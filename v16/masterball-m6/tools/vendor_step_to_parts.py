"""Extract per-component STLs + parts.json from the official Waveshare 1.43 STEP (download it yourself:
https://files.waveshare.com/wiki/ESP32-S3-Touch-AMOLED-1.43/ESP32-S3-Touch-AMOLED-1.43-3DFile.zip).
usage: python vendor_step_to_parts.py <ESP32-S3-Touch-AMOLED-1_43.stp> <out_dir>   (vendor files are not redistributed)
"""
import json
import os
import sys

from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDF import TDF_Label
from OCP.TDataStd import TDataStd_Name
from OCP.collections import Sequence_TDF_Label
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.TopLoc import TopLoc_Location

step, outdir = sys.argv[1:3]
os.makedirs(outdir, exist_ok=True)
doc = TDocStd_Document(TCollection_ExtendedString("doc"))
rd = STEPCAFControl_Reader()
rd.SetNameMode(True)
assert rd.ReadFile(step) == 1
rd.Transfer(doc)
st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())


def s_(obj, name):
    return getattr(obj, name + "_s", None) or getattr(obj, name)


def name_of(label):
    attr = TDataStd_Name()
    if label.FindAttribute(TDataStd_Name.GetID_s(), attr):
        return attr.Get().ToExtString()
    return "?"


def bbox(shape):
    b = Bnd_Box()
    BRepBndLib.Add_s(shape, b, True)
    if b.IsVoid():
        return None
    lo, hi = b.CornerMin(), b.CornerMax()
    return [round(v, 3) for v in (lo.X(), lo.Y(), lo.Z(), hi.X(), hi.Y(), hi.Z())]


rows = []
KEEP = ("PMMA", "DO0143", "PCB", "TYPE-C", "HP1_25", "TF_CARD", "MICRO_SD", "PITCH1MM", "2X7", "U_FL", "SWITCHER", "SMTSO", "_7_AF0", "BOARD")


def walk(label, loc, path):
    nm = name_of(label)
    if s_(st, "IsReference")(label):
        ref = TDF_Label()
        s_(st, "GetReferredShape")(label, ref)
        walk(ref, loc.Multiplied(s_(st, "GetLocation")(label)), path)
        return
    if s_(st, "IsAssembly")(label):
        kids = Sequence_TDF_Label()
        s_(st, "GetComponents")(label, kids, False)
        for i in range(1, kids.Length() + 1):
            walk(kids.Value(i), loc, path + [nm])
        return
    shape = s_(st, "GetShape")(label).Moved(loc)
    full = "/".join(path[1:] + [nm])
    bb = bbox(shape)
    if bb is None:
        return
    rows.append({"path": full, "bbox": bb})
    tag = next((k for k in KEEP if k in full.upper()), None)
    if tag:
        BRepMesh_IncrementalMesh(shape, 0.05, False, 0.3, True)
        StlAPI_Writer().Write(shape, os.path.join(outdir, f"{len(rows):03d}_{tag}.stl"))


roots = Sequence_TDF_Label()
st.GetFreeShapes(roots)
for i in range(1, roots.Length() + 1):
    walk(roots.Value(i), TopLoc_Location(), [])
json.dump(rows, open(os.path.join(outdir, "parts.json"), "w"), indent=1)
for r in rows:
    if any(k in r["path"].upper() for k in KEEP):
        x0, y0, z0, x1, y1, z1 = r["bbox"]
        print(f'{r["path"][-58:]:58s} x[{x0:7.2f},{x1:7.2f}] y[{y0:7.2f},{y1:7.2f}] z[{z0:6.2f},{z1:6.2f}]')
