// PokéDock Mobile V18 — app shell. Keeps the V17.1 screens and adds the Pokédex, arcade, richer
// timer/alarms, partner bond and the M6 Master Ball link. Pure logic lives in core.js.
import { POKEDEX, PARTNERS, byId, josa, typesEn, typesKo, artUrl, pixelUrl, reactionFor, cryUrl } from './pokedex.js';
import {
  STATE_KEY, FIRED_KEY, ALARM_SOUNDS, SNOOZE_CHOICES, MAX_ALARMS, FOCUS_PRESETS, BADGES,
  loadState, normalizeState, kstParts, kstDay, formatSeconds, formatMinutes, idleFocus, focusRemaining, startFocus, pauseFocus,
  resetFocus, advanceFocus, creditFocus, weekStats, alarmDue, nextAlarm, duplicateAlarms, m6AlarmProjection,
  bondLevel, touchVisit, addBond, PET_DAILY_CAP, newBadges, recordResult, dailyPick,
} from './core.js';
import { el, button, pokeImg, prefersReducedMotion } from './ui.js';
import { sfx, setSoundEnabled, unlockAudio } from './sfx.js';
import { createArcade } from './games/arcade.js';
import cry from './games/cry.js';
import balance from './games/balance.js';
import silhouette from './games/silhouette.js';
import memory from './games/memory.js';
import runner from './games/runner.js';
import reaction from './games/reaction.js';
import daily from './games/daily.js';
import { M6Link, M6_PARTNERS, MAX_MESSAGE_BYTES, utf8Bytes } from './ble/m6.js';

const $ = (id) => document.getElementById(id);
const APP_VERSION = '18.0.0';
const loaded = loadState(localStorage);
let state = loaded.state, fired = loaded.fired, toastTimer, bubbleTimer, gestureCount = 0, ringingAlarm = null, ringAudio = null, ringStop = 0;
const native = () => !!window.Capacitor?.isNativePlatform?.();
const Notif = () => window.Capacitor?.Plugins?.LocalNotifications || null;

function save() {
  try { localStorage.setItem(STATE_KEY, JSON.stringify(state)); }
  catch (e) { if (!save.warned) { save.warned = true; notice('저장 공간이 부족해 기록을 저장하지 못했어요. 설정 → 오프라인 콘텐츠에서 캐시를 정리해 줘.'); } }
}
function saveFired() { try { localStorage.setItem(FIRED_KEY, JSON.stringify(fired)); } catch { /* best effort */ } }
function update(fn) { fn(state); save(); }
function notice(msg) { const t = $('toast'); t.textContent = msg; t.hidden = false; clearTimeout(toastTimer); toastTimer = setTimeout(() => (t.hidden = true), 3300); }
const partner = () => byId(state.character) || byId(94);
const today = () => kstDay();

// ------------------------------------------------------------------ partner, motion, bond
const MOTIONS = ['hop', 'dance', 'peek', 'celebrate', 'wave', 'sleep'];
function motion(type) {
  for (const img of [$('hero-pokemon'), $('game-pokemon')]) {
    img.classList.remove(...MOTIONS);
    void img.offsetWidth;
    if (!prefersReducedMotion(state)) img.classList.add(type);
  }
  clearTimeout(motion.t);
  motion.t = setTimeout(() => { for (const img of [$('hero-pokemon'), $('game-pokemon')]) img.classList.remove(...MOTIONS.filter((m) => m !== 'sleep')); }, type === 'sleep' ? 2600 : 1450);
  if (type === 'sleep') setTimeout(() => { for (const img of [$('hero-pokemon'), $('game-pokemon')]) img.classList.remove('sleep'); }, 2600);
}
function say(text, ms = 2600) {
  for (const id of ['hero-bubble', 'stage-bubble']) { const b = $(id); b.textContent = text; b.hidden = false; }
  clearTimeout(bubbleTimer);
  bubbleTimer = setTimeout(() => { $('hero-bubble').hidden = true; $('stage-bubble').hidden = true; }, ms);
}

function setImage(img, id, style) {
  const p = byId(id);
  const chain = style === 'pixel' ? [pixelUrl(id), `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/showdown/${id}.gif`, artUrl(id)] : [artUrl(id)];
  let i = 0;
  img.onerror = () => {
    i++;
    if (i < chain.length) { img.src = chain[i]; img.classList.toggle('pixel', i < 2 && style === 'pixel'); return; }
    img.onerror = null;
    img.alt = '이미지를 불러오지 못했어요. 인터넷 연결을 확인해 주세요';
    img.removeAttribute('src');
  };
  img.onload = () => { if (img.id === 'game-pokemon') sizePixelSprite(); };
  img.classList.toggle('pixel', style === 'pixel');
  img.alt = p?.name || '포켓몬';
  img.src = chain[0];
}
function sizePixelSprite() {
  const img = $('game-pokemon');
  if (!img.classList.contains('pixel')) { img.style.removeProperty('width'); img.style.removeProperty('height'); return; }
  const box = img.parentElement.getBoundingClientRect();
  if (!box.width || !box.height) return;
  const [w, h] = partner().pixel || [img.naturalWidth || 64, img.naturalHeight || 64];
  const scale = Math.max(1, Math.min(3, Math.floor((box.width * 0.78) / w), Math.floor((box.height * 0.75) / h)));
  img.style.width = `${w * scale}px`;
  img.style.height = `${h * scale}px`;
}

function renderCharacter() {
  const c = partner();
  setImage($('hero-pokemon'), c.id, 'art');
  setImage($('game-pokemon'), c.id, state.style);
  $('partner-name').textContent = c.name;
  $('partner-type').textContent = typesEn(c);
  $('partner-line').textContent = c.line;
  $('partner-index').textContent = 'NO. ' + String(c.id).padStart(3, '0');
  $('daily-title').textContent = `${josa(c.name, '이랑', '랑')} 보내는 하루`;
  $('mode-tag').textContent = c.en + ' IS HERE';
  $('daily-subtitle').textContent = c.line;
  for (const b of document.querySelectorAll('#roster [data-id]')) b.classList.toggle('selected', Number(b.dataset.id) === state.character);
  for (const b of document.querySelectorAll('#style-switch [data-style]')) b.classList.toggle('selected', b.dataset.style === state.style);
  sizePixelSprite();
}

function renderBond() {
  const b = state.bond, lv = bondLevel(b.points);
  $('bond-level').textContent = `친밀도 Lv.${lv.level}`;
  $('bond-days').textContent = b.daysTogether <= 1 ? '오늘 처음 만났어 ♡' : `함께한 지 ${b.daysTogether}일째${b.streak >= 2 ? ` · ${b.streak}일 연속` : ''}`;
  $('bond-fill').style.width = `${Math.round(lv.progress * 100)}%`;
  $('bond-pets').textContent = `쓰다듬기 ${b.petDay === today() ? b.petsToday : 0}/${PET_DAILY_CAP}`;
}

function award(reason, amount) {
  const pts = amount ?? { pet: 1, focus: 2, game: 1, daily: 3, discover: 1 }[reason] ?? 1;
  const before = bondLevel(state.bond.points).level;
  const r = addBond(state.bond, pts, reason, today());
  state.bond = r.bond;
  const after = bondLevel(state.bond.points).level;
  checkBadges();
  save();
  renderBond();
  if (after > before) { notice(`${josa(partner().name, '과', '와')} 더 친해졌어! 친밀도 Lv.${after} ♡`); motion('celebrate'); }
  return r.gained;
}
function checkBadges() {
  const r = newBadges(state, today());
  state.badges = r.badges;
  for (const b of r.earned) setTimeout(() => notice(`${b.icon} 배지 획득 · ${b.name}`), 600);
}
function discover(id) {
  if (state.discovered[id]) return;
  state.discovered[id] = today();
  award('discover');
  notice(`새 친구 발견! 도감에 ${byId(id)?.name} 등록 ✦`);
}

function handlePet() {
  unlockAudio();
  gestureCount++;
  state.petCount++;
  const c = partner();
  if (gestureCount >= 5) {
    gestureCount = 0;
    state.secretUnlocked = true;
    save();
    openMemories();
    notice('✧ 팬텀의 비밀 공간이 열렸어!');
    return;
  }
  const gained = award('pet');
  const kst = kstParts();
  if (c.id === 94 && (kst.hour >= 22 || kst.hour < 4) && !state.flags.nightGengar) { state.flags.nightGengar = true; checkBadges(); save(); }
  motion(c.behavior);
  say(reactionFor(c, state.petCount));
  if (!gained && gestureCount === 1) notice('오늘은 충분히 쓰다듬어 줬어. 그래도 좋아해! ♡');
}

