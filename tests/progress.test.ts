import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  addSession, bestStars, createProfile, deleteProfile, emptyStore, ensureProfile, GARDEN_MAX_ITEMS, GARDEN_SPECIES,
  clearAll, gardenView, KEY, load, mastery, MAX_PROFILES, mistakeTip, parseStore, practiceItems, save, speciesFor, startLevel,
  update, type Reward, type SessionRecord, type Store,
} from '../src/scripts/progress.ts';

let n = 0;
const rec = (o: Partial<SessionRecord> = {}): SessionRecord => ({
  id: `s_${++n}`, game: 'addition-grade-1', gameVersion: '1.0.0', skill: 'math.addition.within-20',
  startedAt: '2026-11-11T10:00:00Z', durationSec: 120, questions: 10, firstTry: 8, levelStart: 1, levelEnd: 3,
  maxDifficulty: 3, completed: true, missed: [], mistakes: {}, ...o,
});

test('corrupt or foreign data never crashes, it starts fresh', () => {
  for (const raw of [null, '', '{', '[]', '{"schema":"2"}', '{"schema":1,"profiles":{},"sessions":"x"}'])
    assert.deepEqual(parseStore(raw).sessions, []);
});

// ---------- Newer schema guard (decision 7) ----------

/** A tiny localStorage for node, so load/save/update run exactly as in the browser. */
const fakeStorage = (initial: Record<string, string> = {}) => {
  const data = new Map<string, string>();
  const writes: string[] = [];
  (globalThis as any).localStorage = {
    getItem: (k: string) => data.get(k) ?? null,
    setItem: (k: string, v: string) => { writes.push(k); data.set(k, v); },
    removeItem: (k: string) => { data.delete(k); },
  };
  clearAll(); // also forgets the in-memory store a previous test (or a read-only tab) left behind
  for (const [k, v] of Object.entries(initial)) data.set(k, v);
  return { data, writes };
};

test('a newer schema is not corrupt: read-only, never overwritten', () => {
  const s = parseStore('{"schema":2,"profiles":{"p_a":{}},"sessions":[]}');
  assert.equal(s.readOnly, true);
  assert.deepEqual(s.profiles, {}, 'newer fields may mean something else, so nothing is read from them');
});

test('old tab after a deploy: playing in it never touches the newer document', () => {
  const newer = JSON.stringify({ schema: 2, profiles: { p_a: { id: 'p_a' } }, sessions: [{ id: 's_new' }], pets: [1] });
  const { data, writes } = fakeStorage({ [KEY]: newer });
  // The old tab does what player.ts does: make sure a player exists, then save a finished session.
  const id = update(s => ensureProfile(s).id);
  update(s => addSession(s, id, rec()));
  assert.equal(data.get(KEY), newer, 'stored document is byte for byte unchanged');
  assert.deepEqual(writes, []);
  // The tab still works for this visit: the player and session live in memory.
  assert.equal(load().sessions.length, 1);
  assert.equal(load().profiles[id].id, id);
});

test('schema 1 with fields this code does not know keeps them on save', () => {
  const doc = { schema: 1, profiles: {}, sessions: [], stickers: { p_a: [{ id: 'first-garden' }] } };
  const { data } = fakeStorage({ [KEY]: JSON.stringify(doc) });
  update(s => { ensureProfile(s); });
  assert.deepEqual(JSON.parse(data.get(KEY)!).stickers, doc.stickers);
});

test('a document without gardens (written before this change) loads and saves normally', () => {
  const doc = { schema: 1, profiles: { p_a: { id: 'p_a', avatar: 'fox', color: 'orange', createdAt: 'x' } }, sessions: [] };
  const { data } = fakeStorage({ [KEY]: JSON.stringify(doc) });
  const s = load();
  assert.deepEqual(s.gardens, {});
  assert.equal(s.readOnly, undefined);
  save(s);
  assert.equal(JSON.parse(data.get(KEY)!).schema, 1, 'top-level schema stays 1');
  assert.equal(JSON.parse(data.get(KEY)!).readOnly, undefined);
});

test('first visit creates exactly one profile and makes it active', () => {
  const s = emptyStore();
  const p = ensureProfile(s);
  assert.equal(ensureProfile(s).id, p.id);
  assert.equal(Object.keys(s.profiles).length, 1);
  assert.equal(s.activeProfile, p.id);
});

