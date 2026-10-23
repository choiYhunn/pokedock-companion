
import importlib.util,tempfile
from pathlib import Path
from PIL import Image
src=Path(__file__).parent.parent/'tools'/'ghf_codec.py'
spec=importlib.util.spec_from_file_location('codec',src)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
im=Image.new('RGBA',(2,2),(0,0,0,0))
im.putpixel((0,0),(92,18,156,255));im.putpixel((1,1),(0,0,0,255))
for style in ('pixel','smooth'):
 blob=mod.frame_bytes(im,16,16,resample=style)
 w,h,pixels=mod.decode_bytes(blob)
 assert (w,h)==(16,16)
 assert any(x is None for x in pixels)
 assert any(x==0 for x in pixels),'opaque black should exist'
with tempfile.TemporaryDirectory() as d:
 f=Path(d)/'sample.gif'
 im.save(f)
 out=mod.pack(f,Path(d)/'dst','gengar',16,16,12,8,resample='pixel')
 assert out['render_style']=='pixel'
print('PASS: GHF nearest-neighbor pixel quality and alpha-mask roundtrip')
