// PokéDock V18 core: persisted state, migration from V17.1, KST calendar helpers, focus timer
// engine, alarm scheduling, bond/badge/daily logic. No DOM access, so node:test covers it.
import { POKEDEX, PARTNER_IDS, byId } from './pokedex.js';

export const SCHEMA = 18;
export const STATE_KEY = 'pokedock-v18-state';
export const FIRED_KEY = 'pokedock-v18-alarm-fired';
export const V17_STATE_KEY = 'pokedock-v17-mobile-state';
export const V17_FIRED_KEY = 'pokedock-v17-alarm-triggers';

export const ALARM_SOUNDS = Object.freeze([
  { id: 'dawn', name: '모험의 아침', file: 'alarm_dawn.wav' },
  { id: 'sparkle', name: '별빛 알림', file: 'alarm_sparkle.wav' },
  { id: 'calm', name: '포근한 밤', file: 'alarm_calm.wav' },
]);
export const SNOOZE_CHOICES = Object.freeze([0, 5, 10, 15]);
export const MAX_ALARMS = 8;
export const FOCUS_PRESETS = Object.freeze([15, 25, 45]);

// ---------------------------------------------------------------- KST calendar (UTC+9, no DST)
const KST_MS = 9 * 3600 * 1000;
const WEEK = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];
const pad = (n) => String(n).padStart(2, '0');

export function kstParts(date = new Date()) {
  const k = new Date((date instanceof Date ? date.getTime() : date) + KST_MS);
  const y = k.getUTCFullYear(), mo = k.getUTCMonth() + 1, d = k.getUTCDate(), h = k.getUTCHours(), mi = k.getUTCMinutes();
  const dow = k.getUTCDay();
  return {
    hhmm: `${pad(h)}:${pad(mi)}`, day: `${y}-${pad(mo)}-${pad(d)}`, weekday: dow, minute: h * 60 + mi,
    display: `${pad(mo)}.${pad(d)}`, weekdayName: WEEK[dow], mmdd: `${pad(mo)}-${pad(d)}`, hour: h,
  };
}
export const kstDay = (t = Date.now()) => kstParts(t).day;
// Midnight (KST) of the day containing t, as epoch ms.
export const kstMidnight = (t) => t - ((t + KST_MS) % 86400000 + 86400000) % 86400000;
export function dayDiff(a, b) {
  // whole days from KST day string a to b
  return Math.round((Date.parse(b + 'T00:00:00Z') - Date.parse(a + 'T00:00:00Z')) / 86400000);
}
export function addDays(day, n) {
  const t = Date.parse(day + 'T00:00:00Z') + n * 86400000;
  return new Date(t).toISOString().slice(0, 10);
}

export function formatSeconds(n) {
  const sec = Math.max(0, Math.floor(n));
  if (sec >= 3600) return `${Math.floor(sec / 3600)}:${pad(Math.floor((sec % 3600) / 60))}:${pad(sec % 60)}`;
  return `${pad(Math.floor(sec / 60))}:${pad(sec % 60)}`;
}
export const formatMinutes = (m) => (m >= 60 ? `${Math.floor(m / 60)}시간 ${m % 60 ? (m % 60) + '분' : ''}`.trim() : `${m}분`);

// ---------------------------------------------------------------- focus timer
// The timer stores an absolute end time (endAt, epoch ms). Remaining time is always derived from
// it, so a throttled tab, a locked phone or an app restart cannot make the countdown drift.
export const DEFAULT_POMODORO = Object.freeze({ focus: 25, brk: 5, long: 15, cycles: 4, autoBreak: true });

const clampInt = (v, lo, hi, dflt) => (Number.isInteger(v) && v >= lo && v <= hi ? v : dflt);

export function phaseMinutes(focus, timer) {
  if (focus.mode === 'pomodoro') {
    const p = timer.pomodoro;
    return focus.phase === 'break' ? p.brk : focus.phase === 'long' ? p.long : p.focus;
  }
  return focus.minutes;
}

