import {ROSTER,ALARM_SOUNDS,artUrl,pixelUrl,kstParts,focusRemaining,formatSeconds,alarmDue,normalizeState} from './core.js';
const $=id=>document.getElementById(id),KEY='pokedock-v17-mobile-state',TRIGGER_KEY='pokedock-v17-alarm-triggers';
function readStorage(key,def){try{return JSON.parse(localStorage.getItem(key))??def}catch{return def}}
let state=normalizeState(readStorage(KEY,{})),fired=readStorage(TRIGGER_KEY,{}),toastTimer,gestureCount=0;
function save(){try{localStorage.setItem(KEY,JSON.stringify(state))}catch{}}
function notice(msg){const el=$('toast');el.textContent=msg;el.hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.hidden=true,3300)}
function imageFor(id,style){return style==='pixel'?pixelUrl(id):artUrl(id)}
function setImage(img,id,style){let src=imageFor(id,style);img.onerror=()=>{img.onerror=null;if(style==='pixel')img.src=artUrl(id);else{img.alt='이미지를 불러오지 못했어요. 인터넷 연결을 확인해 주세요';img.removeAttribute('src')}};img.src=src;img.alt=ROSTER.find(x=>x.id===id)?.name||'포켓몬';img.classList.toggle('pixel',style==='pixel')}
function sizePixelSprite(){
 const img=$('game-pokemon');
 if(!img.classList.contains('pixel')){img.style.removeProperty('width');img.style.removeProperty('height');return;}
 const c=ROSTER.find(p=>p.id===state.character)||ROSTER[0],box=img.parentElement.getBoundingClientRect();
 if(!box.width||!box.height)return;
 const [w,h]=c.pixel;
 const scale=Math.max(1,Math.min(3,Math.floor(box.width*.78/w),Math.floor(box.height*.75/h)));
 img.style.width=`${w*scale}px`;img.style.height=`${h*scale}px`;
}
function motion(type){for(const img of [$('hero-pokemon'),$('game-pokemon')]){img.classList.remove('hop','dance','peek','celebrate');void img.offsetWidth;if(!state.reduceMotion)img.classList.add(type);}setTimeout(()=>{for(const img of [$('hero-pokemon'),$('game-pokemon')])img.classList.remove('hop','dance','peek','celebrate')},1450)}
function renderCharacter(){const c=ROSTER.find(p=>p.id===state.character)||ROSTER[0];setImage($('hero-pokemon'),c.id,'art');setImage($('game-pokemon'),c.id,state.style);
$('partner-name').textContent=c.name;$('partner-type').textContent=c.types;$('partner-line').textContent=c.line;$('partner-index').textContent='NO. '+String(c.id).padStart(3,'0');$('daily-title').textContent=`${c.name}이랑 보내는 하루`;$('mode-tag').textContent=c.en+' IS HERE';$('daily-subtitle').textContent=c.line;
for(const b of document.querySelectorAll('#roster [data-id]'))b.classList.toggle('selected',Number(b.dataset.id)===state.character);
for(const b of document.querySelectorAll('#style-switch [data-style]'))b.classList.toggle('selected',b.dataset.style===state.style);sizePixelSprite();}
function renderClock(){const p=kstParts();$('hero-clock').textContent=p.hhmm;$('date-line').textContent=`${p.weekdayName} · ${p.display}`;$('greeting').textContent=p.minute<12*60?'오늘도 좋은 하루 보내 ♡':p.minute<19*60?'잠깐 쉬어도 좋아 ♡':'오늘도 수고했어 ♡';}
function renderFocus(){const sec=focusRemaining(state.focus);$('focus-clock').textContent=formatSeconds(sec);$('focus-start').textContent=state.focus.running?'일시정지':(sec!==state.focusMinutes*60?'계속하기':'집중 시작');for(const b of document.querySelectorAll('[data-focus]'))b.classList.toggle('active',Number(b.dataset.focus)===state.focusMinutes)}
function getNextAlarmLabel(){const on=state.alarms.filter(a=>a.on&&a.days.length);if(!on.length)return {time:'--:--',desc:'알람을 설정해 줘'};const p=kstParts();let candidates=[];for(const alarm of on)for(let d=0;d<8;d++){const dow=(p.weekday+d)%7;if(!alarm.days.includes(dow))continue;const at=d*1440+Number(alarm.time.slice(0,2))*60+Number(alarm.time.slice(3));if(d===0&&at<=p.minute)continue;candidates.push({at,alarm})}const first=candidates.sort((a,b)=>a.at-b.at)[0];return first?{time:first.alarm.time,desc:first.at<1440?'오늘 '+first.alarm.title:'다음 '+first.alarm.title}:{time:on[0].time,desc:on[0].title}}
function renderAlarm(){const a=getNextAlarmLabel();$('alarm-next').textContent=a.time;$('alarm-summary').textContent=a.desc;}
function openGame(){state.view='game';save();updateView();sizePixelSprite();notice('가로로 돌리면 게임 화면이 더 넓게 보여요.');try{screen.orientation?.lock?.('landscape').catch(()=>{})}catch{}}
function goHome(){state.view='home';save();updateView();try{screen.orientation?.unlock?.()}catch{}}
function updateView(){const shouldGame=state.view==='game';$('daily').hidden=shouldGame;$('game').hidden=!shouldGame;$('bottom-nav').hidden=shouldGame;document.querySelectorAll('.bottom-nav button').forEach(b=>b.classList.toggle('selected',b.dataset.view===(shouldGame?'game':'home')))}
function openSheet(title,content){$('sheet-inner').replaceChildren();const h=document.createElement('h2');h.textContent=title;$('sheet-inner').append(h);if(typeof content==='string'){const p=document.createElement('p');p.textContent=content;$('sheet-inner').append(p)}else $('sheet-inner').append(content);$('sheet').hidden=false;$('sheet-backdrop').hidden=false}
function closeSheet(){$('sheet').hidden=true;$('sheet-backdrop').hidden=false;$('sheet-backdrop').hidden=true}
function node(tag,cls='',text=''){const e=document.createElement(tag);e.className=cls;e.textContent=text;return e}
function openFriends(){const body=node('div');const intro=node('p','','마음에 드는 포켓몬을 파트너로 골라 줘. 게임 모드에서 더 크게 움직여!');body.append(intro);
 for(const c of ROSTER){const line=node('div','sheet-row');const icon=new Image();icon.src=artUrl(c.id);icon.width=46;icon.height=46;icon.style.objectFit='contain';icon.alt=c.name;const title=node('div');title.append(node('b','',c.name),node('small','',c.en));const choose=node('button','btn light',c.id===state.character?'선택됨':'선택');choose.addEventListener('click',()=>{state.character=c.id;save();renderCharacter();closeSheet();motion(c.behavior);notice(c.name+'이(가) 나타났어!')});line.append(icon,title,choose);body.append(line)}openSheet('나의 포켓몬 친구들',body)}

