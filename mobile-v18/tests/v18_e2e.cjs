// End-to-end checks for PokéDock Mobile V18 in Chromium (Edge channel) with phone viewports.
// Run: NODE_PATH=<dir containing playwright> node mobile-v18/tests/v18_e2e.cjs <base url> <shots dir>
// Network access to raw.githubusercontent.com is needed for the online parts (sprites / cries).
const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

const BASE = process.argv[2] || 'http://127.0.0.1:8718/mobile-v18/';
const OUT = process.argv[3] || 'shots/v18';
fs.mkdirSync(OUT, { recursive: true });
const IPHONE = { width: 390, height: 844 };
const ANDROID = { width: 412, height: 915 };
const LAND = { width: 844, height: 390 };
const results = [];
let browser;

async function ctxFor(viewport, opts = {}) {
  const ctx = await browser.newContext({ viewport, deviceScaleFactor: 2, hasTouch: true, isMobile: true, locale: 'ko-KR', timezoneId: 'Asia/Seoul', serviceWorkers: opts.sw ? 'allow' : 'block', colorScheme: opts.dark ? 'dark' : 'light', ...opts.ctx });
  const page = await ctx.newPage();
  page.errors = [];
  page.on('pageerror', (e) => page.errors.push('pageerror: ' + e.message));
  page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') page.errors.push(`${m.type()}: ${m.text()}`); });
  if (opts.init) await page.addInitScript(opts.init);
  if (opts.clock) await page.clock.install({ time: opts.clock });
  return { ctx, page };
}
const shot = (page, name) => page.screenshot({ path: path.join(OUT, name + '.png') });
const appState = (page) => page.evaluate(() => JSON.parse(JSON.stringify(window.pokedockApp.state)));
// Only errors caused by our own code count; blocked/aborted remote assets are expected in failure tests.
const ownErrors = (page) => page.errors.filter((e) => !/raw\.githubusercontent|net::ERR|Failed to load resource|Service Worker registration blocked by Playwright/.test(e));

async function test(name, fn) {
  const t0 = Date.now();
  try { await fn(); results.push(['PASS', name, Date.now() - t0]); }
  catch (e) { results.push(['FAIL', name, Date.now() - t0, e.message.split('\n').slice(0, 4).join(' | ')]); }
}

