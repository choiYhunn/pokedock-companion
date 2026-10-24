// Captures the V17.1 reference screens that V18 must not regress against.
// Run: NODE_PATH=<dir with playwright> node mobile-v18/tests/baseline_v17.cjs <v17 url> <out dir>
const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');

const [url = 'https://choiyhunn.github.io/pokedock-companion/mobile-v17/', out = 'shots/v17'] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });

(async () => {
  const browser = await chromium.launch({ channel: 'msedge' });
  const shot = async (name, viewport, act) => {
    const ctx = await browser.newContext({ viewport, deviceScaleFactor: 2, hasTouch: true, isMobile: true, locale: 'ko-KR', timezoneId: 'Asia/Seoul' });
    const page = await ctx.newPage();
    await page.goto(url, { waitUntil: 'networkidle' });
    await page.waitForTimeout(800);
    if (act) await act(page);
    await page.waitForTimeout(700);
    await page.screenshot({ path: path.join(out, name + '.png') });
    await ctx.close();
  };
  const portrait = { width: 390, height: 844 };
  const landscape = { width: 844, height: 390 };
  await shot('01_home_portrait', portrait);
  await shot('02_alarm_sheet', portrait, (p) => p.click('#alarm-edit'));
  await shot('03_friends_sheet', portrait, (p) => p.click('#open-partners'));
  await shot('04_game_landscape', landscape, (p) => p.click('#orientation-button'));
  await shot('05_quiz', landscape, async (p) => { await p.click('#orientation-button'); await p.click('#quiz-open'); });
  await browser.close();
  console.log('saved V17 baseline to', out);
})();
