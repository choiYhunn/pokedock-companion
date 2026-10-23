#!/usr/bin/env python3
"""V16 GHF1 private animation frame encoder. Requires Pillow; no Pokémon assets included.
Header: GHF1 + width/height uint16 LE + payload_size uint32 LE.
Ops: 0..127 literal length+1 RGB565LE; 128..191 transparent len=(op&63)+1;
192..255 single-color run len=(op&63)+1 plus RGB565LE.
"""
import argparse, hashlib, json, struct
from pathlib import Path
from PIL import Image, ImageSequence
MAX_DIM=480
MAX_FRAMES=480
MAX_BYTES=24*1024*1024
def rgb565(r,g,b):
    return (r>>3)<<11 | (g>>2)<<5 | (b>>3)
def frame_bytes(frame,width,height,alpha_cutoff=64,resample='smooth'):
    if resample not in ('smooth','pixel'):raise ValueError('resample')
    alg=Image.Resampling.NEAREST if resample=='pixel' else Image.Resampling.LANCZOS
    rgba=frame.convert('RGBA').resize((width,height),alg)
    px=[None if a<alpha_cutoff else rgb565(r,g,b) for r,g,b,a in rgba.getdata()]
    out=bytearray();i=0
    while i<len(px):
        color=px[i]
        if color is None:
            n=1
            while i+n<len(px) and n<64 and px[i+n] is None:n+=1
            out.append(0x80|(n-1));i+=n;continue
        n=1
        while i+n<len(px) and n<64 and px[i+n]==color:n+=1
        if n>=3:
            out.append(0xC0|(n-1));out.extend(struct.pack('<H',color));i+=n;continue
        seq=[]
        while i<len(px) and len(seq)<128:
            if px[i] is None:break
            candidate=px[i];same=1
            while i+same<len(px) and same<3 and px[i+same]==candidate:same+=1
            if same>=3:break
            seq.append(candidate);i+=1
        if not seq:
            out.append(0xC0|(n-1));out.extend(struct.pack('<H',color));i+=n
        else:
            out.append(len(seq)-1)
            for v in seq:out.extend(struct.pack('<H',v))
    return b'GHF1'+struct.pack('<HHI',width,height,len(out))+bytes(out)
def decode_bytes(data):
    if len(data)<12 or data[:4]!=b'GHF1':raise ValueError('magic')
    w,h,sz=struct.unpack_from('<HHI',data,4)
    if not (1<=w<=MAX_DIM and 1<=h<=MAX_DIM and sz==len(data)-12):raise ValueError('size')
    out=[];i=12
    while i<len(data):
        op=data[i];i+=1
        if op<0x80:
            n=op+1;end=i+n*2
            if end>len(data):raise ValueError('literal truncated')
            out.extend(struct.unpack_from('<'+'H'*n,data,i));i=end
        elif op<0xC0:out.extend([None]*((op&0x3F)+1))
        else:
            if i+2>len(data):raise ValueError('solid truncated')
            c=struct.unpack_from('<H',data,i)[0];i+=2
            out.extend([c]*((op&0x3F)+1))
        if len(out)>w*h:raise ValueError('overflow')
    if len(out)!=w*h:raise ValueError('decoded length')
    return w,h,out
def pack(src_path,dest,character,width,height,fps,limit,resample='smooth'):
    if not(1<=width<=MAX_DIM and 1<=height<=MAX_DIM):raise ValueError('dimensions')
    if not(1<=fps<=30 and 1<=limit<=MAX_FRAMES):raise ValueError('fps or frame limit')
    if character not in ('gengar','piplup','togekiss','lucario','quagsire'):raise ValueError('character')
    dest.mkdir(parents=True,exist_ok=True)
    src=Image.open(src_path);frames=[];total=0
    for i,frame in enumerate(ImageSequence.Iterator(src)):
        if i>=limit:break
        blob=frame_bytes(frame,width,height,resample=resample)
        assert decode_bytes(blob)[:2]==(width,height)
        total+=len(blob)
        if total>MAX_BYTES:raise ValueError('pack too large')
        name=f'{character}_{i:04d}.ghf';(dest/name).write_bytes(blob)
        duration=int(frame.info.get('duration') or 1000/fps)
        duration=max(33,min(1000,duration))
        frames.append({'name':name,'duration_ms':duration,'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest()})
    if not frames:raise ValueError('no frames')
    manifest={'format':'ghost-ghf1','schema':1,'character':character,'resolution':[width,height],'frame_count':len(frames),'total_bytes':total,'render_style':resample,'frames':frames}
    (dest/f'{character}_index.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    return manifest
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output_dir',type=Path)
    p.add_argument('--character',choices=['gengar','piplup','togekiss','lucario','quagsire'],required=True)
    p.add_argument('--width',type=int,default=256);p.add_argument('--height',type=int,default=256)
    p.add_argument('--fps',type=int,default=12);p.add_argument('--max-frames',type=int,default=120)
    p.add_argument('--resample',choices=['pixel','smooth'],default='smooth')
    a=p.parse_args();m=pack(a.input,a.output_dir,a.character,a.width,a.height,a.fps,a.max_frames,a.resample)
    print('GHF1 converted',m['frame_count'],'frames',m['total_bytes'],'bytes')
