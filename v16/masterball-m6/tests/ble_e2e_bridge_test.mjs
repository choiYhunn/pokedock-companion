// End-to-end test: real JS client  <->  simulated GATT link  <->  real C++ ProtocolEngine (host build).
// The link layer simulates MTU negotiation, encryption/authentication state, lost notifications
// and disconnects. This is NOT a radio test; see docs for the on-device checklist.
// usage: node ble_e2e_bridge_test.mjs <path-to-ble_bridge_host executable>
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import readline from 'node:readline';
import { PokeDockClient } from '../mobile/pokedock_ble_client.mjs';

const exe = process.argv[2];
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
  cmd(line, match) {
    return new Promise((resolve) => { this.waiters.push({ match, resolve }); this.p.stdin.write(line + '\n'); });
  }
  send(line) { this.p.stdin.write(line + '\n'); }
  rev() { return this.cmd('X', (l) => l.startsWith('X ')).then((l) => Number(l.slice(2))); }
  async tick(ms) { await this.cmd(`T ${ms}`, (l) => l === 'K'); }
  close() { this.p.stdin.end(); }
}

class LinkTransport {
  constructor(dev, { mtu = 185, authenticated = true } = {}) {
    Object.assign(this, { dev, mtu, authenticated, dropAcks: 0, dropAfterWrite: false, connects: 0, writes: 0 });
  }
  async connect(onEvent, onDisconnect) {
    this.connects++;
    this.onEvent = onEvent;
    this.onDisconnect = onDisconnect;
    this.up = true;
    this.dev.sink = (l) => {
      if (!this.up) return;
      const [k, h] = l.split(' ');
      if (k === 'N' && this.dropAcks > 0) { this.dropAcks--; return; }
      if (k === 'N' || k === 'S') {
        const bytes = fromHex(h);
        if (bytes.byteLength > this.mtu - 3) throw new Error(`notification ${bytes.byteLength} B exceeds MTU ${this.mtu}`);
        queueMicrotask(() => this.onEvent(bytes));
      }
    };
    return { mtu: this.mtu };
  }
  async write(u8) {
    if (!this.up) throw new Error('not connected');
    if (u8.byteLength > this.mtu - 3) throw new Error('ATT write exceeds MTU');
    this.writes++;
    this.dev.send(`W ${this.authenticated ? 1 : 0} ${toHex(u8)}`);
    if (this.dropAfterWrite) {      // link drops before the ACK can be notified
      this.dropAfterWrite = false;
      this.up = false;
      setTimeout(() => this.onDisconnect(), 5);
    }
  }
  async read() {
    const l = await this.dev.cmd('R', (x) => x.startsWith('S '));
    return fromHex(l.slice(2));
  }
  async disconnect() { this.up = false; }
}

const results = [];
async function test(name, fn) {
  try { await fn(); results.push(['PASS', name]); } catch (e) { results.push(['FAIL', name, e.message]); }
}

const dev = new Device();
await dev.cmd('', (l) => l.startsWith('READY'));
const fast = { ackTimeoutMs: 300, sleep: (ms) => new Promise((r) => setTimeout(r, Math.min(ms, 20))) };

await test('MTU below 185 is refused before any command', async () => {
  const c = new PokeDockClient(new LinkTransport(dev, { mtu: 23 }), fast);
  await assert.rejects(c.connect(), /MTU 23/);
});

const link = new LinkTransport(dev);
const app = new PokeDockClient(link, { ...fast, random: () => 0.25 });
const seen = [];
app.onState((s) => seen.push(s));

await test('connect reads initial state (device standalone defaults)', async () => {
  const s = await app.connect();
  assert.equal(s.partner, 94);
  assert.equal(s.firmware, 'm6-0.1.0');
  assert.equal(s.clock.trusted, false);
});

await test('unauthenticated link: write refused with auth error, nothing changes', async () => {
  link.authenticated = false;
  const before = await dev.rev();
  await assert.rejects(app.setPartner(393), (e) => e.code === 'auth');
  assert.equal(await dev.rev(), before);
  link.authenticated = true;
});

await test('set partner -> ACK ok + state notification', async () => {
  await app.setPartner(393);
  await new Promise((r) => setTimeout(r, 30));
  assert.equal(app.state.partner, 393);
});

await test('invalid input rejected locally, never sent', async () => {
  const w = link.writes;
  await assert.rejects(app.send('partner', { id: 999 }), RangeError);
  await assert.rejects(app.setBrightness(0), RangeError);
  await assert.rejects(app.send('partner', { id: 94, extra: 1 }), RangeError);
  await assert.rejects(app.send('remote_reset'), RangeError);
  assert.equal(link.writes, w);
});

await test('lost ACK -> retry with same seq -> executed exactly once', async () => {
  const before = await dev.rev();
  link.dropAcks = 1;
  await app.focusStart(25);
  assert.equal(await dev.rev(), before + 1);
  assert.ok(link.writes >= 2);
});

await test('disconnect after write -> reconnect -> cached ACK, no double execution, state resync', async () => {
  const before = await dev.rev();
  const connects = link.connects;
  link.dropAfterWrite = true;
  await app.focusPause();
  assert.equal(await dev.rev(), before + 1);
  assert.ok(link.connects > connects);
  assert.equal(app.state.focus.phase, 'paused');
});

await test('device runs standalone while app is away; app resyncs on connect', async () => {
  await app.focusResume();
  await app.disconnect();
  await dev.tick(5 * 60000);
  const s = await app.connect();
  assert.equal(s.focus.phase, 'running');
  assert.ok(s.focus.remaining_s <= 20 * 60 + 1 && s.focus.remaining_s >= 20 * 60 - 1, `remaining ${s.focus.remaining_s}`);
});

await test('clock sync + daily alarm rings on device and is dismissed from the app', async () => {
  const now = Date.UTC(2026, 9, 24, 22, 28, 0); // 07:28 KST
  await app.send('time_sync', { t: Math.floor(now / 1000), tz: 540 });
  await app.setAlarm(7, 30, true);
  await dev.tick(5 * 60000 + 3 * 60000);
  await new Promise((r) => setTimeout(r, 30));
  assert.equal(app.state.alarm.ringing, true);
  await app.dismissAlarm();
  await new Promise((r) => setTimeout(r, 30));
  assert.equal(app.state.alarm.ringing, false);
  assert.equal(app.state.clock.trusted, true);
});

await test('Korean private message within 90 bytes; 31 syllables refused locally', async () => {
  await app.setMessage('오늘도 같이 집중하자 팬텀이랑');
  await assert.rejects(async () => app.setMessage('가'.repeat(31)), RangeError);
});

await test('app restart = new session, seq restarts at 1 and still executes', async () => {
  const before = await dev.rev();
  const restarted = new PokeDockClient(new LinkTransport(dev), { ...fast, random: () => 0.75 });
  await restarted.connect();
  await restarted.setSound(false);
  assert.equal(await dev.rev(), before + 1);
  assert.equal(restarted.seq, 1);
});

await test('every ACK/state fits a 185-byte MTU (enforced by link)', async () => {
  await app.refresh();
  assert.ok(app.state.rev > 1);
});

dev.close();
for (const r of results) console.log(r.join('  '));
const failed = results.filter((r) => r[0] === 'FAIL').length;
console.log(`${failed ? 'FAIL' : 'PASS'}: ${results.length - failed} passed, ${failed} failed (simulated link; not a radio test)`);
process.exit(failed ? 1 : 0);