function openQuiz(){
 const shuffle=items=>[...items].sort(()=>Math.random()-.5),rounds=shuffle(ROSTER).slice(0,5);
 const body=node('div','quiz-body');let round=0,score=0;
 function show(){
  body.replaceChildren();
  if(round===rounds.length){
   state.quizBest=Math.max(state.quizBest,score);save();
   body.append(node('div','quiz-result',`${score} / ${rounds.length} 정답!`),node('p','',`최고 기록 ${state.quizBest}점 · 잠깐 쉬면서 또 놀자.`));
   const again=node('button','btn solid','다시 도전');again.onclick=openQuiz;body.append(again);return;
  }
  const answer=rounds[round];body.append(node('p','',`${round+1} / ${rounds.length} · 실루엣의 주인공은 누구일까?`));
  const img=new Image();img.src=artUrl(answer.id);img.alt='포켓몬 실루엣';img.className='quiz-image hidden';body.append(img);
  const choices=node('div','quiz-choices');
  const options=shuffle([answer,...shuffle(ROSTER.filter(c=>c.id!==answer.id)).slice(0,2)]);
  for(const choice of options){const b=node('button','',choice.name);b.onclick=()=>{
    for(const button of choices.querySelectorAll('button'))button.disabled=true;
    img.classList.remove('hidden');img.alt=answer.name;
    const correct=choice.id===answer.id;if(correct)score++;
    b.classList.add(correct?'correct':'wrong');
    feedback.textContent=correct?'정답! '+answer.name:'아쉬워! 정답은 '+answer.name;
    setTimeout(()=>{round++;if(body.isConnected)show()},1000);
   };choices.append(b)}body.append(choices);const feedback=node('p','quiz-feedback','최고 기록 '+state.quizBest+'점');body.append(feedback);
 }
 show();openSheet('누구일까?',body);
}

