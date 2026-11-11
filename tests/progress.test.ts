import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  addSession, bestStars, createProfile, deleteProfile, emptyStore, ensureProfile, mastery, MAX_PROFILES,
  mistakeTip, parseStore, practiceItems, startLevel, type SessionRecord,
} from '../src/scripts/progress.ts';

let n = 0;
const rec = (o: Partial<SessionRecord> = {}): SessionRecord => ({
  id: `s_${++n}`, game: 'addition-grade-1', gameVersion: '1.0.0', skill: 'math.addition.within-20',
  startedAt: '2026-11-11T10:00:00Z', durationSec: 120, questions: 10, firstTry: 8, levelStart: 1, levelEnd: 3,
  maxDifficulty: 3, completed: true, missed: [], mistakes: {}, ...o,
});

test('corrupt or foreign data never crashes, it starts fresh', () => {
  for (const raw of [null, '', '{', '[]', '{"schema":2}', '{"schema":1,"profiles":{},"sessions":"x"}'])
    assert.deepEqual(parseStore(raw).sessions, []);
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
