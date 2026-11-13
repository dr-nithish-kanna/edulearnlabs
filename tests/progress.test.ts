import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  addSession, bestStars, createProfile, deleteProfile, emptyStore, ensureProfile, GARDEN_MAX_ITEMS, GARDEN_SPECIES,
  clearAll, gardenView, hostInitFor, KEY, load, mastery, MAX_PROFILES, mistakeTip, parseStore, practiceItems, quiltView, QUILT_MAX_PATCHES,
  QUILT_VIEW_PATCHES, save, speciesFor, startLevel, update, wallView, WALL_MAX_WORDS, type PatchReward, type Reward, type SessionRecord,
  type Store, type WordReward,
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


// ---------- Word wall (planning/slot-build-design.md, decision 13) ----------

const W = 'word-building-grade-1';
const WSKILL = 'language.phonics.word-building';
/** A slot-build session: one word reward per solved word, in the order they were solved. */
const spelled = (words: string[], o: Partial<SessionRecord> = {}): SessionRecord => {
  const r = rec({ game: W, skill: WSKILL, questions: Math.max(words.length, o.questions ?? words.length), hints: 0, ...o });
  r.rewards = words.map((w, i): WordReward => ({ id: `${r.id}-${i}`, kind: 'word', wordId: w, at: `2026-11-13T10:00:0${i % 10}Z` }));
  return r;
};
const wall = (s: Store, p: string) => s.walls[p][W];

test('word rewards move from the session into the wall, stripped from the stored session', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  assert.ok(addSession(s, p.id, spelled(['w-cat', 'w-dog', 'w-sun'], { hints: 1 })));
  assert.equal(wall(s, p.id).v, 1);
  assert.deepEqual(wall(s, p.id).words.map(x => x.wordId), ['w-cat', 'w-dog', 'w-sun']);
  assert.deepEqual(wall(s, p.id).words[0], { wordId: 'w-cat', at: '2026-11-13T10:00:00Z', session: s.sessions[0].id });
  assert.equal('rewards' in s.sessions[0], false);
  assert.equal(s.sessions[0].seeds, undefined, 'word cards are not garden seeds');
  assert.equal(s.sessions[0].hints, 1);
  assert.equal(s.gardens[p.id], undefined, 'a word game makes no garden');
});

test('wall dedupes by wordId: a word earned again is kept once, the first time stays', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  addSession(s, p.id, spelled(['w-cat', 'w-dog', 'w-cat']));
  const first = wall(s, p.id).words.map(x => ({ ...x }));
  assert.deepEqual(first.map(x => x.wordId), ['w-cat', 'w-dog']);
  addSession(s, p.id, spelled(['w-dog', 'w-hen', 'w-cat'], { startedAt: '2026-11-14T09:00:00Z' }));
  assert.deepEqual(wall(s, p.id).words.map(x => x.wordId), ['w-cat', 'w-dog', 'w-hen'], 'oldest first, new word at the end');
  assert.deepEqual(wall(s, p.id).words.slice(0, 2), first, 'first-earned time and session are unchanged');
});

test('wall order is the order words were earned on this device, not the reward clock', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  addSession(s, p.id, spelled(['w-sun']));
  const late = spelled(['w-pig']);
  late.rewards![0].at = '2020-01-01T00:00:00Z'; // a wrong device clock must not move the card to the front
  addSession(s, p.id, late);
  assert.deepEqual(wallView(s, p.id, W), { words: ['w-sun', 'w-pig'] });
});

test('wall view: word ids only, oldest first; empty for a child with no wall', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  assert.deepEqual(wallView(s, p.id, W), { words: [] });
  addSession(s, p.id, spelled(['w-cat', 'w-dog']));
  const v = wallView(s, p.id, W)!;
  assert.deepEqual(v, { words: ['w-cat', 'w-dog'] });
  assert.doesNotMatch(JSON.stringify(v), /p_|2026|s_/, 'no profile id, no timestamps, no session ids');
});

