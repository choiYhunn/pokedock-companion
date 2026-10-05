const POKE=id=>`https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${id}.png`;

const screens=[
{id:'home',label:'HOME',purpose:'항상 켜두는 기본 화면'},
{id:'focus',label:'FOCUS',purpose:'Pomodoro / 집중 세션'},
{id:'timer',label:'TIMER',purpose:'일반 카운트다운'},
{id:'stopwatch',label:'STOPWATCH',purpose:'Lap 스톱워치'},
{id:'today',label:'TODAY',purpose:'할 일 / D-day / 오늘 기록'},
{id:'stats',label:'STATS',purpose:'주간 공부 통계'},
{id:'dex',label:'DEX',purpose:'공부 보상 / NFC 캐릭터'},
{id:'nfc',label:'NFC',purpose:'측면 태그/피규어 인식'},
{id:'weather',label:'WEATHER',purpose:'날씨 / 환경 정보'},
{id:'alarm',label:'ALARM',purpose:'알람 관리'},
{id:'phone',label:'PHONE',purpose:'후면 폰 / 중요 알림'},
{id:'light',label:'LIGHT',purpose:'무드등 테마'},
{id:'settings',label:'SETTINGS',purpose:'기기 설정'},
{id:'birthday',label:'BIRTHDAY',purpose:'생일 Secret Event'},
{id:'night',label:'NIGHT',purpose:'야간 저휘도 모드'}
];

const state={
screen:'home',phoneParked:true,dark:false,priority:false,nfc:false,birthday:false,
focusRemaining:1458,focusRunning:false,countdown:600,countdownRunning:false,
stopwatch:1938.4,stopwatchRunning:false,laps:['32:18.4','21:04.8','10:12.1']
};

let tickTimer=null;

