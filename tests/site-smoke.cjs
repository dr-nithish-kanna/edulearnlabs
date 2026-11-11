// Site smoke test: a family's path through the built site, on the throttled profile.
// Run: npm run build && npm run test:e2e   (needs Playwright with Chromium)
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');

const DIST = path.join(__dirname, '..', 'dist');
const BASE = '/edulearnlabs/';
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.woff2': 'font/woff2', '.json': 'application/json',
  '.svg': 'image/svg+xml', '.webp': 'image/webp', '.png': 'image/png', '.xml': 'application/xml', '.txt': 'text/plain' };
const server = http.createServer((req, res) => {
  let u = decodeURIComponent(req.url.split('?')[0]);
  if (!u.startsWith(BASE)) { res.writeHead(404); return res.end(); }
  let f = path.join(DIST, u.slice(BASE.length));
  if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, 'index.html');
  if (!f.startsWith(DIST) || !fs.existsSync(f)) { res.writeHead(404, { 'content-type': 'text/html' }); return res.end(fs.readFileSync(path.join(DIST, '404.html'))); }
  res.writeHead(200, { 'content-type': TYPES[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
});
let failures = 0;
// Screenshots only when SHOTS=<folder> is set, for a human to look at.
const shot = (page, name, fullPage = false) => process.env.SHOTS ? page.screenshot({ path: `${process.env.SHOTS}/${name}.png`, fullPage }) : null;
const check = (ok, msg) => { console.log(`${ok ? 'ok  ' : 'FAIL'} ${msg}`); if (!ok) failures++; };

async function playFullGame(page) {
  const game = page.frameLocator('.overlay iframe');
  await game.locator('.ell-start .ell-btn').click({ force: true, timeout: 15000 });
  for (let n = 0; n < 20; n++) {
    if (await game.locator('.ell-end').isVisible()) break;
    await game.locator('.ell-choice:not([disabled])').first().waitFor({ timeout: 15000 });
    const [a, , b] = (await game.locator('.ell-prompt').textContent()).split(' ');
    await game.locator(`.ell-choice:text-is("${+a + +b}")`).click();
    await page.waitForFunction(() => {
      const d = document.querySelector('.overlay iframe')?.contentDocument;
      return d && (d.querySelector('.ell-end:not([hidden])') || [...d.querySelectorAll('.ell-choice')].every(x => !x.disabled));
    }, null, { timeout: 15000 });
  }
  await game.locator('.ell-end').waitFor({ state: 'visible' });
  return game;
}

(async () => {
  await new Promise(r => server.listen(0, r));
  const origin = `http://localhost:${server.address().port}`;
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await page.addInitScript(() => {
    window.__cls = 0;
    new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; })
      .observe({ type: 'layout-shift', buffered: true });
    new PerformanceObserver(l => { const e = l.getEntries().at(-1); window.__lcp = e.startTime; }).observe({ type: 'largest-contentful-paint', buffered: true });
  });

  const cdp = await ctx.newCDPSession(page);
  await cdp.send('Network.enable');
  await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 150, downloadThroughput: 200000, uploadThroughput: 93750 });
  await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });

  // Every page: one H1, a title, a description, no layout shift.
  for (const p of ['', 'math-games/', 'math-games/addition-for-grade-1/', 'grown-ups/', 'privacy/']) {
    const t0 = Date.now();
    await page.goto(origin + BASE + p, { waitUntil: 'load' });
    const loadMs = Date.now() - t0;
    await page.waitForTimeout(600);
    const info = await page.evaluate(() => ({
      h1: document.querySelectorAll('h1').length, title: document.title,
      desc: document.querySelector('meta[name=description]')?.content ?? '', cls: window.__cls, lcp: window.__lcp,
    }));
    check(info.h1 === 1 && info.title && info.desc.length > 50, `/${p}: one H1, title, description`);
    check(info.cls === 0, `/${p}: layout shift ${info.cls.toFixed(3)} (target 0)`);
    check(loadMs < 5000, `/${p}: loaded in ${loadMs} ms throttled, LCP ${Math.round(info.lcp)} ms`);
  }
  const before = errors.length;
  await page.goto(origin + BASE + 'nope/');
  check((await page.locator('h1').textContent()).includes('flew away'), '404 page shows');
  errors.splice(before); // the 404 status itself is expected here
  await cdp.send('Emulation.setCPUThrottlingRate', { rate: 1 });
  await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });

  // Click 1: home to game page. Click 2: Play.
  await page.goto(origin + BASE);
  await shot(page, 'site-home');
  await page.getByRole('link', { name: /Play Addition Garden/ }).click();
  await page.waitForURL(/addition-for-grade-1/);
  await page.waitForTimeout(2500); // let the idle prefetch run
  const prefetched = await page.evaluate(() => document.querySelectorAll('link[rel=prefetch]').length);
  check(prefetched >= 3, `game files prefetched while reading (${prefetched} links)`);
  await shot(page, 'site-game-page');
  await page.locator('[data-play]').click({ force: true });
  check(await page.locator('.overlay iframe').isVisible(), 'Play opens the game full screen (2 clicks from home)');
  const game = await playFullGame(page);
  await shot(page, 'site-playing-end');
  await game.locator('.ell-end .ell-btn--plain').click(); // Back
  await page.locator('.overlay').waitFor({ state: 'hidden' });
  check(true, 'game Back closes the overlay');

  const store = await page.evaluate(() => JSON.parse(localStorage.getItem('ell:v1')));
  const profiles = Object.values(store.profiles);
  check(profiles.length === 1, 'first play created exactly one profile');
  check(store.sessions.length === 1 && store.sessions[0].profile === profiles[0].id && store.sessions[0].completed, 'session saved under that profile');
  check(store.sessions[0].firstTry === 10, 'all 10 answered right first try');
  const row = await page.locator('[data-progress]').textContent();
  check(/Sprout|Bud/.test(row) && row.includes('★★★'), `progress shows on the page: "${row.replace(/\s+/g, ' ').trim()}"`);
  await shot(page, 'site-after-play');

  // Second game starts one level below where the first ended.
  const expected = Math.max(1, store.sessions[0].levelEnd - 1);
  await page.locator('[data-play]').click({ force: true });
  await playFullGame(page);
  await page.frameLocator('.overlay iframe').locator('.ell-end .ell-btn--plain').click();
  const s2 = await page.evaluate(() => JSON.parse(localStorage.getItem('ell:v1')).sessions[1]);
  check(s2.levelStart === expected, `second game started at level ${s2.levelStart} (expected ${expected})`);

  // A sibling joins: Grown-ups adds a player, then Play asks who is playing.
  await page.goto(origin + BASE + 'grown-ups/');
  await page.getByRole('button', { name: '+ Add a player' }).click();
  check(await page.locator('.profile-row').count() === 2, 'Grown-ups shows 2 players');
  await shot(page, 'site-grown-ups', true);
  await page.goto(origin + BASE + 'math-games/addition-for-grade-1/');
  await page.locator('[data-play]').click({ force: true });
  check(await page.locator('#player-picker').isVisible(), '"Who\'s playing?" appears with 2 players');
  await shot(page, 'site-picker');
  await page.locator('#player-picker .pick').nth(1).click();
  check(await page.locator('.overlay iframe').isVisible(), 'picking a player starts the game');

  check(errors.length === 0, `no console errors${errors.length ? ': ' + errors.join(' | ') : ''}`);
  console.log(failures ? `\n${failures} check(s) failed` : '\nPASS');
  await browser.close(); server.close();
  process.exitCode = failures ? 1 : 0;
})().catch(e => { console.error('FAILED', e.message); server.close(); process.exit(1); });
