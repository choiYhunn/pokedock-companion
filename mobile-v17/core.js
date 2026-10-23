export const ROSTER = Object.freeze([
 {id:94,name:'팬텀',en:'GENGAR',types:'GHOST · POISON',line:'오늘은 나랑 놀아볼래?',color:'#ae88d4',behavior:'peek',pixel:[74,63]},
 {id:393,name:'팽도리',en:'PIPLUP',types:'WATER',line:'한 번 더 도전해 볼까?',color:'#91c5ed',behavior:'hop',pixel:[30,41]},
 {id:468,name:'토게키스',en:'TOGEKISS',types:'FAIRY · FLYING',line:'좋은 일이 가득할 거야!',color:'#eec9e5',behavior:'dance',pixel:[86,52]},
 {id:448,name:'루카리오',en:'LUCARIO',types:'FIGHTING · STEEL',line:'오늘도 조금씩 성장하자.',color:'#7a9fd2',behavior:'celebrate',pixel:[47,63]},
 {id:195,name:'누오',en:'QUAGSIRE',types:'WATER · GROUND',line:'천천히 가도 괜찮아.',color:'#add4d9',behavior:'hop',pixel:[67,58]},
 {id:175,name:'토게피',en:'TOGEPI',types:'FAIRY',line:'너랑 있으면 행복해!',color:'#f1c3b1',behavior:'celebrate',pixel:[40,38]},
 {id:417,name:'파치리스',en:'PACHIRISU',types:'ELECTRIC',line:'우리, 잠깐 놀까?',color:'#bed8ee',behavior:'dance',pixel:[53,55]},
 {id:385,name:'지라치',en:'JIRACHI',types:'STEEL · PSYCHIC',line:'소원 하나 들어줄까?',color:'#eec97c',behavior:'peek',pixel:[55,47]}
]);
export const artUrl = id => `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${id}.png`;
export const pixelUrl = id => `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/${id}.gif`;
export const ALARM_SOUNDS = Object.freeze([
 {id:'dawn',name:'모험의 아침',file:'alarm_dawn.wav'},
 {id:'sparkle',name:'별빛 알림',file:'alarm_sparkle.wav'},
 {id:'calm',name:'포근한 밤',file:'alarm_calm.wav'}
]);
export const DEFAULT_ALARMS = [{id:'morning',time:'07:30',days:[1,2,3,4,5],on:false,title:'아침 인사',sound:'dawn'}, {id:'break',time:'08:10',days:[2,4],on:false,title:'오늘도 좋은 하루',sound:'sparkle'}, {id:'night',time:'22:20',days:[0,1,2,3,4,5,6],on:false,title:'하루를 마무리할 시간',sound:'calm'}];
export function normalizeAlarms(value){
 if(!Array.isArray(value))return structuredClone(DEFAULT_ALARMS);
 const seen=new Set();
 return value.slice(0,8).map((raw,i)=>{
  const fallback=DEFAULT_ALARMS[i]||DEFAULT_ALARMS[0];
  let id=typeof raw?.id==='string'&&/^[a-zA-Z0-9_-]{1,40}$/.test(raw.id)?raw.id:`custom_${i}`;
  if(seen.has(id))id=`custom_${i}`;seen.add(id);
  const time=typeof raw?.time==='string'&&/^([01]\d|2[0-3]):[0-5]\d$/.test(raw.time)?raw.time:fallback.time;
  const days=Array.isArray(raw?.days)?[...new Set(raw.days.filter(d=>Number.isInteger(d)&&d>=0&&d<=6))].sort():fallback.days;
  const title=typeof raw?.title==='string'&&raw.title.trim()?raw.title.trim().slice(0,32):fallback.title;
  const sound=ALARM_SOUNDS.some(item=>item.id===raw?.sound)?raw.sound:fallback.sound;
  return {id,time,days,on:!!raw?.on,title,sound};
 });
}
export function kstParts(date=new Date()) {
 const p = new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Seoul',year:'numeric',month:'2-digit',day:'2-digit',weekday:'short',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).formatToParts(date);
 const o=Object.fromEntries(p.filter(x=>x.type!=='literal').map(x=>[x.type,x.value]));
 const kstDate=new Date(`${o.year}-${o.month}-${o.day}T12:00:00Z`);
 const dow=kstDate.getUTCDay();
 return {hhmm:`${o.hour}:${o.minute}`,day:`${o.year}-${o.month}-${o.day}`,weekday:dow,minute:Number(o.hour)*60+Number(o.minute),display:`${o.month}.${o.day}`,weekdayName:['SUN','MON','TUE','WED','THU','FRI','SAT'][dow]};
}
export function focusRemaining(state,now=Date.now()){
 if(state.running)return Math.max(0,Math.ceil((state.endAt-now)/1000));return Math.max(0,state.remainingSec);
}
export function formatSeconds(n){const sec=Math.max(0,Math.floor(n));return String(Math.floor(sec/60)).padStart(2,'0')+':'+String(sec%60).padStart(2,'0');}
export function alarmDue(alarms,now,lastTriggered={}){
 const p=kstParts(now),due=[];
 for(const a of alarms){if(!a.on||!a.days.includes(p.weekday)||a.time!==p.hhmm)continue;
  const key=p.day+'|'+a.id;if(lastTriggered[a.id]===key)continue;
  due.push({alarm:a,key});
 }return due;
}
export function normalizeState(data={}){
 const s={character:94,style:'art',view:'home',focusMinutes:25,focus:{running:false,endAt:0,remainingSec:1500},alarms:structuredClone(DEFAULT_ALARMS),message:'너와 함께하는 평범한 하루가 좋아. ♡',birthday:'',petCount:0,secretUnlocked:false,reduceMotion:false,quizBest:0,...data};
 if(!ROSTER.some(x=>x.id===s.character))s.character=94;
 if(!['art','pixel'].includes(s.style))s.style='art';
 if(![15,25,45].includes(s.focusMinutes))s.focusMinutes=25;
 s.alarms=normalizeAlarms(s.alarms);
 if(!Number.isInteger(s.quizBest)||s.quizBest<0||s.quizBest>5)s.quizBest=0;
 if(!s.focus||typeof s.focus!=='object')s.focus={running:false,endAt:0,remainingSec:s.focusMinutes*60};
 return s;
}
