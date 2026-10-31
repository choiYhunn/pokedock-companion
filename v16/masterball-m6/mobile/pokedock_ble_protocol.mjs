// PokéDock BLE protocol v2 — client-side codec (single source for app + tests).
// Mirrors core/protocol.hpp. UUIDs share the edc0000x base already reserved in BLE_PROTOCOL v1.
export const SERVICE_UUID = 'edc00001-8148-4b41-9a3e-7bd93d2ab771';
export const COMMAND_UUID = 'edc00002-8148-4b41-9a3e-7bd93d2ab771'; // write with response, encrypted+authenticated
export const EVENT_UUID = 'edc00003-8148-4b41-9a3e-7bd93d2ab771';   // notify: ACK and state
export const STATE_UUID = 'edc00004-8148-4b41-9a3e-7bd93d2ab771';   // read: current state
export const MAX_COMMAND_BYTES = 180;
export const MAX_MESSAGE_BYTES = 90;
export const MIN_MTU = 185;
export const PARTNERS = Object.freeze([94, 393, 468, 448, 195, 175, 417, 385]);

const int = (v, lo, hi) => Number.isInteger(v) && v >= lo && v <= hi;
const enc = new TextEncoder();

const SPEC = {
  get_state: {},
  partner: { id: (v) => PARTNERS.includes(v) },
  brightness: { val: (v) => int(v, 1, 100) },
  sound: { on: (v) => typeof v === 'boolean' },
  focus_start: { min: (v) => int(v, 1, 120) },
  focus_pause: {}, focus_resume: {}, focus_cancel: {},
  alarm_set: { h: (v) => int(v, 0, 23), m: (v) => int(v, 0, 59), en: (v) => typeof v === 'boolean' },
  alarm_dismiss: {}, alarm_snooze: {},
  time_sync: { t: (v) => int(v, 1767225600, 4102444800), tz: (v) => int(v, -720, 840) },
  message: { txt: (v) => typeof v === 'string' && enc.encode(v).byteLength <= MAX_MESSAGE_BYTES && !/[\u0000-\u001f]/.test(v) },
  reaction: {},
};

export function validateArgs(cmd, args = {}) {
  const spec = SPEC[cmd];
  if (!spec) return `unknown command ${cmd}`;
  for (const k of Object.keys(args)) if (!(k in spec)) return `unexpected field ${k}`;
  for (const [k, ok] of Object.entries(spec)) if (!ok(args[k])) return `invalid ${k}`;
  return null;
}

export function encodeCommand(session, seq, cmd, args = {}) {
  const err = validateArgs(cmd, args);
  if (err) throw new RangeError(err);
  if (!int(session, 0, 0xffffffff) || !int(seq, 1, 0xffffffff)) throw new RangeError('bad session/seq');
  const bytes = enc.encode(JSON.stringify({ v: 2, s: session, q: seq, c: cmd, ...args }));
  if (bytes.byteLength > MAX_COMMAND_BYTES) throw new RangeError(`command ${bytes.byteLength} B > ${MAX_COMMAND_BYTES}`);
  return bytes;
}

export function decodeEvent(bytes) {
  const text = typeof bytes === 'string' ? bytes : new TextDecoder('utf-8', { fatal: true }).decode(bytes);
  const o = JSON.parse(text);
  if (o === null || typeof o !== 'object') throw new TypeError('event not an object');
  if ('q' in o && 'ok' in o) return { kind: 'ack', seq: o.q, ok: o.ok === 1, rev: o.r ?? null, error: o.ok === 1 ? null : String(o.e ?? '?') };
  if ('r' in o && 'p' in o) return { kind: 'state', state: parseState(o) };
  throw new TypeError('unrecognised event');
}

export function parseState(o) {
  const [phase, remaining_s, total_s] = o.f;
  const [en, h, m, ringing] = o.a;
  return {
    rev: o.r, partner: o.p, brightness: o.b, sound: o.snd === 1,
    focus: { phase: ['idle', 'running', 'paused', 'done'][phase] ?? 'unknown', remaining_s, total_s },
    alarm: { enabled: en === 1, hour: h, minute: m, ringing: ringing === 1 },
    clock: { trusted: o.clk[0] === 1, syncAgeMin: o.clk[1] },
    power: { usbMv: o.pwr[0], ok: o.pwr[1] === 1 },
    messageBytes: o.msg, firmware: o.fw,
  };
}
