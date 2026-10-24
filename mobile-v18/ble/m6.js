// App-side manager for the M6 Master Ball link. Owns the PokeDockClient, reports an honest status
// (never "connected" for the test simulation) and maps device error codes to readable Korean.
import { PokeDockClient } from './pokedock_ble_client.mjs';
import { PARTNERS, MAX_MESSAGE_BYTES } from './pokedock_ble_protocol.mjs';
import { CapacitorBleTransport, MockTransport, WebBluetoothTransport } from './transports.js';

export const M6_PARTNERS = PARTNERS;
export { MAX_MESSAGE_BYTES };

const ERRORS = {
  auth: '본딩(페어링)이 필요해요. 볼 화면의 6자리 번호로 페어링해 주세요.',
  range: '기기가 받아들일 수 없는 값이에요.',
  busy: '마스터볼에서 이미 집중 타이머가 돌고 있어요.',
  state: '지금 마스터볼 상태에서는 할 수 없는 동작이에요.',
  ver: '마스터볼 펌웨어 프로토콜 버전이 달라요.',
  args: '명령 형식이 맞지 않아요.', json: '명령 형식이 맞지 않아요.', size: '명령이 너무 길어요.', seq: '명령 번호 오류예요.',
  unknown: '이 펌웨어가 모르는 명령이에요.', rtc: '마스터볼 시계를 저장하지 못했어요.',
};
export function describeError(e) {
  if (!e) return '';
  if (e.code && ERRORS[e.code]) return ERRORS[e.code];
  const m = String(e.message || e);
  if (/ack timeout/.test(m)) return '마스터볼이 응답하지 않아요. 가까이에서 다시 시도해 주세요.';
  if (/unreachable/.test(m)) return '마스터볼을 찾을 수 없어요. 전원과 거리를 확인해 주세요.';
  if (/MTU/.test(m)) return '휴대폰이 충분한 BLE 패킷 크기를 허용하지 않았어요.';
  if (/cancel|chooser|NotFoundError/i.test(m)) return '기기 선택이 취소됐어요.';
  if (/NetworkError|GATT|connect/i.test(m)) return '연결이 끊겼어요. 다시 연결해 주세요.';
  return m.slice(0, 90);
}

export function detectSupport(search = typeof location !== 'undefined' ? location.search : '') {
  if (/[?&]m6=mock\b/.test(search)) return { kind: 'mock', ok: true, label: '모의 연결 (테스트 전용)' };
  if (CapacitorBleTransport.supported()) return { kind: 'native', ok: true, label: '네이티브 앱 BLE' };
  if (WebBluetoothTransport.supported()) return { kind: 'web', ok: true, label: '브라우저 Web Bluetooth (실험적)' };
  const ios = typeof navigator !== 'undefined' && /iPhone|iPad|iPod/.test(navigator.userAgent);
  return {
    kind: 'none', ok: false,
    label: ios ? 'iPhone Safari는 Web Bluetooth를 지원하지 않아요. 네이티브 iOS 앱이 필요해요.'
      : '이 브라우저는 Bluetooth 연결을 지원하지 않아요. Android Chrome이나 네이티브 앱에서 연결할 수 있어요.',
  };
}

export class M6Link {
  constructor({ search, onChange = () => {}, log = () => {} } = {}) {
    this.support = detectSupport(search);
    this.status = this.support.ok ? 'idle' : 'unsupported';
    this.onChange = onChange;
    this.logFn = log;
    this.client = null;
    this.deviceState = null;
    this.lastError = '';
    this.history = [];
  }
  get mock() { return this.support.kind === 'mock'; }
  get connected() { return this.status === 'connected'; }