export function idleFocus(mode, minutes, timer, cycle = 1, phase = 'focus') {
  const f = { mode, phase, minutes, cycle, running: false, endAt: 0, remainingSec: 0, totalSec: 0 };
  f.totalSec = f.remainingSec = phaseMinutes(f, timer) * 60;
  return f;
}

export function focusRemaining(f, now = Date.now()) {
  if (f.running) return Math.max(0, Math.ceil((f.endAt - now) / 1000));
  return Math.max(0, f.remainingSec);
}

export function startFocus(f, now = Date.now()) {
  if (f.running) return f;
  const secs = f.remainingSec > 0 ? f.remainingSec : f.totalSec;
  return { ...f, running: true, endAt: now + secs * 1000, remainingSec: secs };
}

export function pauseFocus(f, now = Date.now()) {
  if (!f.running) return f;
  return { ...f, running: false, remainingSec: focusRemaining(f, now), endAt: 0 };
}

// Reset the current phase. A focus phase that ran at least a minute is credited (not as a session).
export function resetFocus(f, timer, now = Date.now()) {
  const elapsed = f.totalSec - focusRemaining(f, now);
  const creditMin = f.phase === 'focus' && elapsed >= 60 ? Math.floor(elapsed / 60) : 0;
  return { focus: idleFocus(f.mode, f.minutes, timer, f.mode === 'pomodoro' ? f.cycle : 1, f.mode === 'pomodoro' ? f.phase : 'focus'), creditMin };
}

// Walk the timer forward to `now`, completing phases whose end time has passed (possibly while the
// app was closed). Returns the new focus state and the completion events in order.
export function advanceFocus(f, timer, now = Date.now()) {
  const events = [];
  let cur = f;
  for (let guard = 0; guard < 4 && cur.running && now >= cur.endAt; guard++) {
    const at = cur.endAt;
    if (cur.phase === 'focus') {
      events.push({ type: 'focusDone', at, minutes: Math.round(cur.totalSec / 60), cycle: cur.cycle });
      if (cur.mode !== 'pomodoro') {
        cur = idleFocus('single', cur.minutes, timer);
        break;
      }
      const long = cur.cycle >= timer.pomodoro.cycles;
      const next = idleFocus('pomodoro', cur.minutes, timer, cur.cycle, long ? 'long' : 'break');
      cur = timer.pomodoro.autoBreak ? { ...next, running: true, endAt: at + next.totalSec * 1000, remainingSec: next.totalSec } : next;
    } else {
      events.push({ type: 'breakDone', at, long: cur.phase === 'long' });
      const cycle = cur.phase === 'long' ? 1 : cur.cycle + 1;
      cur = idleFocus('pomodoro', cur.minutes, timer, cycle, 'focus'); // the next focus waits for a tap
    }
  }
  return { focus: cur, events };
}

// ---------------------------------------------------------------- focus statistics
export function creditFocus(stats, at, minutes, completed) {
  if (!(minutes > 0)) return stats;
  const day = kstDay(at);
  const days = { ...stats.days };
  const d = days[day] || { min: 0, sessions: 0 };
  days[day] = { min: d.min + minutes, sessions: d.sessions + (completed ? 1 : 0) };
  // keep ~4 months of daily history; totals keep everything
  const cutoff = addDays(day, -120);
  for (const k of Object.keys(days)) if (k < cutoff) delete days[k];
  return { days, totalMin: stats.totalMin + minutes, sessions: stats.sessions + (completed ? 1 : 0) };
}

export function weekStats(stats, now = Date.now()) {
  const today = kstDay(now);
  const out = [];
  for (let i = 6; i >= 0; i--) {
    const day = addDays(today, -i);
    const d = stats.days[day] || { min: 0, sessions: 0 };
    out.push({ day, weekday: kstParts(Date.parse(day + 'T03:00:00Z')).weekday, ...d });
  }
  return out;
}

