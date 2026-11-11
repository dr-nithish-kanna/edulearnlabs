// Local progress store (planning/framework-spec.md, section 4). One localStorage key, one JSON document.
// Facts (sessions) are only ever added. Stars, mastery and start levels are derived, never stored as truth,
// so formulas can change later without losing anyone's progress. Nothing here ever leaves the device.

export const KEY = 'ell:v1';
export const MAX_PROFILES = 12;
const SESSIONS_KEPT = 50; // per profile per game; older ones fold into totals

export type DistractorKind = 'off-by-one' | 'off-by-two' | 'wrong-operation';

export interface SessionRecord {
  id: string;
  game: string;
  gameVersion: string;
  skill: string;
  startedAt: string;
  durationSec: number;
  questions: number;
  firstTry: number;
  levelStart: number;
  levelEnd: number;
  maxDifficulty: number;
  completed: boolean;
  missed: string[];
  mistakes: Partial<Record<DistractorKind, number>>;
}
export interface StoredSession extends SessionRecord { profile: string }
export interface Profile { id: string; avatar: string; color: string; createdAt: string }
export interface Settings { audio: boolean; music: boolean; reducedMotion: boolean }
export interface Totals { sessions: number; questions: number; firstTry: number }

export interface Store {
  schema: 1;
  updatedAt: string;
  activeProfile: string | null;
  settings: Settings;
  profiles: Record<string, Profile>;
  sessions: StoredSession[];
  /** Summary of sessions folded out of the list: totals[profile][game] */
  totals: Record<string, Record<string, Totals>>;
}

export const AVATARS = [
  { id: 'fox', emoji: '🦊', name: 'Fox' }, { id: 'bear', emoji: '🐻', name: 'Bear' },
  { id: 'panda', emoji: '🐼', name: 'Panda' }, { id: 'rabbit', emoji: '🐰', name: 'Bunny' },
  { id: 'tiger', emoji: '🐯', name: 'Tiger' }, { id: 'frog', emoji: '🐸', name: 'Frog' },
  { id: 'koala', emoji: '🐨', name: 'Koala' }, { id: 'lion', emoji: '🦁', name: 'Lion' },
  { id: 'penguin', emoji: '🐧', name: 'Penguin' }, { id: 'monkey', emoji: '🐵', name: 'Monkey' },
  { id: 'unicorn', emoji: '🦄', name: 'Unicorn' }, { id: 'turtle', emoji: '🐢', name: 'Turtle' },
] as const;
export const COLORS = ['orange', 'teal', 'pink', 'sky', 'sun', 'leaf'] as const;

export const emptyStore = (): Store => ({
  schema: 1, updatedAt: new Date().toISOString(), activeProfile: null,
  settings: { audio: true, music: true, reducedMotion: false }, profiles: {}, sessions: [], totals: {},
});

export function randomId(prefix: string): string {
  const bytes = new Uint8Array(8);
  globalThis.crypto.getRandomValues(bytes);
  return prefix + '_' + Array.from(bytes, b => (b % 36).toString(36)).join('');
}

/** Accepts anything (corrupt data, an older schema) and returns a valid store. Never throws. */
export function parseStore(raw: string | null): Store {
  if (!raw) return emptyStore();
  try {
    const d = JSON.parse(raw);
    if (!d || d.schema !== 1 || typeof d.profiles !== 'object' || !Array.isArray(d.sessions)) return emptyStore();
    const s = emptyStore();
    return {
      ...s, ...d,
      settings: { ...s.settings, ...d.settings },
      totals: d.totals ?? {},
      activeProfile: d.activeProfile && d.profiles[d.activeProfile] ? d.activeProfile : null,
    };
  } catch {
    return emptyStore();
  }
}

// ---------- Profiles ----------

export function createProfile(store: Store, avatar?: string, color?: string): Profile | null {
  if (Object.keys(store.profiles).length >= MAX_PROFILES) return null;
  const used = new Set(Object.values(store.profiles).map(p => p.avatar));
  const free = AVATARS.filter(a => !used.has(a.id));
  const pick = avatar ?? (free.length ? free : AVATARS)[Math.floor(Math.random() * (free.length || AVATARS.length))].id;
  const p: Profile = {
    id: randomId('p'), avatar: pick,
    color: color ?? COLORS[Object.keys(store.profiles).length % COLORS.length],
    createdAt: new Date().toISOString(),
  };
  store.profiles[p.id] = p;
  store.activeProfile ??= p.id;
  return p;
}

/** First visit: make one profile so a child can play straight away. */
export function ensureProfile(store: Store): Profile {
  if (store.activeProfile && store.profiles[store.activeProfile]) return store.profiles[store.activeProfile];
  const first = Object.values(store.profiles)[0];
  if (first) { store.activeProfile = first.id; return first; }
  return createProfile(store)!;
}

export function deleteProfile(store: Store, id: string) {
  delete store.profiles[id];
  delete store.totals[id];
  store.sessions = store.sessions.filter(s => s.profile !== id);
  if (store.activeProfile === id) store.activeProfile = Object.keys(store.profiles)[0] ?? null;
}

// ---------- Sessions (facts) ----------

const isRecord = (r: unknown): r is SessionRecord => {
  const x = r as SessionRecord;
  return !!x && typeof x.id === 'string' && typeof x.game === 'string' && typeof x.skill === 'string' &&
    Number.isFinite(x.questions) && Number.isFinite(x.firstTry) && Array.isArray(x.missed);
};