test('profiles: up to 12, avatars unique while possible, no names stored', () => {
  const s = emptyStore();
  for (let i = 0; i < MAX_PROFILES; i++) assert.ok(createProfile(s));
  assert.equal(createProfile(s), null);
  assert.equal(new Set(Object.values(s.profiles).map(p => p.avatar)).size, 12);
  assert.deepEqual(Object.keys(Object.values(s.profiles)[0]).sort(), ['avatar', 'color', 'createdAt', 'id']);
});

test('sessions are facts: duplicates ignored, junk rejected, unknown profile rejected', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  const r = rec();
  assert.ok(addSession(s, p.id, r));
  assert.equal(addSession(s, p.id, r), false);
  assert.equal(addSession(s, p.id, { hello: 1 }), false);
  assert.equal(addSession(s, 'p_nobody', rec()), false);
  assert.equal(s.sessions.length, 1);
});

test('old sessions fold into totals so storage stays small', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  for (let i = 0; i < 60; i++) addSession(s, p.id, rec());
  assert.equal(s.sessions.length, 50);
  assert.deepEqual(s.totals[p.id]['addition-grade-1'], { sessions: 10, questions: 100, firstTry: 80 });
});

test('start level is one below the last level reached, never below 1', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  assert.equal(startLevel(s, p.id, 'addition-grade-1'), 1);
  addSession(s, p.id, rec({ levelEnd: 4 }));
  assert.equal(startLevel(s, p.id, 'addition-grade-1'), 3);
  addSession(s, p.id, rec({ levelEnd: 1 }));
  assert.equal(startLevel(s, p.id, 'addition-grade-1'), 1);
});

test('practice items: recent misses, newest first, unique, at most 5', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  addSession(s, p.id, rec({ missed: ['q-1-1', 'q-2-2'] }));
  addSession(s, p.id, rec({ missed: ['q-3-3', 'q-1-1', 'q-4-4', 'q-5-5', 'q-6-6'] }));
  assert.deepEqual(practiceItems(s, p.id, 'addition-grade-1'), ['q-3-3', 'q-1-1', 'q-4-4', 'q-5-5', 'q-6-6']);
});

test('mastery grows seed, sprout, bud, flower and needs two different days for flower', () => {
  const s = emptyStore(); const p = ensureProfile(s); const sk = 'math.addition.within-20';
  assert.equal(mastery(s, p.id, sk, 5), 'new');
  addSession(s, p.id, rec({ firstTry: 5, maxDifficulty: 1 }));
  assert.equal(mastery(s, p.id, sk, 5), 'practicing');
  addSession(s, p.id, rec({ firstTry: 8, maxDifficulty: 3 }));
  assert.equal(mastery(s, p.id, sk, 5), 'getting');
  addSession(s, p.id, rec({ firstTry: 9, maxDifficulty: 5, startedAt: '2026-11-11T10:00:00Z' }));
  addSession(s, p.id, rec({ firstTry: 10, maxDifficulty: 5, startedAt: '2026-11-11T18:00:00Z' }));
  assert.equal(mastery(s, p.id, sk, 5), 'getting', 'same day twice is not enough');
  addSession(s, p.id, rec({ firstTry: 9, maxDifficulty: 5, startedAt: '2026-11-13T09:00:00Z' }));
  assert.equal(mastery(s, p.id, sk, 5), 'mastered');
});

test('best stars counts completed sessions only; deleting a profile removes its data', () => {
  const s = emptyStore(); const p = ensureProfile(s); const q = createProfile(s)!;
  addSession(s, p.id, rec({ firstTry: 10, completed: false }));
  addSession(s, p.id, rec({ firstTry: 7 }));
  addSession(s, q.id, rec({ firstTry: 10 }));
  assert.equal(bestStars(s, p.id, 'addition-grade-1'), 2);
  deleteProfile(s, p.id);
  assert.equal(s.sessions.every(x => x.profile === q.id), true);
  assert.equal(s.activeProfile, q.id);
});

test('mistake tip appears only when a mistake repeats', () => {
  const s = emptyStore(); const p = ensureProfile(s); const sk = 'math.addition.within-20';
  addSession(s, p.id, rec({ mistakes: { 'wrong-operation': 2 } }));
  assert.equal(mistakeTip(s, p.id, sk), null);
  addSession(s, p.id, rec({ mistakes: { 'wrong-operation': 1, 'off-by-one': 1 } }));
  assert.match(mistakeTip(s, p.id, sk)!, /subtracts instead of adding/);
});

