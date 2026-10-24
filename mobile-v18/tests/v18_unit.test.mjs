// node --test mobile-v18/tests/v18_unit.test.mjs  — pure logic, no browser.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { POKEDEX, PARTNERS, PARTNER_IDS, byId } from '../pokedex.js';
import {
  normalizeState, migrateFromV17, loadState, kstParts, idleFocus, startFocus, pauseFocus, resetFocus, advanceFocus, focusRemaining,
  creditFocus, weekStats, alarmDue, nextAlarm, duplicateAlarms, m6AlarmProjection, normalizeAlarms, touchVisit, addBond, bondLevel,
  newBadges, recordResult, dailyPick, formatSeconds, STATE_KEY, V17_STATE_KEY, DEFAULT_POMODORO,
} from '../core.js';
import { makeBoard, flip, settle } from '../games/memory.js';
import { createRunner, stepRunner, circleHit, totalScore } from '../games/runner-engine.js';
import { cryChoices } from '../games/cry.js';
import { summarize, PROMPTS } from '../games/balance.js';
import { typeQuiz } from '../games/daily.js';
import { freshDeck } from '../ui.js';
import { _hex, MockTransport } from '../ble/transports.js';
import { PokeDockClient } from '../ble/pokedock_ble_client.mjs';
import { encodeCommand, MAX_COMMAND_BYTES } from '../ble/pokedock_ble_protocol.mjs';
import { describeError } from '../ble/m6.js';

const KST = (iso) => Date.parse(iso + '+09:00');
const timer = { mode: 'single', custom: 30, pomodoro: { ...DEFAULT_POMODORO } };