// ---------------------------------------------------------------- alarms
export const DEFAULT_ALARMS = Object.freeze([
  { id: 'morning', time: '07:30', days: [1, 2, 3, 4, 5], on: false, title: '아침 인사', sound: 'dawn', pokemon: 94, snooze: 5, quiet: false },
  { id: 'break', time: '08:10', days: [2, 4], on: false, title: '오늘도 좋은 하루', sound: 'sparkle', pokemon: 393, snooze: 5, quiet: false },
  { id: 'night', time: '22:20', days: [0, 1, 2, 3, 4, 5, 6], on: false, title: '하루를 마무리할 시간', sound: 'calm', pokemon: 195, snooze: 10, quiet: true },
]);
const TIME_RE = /^([01]\d|2[0-3]):[0-5]\d$/;

export function normalizeAlarms(value) {
  if (!Array.isArray(value)) return normalizeAlarms(structuredClone(DEFAULT_ALARMS));
  const seen = new Set();
  return value.slice(0, MAX_ALARMS).map((raw, i) => {
    const fallback = DEFAULT_ALARMS[i] || DEFAULT_ALARMS[0];
    let id = typeof raw?.id === 'string' && /^[a-zA-Z0-9_-]{1,40}$/.test(raw.id) ? raw.id : `custom_${i}`;
    if (seen.has(id)) id = `custom_${i}_${seen.size}`;
    seen.add(id);
    const time = typeof raw?.time === 'string' && TIME_RE.test(raw.time) ? raw.time : fallback.time;
    const days = Array.isArray(raw?.days) ? [...new Set(raw.days.filter((d) => Number.isInteger(d) && d >= 0 && d <= 6))].sort() : [...fallback.days];
    const title = typeof raw?.title === 'string' && raw.title.trim() ? raw.title.trim().slice(0, 32) : fallback.title;
    const sound = ALARM_SOUNDS.some((s) => s.id === raw?.sound) ? raw.sound : fallback.sound;
    const pokemon = byId(raw?.pokemon) ? raw.pokemon : fallback.pokemon;
    const snooze = SNOOZE_CHOICES.includes(raw?.snooze) ? raw.snooze : fallback.snooze;
    const quiet = typeof raw?.quiet === 'boolean' ? raw.quiet : false;
    const armedAt = Number.isFinite(raw?.armedAt) ? raw.armedAt : 0;
    return { id, time, days, on: !!raw?.on, title, sound, pokemon, snooze, quiet, armedAt };
  });
}

// Alarms whose minute started within the last `windowMin` minutes and have not fired for that day.
// The window lets a throttled tab catch up (e.g. 23:59 checked at 00:00:40 still rings, once).
export function alarmDue(alarms, now = Date.now(), fired = {}, windowMin = 2) {
  const t = now instanceof Date ? now.getTime() : now;
  const due = [];
  const taken = new Set();
  for (let k = windowMin; k >= 0; k--) {
    const at = t - k * 60000;
    const p = kstParts(at);
    const minuteStart = at - (at % 60000);
    for (const a of alarms) {
      if (!a.on || !a.days.includes(p.weekday) || a.time !== p.hhmm || taken.has(a.id)) continue;
      if (a.armedAt && minuteStart < a.armedAt - 60000) continue; // switched on after this minute passed
      const key = p.day + '|' + a.id;
      if (fired[a.id] === key) continue;
      taken.add(a.id);
      due.push({ alarm: a, key });
    }
  }
  return due;
}

// Next occurrence of any enabled alarm, as {alarm, at (epoch ms), day, inMin}.
export function nextAlarm(alarms, now = Date.now()) {
  const p = kstParts(now);
  const midnight = kstMidnight(now);
  let best = null;
  for (const a of alarms) {
    if (!a.on || !a.days.length) continue;
    const [h, m] = a.time.split(':').map(Number);
    for (let d = 0; d < 8; d++) {
      const dow = (p.weekday + d) % 7;
      if (!a.days.includes(dow)) continue;
      const at = midnight + d * 86400000 + (h * 60 + m) * 60000;
      if (at <= now) continue;
      if (!best || at < best.at) best = { alarm: a, at };
      break;
    }
  }
  if (!best) return null;
  return { ...best, day: kstDay(best.at), inMin: Math.ceil((best.at - now) / 60000), today: kstDay(best.at) === p.day };
}

