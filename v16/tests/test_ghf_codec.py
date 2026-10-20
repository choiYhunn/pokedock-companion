import importlib.util, random, tempfile
from pathlib import Path
from PIL import Image
src=Path(__file__).parent.parent/'tools'/'ghf_codec.py'
spec=importlib.util.spec_from_file_location('codec',src)
codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)
for w,h in [(1,1),(11,13),(64,64),(256,256)]:
    im=Image.new('RGBA',(w,h));rand=random.Random(2026);pixels=[]
    for j in range(w*h):
        if j%13<7:pixels.append((0,0,0,0))
        elif j%13<10:pixels.append((120,20,200,255))
        else:pixels.append((rand.randrange(256),rand.randrange(256),rand.randrange(256),255))
    im.putdata(pixels);dat=codec.frame_bytes(im,w,h)
    ww,hh,got=codec.decode_bytes(dat)
    expected=[None if a<64 else codec.rgb565(r,g,b) for r,g,b,a in pixels]
    assert (ww,hh)==(w,h) and got==expected
    for bad in [dat[:8],dat+b'junk',dat[:12]+bytes([127,0])]:
        try:codec.decode_bytes(bad)
        except ValueError:pass
        else:raise AssertionError('accepted invalid stream')
print('GHF1 roundtrip + corruption PASS')
with tempfile.TemporaryDirectory() as tmp:
    im=Image.new('RGBA',(64,64),(0,0,0,0))
    for x in range(12,48):
        for y in range(7,53):im.putpixel((x,y),(120,35,169,255))
    inp=Path(tmp)/'test.png';im.save(inp);out=Path(tmp)/'out'
    m=codec.pack(inp,out,'gengar',64,64,12,120)
    assert m['frame_count']==1 and m['total_bytes']<8192
print('GHF1 manifest + fixture PASS')
