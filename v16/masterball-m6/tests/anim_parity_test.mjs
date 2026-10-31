// The simulator's JS mirror (ui/m6_anim.js) must match core/anim_director.hpp exactly.
// usage: node tests/anim_parity_test.mjs <path to anim_dump executable>
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const A = require('../ui/m6_anim.js');
const out = execFileSync(process.argv[2], { maxBuffer: 1 << 28 }).toString().trim().split('\n');
let n = 0, bad = 0;
for (const line of out) {
  const f = line.trim().split(' ');
  const v = f.slice(1).map(Number);
  let got, want;
  if (f[0] === 'P') {
    const [a, d, t] = v;
    const p = A.poseFor(a, t, d);
    got = [p.dx, p.dy, p.zoom, p.overlay, p.overlayDy, p.overlayOpa];
    want = v.slice(3);
  } else {
    const [a, d, t, st, w, h] = v;
    const r = A.place(st, w, h, A.poseFor(a, t, d));
    got = [r.x, r.y, r.w, r.h, r.zoom];
    want = v.slice(6);
  }
  n++;
  if (got.join() !== want.join()) { if (bad++ < 5) console.log('MISMATCH', line, '-> js', got.join(' ')); }
}
console.log(`${bad ? 'FAIL' : 'PASS'}: ${n - bad}/${n} samples identical (C++ vs JS)`);
process.exit(bad ? 1 : 0);