// Enabled alarms that would ring at the same minute on a shared weekday.
export function duplicateAlarms(alarms) {
  const dupes = new Set();
  for (let i = 0; i < alarms.length; i++)
    for (let j = i + 1; j < alarms.length; j++) {
      const a = alarms[i], b = alarms[j];
      if (a.on && b.on && a.time === b.time && a.days.some((d) => b.days.includes(d))) dupes.add(a.id).add(b.id);
    }
  return dupes;
}

// The M6 firmware (protocol v2) stores ONE daily alarm without weekdays. Send the next phone alarm
// if it rings within 24 h, otherwise disable the ball's alarm. The app re-sends on every connect.
export function m6AlarmProjection(alarms, now = Date.now()) {
  const n = nextAlarm(alarms, now);
  if (n && n.at - now <= 24 * 3600 * 1000) {
    const [h, m] = n.alarm.time.split(':').map(Number);
    return { h, m, en: true, alarmId: n.alarm.id, title: n.alarm.title };
  }
  return { h: 7, m: 0, en: false, alarmId: null, title: null };
}

// ---------------------------------------------------------------- bond, discovery, badges
export const BOND_LEVELS = Object.freeze([0, 10, 30, 60, 100, 160, 240, 340, 480, 650]);
export function bondLevel(points) {
  let lv = 1;
  for (let i = 0; i < BOND_LEVELS.length; i++) if (points >= BOND_LEVELS[i]) lv = i + 1;
  const next = BOND_LEVELS[lv] ?? null;
  return { level: lv, next, base: BOND_LEVELS[lv - 1], progress: next ? (points - BOND_LEVELS[lv - 1]) / (next - BOND_LEVELS[lv - 1]) : 1 };
}

export const PET_DAILY_CAP = 5;
// Visit bookkeeping: distinct days together and the current streak.
export function touchVisit(bond, day) {
  if (bond.lastDay === day) return bond;
  const streak = bond.lastDay && dayDiff(bond.lastDay, day) === 1 ? bond.streak + 1 : 1;
  return { ...bond, firstDay: bond.firstDay || day, lastDay: day, daysTogether: bond.daysTogether + 1, streak, petDay: bond.petDay, petsToday: bond.petDay === day ? bond.petsToday : 0 };
}
export function addBond(bond, amount, reason, day) {
  if (reason === 'pet') {
    const pets = bond.petDay === day ? bond.petsToday : 0;
    if (pets >= PET_DAILY_CAP) return { bond: { ...bond, petDay: day, petsToday: pets }, gained: 0 };
    return { bond: { ...bond, points: bond.points + amount, petDay: day, petsToday: pets + 1 }, gained: amount };
  }
  return { bond: { ...bond, points: bond.points + amount }, gained: amount };
}

export const BADGES = Object.freeze([
  { id: 'FOCUS', icon: '◷', name: '첫 집중', desc: '집중 타이머를 끝까지 한 번 완료', test: (s) => s.stats.sessions >= 1 },
  { id: 'FOCUS10', icon: '✦', name: '집중 열 번', desc: '집중 세션 10회 완료', test: (s) => s.stats.sessions >= 10 },
  { id: 'STREAK', icon: '☀', name: '사흘 연속', desc: '3일 연속으로 만나기', test: (s) => s.bond.streak >= 3 },
  { id: 'ROUTINE', icon: '♬', name: '알람 친구', desc: '알람을 하나 이상 켜 두기', test: (s) => s.alarms.some((a) => a.on) },
  { id: 'NIGHT', icon: '☾', name: '밤의 친구', desc: '밤 10시 이후 팬텀과 놀기', test: (s) => !!s.flags.nightGengar },
  { id: 'DEX', icon: '❖', name: '도감 절반', desc: '포켓몬 12종 발견', test: (s) => Object.keys(s.discovered).length >= 12 },
  { id: 'DEXALL', icon: '❂', name: '도감 완성', desc: `포켓몬 ${POKEDEX.length}종 모두 발견`, test: (s) => Object.keys(s.discovered).length >= POKEDEX.length },
  { id: 'WISH', icon: '★', name: '소원 도장 7개', desc: '오늘의 포켓몬 도장 7개 모으기', test: (s) => Object.values(s.daily).filter((d) => d.stamp).length >= 7 },
  { id: 'PLAYER', icon: '♣', name: '놀이 탐험가', desc: '7가지 게임을 모두 한 번씩', test: (s) => GAME_IDS.every((g) => (s.games[g]?.plays || 0) > 0) },
  { id: 'RUNNER', icon: '☄', name: '그림자 질주', desc: '팬텀 런 300점 달성', test: (s) => Object.values(s.games.runner?.best || {}).some((v) => v >= 300) },
]);
export function newBadges(state, day) {
  const earned = [];
  for (const b of BADGES) if (!state.badges[b.id] && b.test(state)) earned.push(b);
  const badges = { ...state.badges };
  for (const b of earned) badges[b.id] = day;
  return { badges, earned };
}