// ------------------------------------------------------------------ clock & special days
function specialDay() {
  const p = kstParts();
  if (state.birthday && state.birthday === p.mmdd) return 'birthday';
  if (state.anniversary && state.anniversary.slice(5) === p.mmdd) return 'anniversary';
  return '';
}
function renderClock() {
  const p = kstParts();
  $('hero-clock').textContent = p.hhmm;
  $('date-line').textContent = `${p.weekdayName} · ${p.display}`;
  const sp = specialDay();
  $('greeting').textContent = sp === 'birthday' ? '생일 축하해! 오늘은 네가 주인공 🎂' : sp === 'anniversary' ? '오늘은 우리의 기념일이야 ♡' : p.minute < 12 * 60 ? '오늘도 좋은 하루 보내 ♡' : p.minute < 19 * 60 ? '잠깐 쉬어도 좋아 ♡' : '오늘도 수고했어 ♡';
  $('easter-text').textContent = sp ? '오늘을 위해 준비한 메시지가 있어 ✦' : '너에게만 보여줄 작은 선물이 있어';
}

// ------------------------------------------------------------------ focus timer
function timerCfg() { return state.timer; }
function renderFocus() {
  const f = state.focus;
  const sec = focusRemaining(f);
  $('focus-clock').textContent = formatSeconds(sec);
  const pomo = f.mode === 'pomodoro';
  $('focus-eyebrow').textContent = pomo ? (f.phase === 'focus' ? `FOCUS ${f.cycle}/${state.timer.pomodoro.cycles}` : f.phase === 'long' ? 'LONG BREAK' : 'BREAK TIME') : 'FOCUS TIME';
  const fresh = !f.running && sec === f.totalSec;
  $('focus-start').textContent = f.running ? '일시정지' : !fresh ? '계속하기' : f.phase === 'focus' ? '집중 시작' : '휴식 시작';
  for (const b of document.querySelectorAll('[data-focus]')) b.classList.toggle('active', !pomo && Number(b.dataset.focus) === f.minutes);
  $('focus-more').classList.toggle('active', pomo || !FOCUS_PRESETS.includes(f.minutes));
  $('focus-more').textContent = pomo ? '🍅' : FOCUS_PRESETS.includes(f.minutes) ? '⋯' : String(f.minutes);
  const d = state.stats.days[today()] || { min: 0, sessions: 0 };
  $('focus-caption').textContent = f.running && f.phase === 'focus' ? `${josa(partner().name, '이', '가')} 옆에서 응원 중 ♡` : f.running ? '쉬는 시간도 소중해 ♡' : `오늘 ${formatMinutes(d.min)} · ${d.sessions}세션`;
  $('focus-tile').classList.toggle('running', f.running);
}
function m6Focus(action) {
  if (!m6.connected) return;
  const minutes = Math.ceil(state.focus.totalSec / 60);
  m6.focus(action, minutes).then((r) => { if (!r.ok) notice('마스터볼 동기화 실패 · ' + r.text.split('·').pop().trim()); });
}
function scheduleTimerNotification() {
  const N = Notif();
  if (!native() || !N) return;
  N.cancel({ notifications: [{ id: 20001 }] }).catch(() => {});
  const f = state.focus;
  if (!f.running) return;
  N.schedule({ notifications: [{ id: 20001, title: f.phase === 'focus' ? 'PokéDock · 집중 완료!' : 'PokéDock · 휴식 끝', body: f.phase === 'focus' ? `${josa(partner().name, '이', '가')} 박수 치고 있어요 ♡` : '준비되면 다시 시작해요', schedule: { at: new Date(f.endAt), allowWhileIdle: true } }] }).catch(() => {});
}
function focusToggle() {
  unlockAudio();
  const now = Date.now();
  const f = state.focus;
  if (f.running) {
    state.focus = pauseFocus(f, now);
    if (f.phase === 'focus') m6Focus('pause');
  } else {
    const fresh = focusRemaining(f, now) === f.totalSec;
    state.focus = startFocus(f, now);
    if (state.focus.phase === 'focus') {
      m6Focus(fresh ? 'start' : 'resume');
      if (fresh) { say(['같이 집중하자! 끝나면 칭찬해 줄게.', '할 수 있어, 천천히 한 걸음씩!', '옆에서 조용히 응원할게 ♡'][state.stats.sessions % 3]); motion('wave'); }
    }
  }
  save();
  scheduleTimerNotification();
  renderFocus();
}
function focusReset() {
  const r = resetFocus(state.focus, timerCfg());
  if (r.creditMin) state.stats = creditFocus(state.stats, Date.now(), r.creditMin, false);
  const wasActive = state.focus.phase === 'focus' && (state.focus.running || state.focus.remainingSec !== state.focus.totalSec);
  state.focus = r.focus;
  save();
  if (wasActive) m6Focus('cancel');
  scheduleTimerNotification();
  renderFocus();
  if (r.creditMin) notice(`${r.creditMin}분 집중한 것도 기록해 뒀어 ♡`);
}
function setSingle(minutes) {
  if (state.focus.running) { notice('타이머가 도는 중이에요. 초기화한 뒤 바꿔 줘.'); return; }
  state.focusMinutes = minutes;
  state.timer.mode = 'single';
  state.focus = idleFocus('single', minutes, timerCfg());
  save();
  renderFocus();
}
function setPomodoro() {
  if (state.focus.running) { notice('타이머가 도는 중이에요. 초기화한 뒤 바꿔 줘.'); return; }
  state.timer.mode = 'pomodoro';
  state.focus = idleFocus('pomodoro', state.focusMinutes, timerCfg());
  save();
  renderFocus();
}
function processFocus(now = Date.now()) {
  const r = advanceFocus(state.focus, timerCfg(), now);
  if (!r.events.length) return;
  state.focus = r.focus;
  for (const ev of r.events) {
    if (ev.type === 'focusDone') {
      state.stats = creditFocus(state.stats, ev.at, ev.minutes, true);
      award('focus');
      motion('celebrate');
      say(`${ev.minutes}분 집중 완료! 정말 대단해 ♡`, 4000);
      notice(state.focus.mode === 'pomodoro' && state.focus.running ? `집중 완료! ${state.focus.phase === 'long' ? '긴 ' : ''}휴식을 시작할게요.` : `집중 완료! ${josa(partner().name, '이', '가')} 응원해 ♡`);
      if (state.sound && !native()) sfx('match', 0.09);
      if (navigator.vibrate) navigator.vibrate([90, 60, 90]);
    } else notice(ev.long ? '긴 휴식 끝! 새 세트를 시작해 볼까?' : '휴식 끝! 준비되면 다시 집중해요.');
  }
  checkBadges();
  save();
  scheduleTimerNotification();
}

