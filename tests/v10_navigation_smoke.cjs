const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const root = path.resolve(__dirname, "..");
const html = fs.readFileSync(path.join(root, "simulator.html"), "utf8");
const code = html.match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(code);
let now = Date.now(), tick=null, onClick=null;
const nodes={};
function node(id){
 if(nodes[id])return nodes[id];
 const flags=new Set();
 return nodes[id]={innerHTML:"",value:"",textContent:"",style:{},
  classList:{toggle(k){if(flags.has(k))flags.delete(k);else flags.add(k)},contains:k=>flags.has(k)}};
}
const document={
 documentElement:{style:{setProperty(){}}},
 getElementById:node,querySelectorAll:()=>[],
 querySelector:()=>({requestFullscreen(){}}),
 addEventListener:(event,fn)=>{if(event==="click")onClick=fn}
};
const kv=new Map();
const storage={getItem:key=>kv.get(key)||null,setItem:(key,val)=>kv.set(key,val)};
class Clock extends Date{static now(){return now}}
new Function("document","localStorage","window","setInterval","location","Date",code)(
 document,storage,{},fn=>tick=fn,{reload(){}},Clock);
function click(action,id){onClick({target:{closest:()=>({dataset:{action,id}})}})}
function page(screen){onClick({target:{closest:()=>({dataset:{screen}})}})}
function shown(v){return node("screen").innerHTML.includes(v)}
assert(shown("바로 집중하기"));
click("drawer");assert(shown("매일 쓰는 도구"));assert(shown("포켓몬 놀이"));
click("menu-group","play");assert(shown("파트너 선택"));
page("dex");click("back");assert(shown("파트너 선택"));
click("back");assert(shown("매일 쓰는 도구"));
click("back");assert(!shown("매일 쓰는 도구"));
page("focus");assert(shown("25분 집중 / 5분 휴식"));
click("focus-toggle");now+=1500*1000;tick();
assert(shown("도감에 기록"));
click("reward-later");assert(!shown("도감에 기록"));
click("drawer");click("menu-group","play");assert(shown("기록 대기"));
click("show-pending");assert(shown("도감에 기록"));
click("register");assert(shown("Vulpix"));assert(shown("No.037"));
const data=JSON.parse(kv.get("pokedock-v10-game"));assert(data.caught.includes(37));
click("back");assert(shown("잠깐 휴식"));
click("focus-toggle");now+=300*1000;tick();assert(shown("공부 집중"));
console.log("V10 menu/timer/back/reward mock smoke PASS");
