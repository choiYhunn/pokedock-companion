// Transports for PokeDockClient: connect(onEvent, onDisconnect) -> {mtu}, write(u8), read() -> u8, disconnect().
// None of them has been exercised against a real M6 board yet (hardware gate G3).
import { COMMAND_UUID, EVENT_UUID, SERVICE_UUID, STATE_UUID, PARTNERS, MAX_MESSAGE_BYTES } from './pokedock_ble_protocol.mjs';

const u8of = (dv) => new Uint8Array(dv.buffer, dv.byteOffset, dv.byteLength);

// Web Bluetooth: Chrome/Edge on Android, Windows, macOS, ChromeOS. Not available in iPhone Safari.
export class WebBluetoothTransport {
  static supported() {
    return typeof navigator !== 'undefined' && !!navigator.bluetooth && (typeof isSecureContext === 'undefined' || isSecureContext);
  }
  constructor() { this.device = null; }
  async connect(onEvent, onDisconnect) {
    if (!this.device) {
      // Needs a user gesture; the browser shows its own device chooser.
      this.device = await navigator.bluetooth.requestDevice({ filters: [{ services: [SERVICE_UUID] }], optionalServices: [SERVICE_UUID] });
    }
    if (this.onGone) this.device.removeEventListener('gattserverdisconnected', this.onGone);
    this.onGone = () => onDisconnect();
    this.device.addEventListener('gattserverdisconnected', this.onGone);
    const server = await this.device.gatt.connect();
    const svc = await server.getPrimaryService(SERVICE_UUID);
    [this.cmd, this.evt, this.state] = await Promise.all([COMMAND_UUID, EVENT_UUID, STATE_UUID].map((u) => svc.getCharacteristic(u)));
    if (this.onValue) this.evt.removeEventListener('characteristicvaluechanged', this.onValue);
    this.onValue = (e) => onEvent(u8of(e.target.value));
    this.evt.addEventListener('characteristicvaluechanged', this.onValue);
    await this.evt.startNotifications();
    // Chrome negotiates the ATT MTU itself (up to 517) and does not expose it; the firmware asks for 247.
    return { mtu: 247 };
  }
  write(u8) { return this.cmd.writeValueWithResponse(u8); }
  async read() { return u8of(await this.state.readValue()); }
  async disconnect() { try { this.device?.gatt?.disconnect(); } catch { /* already gone */ } }
  get name() { return this.device?.name || ''; }
}

// Capacitor native (Android/iOS) through @capacitor-community/bluetooth-le's bridge object.
// The raw plugin API exchanges values as hex strings (bluetooth-le 7.x writes "0a1b…", reads either form).
const toHex = (u8) => Array.from(u8, (b) => b.toString(16).padStart(2, '0')).join('');
const fromHex = (s) => {
  const h = String(s || '').replace(/[^0-9a-f]/gi, '');
  const out = new Uint8Array(h.length >> 1);
  for (let i = 0; i < out.length; i++) out[i] = parseInt(h.substr(i * 2, 2), 16);
  return out;
};
export class CapacitorBleTransport {
  static plugin() {
    const C = typeof window !== 'undefined' ? window.Capacitor : null;
    if (!C?.isNativePlatform?.()) return null;
    if (C.isPluginAvailable && !C.isPluginAvailable('BluetoothLe')) return null;
    return C.Plugins?.BluetoothLe || null;
  }
  static supported() { return !!CapacitorBleTransport.plugin(); }
  constructor({ deviceId = null } = {}) { this.deviceId = deviceId; this.ble = CapacitorBleTransport.plugin(); this.subs = []; }
  async connect(onEvent, onDisconnect) {
    const ble = this.ble;
    await ble.initialize({ androidNeverForLocation: true });
    if (!this.deviceId) {
      const dev = await ble.requestDevice({ services: [SERVICE_UUID], namePrefix: 'PokeDock' });
      this.deviceId = dev.deviceId;
      this.deviceName = dev.name || '';
    }
    for (const s of this.subs) await s.remove?.();
    this.subs = [];
    this.subs.push(await ble.addListener(`disconnected|${this.deviceId}`, () => onDisconnect()));
    await ble.connect({ deviceId: this.deviceId, timeout: 10000 });
    // Bond before touching the encrypted characteristics; Android shows the passkey dialog and the
    // 6 digits appear on the ball's screen.
    try { await ble.createBond({ deviceId: this.deviceId }); } catch { /* iOS bonds on first encrypted access */ }
    let mtu = 185;
    try { mtu = (await ble.getMtu({ deviceId: this.deviceId })).value || mtu; } catch { /* iOS negotiates itself */ }
    const key = `notification|${this.deviceId}|${SERVICE_UUID}|${EVENT_UUID}`;
    this.subs.push(await ble.addListener(key, (r) => onEvent(fromHex(r?.value))));
    await ble.startNotifications({ deviceId: this.deviceId, service: SERVICE_UUID, characteristic: EVENT_UUID });
    return { mtu };
  }
  write(u8) { return this.ble.write({ deviceId: this.deviceId, service: SERVICE_UUID, characteristic: COMMAND_UUID, value: toHex(u8) }); }
  async read() { return fromHex((await this.ble.read({ deviceId: this.deviceId, service: SERVICE_UUID, characteristic: STATE_UUID })).value); }
  async disconnect() { if (this.deviceId) await this.ble.disconnect({ deviceId: this.deviceId }).catch(() => {}); }
  get name() { return this.deviceName || ''; }
}
export const _hex = { toHex, fromHex };