function openTimerSheet() {
  const body = el('div', 'timer-sheet');
  const t = state.timer;
  const modeRow = el('div', 'seg');
  const single = button('한 번 집중', state.focus.mode === 'single' ? 'selected' : '', () => { setSingle(t.custom && !FOCUS_PRESETS.includes(state.focus.minutes) ? state.focus.minutes : state.focusMinutes); openTimerSheet(); });
  const pomo = button('포모도로', state.focus.mode === 'pomodoro' ? 'selected' : '', () => { setPomodoro(); openTimerSheet(); });
  modeRow.append(single, pomo);
  body.append(el('span', 'eyebrow', 'MODE'), modeRow);
  if (state.focus.running) body.append(el('p', 'setup-problem', '타이머가 도는 중에는 설정을 바꿀 수 없어요. 일시정지 후 초기화해 줘.'));

  const stepper = (label, value, lo, hi, step, onChange) => {
    const row = el('div', 'stepper-row');
    const out = el('b', '', `${value}분`);
    const set = (v) => { value = Math.max(lo, Math.min(hi, v)); out.textContent = `${value}분`; onChange(value); };
    row.append(el('span', '', label), button('－', 'step', () => set(value - step), { 'aria-label': `${label} 줄이기` }), out, button('＋', 'step', () => set(value + step), { 'aria-label': `${label} 늘리기` }));
    return row;
  };
  if (state.focus.mode === 'single') {
    body.append(el('span', 'eyebrow', 'CUSTOM'));
    const custom = stepper('집중 시간', state.focus.minutes, 1, 120, 5, (v) => { t.custom = v; setSingle(v); });
    const chips = el('div', 'chip-row');
    for (const m of [5, 10, 30, 60, 90]) chips.append(button(`${m}분`, 'chip', () => { t.custom = m; setSingle(m); openTimerSheet(); }));
    body.append(custom, chips);
  } else {
    const p = t.pomodoro;
    body.append(el('span', 'eyebrow', 'POMODORO'));
    const change = (k) => (v) => { p[k] = v; if (!state.focus.running) state.focus = idleFocus('pomodoro', state.focusMinutes, t, state.focus.cycle, state.focus.phase); save(); renderFocus(); };
    body.append(stepper('집중', p.focus, 5, 90, 5, change('focus')), stepper('휴식', p.brk, 1, 30, 1, change('brk')), stepper('긴 휴식', p.long, 5, 45, 5, change('long')));
    const cyc = el('div', 'stepper-row');
    const cout = el('b', '', `${p.cycles}세트`);
    cyc.append(el('span', '', '긴 휴식까지'), button('－', 'step', () => { p.cycles = Math.max(2, p.cycles - 1); cout.textContent = `${p.cycles}세트`; change('cycles')(p.cycles); }), cout, button('＋', 'step', () => { p.cycles = Math.min(8, p.cycles + 1); cout.textContent = `${p.cycles}세트`; change('cycles')(p.cycles); }));
    const auto = el('label', 'sheet-row');
    const ab = el('input', '', '', { type: 'checkbox' });
    ab.checked = p.autoBreak;
    ab.onchange = () => { p.autoBreak = ab.checked; save(); };
    auto.append(el('b', '', '집중이 끝나면 휴식 자동 시작'), ab);
    body.append(cyc, auto, el('p', '', '25분 집중 → 5분 휴식을 반복하고, 정해진 세트마다 긴 휴식을 가져요. 휴식이 끝나면 다음 집중은 버튼을 눌러 시작해요.'));
  }
  // statistics
  const week = weekStats(state.stats);
  const maxMin = Math.max(30, ...week.map((d) => d.min));
  const chart = el('div', 'week-chart', '', { role: 'img', 'aria-label': '최근 7일 집중 시간: ' + week.map((d) => `${'일월화수목금토'[d.weekday]} ${d.min}분`).join(', ') });
  for (const d of week) {
    const col = el('span', 'week-col' + (d.day === today() ? ' today' : ''));
    const bar = el('i');
    bar.style.height = `${Math.max(3, Math.round((d.min / maxMin) * 100))}%`;
    col.append(el('small', '', d.min ? String(d.min) : ''), bar, el('em', '', '일월화수목금토'[d.weekday]));
    chart.append(col);
  }
  const td = state.stats.days[today()] || { min: 0, sessions: 0 };
  const weekMin = week.reduce((a, d) => a + d.min, 0);
  const stats = el('div', 'stat-row');
  for (const [k, v] of [['오늘', formatMinutes(td.min)], ['이번 주', formatMinutes(weekMin)], ['누적', formatMinutes(state.stats.totalMin)], ['완료 세션', `${state.stats.sessions}회`]]) {
    const s = el('span', 'stat');
    s.append(el('small', '', k), el('b', '', v));
    stats.append(s);
  }
  body.append(el('span', 'eyebrow', 'MY FOCUS'), stats, chart, el('p', '', weekMin ? '조금씩 쌓인 시간이 보여? 무리하지 말고 쉬엄쉬엄 ♡' : '아직 기록이 없어요. 5분부터 가볍게 시작해 볼까?'));
  if (native()) body.append(el('p', 'setup-note', '앱이 백그라운드에 있어도 종료 알림이 예약돼요. 기기 절전 설정에 따라 늦을 수 있어요.'));
  else body.append(el('p', 'setup-note', '타이머는 종료 시각을 저장해서 화면을 잠그거나 앱을 다시 열어도 남은 시간을 정확히 다시 계산해요. 웹앱은 화면이 꺼져 있을 때 소리 알림을 보낼 수 없어요.'));
  openSheet('집중 타이머', body);
}

// ------------------------------------------------------------------ alarms
let nativePermissionAsked = false, previewAudio;
const soundFor = (id) => ALARM_SOUNDS.find((s) => s.id === id) || ALARM_SOUNDS[0];
function playAlarmSound(id, loop = false) {
  try {
    previewAudio?.pause();
    previewAudio = new Audio('assets/sounds/' + soundFor(id).file);
    previewAudio.loop = loop;
    previewAudio.play().catch(() => {});
    return previewAudio;
  } catch { return null; }
}
const weekdayKo = (days) => (days.length === 7 ? '매일' : days.length === 5 && [1, 2, 3, 4, 5].every((d) => days.includes(d)) ? '평일' : days.length === 2 && days.includes(0) && days.includes(6) ? '주말' : days.map((d) => '일월화수목금토'[d]).join(' '));
function nextAlarmText(n) {
  if (!n) return { time: '--:--', desc: '알람을 설정해 줘' };
  const h = Math.floor(n.inMin / 60), m = n.inMin % 60;
  const rel = n.inMin < 60 ? `${n.inMin}분 후` : `${h}시간${m ? ` ${m}분` : ''} 후`;
  return { time: n.alarm.time, desc: `${n.today ? '오늘' : '다음'} ${n.alarm.title} · ${rel}` };
}
function renderAlarm() {
  const t = nextAlarmText(nextAlarm(state.alarms));
  $('alarm-next').textContent = t.time;
  $('alarm-summary').textContent = t.desc;
}

async function cancelNativeAlarms() {
  const N = Notif();
  if (!N) return;
  const ids = [];
  for (let i = 0; i < MAX_ALARMS; i++) { for (let d = 0; d < 7; d++) ids.push({ id: 10000 + i * 20 + d }); ids.push({ id: 19000 + i }); }
  await N.cancel({ notifications: ids });
}
async function registerNativeExtras(N) {
  if (registerNativeExtras.done) return;
  registerNativeExtras.done = true;
  try {
    await N.registerActionTypes({ types: [{ id: 'POKEDOCK_ALARM', actions: [{ id: 'snooze', title: '조금만 더' }, { id: 'dismiss', title: '끄기', destructive: true }] }] });
    N.addListener('localNotificationActionPerformed', (e) => {
      const alarm = state.alarms.find((a) => a.id === e.notification?.extra?.alarmId);
      if (!alarm) return;
      if (e.actionId === 'snooze') scheduleSnooze(alarm);
      else if (e.actionId === 'tap') showRinging(alarm, false);
    });
  } catch { /* older plugin: plain notifications still work */ }
}
async function syncNativeAlarms() {
  const N = Notif();
  if (!N) return false;
  try {
    const perm = await N.checkPermissions();
    if (perm.display !== 'granted') {
      if (nativePermissionAsked) return false;
      nativePermissionAsked = true;
      const p = await N.requestPermissions();
      if (p.display !== 'granted') { notice('알림 권한이 꺼져 있어요. 시스템 설정을 확인해 주세요.'); return false; }
    }
    await registerNativeExtras(N);
    await cancelNativeAlarms();
    const android = window.Capacitor?.getPlatform?.() === 'android';
    if (android && typeof N.createChannel === 'function') {
      for (const s of ALARM_SOUNDS) await N.createChannel({ id: `pokedock_alarm_${s.id}_v1`, name: `PokéDock · ${s.name}`, importance: 4, visibility: 1, sound: s.file });
      await N.createChannel({ id: 'pokedock_alarm_quiet_v1', name: 'PokéDock · 조용한 알람', importance: 2, visibility: 1, vibration: true });
    }
    const list = [];
    state.alarms.forEach((a, i) => {
      if (!a.on) return;
      const [hour, minute] = a.time.split(':').map(Number);
      const s = soundFor(a.sound);
      for (const day of a.days) {
        list.push({
          id: 10000 + i * 20 + day, title: `PokéDock · ${a.title}`, body: `${josa(byId(a.pokemon)?.name || '파트너', '이', '가')} 기다리고 있어요 ♡`,
          schedule: { on: { weekday: day + 1, hour, minute, second: 0 }, allowWhileIdle: true }, actionTypeId: 'POKEDOCK_ALARM', extra: { alarmId: a.id },
          ...(a.quiet ? {} : { sound: s.file }),
          ...(android ? { channelId: a.quiet ? 'pokedock_alarm_quiet_v1' : `pokedock_alarm_${s.id}_v1`, smallIcon: 'ic_stat_name' } : {}),
        });
      }
    });
    if (list.length) await N.schedule({ notifications: list });
    const exact = android && typeof N.checkExactNotificationSetting === 'function' ? await N.checkExactNotificationSetting() : null;
    notice(`반복 알림 ${list.length}개 등록${exact?.exact_alarm === 'denied' ? ' · 정확한 알람 권한을 켜 줘.' : '됐어.'}`);
    return true;
  } catch (e) { notice('알람 등록 확인 필요: ' + String(e?.message || e).slice(0, 90)); return false; }
}
async function scheduleSnooze(alarm) {
  const at = Date.now() + alarm.snooze * 60000;
  update((s) => { s.snoozes = [...s.snoozes.filter((z) => z.id !== alarm.id), { id: alarm.id, at }]; });
  const N = Notif();
  if (native() && N) {
    const i = state.alarms.indexOf(alarm);
    await N.schedule({ notifications: [{ id: 19000 + Math.max(0, i), title: `PokéDock · ${alarm.title}`, body: `${alarm.snooze}분 지났어요! 이번엔 일어나 볼까?`, schedule: { at: new Date(at), allowWhileIdle: true }, actionTypeId: 'POKEDOCK_ALARM', extra: { alarmId: alarm.id } }] }).catch(() => {});
  }
  notice(`${alarm.snooze}분 뒤에 다시 깨울게요.`);
}