// Device-local notification scheduling, only after explicit user action. No server/push needed.
let nativePermissionAsked=false,previewAudio;
const soundFor=id=>ALARM_SOUNDS.find(item=>item.id===id)||ALARM_SOUNDS[0];
async function cancelNativeAlarms(){
 const N=window.Capacitor?.Plugins?.LocalNotifications;if(!N)return;
 const ids=[];for(let i=0;i<8;i++)for(let d=0;d<14;d++)ids.push({id:10000+i*20+d});
 await N.cancel({notifications:ids});
}
function playAlarmSound(id){
 try{previewAudio?.pause();previewAudio=new Audio('assets/sounds/'+soundFor(id).file);previewAudio.play().catch(()=>{});}catch{}
}
async function syncNativeAlarms(){
 const N=window.Capacitor?.Plugins?.LocalNotifications;
 if(!N)return false;
 try{
  const perm=await N.checkPermissions();
  if(perm.display!=='granted'){
   if(!nativePermissionAsked){nativePermissionAsked=true;const p=await N.requestPermissions();if(p.display!=='granted'){notice('알림 권한이 꺼져 있어요. 시스템 설정을 확인해 주세요.');return false;}}
   else return false;
  }
  await cancelNativeAlarms();
  const scheduled=[];
  const android=window.Capacitor?.getPlatform?.()==='android';
  if(android&&typeof N.createChannel==='function')for(const sound of ALARM_SOUNDS){
   await N.createChannel({id:`pokedock_alarm_${sound.id}_v1`,name:`PokéDock · ${sound.name}`,importance:4,visibility:1,sound:sound.file});
  }
  for(let i=0;i<state.alarms.length;i++){
   const a=state.alarms[i];if(!a.on)continue;
   const [hour,minute]=a.time.split(':').map(Number);
   const sound=soundFor(a.sound);
   for(const day of a.days){
    scheduled.push({id:10000+i*20+day,title:'PokéDock · '+a.title,body:'파트너가 기다리고 있어요 ♡',schedule:{on:{weekday:day+1,hour,minute,second:0},allowWhileIdle:true},sound:sound.file,...(android?{channelId:`pokedock_alarm_${sound.id}_v1`,smallIcon:'ic_stat_name'}:{})});
   }
  }
  if(scheduled.length)await N.schedule({notifications:scheduled});
  const exact=android&&typeof N.checkExactNotificationSetting==='function'?await N.checkExactNotificationSetting():null;
  notice('반복 알림 '+scheduled.length+'개 등록'+(exact?.exact_alarm==='denied'?' · 정확한 알람 권한을 확인해 줘.':'됐어.'));return true;
 }catch(e){notice('알람 등록 확인 필요: '+String(e?.message||e).slice(0,90));return false;}
}