test('wrong-operation tip is topic aware: subtraction says adding instead of taking away', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  const sub = 'math.subtraction.within-20';
  addSession(s, p.id, rec({ skill: sub, mistakes: { 'wrong-operation': 3 } }));
  const tip = mistakeTip(s, p.id, sub)!;
  assert.match(tip, /adds instead of taking away/);
  assert.doesNotMatch(tip, /subtracts instead of adding/);
  // Other kinds keep their shared text for subtraction, and addition keeps its own tip.
  addSession(s, p.id, rec({ skill: sub, mistakes: { 'off-by-one': 9 } }));
  assert.match(mistakeTip(s, p.id, sub)!, /one away/);
  const s2 = emptyStore(); const q = ensureProfile(s2);
  addSession(s2, q.id, rec({ mistakes: { 'wrong-operation': 3 } }));
  assert.match(mistakeTip(s2, q.id, 'math.addition.within-20')!, /subtracts instead of adding/);
});

// ---------- Garden ----------

const G = 'addition-grade-1';
/** A fill-container session with n solved orders, each earning one seed. */
const played = (n: number, o: Partial<SessionRecord> = {}): SessionRecord => {
  const r = rec({ questions: Math.max(n, o.questions ?? n), hints: 0, ...o });
  r.rewards = Array.from({ length: n }, (_, i): Reward =>
    ({ id: `${r.id}-${i}`, kind: 'garden', species: speciesFor(GARDEN_SPECIES, i), at: '2026-11-12T10:00:00Z' }));
  return r;
};
const garden = (s: Store, p: string) => s.gardens[p][G];
const stagesNow = (s: Store, p: string) => gardenView(s, p, G)!.items.map(i => i.stage);

test('rewards move from the session into the garden, stripped from the stored session', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  assert.ok(addSession(s, p.id, played(3, { hints: 2 })));
  assert.equal(garden(s, p.id).v, 1);
  assert.deepEqual(garden(s, p.id).items.map(i => i.species), ['sunflower', 'tulip', 'daisy']);
  assert.equal(garden(s, p.id).items[0].session, s.sessions[0].id);
  assert.equal('rewards' in s.sessions[0], false);
  assert.equal(s.sessions[0].seeds, 3);
  assert.equal(s.sessions[0].hints, 2);
});

test('duplicate rewards and junk are ignored; never more seeds than questions', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  const r = played(2);
  r.rewards!.push(r.rewards![0], { id: 'x', kind: 'sticker', species: 'tulip', at: 'x' } as any,
    { id: 'y', kind: 'garden', species: '<b>', at: 'x' } as any);
  addSession(s, p.id, r);
  assert.equal(garden(s, p.id).items.length, 2);
  assert.equal(addSession(s, p.id, r), false, 'same session again plants nothing');
  assert.equal(garden(s, p.id).items.length, 2);
  const greedy = played(5, { questions: 2 });
  addSession(s, p.id, greedy);
  assert.equal(garden(s, p.id).items.length, 4);
});

test('unknown session fields are ignored, not stored', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  addSession(s, p.id, { ...rec(), pointerPath: [1, 2, 3], profile: 'p_spoof' });
  assert.equal('pointerPath' in s.sessions[0], false);
  assert.equal(s.sessions[0].profile, p.id);
});

test('quiz sessions (no rewards) make no garden', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  addSession(s, p.id, rec());
  assert.equal(s.gardens[p.id], undefined);
  assert.deepEqual(gardenView(s, p.id, G), { total: 0, items: [] });
});

test('stages: seed, sprout, bloom across sessions; only sessions with a solved order count', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  addSession(s, p.id, played(1));
  assert.deepEqual(gardenView(s, p.id, G)!.items.map(i => [i.stage, i.nextStage]), [[0, 1]]);
  addSession(s, p.id, played(0, { questions: 0, completed: false })); // opened and left: no growth
  addSession(s, p.id, played(0, { questions: 1, completed: false })); // asked one, solved none: no growth
  assert.deepEqual(stagesNow(s, p.id), [0]);
  addSession(s, p.id, played(1, { questions: 1, completed: false })); // early exit with one solved order counts
  assert.deepEqual(stagesNow(s, p.id), [0, 1], 'newest first');
  addSession(s, p.id, played(1));
  assert.deepEqual(gardenView(s, p.id, G)!.items.map(i => [i.stage, i.nextStage]), [[0, 1], [1, 2], [2, 2]]);
});

