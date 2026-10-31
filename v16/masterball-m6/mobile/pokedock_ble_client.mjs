// PokéDock BLE GATT client (phone = central). Transport-agnostic: give it an object with
//   connect(onEvent, onDisconnect) -> {mtu}, write(Uint8Array), read() -> Uint8Array, disconnect()
// Capacitor (Android/iOS) and test transports implement that interface.
//
// Guarantees: every command waits for its ACK (timeout -> retry with the SAME seq so the device
// executes it once); a fresh random session id per app launch; state is re-read after every
// (re)connect; reconnect uses capped exponential backoff; inputs are validated before sending.
import { MIN_MTU, decodeEvent, encodeCommand } from './pokedock_ble_protocol.mjs';

export class PokeDockClient {
  constructor(transport, { ackTimeoutMs = 2000, retries = 3, random = Math.random, sleep, log = () => {}, now = () => Date.now(),
    autoSync = true } = {}) {
    this.now = now;
    this.autoSync = autoSync;
    this.t = transport;
    this.ackTimeoutMs = ackTimeoutMs;
    this.retries = retries;
    this.session = Math.floor(random() * 0xffffffff) >>> 0;
    this.seq = 0;
    this.pending = new Map();
    this.state = null;
    this.connected = false;
    this.listeners = new Set();
    this.sleep = sleep ?? ((ms) => new Promise((r) => setTimeout(r, ms)));
    this.log = log;
    this.queue = Promise.resolve();
    this.wantConnected = false;
  }

  onState(fn) { this.listeners.add(fn); return () => this.listeners.delete(fn); }

  async connect() {
    this.wantConnected = true;
    const { mtu } = await this.t.connect((bytes) => this.#onEvent(bytes), () => this.#onDisconnect());
    if (mtu < MIN_MTU) {
      await this.t.disconnect();
      throw new Error(`MTU ${mtu} < ${MIN_MTU}: phone/OS refused a large enough MTU`);
    }
    this.connected = true;
    await this.refresh();
    // No RTC backup cell: after any power cut the ball's clock is untrusted until a phone syncs it.
    const c = this.state.clock;
    if (this.autoSync && (!c.trusted || c.syncAgeMin < 0 || c.syncAgeMin > 12 * 60)) {
      await this.#sendNow('time_sync', this.#clockArgs());  // direct: we may already be inside a queued send
      this.log('clock synced on connect');
    }
    return this.state;
  }

  #clockArgs() {
    const t = this.now();
    return { t: Math.floor(t / 1000), tz: -new Date(t).getTimezoneOffset() };
  }

  async disconnect() { this.wantConnected = false; this.connected = false; await this.t.disconnect(); }

  async refresh() {
    const ev = decodeEvent(await this.t.read());
    this.#applyState(ev.state);
    return this.state;
  }

  // Serialise commands: write-with-response + ACK keeps ordering simple and MTU-safe.
  send(cmd, args = {}) {
    const run = () => this.#sendNow(cmd, args);
    const p = this.queue.then(run, run);
    this.queue = p.catch(() => {});
    return p;
  }

  async #sendNow(cmd, args) {
    const seq = (this.seq = (this.seq % 0xfffffffe) + 1);
    const bytes = encodeCommand(this.session, seq, cmd, args); // throws before anything is sent
    let lastErr;
    for (let attempt = 0; attempt <= this.retries; attempt++) {
      if (!this.connected) await this.#reconnect();
      const ack = new Promise((resolve, reject) => {
        const timer = setTimeout(() => { this.pending.delete(seq); reject(new Error('ack timeout')); }, this.ackTimeoutMs);
        this.pending.set(seq, (a) => { clearTimeout(timer); resolve(a); });
      });
      try {
        await this.t.write(bytes);
        const a = await ack;
        if (!a.ok) {
          const e = new Error(`device refused ${cmd}: ${a.error}`);
          e.code = a.error;
          throw e;
        }
        return a;
      } catch (e) {
        this.pending.delete(seq);
        if (e.code) throw e; // a NACK is final, retrying cannot help
        lastErr = e;
        this.log(`retry ${cmd} seq=${seq} attempt=${attempt + 1}: ${e.message}`);
      }
    }
    throw lastErr;
  }

  async #reconnect() {
    let delay = 250;
    for (let i = 0; i < 6 && this.wantConnected; i++) {
      try {
        await this.connect();
        return;
      } catch (e) {
        this.log(`reconnect failed: ${e.message}`);
        await this.sleep(delay);
        delay = Math.min(delay * 2, 4000);
      }
    }
    throw new Error('device unreachable');
  }

  #onEvent(bytes) {
    let ev;
    try { ev = decodeEvent(bytes); } catch (e) { this.log(`bad event: ${e.message}`); return; }
    if (ev.kind === 'ack') {
      const cb = this.pending.get(ev.seq);
      if (cb) { this.pending.delete(ev.seq); cb(ev); }
    } else this.#applyState(ev.state);
  }

  #applyState(s) {
    if (this.state && s.rev < this.state.rev) return; // stale notification after reconnect
    this.state = s;
    for (const fn of this.listeners) fn(s);
  }

  #onDisconnect() {
    this.connected = false;
    for (const [seq, cb] of this.pending) { this.pending.delete(seq); void cb; }
  }

  // convenience API used by the V17 screens
  setPartner(id) { return this.send('partner', { id }); }
  setBrightness(val) { return this.send('brightness', { val }); }
  setSound(on) { return this.send('sound', { on }); }
  focusStart(min) { return this.send('focus_start', { min }); }
  focusPause() { return this.send('focus_pause'); }
  focusResume() { return this.send('focus_resume'); }
  focusCancel() { return this.send('focus_cancel'); }
  setAlarm(h, m, en) { return this.send('alarm_set', { h, m, en }); }
  dismissAlarm() { return this.send('alarm_dismiss'); }
  snoozeAlarm() { return this.send('alarm_snooze'); }
  setMessage(txt) { return this.send('message', { txt }); }
  syncClock() { return this.send('time_sync', this.#clockArgs()); }
}