let m6AlarmTimer = 0;
function alarmsChanged() {
  save();
  renderAlarm();
  checkBadges();
  if (m6.connected && state.m6.autoSync) {
    clearTimeout(m6AlarmTimer);
    m6AlarmTimer = setTimeout(() => sendM6Alarm(true), 1200);
  }
}
async function sendM6Alarm(quiet) {
  const proj = m6AlarmProjection(state.alarms);
  const r = await m6.setAlarm(proj);
  if (!quiet || !r.ok) notice(r.ok ? (proj.en ? `마스터볼에 ${proj.title} (${String(proj.h).padStart(2, '0')}:${String(proj.m).padStart(2, '0')}) 전송 완료` : '24시간 안에 알람이 없어서 마스터볼 알람을 껐어요.') : r.text);
  return r;
}

function openAlarmSheet() {
  const body = el('div');
  const n = nextAlarm(state.alarms);
  const head = el('div', 'alarm-head');
  const nt = nextAlarmText(n);
  head.append(el('span', 'eyebrow', 'NEXT ALARM'), el('b', '', n ? `${nt.time} · ${weekdayKo([kstParts(n.at).weekday])}요일` : '켜진 알람이 없어요'), el('small', '', n ? nt.desc : '알람을 켜면 여기서 알려 줄게.'));
  body.append(head);
  body.append(el('p', '', native()
    ? '시간·요일·소리를 고른 뒤 “기기에 알람 적용”을 눌러 줘. 알림 권한·정확한 알람 권한·절전 설정에 따라 늦어질 수 있어.'
    : '웹앱 알람은 이 화면이 열려 있을 때만 울려요. 화면이 잠기거나 앱이 닫히면 울리지 않아요. 확실한 기상 알람은 네이티브 앱이나 휴대폰 기본 시계를 같이 써 줘.'));
  const warn = el('p', 'setup-problem', '', { 'aria-live': 'polite' });
  const list = el('div');
  body.append(warn, list);
  const apply = button('기기에 알람 적용', 'btn solid', async () => { if (await syncNativeAlarms()) apply.textContent = '기기에 적용됨'; });
  const changed = () => { alarmsChanged(); if (native()) apply.textContent = '변경사항 기기에 적용'; paintWarn(); };
  const paintWarn = () => {
    const d = duplicateAlarms(state.alarms);
    warn.textContent = d.size ? `같은 시각·요일에 켜진 알람이 있어요: ${state.alarms.filter((a) => d.has(a.id)).map((a) => a.title).join(', ')}. 한 번만 울리도록 하나를 꺼 줘.` : '';
    warn.hidden = !d.size;
  };
  const sel = (label, options, value, onChange) => {
    const s = el('select', '', '', { 'aria-label': label });
    for (const [v, t] of options) { const o = el('option', '', t, { value: String(v) }); s.append(o); }
    s.value = String(value);
    s.onchange = () => onChange(s.value);
    return s;
  };
  function draw() {
    list.replaceChildren();
    state.alarms.forEach((alarm, i) => {
      const arm = () => { alarm.armedAt = Date.now(); };
      const card = el('div', 'alarm-card' + (alarm.on ? '' : ' off'));
      const top = el('div', 'alarm-top');
      const face = el('span', 'alarm-face');
      face.append(pokeImg(alarm.pokemon, { cls: 'alarm-face-img' }));
      const title = el('input', '', '', { type: 'text', maxlength: '32', 'aria-label': `${i + 1}번 알람 이름` });
      title.value = alarm.title;
      title.onchange = () => { alarm.title = title.value.trim() || '새 알람'; changed(); };
      const toggle = el('input', 'switch', '', { type: 'checkbox', role: 'switch', 'aria-label': alarm.title + ' 사용' });
      toggle.checked = alarm.on;
      toggle.onchange = () => { alarm.on = toggle.checked; arm(); card.classList.toggle('off', !alarm.on); changed(); };
      top.append(face, title, toggle);
      const time = el('input', '', '', { type: 'time', 'aria-label': alarm.title + ' 시간' });
      time.value = alarm.time;
      time.onchange = () => { if (/^([01]\d|2[0-3]):[0-5]\d$/.test(time.value)) { alarm.time = time.value; arm(); changed(); } };
      const days = el('div', 'weekday-picker', '', { role: 'group', 'aria-label': alarm.title + ' 반복 요일' });
      ['일', '월', '화', '수', '목', '금', '토'].forEach((label, day) => {
        const b = button(label, alarm.days.includes(day) ? 'selected' : '', () => {
          alarm.days = alarm.days.includes(day) ? alarm.days.filter((x) => x !== day) : [...alarm.days, day].sort();
          b.classList.toggle('selected', alarm.days.includes(day));
          b.setAttribute('aria-pressed', String(alarm.days.includes(day)));
          arm();
          changed();
        }, { 'aria-pressed': String(alarm.days.includes(day)) });
        days.append(b);
      });
      const grid = el('div', 'alarm-grid');
      const pk = sel(alarm.title + ' 포켓몬', POKEDEX.map((p) => [p.id, p.name]), alarm.pokemon, (v) => { alarm.pokemon = Number(v); face.replaceChildren(pokeImg(alarm.pokemon, { cls: 'alarm-face-img' })); changed(); });
      const snd = sel(alarm.title + ' 알람 소리', ALARM_SOUNDS.map((s) => [s.id, s.name]), alarm.sound, (v) => { alarm.sound = v; changed(); });
      const snz = sel(alarm.title + ' 다시 알림', SNOOZE_CHOICES.map((m) => [m, m ? `${m}분 뒤 다시` : '다시 알림 없음']), alarm.snooze, (v) => { alarm.snooze = Number(v); changed(); });
      const quiet = sel(alarm.title + ' 알람 종류', [['0', '일반 알람'], ['1', '조용한 알람 (진동·화면)']], alarm.quiet ? 1 : 0, (v) => { alarm.quiet = v === '1'; changed(); });
      grid.append(labelled('포켓몬', pk), labelled('소리', snd), labelled('스누즈', snz), labelled('종류', quiet));
      const actions = el('div', 'alarm-sound-row');
      actions.append(button('▶ 미리 듣기', 'btn text-btn', () => (alarm.quiet ? (navigator.vibrate?.([120, 80, 120]), notice('조용한 알람은 진동과 화면으로만 알려요.')) : playAlarmSound(alarm.sound))),
        button('아침 화면 보기', 'btn text-btn', () => { closeSheet(); showRinging(alarm, true); }),
        button('삭제', 'alarm-remove', () => { state.alarms.splice(i, 1); changed(); draw(); }));
      card.append(top, time, days, grid, actions);
      list.append(card);
    });
    add.disabled = state.alarms.length >= MAX_ALARMS;
    add.textContent = state.alarms.length >= MAX_ALARMS ? `알람은 최대 ${MAX_ALARMS}개까지` : '＋ 알람 추가';
  }
  function labelled(t, control) { const l = el('label', 'mini-field'); l.append(el('small', '', t), control); return l; }
  const add = button('＋ 알람 추가', 'btn light', () => {
    state.alarms.push({ id: 'custom_' + Date.now(), title: '새 알람', time: '09:00', days: [0, 1, 2, 3, 4, 5, 6], on: true, sound: 'dawn', pokemon: state.character, snooze: 5, quiet: false, armedAt: Date.now() });
    changed();
    draw();
  });
  body.append(add);
  if (native()) body.append(apply);
  // M6 section
  const m6box = el('div', 'm6-inline');
  const proj = m6AlarmProjection(state.alarms);
  m6box.append(el('b', '', '마스터볼 M6 알람'), el('p', '', `현재 M6 펌웨어(프로토콜 v2)는 매일 울리는 알람 1개만 저장해요. 그래서 앱은 24시간 안에 울릴 다음 알람만 보내고, 연결할 때마다 다시 맞춰요. 지금 보낼 값: ${proj.en ? `${proj.title} ${String(proj.h).padStart(2, '0')}:${String(proj.m).padStart(2, '0')}` : '알람 끄기'}`));
  const sendBtn = button(m6.connected ? '마스터볼에 다음 알람 보내기' : '마스터볼이 연결되어 있지 않아요', 'btn light', async () => { sendBtn.disabled = true; await sendM6Alarm(false); sendBtn.disabled = false; });
  sendBtn.disabled = !m6.connected;
  m6box.append(sendBtn);
  body.append(m6box);
  draw();
  paintWarn();
  openSheet('알람 관리', body);
}