function nav(active){
 const tabs=['HOME','FOCUS','TOOLS','TODAY','DEX'];
 return `<div class="pk-bottom">${tabs.map(t=>`<span class="pk-tab ${active===t?'on':''}">${t}</span>`).join('')}</div>`;
}
function top(status='Wi‑Fi ●'){
 return `<div class="pk-top"><div class="pk-brand">POKÉDOCK</div><div class="pk-status"><span>${status}</span><span>23°C</span><span>${state.phoneParked?'PHONE ●':'PHONE ○'}</span></div></div>`;
}
function overlay(){
 if(!state.priority)return '';
 return `<div class="pk-overlay"><b>CALENDAR · 중요 알림</b><span>15분 뒤 일정이 있어요</span></div>`;
}
function shell(body,active='HOME',dark=false,status){
 return `<div class="pk-screen ${dark?'dark':''}">${top(status)}<div class="pk-body">${body}</div>${nav(active)}${overlay()}</div>`;
}
function fmt(sec){
 sec=Math.max(0,Math.floor(sec)); const m=Math.floor(sec/60),s=sec%60;
 return `${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
}
function renderHome(){
 return shell(`<div class="pk-grid pk-home"><div class="pk-card pk-hero"><div class="pk-time">14:36</div><div class="pk-date">10월 5일 · 월요일</div><img class="pk-char" src="${POKE(468)}"><div class="pk-message">오늘도 차근차근.<small>토게키스가 오늘 계획을 정리했습니다.</small></div></div><div class="pk-stack"><div class="pk-card pk-mini"><b>오늘 공부</b><span>1h 45m · 목표 3h</span></div><div class="pk-card pk-mini"><b>D‑DAY</b><span>확률 과제 · D‑4</span></div><div class="pk-card pk-mini"><b>날씨</b><span>18°C · 맑음</span></div><div class="pk-card pk-mini"><b>다음</b><span>전자회로 복습 25분</span></div></div></div>`,'HOME',state.dark);
}
function renderFocus(){
 return shell(`<div class="pk-grid pk-focus"><div class="pk-card pk-timer-main"><div><div class="pk-mode-label">FOCUS SESSION</div><div class="pk-big-time">${fmt(state.focusRemaining)}</div><div class="pk-progress"><i style="width:${Math.min(100,100*(1500-state.focusRemaining)/1500)}%"></i></div><div class="pk-actions"><button class="pk-btn" data-ui="focus-toggle">${state.focusRunning?'일시정지':'시작'}</button><button class="pk-btn" data-ui="focus-plus">+5분</button><button class="pk-btn" data-ui="focus-reset">리셋</button></div></div></div><div class="pk-card pk-buddy"><h3>Lucario Focus</h3><p>집중 중에는 랜덤 이벤트와 일반 알림을 막고 중요 알림만 작게 표시합니다.</p><img src="${POKE(448)}"></div></div>`,'FOCUS',state.dark);
}
function renderTimer(){
 return shell(`<div class="pk-grid pk-two"><div class="pk-card pk-tool"><h3>COUNTDOWN</h3><div class="pk-big-time">${fmt(state.countdown)}</div><div class="pk-actions"><button class="pk-btn" data-ui="countdown-toggle">${state.countdownRunning?'Pause':'Start'}</button><button class="pk-btn" data-ui="countdown-reset">10m</button></div></div><div class="pk-card pk-tool"><h3>PRESETS</h3><div class="pk-list"><div class="pk-row"><span>5분</span><b>QUICK</b></div><div class="pk-row"><span>10분</span><b>DEFAULT</b></div><div class="pk-row"><span>30분</span><b>LONG</b></div><div class="pk-row"><span>Custom</span><b>SET</b></div></div></div></div>`,'TOOLS',state.dark);
}
function renderStopwatch(){
 return shell(`<div class="pk-grid pk-two"><div class="pk-card pk-tool"><h3>STOPWATCH</h3><div class="pk-big-time">${fmt(state.stopwatch)}</div><div class="pk-actions"><button class="pk-btn" data-ui="sw-toggle">${state.stopwatchRunning?'Pause':'Start'}</button><button class="pk-btn" data-ui="sw-lap">Lap</button><button class="pk-btn" data-ui="sw-reset">Reset</button></div></div><div class="pk-card pk-tool"><h3>LAPS</h3><div class="pk-list">${state.laps.slice(0,4).map((l,i)=>`<div class="pk-row"><span>Lap ${state.laps.length-i}</span><b>${l}</b></div>`).join('')}</div></div></div>`,'TOOLS',state.dark);
}
function renderToday(){
 return shell(`<div class="pk-grid pk-two"><div class="pk-card pk-tool"><h3>TODAY</h3><div class="pk-list"><div class="pk-row"><span>신호 복습 25분</span><i class="pk-good">DONE</i></div><div class="pk-row"><span>확률 과제 1페이지</span><b>18:00</b></div><div class="pk-row"><span>영단어 20개</span><b>20:30</b></div><div class="pk-row"><span>전자회로 복습</span><b>NEXT</b></div></div></div><div class="pk-card pk-tool"><h3>DAILY</h3><div class="pk-stat">1h45m</div><div class="pk-substat">3 sessions · 목표 3h · 4-day streak</div><div class="pk-progress"><i style="width:58%"></i></div><div class="pk-list"><div class="pk-row"><span>가장 가까운 D-day</span><b>D‑4</b></div></div></div></div>`,'TODAY',state.dark);
}
function renderStats(){
 return shell(`<div class="pk-grid pk-two"><div class="pk-card pk-tool"><h3>THIS WEEK</h3><div class="pk-stat">8h20m</div><div class="pk-substat">12 sessions · +18% vs last week</div><div class="pk-list"><div class="pk-row"><span>월</span><b>1h10</b></div><div class="pk-row"><span>화</span><b>2h05</b></div><div class="pk-row"><span>수</span><b>0h45</b></div><div class="pk-row"><span>목</span><b>2h35</b></div></div></div><div class="pk-card pk-tool"><h3>STREAK</h3><div class="pk-stat">4 days</div><div class="pk-substat">다음 reward까지 1 session</div><img src="${POKE(175)}" style="position:absolute;width:46%;right:5%;bottom:0"></div></div>`,'TODAY',state.dark);
}
function renderDex(){
 const ids=[94,175,417,448,468,385,25,133,197,196,492,778,700,702,447,570,280,39];
 return shell(`<div class="pk-dex-grid">${ids.map((id,i)=>`<div class="pk-mon"><img src="${POKE(id)}">#${id}${i<11?' · FOUND':' · LOCKED'}</div>`).join('')}</div>`,'DEX',state.dark);
}
function renderNfc(){
 return shell(`<div class="pk-grid pk-nfc"><div class="pk-card pk-nfc-pad"><div><div class="pk-nfc-ring">${state.nfc?'✓':'NFC'}</div><h3 style="font-size:3cqw;margin:5% 0 0">${state.nfc?'Gengar detected':'측면 피규어/태그를 대주세요'}</h3><p style="font-size:1.8cqw;color:#777">오른쪽 side pod · Qi와 물리 분리</p></div></div><div class="pk-card pk-buddy"><h3>${state.nfc?'Gengar Theme':'NFC Mode'}</h3><p>${state.nfc?'Night buddy와 조명 테마를 불러왔습니다.':'태그로 companion, 조명, 집중 preset을 전환할 수 있습니다.'}</p><img src="${POKE(state.nfc?94:417)}"></div></div>`,'DEX',state.dark);
}
function renderWeather(){
 return shell(`<div class="pk-grid pk-weather"><div class="pk-card pk-weather-now"><div class="pk-mode-label">SUWON · NOW</div><div class="pk-temp">18°</div><div class="pk-substat">맑음 · 체감 17° · 습도 48%</div><div class="pk-forecast"><div class="pk-day">15시<br><b>18°</b></div><div class="pk-day">18시<br><b>16°</b></div><div class="pk-day">21시<br><b>13°</b></div><div class="pk-day">00시<br><b>11°</b></div></div></div><div class="pk-card pk-weather-char"><img src="${POKE(468)}"><span style="font-size:2cqw">산책하기 좋은 날씨</span></div></div>`,'HOME',state.dark);
}
function renderAlarm(){
 return shell(`<div class="pk-alarm-list"><div class="pk-alarm"><div><strong>07:30</strong><small> 평일 · Togepi Morning</small></div><span class="pk-switch"></span></div><div class="pk-alarm"><div><strong>08:10</strong><small> 화/목 · 수업 준비</small></div><span class="pk-switch"></span></div><div class="pk-alarm"><div><strong>22:20</strong><small> 매일 · 내일 준비</small></div><span class="pk-switch"></span></div><div class="pk-card pk-tool"><h3>BEDTIME</h3><div class="pk-substat">22:30 이후 자동 Night Mode · 알람은 항상 유지</div></div></div>`,'HOME',state.dark);
}
function renderPhone(){
 return shell(`<div class="pk-grid pk-phone"><div class="pk-card pk-phone-icon"><div><div class="pk-phone-shape"></div><p style="font-size:1.8cqw;text-align:center">${state.phoneParked?'후면 거치 · 충전 중':'폰 없음'}</p></div></div><div class="pk-card pk-notices"><h3 style="font-size:3cqw;margin:0">Priority only</h3><div class="pk-notice"><b>CALL · 엄마</b><p>통화 수신 알림</p></div><div class="pk-notice"><b>CALENDAR · 15분 뒤</b><p>다음 일정 요약</p></div><div class="pk-notice"><b>PRIORITY · selected contact</b><p>본문은 표시/저장하지 않음</p></div></div></div>`,'HOME',state.dark);
}
function renderLight(){
 return shell(`<div class="pk-grid pk-light"><div class="pk-card pk-theme" style="--theme:#f4d9bf"><span>Warm · Togepi</span></div><div class="pk-card pk-theme" style="--theme:#d8eefa"><span>Electric · Pachirisu</span></div><div class="pk-card pk-theme" style="--theme:#d7e8ef"><span>Calm · Togekiss</span></div><div class="pk-card pk-theme" style="--theme:#4e3e69"><span>Night · Gengar</span></div></div>`,'HOME',state.dark);
}
function renderSettings(){
 return shell(`<div class="pk-grid pk-settings"><div class="pk-card pk-settings-col"><div class="pk-setting"><span>Auto brightness</span><b>ON</b></div><div class="pk-setting"><span>Night start</span><b>22:30</b></div><div class="pk-setting"><span>Volume</span><b>35%</b></div><div class="pk-setting"><span>Random encounter</span><b>ON</b></div></div><div class="pk-card pk-settings-col"><div class="pk-setting"><span>Wi‑Fi</span><b>CONNECTED</b></div><div class="pk-setting"><span>NFC side</span><b>RIGHT</b></div><div class="pk-setting"><span>Phone bridge</span><b>OPTIONAL</b></div><div class="pk-setting"><span>Web settings</span><b>OPEN</b></div></div></div>`,'HOME',state.dark);
}
function renderBirthday(){
 return `<div class="pk-screen"><div class="pk-birthday"><div><div class="pk-mode-label" style="color:#d4d7e2">SPECIAL EVENT</div><img src="${POKE(385)}"><h2>A SPECIAL EVENT HAS STARTED.</h2><p>오늘만 열리는 아주 희귀한 이벤트 ✦</p><button class="pk-btn" data-ui="birthday-close">오늘의 포켓몬 센터 열기</button></div></div></div>`;
}
function renderNight(){
 return shell(`<div class="pk-grid pk-home"><div class="pk-card pk-hero"><div class="pk-time">23:48</div><div class="pk-date">Night Mode · brightness 18%</div><img class="pk-char" src="${POKE(94)}"><div class="pk-message">밤이 됐다.<small>애니메이션과 밝기를 줄이고 알람은 유지합니다.</small></div></div><div class="pk-stack"><div class="pk-card pk-mini"><b>내일 첫 일정</b><span>09:00</span></div><div class="pk-card pk-mini"><b>오늘 공부</b><span>2h 35m</span></div><div class="pk-card pk-mini"><b>알람</b><span>07:30 ON</span></div><div class="pk-card pk-mini"><b>Phone</b><span>${state.phoneParked?'후면 충전 중':'없음'}</span></div></div></div>`,'HOME',true,'Night · Wi‑Fi ●');
}

const renderers={home:renderHome,focus:renderFocus,timer:renderTimer,stopwatch:renderStopwatch,today:renderToday,stats:renderStats,dex:renderDex,nfc:renderNfc,weather:renderWeather,alarm:renderAlarm,phone:renderPhone,light:renderLight,settings:renderSettings,birthday:renderBirthday,night:renderNight};

function render(){
 const s=screens.find(x=>x.id===state.screen);
 document.getElementById('deviceScreen').innerHTML=renderers[state.screen]();
 document.getElementById('screenTitle').textContent=s.label;
 document.getElementById('screenPurpose').textContent=s.purpose;
 document.querySelectorAll('#screenPicker button').forEach(b=>b.classList.toggle('active',b.dataset.screen===state.screen));
 document.getElementById('stateBox').textContent=`screen: ${state.screen}\nphoneParked: ${state.phoneParked}\npriority: ${state.priority}\ndark: ${state.dark}\nnfc: ${state.nfc}\nfocus: ${fmt(state.focusRemaining)}`;
 bindUiButtons();
}
function bindUiButtons(){
 document.querySelectorAll('[data-ui]').forEach(el=>el.onclick=()=>{
  const a=el.dataset.ui;
  if(a==='focus-toggle')state.focusRunning=!state.focusRunning;
  if(a==='focus-plus')state.focusRemaining+=300;
  if(a==='focus-reset'){state.focusRemaining=1500;state.focusRunning=false}
  if(a==='countdown-toggle')state.countdownRunning=!state.countdownRunning;
  if(a==='countdown-reset'){state.countdown=600;state.countdownRunning=false}
  if(a==='sw-toggle')state.stopwatchRunning=!state.stopwatchRunning;
  if(a==='sw-lap')state.laps.unshift(fmt(state.stopwatch));
  if(a==='sw-reset'){state.stopwatch=0;state.stopwatchRunning=false;state.laps=[]}
  if(a==='birthday-close'){state.birthday=false;state.screen='home'}
  render();
 }};
}
function buildPicker(){
 const p=document.getElementById('screenPicker');
 p.innerHTML=screens.map(s=>`<button data-screen="${s.id}"><b>${s.label}</b><small>${s.purpose}</small></button>`).join('');
 p.querySelectorAll('button').forEach(b=>b.onclick=()=>{state.screen=b.dataset.screen;render()});
}
function buildGallery(){
 const g=document.getElementById('screenGallery');
 g.innerHTML=screens.map(s=>`<article class="gallery-card" data-open="${s.id}"><header><b>${s.label}</b><span>${s.purpose}</span></header><div class="mini-frame"><div class="pk-screen">${renderers[s.id]().replace(/^<div class="pk-screen[^>]*>|<\/div>$/g,'')}</div></div></article>`).join('');
 g.querySelectorAll('.gallery-card').forEach(c=>c.onclick=()=>{state.screen=c.dataset.open;location.hash='ui-lab';render()});
}
function action(a){
 if(a==='toggle-phone')state.phoneParked=!state.phoneParked;
 if(a==='priority-alert')state.priority=!state.priority;
 if(a==='toggle-dark')state.dark=!state.dark;
 if(a==='nfc-scan'){state.nfc=!state.nfc;state.screen='nfc'}
 if(a==='birthday'){state.birthday=true;state.screen='birthday'}
 if(a==='reset')Object.assign(state,{screen:'home',phoneParked:true,dark:false,priority:false,nfc:false,birthday:false,focusRemaining:1458,focusRunning:false,countdown:600,countdownRunning:false,stopwatch:1938.4,stopwatchRunning:false,laps:['32:18.4','21:04.8','10:12.1']});
 render(); buildGallery();
}
document.querySelectorAll('[data-action]').forEach(b=>b.onclick=()=>action(b.dataset.action));

setInterval(()=>{
 let dirty=false;
 if(state.focusRunning&&state.focusRemaining>0){state.focusRemaining--;dirty=state.screen==='focus'}
 if(state.countdownRunning&&state.countdown>0){state.countdown--;dirty=dirty||state.screen==='timer'}
 if(state.stopwatchRunning){state.stopwatch+=1;dirty=dirty||state.screen==='stopwatch'}
 if(dirty)render();
},1000);

buildPicker();render();buildGallery();