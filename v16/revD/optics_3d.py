#!/usr/bin/env python3
"""Ideal 3D specular mirror coverage; geometric only, NOT brightness."""
import math,json
from dataclasses import dataclass
@dataclass
class Config:
    plate_width:float=82.
    plate_length:float=88.
    plate_y:float=-7.
    plate_z:float=94.
    cover_depth:float=91.
    cover_width:float=104.
    eye_dist:float=600.
    eye_height:float=300.
    yaw:float=0.
def score(m):
    a=math.pi/4;ny=math.cos(a);nz=math.sin(a)
    cx=m.eye_dist*math.tan(math.radians(m.yaw));cy=-m.eye_dist;cz=m.eye_height
    inside=0;total=0
    for ix in range(11):
      for iy in range(11):
        sx=(ix/10-.5)*49.65;sy=(iy/10-.5)*37.22;sz=52.
        projection=(sy-m.plate_y)*ny+(sz-m.plate_z)*nz
        vx=sx;vy=sy-2*projection*ny;vz=sz-2*projection*nz
        denom=(vy-cy)*ny+(vz-cz)*nz
        if abs(denom)<1e-9:continue
        t=((m.plate_y-cy)*ny+(m.plate_z-cz)*nz)/denom
        hx=cx+t*(vx-cx);hy=cy+t*(vy-cy);hz=cz+t*(vz-cz)
        along=(hy-m.plate_y)*math.sin(a)-(hz-m.plate_z)*math.cos(a)
        total+=1
        if (0<=t<=1 and abs(hx)<=m.plate_width/2 and
            abs(along)<=m.plate_length/2 and abs(hx)<=m.cover_width/2 and
            abs(hy)<=m.cover_depth/2 and 54<=hz<=136):inside+=1
    return inside/total if total else 0
def summary():
    cases=[(d,h,y) for d in (500,700) for h in (240,300,360) for y in (-10,0,10)]
    results={}
    for name,m in [('RevC',Config(plate_width=64,plate_length=70,plate_y=0,cover_depth=85)),
                   ('RevD',Config())]:
        values=[]
        for d,h,y in cases:
            m.eye_dist=d;m.eye_height=h;m.yaw=y
            values.append(round(score(m),4))
        results[name]={'mean':round(sum(values)/len(values),4),'minimum':min(values),'values':values}
    results['conditions']=[{'dist_mm':a,'eye_z_mm':b,'yaw_degrees':c} for a,b,c in cases]
    results['warning']='Ideal rays only: no coating, double reflection, scattering, luminance or human visual perception.'
    return results
if __name__=='__main__':
    print(json.dumps(summary(),indent=2,ensure_ascii=False))