function openAlarmSheet(){
 const body=node('div'),native=!!window.Capacitor?.isNativePlatform?.();
 body.append(node('p','',native?'시간·요일·소리를 고른 뒤 아래의 기기에 적용을 눌러 줘. 알림 권한과 절전 설정에 따라 지연될 수 있어.':'웹앱 소리는 앱 화면이 열려 있을 때만 울려. 잠금 상태에서도 울리는 알람은 설치된 네이티브 앱이 필요해.'));
 const list=node('div');body.append(list);
 const apply=node('button','btn solid','기기에 알람 적용');
 const changed=()=>{save();renderAlarm();if(native)apply.textContent='변경사항 기기에 적용';};
 function draw(){
  list.replaceChildren();
  state.alarms.forEach((alarm,i)=>{
   const card=node('div','alarm-card');
   const top=node('div','alarm-top');
   const title=document.createElement('input');title.type='text';title.maxLength=32;title.value=alarm.title;title.setAttribute('aria-label',`${i+1}번 알람 이름`);title.onchange=()=>{alarm.title=title.value.trim()||'새 알람';changed()};
   const toggle=document.createElement('input');toggle.type='checkbox';toggle.checked=alarm.on;toggle.setAttribute('aria-label',alarm.title+' 사용');toggle.onchange=()=>{alarm.on=toggle.checked;changed()};
   top.append(title,toggle);card.append(top);
   const time=document.createElement('input');time.type='time';time.value=alarm.time;time.setAttribute('aria-label',alarm.title+' 시간');time.onchange=()=>{if(/^([01]\d|2[0-3]):[0-5]\d$/.test(time.value)){alarm.time=time.value;changed()}};card.append(time);
   const days=node('div','weekday-picker');days.setAttribute('aria-label',alarm.title+' 반복 요일');
   ['일','월','화','수','목','금','토'].forEach((label,day)=>{const b=node('button',alarm.days.includes(day)?'selected':'',label);b.type='button';b.setAttribute('aria-pressed',String(alarm.days.includes(day)));b.onclick=()=>{alarm.days=alarm.days.includes(day)?alarm.days.filter(x=>x!==day):[...alarm.days,day].sort();b.classList.toggle('selected',alarm.days.includes(day));b.setAttribute('aria-pressed',String(alarm.days.includes(day)));changed()};days.append(b)});card.append(days);
   const soundRow=node('div','alarm-sound-row');const select=document.createElement('select');select.setAttribute('aria-label',alarm.title+' 알람 소리');for(const sound of ALARM_SOUNDS){const opt=document.createElement('option');opt.value=sound.id;opt.textContent=sound.name;select.append(opt)}select.value=alarm.sound;select.onchange=()=>{alarm.sound=select.value;changed()};const preview=node('button','btn text-btn','▶ 미리 듣기');preview.type='button';preview.onclick=()=>playAlarmSound(alarm.sound);soundRow.append(select,preview);card.append(soundRow);
   const remove=node('button','alarm-remove','알람 삭제');remove.type='button';remove.onclick=()=>{state.alarms.splice(i,1);changed();draw()};card.append(remove);list.append(card);
  });
  add.disabled=state.alarms.length>=8;
 }
 const add=node('button','btn light','＋ 알람 추가');add.type='button';add.onclick=()=>{state.alarms.push({id:'custom_'+Date.now(),title:'새 알람',time:'09:00',days:[0,1,2,3,4,5,6],on:true,sound:'dawn'});changed();draw()};body.append(add);
 if(native){apply.onclick=async()=>{if(await syncNativeAlarms())apply.textContent='기기에 적용됨'};body.append(apply)}
 draw();openSheet('알람 관리',body);
}
function openMemories(){const body=node('div');body.append(node('p','','이곳은 우리만 아는 공간이야. 팬텀을 다섯 번 누르면 열리는 이스터에그도 그대로 유지했어.'));
 const input=node('textarea');input.value=state.message;input.setAttribute('aria-label','우리만의 편지');input.maxLength=1000;body.append(input);
 const saveBtn=node('button','btn solid','편지 저장');saveBtn.addEventListener('click',()=>{state.message=input.value;save();closeSheet();notice('우리 서랍에 편지를 보관했어 ♡')});body.append(saveBtn);
 const secret=node('div','sheet-row');secret.append(node('b','',state.secretUnlocked?'✦ 팬텀의 비밀이 열렸어!':'🔒 팬텀의 작은 비밀'));body.append(secret);
 const birthday=node('button','btn light','🎂 특별한 날의 깜짝 메시지 보기');birthday.addEventListener('click',()=>{notice('오늘 가장 소중한 주인공은 바로 너야! ♡');motion('celebrate')});body.append(birthday);openSheet('우리 서랍 ♡',body)}