test('invalid word rewards are dropped; unknown kinds are ignored; never more cards than questions', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  const r = spelled(['w-cat']);
  r.rewards!.push(
    r.rewards![0], // same reward id twice
    { id: 'a', kind: 'word', wordId: '<img src=x>', at: 'x' } as any,
    { id: 'b', kind: 'word', wordId: '', at: 'x' } as any,
    { id: 'c', kind: 'word', wordId: 'w-' + 'x'.repeat(80), at: 'x' } as any,
    { id: 'd', kind: 'word', wordId: 'w-bed' } as any, // no time
    { id: '', kind: 'word', wordId: 'w-bed', at: 'x' } as any,
    { id: 'e', kind: 'sticker', wordId: 'w-bed', at: 'x' } as any,
    { id: 'f', kind: 'word', wordId: 42, at: 'x' } as any,
    'w-bed' as any, null as any,
  );
  addSession(s, p.id, r);
  assert.deepEqual(wallView(s, p.id, W), { words: ['w-cat'] });
  const greedy = spelled(['w-a', 'w-b', 'w-c', 'w-d'], { questions: 2 });
  addSession(s, p.id, greedy);
  assert.deepEqual(wallView(s, p.id, W), { words: ['w-cat', 'w-a', 'w-b'] });
  const notList = rec({ game: W, skill: WSKILL }) as any; notList.rewards = { id: 'x', kind: 'word' };
  assert.ok(addSession(s, p.id, notList), 'a broken rewards field never blocks saving the session');
});

test('the same session saved twice adds no cards', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  const r = spelled(['w-cat', 'w-dog']);
  addSession(s, p.id, r);
  assert.equal(addSession(s, p.id, r), false);
  assert.equal(wall(s, p.id).words.length, 2);
});

test('wall is capped: new words past the cap are not added, earned cards are never dropped', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  const ids = Array.from({ length: WALL_MAX_WORDS + 15 }, (_, i) => `w-${i}`);
  for (let k = 0; k < ids.length; k += 10) addSession(s, p.id, spelled(ids.slice(k, k + 10)));
  assert.equal(wall(s, p.id).words.length, WALL_MAX_WORDS);
  assert.equal(wall(s, p.id).words[0].wordId, 'w-0', 'the first cards stay');
  assert.equal(wall(s, p.id).words.at(-1)!.wordId, `w-${WALL_MAX_WORDS - 1}`);
});

test('walls are per child and per game; deleting a child deletes their wall', () => {
  const s = emptyStore(); const p = ensureProfile(s); const q = createProfile(s)!;
  addSession(s, p.id, spelled(['w-cat']));
  addSession(s, q.id, spelled(['w-dog']));
  addSession(s, q.id, spelled(['w-hen'], { game: 'spelling-grade-2' }));
  assert.deepEqual(wallView(s, q.id, W), { words: ['w-dog'] });
  assert.deepEqual(wallView(s, q.id, 'spelling-grade-2'), { words: ['w-hen'] });
  deleteProfile(s, p.id);
  assert.equal(s.walls[p.id], undefined);
  assert.deepEqual(wallView(s, q.id, W), { words: ['w-dog'] });
});

test('a wall with a newer sub-schema is kept untouched, never written to and not shown', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  const future = { v: 2, shelves: [{ any: 'thing' }] };
  (s.walls as any)[p.id] = { [W]: future };
  addSession(s, p.id, spelled(['w-cat']));
  assert.deepEqual(s.walls[p.id][W], future);
  assert.equal(wallView(s, p.id, W), undefined);
  assert.equal(s.sessions.length, 1, 'the session itself is still saved');
  assert.deepEqual(parseStore(JSON.stringify(s)).walls[p.id][W], future, 'survives a load and save');
  assert.equal(hostInitFor(s, s.profiles[p.id], W, 'wall').wall, undefined, 'HostInit sends no wall it cannot read');
});