// ---------------------------------------------------------------- games records
export const GAME_IDS = Object.freeze(['cry', 'balance', 'silhouette', 'memory', 'runner', 'reaction', 'daily']);
// lowerIsBetter: reaction (ms) and memory (moves).
export function recordResult(games, gameId, key, value, lowerIsBetter, day) {
  const g = { plays: 0, best: {}, lastDay: '', ...(games[gameId] || {}) };
  const best = { ...g.best };
  const prev = best[key];
  const isBest = value != null && (prev == null || (lowerIsBetter ? value < prev : value > prev));
  if (isBest) best[key] = value;
  return { games: { ...games, [gameId]: { ...g, plays: g.plays + 1, best, lastDay: day } }, isBest, prev: prev ?? null };
}

// ---------------------------------------------------------------- daily Pokémon
export function hashDay(day, salt = 0) {
  let h = 2166136261 ^ salt;
  for (const ch of day) h = Math.imul(h ^ ch.charCodeAt(0), 16777619);
  return h >>> 0;
}
export const DAILY_MISSIONS = Object.freeze([
  { id: 'pet3', text: '파트너를 세 번 쓰다듬어 주기', check: (s, day) => s.bond.petDay === day && s.bond.petsToday >= 3 },
  { id: 'focus1', text: '집중 타이머 1번 끝까지 해 보기', check: (s, day) => (s.stats.days[day]?.sessions || 0) >= 1 },
  { id: 'play1', text: '게임을 아무거나 한 판 하기', check: (s, day) => GAME_IDS.some((g) => g !== 'daily' && s.games[g]?.lastDay === day) },
  { id: 'dex1', text: '도감에서 좋아하는 포켓몬에 ♥ 누르기', check: (s) => s.favorites.length > 0 },
]);
export function dailyPick(day) {
  const h = hashDay(day);
  const pokemon = POKEDEX[h % POKEDEX.length];
  const mission = DAILY_MISSIONS[hashDay(day, 7) % DAILY_MISSIONS.length];
  return { pokemon, mission };
}