function openSettings(){const body=node('div');body.append(node('p','','시계는 한국 시간 기준이며 개인정보와 편지는 이 기기에만 저장돼.'));
 const row=node('div','sheet-row'),title=node('b','','동작 줄이기'),check=document.createElement('input');check.type='checkbox';check.checked=state.reduceMotion;check.onchange=()=>{state.reduceMotion=check.checked;save()};row.append(title,check);body.append(row);
 const clear=node('button','btn light','데이터 초기화');clear.onclick=async()=>{if(confirm('알람·편지·캐릭터 설정을 삭제할까?')){if(window.Capacitor?.isNativePlatform?.())await cancelNativeAlarms().catch(()=>{});localStorage.removeItem(KEY);localStorage.removeItem(TRIGGER_KEY);fired={};state=normalizeState();save();closeSheet();initScreen();notice('초기화했어')}};body.append(clear);openSheet('설정',body)}
function initRoster(){const el=$('roster');el.replaceChildren();for(const c of ROSTER){const b=node('button','',c.name);b.dataset.id=c.id;b.onclick=()=>{state.character=c.id;save();renderCharacter();motion(c.behavior)};el.append(b)}}
function handlePet(){gestureCount++;state.petCount=(state.petCount||0)+1;if(gestureCount>=5){gestureCount=0;state.secretUnlocked=true;save();openMemories();notice('✧ 팬텀의 비밀 공간이 열렸어!')}else{motion(ROSTER.find(c=>c.id===state.character)?.behavior||'hop');notice(['놀러 왔어?','헤헤, 간지러워!','오늘도 함께하자 ♡','거의 비밀을 찾았어!'][Math.min(gestureCount-1,3)])}}
function updateAlarms(){const due=alarmDue(state.alarms,new Date(),fired);for(const item of due){fired[item.alarm.id]=item.key;try{localStorage.setItem(TRIGGER_KEY,JSON.stringify(fired))}catch{}notice('♬ '+item.alarm.title+' · '+item.alarm.time);if(!window.Capacitor?.isNativePlatform?.())playAlarmSound(item.alarm.sound);if(navigator.vibrate)navigator.vibrate([120,80,120]);motion('celebrate')}}
function tick(){renderClock();const remaining=focusRemaining(state.focus);if(state.focus.running&&remaining===0){state.focus.running=false;state.focus.remainingSec=0;save();notice('집중 완료! 팬텀이 응원해 ♡');motion('celebrate');}renderFocus();updateAlarms()}
function initScreen(){initRoster();renderCharacter();renderClock();renderFocus();renderAlarm();updateView()}
$('orientation-button').onclick=openGame;$('game-exit').onclick=goHome;$('settings-button').onclick=openSettings;$('focus-reset').onclick=()=>{state.focus={running:false,endAt:0,remainingSec:state.focusMinutes*60};save();renderFocus()};
$('focus-start').onclick=()=>{const now=Date.now();const remaining=focusRemaining(state.focus,now);if(state.focus.running){state.focus.running=false;state.focus.remainingSec=remaining;}else{const secs=remaining||state.focusMinutes*60;state.focus.endAt=now+secs*1000;state.focus.remainingSec=secs;state.focus.running=true;}save();renderFocus()};
for(const b of document.querySelectorAll('[data-focus]'))b.onclick=()=>{state.focusMinutes=Number(b.dataset.focus);state.focus={running:false,endAt:0,remainingSec:state.focusMinutes*60};save();renderFocus()};
$('alarm-edit').onclick=openAlarmSheet;$('open-partners').onclick=openFriends;$('pet-pokemon').onclick=handlePet;$('easter-entry').onclick=openMemories;
$('quiz-open').onclick=openQuiz;
$('sheet-close').onclick=closeSheet;$('sheet-backdrop').onclick=closeSheet;
for(const b of document.querySelectorAll('[data-view]'))b.onclick=()=>{const v=b.dataset.view;if(v==='home')goHome();else if(v==='game')openGame();else if(v==='friends')openFriends();else openMemories()};
for(const b of document.querySelectorAll('[data-style]'))b.onclick=()=>{state.style=b.dataset.style;save();renderCharacter()};
for(const b of document.querySelectorAll('[data-motion]'))b.onclick=()=>motion(b.dataset.motion);
window.addEventListener('keydown',e=>{if(e.key==='Escape'){closeSheet();if(state.view==='game')goHome()}});
// offline.js installs the service worker and reports sprite cache progress.
window.addEventListener('resize',sizePixelSprite);
initScreen();setInterval(tick,1000);document.addEventListener('visibilitychange',()=>{if(!document.hidden)tick()});