test('a store written before walls existed loads, gets an empty walls field and keeps schema 1', () => {
  const doc = {
    schema: 1, profiles: { p_a: { id: 'p_a', avatar: 'fox', color: 'orange', createdAt: 'x' } }, activeProfile: 'p_a',
    sessions: [{ ...rec(), profile: 'p_a' }], gardens: { p_a: { [G]: { v: 1, items: [], meadow: {} } } },
  };
  const { data } = fakeStorage({ [KEY]: JSON.stringify(doc) });
  const s = load();
  assert.deepEqual(s.walls, {});
  assert.equal(s.readOnly, undefined);
  assert.equal(s.sessions.length, 1);
  update(st => addSession(st, 'p_a', spelled(['w-cat'])));
  const saved = JSON.parse(data.get(KEY)!);
  assert.equal(saved.schema, 1, 'top-level schema stays 1');
  assert.deepEqual(saved.walls.p_a[W].words.map((x: any) => x.wordId), ['w-cat']);
  assert.deepEqual(saved.gardens, doc.gardens, 'gardens untouched');
  for (const bad of ['x', 7, [], null]) assert.deepEqual(parseStore(JSON.stringify({ ...doc, walls: bad })).walls, {});
});

test('corrupt wall data never crashes saving or HostInit', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  (s.walls as any)[p.id] = 'broken';
  assert.ok(addSession(s, p.id, spelled(['w-cat'])));
  assert.deepEqual(wallView(s, p.id, W), { words: ['w-cat'] });
  (s.walls as any)[p.id][W].words.push(null, { wordId: 7 }, { wordId: '<b>' });
  assert.deepEqual(wallView(s, p.id, W), { words: ['w-cat'] }, 'junk entries are not shown');
  addSession(s, p.id, spelled(['w-dog']));
  assert.deepEqual(wallView(s, p.id, W), { words: ['w-cat', 'w-dog'] });
  for (const bad of ['x', 3, null, { words: 'nope' }]) {
    (s.walls as any)[p.id][W] = bad; // no `v`: corrupt, not newer, so a fresh wall replaces it
    assert.ok(addSession(s, p.id, spelled(['w-hen'])));
    assert.deepEqual(wallView(s, p.id, W), { words: ['w-hen'] }, JSON.stringify(bad));
  }
});

test('a store with gardens and walls side by side: each game feeds only its own reward', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  addSession(s, p.id, played(2));
  addSession(s, p.id, spelled(['w-cat', 'w-dog']));
  addSession(s, p.id, rec({ game: 'subtraction-grade-1', skill: 'math.subtraction.within-20' }));
  const mixed = rec({ game: W, skill: WSKILL, questions: 4 }); // one list with both kinds: each goes to its own place
  mixed.rewards = [
    { id: mixed.id + '-0', kind: 'word', wordId: 'w-sun', at: 'x' },
    { id: mixed.id + '-1', kind: 'garden', species: 'tulip', at: 'x' },
  ] as any;
  addSession(s, p.id, mixed);
  const back = parseStore(JSON.stringify(s));
  assert.deepEqual(wallView(back, p.id, W), { words: ['w-cat', 'w-dog', 'w-sun'] });
  assert.equal(gardenView(back, p.id, G)!.total, 2);
  assert.equal(back.walls[p.id][G], undefined, 'the garden game has no wall');
  assert.equal(back.walls[p.id]['subtraction-grade-1'], undefined);
  assert.equal(back.gardens[p.id]['subtraction-grade-1'], undefined);
  deleteProfile(back, p.id);
  assert.deepEqual([back.walls, back.gardens, back.sessions], [{}, {}, []]);
});

test('old tab saved word rewards inside a session: next load moves them onto the wall', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  const r = spelled(['w-cat', 'w-cat', 'w-dog']);
  s.sessions.push({ ...r, profile: p.id } as any);
  const back = parseStore(JSON.stringify(s));
  assert.deepEqual(wallView(back, p.id, W), { words: ['w-cat', 'w-dog'] });
  assert.equal('rewards' in back.sessions[0], false);
  assert.deepEqual(parseStore(JSON.stringify(back)).walls[p.id][W].words.length, 2, 'idempotent');
});