// TEST ONLY: an in-page imitation of the M6 protocol engine so UI flows can be checked without a
// board. Enabled with ?m6=mock and always labelled as a simulation in the UI.
export class MockTransport {
  static supported() { return true; }
  constructor() {
    this.rev = 1;
    this.dev = { p: 94, b: 40, snd: 1, f: [0, 0, 0], a: [0, 7, 0, 0], clk: [0, -1], msg: 0 };
    this.cache = new Map();
    this.name = 'PokeDock-MB (모의)';
  }
  async connect(onEvent, onDisconnect) {
    this.onEvent = onEvent; this.onDisconnect = onDisconnect; this.up = true;
    await new Promise((r) => setTimeout(r, 120));
    return { mtu: 247 };
  }
  stateJson() {
    const d = this.dev;
    return JSON.stringify({ r: this.rev, p: d.p, b: d.b, snd: d.snd, f: d.f, a: d.a, clk: d.clk, pwr: [4870, 1], msg: d.msg, fw: 'm6-0.2.0' });
  }
  async read() { return new TextEncoder().encode(this.stateJson()); }
  async write(u8) {
    if (!this.up) throw new Error('not connected');
    const o = JSON.parse(new TextDecoder().decode(u8));
    const k = `${o.s}:${o.q}`;
    let ack = this.cache.get(k);
    let changed = false;
    if (!ack) {
      const d = this.dev;
      const ok = (ch = true) => { if (ch) { this.rev++; changed = true; } return { q: o.q, ok: 1, r: this.rev }; };
      const no = (e) => ({ q: o.q, ok: 0, e });
      switch (o.c) {
        case 'get_state': ack = ok(false); break;
        case 'partner': ack = PARTNERS.includes(o.id) ? (d.p = o.id, ok()) : no('range'); break;
        case 'brightness': d.b = o.val; ack = ok(); break;
        case 'sound': d.snd = o.on ? 1 : 0; ack = ok(); break;
        case 'focus_start': ack = d.f[0] === 1 ? no('busy') : (d.f = [1, o.min * 60, o.min * 60], ok()); break;
        case 'focus_pause': ack = d.f[0] === 1 ? (d.f = [2, d.f[1], d.f[2]], ok()) : no('state'); break;
        case 'focus_resume': ack = d.f[0] === 2 ? (d.f = [1, d.f[1], d.f[2]], ok()) : no('state'); break;
        case 'focus_cancel': ack = d.f[0] ? (d.f = [0, 0, 0], ok()) : no('state'); break;
        case 'alarm_set': d.a = [o.en ? 1 : 0, o.h, o.m, 0]; ack = ok(); break;
        case 'alarm_dismiss': d.a[3] = 0; ack = ok(); break;
        case 'alarm_snooze': ack = no('state'); break;
        case 'time_sync': d.clk = [1, 0]; ack = ok(); break;
        case 'message': d.msg = new TextEncoder().encode(o.txt).byteLength; ack = d.msg <= MAX_MESSAGE_BYTES ? ok() : no('range'); break;
        case 'reaction': ack = ok(false); break;
        default: ack = no('unknown');
      }
      ack = JSON.stringify(ack);
      this.cache.set(k, ack);
    }
    const enc = new TextEncoder();
    setTimeout(() => {
      this.onEvent(enc.encode(ack));
      if (changed) this.onEvent(enc.encode(this.stateJson()));
    }, 40);
  }
  async disconnect() { this.up = false; }
}
