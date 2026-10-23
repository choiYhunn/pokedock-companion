const fs=require('node:fs');const path=require('node:path');const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..');const original=fs.readFileSync(path.join(root,'simulator.html'),'utf8');const mobile=fs.readFileSync(path.join(root,'mobile/index.html'),'utf8');const lab=fs.readFileSync(path.join(root,'v16/character-lab/index.html'),'utf8');
for(const keyword of ['secretTaps>=5','birthday-demo','pokedock-v10-game','our-space','focusRun','alarm','egg','trainer','dex','reviewBtn']){assert(original.includes(keyword),keyword+' missing original');assert(mobile.includes(keyword),keyword+' missing mobile')}
assert(mobile.includes('../ui/party-game.js?v=9'));assert(mobile.includes('../ui/party-game.css?v=9'));
assert(mobile.includes("localStorage.setItem(MOBILE_ALARM_KEY"));assert(mobile.includes('mobileForegroundAlarm'));
assert(lab.includes('gengarSneak')&&lab.includes('piplupHop')&&lab.includes('togekissGlide')&&lab.includes('lucarioStance')&&lab.includes('quagsireWobble'));
for(const id of [94,393,468,448,195,175,417,385])assert(lab.includes(String(id)));
function scripts(text){const found=[];const re=/<script>([\s\S]*?)<\/script>/g;let match;while((match=re.exec(text)))found.push(match[1]);return found}
for(const [name,html] of [['original',original],['mobile',mobile],['animationLab',lab]]){const sc=scripts(html);assert(sc.length>0,name+' script missing');for(const js of sc)new Function(js);}
JSON.parse(fs.readFileSync(path.join(root,'mobile/manifest.webmanifest'),'utf8'));
new Function(fs.readFileSync(path.join(root,'mobile/sw.js'),'utf8'));
console.log('PASS: original V10 UI/easter eggs/party preserved; mobile scripts and animation lab JS parse');