// ---------- Quilt (planning/pair-match-design.md, sections 2.4 and 12) ----------

const Q = 'memory-match-prek';
const QSKILL = 'logic-memory.memory.matching-pairs';
const SLUGS = ['gingham-red', 'dots-blue', 'stripe-green', 'flower-yellow'];
/** A pair-match session: one patch reward per finished board, the pattern cycling through SLUGS from `from`. */
const stitched = (count: number, o: Partial<SessionRecord> & { from?: number } = {}): SessionRecord => {
  const { from = 0, ...rest } = o;
  const r = rec({ game: Q, skill: QSKILL, questions: Math.max(count, rest.questions ?? count), hints: 0, misses: 0, ...rest });
  r.rewards = Array.from({ length: count }, (_, i): PatchReward => ({
    id: `${r.id}-${i}`, kind: 'patch', patch: SLUGS[(from + i) % SLUGS.length], at: `2026-11-13T10:00:0${i % 10}Z`,
  }));
  return r;
};
const quilt = (s: Store, p: string) => s.quilts[p][Q];

test('patch rewards move from the session into the quilt, stripped from the stored session', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  assert.ok(addSession(s, p.id, stitched(3, { misses: 2, hints: 1 })));
  assert.equal(quilt(s, p.id).v, 1);
  assert.deepEqual(quilt(s, p.id).patches.map(x => x.patch), ['gingham-red', 'dots-blue', 'stripe-green']);
  assert.deepEqual(quilt(s, p.id).patches[0], { id: `${s.sessions[0].id}-0`, patch: 'gingham-red', at: '2026-11-13T10:00:00Z', session: s.sessions[0].id });
  assert.equal('rewards' in s.sessions[0], false);
  assert.equal(s.sessions[0].seeds, undefined, 'patches are not garden seeds');
  assert.equal(s.sessions[0].misses, 2, 'misses are kept as a fact');
  assert.equal(s.sessions[0].hints, 1);
  assert.equal(s.gardens[p.id], undefined, 'a quilt game makes no garden');
  assert.equal(s.walls[p.id], undefined, 'a quilt game makes no word wall');
});

test('misses are stored when they are a sane number, ignored otherwise', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  addSession(s, p.id, stitched(1, { misses: 0 }));
  assert.equal(s.sessions[0].misses, 0, 'zero misses is a fact too');
  for (const bad of [-1, NaN, '3', null, undefined]) {
    addSession(s, p.id, stitched(1, { misses: bad as any }));
    assert.equal('misses' in s.sessions.at(-1)!, false, String(bad));
  }
  addSession(s, p.id, rec({ misses: 4 }));
  assert.equal(s.sessions.at(-1)!.misses, 4, 'kept for any record that carries it');
});

test('quilt keeps repeats of a pattern and dedupes by reward id only', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  const r = stitched(4); // gingham, dots, stripe, flower
  addSession(s, p.id, r);
  const again = stitched(4, { from: 3 }); // flower, gingham, dots, stripe: repeats of earlier patterns
  addSession(s, p.id, again);
  assert.deepEqual(quiltView(s, p.id, Q), { patches: [...SLUGS, 'flower-yellow', 'gingham-red', 'dots-blue', 'stripe-green'] });
  assert.equal(addSession(s, p.id, r), false, 'the same session twice is not saved again');
  assert.equal(quilt(s, p.id).patches.length, 8);
  // The same reward ids arriving inside another session record (a replay) add nothing either.
  const replay = stitched(2); replay.rewards = r.rewards!.slice(0, 2);
  addSession(s, p.id, replay);
  assert.equal(quilt(s, p.id).patches.length, 8, 'union by id');
  const same = stitched(3); same.rewards![1].id = same.rewards![0].id; // one reward id twice inside one record
  addSession(s, p.id, same);
  assert.equal(quilt(s, p.id).patches.length, 10, 'two new ids added, the repeated id once');
});