test('time alone never changes a stage (nothing wilts, nothing grows on its own)', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  addSession(s, p.id, played(2, { startedAt: '2026-11-12T10:00:00Z' }));
  const before = JSON.stringify(gardenView(s, p.id, G));
  const realNow = Date.now;
  try {
    Date.now = () => realNow() + 60 * 86400e3;
    assert.equal(JSON.stringify(gardenView(s, p.id, G)), before);
  } finally { Date.now = realNow; }
  // A later session with a wrong device clock (60 days in the past) still counts: order of play decides.
  addSession(s, p.id, played(1, { startedAt: '2026-09-13T10:00:00Z' }));
  assert.deepEqual(stagesNow(s, p.id), [0, 1, 1]);
});

test('species follow the fixed cycle and continue from the garden total', () => {
  assert.deepEqual(Array.from({ length: 7 }, (_, i) => speciesFor(GARDEN_SPECIES, i)),
    ['sunflower', 'tulip', 'daisy', 'lavender', 'strawberry', 'small-tree', 'sunflower']);
  assert.equal(speciesFor(GARDEN_SPECIES, 23, 2), 'tulip', '25 % 6 = 1');
});

test('garden view: newest 30 for the plot, older ones in the meadow, total stays exact', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  for (let k = 0; k < 4; k++) addSession(s, p.id, played(10));
  const v = gardenView(s, p.id, G)!;
  assert.equal(v.total, 40);
  assert.equal(v.items.length, 30);
  assert.equal(Object.values(v.meadow!).reduce((a, b) => a + b, 0), 10);
  assert.equal(v.items[0].id, s.sessions[3].id + '-9', 'newest first');
  assert.deepEqual(Object.keys(v.items[0]).sort(), ['id', 'nextStage', 'species', 'stage'], 'no timestamps, no profile');
});

test('cap: 300 items per child per game, oldest blooms fold into the meadow, total kept', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  for (let k = 0; k < 35; k++) addSession(s, p.id, played(10));
  const g = garden(s, p.id);
  assert.equal(g.items.length, GARDEN_MAX_ITEMS);
  assert.equal(Object.values(g.meadow).reduce((a, b) => a + b, 0), 50);
  assert.equal(gardenView(s, p.id, G)!.total, 350);
  assert.equal(g.items[0].id, s.sessions[5].id + '-0', 'the oldest were folded, newest kept');
});

test('sessions folded at 50 per game: their items count as blooms', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  addSession(s, p.id, played(1));
  for (let k = 0; k < 55; k++) addSession(s, p.id, rec());
  assert.equal(s.sessions.some(x => x.id === garden(s, p.id).items[0].session), false);
  assert.deepEqual(stagesNow(s, p.id), [2]);
});

test('gardens are per child; deleting a child deletes their garden', () => {
  const s = emptyStore(); const p = ensureProfile(s); const q = createProfile(s)!;
  addSession(s, p.id, played(2));
  addSession(s, q.id, played(1));
  assert.equal(gardenView(s, q.id, G)!.total, 1);
  deleteProfile(s, p.id);
  assert.equal(s.gardens[p.id], undefined);
  assert.equal(gardenView(s, q.id, G)!.total, 1);
});

test('a garden with a newer sub-schema is kept untouched and not shown', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  const future = { v: 2, plots: [{ any: 'thing' }] };
  (s.gardens as any)[p.id] = { [G]: future };
  addSession(s, p.id, played(2));
  assert.deepEqual(s.gardens[p.id][G], future);
  assert.equal(gardenView(s, p.id, G), undefined);
  assert.deepEqual(parseStore(JSON.stringify(s)).gardens[p.id][G], future);
});

test('old tab saved rewards inside a session: next load moves them into the garden', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  const r = played(2);
  s.sessions.push({ ...r, profile: p.id } as any); // what pre-garden code does: spreads the whole record
  const back = parseStore(JSON.stringify(s));
  assert.equal(back.gardens[p.id][G].items.length, 2);
  assert.equal('rewards' in back.sessions[0], false);
  assert.equal(back.sessions[0].seeds, 2);
  assert.equal(parseStore(JSON.stringify(back)).gardens[p.id][G].items.length, 2, 'harvest is idempotent');
});
