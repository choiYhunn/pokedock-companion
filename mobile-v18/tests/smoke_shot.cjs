// Quick visual check: node smoke_shot.cjs <url> <out.png> [width height] [js-to-run]
const { chromium } = require('playwright');
(async () => {
  const [url, out, w = '390', h = '844', js = ''] = process.argv.slice(2);
  const browser = await chromium.launch({ channel: 'msedge' });
  const ctx = await browser.newContext({ viewport: { width: +w, height: +h }, deviceScaleFactor: 2, hasTouch: true, isMobile: true, locale: 'ko-KR', timezoneId: 'Asia/Seoul' });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (m) => { if (['error', 'warning'].includes(m.type())) errors.push(m.type() + ': ' + m.text()); });
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.waitForTimeout(900);
  if (js) { await page.evaluate(js); await page.waitForTimeout(900); }
  await page.screenshot({ path: out });
  console.log(errors.length ? errors.join('\n') : 'no console errors');
  await browser.close();
})();
