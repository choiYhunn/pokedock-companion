// V18 app ↔ real M6 ProtocolEngine (C++ host build from PR #21) over a simulated GATT link.
// Build the bridge from the M6 branch:  g++ -std=c++17 -O1 v16/masterball-m6/tests/ble_bridge_host.cpp -o ble_bridge
// Run:  node mobile-v18/tests/ble_bridge_app_test.mjs <path to ble_bridge executable>
// This is NOT a radio test: pairing, MTU negotiation and range need the real board (gate G3).
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import readline from 'node:readline';
import { PokeDockClient } from '../ble/pokedock_ble_client.mjs';
import { m6AlarmProjection, normalizeAlarms } from '../core.js';
import { describeError } from '../ble/m6.js';

const exe = process.argv[2];
if (!exe) { console.error('usage: node ble_bridge_app_test.mjs <ble_bridge exe>'); process.exit(2); }
const toHex = (u8) => Buffer.from(u8).toString('hex');
const fromHex = (h) => new Uint8Array(Buffer.from(h, 'hex'));

class Device {
  constructor() {
    this.p = spawn(exe, [], { stdio: ['pipe', 'pipe', 'inherit'] });
    this.rl = readline.createInterface({ input: this.p.stdout });
    this.waiters = [];
    this.sink = null;
    this.rl.on('line', (l) => {
      const w = this.waiters.findIndex((x) => x.match(l));
      if (w >= 0) return this.waiters.splice(w, 1)[0].resolve(l);
      this.sink?.(l);
    });
  }
  cmd(line, match) { return new Promise((resolve) => { this.waiters.push({ match, resolve }); this.p.stdin.write(line + '\n'); }); }
  send(line) { this.p.stdin.write(line + '\n'); }
  rev() { return this.cmd('X', (l) => l.startsWith('X ')).then((l) => Number(l.slice(2))); }
  tick(ms) { return this.cmd(`T ${ms}`, (l) => l === 'K'); }
  close() { this.p.stdin.end(); }
}
class Link {
  constructor(dev, { mtu = 185, authenticated = true } = {}) { Object.assign(this, { dev, mtu, authenticated, dropAcks: 0, writes: 0, up: false }); }
  async connect(onEvent, onDisconnect) {
    this.onDisconnect = onDisconnect;
    this.up = true;
    this.dev.sink = (l) => {
      if (!this.up) return;
      const [k, h] = l.split(' ');
      if (k === 'N' && this.dropAcks > 0) { this.dropAcks--; return; }
      if (k === 'N' || k === 'S') {
        const b = fromHex(h);
        if (b.byteLength > this.mtu - 3) throw new Error(`notify ${b.byteLength} B > MTU ${this.mtu}`);
        queueMicrotask(() => onEvent(b));
      }
    };
    return { mtu: this.mtu };
  }
  async write(u8) {
    if (!this.up) throw new Error('not connected');
    if (u8.byteLength > this.mtu - 3) throw new Error('ATT write exceeds MTU');
    this.writes++;
    this.dev.send(`W ${this.authenticated ? 1 : 0} ${toHex(u8)}`);
  }
  async read() { return fromHex((await this.dev.cmd('R', (x) => x.startsWith('S '))).slice(2)); }
  async disconnect() { this.up = false; }
  drop() { this.up = false; setTimeout(() => this.onDisconnect(), 5); }
}

const results = [];
async function test(name, fn) {
  try { await fn(); results.push(['PASS', name]); } catch (e) { results.push(['FAIL', name, e.message]); }
}
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
const fast = { ackTimeoutMs: 300, sleep: (ms) => wait(Math.min(ms, 20)) };

const dev = new Device();
await dev.cmd('', (l) => l.startsWith('READY'));
// Sunday 2026-10-25 21:00 KST
let wall = Date.parse('2026-10-25T21:00:00+09:00');
let mono = 0;
const link = new Link(dev);
const app = new PokeDockClient(link, { ...fast, random: () => 0.31, now: () => wall });

await test('connect: reads state and auto time_syncs the untrusted clock (no RTC cell)', async () => {
  const s = await app.connect();
  assert.equal(s.clock.trusted, true);
  assert.equal(s.firmware, 'm6-0.2.0');
});

await test('app partner change reaches the device; non-partner is refused before sending', async () => {
  await app.setPartner(94);
  await wait(30);
  assert.equal(app.state.partner, 94);
  const w = link.writes;
  await assert.rejects(app.setPartner(25), RangeError);
  assert.equal(link.writes, w);
});

await test('V18 weekday alarm is projected to the single M6 alarm and rings on the device', async () => {
  const alarms = normalizeAlarms([{ id: 'mon', time: '07:30', days: [1], on: true, title: '월요일 아침' }, { id: 'off', time: '06:00', days: [1], on: false, title: 'x' }]);
  const p = m6AlarmProjection(alarms, wall);
  assert.deepEqual([p.h, p.m, p.en], [7, 30, true]);
  await app.setAlarm(p.h, p.m, p.en);
  mono += (10 * 60 + 30) * 60000; wall += (10 * 60 + 30) * 60000; // to Monday 07:30
  await dev.tick(mono);
  await wait(30);
  await app.refresh();
  assert.equal(app.state.alarm.ringing, true);
  await app.dismissAlarm();
  await wait(30);
  assert.equal(app.state.alarm.ringing, false);
});

await test('no alarm within 24 h → the app disables the device alarm', async () => {
  const p = m6AlarmProjection(normalizeAlarms([{ id: 'mon', time: '07:30', days: [1], on: true }]), wall + 60000);
  assert.equal(p.en, false);
  await app.setAlarm(p.h, p.m, p.en);
  await app.refresh();
  assert.equal(app.state.alarm.enabled, false);
});

await test('focus start / pause / resume / cancel mirror the app timer', async () => {
  await app.focusStart(25);
  await app.refresh();
  assert.equal(app.state.focus.phase, 'running');
  await app.focusPause();
  await app.refresh();
  assert.equal(app.state.focus.phase, 'paused');
  await app.focusResume();
  await app.focusCancel();
  await app.refresh();
  assert.equal(app.state.focus.phase, 'idle');
  await assert.rejects(app.focusPause(), (e) => e.code === 'state' && /상태/.test(describeError(e)));
});

await test('lost ACK is retried with the same seq and executed once', async () => {
  const before = await dev.rev();
  link.dropAcks = 1;
  await app.setBrightness(70);
  assert.equal(await dev.rev(), before + 1);
});

await test('link drop → automatic reconnect on next command, state re-read', async () => {
  link.drop();
  await wait(20);
  await app.setSound(false);
  await app.refresh();
  assert.equal(app.state.sound, false);
});

await test('Korean message from 우리 서랍 (30 syllables) fits, 31 is refused locally', async () => {
  await app.setMessage('가'.repeat(30));
  await assert.rejects(async () => app.setMessage('가'.repeat(31)), RangeError);
});

await test('unauthenticated link → auth NACK with a readable Korean hint', async () => {
  link.authenticated = false;
  await assert.rejects(app.setPartner(393), (e) => e.code === 'auth' && /페어링/.test(describeError(e)));
  link.authenticated = true;
});

dev.close();
for (const r of results) console.log(r.join('  '));
const failed = results.filter((r) => r[0] === 'FAIL').length;
console.log(`${failed ? 'FAIL' : 'PASS'}: ${results.length - failed}/${results.length} app↔engine checks (simulated link; not a radio test)`);
process.exit(failed ? 1 : 0);
