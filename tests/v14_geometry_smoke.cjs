#!/usr/bin/env node
// Verify only algebraic V14 sample envelopes, NOT real stability or charging.
"use strict";
const assert = require("node:assert/strict");
const almost=(a,b,tol=0.11)=>assert.ok(Math.abs(a-b)<=tol,`Expected ${a} ≈ ${b}`);
const phone={L:147.5,W:71.5};
const screen={W:116.3,H:79};
function fit({extraL=6,extraW=6,theta=70,y0=42,screenAngle=76,
              edge=8,rearClearance=22,minDepth=95}={}){
  const L=phone.L+extraL, W=phone.W+extraW;
  const r=theta*Math.PI/180, sa=screenAngle*Math.PI/180;
  const width=Math.max(screen.W+edge*2,L+edge*2);
  const depth=Math.max(minDepth,y0+W*Math.cos(r)+rearClearance);
  return {theta,L,W,width,depth,area:width*depth/100,
          projection:W*Math.cos(r),rise:W*Math.sin(r),
          phoneTop:7+W*Math.sin(r),screenTop:12+screen.H*Math.sin(sa),
          overhang:(L-screen.W)/2};
}
for(const theta of [65,70,75]){
  const f=fit({theta});
  almost(f.projection,77.5*Math.cos(theta*Math.PI/180));
  almost(f.rise,77.5*Math.sin(theta*Math.PI/180));
  assert.ok(f.width>=f.L+16 && f.depth>=95);
}
const sample=fit();
almost(sample.width,169.5,0.01);
almost(sample.depth,95,0.01);
almost(sample.area,161.025,0.01);
almost(sample.projection,26.5065);
almost(sample.rise,72.8262);
almost(sample.overhang,18.6,0.01);
assert.ok(sample.screenTop>sample.phoneTop);
// Baseline change in phone rear support cannot be declared safe from algebra.
const at65=fit({theta:65});
assert.ok(at65.depth>=sample.depth);
console.log("PokéDock V14 sample geometry arithmetic PASS (NOT structural/charging test)");
console.log(JSON.stringify({at65,at70:sample,at75:fit({theta:75})},null,2));