test('quilt order is the order patches were earned on this device, not the reward clock', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  addSession(s, p.id, stitched(1));
  const late = stitched(1, { from: 1 });
  late.rewards![0].at = '2020-01-01T00:00:00Z';
  addSession(s, p.id, late);
  assert.deepEqual(quiltView(s, p.id, Q), { patches: ['gingham-red', 'dots-blue'] });
});

test('quilt view: slugs only, oldest first; empty for a child with no quilt; newest 64 at most', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  assert.deepEqual(quiltView(s, p.id, Q), { patches: [] });
  addSession(s, p.id, stitched(2));
  const v = quiltView(s, p.id, Q)!;
  assert.deepEqual(v, { patches: ['gingham-red', 'dots-blue'] });
  assert.doesNotMatch(JSON.stringify(v), /p_|2026|s_/, 'no profile id, no timestamps, no session ids');
  const t = emptyStore(); const q = ensureProfile(t);
  for (let k = 0; k < 8; k++) addSession(t, q.id, stitched(10, { from: k * 10 }));
  const big = quiltView(t, q.id, Q)!.patches;
  assert.equal(big.length, QUILT_VIEW_PATCHES);
  assert.equal(quilt(t, q.id).patches.length, 80, 'all 80 are stored');
  assert.equal(big.at(-1), quilt(t, q.id).patches.at(-1)!.patch, 'the newest is last');
  assert.equal(big[0], quilt(t, q.id).patches[80 - 64].patch, 'the view is the newest 64');
});

test('invalid patch rewards are dropped; unknown kinds are ignored; never more patches than questions', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  const r = stitched(1);
  r.rewards!.push(
    r.rewards![0],
    { id: 'a', kind: 'patch', patch: '<img src=x>', at: 'x' } as any,
    { id: 'b', kind: 'patch', patch: '', at: 'x' } as any,
    { id: 'c', kind: 'patch', patch: 'p' + 'x'.repeat(40), at: 'x' } as any,
    { id: 'd', kind: 'patch', patch: 'dots-blue' } as any, // no time
    { id: '', kind: 'patch', patch: 'dots-blue', at: 'x' } as any,
    { id: 'e', kind: 'sticker', patch: 'dots-blue', at: 'x' } as any,
    { id: 'f', kind: 'patch', patch: 42, at: 'x' } as any,
    { id: 'g', kind: 'patch', patch: 'Dots-Blue', at: 'x' } as any, // slugs are lower case
    'dots-blue' as any, null as any,
  );
  addSession(s, p.id, r);
  assert.deepEqual(quiltView(s, p.id, Q), { patches: ['gingham-red'] });
  addSession(s, p.id, stitched(5, { questions: 2 }));
  assert.deepEqual(quiltView(s, p.id, Q), { patches: ['gingham-red', 'gingham-red', 'dots-blue'] }, 'two boards, two patches');
  const notList = rec({ game: Q, skill: QSKILL }) as any; notList.rewards = { id: 'x', kind: 'patch' };
  assert.ok(addSession(s, p.id, notList), 'a broken rewards field never blocks saving the session');
});

test('quilt is capped: the oldest fold into a count, the newest stay, the pattern can continue', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  const total = QUILT_MAX_PATCHES + 15;
  for (let k = 0; k < total; k += 5) addSession(s, p.id, stitched(5, { from: k }));
  const q = quilt(s, p.id);
  assert.equal(q.patches.length, QUILT_MAX_PATCHES);
  assert.equal(q.folded, 15, 'the total stays exact: kept plus folded');
  assert.equal(q.patches.at(-1)!.patch, SLUGS[(total - 1) % SLUGS.length], 'the newest patch is still the last');
  assert.equal(quiltView(s, p.id, Q)!.patches.length, QUILT_VIEW_PATCHES);
  assert.deepEqual(parseStore(JSON.stringify(s)).quilts[p.id][Q], q, 'survives a load and save');
});