(async () => {
  browser = await chromium.launch({ channel: 'msedge', args: ['--autoplay-policy=no-user-gesture-required'] });

  await test('iPhone portrait home: V17 layout, no wrap, no console errors', async () => {
    const { ctx, page } = await ctxFor(IPHONE);
    await page.goto(BASE, { waitUntil: 'networkidle' });
    await page.waitForTimeout(600);
    const pill = await page.locator('#orientation-button').boundingBox();
    assert.ok(pill.height < 48, `game pill wrapped (h=${pill.height})`);
    for (const id of ['hero-clock', 'focus-clock', 'alarm-next', 'bond-strip', 'today-tile', 'm6-tile', 'easter-entry']) assert.ok(await page.locator('#' + id).isVisible(), id);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    assert.ok(overflow <= 0, `horizontal overflow ${overflow}px`);
    await shot(page, '01_home_iphone');
    await page.evaluate(() => window.scrollTo(0, 600));
    await shot(page, '01b_home_iphone_scrolled');
    assert.equal(ownErrors(page).join(' | '), '');
    await ctx.close();
  });

  await test('V17.1 data migrates into V18 and V17 storage stays intact', async () => {
    const v17 = { character: 393, style: 'pixel', focusMinutes: 45, alarms: [{ id: 'morning', time: '06:50', days: [1, 3], on: true, title: '기상!', sound: 'calm' }], message: '비밀 편지 테스트', quizBest: 4, secretUnlocked: true };
    const { ctx, page } = await ctxFor(IPHONE, { init: `if(!sessionStorage.getItem('seeded')){localStorage.setItem('pokedock-v17-mobile-state', ${JSON.stringify(JSON.stringify(v17))});sessionStorage.setItem('seeded','1')}` });
    await page.goto(BASE, { waitUntil: 'networkidle' });
    await page.waitForTimeout(900);
    assert.match(await page.locator('#toast').innerText(), /V17\.1/);
    assert.equal(await page.locator('#daily-title').innerText(), '팽도리랑 보내는 하루');
    assert.equal(await page.locator('#focus-clock').innerText(), '45:00');
    assert.equal(await page.locator('#alarm-next').innerText(), '06:50');
    const s = await appState(page);
    assert.equal(s.message, '비밀 편지 테스트');
    assert.equal(s.games.silhouette.best['easy-5'], 4);
    assert.equal(await page.evaluate(() => JSON.parse(localStorage.getItem('pokedock-v17-mobile-state')).message), '비밀 편지 테스트');
    await ctx.close();
  });

  await test('focus timer: end-time based, survives reload while running, completes and records stats', async () => {
    const { ctx, page } = await ctxFor(IPHONE, { clock: new Date('2026-10-26T09:00:00+09:00') });
    await page.goto(BASE, { waitUntil: 'networkidle' });
    await page.click('[data-focus="15"]');
    await page.click('#focus-start');
    assert.equal(await page.locator('#focus-start').innerText(), '일시정지');
    await page.clock.fastForward('05:00');
    await page.waitForTimeout(200);
    assert.equal(await page.locator('#focus-clock').innerText(), '10:00');
    // app restarted while the phone was locked for 6 more minutes
    await page.clock.fastForward('06:00');
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(300);
    assert.equal(await page.locator('#focus-clock').innerText(), '04:00');
    await page.click('#focus-start'); // pause
    const pausedAt = await page.locator('#focus-clock').innerText();
    assert.match(pausedAt, /^0[34]:\d\d$/);
    await page.clock.fastForward('10:00');
    assert.equal(await page.locator('#focus-clock').innerText(), pausedAt, 'paused timer does not move');
    await page.click('#focus-start'); // resume
    await page.clock.fastForward('04:05');
    await page.waitForTimeout(300);
    const s = await appState(page);
    assert.equal(s.stats.sessions, 1);
    assert.equal(s.stats.days['2026-10-26'].min, 15);
    assert.ok(s.badges.FOCUS, 'first focus badge');
    assert.match(await page.locator('#focus-caption').innerText(), /15분 · 1세션/);
    await shot(page, '02_focus_done');
    assert.equal(ownErrors(page).join(' | '), '');
    await ctx.close();
  });

  await test('pomodoro 25/5 from the timer sheet, break auto-starts, stats chart', async () => {
    const { ctx, page } = await ctxFor(IPHONE, { clock: new Date('2026-10-26T14:00:00+09:00') });
    await page.goto(BASE, { waitUntil: 'networkidle' });
    await page.click('#focus-more');
    await page.getByRole('button', { name: '포모도로' }).click();
    await shot(page, '03_timer_sheet_pomodoro');
    await page.click('#sheet-close');
    assert.equal(await page.locator('#focus-eyebrow').innerText(), 'FOCUS 1/4');
    await page.click('#focus-start');
    await page.clock.fastForward('25:01');
    await page.waitForTimeout(200);
    assert.equal(await page.locator('#focus-eyebrow').innerText(), 'BREAK TIME');
    assert.equal(await page.locator('#focus-start').innerText(), '일시정지', 'break is running');
    await page.clock.fastForward('05:01');
    await page.waitForTimeout(200);
    assert.equal(await page.locator('#focus-eyebrow').innerText(), 'FOCUS 2/4');
    assert.equal(await page.locator('#focus-start').innerText(), '집중 시작');
    await page.click('#focus-more');
    assert.match(await page.locator('.stat-row').innerText(), /25분/);
    await shot(page, '03b_timer_stats');
    await ctx.close();
  });

  await test('alarms: add, pokemon/snooze/quiet fields, duplicate warning, ring screen, snooze re-rings, dismiss', async () => {
    const { ctx, page } = await ctxFor(IPHONE, { clock: new Date('2026-10-26T06:58:00+09:00') });
    await page.goto(BASE, { waitUntil: 'networkidle' });
    await page.click('#alarm-edit');
    await page.getByRole('button', { name: '＋ 알람 추가' }).click();
    const card = page.locator('.alarm-card').last();
    await card.locator('input[type=time]').fill('07:00');
    await card.locator('input[type=time]').dispatchEvent('change');
    await card.locator('select').first().selectOption('25');
    // turn on the default 07:30 weekday alarm and give the new one the same time → duplicate warning
    const first = page.locator('.alarm-card').first();
    await first.locator('input[type=time]').fill('07:00');
    await first.locator('input[type=time]').dispatchEvent('change');
    await first.locator('input.switch').check();
    assert.match(await page.locator('.setup-problem').first().innerText(), /같은 시각/);
    await first.locator('input.switch').uncheck();
    await shot(page, '04_alarm_sheet');
    await page.click('#sheet-close');
    assert.equal(await page.locator('#alarm-next').innerText(), '07:00');
    await page.clock.fastForward('02:05');
    await page.waitForTimeout(300);
    assert.ok(await page.locator('#ringing').isVisible(), 'ringing screen');
    assert.equal(await page.locator('#ring-title').innerText(), '새 알람');
    await shot(page, '05_ringing');
    await page.click('#ring-snooze');
    assert.ok(!(await page.locator('#ringing').isVisible()));
    await page.clock.fastForward('05:05');
    await page.waitForTimeout(300);
    assert.ok(await page.locator('#ringing').isVisible(), 'snooze rang again');
    await page.click('#ring-dismiss');
    await page.clock.fastForward('03:00');
    assert.ok(!(await page.locator('#ringing').isVisible()), 'no duplicate ring the same day');
    await ctx.close();
  });

  await test('Pokédex: 24 entries, filters, detail, favourite, M6 support labels', async () => {
    const { ctx, page } = await ctxFor(IPHONE);
    await page.goto(BASE, { waitUntil: 'networkidle' });
    await page.click('[data-view="friends"]');
    assert.equal(await page.locator('.dex-card').count(), 24);
    assert.equal(await page.locator('.dex-card.unknown').count(), 16);
    await page.waitForTimeout(700);
    await shot(page, '06_dex');
    await page.getByRole('tab', { name: 'M6 파트너' }).click();
    assert.equal(await page.locator('.dex-card').count(), 8);
    await page.locator('.dex-card').first().click();
    await page.waitForTimeout(700);
    await page.locator('.fav-btn').click();
    assert.ok((await appState(page)).favorites.includes(94));
    await shot(page, '07_dex_detail');
    await ctx.close();
  });

  await test('arcade hub lists 7 games; every game reaches its result screen', async () => {
    const { ctx, page } = await ctxFor(IPHONE, { init: 'delete Navigator.prototype.canShare; delete Navigator.prototype.share;' });
    await page.goto(BASE, { waitUntil: 'networkidle' });
    await page.click('#orientation-button');
    await page.click('#arcade-open');
    assert.equal(await page.locator('.game-card').count(), 7);
    await page.waitForTimeout(800);
    await shot(page, '08_arcade_hub');

    // 1 cry quiz (real cries over the network)
    await page.getByRole('button', { name: '울음소리 퀴즈 열기' }).click();
    await shot(page, '09_cry_setup');
    await page.click('.setup-start');
    await page.waitForTimeout(1200);
    await shot(page, '09b_cry_play');
    for (let i = 0; i < 5; i++) {
      await page.locator('.choice:not([disabled])').first().click({ timeout: 8000 });
      await page.waitForTimeout(1400);
    }
    await page.locator('.game-result').waitFor({ timeout: 5000 });
    await shot(page, '09c_cry_result');
    const cryState = await appState(page);
    assert.ok(cryState.games.cry.plays >= 1);
    await page.getByRole('button', { name: '다른 게임' }).click();

    // 2 balance
    await page.getByRole('button', { name: '밸런스 게임 열기' }).click();
    await page.click('.setup-start');
    await page.waitForTimeout(600);
    await shot(page, '10_balance');
    for (let i = 0; i < 5; i++) { await page.locator('.balance-card').first().click(); await page.waitForTimeout(1600); }
    await page.locator('.game-result').waitFor();
    await page.getByRole('button', { name: '결과 카드 만들기' }).click();
    await page.locator('.share-preview img').waitFor({ timeout: 8000 });
    await shot(page, '10b_balance_result');
    assert.equal((await appState(page)).balance.length, 5);
    await page.getByRole('button', { name: '다른 게임' }).click();

    // 3 silhouette (5 questions, easy)
    await page.getByRole('button', { name: '실루엣 퀴즈 열기' }).click();
    await page.locator('.seg-group').nth(1).getByRole('radio', { name: '쉬움' }).click();
    await page.locator('.seg-group').nth(2).getByRole('radio', { name: '5' }).click();
    await page.click('.setup-start');
    await page.waitForTimeout(800);
    await shot(page, '11_silhouette');
    for (let i = 0; i < 5; i++) { await page.locator('.choice:not([disabled])').first().click(); await page.waitForTimeout(1150); }
    await page.locator('.game-result').waitFor();
    await page.getByRole('button', { name: '다른 게임' }).click();

    // 4 memory: solve using the card faces
    await page.getByRole('button', { name: '카드 짝맞추기 열기' }).click();
    await page.click('.setup-start');
    const names = await page.locator('.mem-front small').allInnerTexts();
    const byName = {};
    names.forEach((n, i) => (byName[n] ||= []).push(i));
    let firstMove = true;
    for (const idx of Object.values(byName)) {
      await page.locator('.mem-card').nth(idx[0]).click();
      if (firstMove) { await page.waitForTimeout(450); await shot(page, '12_memory'); firstMove = false; }
      await page.locator('.mem-card').nth(idx[1]).click();
      await page.waitForTimeout(120);
    }
    await page.locator('.game-result').waitFor();
    assert.match(await page.locator('.result-score').innerText(), /6번 만에/);
    await page.getByRole('button', { name: '다른 게임' }).click();

    // 6 reaction: false start then 3 clean rounds
    await page.getByRole('button', { name: '반응속도 열기' }).click();
    await page.locator('.seg-group').first().getByRole('radio', { name: '3번' }).click();
    await page.click('.setup-start');
    const stage = page.locator('.rx-stage');
    await stage.dispatchEvent('pointerdown');
    await page.waitForTimeout(300);
    await stage.dispatchEvent('pointerdown'); // too early
    assert.match(await stage.innerText(), /부정 출발/);
    for (let r = 0; r < 3; r++) {
      await stage.dispatchEvent('pointerdown');
      await page.locator('.rx-stage.go').waitFor({ timeout: 6000 });
      await page.waitForTimeout(180);
      await stage.dispatchEvent('pointerdown');
      await page.waitForTimeout(150);
    }
    await page.locator('.game-result').waitFor();
    await shot(page, '13_reaction_result');
    await page.getByRole('button', { name: '다른 게임' }).click();

    // 7 daily
    await page.getByRole('button', { name: '오늘의 포켓몬 열기' }).click();
    await page.click('.setup-start');
    await page.click('.daily-reveal');
    await page.locator('.daily-section .choice').first().click();
    const d = Object.values((await appState(page)).daily)[0];
    assert.ok(d.revealed && d.answered != null);
    assert.equal(await page.locator('.daily-section .choice:not([disabled])').count(), 0, 'one answer per day');
    await shot(page, '14_daily');
    assert.equal(ownErrors(page).join(' | '), '');
    await ctx.close();
  });

  await test('Gengar run (landscape): plays at speed, pause/resume, game over', async () => {
    const { ctx, page } = await ctxFor(LAND);
    await page.goto(BASE + '#runner', { waitUntil: 'networkidle' });
    await page.click('#orientation-button');
    await shot(page, '15_partner_room_landscape');
    await page.click('#arcade-open');
    await page.getByRole('button', { name: '팬텀 런 열기' }).click();
    await page.click('.setup-start');
    const box = await page.locator('.runner-canvas').boundingBox();
    await page.mouse.move(box.x + 100, box.y + box.height / 2);
    await page.mouse.down();
    const fps = await page.evaluate(() => new Promise((res) => { let n = 0; const t0 = performance.now(); const f = () => { n++; if (performance.now() - t0 < 2000) requestAnimationFrame(f); else res(n / 2); }; requestAnimationFrame(f); }));
    for (let i = 0; i < 6; i++) { await page.mouse.move(box.x + 100, box.y + (i % 2 ? 40 : box.height - 40), { steps: 8 }); await page.waitForTimeout(250); }
    await shot(page, '16_runner_play');
    await page.mouse.up();
    await page.click('#arcade-pause');
    assert.ok(await page.locator('.pause-layer').isVisible());
    await shot(page, '16b_runner_paused');
    await page.getByRole('button', { name: '계속하기' }).click();
    await page.locator('.game-result').waitFor({ timeout: 90000 }); // drifts into orbs eventually
    await shot(page, '17_runner_result');
    const best = (await appState(page)).games.runner.best.normal;
    assert.ok(best > 0, 'score recorded');
    console.log(`  runner rAF ≈ ${fps} fps (headless Edge, desktop CPU)`);
    if (page.metrics) { /* not available */ }
    const heap = await page.evaluate(() => performance.memory ? Math.round(performance.memory.usedJSHeapSize / 1048576) : null);
    console.log(`  JS heap after runner: ${heap} MB`);
    assert.equal(ownErrors(page).join(' | '), '');
    await ctx.close();
  });

  await test('M6 mock link is labelled as a simulation and syncs partner/alarm/brightness', async () => {
    const { ctx, page } = await ctxFor(IPHONE);
    await page.goto(BASE + '?m6=mock', { waitUntil: 'networkidle' });
    await page.click('#m6-tile');
    await page.getByRole('button', { name: '마스터볼 찾기' }).click();
    await page.locator('.m6-state').waitFor({ timeout: 8000 });
    assert.equal(await page.locator('#m6-title').innerText(), '모의 연결 (테스트)');
    assert.ok(!(await page.locator('.m6-head b').innerText()).includes('연결됨'));
    assert.match(await page.locator('.m6-sheet').innerText(), /실제 마스터볼과 연결된 것이 아니에요/);
    await page.getByRole('button', { name: '시간 동기화' }).click();
    await page.waitForTimeout(400);
    await shot(page, '18_m6_mock');
    const st = await page.evaluate(() => window.pokedockApp.m6.deviceState);
    assert.equal(st.partner, 94);
    assert.equal(st.clock.trusted, true);
    await ctx.close();
  });

  await test('M6 unsupported browser (iPhone Safari-like) explains instead of pretending', async () => {
    const { ctx, page } = await ctxFor(IPHONE, { init: 'Object.defineProperty(navigator, "bluetooth", {get: () => undefined}); Object.defineProperty(navigator, "userAgent", {get: () => "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1"});' });
    await page.goto(BASE, { waitUntil: 'networkidle' });
    assert.equal(await page.locator('#m6-title').innerText(), '이 기기에서 연결 불가');
    await page.click('#m6-tile');
    assert.match(await page.locator('.m6-sheet').innerText(), /iPhone Safari는 Web Bluetooth를 지원하지 않아요/);
    assert.equal(await page.getByRole('button', { name: '마스터볼 찾기' }).count(), 0);
    await shot(page, '19_m6_unsupported');
    await ctx.close();
  });

  await test('remote images and cries blocked: app still works, games skip honestly', async () => {
    const { ctx, page } = await ctxFor(IPHONE);
    await ctx.route('https://raw.githubusercontent.com/**', (r) => r.abort());
    await page.goto(BASE, { waitUntil: 'load' });
    await page.waitForTimeout(600);
    await page.click('[data-view="friends"]');
    await page.waitForTimeout(400);
    assert.ok(await page.locator('.poke-placeholder').count() > 0, 'placeholders shown');
    await shot(page, '20_images_blocked_dex');
    await page.click('#sheet-close');
    await page.click('#today-tile');
    await page.click('#arcade-back');
    await page.getByRole('button', { name: '울음소리 퀴즈 열기' }).click();
    await page.click('.setup-start');
    await page.locator('text=울음소리를 불러오지 못했어요').first().waitFor({ timeout: 6000 });
    await page.getByRole('button', { name: '이 문제 건너뛰기' }).click();
    await shot(page, '21_cry_blocked');
    assert.equal(ownErrors(page).join(' | '), '');
    await ctx.close();
  });

  await test('offline: service worker caches shell + 48 sprites, app and images work with network off', async () => {
    const { ctx, page } = await ctxFor(IPHONE, { sw: true });
    await page.goto(BASE, { waitUntil: 'networkidle' });
    await page.waitForFunction(() => window.pokedockOffline?.status.sprites.done === 48 && window.pokedockOffline.status.shell.ready, null, { timeout: 60000 });
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(500);
    assert.match(await page.locator('#offline-badge').innerText(), /오프라인|✓/);
    await ctx.setOffline(true);
    await page.reload({ waitUntil: 'load' });
    await page.waitForTimeout(800);
    const heroOk = await page.evaluate(() => document.getElementById('hero-pokemon').naturalWidth > 0);
    assert.ok(heroOk, 'hero image from cache');
    await page.click('#orientation-button');
    await page.click('#arcade-open');
    await page.getByRole('button', { name: '카드 짝맞추기 열기' }).click();
    await page.click('.setup-start');
    await page.locator('.mem-card').first().click();
    await page.waitForTimeout(500);
    const imgs = await page.evaluate(() => [...document.querySelectorAll('.mem-img')].filter((i) => i.naturalWidth > 0).length);
    assert.ok(imgs >= 10, `cached memory images ${imgs}`);
    await shot(page, '22_offline_memory');
    for (let i = 0; i < 6 && await page.locator('#arcade').isVisible(); i++) await page.click('#arcade-back');
    await page.click('#settings-button');
    await page.getByRole('button', { name: '오프라인 콘텐츠 관리 →' }).click();
    await page.waitForTimeout(400);
    await shot(page, '23_offline_sheet');
    assert.equal(ownErrors(page).join(' | '), '');
    await ctx.close();
  });

  await test('native Android bridge (recorded LocalNotifications): weekly ids, weekday mapping, channels, quiet, timer end', async () => {
    const init = `window.__calls = [];
      const rec = (name, ret) => (arg) => { window.__calls.push([name, JSON.parse(JSON.stringify(arg ?? null))]); return Promise.resolve(ret); };
      window.Capacitor = { isNativePlatform: () => true, getPlatform: () => 'android', isPluginAvailable: (n) => n === 'LocalNotifications',
        Plugins: { LocalNotifications: { checkPermissions: rec('check', { display: 'granted' }), requestPermissions: rec('request', { display: 'granted' }),
          cancel: rec('cancel'), schedule: rec('schedule'), createChannel: rec('channel'), registerActionTypes: rec('actions'),
          addListener: rec('listen', { remove() {} }), checkExactNotificationSetting: rec('exact', { exact_alarm: 'granted' }) } } };`;
    const { ctx, page } = await ctxFor(IPHONE, { init });
    await page.goto(BASE, { waitUntil: 'networkidle' });
    await page.click('#alarm-edit');
    const first = page.locator('.alarm-card').first();      // 07:30 Mon–Fri
    await first.locator('input.switch').check();
    const third = page.locator('.alarm-card').nth(2);       // 22:20 daily, quiet by default
    await third.locator('input.switch').check();
    await page.getByRole('button', { name: /기기에 (알람 )?적용/ }).click();
    await page.waitForTimeout(400);
    const calls = await page.evaluate(() => window.__calls);
    const sched = calls.filter((c) => c[0] === 'schedule').pop()[1].notifications;
    assert.equal(sched.length, 5 + 7);
    const mon = sched.find((n) => n.id === 10000 + 1);
    assert.deepEqual(mon.schedule.on, { weekday: 2, hour: 7, minute: 30, second: 0 }, 'Capacitor weekday 1=Sunday');
    assert.equal(mon.channelId, 'pokedock_alarm_dawn_v1');
    assert.equal(mon.actionTypeId, 'POKEDOCK_ALARM');
    const quiet = sched.find((n) => n.id === 10000 + 2 * 20 + 0);
    assert.equal(quiet.channelId, 'pokedock_alarm_quiet_v1');
    assert.equal(quiet.sound, undefined);
    assert.ok(calls.some((c) => c[0] === 'channel' && c[1].id === 'pokedock_alarm_quiet_v1' && c[1].importance === 2));
    const cancelled = calls.find((c) => c[0] === 'cancel')[1].notifications.map((n) => n.id);
    assert.ok(cancelled.includes(10000 + 7 * 20 + 6) && cancelled.includes(19007), 'old weekly + snooze ids cleared first');
    await page.click('#sheet-close');
    await page.click('#focus-start');
    await page.waitForTimeout(200);
    const timerN = (await page.evaluate(() => window.__calls)).filter((c) => c[0] === 'schedule').pop()[1].notifications[0];
    assert.equal(timerN.id, 20001);
    assert.ok(Date.parse(timerN.schedule.at) > Date.now() + 24 * 60000);
    await ctx.close();
  });

  await test('V17.1 and V18 coexist on one origin: V18 never deletes V17 caches or storage', async () => {
    const { ctx, page } = await ctxFor(IPHONE, { sw: true });
    const v17 = BASE.replace('mobile-v18', 'mobile-v17');
    await page.goto(v17, { waitUntil: 'networkidle' });
    await page.waitForFunction(() => window.pokedockOfflineReady === true, null, { timeout: 60000 });
    await page.click('[data-focus="45"]');
    await page.goto(BASE, { waitUntil: 'networkidle' });
    await page.waitForFunction(() => window.pokedockOffline?.status.sprites.done === 48, null, { timeout: 60000 });
    const keys = await page.evaluate(() => caches.keys());
    assert.ok(keys.some((k) => k.startsWith('pokedock-v17')), 'V17 caches kept: ' + keys.join(','));
    assert.ok(keys.some((k) => k.startsWith('pokedock-v18-shell-')));
    await page.goto(v17, { waitUntil: 'networkidle' });
    assert.equal(await page.locator('#focus-clock').innerText(), '45:00', 'V17 still has its own state');
    assert.deepEqual(page.errors.filter((e) => !/Failed to load resource/.test(e)), []);
    await ctx.close();
  });

  await test('Android size, dark system theme and large text keep the layout intact', async () => {
    const { ctx, page } = await ctxFor(ANDROID, { dark: true });
    await page.goto(BASE, { waitUntil: 'networkidle' });
    await page.click('#settings-button');
    await page.locator('label.sheet-row', { hasText: '글자 크게' }).locator('input').check();
    await page.click('#sheet-close');
    await page.waitForTimeout(400);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    assert.ok(overflow <= 0, `overflow ${overflow}`);
    const bg = await page.evaluate(() => getComputedStyle(document.querySelector('.app-shell')).backgroundColor);
    assert.equal(bg, 'rgb(250, 248, 246)', 'stays on the light V17 palette in dark mode');
    await shot(page, '24_android_dark_largetext');
    await ctx.close();
  });

  await test('partner room landscape + arcade landscape layout', async () => {
    const { ctx, page } = await ctxFor(LAND);
    await page.goto(BASE, { waitUntil: 'networkidle' });
    await page.click('#orientation-button');
    await page.locator('[data-motion="sleep"]').click();
    await page.waitForTimeout(500);
    await shot(page, '25_partner_room_sleep');
    await page.click('#arcade-open');
    await page.waitForTimeout(800);
    await shot(page, '26_arcade_landscape');
    await ctx.close();
  });

  await browser.close();
  for (const r of results) console.log(`${r[0]}  ${r[1]}  (${r[2]} ms)${r[3] ? '\n      ' + r[3] : ''}`);
  const failed = results.filter((r) => r[0] === 'FAIL').length;
  console.log(`${failed ? 'FAIL' : 'PASS'}: ${results.length - failed}/${results.length} e2e checks`);
  process.exit(failed ? 1 : 0);
})();
