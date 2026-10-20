/* V16 portable interaction engine; no hardware I/O, no licensed images. */
(function(root,factory){const api=factory();if(typeof module==="object"&&module.exports)module.exports=api;else root.GhostEngine=api;})(typeof globalThis!=="undefined"?globalThis:this,function(){
"use strict";
const CHARACTERS=[
 {id:"gengar",name:"팬텀",en:"GENGAR",accent:"#a98bd9",action:"float"},
 {id:"piplup",name:"팽도리",en:"PIPLUP",accent:"#8ab8ef",action:"hop"},
 {id:"togekiss",name:"토게키스",en:"TOGEKISS",accent:"#e6d9f7",action:"glide"},
 {id:"lucario",name:"루카리오",en:"LUCARIO",accent:"#98c6e9",action:"pose"},
 {id:"quagsire",name:"누오",en:"QUAGSIRE",accent:"#b7d9ce",action:"wiggle"}
];
const FOCUS_MINUTES=[15,25,45];
function isValidHHMM(v){return typeof v==="string"&&/^([01][0-9]|2[0-3]):[0-5][0-9]$/.test(v);}
function partsKST(date){const d=(date instanceof Date?date:new Date(date));const p=new Intl.DateTimeFormat("en-GB",{timeZone:"Asia/Seoul",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hourCycle:"h23"}).formatToParts(d);
 const o={};for(const x of p)o[x.type]=x.value;return {day:o.year+"-"+o.month+"-"+o.day,hhmm:o.hour+":"+o.minute,display:o.hour+":"+o.minute};}
class Engine {
 constructor(now=()=>performance.now(), wall=()=>new Date()) {this.now=now;this.wall=wall;this.character=0;this.mode="clock";this.focusSec=1500;this.remainingSec=1500;this.endsAt=0;this.running=false;this.paused=false;this.motion="idle";this.motionUntil=0;this.alarm={enabled:false,at:"07:30"};this.lastAlarmKey="";this.muted=true;this.reducedMotion=false;this.events=[];this.version="v16.0.0-prototype";}
 emit(type,detail={}){this.events.push({type,...detail});return type;}
 selectCharacter(i){if(!Number.isInteger(i)||i<0||i>=CHARACTERS.length)throw new RangeError("unknown character");this.character=i;this.animate("enter",1300);this.emit("character",{id:CHARACTERS[i].id});}
 nextCharacter(){this.selectCharacter((this.character+1)%CHARACTERS.length);}
 animate(name,durationMs=900){this.motion=name;this.motionUntil=this.now()+durationMs;}
 interact(){this.animate(["hop","dance","peek","spin"][Math.floor(this.now()/117)%4],1100);this.emit("interaction",{character:CHARACTERS[this.character].id});}
 setFocus(minutes){if(!FOCUS_MINUTES.includes(minutes))throw new RangeError("invalid focus preset");if(this.running)throw Error("stop the current timer first");this.focusSec=minutes*60;this.remainingSec=this.focusSec;this.mode="focus";this.paused=false;}
 start(){if(this.running)return false;if(this.mode!=="focus")this.mode="focus";if(this.remainingSec<=0)this.remainingSec=this.focusSec;this.endsAt=this.now()+this.remainingSec*1000;this.running=true;this.paused=false;this.animate("pose",750);this.emit("focus_start");return true;}
 pause(){if(!this.running)return false;this.tick();if(!this.running)return false;this.running=false;this.paused=true;this.emit("focus_pause");return true;}
 resume(){if(!this.paused||this.running)return false;this.endsAt=this.now()+this.remainingSec*1000;this.running=true;this.paused=false;this.emit("focus_resume");return true;}
 stop(){this.running=false;this.paused=false;this.remainingSec=this.focusSec;this.mode="clock";this.emit("focus_stop");}
 setAlarm(at,enabled){if(!isValidHHMM(at))throw new RangeError("invalid alarm");this.alarm={at,enabled:!!enabled};this.emit("alarm_config");}
 tick(){if(this.running){this.remainingSec=Math.max(0,Math.ceil((this.endsAt-this.now())/1000));if(this.remainingSec===0){this.running=false;this.paused=false;this.emit("focus_complete");this.animate("celebrate",1600);}}
 if(this.motionUntil && this.now()>=this.motionUntil){this.motion="idle";this.motionUntil=0;}
 if(this.alarm.enabled){const p=partsKST(this.wall());const key=p.day+"T"+p.hhmm;if(p.hhmm===this.alarm.at && key!==this.lastAlarmKey){this.lastAlarmKey=key;this.emit("alarm_fire");this.animate("celebrate",1600);}}
 return this.snapshot();}
 snapshot(){return {character:CHARACTERS[this.character],characterIndex:this.character,mode:this.mode,focusSec:this.focusSec,remainingSec:this.remainingSec,running:this.running,paused:this.paused,motion:this.motion,alarm:{...this.alarm},muted:this.muted,reducedMotion:this.reducedMotion,time:partsKST(this.wall()).display,version:this.version};}
 drain(){return this.events.splice(0);}
}
return {Engine,CHARACTERS,FOCUS_MINUTES,isValidHHMM,partsKST};
});
