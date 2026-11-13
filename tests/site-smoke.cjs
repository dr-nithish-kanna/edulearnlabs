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
// Letter Workshop's build is copied in by `npm run sync-game` after the game repo is done. Until then, every check that
// needs /play/word-building-grade-1/ is skipped OUT LOUD (a silent skip proves nothing, see the playbook).
const WORD = 'word-building-grade-1';
const WORD_SYNCED = fs.existsSync(path.join(DIST, 'play', WORD, 'index.html'));
const skipped = [];
const skip = msg => { console.log(`SKIPPED: game build not synced: ${msg}`); skipped.push(msg); };
let unsyncedMisses = 0; // requests for the missing build (poster, manifest) that 404 before the sync
// Screenshots only when SHOTS=<folder> is set, for a human to look at.
const shot = (page, name, fullPage = false) => process.env.SHOTS ? page.screenshot({ path: `${process.env.SHOTS}/${name}.png`, fullPage }) : null;
const check = (ok, msg) => { console.log(`${ok ? 'ok  ' : 'FAIL'} ${msg}`); if (!ok) failures++; };

/** Plays a whole Addition Garden session by tapping (tap a bin, then the basket), the way a child without drag would. */
async function playFullGame(page) {
  const game = page.frameLocator('.overlay iframe');
  await game.locator('.ell-start .ell-btn').click({ force: true, timeout: 15000 });
  const center = async loc => { const b = await loc.boundingBox(); return { x: b.x + b.width / 2, y: b.y + b.height / 2 }; };
  for (let n = 0; n < 20; n++) {
    if (await game.locator('.ell-end:not([hidden])').count()) break;
    await game.locator('.ell-fill-view[data-phase="build"]').waitFor({ timeout: 15000 });
    const bins = await game.locator('.ell-fill-bin').evaluateAll(els => els.map(e => ({ id: e.dataset.bin, want: Number(e.dataset.want) })));
    const prefill = await game.locator('.ell-cell.is-pre').count();
    const answer = prefill + bins.reduce((t, b) => t + b.want, 0);
    for (const b of bins) for (let i = 0; i < b.want; i++) {
      const from = await center(game.locator(`.ell-fill-bin[data-bin="${b.id}"]`));
      const to = await center(game.locator('.ell-fill-target'));
      await page.mouse.click(from.x, from.y);
      await page.mouse.click(to.x, to.y);
      await page.waitForTimeout(80);
    }
    await game.locator('.ell-fill-choices:not([hidden])').waitFor({ timeout: 15000 });
    await game.locator(`.ell-choice[data-choice="${answer}"]`).click();
    for (let i = 0; i < 100; i++) {
      if (await game.locator('.ell-end:not([hidden])').count()) break;
      if ((await game.locator('.ell-fill-view').getAttribute('data-phase').catch(() => null)) === 'build') break;
      await page.waitForTimeout(100);
    }
    await page.waitForTimeout(1300);
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
  page.on('console', m => {
    if (m.type() !== 'error') return;
    // Before the sync, the Letter Workshop poster and asset manifest 404. Counted and reported, never silently dropped.
    if (!WORD_SYNCED && (m.location().url || '').includes(`/play/${WORD}/`)) { unsyncedMisses++; return; }
    errors.push(m.text());
  });
  if (!WORD_SYNCED) console.log(`SKIPPED: game build not synced: dist/play/${WORD}/ is missing, so the Letter Workshop play checks below are skipped. Run npm run sync-game -- ../${WORD}, then npm run build && npm run test:e2e.`);
  await page.addInitScript(() => {
    window.__cls = 0;
    new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; })
      .observe({ type: 'layout-shift', buffered: true });
    new PerformanceObserver(l => { const e = l.getEntries().at(-1); window.__lcp = e.startTime; }).observe({ type: 'largest-contentful-paint', buffered: true });
    // Runs in the game frame too: remember what the website told the game, to check the contract.
    addEventListener('message', e => { if (e.data && e.data.type === 'HostInit') window.__hostInit = e.data; });
  });
  // The newest game frame, and the HostInit it received.
  const gameFrame = () => page.frames().filter(f => f.url().includes('/play/')).at(-1);
  const hostInit = async () => {
    await page.waitForFunction(() => !!document.querySelector('.overlay iframe')?.contentWindow?.__hostInit, null, { timeout: 15000 });
    return gameFrame().evaluate(() => window.__hostInit);
  };

  const cdp = await ctx.newCDPSession(page);
  await cdp.send('Network.enable');
  await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 150, downloadThroughput: 200000, uploadThroughput: 93750 });
  await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });

  // Every page: one H1, a title, a description, no layout shift.
  for (const p of ['', 'math-games/', 'math-games/addition-for-grade-1/', 'math-games/subtraction-for-grade-1/',
    'language-games/', 'language-games/word-building-for-grade-1/', 'grown-ups/', 'privacy/']) {
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
  const init1 = await hostInit();
  const firstProfile = Object.keys(await page.evaluate(() => JSON.parse(localStorage.getItem('ell:v1') || '{"profiles":{}}').profiles))[0];
  check(JSON.stringify(init1.garden) === '{"total":0,"items":[]}', `HostInit carries an empty garden for a garden game: ${JSON.stringify(init1.garden)}`);
  check(!JSON.stringify(init1).includes('p_'), 'HostInit carries no profile id');
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
  const garden = Object.values(store.gardens || {})[0]?.['addition-grade-1'];
  check(!('rewards' in store.sessions[0]) && garden && garden.items.length + Object.values(garden.meadow || {}).reduce((t, n) => t + n, 0) === 10, `ten solved orders planted ten seeds (${garden && garden.items.length})`);
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

  // Garden, website side. The fill-container build is not synced yet, so the game frame posts what that build will
  // send: a GameCompleted with `hints`, `rewards` and an extra unknown field. Same origin and same source window as
  // the real game, so it goes through player.ts's real origin check.
  await hostInit();
  await gameFrame().evaluate(() => {
    const session = { id: 's_e2egarden', game: 'addition-grade-1', gameVersion: '2.0.0', skill: 'math.addition.within-20',
      startedAt: new Date().toISOString(), durationSec: 40, questions: 2, firstTry: 1, levelStart: 1, levelEnd: 1,
      maxDifficulty: 1, completed: false, missed: ['q-3-4'], mistakes: { 'off-by-one': 1 }, hints: 1, dragPath: [1, 2],
      rewards: [0, 1].map(i => ({ id: 's_e2egarden-' + i, kind: 'garden', species: ['sunflower', 'tulip'][i], at: new Date().toISOString() })) };
    parent.postMessage({ type: 'GameCompleted', session }, location.origin);
    parent.postMessage({ type: 'GameCompleted', session }, location.origin); // a repeat must not plant twice
    parent.postMessage({ type: 'GameExit', reason: 'home' }, location.origin);
  });
  await page.locator('.overlay').waitFor({ state: 'hidden' });
  const g = await page.evaluate(() => JSON.parse(localStorage.getItem('ell:v1')));
  const sib = g.sessions.find(x => x.id === 's_e2egarden');
  check(sib && sib.profile !== firstProfile && sib.seeds === 2 && sib.hints === 1 && !('rewards' in sib) && !('dragPath' in sib),
    'fill-container session saved for the chosen player: seeds and hints kept, rewards moved out, unknown field dropped');
  const items = g.gardens?.[sib?.profile]?.['addition-grade-1']?.items ?? [];
  check(items.length === 2 && items.map(i => i.species).join() === 'sunflower,tulip', `two seeds planted once (${items.length})`);
  const firstGarden = g.gardens?.[firstProfile]?.['addition-grade-1'];
  const firstCount = (firstGarden?.items.length ?? 0) + Object.values(firstGarden?.meadow ?? {}).reduce((t, n) => t + n, 0);
  check(firstCount === 20 && !firstGarden.items.some(i => i.id.includes('e2egarden')), `the other child's garden is untouched (still ${firstCount} seeds from their two real games)`);
  await page.locator('[data-play]').click({ force: true });
  await page.locator('#player-picker .pick').nth(1).click();
  const init2 = await hostInit();
  check(init2.garden?.total === 2 && init2.garden.items.every(i => i.stage === 0 && i.nextStage === 1) && init2.garden.items[0].species === 'tulip',
    `next HostInit shows the garden, newest first, seeds about to sprout: ${JSON.stringify(init2.garden)}`);

  // Pond Hop, website side. Its reward is session lights only: the website sends no garden, and a session record has
  // no `rewards`. The frame posts what the real build sends (the game's own smoke test proves the real build does).
  await page.goto(origin + BASE + 'math-games/subtraction-for-grade-1/');
  await page.locator('[data-play]').click({ force: true });
  await page.locator('#player-picker .pick').nth(1).click();
  const pondInit = await hostInit();
  check(!('garden' in pondInit), 'Pond Hop HostInit carries no garden (lights are never stored)');
  await gameFrame().evaluate(() => {
    const session = { id: 's_e2epond', game: 'subtraction-grade-1', gameVersion: '1.0.0', skill: 'math.subtraction.within-20',
      startedAt: new Date().toISOString(), durationSec: 90, questions: 10, firstTry: 6, levelStart: 1, levelEnd: 3,
      maxDifficulty: 3, completed: true, missed: ['q-8m3', 'q-9m4', 'q-7m2', 'q-6m5'], mistakes: { 'wrong-operation': 4 }, hints: 2 };
    parent.postMessage({ type: 'GameCompleted', session }, location.origin);
    parent.postMessage({ type: 'GameExit', reason: 'home' }, location.origin);
  });
  await page.locator('.overlay').waitFor({ state: 'hidden' });
  const pond = await page.evaluate(() => JSON.parse(localStorage.getItem('ell:v1')));
  const ps = pond.sessions.find(x => x.id === 's_e2epond');
  check(ps && ps.skill === 'math.subtraction.within-20' && !('rewards' in ps) && !ps.seeds, 'Pond Hop session saved with no seeds and no rewards');
  check(!Object.values(pond.gardens || {}).some(gd => gd['subtraction-grade-1']), 'Pond Hop created no garden for any child');
  await page.goto(origin + BASE + 'grown-ups/');
  const gu = (await page.locator('body').textContent()).replace(/\s+/g, ' ');
  check(gu.includes('Taking away within 20'), 'Grown-ups page lists Taking away within 20');
  check(gu.includes('adds instead of taking away') && !gu.includes('subtracts instead of adding'), 'Grown-ups tip for the wrong operation is the subtraction one');
  await shot(page, 'site-grown-ups-pond', true);

  // ---------- Letter Workshop: category page, game page, navigation, sitemap (no game build needed) ----------
  const words = sel => page.evaluate(q => (document.querySelector(q)?.innerText ?? '').split(/\s+/).filter(Boolean).length, sel);
  await page.goto(origin + BASE);
  const home = (await page.locator('main').innerText()).replace(/\s+/g, ' ');
  check(home.includes('2 games ready, 6 on the way') && home.includes('1 game ready, 7 on the way'),
    'home page counts: math 2 ready 6 on the way, reading 1 ready 7 on the way');
  check(await page.locator(`main a.subject-card[href="${BASE}language-games/"]`).count() === 1, 'home page Reading games card links to /language-games/');
  check(await page.locator(`main a.game-card[href="${BASE}language-games/word-building-for-grade-1/"]`).count() === 1, 'home page lists Letter Workshop');
  await page.goto(origin + BASE + 'language-games/');
  check((await page.locator('h1').innerText()).includes('reading and language games'), 'language category page: H1');
  check(await page.locator('.site-header a[aria-current="page"]').innerText() === 'Reading games', 'language category page: Reading games is the current nav item');
  check(await page.locator(`.crumbs a.back[href="${BASE}"]`).count() === 1 && (await page.locator('.crumbs [aria-current=page]').innerText()) === 'Reading games',
    'language category page: breadcrumbs Home > Reading games with a back button');
  check(await page.locator(`.grid a.game-card[href="${BASE}language-games/word-building-for-grade-1/"]`).count() === 1, 'language category page: lists Word Building for Grade 1');
  const soonText = await page.locator('.soon-list').innerText();
  check(!/Word building/i.test(soonText) && /Sentence completion/.test(soonText), 'language category page: Word building is off the coming-soon list');
  const catWords = await words('main');
  check(catWords >= 500 && catWords <= 1100, `language category page: ${catWords} words of text (target 500 to 1000 of prose)`);
  await page.goto(origin + BASE + 'language-games/word-building-for-grade-1/');
  check(await page.locator('h1').innerText() === 'Word Building for Grade 1', 'word game page: H1 is the keyword title');
  check(/Word Building for Grade 1.*Grade 1|Grade 1.*Spelling/.test(await page.title()), `word game page: title "${await page.title()}"`);
  check(await page.locator(`.crumbs a.back[href="${BASE}language-games/"]`).count() === 1, 'word game page: back button goes to Reading games');
  const gameWords = await words('main section.prose');
  check(gameWords >= 300 && gameWords <= 600, `word game page: ${gameWords} words of text (target 300 to 600)`);
  check(await page.locator(`[data-game-player][data-game="${WORD}"][data-reward="wall"]`).count() === 1, 'word game page: player is wired with reward "wall"');
  check(await page.locator(`main a[href="${BASE}math-games/addition-for-grade-1/"]`).count() >= 1 &&
    await page.locator(`main a[href="${BASE}math-games/subtraction-for-grade-1/"]`).count() >= 1, 'word game page: links to the two math games');
  check(/word wall/i.test(await page.locator('main').innerText()) && /Nothing is sent anywhere/.test(await page.locator('main').innerText()),
    'word game page: explains the word wall stays on this device');
  const sitemap = fs.readdirSync(DIST).filter(f => /^sitemap-\d+\.xml$/.test(f)).map(f => fs.readFileSync(path.join(DIST, f), 'utf8')).join('');
  check(sitemap.includes('/language-games/</loc>') && sitemap.includes('/language-games/word-building-for-grade-1/</loc>') && !sitemap.includes('/play/'),
    'sitemap lists the language category and the word game page, and no /play/ files');
  await page.goto(origin + BASE + 'privacy/');
  check(/word wall/.test(await page.locator('main').innerText()), 'privacy page mentions the word wall');

  // ---------- Letter Workshop: play round trip (needs the synced build) ----------
  // Same pattern as the garden checks: the REAL game frame sends GameReady (so HostInit is real), then the frame posts
  // what the build sends at the end: word rewards with a repeat, a junk entry and an unknown kind.
  if (WORD_SYNCED) {
    await page.goto(origin + BASE + 'language-games/word-building-for-grade-1/');
    await page.locator('[data-play]').click({ force: true });
    await page.locator('#player-picker .pick').nth(1).click();
    const w1 = await hostInit();
    check(JSON.stringify(w1.wall) === '{"words":[]}' && !('garden' in w1), `word game HostInit carries an empty wall and no garden: ${JSON.stringify(w1.wall)}`);
    check(!JSON.stringify(w1).includes('p_'), 'word game HostInit carries no profile id');
    await gameFrame().evaluate(() => {
      const at = new Date().toISOString();
      const session = { id: 's_e2eword', game: 'word-building-grade-1', gameVersion: '1.0.0', skill: 'language.phonics.word-building',
        startedAt: at, durationSec: 100, questions: 4, firstTry: 2, levelStart: 1, levelEnd: 2, maxDifficulty: 2, completed: false,
        missed: ['w-dog'], mistakes: { 'look-alike': 1, 'wrong-vowel': 1 }, hints: 2,
        rewards: [
          { id: 's_e2eword-0', kind: 'word', wordId: 'w-cat', at }, { id: 's_e2eword-1', kind: 'word', wordId: 'w-dog', at },
          { id: 's_e2eword-2', kind: 'word', wordId: 'w-cat', at }, { id: 's_e2eword-3', kind: 'word', wordId: '<b>', at },
          { id: 's_e2eword-4', kind: 'sticker', wordId: 'w-sun', at },
        ] };
      parent.postMessage({ type: 'GameCompleted', session }, location.origin);
      parent.postMessage({ type: 'GameCompleted', session }, location.origin);
      parent.postMessage({ type: 'GameExit', reason: 'home' }, location.origin);
    });
    await page.locator('.overlay').waitFor({ state: 'hidden' });
    const ws = await page.evaluate(() => JSON.parse(localStorage.getItem('ell:v1')));
    const wsess = ws.sessions.find(x => x.id === 's_e2eword');
    const wall = ws.walls?.[wsess?.profile]?.['word-building-grade-1'];
    check(wsess && !('rewards' in wsess) && wsess.hints === 2 && wsess.mistakes['look-alike'] === 1, 'word session saved: rewards moved out, hints and letter mistakes kept');
    check(wall && wall.v === 1 && wall.words.map(x => x.wordId).join() === 'w-cat,w-dog', `word wall stored once per word, junk and unknown kinds dropped: ${JSON.stringify(wall && wall.words.map(x => x.wordId))}`);
    check(!ws.walls?.[firstProfile]?.['word-building-grade-1'], "the other child's wall is untouched");
    await page.locator('[data-play]').click({ force: true });
    await page.locator('#player-picker .pick').nth(1).click();
    const w2 = await hostInit();
    check(JSON.stringify(w2.wall) === '{"words":["w-cat","w-dog"]}', `next HostInit shows the wall, oldest first: ${JSON.stringify(w2.wall)}`);
    await gameFrame().evaluate(() => parent.postMessage({ type: 'GameExit', reason: 'home' }, location.origin));
    await page.locator('.overlay').waitFor({ state: 'hidden' });
  } else {
    skip('word game HostInit carries an empty wall and no garden');
    skip('word game GameCompleted stores word cards once per word (play round trip)');
    skip('next HostInit shows the wall, oldest first');
  }
  // Pond Hop and Addition Garden must still get exactly what they got before the wall existed.
  await page.goto(origin + BASE + 'math-games/subtraction-for-grade-1/');
  await page.locator('[data-play]').click({ force: true });
  await page.locator('#player-picker .pick').nth(1).click();
  const pondAgain = await hostInit();
  check(!('wall' in pondAgain) && !('garden' in pondAgain), 'Pond Hop HostInit still carries no wall and no garden');
  await gameFrame().evaluate(() => parent.postMessage({ type: 'GameExit', reason: 'home' }, location.origin));
  await page.locator('.overlay').waitFor({ state: 'hidden' });

  // ---------- Word wall store round trip through the built site (no game build needed) ----------
  // A store saved by this code's future self: a wall, a garden, a wall with a newer sub-schema and letter mistakes.
  // The Grown-ups page loads it, saves it (adding a player), and must keep every wall byte for byte.
  const seeded = await page.evaluate(() => {
    const at = '2026-11-13T10:00:00.000Z';
    const prof = id => ({ id, avatar: 'fox', color: 'orange', createdAt: at });
    const sess = (id, mistakes) => ({ id, game: 'word-building-grade-1', gameVersion: '1.0.0', skill: 'language.phonics.word-building',
      startedAt: at, durationSec: 90, questions: 8, firstTry: 5, levelStart: 1, levelEnd: 2, maxDifficulty: 2, completed: true,
      missed: [], mistakes, hints: 1, profile: 'p_wall' });
    const doc = { schema: 1, updatedAt: at, activeProfile: 'p_wall', settings: { audio: true, music: true, reducedMotion: false },
      profiles: { p_wall: prof('p_wall') }, sessions: [sess('s_w1', { 'look-alike': 2 }), sess('s_w2', { 'look-alike': 1, 'letter-order': 1 })],
      totals: {}, gardens: { p_wall: { 'addition-grade-1': { v: 1, items: [{ id: 'g1', species: 'tulip', at, session: 's_x' }], meadow: {} } } },
      walls: { p_wall: {
        'word-building-grade-1': { v: 1, words: [{ wordId: 'w-cat', at, session: 's_w1' }, { wordId: 'w-frog', at, session: 's_w2' }] },
        'spelling-grade-2': { v: 9, anything: ['newer code wrote this'] } } } };
    localStorage.setItem('ell:v1', JSON.stringify(doc));
    return doc;
  });
  await page.goto(origin + BASE + 'grown-ups/');
  const guWords = (await page.locator('body').innerText()).replace(/\s+/g, ' ');
  check(guWords.includes('Word building') && guWords.includes('look alike'), 'Grown-ups shows the Word building skill and the look-alike tip');
  await page.getByRole('button', { name: '+ Add a player' }).click();
  const after = await page.evaluate(() => JSON.parse(localStorage.getItem('ell:v1')));
  check(after.schema === 1 && Object.keys(after.profiles).length === 2 && JSON.stringify(after.walls) === JSON.stringify(seeded.walls) &&
    JSON.stringify(after.gardens) === JSON.stringify(seeded.gardens), 'word wall store round trip: load and save keep walls (and a newer-v wall) and gardens unchanged');
  const delBtn = page.locator('[data-delete="p_wall"]');
  await delBtn.evaluate(b => b.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })));
  page.once('dialog', d => d.accept());
  await page.waitForTimeout(3400);
  const gone = await page.evaluate(() => JSON.parse(localStorage.getItem('ell:v1')));
  check(!gone.profiles.p_wall && !gone.walls.p_wall && !gone.gardens.p_wall && !gone.sessions.some(x => x.profile === 'p_wall'),
    'deleting a player (hold to confirm) deletes their word wall, garden and sessions');

  if (!WORD_SYNCED) console.log(`SKIPPED: game build not synced: ${skipped.length} play check(s) skipped, ${unsyncedMisses} request(s) for the missing build answered 404 and were not counted as errors.`);
  check(errors.length === 0, `no console errors${errors.length ? ': ' + errors.join(' | ') : ''}`);
  console.log(failures ? `\n${failures} check(s) failed` : '\nPASS');
  await browser.close(); server.close();
  process.exitCode = failures ? 1 : 0;
})().catch(e => { console.error('FAILED', e.message); server.close(); process.exit(1); });
