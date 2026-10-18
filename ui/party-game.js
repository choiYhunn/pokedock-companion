/* PokéDock V9 — touch-first party-select microgame.
   The simulator uses PokeAPI sprites; the device LVGL port must use packaged, licensed assets. */
(() => {
  "use strict";
  const ART_BASE = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/";
  const ART = id => ART_BASE + "other/official-artwork/" + id + ".png";
  const GIF = id => ART_BASE + "versions/generation-v/black-white/animated/" + id + ".gif";
  const ICON = id => ART_BASE + "versions/generation-v/icons/" + id + ".png";
  const ROSTER = Object.freeze([
    { id:94, name:"팬텀", en:"GENGAR", role:"압도적인 1위 · 장난꾸러기", type:"GHOST / POISON", pose:"gengar",
      desc:"팬텀이 장난스럽게 웃으며 다가왔다!", line:"오늘은 나랑 놀아볼래?", sky:"#d9c4f1", glow:"#d1b4ee" },
    { id:393, name:"팽도리", en:"PIPLUP", role:"물장구치며 쉬는 시간", type:"WATER", pose:"piplup",
      desc:"팽도리가 깡충 뛰며 인사한다!", line:"한 번 더 도전해볼까?", sky:"#cae8fb", glow:"#b7dbf3" },
    { id:468, name:"토게키스", en:"TOGEKISS", role:"행복하고 포근한 분위기", type:"FAIRY / FLYING", pose:"togekiss",
      desc:"토게키스가 부드럽게 날아왔다!", line:"기분 좋은 하루가 될 거야.", sky:"#fce0ed", glow:"#e3d9f8" },
    { id:448, name:"루카리오", en:"LUCARIO", role:"오라 수련 · 집중 모드", type:"FIGHTING / STEEL", pose:"lucario",
      desc:"루카리오가 자세를 바로잡았다!", line:"집중하고 싶을 땐 날 찾아줘.", sky:"#d9e8f7", glow:"#9acaf1" },
    { id:195, name:"누오", en:"QUAGSIRE", role:"느긋한 휴식 담당", type:"WATER / GROUND", pose:"quagsire",
      desc:"누오가 느릿느릿 고개를 갸웃했다!", line:"급할 거 없어. 천천히 가자.", sky:"#d4f0ec", glow:"#b6e5d9" },
    { id:175, name:"토게피", en:"TOGEPI", role:"아침의 작은 응원", type:"FAIRY", pose:"other",
      desc:"토게피가 웃으면서 반겨준다!", line:"오늘도 좋은 아침!", sky:"#ffe5d9", glow:"#ffdab0" },
    { id:417, name:"파치리스", en:"PACHIRISU", role:"폰과 전기 친구", type:"ELECTRIC", pose:"other",
      desc:"파치리스가 꼬리를 번쩍 흔든다!", line:"휴대폰을 내려놓고 쉬어볼까?", sky:"#deefff", glow:"#b9e9fa" },
    { id:385, name:"지라치", en:"JIRACHI", role:"숨겨진 소원 친구", type:"STEEL / PSYCHIC", pose:"other",
      desc:"지라치가 작은 별을 남겼다!", line:"작은 소원을 하나 골라볼까?", sky:"#fff0c5", glow:"#f8dd91" }
  ]);
  const key = "pokedock-partner-v9";
  const state = { open:false, selected:94, entering:false, confirming:false, confirmTimer:null, petTapsSeen:0 };
  const esc = value => String(value).replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
  const bridge = () => window.__pokedockPartyBridge;
  const byId = id => ROSTER.find(item => item.id === id) || ROSTER[0];
  const element = () => document.getElementById("screen");

  function rosterMarkup() {
    return ROSTER.map((p,i) => {
      const selected = state.selected === p.id;
      return '<button class="party-choice" role="option" aria-selected="'+selected+'" tabindex="'+(selected?0:-1)+'" data-party="choose" data-id="'+p.id+'">'+
        '<span class="choice-index">'+String(i+1).padStart(2,"0")+'</span>'+
        '<img src="'+ICON(p.id)+'" alt="" loading="eager">'+
        '<span><span class="choice-name">'+p.name+'</span><span class="choice-role">'+esc(p.role)+'</span></span>'+
        '<span class="choice-mark">'+(bridge()?.getPartner?.()===p.id?"♥":selected?"▶":"")+'</span>'+
      '</button>';
    }).join("");
  }

  function stageMarkup(p) {
    const sparks = Array.from({length:7},(_,i)=>{
      const xs=[24,63,44,73,32,84,57], ys=[35,22,52,65,18,41,73];
      return '<span class="stage-spark" style="--spark-x:'+xs[i]+'%;--spark-y:'+ys[i]+'%;--spark-d:'+(i*0.37)+'s">✦</span>';
    }).join("");
    return '<section class="party-stage" aria-label="'+p.name+' 등장 애니메이션" data-mode="'+p.pose+
      '" data-enter="true" style="--party-sky:'+p.sky+';--party-glow:'+p.glow+'">'+
      '<div class="party-ribbon"><span>✧</span> No.'+String(p.id).padStart(3,"0")+' · '+p.type+'</div>'+
      '<img class="party-portrait" src="'+ART(p.id)+'" alt="" aria-hidden="true">'+
      '<div class="party-stage-rail"></div>'+
      '<div class="party-pixel-wrap"><img class="party-pixel" data-pose="'+p.pose+'" src="'+GIF(p.id)+'" alt="'+p.name+' 픽셀 스프라이트"></div>'+
      sparks+'</section>';
  }

  function markup() {
    const p=byId(state.selected);
    return '<div class="party-overlay" role="dialog" aria-modal="true" aria-label="파트너 포켓몬 선택" data-party-root>'+
      '<aside class="party-side">'+
      '<div class="party-eyebrow">✦ SINNOH · PARTY BOX</div>'+
      '<div class="party-title">파트너를 골라줘!</div>'+
      '<div class="party-subtitle">포켓몬을 터치하면 등장해요. 이름을 다시 눌러도 선택할 수 있어요.</div>'+
      '<div class="party-choices" role="listbox" aria-label="파트너 목록">'+rosterMarkup()+'</div>'+
      '<div class="party-footnote">↑ ↓ 선택 · ENTER 확정 · ESC 닫기</div></aside>'+
      '<div class="party-scene">'+
      '<button class="party-close" data-party="close" aria-label="닫기">×</button>'+
      stageMarkup(p)+
      '<div class="party-dialog"><div class="party-details">'+
      '<div class="party-meta">✦ '+p.en+' · '+p.type+'</div>'+
      '<div class="party-dialog-title">'+p.name+' <span style="color:#bc7ea9">♥</span></div>'+
      '<div class="party-dialog-line">'+esc(p.desc)+'</div></div>'+
      '<div class="party-actions"><button class="party-confirm" data-party="confirm">파트너로 선택!</button>'+
      '<button class="party-other" data-party="close">나중에 할게</button></div>'+
      '</div></div></div>';
  }

  function mount() {
    const screen=element();
    if(!screen)return;
    screen.querySelector("[data-party-root]")?.remove();
    const holder=document.createElement("div");
    holder.innerHTML=markup();
    const overlay=holder.firstElementChild;
    screen.appendChild(overlay);
    overlay.addEventListener("click", event => {
      const button=event.target.closest("button[data-party]");
      if(!button)return;
      event.stopPropagation();
      const action=button.dataset.party;
      if(action==="close")close();
      else if(action==="choose")select(Number(button.dataset.id));
      else if(action==="confirm")confirm();
    });
    overlay.querySelector(".party-pixel")?.addEventListener("error",event => {
      const img=event.currentTarget;
      img.removeAttribute("data-pose");
      img.src=ART(state.selected);
      img.style.imageRendering="auto";
    },{once:true});
    overlay.querySelectorAll(".party-choice img").forEach(img => {
      img.addEventListener("error",()=>{img.src=ART(Number(img.closest(".party-choice").dataset.id));img.style.imageRendering="auto"}, {once:true});
    });
  }

  function open() {
    if(state.open)return;
    if(!bridge()?.getPartner)return;
    state.selected=bridge().getPartner();
    state.open=true;state.confirming=false;
    mount();
    document.querySelector(".party-choice[aria-selected='true']")?.focus({preventScroll:true});
  }
  function close() {
    if(state.confirmTimer)clearTimeout(state.confirmTimer);
    state.confirmTimer=null;state.confirming=false;state.open=false;
    element()?.querySelector("[data-party-root]")?.remove();
  }
  function select(id) {
    if(!ROSTER.some(p=>p.id===id)||state.confirming)return;
    state.selected=id;
    mount();
    element()?.querySelector(".party-choice[aria-selected='true']")?.scrollIntoView({block:"nearest",behavior:"smooth"});
  }
  function confirm() {
    if(state.confirming)return;
    state.confirming=true;
    const overlay=element()?.querySelector("[data-party-root]");
    if(!overlay)return;
    overlay.classList.add("is-confirming");
    const marker=document.createElement("div");
    marker.className="party-confirmed";marker.textContent="✦ 파트너가 되었어!";
    overlay.appendChild(marker);
    state.confirmTimer=setTimeout(()=>{
      const chosen=state.selected;
      close();
      bridge()?.selectPartner?.(chosen);
    },810);
  }
  function keydown(event) {
    if(!state.open)return;
    if(event.key==="Escape"){event.preventDefault();close();return}
    const idx=ROSTER.findIndex(p=>p.id===state.selected);
    if(event.key==="ArrowDown"||event.key==="ArrowRight"){event.preventDefault();select(ROSTER[(idx+1)%ROSTER.length].id)}
    else if(event.key==="ArrowUp"||event.key==="ArrowLeft"){event.preventDefault();select(ROSTER[(idx+ROSTER.length-1)%ROSTER.length].id)}
    else if(event.key==="Enter"){event.preventDefault();confirm()}
  }
  function afterRender() {
    if(state.open){mount();return}
    const card=document.querySelector(".homegrid .partner-card");
    if(!card)return;
    const p=byId(bridge()?.getPartner?.()||94);
    card.classList.remove("poke-pet--gengar","poke-pet--piplup","poke-pet--togekiss","poke-pet--lucario","poke-pet--quagsire","poke-pet--other");
    card.classList.add("poke-pet--"+p.pose);
    const wanderer=document.createElement("img");
    wanderer.className="poke-pet-walker";
    wanderer.alt="";
    wanderer.src=GIF(p.id);
    wanderer.addEventListener("error",()=>{wanderer.src=ART(p.id);wanderer.style.imageRendering="auto"}, {once:true});
    card.appendChild(wanderer);
    const taps=bridge()?.getPetTaps?.()||0;
    if(taps>state.petTapsSeen) {
      const heart=document.createElement("span");
      heart.className="poke-pet-heart";
      heart.textContent=taps%2?"♥":"✦";
      card.appendChild(heart);
      state.petTapsSeen=taps;
    }
  }
  document.addEventListener("click",event => {
    const opener=event.target.closest("button[data-action='party-open']");
    if(!opener)return;
    event.preventDefault();
    event.stopImmediatePropagation();
    open();
  },true);
  document.addEventListener("keydown",keydown,true);
  try{
    const saved=Number(localStorage.getItem(key));
    if(ROSTER.some(p=>p.id===saved))bridge()?.selectPartner?.(saved,false);
  }catch(e){}
  window.PokeParty={open,close,afterRender,isOpen:()=>state.open,getCharacters:()=>ROSTER.map(({id,name,role})=>({id,name,role}))};
  afterRender();
})();
