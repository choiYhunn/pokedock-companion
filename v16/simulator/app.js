/* V16 UI optical preview — original vector stand-ins, NOT Pokémon sprite distribution. */
(()=>{"use strict";
const {Engine,CHARACTERS}=window.GhostEngine,engine=new Engine();
const $=id=>document.getElementById(id);const canvas=$("pokemon-canvas");const ctx=canvas.getContext("2d");
let lastTick=0,lastMotion=0;const descriptions=["유령 친구가 둥둥 떠다닙니다.","뒤뚱거리며 활발하게 등장해요.","가볍게 날아와 휴식을 알려줘요.","집중할 때 응원하는 친구예요.","느긋하게 인사하는 친구예요."];
const setLog=s=>{$("log").textContent=s;}; const setStatus=s=>{$("status").textContent=s;};
function choose(i){engine.selectCharacter(i);sync();renderCharButtons();setLog(CHARACTERS[i].name+" 등장!");}
function renderCharButtons(){const host=$("characters");host.replaceChildren();CHARACTERS.forEach((c,i)=>{const b=document.createElement("button");b.textContent=c.name;b.className=i===engine.character?"active":"";b.addEventListener("click",()=>choose(i));host.append(b);});}
function sync(){const s=engine.snapshot();$("character-name").textContent=s.character.name;$("character-desc").textContent=descriptions[s.characterIndex];$("clock").textContent=s.time;$("clock-sub").textContent="KST";$("focus-display").textContent=String(Math.floor(s.remainingSec/60)).padStart(2,"0")+":"+String(s.remainingSec%60).padStart(2,"0");
setStatus(s.running?"FOCUS":s.paused?"PAUSED":s.motion==="idle"?"IDLE":s.motion.toUpperCase());$("start").textContent=s.paused?"계속하기":s.running?"집중 중":"집중 시작";$("start").disabled=s.running;}
function ellipse(x,y,rx,ry,color){ctx.fillStyle=color;ctx.beginPath();ctx.ellipse(x,y,rx,ry,0,0,Math.PI*2);ctx.fill();}
function path(points,fill,stroke="#66528a",width=2){ctx.beginPath();ctx.moveTo(...points[0]);for(const p of points.slice(1))ctx.lineTo(...p);ctx.closePath();ctx.fillStyle=fill;ctx.fill();if(stroke){ctx.lineWidth=width;ctx.strokeStyle=stroke;ctx.stroke();}}
function eye(x,y,rx=9,ry=6,color="#e9a1b8"){ellipse(x,y,rx,ry,color);}
function paint(c,t){switch(c.id){
case "gengar":
ctx.fillStyle="#8966ba";ctx.strokeStyle="#543e80";ctx.lineWidth=3;
ctx.beginPath();ctx.moveTo(-75,-8);ctx.lineTo(-70,-77);ctx.lineTo(-47,-63);ctx.lineTo(-32,-90);ctx.lineTo(-12,-70);ctx.lineTo(12,-97);ctx.lineTo(28,-68);ctx.lineTo(55,-86);ctx.lineTo(64,-56);ctx.lineTo(80,-49);ctx.quadraticCurveTo(100,35,66,58);ctx.quadraticCurveTo(0,94,-60,57);ctx.quadraticCurveTo(-93,30,-75,-8);ctx.closePath();ctx.fill();ctx.stroke();
eye(-33,-19,18,12);eye(33,-19,18,12);ellipse(-33,-19,5,7,"#4c3a63");ellipse(33,-19,5,7,"#4c3a63");
ctx.beginPath();ctx.moveTo(-50,17);ctx.quadraticCurveTo(0,68,53,15);ctx.lineTo(43,38);ctx.lineTo(31,30);ctx.lineTo(16,42);ctx.lineTo(4,31);ctx.lineTo(-10,43);ctx.lineTo(-25,31);ctx.lineTo(-39,39);ctx.closePath();ctx.fillStyle="#fbf0ff";ctx.fill();break;
case "piplup":
ellipse(0,1,75,85,"#7eafd9");ellipse(0,22,54,57,"#e9efff");
path([[-39,-50],[-55,-111],[-10,-76]],"#5889be");path([[25,-70],[49,-107],[43,-48]],"#5889be");
eye(-28,-31,10,13,"#fbfdff");eye(28,-31,10,13,"#fbfdff");ellipse(-28,-29,5,8,"#304a7f");ellipse(28,-29,5,8,"#304a7f");path([[0,-22],[-14,-6],[0,5],[14,-6]],"#f5c878",null);ellipse(-66,31,25,12,"#84b1d8");ellipse(66,31,25,12,"#84b1d8");break;
case "togekiss":
ellipse(0,5,67,68,"#f5effb");path([[-48,-11],[-127,-29],[-82,30],[-36,26]],"#fff9ff","#d7c8e9");path([[48,-11],[127,-29],[82,30],[36,26]],"#fff9ff","#d7c8e9");path([[-30,-35],[-15,-97],[5,-52]],"#fffafd","#d7c8e9");ellipse(-26,-10,8,11,"#465c71");ellipse(27,-10,8,11,"#465c71");ellipse(-44,16,7,6,"#d0a4c0");ellipse(44,16,7,6,"#d0a4c0");ctx.beginPath();ctx.moveTo(-5,8);ctx.lineTo(4,8);ctx.lineWidth=3;ctx.strokeStyle="#c8a9d6";ctx.stroke();break;
case "lucario":
path([[-57,72],[-52,-17],[-70,-101],[-28,-73],[28,-73],[67,-100],[55,-15],[57,73]],"#7495cb","#3e537d",4);
path([[-26,-59],[26,-59],[38,-14],[24,18],[-23,18],[-37,-14]],"#232f54","#32456e");eye(-21,-28,9,5,"#e6d1d1");eye(21,-28,9,5,"#e6d1d1");ellipse(0,4,14,11,"#253353");ellipse(0,64,32,26,"#d8cae6");break;
case "quagsire":
ellipse(0,10,78,84,"#a3c8d5");ellipse(-55,-58,19,20,"#a3c8d5");ellipse(55,-58,19,20,"#a3c8d5");eye(-27,-23,6,8,"#364d67");eye(27,-23,6,8,"#364d67");ctx.strokeStyle="#536a77";ctx.lineWidth=4;ctx.beginPath();ctx.arc(0,2,18,0,Math.PI);ctx.stroke();ellipse(-66,18,20,11,"#95bdca");ellipse(66,18,20,11,"#95bdca");break;
}
}
function draw(ts){const s=engine.snapshot();const t=engine.reducedMotion?0:ts/1000;ctx.clearRect(0,0,480,480);ctx.save();ctx.translate(240,227);
const phase=s.characterIndex*1.3,breathe=Math.sin(t*2+phase)*6;let dx=0,dy=breathe,r=0,scale=1;
if(!engine.reducedMotion){switch(s.motion){case"hop":dy-=Math.abs(Math.sin(t*9))*62;break;case"dance":r=Math.sin(t*10)*.18;dx=Math.sin(t*6)*21;break;case"peek":dx=Math.cos(t*7)*40;break;case"spin":r=(t*4)%(Math.PI*2);break;case"enter":scale=.85+Math.abs(Math.sin(t*3))*.15;break;case"celebrate":dy-=Math.abs(Math.sin(t*12))*45;break;case"pose":scale=1+Math.sin(t*4)*.04;break;}}
ctx.translate(dx,dy);ctx.rotate(r);ctx.scale(scale,scale);
ellipse(0,93,83,11,"#b59ac71f");paint(s.character,t);ctx.restore();
if(!engine.reducedMotion){for(let i=0;i<9;i++){let x=70+((i*63+ts*.008*(i%3+1))%330),y=80+((i*53+ts*.012*(i%2?1:-1))%290);ctx.globalAlpha=.16+.14*Math.sin(t+i);ellipse(x,y,1.4+(i%2),1.4+(i%2),s.character.accent);}ctx.globalAlpha=1;}
}
function frame(ts){if(ts-lastTick>=180){engine.tick();for(const e of engine.drain()){if(e.type==="focus_complete")setLog("집중 완료! 이제 쉬어도 좋아요.");if(e.type==="alarm_fire"){setLog("알람 시간이 되었어요.");if(!engine.muted)beep();}}sync();lastTick=ts;}draw(ts);requestAnimationFrame(frame);}
let audio=null;function beep(){try{audio=audio||new(window.AudioContext||window.webkitAudioContext)();const osc=audio.createOscillator(),gain=audio.createGain();osc.type="sine";osc.frequency.value=650;gain.gain.value=.035;osc.connect(gain).connect(audio.destination);osc.start();osc.stop(audio.currentTime+.2);}catch(e){setLog("브라우저 오디오가 차단되어 알람은 시각적으로만 표시합니다.");}}
$("interact").onclick=()=>{engine.interact();setLog("반응 애니메이션 실행");};
$("switch").onclick=()=>choose((engine.character+1)%CHARACTERS.length);
$("knob").onclick=()=>$("switch").click();$("knob").onkeydown=e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();$("switch").click();}};
document.querySelectorAll("[data-min]").forEach(b=>b.addEventListener("click",()=>{try{engine.setFocus(Number(b.dataset.min));document.querySelectorAll("[data-min]").forEach(x=>x.classList.toggle("selected",x===b));sync();}catch(e){setLog("먼저 진행 중인 타이머를 종료하세요.");}}));
$("start").onclick=()=>{if(engine.paused)engine.resume();else engine.start();sync();};
$("pause").onclick=()=>{engine.pause();sync();};$("stop").onclick=()=>{engine.stop();sync();};
$("alarm-at").onchange=()=>{try{engine.setAlarm($("alarm-at").value,$("alarm-enabled").checked);}catch(e){setLog("알람 시간을 확인하세요.");}};
$("alarm-enabled").onchange=()=>$("alarm-at").onchange();
$("sound").onchange=()=>{engine.muted=!$("sound").checked;if(!engine.muted)beep();};
$("reduce").onchange=()=>{engine.reducedMotion=$("reduce").checked;};$("mirror").onchange=()=>{canvas.style.transform=$("mirror").checked?"scaleX(-1)":"none";};
$("update").onclick=()=>{setLog("업데이트는 시뮬레이터에서 수행되지 않습니다. 실제 장치 OTA는 별도 하드웨어 및 보안 검증 후 연결합니다.");};
renderCharButtons();engine.setFocus(25);engine.stop();sync();requestAnimationFrame(frame);
})();