function showRinging(alarm, preview) {
  ringingAlarm = { alarm, preview };
  const p = byId(alarm.pokemon) || partner();
  const kst = kstParts();
  $('ring-time').textContent = preview ? alarm.time : kst.hhmm;
  $('ring-eyebrow').textContent = preview ? 'PREVIEW · 미리 보기' : kst.hour < 12 ? 'GOOD MORNING' : kst.hour < 18 ? 'HELLO' : 'GOOD EVENING';
  $('ring-title').textContent = alarm.title;
  $('ring-line').textContent = kst.hour < 12 ? `좋은 아침! ${p.name}: “${p.line}”` : `${p.name}: “${p.line}”`;
  $('ring-art').replaceChildren(pokeImg(p.id, { cls: 'ring-img' + (prefersReducedMotion(state) ? '' : ' celebrate') }));
  $('ring-snooze').hidden = !alarm.snooze;
  $('ring-snooze').textContent = `${alarm.snooze}분만 더`;
  $('ringing').hidden = false;
  $('ring-dismiss').focus();
  ringAudio?.pause();
  ringAudio = null;
  if (!alarm.quiet && !native()) ringAudio = playAlarmSound(alarm.sound, true);
  if (navigator.vibrate) navigator.vibrate(alarm.quiet ? [200, 100, 200, 100, 200] : [120, 80, 120]);
  clearTimeout(ringStop);
  ringStop = setTimeout(() => { ringAudio?.pause(); }, 2 * 60 * 1000); // like the M6: stop after 2 minutes
}
function stopRinging(snooze) {
  ringAudio?.pause();
  ringAudio = null;
  clearTimeout(ringStop);
  $('ringing').hidden = true;
  if (!ringingAlarm) return;
  const { alarm, preview } = ringingAlarm;
  ringingAlarm = null;
  if (preview) return;
  if (snooze) scheduleSnooze(alarm);
  else {
    update((s) => { s.snoozes = s.snoozes.filter((z) => z.id !== alarm.id); });
    say('오늘 하루도 같이 힘내자!');
  }
  if (m6.connected && m6.deviceState?.alarm.ringing) m6.run(snooze ? '마스터볼 스누즈' : '마스터볼 알람 끄기', (c) => (snooze ? c.snoozeAlarm() : c.dismissAlarm()));
}
function updateAlarms(now = Date.now()) {
  for (const item of alarmDue(state.alarms, now, fired)) {
    fired[item.alarm.id] = item.key;
    saveFired();
    if (!ringingAlarm) showRinging(item.alarm, false);
  }
  const due = state.snoozes.filter((z) => z.at <= now);
  if (due.length) {
    update((s) => { s.snoozes = s.snoozes.filter((z) => z.at > now); });
    for (const z of due) { const a = state.alarms.find((x) => x.id === z.id); if (a && !ringingAlarm) showRinging(a, false); }
  }
}

// ------------------------------------------------------------------ sheets
function openSheet(title, content) {
  const inner = $('sheet-inner');
  inner.replaceChildren(el('h2', '', title));
  inner.append(typeof content === 'string' ? el('p', '', content) : content);
  if ($('sheet').hidden) openSheet.lastFocus = document.activeElement;
  $('sheet').hidden = false;
  $('sheet-backdrop').hidden = false;
  $('sheet').scrollTop = 0;
  $('sheet-close').focus({ preventScroll: true });
}
function closeSheet() {
  $('sheet').hidden = true;
  $('sheet-backdrop').hidden = true;
  openSheet.lastFocus?.focus?.({ preventScroll: true });
}

// ---- Pokédex
let dexFilter = 'all';
function openDex() {
  const body = el('div', 'dex');
  const found = POKEDEX.filter((p) => state.discovered[p.id]).length;
  body.append(el('p', '', `발견한 친구 ${found} / ${POKEDEX.length} · ♡ 좋아요 ${state.favorites.length}. 게임에서 만나면 도감에 기록돼요.`));
  const filters = el('div', 'chip-row', '', { role: 'tablist', 'aria-label': '도감 보기' });
  for (const [k, t] of [['all', '전체'], ['partner', 'M6 파트너'], ['fav', '좋아요'], ['found', '발견']]) {
    filters.append(button(t, 'chip' + (dexFilter === k ? ' selected' : ''), () => { dexFilter = k; openDex(); }, { role: 'tab', 'aria-selected': String(dexFilter === k) }));
  }
  body.append(filters);
  const grid = el('div', 'dex-grid');
  const list = POKEDEX.filter((p) => dexFilter === 'all' || (dexFilter === 'partner' && p.partner) || (dexFilter === 'fav' && state.favorites.includes(p.id)) || (dexFilter === 'found' && state.discovered[p.id]));
  for (const p of list) {
    const known = !!state.discovered[p.id];
    const card = button('', 'dex-card' + (p.id === state.character ? ' current' : '') + (known ? '' : ' unknown'), () => openDexDetail(p.id), { 'aria-label': known ? `${p.name} 자세히 보기` : `${String(p.id).padStart(3, '0')}번 아직 만나지 못한 친구` });
    card.style.setProperty('--pc', p.color);
    card.append(pokeImg(p.id, { cls: 'dex-img' + (known ? '' : ' silhouette'), alt: '' }), el('small', 'dex-no', '#' + String(p.id).padStart(3, '0')), el('b', '', known ? p.name : '???'));
    if (state.favorites.includes(p.id)) card.append(el('span', 'dex-fav', '♥', { 'aria-hidden': 'true' }));
    if (p.partner) card.append(el('span', 'dex-m6', 'M6', { title: '마스터볼 M6 지원' }));
    grid.append(card);
  }
  if (!list.length) grid.append(el('p', 'setup-note', dexFilter === 'fav' ? '아직 ♥ 누른 친구가 없어요.' : '해당하는 친구가 없어요.'));
  body.append(grid);
  openSheet('포켓몬 도감', body);
}
function openDexDetail(id) {
  const p = byId(id);
  const known = !!state.discovered[id];
  const body = el('div', 'dex-detail');
  body.append(button('← 도감 목록', 'btn text-btn back-link', openDex));
  const stage = el('div', 'dex-stage');
  stage.style.setProperty('--pc', p.color);
  const preview = pokeImg(id, { kind: known ? 'pixel' : 'art', cls: 'dex-preview' + (known ? '' : ' silhouette') });
  stage.append(preview);
  body.append(stage);
  if (!known) {
    body.append(el('h3', '', `No. ${String(id).padStart(3, '0')} · ???`), el('p', '', '아직 만나지 못한 친구예요. 울음소리 퀴즈·실루엣 퀴즈·오늘의 포켓몬에서 만나면 도감에 기록돼요.'));
    openSheet('포켓몬 도감', body);
    return;
  }
  const head = el('div', 'dex-head');
  const fav = button(state.favorites.includes(id) ? '♥' : '♡', 'fav-btn' + (state.favorites.includes(id) ? ' on' : ''), () => {
    update((s) => { s.favorites = s.favorites.includes(id) ? s.favorites.filter((x) => x !== id) : [...s.favorites, id]; });
    checkBadges();
    openDexDetail(id);
  }, { 'aria-label': state.favorites.includes(id) ? '좋아요 취소' : '좋아요', 'aria-pressed': String(state.favorites.includes(id)) });
  const name = el('div');
  name.append(el('span', 'eyebrow', `NO. ${String(id).padStart(3, '0')} · ${typesEn(p)}`), el('h3', '', p.name), el('small', '', `${typesKo(p)} 타입 · ${state.discovered[id]} 발견`));
  head.append(name, fav);
  body.append(head, el('p', 'dex-line', `“${p.line}”`));
  const moves = el('div', 'chip-row');
  for (const [m, t] of [['hop', '점프'], ['dance', '춤'], ['peek', '장난'], ['celebrate', '축하']]) {
    moves.append(button(t, 'chip', () => {
      preview.classList.remove('hop', 'dance', 'peek', 'celebrate');
      void preview.offsetWidth;
      if (!prefersReducedMotion(state)) preview.classList.add(m);
    }));
  }
  body.append(moves);
  const actions = el('div', 'dex-actions');
  const choose = button(id === state.character ? '지금 함께하는 친구' : '파트너로 함께하기', 'btn solid', () => setPartner(id));
  choose.disabled = id === state.character;
  const listen = button('♪ 울음소리', 'btn light', async () => {
    listen.disabled = true;
    try {
      const res = await fetch(cryUrl(id), { mode: 'cors', credentials: 'omit' });
      if (!res.ok) throw new Error();
      const a = new Audio(URL.createObjectURL(await res.blob()));
      await a.play();
    } catch (e) { notice(e?.name === 'NotSupportedError' ? '이 브라우저는 울음소리 형식(OGG)을 재생하지 못해요.' : '울음소리를 불러오지 못했어요. 인터넷 연결이나 오프라인 저장을 확인해 줘.'); }
    listen.disabled = false;
  });
  actions.append(choose, listen);
  body.append(actions);
  body.append(el('p', 'setup-note', p.partner ? '마스터볼 M6에서도 이 친구를 표시할 수 있어요.' : '이 친구는 앱 안에서만 함께해요. 마스터볼 M6는 파트너 8종만 지원해요.'));
  openSheet('포켓몬 도감', body);
}
function setPartner(id) {
  const p = byId(id);
  state.character = id;
  save();
  renderCharacter();
  initRoster();
  closeSheet();
  motion(p.behavior);
  say(p.line);
  notice(`${josa(p.name, '이', '가')} 나타났어!`);
  if (m6.connected && state.m6.autoSync) {
    if (M6_PARTNERS.includes(id)) m6.setPartner(id).then((r) => { if (!r.ok) notice(r.text); });
    else notice('마스터볼은 파트너 8종만 표시해서 볼 화면은 그대로예요.');
  }
}