/** Adds a finished session. Duplicates (same id) are ignored, which also makes a future sync merge trivial. */
export function addSession(store: Store, profile: string, record: unknown): boolean {
  if (!isRecord(record) || !store.profiles[profile]) return false;
  if (store.sessions.some(s => s.id === record.id)) return false;
  store.sessions.push({ ...record, missed: record.missed.slice(0, 30), profile });
  const mine = store.sessions.filter(s => s.profile === profile && s.game === record.game);
  for (const old of mine.slice(0, Math.max(0, mine.length - SESSIONS_KEPT))) {
    const t = ((store.totals[profile] ??= {})[old.game] ??= { sessions: 0, questions: 0, firstTry: 0 });
    t.sessions++; t.questions += old.questions; t.firstTry += old.firstTry;
    store.sessions.splice(store.sessions.indexOf(old), 1);
  }
  return true;
}

// ---------- Derived values (opinions) ----------

export const starsFor = (r: Pick<SessionRecord, 'questions' | 'firstTry'>): 1 | 2 | 3 => {
  const pct = r.questions ? r.firstTry / r.questions : 0;
  return pct >= 0.9 ? 3 : pct >= 0.7 ? 2 : 1;
};

const sessionsOf = (store: Store, profile: string, filter: (s: StoredSession) => boolean) =>
  store.sessions.filter(s => s.profile === profile && filter(s));

export type Stage = 'new' | 'practicing' | 'getting' | 'mastered';
export const STAGES: Record<Stage, { plant: string; label: string }> = {
  new: { plant: '🌰', label: 'Seed' },
  practicing: { plant: '🌱', label: 'Sprout' },
  getting: { plant: '🌷', label: 'Bud' },
  mastered: { plant: '🌻', label: 'Flower' },
};

const day = (iso: string) => iso.slice(0, 10);

/**
 * Mastery per skill. "Mastered" needs 2 strong sessions at the top difficulty on different days:
 * the spacing effect. Remembering on another day shows real learning, not just a warm streak.
 * Stages never go down when a child stops playing (no wilting).
 */
export function mastery(store: Store, profile: string, skill: string, topDifficulty: number): Stage {
  const list = sessionsOf(store, profile, s => s.skill === skill && s.questions > 0);
  const folded = Object.values(store.totals[profile] ?? {}).some(t => t.sessions > 0);
  const pct = (s: StoredSession) => s.firstTry / s.questions;
  const topDays = new Set(list.filter(s => s.maxDifficulty >= topDifficulty && pct(s) >= 0.85).map(s => day(s.startedAt)));
  if (topDays.size >= 2) return 'mastered';
  if (list.some(s => s.maxDifficulty >= 3 && pct(s) >= 0.8)) return 'getting';
  return list.length || folded ? 'practicing' : 'new';
}

/** One level below the highest reached last time, so the next session starts with a warm-up success. */
export function startLevel(store: Store, profile: string, game: string): number {
  const last = sessionsOf(store, profile, s => s.game === game).at(-1);
  return last ? Math.max(1, last.levelEnd - 1) : 1;
}

/** Items missed in the last 3 sessions, newest first, at most 5. The game mixes them in for practice. */
export function practiceItems(store: Store, profile: string, game: string): string[] {
  const recent = sessionsOf(store, profile, s => s.game === game).slice(-3).reverse();
  return [...new Set(recent.flatMap(s => s.missed))].slice(0, 5);
}

export function bestStars(store: Store, profile: string, game: string): number {
  return sessionsOf(store, profile, s => s.game === game && s.completed).reduce((m, s) => Math.max(m, starsFor(s)), 0);
}

/** Plain words for parents: which mistake shows up most for this skill, if any shows up often. */
export function mistakeTip(store: Store, profile: string, skill: string): string | null {
  const counts: Partial<Record<DistractorKind, number>> = {};
  for (const s of sessionsOf(store, profile, x => x.skill === skill).slice(-5))
    for (const [k, n] of Object.entries(s.mistakes)) counts[k as DistractorKind] = (counts[k as DistractorKind] ?? 0) + (n ?? 0);
  const [kind, n] = (Object.entries(counts) as [DistractorKind, number][]).sort((a, b) => b[1] - a[1])[0] ?? [];
  if (!kind || n < 3) return null;
  return {
    'off-by-one': 'Often lands one away from the answer. Counting on fingers or dots, slowly, helps.',
    'off-by-two': 'Sometimes lands two away from the answer. Practice counting on from the bigger number.',
    'wrong-operation': 'Sometimes subtracts instead of adding. Point at the + sign and say "plus means put together".',
  }[kind];
}

// ---------- Persistence ----------

let memory: Store | null = null; // used when storage is blocked (private mode, full, disabled)

export function load(): Store {
  if (memory) return memory;
  try { return parseStore(localStorage.getItem(KEY)); } catch { return (memory = emptyStore()); }
}

export function save(store: Store) {
  store.updatedAt = new Date().toISOString();
  try { localStorage.setItem(KEY, JSON.stringify(store)); memory = null; } catch { memory = store; }
}

/** Read, change, write in one step, so two changes never overwrite each other. */
export function update<T>(fn: (s: Store) => T): T {
  const s = load();
  const out = fn(s);
  save(s);
  return out;
}

export function clearAll() {
  memory = null;
  try { localStorage.removeItem(KEY); } catch { /* nothing stored */ }
}

export const avatarOf = (p: Profile) => AVATARS.find(a => a.id === p.avatar) ?? AVATARS[0];