test('quilts are per child and per game; deleting a child deletes their quilt', () => {
  const s = emptyStore(); const p = ensureProfile(s); const q = createProfile(s)!;
  addSession(s, p.id, stitched(1));
  addSession(s, q.id, stitched(2, { from: 1 }));
  addSession(s, q.id, stitched(1, { from: 2, game: 'memory-match-k' }));
  assert.deepEqual(quiltView(s, q.id, Q), { patches: ['dots-blue', 'stripe-green'] });
  assert.deepEqual(quiltView(s, q.id, 'memory-match-k'), { patches: ['stripe-green'] });
  assert.deepEqual(quiltView(s, p.id, Q), { patches: ['gingham-red'] });
  deleteProfile(s, p.id);
  assert.equal(s.quilts[p.id], undefined);
  assert.deepEqual(quiltView(s, q.id, Q), { patches: ['dots-blue', 'stripe-green'] });
});

test('a quilt with a newer sub-schema is kept untouched, never written to and not shown', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  const future = { v: 2, squares: [{ any: 'thing' }] };
  (s.quilts as any)[p.id] = { [Q]: future };
  addSession(s, p.id, stitched(2, { misses: 1 }));
  assert.deepEqual(s.quilts[p.id][Q], future);
  assert.equal(quiltView(s, p.id, Q), undefined);
  assert.equal(s.sessions.length, 1, 'the session itself is still saved');
  assert.equal(s.sessions[0].misses, 1, 'and keeps its facts');
  assert.deepEqual(parseStore(JSON.stringify(s)).quilts[p.id][Q], future, 'survives a load and save');
  assert.equal(hostInitFor(s, s.profiles[p.id], Q, 'quilt').quilt, undefined, 'HostInit sends no quilt it cannot read');
});

test('a store written before quilts existed loads, gets an empty quilts field and keeps schema 1', () => {
  const doc = {
    schema: 1, profiles: { p_a: { id: 'p_a', avatar: 'fox', color: 'orange', createdAt: 'x' } }, activeProfile: 'p_a',
    sessions: [{ ...rec(), profile: 'p_a' }], gardens: {}, walls: { p_a: { [W]: { v: 1, words: [{ wordId: 'w-cat', at: 'x', session: 's' }] } } },
  };
  const { data } = fakeStorage({ [KEY]: JSON.stringify(doc) });
  const s = load();
  assert.deepEqual(s.quilts, {});
  assert.equal(s.readOnly, undefined);
  update(st => addSession(st, 'p_a', stitched(2)));
  const saved = JSON.parse(data.get(KEY)!);
  assert.equal(saved.schema, 1, 'top-level schema stays 1');
  assert.deepEqual(saved.quilts.p_a[Q].patches.map((x: any) => x.patch), ['gingham-red', 'dots-blue']);
  assert.deepEqual(saved.walls, doc.walls, 'walls untouched');
  for (const bad of ['x', 7, [], null]) assert.deepEqual(parseStore(JSON.stringify({ ...doc, quilts: bad })).quilts, {});
});

test('corrupt quilt data never crashes saving or HostInit', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  (s.quilts as any)[p.id] = 'broken';
  assert.ok(addSession(s, p.id, stitched(1)));
  assert.deepEqual(quiltView(s, p.id, Q), { patches: ['gingham-red'] });
  (s.quilts as any)[p.id][Q].patches.push(null, { patch: 7 }, { patch: '<b>' });
  assert.deepEqual(quiltView(s, p.id, Q), { patches: ['gingham-red'] }, 'junk entries are not shown');
  addSession(s, p.id, stitched(1, { from: 1 }));
  assert.deepEqual(quiltView(s, p.id, Q), { patches: ['gingham-red', 'dots-blue'] });
  for (const bad of ['x', 3, null, { patches: 'nope' }]) {
    (s.quilts as any)[p.id][Q] = bad; // no `v`: corrupt, not newer, so a fresh quilt replaces it
    assert.ok(addSession(s, p.id, stitched(1, { from: 2 })));
    assert.deepEqual(quiltView(s, p.id, Q), { patches: ['stripe-green'] }, JSON.stringify(bad));
  }
});