// ---------------------------------------------------------------- state
const isDay = (v) => typeof v === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(v);
const isMmdd = (v) => typeof v === 'string' && /^(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/.test(v);
const obj = (v) => (v && typeof v === 'object' && !Array.isArray(v) ? v : {});

export function defaultState() {
  return {
    schema: SCHEMA, character: 94, style: 'art', view: 'home', focusMinutes: 25,
    timer: { mode: 'single', custom: 30, pomodoro: { ...DEFAULT_POMODORO } },
    focus: null, stats: { days: {}, totalMin: 0, sessions: 0 },
    alarms: structuredClone(DEFAULT_ALARMS), snoozes: [],
    message: '너와 함께하는 평범한 하루가 좋아. ♡', birthday: '', anniversary: '',
    petCount: 0, secretUnlocked: false, reduceMotion: false, sound: true, largeText: false,
    favorites: [], discovered: {}, bond: { points: 0, firstDay: '', lastDay: '', daysTogether: 0, streak: 0, petDay: '', petsToday: 0 },
    badges: {}, flags: {}, games: {}, daily: {}, balance: [], review: [], seen: {},
    m6: { autoSync: true, lastSyncAt: 0, lastResult: '' },
    migratedFrom: '',
  };
}

export function normalizeState(data = {}) {
  const d = obj(data);
  const s = { ...defaultState(), ...d };
  if (!byId(s.character)) s.character = 94;
  if (!['art', 'pixel'].includes(s.style)) s.style = 'art';
  if (!['home', 'game'].includes(s.view)) s.view = 'home';
  s.focusMinutes = clampInt(s.focusMinutes, 1, 120, 25);
  const t = obj(d.timer);
  const pomo = obj(t.pomodoro);
  s.timer = {
    mode: t.mode === 'pomodoro' ? 'pomodoro' : 'single',
    custom: clampInt(t.custom, 1, 120, 30),
    pomodoro: {
      focus: clampInt(pomo.focus, 5, 90, DEFAULT_POMODORO.focus), brk: clampInt(pomo.brk, 1, 30, DEFAULT_POMODORO.brk),
      long: clampInt(pomo.long, 5, 45, DEFAULT_POMODORO.long), cycles: clampInt(pomo.cycles, 2, 8, DEFAULT_POMODORO.cycles),
      autoBreak: typeof pomo.autoBreak === 'boolean' ? pomo.autoBreak : true,
    },
  };
  s.focus = normalizeFocus(d.focus, s);
  const st = obj(d.stats);
  const days = {};
  for (const [k, v] of Object.entries(obj(st.days))) if (isDay(k) && Number.isFinite(v?.min)) days[k] = { min: Math.max(0, Math.round(v.min)), sessions: Math.max(0, v.sessions | 0) };
  s.stats = { days, totalMin: Math.max(0, Math.round(Number(st.totalMin) || 0)), sessions: Math.max(0, Number(st.sessions) | 0) };
  s.alarms = normalizeAlarms(d.alarms);
  s.snoozes = (Array.isArray(d.snoozes) ? d.snoozes : []).filter((z) => typeof z?.id === 'string' && Number.isFinite(z?.at)).slice(0, MAX_ALARMS);
  s.message = typeof s.message === 'string' ? s.message.slice(0, 1000) : defaultState().message;
  s.birthday = isMmdd(s.birthday) ? s.birthday : '';
  s.anniversary = isDay(s.anniversary) ? s.anniversary : '';
  s.petCount = Math.max(0, Number(s.petCount) | 0);
  for (const k of ['secretUnlocked', 'reduceMotion', 'largeText']) s[k] = !!s[k];
  s.sound = s.sound !== false;
  s.favorites = [...new Set((Array.isArray(d.favorites) ? d.favorites : []).filter((id) => byId(id)))];
  s.discovered = {};
  for (const [k, v] of Object.entries(obj(d.discovered))) if (byId(Number(k)) && isDay(v)) s.discovered[k] = v;
  const b = obj(d.bond);
  s.bond = {
    points: Math.max(0, Number(b.points) | 0), firstDay: isDay(b.firstDay) ? b.firstDay : '', lastDay: isDay(b.lastDay) ? b.lastDay : '',
    daysTogether: Math.max(0, Number(b.daysTogether) | 0), streak: Math.max(0, Number(b.streak) | 0),
    petDay: isDay(b.petDay) ? b.petDay : '', petsToday: Math.max(0, Number(b.petsToday) | 0),
  };
  s.badges = {};
  for (const [k, v] of Object.entries(obj(d.badges))) if (BADGES.some((x) => x.id === k) && isDay(v)) s.badges[k] = v;
  s.flags = obj(d.flags);
  s.games = {};
  for (const [k, v] of Object.entries(obj(d.games)))
    if (GAME_IDS.includes(k)) {
      const best = {};
      for (const [bk, bv] of Object.entries(obj(v.best))) if (Number.isFinite(bv)) best[bk] = bv;
      const lastOpts = {};
      for (const [ok, ov] of Object.entries(obj(v.lastOpts))) if (['string', 'number'].includes(typeof ov)) lastOpts[ok] = ov;
      s.games[k] = { plays: Math.max(0, Number(v.plays) | 0), best, lastDay: isDay(v.lastDay) ? v.lastDay : '', lastOpts };
    }
  s.daily = {};
  for (const [k, v] of Object.entries(obj(d.daily)))
    if (isDay(k)) s.daily[k] = { revealed: !!v?.revealed, answered: v?.answered ?? null, correct: !!v?.correct, mission: !!v?.mission, stamp: !!v?.stamp };
  s.balance = (Array.isArray(d.balance) ? d.balance : []).filter((x) => typeof x?.q === 'string' && (x.pick === 0 || x.pick === 1)).slice(-60);
  s.review = [...new Set((Array.isArray(d.review) ? d.review : []).filter((id) => byId(id)))].slice(0, 40);
  s.seen = {};
  for (const [k, v] of Object.entries(obj(d.seen))) if (byId(Number(k)) && Number.isFinite(v)) s.seen[k] = v;
  const m = obj(d.m6);
  s.m6 = { autoSync: m.autoSync !== false, lastSyncAt: Number.isFinite(m.lastSyncAt) ? m.lastSyncAt : 0, lastResult: typeof m.lastResult === 'string' ? m.lastResult.slice(0, 120) : '' };
  // Partners are always known; everything else is discovered by meeting it in the app.
  for (const id of PARTNER_IDS) if (!s.discovered[id]) s.discovered[id] = s.bond.firstDay || kstDay();
  s.schema = SCHEMA;
  delete s.quizBest;
  return s;
}

function normalizeFocus(raw, s) {
  const f = obj(raw);
  const mode = f.mode === 'pomodoro' ? 'pomodoro' : 'single';
  const minutes = clampInt(f.minutes, 1, 120, s.focusMinutes);
  const phase = mode === 'pomodoro' && ['focus', 'break', 'long'].includes(f.phase) ? f.phase : 'focus';
  const cycle = clampInt(f.cycle, 1, s.timer.pomodoro.cycles, 1);
  const base = idleFocus(mode, minutes, s.timer, cycle, phase);
  if (!Number.isFinite(f.totalSec) || f.totalSec <= 0) {
    // V17 shape: {running,endAt,remainingSec}
    if (f.running && Number.isFinite(f.endAt) && f.endAt > 0) return { ...base, running: true, endAt: f.endAt, remainingSec: base.totalSec };
    if (Number.isFinite(f.remainingSec) && f.remainingSec > 0 && f.remainingSec <= base.totalSec) return { ...base, remainingSec: Math.floor(f.remainingSec) };
    return base;
  }
  const totalSec = Math.min(Math.max(60, Math.floor(f.totalSec)), 180 * 60);
  const remainingSec = clampInt(Math.floor(f.remainingSec), 0, totalSec, totalSec);
  if (f.running && Number.isFinite(f.endAt) && f.endAt > 0) return { ...base, totalSec, remainingSec, running: true, endAt: f.endAt };
  return { ...base, totalSec, remainingSec };
}

// V17.1 stored everything under its own key. V18 copies it once (V17 keeps working untouched).
export function migrateFromV17(v17) {
  const o = obj(v17);
  const migrated = normalizeState({
    character: o.character, style: o.style, focusMinutes: o.focusMinutes, focus: o.focus, alarms: o.alarms,
    message: o.message, petCount: o.petCount, secretUnlocked: o.secretUnlocked, reduceMotion: o.reduceMotion,
  });
  migrated.birthday = '';
  if (Number.isInteger(o.quizBest) && o.quizBest > 0 && o.quizBest <= 5) migrated.games.silhouette = { plays: 1, best: { 'easy-5': o.quizBest }, lastDay: '' };
  migrated.migratedFrom = 'v17.1';
  return migrated;
}

export function loadState(storage) {
  const read = (k) => {
    try { return JSON.parse(storage.getItem(k)); } catch { return null; }
  };
  const v18 = read(STATE_KEY);
  if (v18 && typeof v18 === 'object') return { state: normalizeState(v18), fired: obj(read(FIRED_KEY)), source: 'v18' };
  const v17 = read(V17_STATE_KEY);
  if (v17 && typeof v17 === 'object') return { state: migrateFromV17(v17), fired: obj(read(V17_FIRED_KEY)), source: 'v17' };
  return { state: normalizeState({}), fired: {}, source: 'new' };
}