// ---- 우리 서랍 (memories)
function openMemories() {
  const body = el('div');
  const sp = specialDay();
  if (sp) {
    const card = el('div', 'special-card');
    card.append(el('b', '', sp === 'birthday' ? '🎂 생일 축하해!' : '♡ 우리의 기념일'), el('p', '', state.message));
    body.append(card);
    motion('celebrate');
  }
  body.append(el('p', '', '이곳은 우리만 아는 공간이야. 편지와 특별한 날은 이 기기에만 저장되고, 어디에도 올라가지 않아.'));
  const input = el('textarea', '', '', { 'aria-label': '우리만의 편지', maxlength: '1000' });
  input.value = state.message;
  body.append(input);
  body.append(button('편지 저장', 'btn solid', () => { state.message = input.value; save(); notice('우리 서랍에 편지를 보관했어 ♡'); }));
  const days = el('div', 'special-days');
  const bd = el('input', '', '', { type: 'text', inputmode: 'numeric', placeholder: 'MM-DD', maxlength: '5', 'aria-label': '생일 (월-일)' });
  bd.value = state.birthday;
  const an = el('input', '', '', { type: 'date', 'aria-label': '기념일' });
  an.value = state.anniversary;
  const saveDays = () => {
    const ok = /^(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/.test(bd.value) || bd.value === '';
    if (!ok) { notice('생일은 10-25처럼 MM-DD로 적어 줘.'); return; }
    update((s) => { s.birthday = bd.value; s.anniversary = an.value; });
    renderClock();
    notice('특별한 날을 기억해 둘게 ♡');
  };
  bd.onchange = saveDays;
  an.onchange = saveDays;
  const l1 = el('label', 'mini-field'); l1.append(el('small', '', '생일'), bd);
  const l2 = el('label', 'mini-field'); l2.append(el('small', '', '기념일'), an);
  days.append(l1, l2);
  body.append(el('span', 'eyebrow', 'SPECIAL DAYS'), days);
  const secret = el('div', 'sheet-row');
  secret.append(el('b', '', state.secretUnlocked ? '✦ 팬텀의 비밀이 열렸어!' : '🔒 팬텀의 작은 비밀'), el('small', '', state.secretUnlocked ? '파트너를 다섯 번 쓰다듬으면 언제든 다시 열려.' : '파트너를 다섯 번 연속으로 눌러 봐.'));
  body.append(secret);
  body.append(button('🎂 특별한 날의 깜짝 메시지 보기', 'btn light', () => { notice('오늘 가장 소중한 주인공은 바로 너야! ♡'); motion('celebrate'); }));
  // badges
  body.append(el('span', 'eyebrow badge-eyebrow', `BADGES · ${Object.keys(state.badges).length}/${BADGES.length}`));
  const bgrid = el('div', 'badge-grid');
  for (const b of BADGES) {
    const got = state.badges[b.id];
    const c = el('div', 'badge' + (got ? ' on' : ''), '', { title: b.desc });
    c.append(el('span', 'badge-icon', got ? b.icon : '?'), el('b', '', b.name), el('small', '', got ? `${got} 획득` : b.desc));
    bgrid.append(c);
  }
  body.append(bgrid);
  // game records
  body.append(el('span', 'eyebrow badge-eyebrow', 'MY GAME RECORDS'));
  const rec = el('div', 'record-list');
  for (const g of Object.values(GAMES)) {
    const r = state.games[g.id];
    const vals = Object.values(r?.best || {});
    const best = vals.length ? (g.lowerIsBetter ? Math.min(...vals) : Math.max(...vals)) : null;
    const row = el('div', 'sheet-row');
    const t = el('div');
    t.append(el('b', '', g.title), el('small', '', `${r?.plays || 0}번 플레이`));
    row.append(t, el('span', 'record-val', g.noRecord ? (g.hubMeta?.(state) || '') : best == null ? '-' : g.format ? g.format(best) : `${best}${g.unit || ''}`));
    rec.append(row);
  }
  body.append(rec);
  // M6 message
  const msgBox = el('div', 'm6-inline');
  const bytes = utf8Bytes(state.message);
  msgBox.append(el('b', '', '마스터볼에 메시지 보내기'), el('p', '', `볼은 ${MAX_MESSAGE_BYTES}바이트(한글 약 30자)까지 저장해요. 지금 편지: ${bytes}바이트. 보낸 메시지는 볼에만 저장돼요.`));
  const short = el('input', '', '', { type: 'text', 'aria-label': '마스터볼 메시지', maxlength: '30' });
  short.value = [...state.message].slice(0, 30).join('');
  const send = button(m6.connected ? '마스터볼로 보내기' : '마스터볼이 연결되어 있지 않아요', 'btn light', async () => {
    if (utf8Bytes(short.value) > MAX_MESSAGE_BYTES) { notice(`메시지가 ${MAX_MESSAGE_BYTES}바이트를 넘어요. 조금 줄여 줘.`); return; }
    send.disabled = true;
    const r = await m6.sendMessage(short.value);
    notice(r.text);
    send.disabled = false;
  });
  send.disabled = !m6.connected;
  msgBox.append(short, send);
  body.append(msgBox);
  openSheet('우리 서랍 ♡', body);
}

// ---- settings & offline
function toggleRow(title, sub, checked, onChange) {
  const row = el('label', 'sheet-row');
  const t = el('div');
  t.append(el('b', '', title));
  if (sub) t.append(el('small', '', sub));
  const c = el('input', 'switch', '', { type: 'checkbox', role: 'switch' });
  c.checked = checked;
  c.onchange = () => onChange(c.checked);
  row.append(t, c);
  return row;
}
function openSettings() {
  const body = el('div');
  body.append(el('p', '', '시계는 한국 시간 기준이며 개인정보와 편지는 이 기기에만 저장돼.'));
  body.append(
    toggleRow('동작 줄이기', '포켓몬 움직임과 화면 흔들림을 줄여요', state.reduceMotion, (v) => { update((s) => { s.reduceMotion = v; }); }),
    toggleRow('게임 효과음', '게임과 집중 완료 효과음', state.sound, (v) => { update((s) => { s.sound = v; }); setSoundEnabled(v); }),
    toggleRow('글자 크게', '화면 전체 글자와 버튼을 조금 키워요', state.largeText, (v) => { update((s) => { s.largeText = v; }); applyDisplay(); }),
    toggleRow('마스터볼 자동 동기화', '연결되면 파트너·다음 알람·집중 타이머를 볼에 맞춰요', state.m6.autoSync, (v) => { update((s) => { s.m6.autoSync = v; }); }),
  );
  body.append(button('오프라인 콘텐츠 관리 →', 'btn light', openOffline), button('마스터볼 M6 연결 →', 'btn light', openM6));
  const info = el('div', 'app-info');
  info.append(el('b', '', `PokéDock Mobile V${APP_VERSION}`), el('small', '', `${native() ? `네이티브 앱 (${window.Capacitor?.getPlatform?.()})` : '웹앱 (GitHub Pages / PWA)'} · 데이터 ${loaded.source === 'v17' ? 'V17.1에서 옮겨 옴' : '이 기기 저장'}`));
  body.append(info);
  body.append(button('V18 기록 초기화', 'btn text-btn danger', async () => {
    if (!confirm('V18의 알람·편지·기록·도감을 이 기기에서 삭제할까? (V17.1 화면의 데이터는 그대로 남아)')) return;
    if (native()) await cancelNativeAlarms().catch(() => {});
    localStorage.removeItem(STATE_KEY);
    localStorage.removeItem(FIRED_KEY);
    fired = {};
    state = normalizeState({});
    state.bond = touchVisit(state.bond, today());
    save();
    closeSheet();
    initScreen();
    notice('초기화했어');
  }));
  openSheet('설정', body);
}
function applyDisplay() {
  document.documentElement.classList.toggle('large-text', state.largeText);
  document.documentElement.classList.toggle('reduce-motion', prefersReducedMotion(state));
}

function openOffline() {
  const off = window.pokedockOffline;
  off?.refresh?.();
  const body = el('div', 'offline-sheet');
  const status = el('div', 'offline-status');
  const usage = el('p', 'setup-note');
  const paint = () => {
    const s = off?.status || window.pokedockOfflineStatus || {};
    status.replaceChildren();
    for (const [k, label] of [['shell', '앱 화면'], ['sprites', '포켓몬 이미지'], ['cries', '울음소리']]) {
      const v = s[k] || { done: 0, total: 0 };
      const row = el('div', 'sheet-row');
      const t = el('div');
      t.append(el('b', '', label), el('small', '', k === 'shell' ? (v.ready ? '오프라인 실행 준비 완료' : '준비 중') : `${v.done}/${v.total} 저장${v.error ? ' · ' + v.error : ''}`));
      const ok = k === 'shell' ? v.ready : v.total && v.done === v.total;
      row.append(t, el('span', 'state-pill' + (ok ? ' ok' : ''), ok ? '완료' : k === 'cries' && !v.done ? '선택' : '진행'));
      status.append(row);
    }
  };
  body.append(status, usage);
  body.append(el('p', '', '이미지는 첫 접속 때 자동으로 이 기기에 저장돼요. 울음소리는 원할 때만 저장해요. 공개 저장소에는 이미지·소리 파일을 올리지 않고, 저작권자는 Nintendo/Creatures/GAME FREAK이에요.'));
  const actions = el('div', 'dex-actions');
  actions.append(
    button('이미지 다시 저장', 'btn light', () => off?.cacheSprites()),
    button('울음소리 저장 (24개)', 'btn light', () => off?.cacheCries()),
  );
  const clear = el('div', 'dex-actions');
  clear.append(button('울음소리 지우기', 'btn text-btn', async () => { await off?.clear('cries'); notice('울음소리 저장을 지웠어요.'); }), button('이미지 캐시 지우기', 'btn text-btn', async () => { await off?.clear('sprites'); notice('이미지 캐시를 지웠어요. 온라인에서 다시 저장돼요.'); }));
  body.append(actions, clear);
  if (!off) body.append(el('p', 'setup-problem', native() ? '네이티브 앱은 이미지가 앱 안에 들어 있어요.' : '이 브라우저는 오프라인 저장(Service Worker)을 지원하지 않아요.'));
  const estimate = async () => {
    try {
      const e = await navigator.storage?.estimate?.();
      if (e) usage.textContent = `이 사이트 저장 공간 사용량 약 ${(e.usage / 1048576).toFixed(1)}MB / 허용 ${(e.quota / 1048576).toFixed(0)}MB`;
    } catch { /* unsupported */ }
  };
  paint();
  estimate();
  const onProgress = () => { if (!$('sheet').hidden && status.isConnected) { paint(); estimate(); } else window.removeEventListener('pokedock-offline', onProgress); };
  window.addEventListener('pokedock-offline', onProgress);
  openSheet('오프라인 콘텐츠', body);
}

// ---- M6 Master Ball
const m6 = new M6Link({ onChange: () => { renderM6(); if (!$('sheet').hidden && $('sheet-inner').querySelector('.m6-sheet')) paintM6Sheet(); } });
const M6_LABEL = { unsupported: '이 기기에서 연결 불가', idle: '연결 안 됨', connecting: '연결 중…', connected: '연결됨', lost: '연결 끊김 · 다시 시도', error: '연결 실패' };
function m6Title() {
  if (m6.mock && m6.status === 'connected') return '모의 연결 (테스트)';
  return M6_LABEL[m6.status] || m6.status;
}
function renderM6() {
  $('m6-title').textContent = m6Title();
  $('m6-dot').className = 'dot-' + (m6.mock && m6.status === 'connected' ? 'mock' : m6.status);
  const s = m6.deviceState;
  $('m6-sub').textContent = m6.status === 'connected' && s ? `${byId(s.partner)?.name || '파트너'} · 밝기 ${s.brightness}%${s.focus.phase === 'running' ? ' · 집중 중' : ''}` : m6.support.ok ? '눌러서 연결하기' : '앱/브라우저 지원 안내 보기';
}
async function onM6Connected() {
  if (!state.m6.autoSync) return;
  const tasks = [];
  if (M6_PARTNERS.includes(state.character) && m6.deviceState?.partner !== state.character) tasks.push(() => m6.setPartner(state.character));
  tasks.push(() => sendM6Alarm(true));
  for (const t of tasks) { const r = await t(); if (!r.ok) break; }
  update((s) => { s.m6.lastSyncAt = Date.now(); s.m6.lastResult = m6.history[0]?.text || ''; });
}
function openM6() {
  const body = el('div', 'm6-sheet');
  openSheet('마스터볼 M6', body);
  paintM6Sheet();
}
function paintM6Sheet() {
  const body = $('sheet-inner').querySelector('.m6-sheet');
  if (!body) return;
  body.replaceChildren();
  const head = el('div', 'm6-head');
  const ball = el('span', 'm6-ball big', '', { 'aria-hidden': 'true' });
  ball.append(el('i', 'dot-' + (m6.mock && m6.status === 'connected' ? 'mock' : m6.status)));
  const ht = el('div');
  ht.append(el('b', '', m6Title()), el('small', '', m6.support.label));
  head.append(ball, ht);
  body.append(head);
  if (m6.mock) body.append(el('p', 'setup-problem', '지금은 테스트용 모의 기기와 이야기하고 있어요. 실제 마스터볼과 연결된 것이 아니에요.'));
  if (!m6.support.ok) {
    body.append(el('p', '', m6.support.label), el('p', 'setup-note', 'M6는 BLE로만 연결돼요. Android 네이티브 앱(BLE 플러그인 포함 빌드) 또는 Android Chrome에서 연결할 수 있어요. iPhone은 서명된 네이티브 iOS 앱이 필요해요. 하드웨어 실기기 연결 시험(G3)은 아직 하지 않았어요.'));
    return;
  }
  if (m6.lastError && m6.status !== 'connected') body.append(el('p', 'setup-problem', m6.lastError));
  const row = el('div', 'dex-actions');
  if (m6.status === 'connected') row.append(button('연결 해제', 'btn light', () => m6.disconnect()), button('상태 새로고침', 'btn light', () => m6.refresh()));
  else row.append(button(m6.status === 'connecting' ? '연결 중…' : m6.status === 'lost' ? '다시 연결' : '마스터볼 찾기', 'btn solid', async () => {
    try { await m6.connect(); await onM6Connected(); notice(m6.mock ? '모의 기기와 연결했어요 (테스트)' : '마스터볼과 연결됐어요!'); } catch { /* shown in sheet */ }
  }, { disabled: m6.status === 'connecting' }));
  body.append(row);
  if (m6.status !== 'connected') {
    body.append(el('p', 'setup-note', '처음 연결할 때: 볼 메뉴에서 “페어링”을 누르면 2분 동안 연결을 받아요(처음 켤 때는 10분 자동). 볼 화면에 나온 6자리 번호를 휴대폰에 입력해 줘.'));
  }
  const s = m6.deviceState;
  if (m6.status === 'connected' && s) {
    const grid = el('div', 'stat-row m6-state');
    const phase = { idle: '대기', running: '집중 중', paused: '일시정지', done: '완료' }[s.focus.phase] || s.focus.phase;
    for (const [k, v] of [['파트너', byId(s.partner)?.name || s.partner], ['밝기', `${s.brightness}%`], ['소리', s.sound ? '켜짐' : '꺼짐'], ['집중', s.focus.phase === 'idle' ? '대기' : `${phase} ${formatSeconds(s.focus.remaining_s)}`],
      ['알람', s.alarm.enabled ? `${String(s.alarm.hour).padStart(2, '0')}:${String(s.alarm.minute).padStart(2, '0')}${s.alarm.ringing ? ' 울리는 중' : ''}` : '꺼짐'], ['시계', s.clock.trusted ? `동기화 ${s.clock.syncAgeMin}분 전` : '미신뢰'],
      ['USB 전원', s.power.ok ? `정상 ${(s.power.usbMv / 1000).toFixed(2)}V` : `낮음 ${(s.power.usbMv / 1000).toFixed(2)}V`], ['펌웨어', s.firmware]]) {
      const c = el('span', 'stat');
      c.append(el('small', '', k), el('b', '', String(v)));
      grid.append(c);
    }
    body.append(grid);
    const ctl = el('div', 'm6-controls');
    const result = el('p', 'quiz-feedback', '', { 'aria-live': 'polite' });
    const run = (p) => p.then((r) => { result.textContent = r.text; });
    const bright = el('input', '', '', { type: 'range', min: '1', max: '100', 'aria-label': '마스터볼 화면 밝기' });
    bright.value = String(s.brightness);
    bright.onchange = () => run(m6.setBrightness(Number(bright.value)));
    const bl = el('label', 'mini-field'); bl.append(el('small', '', '화면 밝기'), bright);
    ctl.append(bl);
    const btns = el('div', 'chip-row');
    btns.append(
      button(M6_PARTNERS.includes(state.character) ? `${partner().name} 보내기` : '파트너 보내기 (8종만)', 'chip', () => run(m6.setPartner(state.character))),
      button('시간 동기화', 'chip', () => run(m6.syncClock())),
      button('다음 알람 보내기', 'chip', () => run(sendM6Alarm(true))),
      button(s.sound ? '볼 소리 끄기' : '볼 소리 켜기', 'chip', () => run(m6.setSound(!s.sound))),
      button('반응 보내기 ♡', 'chip', () => run(m6.reaction())),
    );
    if (s.alarm.ringing) btns.append(button('볼 알람 끄기', 'chip', () => run(m6.run('알람 끄기', (c) => c.dismissAlarm()))));
    ctl.append(btns, result);
    body.append(ctl);
  }
  if (m6.history.length) {
    const log = el('details', 'history-box');
    log.append(el('summary', '', '최근 통신 기록'));
    const ul = el('ul', 'history-list');
    for (const h of m6.history) ul.append(el('li', h.ok ? 'ok' : 'bad', `${new Date(h.at).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })} · ${h.text}`));
    log.append(ul);
    body.append(log);
  }
}

// ------------------------------------------------------------------ arcade
const GAMES = Object.fromEntries([cry, balance, silhouette, memory, runner, reaction, daily].map((g) => [g.id, g]));
const arcadeEnv = {
  getState: () => state,
  update,
  notice,
  discover,
  reduceMotion: () => prefersReducedMotion(state),
  markSeen(id) { state.seen[id] = Date.now(); save(); },
  markPlayed(id) { update((s) => { const g = s.games[id] || { plays: 0, best: {}, lastDay: '' }; s.games[id] = { ...g, plays: g.plays + 1, lastDay: today() }; }); checkBadges(); save(); },
  award: (reason) => award(reason),
  recordGame(id, key, value, lower) {
    const firstToday = state.games[id]?.lastDay !== today();
    const r = recordResult(state.games, id, key, value, lower, today());
    state.games = r.games;
    if (firstToday) award('game');
    checkBadges();
    save();
    return r;
  },
  afterGame() { renderToday(); },
  onClose() { renderToday(); renderBond(); },
};
const arcade = createArcade(arcadeEnv, GAMES);

function renderToday() {
  const { pokemon } = dailyPick(today());
  const r = state.daily[today()];
  $('today-art').replaceChildren(pokeImg(pokemon.id, { cls: 'mini-img' + (r?.revealed ? '' : ' silhouette'), alt: r?.revealed ? pokemon.name : '오늘의 포켓몬 실루엣' }));
  $('today-title').textContent = r?.revealed ? pokemon.name : '새 친구 등장!';
  $('today-sub').textContent = r?.stamp ? '오늘의 도장 완료 ✓' : r?.revealed ? '퀴즈·미션으로 도장 받기' : '하루 한 번 공개';
}

// ------------------------------------------------------------------ views
function openGame() { state.view = 'game'; save(); updateView(); sizePixelSprite(); if (innerHeight > innerWidth) notice('가로로 돌리면 게임 화면이 더 넓게 보여요.'); try { screen.orientation?.lock?.('landscape').catch(() => {}); } catch { /* not allowed */ } }
function goHome() { state.view = 'home'; save(); updateView(); try { screen.orientation?.unlock?.(); } catch { /* not allowed */ } }
function updateView() {
  const g = state.view === 'game';
  $('daily').hidden = g;
  $('game').hidden = !g;
  $('bottom-nav').hidden = g;
  document.querySelectorAll('.bottom-nav button').forEach((b) => b.classList.toggle('selected', b.dataset.view === (g ? 'game' : 'home')));
}
function initRoster() {
  const r = $('roster');
  r.replaceChildren();
  for (const c of PARTNERS) {
    const b = button(c.name, '', () => { state.character = c.id; save(); renderCharacter(); motion(c.behavior); say(reactionFor(c, Date.now())); if (m6.connected && state.m6.autoSync) m6.setPartner(c.id); }, { 'data-id': String(c.id) });
    r.append(b);
  }
  const cur = partner();
  const more = button(cur.partner ? '도감 친구들 ↗' : `${cur.name} ↗`, cur.partner ? 'roster-more' : 'roster-more selected', openDex, { 'aria-label': '도감에서 다른 친구 고르기' });
  r.append(more);
}
function renderOfflineBadge() {
  const s = window.pokedockOffline?.status || window.pokedockOfflineStatus;
  const b = $('offline-badge');
  if (!s) return;
  const ready = s.shell?.ready && s.sprites?.total && s.sprites.done === s.sprites.total;
  b.classList.toggle('ready', !!ready);
  b.querySelector('.long').textContent = s.unsupported ? '오프라인 미지원' : ready ? '오프라인 준비 완료' : `이미지 저장 ${s.sprites?.done || 0}/${s.sprites?.total || 0}`;
  b.querySelector('.short').textContent = s.unsupported ? '미지원' : ready ? '오프라인 ✓' : `${s.sprites?.done || 0}/${s.sprites?.total || 0}`;
}

let lastDay = today();
function tick() {
  const now = Date.now();
  renderClock();
  processFocus(now);
  renderFocus();
  updateAlarms(now);
  if (today() !== lastDay) { lastDay = today(); state.bond = touchVisit(state.bond, lastDay); checkBadges(); save(); renderBond(); renderToday(); renderAlarm(); }
  else if (now % 60000 < 1100) renderAlarm();
}
function initScreen() {
  applyDisplay();
  setSoundEnabled(state.sound);
  initRoster();
  renderCharacter();
  renderClock();
  renderFocus();
  renderAlarm();
  renderBond();
  renderToday();
  renderM6();
  updateView();
}

// ------------------------------------------------------------------ wiring
$('orientation-button').onclick = openGame;
$('game-exit').onclick = goHome;
$('settings-button').onclick = openSettings;
$('focus-reset').onclick = focusReset;
$('focus-start').onclick = focusToggle;
$('focus-more').onclick = openTimerSheet;
for (const b of document.querySelectorAll('[data-focus]')) b.onclick = () => setSingle(Number(b.dataset.focus));
$('alarm-edit').onclick = openAlarmSheet;
$('open-partners').onclick = openDex;
$('pet-pokemon').onclick = handlePet;
$('easter-entry').onclick = openMemories;
$('bond-strip').onclick = openMemories;
$('arcade-open').onclick = () => arcade.open();
$('today-tile').onclick = () => arcade.open('daily');
$('m6-tile').onclick = openM6;
$('offline-badge').onclick = openOffline;
$('sheet-close').onclick = closeSheet;
$('sheet-backdrop').onclick = closeSheet;
$('ring-dismiss').onclick = () => stopRinging(false);
$('ring-snooze').onclick = () => stopRinging(true);
for (const b of document.querySelectorAll('[data-view]')) b.onclick = () => { const v = b.dataset.view; if (v === 'home') goHome(); else if (v === 'game') openGame(); else if (v === 'friends') openDex(); else openMemories(); };
for (const b of document.querySelectorAll('[data-style]')) b.onclick = () => { state.style = b.dataset.style; save(); renderCharacter(); };
for (const b of document.querySelectorAll('[data-motion]')) b.onclick = () => {
  const m = b.dataset.motion, c = partner();
  motion(m);
  const lines = { wave: `안녕! 나는 ${c.name}!`, sleep: 'Zzz… 조금만 잘게…', celebrate: '야호! 축하해!', peek: c.id === 94 ? '크크, 여기 있었지롱!' : '살짝 엿보기!', hop: '폴짝!', dance: '랄랄라~' };
  say(lines[m] || c.line);
  if (m === 'wave' && m6.connected) m6.reaction();
};
window.addEventListener('keydown', (e) => {
  if (e.key !== 'Escape') return;
  if (!$('ringing').hidden) return;
  if (!$('sheet').hidden) return closeSheet();
  if (state.view === 'game' && $('arcade').hidden) goHome();
});
window.addEventListener('resize', sizePixelSprite);
window.addEventListener('pokedock-offline', renderOfflineBadge);
document.addEventListener('visibilitychange', () => { if (!document.hidden) tick(); else save(); });
window.addEventListener('pagehide', save);
window.pokedockApp = { get state() { return state; }, GAMES, arcade, m6, tick, version: APP_VERSION };

state.bond = touchVisit(state.bond, today());
checkBadges();
save();
initScreen();
renderOfflineBadge();
if (loaded.source === 'v17') setTimeout(() => notice('V17.1의 알람·편지·파트너 설정을 V18로 옮겨 왔어 ♡'), 600);
if (native() && Notif()) registerNativeExtras(Notif()).catch(() => {});
setInterval(tick, 1000);
tick();