test('gardens, walls and quilts side by side: each game feeds only its own reward', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  addSession(s, p.id, played(2));
  addSession(s, p.id, spelled(['w-cat']));
  addSession(s, p.id, stitched(3));
  const mixed = rec({ game: Q, skill: QSKILL, questions: 4 }); // one list with all kinds: each goes to its own place
  mixed.rewards = [
    { id: mixed.id + '-0', kind: 'patch', patch: 'dots-blue', at: 'x' },
    { id: mixed.id + '-1', kind: 'word', wordId: 'w-sun', at: 'x' },
    { id: mixed.id + '-2', kind: 'garden', species: 'tulip', at: 'x' },
  ] as any;
  addSession(s, p.id, mixed);
  const back = parseStore(JSON.stringify(s));
  assert.deepEqual(quiltView(back, p.id, Q), { patches: ['gingham-red', 'dots-blue', 'stripe-green', 'dots-blue'] });
  assert.deepEqual(wallView(back, p.id, W), { words: ['w-cat'] }, 'the word game keeps its own wall');
  assert.deepEqual(wallView(back, p.id, Q), { words: ['w-sun'] }, 'a word reward inside a quilt record goes to that game\'s wall');
  assert.equal(gardenView(back, p.id, G)!.total, 2, 'the addition garden is untouched');
  assert.equal(gardenView(back, p.id, Q)!.total, 1, 'a garden reward inside a quilt record goes to that game\'s garden');
  assert.equal(back.quilts[p.id][G], undefined, 'the garden game has no quilt');
  assert.equal(back.quilts[p.id][W], undefined, 'the word game has no quilt');
  deleteProfile(back, p.id);
  assert.deepEqual([back.quilts, back.walls, back.gardens, back.sessions], [{}, {}, {}, []]);
});

test('old tab saved patch rewards inside a session: next load moves them onto the quilt', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  const r = stitched(3);
  s.sessions.push({ ...r, profile: p.id } as any);
  const back = parseStore(JSON.stringify(s));
  assert.deepEqual(quiltView(back, p.id, Q), { patches: ['gingham-red', 'dots-blue', 'stripe-green'] });
  assert.equal('rewards' in back.sessions[0], false);
  assert.equal(back.sessions[0].misses, 0, 'misses survive the move');
  assert.equal(parseStore(JSON.stringify(back)).quilts[p.id][Q].patches.length, 3, 'idempotent');
});

test('HostInit: quilt games get a quilt, nobody else does; never a profile id', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  addSession(s, p.id, played(2));
  addSession(s, p.id, spelled(['w-cat']));
  addSession(s, p.id, stitched(3, { levelEnd: 4, missed: ['q-3'] }));
  const quiltInit = hostInitFor(s, p, Q, 'quilt');
  assert.deepEqual(Object.keys(quiltInit).sort(), ['avatar', 'color', 'practiceItems', 'quilt', 'settings', 'startLevel']);
  assert.deepEqual(quiltInit.quilt, { patches: ['gingham-red', 'dots-blue', 'stripe-green'] });
  assert.equal(quiltInit.startLevel, 3);
  assert.deepEqual(quiltInit.practiceItems, ['q-3']);
  assert.equal(hostInitFor(emptyStore(), p, Q, 'quilt').quilt!.patches.length, 0, 'a new child gets an empty quilt');
  assert.equal(hostInitFor(s, p, Q, 'garden').quilt, undefined, 'the catalog reward decides, not the game id');
  for (const other of [hostInitFor(s, p, G, 'garden'), hostInitFor(s, p, W, 'wall'), hostInitFor(s, p, 'subtraction-grade-1', 'lights')])
    assert.equal('quilt' in other, false);
  assert.doesNotMatch(JSON.stringify(quiltInit), /p_/);
});