// ------------------------------------------------------------------ Pokédex
test('8 partners kept first in V17 order, Gengar first; 24 total with the requested 16', () => {
  assert.deepEqual(PARTNER_IDS, [94, 393, 468, 448, 195, 175, 417, 385]);
  assert.equal(POKEDEX.length, 24);
  for (const id of [25, 133, 54, 143, 37, 39, 196, 197, 258, 280, 447, 492, 570, 700, 702, 778]) assert.ok(byId(id), `missing ${id}`);
  assert.equal(new Set(POKEDEX.map((p) => p.id)).size, 24);
});
test('Pokédex ids match config/pokemon_catalog.json and the service worker list', () => {
  const cat = JSON.parse(readFileSync(new URL('../../config/pokemon_catalog.json', import.meta.url), 'utf8'));
  const ids = [...cat.favorites, ...cat.supporting, ...cat.extended].map((p) => p.id).sort((a, b) => a - b);
  assert.deepEqual(POKEDEX.map((p) => p.id).sort((a, b) => a - b), ids);
  const sw = readFileSync(new URL('../sw.js', import.meta.url), 'utf8');
  assert.deepEqual(JSON.parse(sw.match(/const IDS = (\[[^\]]+\])/)[1]), POKEDEX.map((p) => p.id));
  for (const f of sw.match(/const CORE = \[([\s\S]*?)\];/)[1].match(/'\.\/[^']*'/g).map((s) => s.slice(3, -1)).filter(Boolean)) {
    readFileSync(new URL('../' + f, import.meta.url)); // throws if the shell lists a missing file
  }
});
test('no Pokémon image or audio file is committed in mobile-v18', () => {
  const sw = readFileSync(new URL('../sw.js', import.meta.url), 'utf8');
  assert.ok(!/\.(png|gif|ogg)'/.test(sw.match(/const CORE = \[([\s\S]*?)\];/)[1].replace(/icon-\d+\.png/g, '')));
});

// ------------------------------------------------------------------ state + migration
test('V17.1 data migrates once: partner, alarms, letter, quiz best; V17 key untouched', () => {
  const v17 = { character: 393, style: 'pixel', focusMinutes: 45, alarms: [{ id: 'morning', time: '06:50', days: [1, 3], on: true, title: '기상', sound: 'calm' }], message: '비밀 편지', quizBest: 4, secretUnlocked: true };
  const store = new Map([[V17_STATE_KEY, JSON.stringify(v17)]]);
  const ls = { getItem: (k) => store.get(k) ?? null };
  const { state, source } = loadState(ls);
  assert.equal(source, 'v17');
  assert.equal(state.character, 393);
  assert.equal(state.focusMinutes, 45);
  assert.equal(state.focus.totalSec, 45 * 60);
  assert.equal(state.alarms[0].time, '06:50');
  assert.equal(state.alarms[0].pokemon, 94, 'new field gets a default');
  assert.equal(state.alarms[0].snooze, 5);
  assert.equal(state.message, '비밀 편지');
  assert.equal(state.games.silhouette.best['easy-5'], 4);
  assert.ok(state.secretUnlocked);
  store.set(STATE_KEY, JSON.stringify(state));
  assert.equal(loadState(ls).source, 'v18');
  assert.equal(store.get(V17_STATE_KEY), JSON.stringify(v17));
});
test('running V17 focus timer survives migration with its end time', () => {
  const s = migrateFromV17({ focusMinutes: 25, focus: { running: true, endAt: 2e12, remainingSec: 1500 } });
  assert.equal(s.focus.running, true);
  assert.equal(s.focus.endAt, 2e12);
});
test('garbage state falls back safely', () => {
  const s = normalizeState({ character: 9999, style: 'x', alarms: 'bad', stats: { days: { nope: 1, '2026-10-25': { min: 'x' } } }, games: { cry: { best: { a: 'x', b: 3 } }, hack: {} }, favorites: [94, 94, 1], timer: { mode: 'pomodoro', pomodoro: { focus: 999 } } });
  assert.equal(s.character, 94);
  assert.equal(s.style, 'art');
  assert.equal(s.alarms.length, 3);
  assert.deepEqual(s.stats.days, {});
  assert.deepEqual(s.games.cry.best, { b: 3 });
  assert.ok(!s.games.hack);
  assert.deepEqual(s.favorites, [94]);
  assert.equal(s.timer.pomodoro.focus, 25);
  assert.equal(normalizeState({ alarms: [] }).alarms.length, 0, 'deleted alarms stay deleted');
});
test('state round-trips through JSON unchanged', () => {
  const s = normalizeState({});
  assert.deepEqual(normalizeState(JSON.parse(JSON.stringify(s))), s);
});

// ------------------------------------------------------------------ KST clock
test('KST clock and weekday', () => {
  const p = kstParts(new Date('2026-10-23T10:34:00Z'));
  assert.equal(p.hhmm, '19:34');
  assert.equal(p.weekday, 5);
  assert.equal(kstParts(new Date('2026-10-24T15:00:00Z')).day, '2026-10-25');
  assert.equal(formatSeconds(1500), '25:00');
  assert.equal(formatSeconds(7200), '2:00:00');
});

// ------------------------------------------------------------------ focus timer
test('timer derives remaining time from the end time (no drift across sleep)', () => {
  let f = idleFocus('single', 25, timer);
  f = startFocus(f, 1000);
  assert.equal(focusRemaining(f, 1000), 1500);
  assert.equal(focusRemaining(f, 1000 + 600000), 900, 'after 10 min of throttled/locked time');
  f = pauseFocus(f, 1000 + 600000);
  assert.equal(focusRemaining(f, 9e12), 900, 'paused time does not move');
  f = startFocus(f, 5e6);
  assert.equal(f.endAt, 5e6 + 900000);
});
test('single focus completes once, even when checked long after the end', () => {
  const f = startFocus(idleFocus('single', 15, timer), 0);
  const r = advanceFocus(f, timer, 3 * 3600 * 1000);
  assert.equal(r.events.length, 1);
  assert.equal(r.events[0].type, 'focusDone');
  assert.equal(r.events[0].at, 15 * 60000);
  assert.equal(r.focus.running, false);
  assert.equal(r.focus.remainingSec, 15 * 60);
  assert.equal(advanceFocus(r.focus, timer, 4 * 3600 * 1000).events.length, 0);
});
test('pomodoro 25/5: focus → auto break → waits for next focus; 4th focus gets long break', () => {
  const t = { ...timer, mode: 'pomodoro' };
  let f = startFocus(idleFocus('pomodoro', 25, t), 0);
  let r = advanceFocus(f, t, 25 * 60000 + 1);
  assert.deepEqual(r.events.map((e) => e.type), ['focusDone']);
  assert.equal(r.focus.phase, 'break');
  assert.equal(r.focus.running, true);
  assert.equal(r.focus.endAt, 30 * 60000, 'break starts at the focus end time, not at the check time');
  r = advanceFocus(r.focus, t, 31 * 60000);
  assert.equal(r.focus.phase, 'focus');
  assert.equal(r.focus.cycle, 2);
  assert.equal(r.focus.running, false);
  // phone locked through focus and break: both complete in order
  f = startFocus(idleFocus('pomodoro', 25, t, 4, 'focus'), 0);
  r = advanceFocus(f, t, 2 * 3600 * 1000);
  assert.deepEqual(r.events.map((e) => e.type), ['focusDone', 'breakDone']);
  assert.ok(r.events[1].long);
  assert.equal(r.focus.cycle, 1);
});
test('reset credits partial focus ≥ 1 minute, never breaks', () => {
  const f = startFocus(idleFocus('single', 25, timer), 0);
  assert.equal(resetFocus(f, timer, 7.5 * 60000).creditMin, 7);
  assert.equal(resetFocus(f, timer, 30000).creditMin, 0);
  const b = startFocus(idleFocus('pomodoro', 25, timer, 1, 'break'), 0);
  assert.equal(resetFocus(b, timer, 4 * 60000).creditMin, 0);
});
test('focus stats: today, week, total; midnight-spanning session counts on its end day', () => {
  let st = { days: {}, totalMin: 0, sessions: 0 };
  st = creditFocus(st, KST('2026-10-25T00:10:00'), 25, true);
  st = creditFocus(st, KST('2026-10-24T22:00:00'), 10, false);
  assert.deepEqual(st.days['2026-10-25'], { min: 25, sessions: 1 });
  assert.equal(st.totalMin, 35);
  assert.equal(st.sessions, 1);
  const w = weekStats(st, KST('2026-10-25T12:00:00'));
  assert.equal(w.length, 7);
  assert.equal(w[6].day, '2026-10-25');
  assert.equal(w[5].min, 10);
});

// ------------------------------------------------------------------ alarms
const A = (o) => normalizeAlarms([{ id: 'a', time: '07:30', days: [1, 2, 3, 4, 5], on: true, title: 't', ...o }])[0];
test('alarm rings once per day; catch-up window covers a throttled tab', () => {
  const a = A({});
  const mon0730 = KST('2026-10-26T07:30:20');
  let due = alarmDue([a], mon0730, {});
  assert.equal(due.length, 1);
  assert.equal(alarmDue([a], mon0730 + 30000, { a: due[0].key }).length, 0, 'no double ring');
  assert.equal(alarmDue([a], KST('2026-10-26T07:32:10'), {}).length, 1, 'woke 2 min late: still rings');
  assert.equal(alarmDue([a], KST('2026-10-26T07:34:00'), {}).length, 0, 'too late: skipped');
  assert.equal(alarmDue([a], KST('2026-10-25T07:30:00'), {}).length, 0, 'Sunday not selected');
});
test('midnight boundary: 23:59 Saturday alarm checked at 00:00 Sunday still rings for Saturday', () => {
  const a = A({ time: '23:59', days: [6] });
  const due = alarmDue([a], KST('2026-10-25T00:00:30'), {});
  assert.equal(due.length, 1);
  assert.equal(due[0].key, '2026-10-24|a');
});
test('alarm switched on after its minute passed does not ring retroactively', () => {
  const a = A({ armedAt: KST('2026-10-26T07:31:30') });
  assert.equal(alarmDue([a], KST('2026-10-26T07:31:40'), {}).length, 0);
});
test('next alarm across the week and its relative time', () => {
  const a = A({ time: '07:30', days: [1] });
  const n = nextAlarm([a, A({ id: 'b', on: false, time: '06:00', days: [0] })], KST('2026-10-25T21:00:00'));
  assert.equal(n.alarm.id, 'a');
  assert.equal(n.inMin, 630);
  assert.equal(n.today, false);
  assert.equal(nextAlarm([], Date.now()), null);
});
test('duplicate alarms are detected only when both are on and share a weekday', () => {
  const x = A({ id: 'x', days: [1, 2] }), y = A({ id: 'y', days: [2, 3] }), z = A({ id: 'z', days: [4] });
  assert.deepEqual([...duplicateAlarms([x, y, z])].sort(), ['x', 'y']);
  assert.equal(duplicateAlarms([x, { ...y, on: false }]).size, 0);
});
test('M6 projection sends only an alarm ringing within 24 h (firmware keeps one daily alarm)', () => {
  const a = A({ time: '07:30', days: [1] });
  assert.deepEqual(m6AlarmProjection([a], KST('2026-10-25T21:00:00')).en, true);
  assert.deepEqual(m6AlarmProjection([a], KST('2026-10-25T21:00:00')).h, 7);
  assert.equal(m6AlarmProjection([a], KST('2026-10-24T09:00:00')).en, false, 'next Monday is > 24 h away');
});

// ------------------------------------------------------------------ bond, badges, records, daily
test('visit streak, pet daily cap and bond level', () => {
  let b = { points: 0, firstDay: '', lastDay: '', daysTogether: 0, streak: 0, petDay: '', petsToday: 0 };
  b = touchVisit(b, '2026-10-24');
  b = touchVisit(b, '2026-10-25');
  b = touchVisit(b, '2026-10-25');
  assert.equal(b.daysTogether, 2);
  assert.equal(b.streak, 2);
  let gained = 0;
  for (let i = 0; i < 8; i++) { const r = addBond(b, 1, 'pet', '2026-10-25'); b = r.bond; gained += r.gained; }
  assert.equal(gained, 5);
  assert.equal(bondLevel(0).level, 1);
  assert.equal(bondLevel(30).level, 3);
  assert.equal(touchVisit(b, '2026-10-28').streak, 1);
});
test('badges are awarded once with the earning day', () => {
  const s = normalizeState({ stats: { days: {}, totalMin: 25, sessions: 1 } });
  const r = newBadges(s, '2026-10-25');
  assert.ok(r.earned.some((b) => b.id === 'FOCUS'));
  assert.equal(newBadges({ ...s, badges: r.badges }, '2026-10-26').earned.length, 0);
});
test('records: higher-is-better and lower-is-better', () => {
  let g = {};
  let r = recordResult(g, 'cry', 'normal-5', 3, false, 'd'); g = r.games; assert.ok(r.isBest);
  r = recordResult(g, 'cry', 'normal-5', 2, false, 'd'); g = r.games; assert.ok(!r.isBest); assert.equal(g.cry.best['normal-5'], 3); assert.equal(g.cry.plays, 2);
  r = recordResult(g, 'reaction', 'avg-5', 300, true, 'd'); g = r.games;
  r = recordResult(g, 'reaction', 'avg-5', 250, true, 'd'); assert.ok(r.isBest);
  r = recordResult(r.games, 'balance', 'q5', null, false, 'd'); assert.ok(!r.isBest); assert.equal(r.games.balance.plays, 1);
});
test('daily pick is stable for a day and the type quiz always contains the answer once', () => {
  assert.deepEqual(dailyPick('2026-10-25'), dailyPick('2026-10-25'));
  const days = new Set(Array.from({ length: 30 }, (_, i) => dailyPick(`2026-11-${String(i + 1).padStart(2, '0')}`).pokemon.id));
  assert.ok(days.size >= 10, 'variety across a month');
  for (const p of POKEDEX) {
    const q = typeQuiz(p, '2026-10-25');
    assert.equal(q.choices.length, 4);
    assert.equal(q.choices.filter((c) => c === q.answer).length, 1);
    assert.deepEqual(typeQuiz(p, '2026-10-25'), q);
  }
});

// ------------------------------------------------------------------ games
const seeded = (seed = 1) => () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
test('quiz choices: 4 distinct, answer included, hard prefers shared types', () => {
  const gengar = byId(94);
  for (let i = 0; i < 50; i++) {
    const c = cryChoices(gengar, POKEDEX, 4, true, seeded(i + 1));
    assert.equal(new Set(c.map((p) => p.id)).size, 4);
    assert.ok(c.includes(gengar));
    assert.ok(c.some((p) => p.id === 778), 'Mimikyu shares Ghost with Gengar');
  }
});
test('fresh deck avoids immediate repeats and prefers unseen Pokémon', () => {
  const d = freshDeck(PARTNERS, 20, {}, seeded(3));
  assert.equal(d.length, 20);
  for (let i = 1; i < d.length; i++) assert.notEqual(d[i].id, d[i - 1].id);
  const seen = Object.fromEntries(PARTNERS.slice(0, 6).map((p, i) => [p.id, i + 1]));
  const first = freshDeck(PARTNERS, 2, seen, seeded(4)).map((p) => p.id);
  assert.ok(first.every((id) => !seen[id]));
});
test('memory: pairs, match, miss and settle', () => {
  const cards = makeBoard('4x3', seeded(9));
  assert.equal(cards.length, 12);
  let g = { cards, pending: [], moves: 0, matched: 0 };
  const a = cards[0];
  const twin = cards.find((c) => c.id === a.id && c.k !== a.k);
  const other = cards.find((c) => c.id !== a.id);
  let r = flip(g, a.k); g = r.game; assert.equal(r.event, 'flip');
  assert.equal(flip(g, a.k).event, 'ignore', 'same card twice is ignored');
  r = flip(g, other.k); g = r.game; assert.equal(r.event, 'miss'); assert.equal(g.moves, 1);
  assert.equal(flip(g, twin.k).event, 'ignore', 'third card waits until the miss settles');
  g = settle(g);
  r = flip(g, a.k); g = r.game; r = flip(g, twin.k); g = r.game;
  assert.equal(r.event, 'match'); assert.equal(g.matched, 1); assert.equal(g.moves, 2);
  assert.equal(makeBoard('4x4').length, 16);
});
test('runner: collisions, scoring, invulnerability and game over without images', () => {
  const s = createRunner(640, seeded(5));
  assert.ok(circleHit({ x: 0, y: 0, r: 10 }, { x: 15, y: 0, r: 10 }));
  assert.ok(!circleHit({ x: 0, y: 0, r: 10 }, { x: 15, y: 0, r: 10 }, 0.7));
  s.items = [{ kind: 'star', x: s.ghost.x, y: s.ghost.y, r: 13 }];
  stepRunner(s, 0.016, {});
  assert.equal(s.stars, 1); assert.equal(s.combo, 1); assert.equal(s.score, 10);
  s.items = [{ kind: 'orb', x: s.ghost.x, y: s.ghost.y, r: 20 }];
  stepRunner(s, 0.016, {});
  assert.equal(s.lives, 2); assert.equal(s.combo, 0);
  s.items = [{ kind: 'orb', x: s.ghost.x, y: s.ghost.y, r: 20 }];
  stepRunner(s, 0.016, {});
  assert.equal(s.lives, 2, 'invulnerable right after a hit');
  s.invuln = 0; s.lives = 1;
  s.items = [{ kind: 'orb', x: s.ghost.x, y: s.ghost.y, r: 20 }];
  stepRunner(s, 0.016, {});
  assert.ok(s.over);
  assert.ok(totalScore(s) >= 10);
});
test('runner: difficulty ramps and pointer control is clamped to the field', () => {
  const s = createRunner(800, seeded(7));
  for (let i = 0; i < 60 * 30; i++) { stepRunner(s, 1 / 60, { targetY: -500 }); s.invuln = 9; s.lives = 3; }
  assert.ok(s.speed > 300, `speed ${s.speed}`);
  assert.equal(s.ghost.y, s.ghost.r);
  assert.ok(s.items.length < 40, 'off-screen items are released');
  stepRunner(s, 5, {});
  assert.ok(s.t < 30.1, 'dt is clamped');
});
test('balance summary uses only the player picks', () => {
  const picks = [PROMPTS[0].a, PROMPTS[5].a, PROMPTS[1].a];
  assert.equal(summarize(picks).type, 'night');
  assert.equal(PROMPTS.length >= 10, true);
  for (const p of PROMPTS) { assert.ok(byId(p.a.pokemon)); assert.ok(byId(p.b.pokemon)); }
});

// ------------------------------------------------------------------ BLE (app side)
test('Capacitor hex codec round-trips and tolerates spaces', () => {
  const u8 = new Uint8Array([0, 15, 16, 255, 123]);
  assert.equal(_hex.toHex(u8), '000f10ff7b', 'same format as @capacitor-community/bluetooth-le 7.3 dataViewToHexString');
  assert.deepEqual(_hex.fromHex('00 0f 10 ff 7b'), u8);
  assert.deepEqual(_hex.fromHex('000f10ff7b'), u8);
});
test('all app commands fit the 180-byte limit, including a 30-syllable message', () => {
  const big = encodeCommand(0xffffffff, 0xfffffffe, 'message', { txt: '가'.repeat(30) });
  assert.ok(big.byteLength <= MAX_COMMAND_BYTES, `${big.byteLength}`);
  assert.throws(() => encodeCommand(1, 1, 'partner', { id: 25 }), RangeError, 'Pikachu is not an M6 partner');
});
test('mock transport + real client: ACK, state notify, NACK mapping', async () => {
  const c = new PokeDockClient(new MockTransport(), { autoSync: true, ackTimeoutMs: 500 });
  const s = await c.connect();
  assert.equal(s.clock.trusted, true, 'client auto-synced the untrusted clock');
  await c.setPartner(393);
  await new Promise((r) => setTimeout(r, 80));
  assert.equal(c.state.partner, 393);
  await assert.rejects(c.focusPause(), (e) => e.code === 'state');
  assert.match(describeError({ code: 'auth' }), /페어링/);
  assert.match(describeError(new Error('ack timeout')), /응답/);
});