  #set(status, error = '') {
    this.status = status;
    if (error) this.lastError = error;
    this.onChange(this);
  }
  #note(ok, text) {
    this.history.unshift({ at: Date.now(), ok, text });
    this.history.length = Math.min(this.history.length, 12);
  }

  #transport() {
    const k = this.support.kind;
    const t = k === 'mock' ? new MockTransport() : k === 'native' ? new CapacitorBleTransport() : new WebBluetoothTransport();
    // Wrap to learn about link loss, which PokeDockClient handles internally.
    return {
      connect: (onEvent, onDisconnect) => t.connect(onEvent, () => {
        onDisconnect();
        if (this.status === 'connected') { this.#note(false, '연결이 끊겼어요'); this.#set('lost'); }
      }),
      write: (u8) => t.write(u8), read: () => t.read(), disconnect: () => t.disconnect(),
      get name() { return t.name; },
    };
  }

  async connect() {
    if (!this.support.ok) throw new Error(this.support.label);
    if (this.status === 'connecting') return;
    this.#set('connecting');
    try {
      if (!this.client) {
        this.transport = this.#transport();
        this.client = new PokeDockClient(this.transport, { log: this.logFn });
        this.client.onState((s) => { this.deviceState = s; this.onChange(this); });
      }
      await this.client.connect(); // re-reads state and auto-syncs an untrusted / stale clock
      this.lastError = '';
      this.#note(true, '연결됨 · 상태 읽기 완료');
      this.#set('connected');
      return this.deviceState;
    } catch (e) {
      const msg = describeError(e);
      this.#note(false, '연결 실패: ' + msg);
      this.#set(this.client?.connected ? 'connected' : 'error', msg);
      throw e;
    }
  }

  async disconnect() {
    try { await this.client?.disconnect(); } finally { this.#note(true, '연결 해제'); this.#set(this.support.ok ? 'idle' : 'unsupported'); }
  }

  // Run one command; resolves {ok, text}. Never throws, so UI buttons can show the outcome.
  async run(label, fn) {
    if (!this.client || (!this.client.connected && this.status !== 'lost')) return { ok: false, text: '마스터볼이 연결되어 있지 않아요.' };
    try {
      await fn(this.client);
      if (this.status !== 'connected') this.#set('connected');
      this.#note(true, label + ' 완료');
      this.onChange(this);
      return { ok: true, text: label + ' 완료' };
    } catch (e) {
      const text = `${label} 실패 · ${describeError(e)}`;
      this.#note(false, text);
      this.lastError = describeError(e);
      if (this.client && !this.client.connected) this.#set('lost');
      else this.onChange(this);
      return { ok: false, text };
    }
  }

  syncClock() { return this.run('시간 동기화', (c) => c.syncClock()); }
  setPartner(id) {
    if (!PARTNERS.includes(id)) return Promise.resolve({ ok: false, text: '마스터볼은 파트너 8종만 표시할 수 있어요.' });
    return this.run('파트너 변경', (c) => c.setPartner(id));
  }
  setBrightness(v) { return this.run('밝기 변경', (c) => c.setBrightness(Math.max(1, Math.min(100, Math.round(v))))); }
  setSound(on) { return this.run(on ? '소리 켜기' : '소리 끄기', (c) => c.setSound(on)); }
  setAlarm(p) { return this.run(p.en ? `알람 ${String(p.h).padStart(2, '0')}:${String(p.m).padStart(2, '0')} 전송` : '알람 끄기 전송', (c) => c.setAlarm(p.h, p.m, p.en)); }
  focus(action, minutes) {
    const map = {
      start: ['집중 시작', (c) => c.focusStart(Math.max(1, Math.min(120, minutes)))],
      pause: ['집중 일시정지', (c) => c.focusPause()], resume: ['집중 재개', (c) => c.focusResume()], cancel: ['집중 초기화', (c) => c.focusCancel()],
    };
    const [label, fn] = map[action];
    return this.run(label, fn);
  }
  sendMessage(txt) { return this.run('메시지 전송', (c) => c.setMessage(txt)); }
  reaction() { return this.run('반응 보내기', (c) => c.send('reaction')); }
  refresh() { return this.run('상태 새로고침', (c) => c.refresh()); }
}

export const utf8Bytes = (s) => new TextEncoder().encode(s).byteLength;