test('misses never turn into a parent tip (a memory miss has no kind)', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  for (let i = 0; i < 4; i++) addSession(s, p.id, stitched(1, { misses: 9, mistakes: {} }));
  assert.equal(mistakeTip(s, p.id, QSKILL), null);
});

// ---------- HostInit (what player.ts sends) ----------

test('HostInit: garden games get a garden, wall games a wall, Pond Hop neither; never a profile id', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  addSession(s, p.id, played(2));
  addSession(s, p.id, spelled(['w-cat', 'w-dog'], { levelEnd: 3, missed: ['w-dog'] }));
  const garden = hostInitFor(s, p, G, 'garden');
  assert.deepEqual(Object.keys(garden).sort(), ['avatar', 'color', 'garden', 'practiceItems', 'settings', 'startLevel']);
  assert.equal(garden.garden!.total, 2);
  const pond = hostInitFor(s, p, 'subtraction-grade-1', 'lights');
  assert.deepEqual(Object.keys(pond).sort(), ['avatar', 'color', 'practiceItems', 'settings', 'startLevel']);
  const word = hostInitFor(s, p, W, 'wall');
  assert.deepEqual(Object.keys(word).sort(), ['avatar', 'color', 'practiceItems', 'settings', 'startLevel', 'wall']);
  assert.deepEqual(word.wall, { words: ['w-cat', 'w-dog'] });
  assert.equal(word.startLevel, 2);
  assert.deepEqual(word.practiceItems, ['w-dog']);
  assert.equal(hostInitFor(emptyStore(), p, W, 'wall').wall!.words.length, 0, 'a new child gets an empty wall');
  assert.equal(hostInitFor(s, p, W, 'garden').wall, undefined, 'the catalog reward decides, not the game id');
  for (const m of [garden, pond, word]) assert.doesNotMatch(JSON.stringify(m), /p_/);
});

// ---------- Parent tips for letter mistakes ----------

test('letter mistake tips: one friendly tip per kind, only once it repeats', () => {
  const tips: Record<string, RegExp> = {
    'letter-order': /order/, 'wrong-vowel': /vowel|middle sound/, 'look-alike': /look alike/, 'wrong-letter': /sound/,
  };
  for (const [kind, re] of Object.entries(tips)) {
    const s = emptyStore(); const p = ensureProfile(s);
    addSession(s, p.id, spelled(['w-cat'], { mistakes: { [kind]: 2 } as any }));
    assert.equal(mistakeTip(s, p.id, WSKILL), null, `${kind}: not yet`);
    addSession(s, p.id, spelled(['w-dog'], { mistakes: { [kind]: 1 } as any }));
    const tip = mistakeTip(s, p.id, WSKILL)!;
    assert.match(tip, re, kind);
    assert.ok(tip.length < 170, `${kind}: short`);
    assert.doesNotMatch(tip, /\u2014|wrong|bad|fail|careless|lazy|should have/i, `${kind}: friendly, no blame, no em dash`);
  }
});

test('the most frequent letter mistake wins; unknown kinds never produce a tip or a crash', () => {
  const s = emptyStore(); const p = ensureProfile(s);
  addSession(s, p.id, spelled(['w-cat'], { mistakes: { 'look-alike': 3, 'letter-order': 1 } as any }));
  assert.match(mistakeTip(s, p.id, WSKILL)!, /look alike/);
  const s2 = emptyStore(); const q = ensureProfile(s2);
  addSession(s2, q.id, spelled(['w-cat'], { mistakes: { 'future-kind': 9 } as any }));
  assert.equal(mistakeTip(s2, q.id, WSKILL), null);
  assert.equal(mistakeTip(s2, q.id, 'math.addition.within-20'), null, 'math tips stay per skill');
});
