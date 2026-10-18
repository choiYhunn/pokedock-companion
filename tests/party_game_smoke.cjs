// Run: node tests/party_game_smoke.cjs
// Uses only built-in Node modules and mocked DOM; no hardware claim.
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const assert=require("node:assert/strict");
const root=path.resolve(__dirname,"..");
const source=fs.readFileSync(path.join(root,"ui/party-game.js"),"utf8");
const html=fs.readFileSync(path.join(root,"simulator.html"),"utf8");
assert.match(html,/ui\/party-game\.js\?v=9/);
assert.match(html,/ui\/party-game\.css\?v=9/);
assert.match(html,/window\.__pokedockPartyBridge/);
new vm.Script(source);
let selected=94;let pending;
const callbacks={};
const screen={current:null,querySelector(k){return k==="[data-party-root]"?this.current:null},appendChild(v){this.current=v}};
const document={
 getElementById(k){return k==="screen"?screen:null},
 querySelector(k){return k===".homegrid .partner-card"?null:{focus(){},scrollIntoView(){}}},
 addEventListener(k,fn){callbacks[k]=fn},
 createElement(k){
  const n={tagName:k,style:{},classList:{add(){},remove(){}},children:[],
   addEventListener(k,fn){this["on_"+k]=fn},
   querySelector(){return null},querySelectorAll(){return []},
   appendChild(v){this.children.push(v)},remove(){if(screen.current===this)screen.current=null}};
  Object.defineProperty(n,"innerHTML",{set(v){this.html=v;this.firstElementChild=document.createElement("root");this.firstElementChild.html=v},get(){return this.html}});
  return n;
 }
};
const localStorage={getItem(){return null},setItem(){}};
const window={__pokedockPartyBridge:{getPartner:()=>selected,selectPartner:x=>selected=x,getPetTaps:()=>0}};
vm.runInNewContext(source,{window,document,localStorage,
 setTimeout:fn=>(pending=fn,1),clearTimeout:()=>pending=null}, {filename:"party-game.js"});
const game=window.PokeParty;
assert.equal(game.getCharacters().length,8);
game.open();
assert.equal(game.isOpen(),true);
assert.match(screen.current.html,/파트너를 골라줘/);
callbacks.keydown({key:"ArrowDown",preventDefault(){}});
assert.match(screen.current.html,/data-id="393"/);
callbacks.keydown({key:"Enter",preventDefault(){}});
assert.equal(typeof pending,"function");
pending();
assert.equal(selected,393);
assert.equal(game.isOpen(),false);
console.log("PokéDock party selection mock smoke PASS");
