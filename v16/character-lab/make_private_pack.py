#!/usr/bin/env python3
"""Personal, on-demand converter for the SAME official sprites referenced by PokéDock V10.
Does not commit or publish copyrighted sprites to the project.
pip install pillow
python v16/character-lab/make_private_pack.py --out ./my-private-sdcard --resolution 128
"""
import argparse, json, hashlib, sys
import urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from ghf_codec import pack

FAVORITES={94:'gengar',393:'piplup',468:'togekiss',448:'lucario',195:'quagsire'}
BASE='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/'
def download(url,dst,max_bytes=8*1024*1024):
    req=urllib.request.Request(url,headers={'User-Agent':'PokeDock-private-prototype/1.0'})
    with urllib.request.urlopen(req,timeout=25) as source:
        mime=source.headers.get('Content-Type','')
        if not (mime.startswith('image/') or url.endswith(('.gif','.png'))):
            raise RuntimeError('not image content: '+mime)
        data=source.read(max_bytes+1)
    if not data or len(data)>max_bytes:raise RuntimeError('empty or large source')
    dst.write_bytes(data)
    return hashlib.sha256(data).hexdigest()
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--resolution',type=int,choices=(96,128,160,192),default=128)
    p.add_argument('--fps',type=int,choices=(8,12,15,24),default=12)
    p.add_argument('--source',choices=('pixel','art'),default='pixel')
    p.add_argument('--only',choices=tuple(FAVORITES.values()),default=None)
    a=p.parse_args()
    root=a.out.resolve();root.mkdir(parents=True,exist_ok=True)
    records=[]
    for id,name in FAVORITES.items():
        if a.only and name!=a.only:continue
        ext='gif' if a.source=='pixel' else 'png'
        sub=root/name;sub.mkdir(exist_ok=True)
        src=sub/('original.'+ext)
        url=BASE+(f'versions/generation-v/black-white/animated/{id}.gif' if a.source=='pixel' else f'other/official-artwork/{id}.png')
        print('Download',name,url)
        digest=download(url,src)
        # NOTE: a PNG "art" source is a still illustration, not a new animation.
        output=sub/'ghf';out=pack(src,output,name,a.resolution,a.resolution,a.fps,120,resample='pixel' if a.source=='pixel' else 'smooth')
        records.append({'name':name,'id':id,'source_sha256':digest,'source_url':url,
                        'style':a.source,'GHF_frame_count':out['frame_count'],'bytes':out['total_bytes']})
    (root/'BUILD_REPORT.json').write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding='utf-8')
    print('Private assets prepared. DO NOT COMMIT',root)
if __name__=='__main__':main()
