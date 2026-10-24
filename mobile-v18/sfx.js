// Tiny original sound effects synthesised with Web Audio (no audio files). Respects the app's
// sound setting; silently does nothing when audio is unavailable or still locked by the browser.
let ctx = null;
let enabled = true;

export function setSoundEnabled(on) { enabled = !!on; }
export function soundEnabled() { return enabled; }

function audio() {
  if (!enabled) return null;
  try {
    ctx ??= new (window.AudioContext || window.webkitAudioContext)();
    if (ctx.state === 'suspended') ctx.resume().catch(() => {});
    return ctx;
  } catch { return null; }
}
// Call from a user gesture so iOS unlocks audio for later automatic effects.
export function unlockAudio() { audio(); }

const NOTES = {
  correct: [[660, 0, 0.09], [880, 0.09, 0.14]],
  wrong: [[300, 0, 0.12], [220, 0.11, 0.18]],
  flip: [[520, 0, 0.05]],
  match: [[700, 0, 0.07], [940, 0.07, 0.07], [1180, 0.14, 0.12]],
  collect: [[880, 0, 0.05], [1320, 0.05, 0.08]],
  berry: [[740, 0, 0.06], [990, 0.06, 0.06], [1240, 0.12, 0.1]],
  hit: [[180, 0, 0.18]],
  start: [[523, 0, 0.08], [659, 0.08, 0.08], [784, 0.16, 0.14]],
  go: [[988, 0, 0.12]],
  tick: [[1200, 0, 0.03]],
  stamp: [[392, 0, 0.08], [523, 0.08, 0.08], [784, 0.16, 0.2]],
};

export function sfx(name, volume = 0.07) {
  const ac = audio();
  if (!ac || !NOTES[name]) return;
  const t0 = ac.currentTime + 0.01;
  for (const [freq, at, dur] of NOTES[name]) {
    const o = ac.createOscillator();
    const g = ac.createGain();
    o.type = name === 'hit' || name === 'wrong' ? 'triangle' : 'square';
    o.frequency.setValueAtTime(freq, t0 + at);
    g.gain.setValueAtTime(0.0001, t0 + at);
    g.gain.exponentialRampToValueAtTime(volume, t0 + at + 0.01);
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + at + dur);
    o.connect(g).connect(ac.destination);
    o.start(t0 + at);
    o.stop(t0 + at + dur + 0.02);
  }
}
