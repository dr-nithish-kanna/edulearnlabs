// Local progress store (planning/framework-spec.md, section 4). One localStorage key, one JSON document.
// Facts (sessions) are only ever added. Stars, mastery and start levels are derived, never stored as truth,
// so formulas can change later without losing anyone's progress. Nothing here ever leaves the device.

export const KEY = 'ell:v1';
export const MAX_PROFILES = 12;
const SESSIONS_KEPT = 50; // per profile per game; older ones fold into totals

export type DistractorKind = 'off-by-one' | 'off-by-two' | 'wrong-operation';
/** Word games (slot-build, kit v0.4.0): how a letter tile missed. Recorded at most once per word by the kit. */
export type LetterMistake = 'letter-order' | 'wrong-vowel' | 'look-alike' | 'wrong-letter';
export type MistakeKind = DistractorKind | LetterMistake;

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
  mistakes: Partial<Record<MistakeKind, number>>;
  /** fill-container, slot-build and pair-match games: hints shown this session. Absent in quiz records. */
  hints?: number;
  /** pair-match only (kit v0.5.0): total missed pairs this session. A fact for a parent page, never shown to the child. */
  misses?: number;
  /**
   * Garden games: one seed per solved order (moved into `gardens`). Word wall games: one word card per solved word
   * (moved into `walls`). Quilt games: one patch per finished board (moved into `quilts`). Never stored in the session itself.
   */
  rewards?: (Reward | WordReward | PatchReward)[];
}
/**
 * A stored session never keeps `rewards` (they live in `gardens` and `walls`). It keeps `seeds`, the count of solved orders,
 * because growth needs to know which sessions had at least one, even after old garden items are folded away.
 */
export interface StoredSession extends Omit<SessionRecord, 'rewards'> { profile: string; seeds?: number }
export interface Profile { id: string; avatar: string; color: string; createdAt: string }
export interface Settings { audio: boolean; music: boolean; reducedMotion: boolean }
export interface Totals { sessions: number; questions: number; firstTry: number }

// ---------- Garden types (planning/fill-container-design.md, section 6) ----------

/** What the game reports per solved order. Id is the session id plus the question index. */
export interface Reward { id: string; kind: 'garden'; species: string; at: string }
/** One planted seed. Stage is never stored: it is derived from sessions played (store facts, derive opinions). */
export interface GardenItem {
  id: string; species: string; at: string; session: string;
  /** Sandbox layout, later. 0 to 1, relative to the plot. */
  x?: number; y?: number; movedAt?: string;
}
/** v is the garden's own schema number, so the garden can change shape without touching the top-level schema. */
export interface Garden { v: 1; items: GardenItem[]; meadow: Record<string, number> }
export type GardenStage = 0 | 1 | 2; // seed, sprout, bloom
/** What the game receives in HostInit. Ids, species and stages only: no profile id, no timestamps. */
export interface GardenView {
  total: number;
  items: { id: string; species: string; stage: GardenStage; nextStage: GardenStage }[];
  meadow?: Record<string, number>;
}

// ---------- Word wall types (planning/slot-build-design.md, decision 13) ----------

/** What a word game reports per solved word. Id is the session id plus the question index; wordId is the item id. */
export interface WordReward { id: string; kind: 'word'; wordId: string; at: string }
/** One card on the wall: a fact. `at` is when it was FIRST earned, `session` the session that earned it. */
export interface WallWord { wordId: string; at: string; session: string }
/** v is the wall's own schema number, like the garden's: the wall can change shape without a top-level schema bump. */
export interface Wall { v: 1; words: WallWord[] }
/** What the game receives in HostInit: word ids only, oldest first. No profile id, no timestamps. */
export interface WallView { words: string[] }

// ---------- Quilt types (planning/pair-match-design.md, sections 2.4 and 12; memory-match-design.md, section 7) ----------

/**
 * What a pair-match game reports per finished board. Id is the session id plus the board index. `patch` is a pattern
 * slug from the game's `reward.patches`. Unlike words, the same patch repeats all the time (a quilt has many squares of
 * one pattern), so rewards dedupe by `id`, never by `patch`.
 */
export interface PatchReward { id: string; kind: 'patch'; patch: string; at: string }
/** One square on the quilt: a fact. `id` is the reward id (the dedupe key), `session` the session that earned it. */
export interface QuiltPatch { id: string; patch: string; at: string; session: string }
/**
 * v is the quilt's own schema number, like the garden's and the wall's. `folded` counts the oldest patches that were
 * dropped past the cap, so the child's total stays exact.
 */
export interface Quilt { v: 1; patches: QuiltPatch[]; folded?: number }
/** What the game receives in HostInit: patch slugs only, oldest first, newest 64 at most. No profile id, no times. */
export interface QuiltView { patches: string[] }

export interface Store {
  schema: 1;
  updatedAt: string;
  activeProfile: string | null;
  settings: Settings;
  profiles: Record<string, Profile>;
  sessions: StoredSession[];
  /** Summary of sessions folded out of the list: totals[profile][game] */
  totals: Record<string, Record<string, Totals>>;
  /** gardens[profile][game]. A garden with an unknown (newer) `v` is kept as is and never written to. */
  gardens: Record<string, Record<string, Garden>>;
  /** walls[profile][game]. Same rule as gardens: a wall with an unknown (newer) `v` is kept as is, never written to. */
  walls: Record<string, Record<string, Wall>>;
  /** quilts[profile][game]. Same rule as walls: a quilt with an unknown (newer) `v` is kept as is, never written to. */
  quilts: Record<string, Record<string, Quilt>>;
  /**
   * Set when the saved document has a newer schema than this code understands (an old tab still open after a
   * deploy). The tab still works for this visit, but `save` never writes to storage, so newer data is never lost.
   */
  readOnly?: true;
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
  settings: { audio: true, music: true, reducedMotion: false }, profiles: {}, sessions: [], totals: {}, gardens: {},
  walls: {}, quilts: {},
});

export function randomId(prefix: string): string {
  const bytes = new Uint8Array(8);
  globalThis.crypto.getRandomValues(bytes);
  return prefix + '_' + Array.from(bytes, b => (b % 36).toString(36)).join('');
}

const isObj = (x: unknown): x is Record<string, any> => !!x && typeof x === 'object' && !Array.isArray(x);

/**
 * Accepts anything (corrupt data, an older schema) and returns a valid store. Never throws.
 * A NEWER schema is not corrupt: it is real data written by newer code. We cannot safely read it (fields may have
 * changed meaning), so we start this tab empty and mark it read-only, and `save` leaves the stored document alone.
 */
export function parseStore(raw: string | null): Store {
  if (!raw) return emptyStore();
  try {
    const d = JSON.parse(raw);
    if (isObj(d) && typeof d.schema === 'number' && d.schema > 1) return { ...emptyStore(), readOnly: true };
    if (!isObj(d) || d.schema !== 1 || !isObj(d.profiles) || !Array.isArray(d.sessions)) return emptyStore();
    const s = emptyStore();
    // Spreading `d` first keeps fields this code does not know (for example `stickers`), so saving writes them back.
    const store: Store = {
      ...s, ...d,
      settings: { ...s.settings, ...d.settings },
      totals: isObj(d.totals) ? d.totals : {},
      gardens: isObj(d.gardens) ? d.gardens : {},
      // Stores saved before word walls existed have no `walls`: an empty default, no schema bump (same as gardens).
      walls: isObj(d.walls) ? d.walls : {},
      // Same for quilts: stores saved before pair-match existed get an empty default, no top-level schema bump.
      quilts: isObj(d.quilts) ? d.quilts : {},
      activeProfile: d.activeProfile && d.profiles[d.activeProfile] ? d.activeProfile : null,
    };
    delete store.readOnly; // only this function decides that, never the stored document
    harvestStrayRewards(store);
    return store;
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
  delete store.gardens[id];
  delete store.walls[id];
  delete store.quilts[id];
  store.sessions = store.sessions.filter(s => s.profile !== id);
  if (store.activeProfile === id) store.activeProfile = Object.keys(store.profiles)[0] ?? null;
}

// ---------- Sessions (facts) ----------

const isRecord = (r: unknown): r is SessionRecord => {
  const x = r as SessionRecord;
  return !!x && typeof x.id === 'string' && typeof x.game === 'string' && typeof x.skill === 'string' &&
    Number.isFinite(x.questions) && Number.isFinite(x.firstTry) && Array.isArray(x.missed);
};

/**
 * Copies only the fields we know. Why: the website decides what child data it keeps. If a future game sends an
 * extra field, it is ignored (protocol rule) instead of being saved without anyone deciding to.
 */
const KNOWN: (keyof SessionRecord)[] = ['id', 'game', 'gameVersion', 'skill', 'startedAt', 'durationSec', 'questions',
  'firstTry', 'levelStart', 'levelEnd', 'maxDifficulty', 'completed', 'missed', 'mistakes'];

/** Adds a finished session. Duplicates (same id) are ignored, which also makes a future sync merge trivial. */
export function addSession(store: Store, profile: string, record: unknown): boolean {
  if (!isRecord(record) || !store.profiles[profile]) return false;
  if (store.sessions.some(s => s.id === record.id)) return false;
  const kept = Object.fromEntries(KNOWN.filter(k => k in record).map(k => [k, record[k]])) as unknown as SessionRecord;
  const stored: StoredSession = { ...kept, missed: record.missed.slice(0, 30), mistakes: isObj(record.mistakes) ? record.mistakes : {}, profile };
  if (Number.isFinite(record.hints)) stored.hints = record.hints;
  if (Number.isFinite(record.misses) && record.misses! >= 0) stored.misses = record.misses;
  // One seed per solved order, and a solved order is a question, so never more seeds than questions.
  const rewards = validRewards(record.rewards).slice(0, Math.max(0, record.questions));
  if (rewards.length) stored.seeds = rewards.length;
  // One card per solved word, so never more cards than questions either. Repeats are fine: the wall dedupes.
  const words = validWordRewards(record.rewards).slice(0, Math.max(0, record.questions));
  // One patch per finished board, and a pair-match question is a board, so never more patches than questions.
  const patches = validPatchRewards(record.rewards).slice(0, Math.max(0, record.questions));
  store.sessions.push(stored);
  const mine = store.sessions.filter(s => s.profile === profile && s.game === record.game);
  for (const old of mine.slice(0, Math.max(0, mine.length - SESSIONS_KEPT))) {
    const t = ((store.totals[profile] ??= {})[old.game] ??= { sessions: 0, questions: 0, firstTry: 0 });
    t.sessions++; t.questions += old.questions; t.firstTry += old.firstTry;
    store.sessions.splice(store.sessions.indexOf(old), 1);
  }
  if (rewards.length) plant(store, profile, record.game, record.id, rewards);
  if (words.length) pinWords(store, profile, record.game, record.id, words);
  if (patches.length) stitch(store, profile, record.game, record.id, patches);
  return true;
}

// ---------- Garden (facts: planted seeds; opinion: their stage) ----------

export const GARDEN_V = 1;
/** Kept per child per game. About 90 bytes each, so 300 is about 27 KB, far inside localStorage limits. */
export const GARDEN_MAX_ITEMS = 300;
/** Newest items sent to the game for the plot. Older ones are drawn as a meadow band. */
export const GARDEN_VIEW_ITEMS = 30;
/**
 * Addition Garden's species, in the fixed cycle the kit uses (game.json `reward.species`). Never random:
 * decisions.md bans variable rewards. The kit picks the species; this copy is for tests and a future garden page.
 */
export const GARDEN_SPECIES = ['sunflower', 'tulip', 'daisy', 'lavender', 'strawberry', 'small-tree'] as const;
/** Species of the next seed: same formula as the kit's speciesFor (design section 6.4). */
export const speciesFor = (species: readonly string[], total: number, solved = 0) =>
  species[((total + solved) % species.length + species.length) % species.length];

const SPECIES_RE = /^[a-z][a-z-]{0,31}$/;
const validRewards = (list: unknown): Reward[] => {
  if (!Array.isArray(list)) return [];
  const seen = new Set<string>();
  return list.filter((r): r is Reward => isObj(r) && r.kind === 'garden' && typeof r.id === 'string' && r.id.length > 0 &&
    r.id.length <= 64 && typeof r.species === 'string' && SPECIES_RE.test(r.species) && typeof r.at === 'string' &&
    !seen.has(r.id) && !!seen.add(r.id));
};

const isGardenV1 = (g: unknown): g is Garden => isObj(g) && g.v === GARDEN_V && Array.isArray(g.items);

/** The garden to write to, or null when a newer garden schema is stored (then we leave it alone). */
function gardenFor(store: Store, profile: string, game: string): Garden | null {
  const byGame = (store.gardens[profile] ??= {});
  const g = (byGame[game] ??= { v: GARDEN_V, items: [], meadow: {} });
  if (!isGardenV1(g)) return null;
  if (!isObj(g.meadow)) g.meadow = {};
  return g;
}

function plant(store: Store, profile: string, game: string, session: string, rewards: Reward[]) {
  const g = gardenFor(store, profile, game);
  if (!g) return;
  const have = new Set(g.items.map(i => i.id));
  for (const r of rewards) {
    if (have.has(r.id)) continue; // merge = union by id, so a repeat never plants twice
    g.items.push({ id: r.id, species: r.species, at: r.at, session });
    have.add(r.id);
  }
  foldGarden(store, profile, game, g);
}

/** Over the cap, the oldest blooms become meadow counts. Total (items plus meadow) never changes. */
function foldGarden(store: Store, profile: string, game: string, g: Garden) {
  let extra = g.items.length - GARDEN_MAX_ITEMS;
  if (extra <= 0) return;
  const stages = stagesOf(store, profile, game, g.items);
  const out = new Set<number>();
  for (let i = 0; i < g.items.length && out.size < extra; i++) if (stages[i] === 2) out.add(i);
  // Safety net: if not enough blooms exist (should not happen), fold the oldest anyway so the cap holds.
  for (let i = 0; i < g.items.length && out.size < extra; i++) out.add(i);
  for (const i of out) g.meadow[g.items[i].species] = (g.meadow[g.items[i].species] ?? 0) + 1;
  g.items = g.items.filter((_, i) => !out.has(i));
}

/** Decision 3: a session helps the garden grow when the child solved at least one order, finished or not. */
const countsForGrowth = (s: StoredSession) => (s.seeds ?? 0) >= 1;

/**
 * Stage per item: how many counting sessions of this game came AFTER the item's session, capped at 2.
 * Only play moves it, never elapsed time, so a child who comes back after a month finds the same garden.
 * "After" means later in the session list (the order they were saved on this device), not a clock comparison,
 * so a wrong device clock cannot freeze or jump the garden. A sync merge must keep the list ordered by startedAt.
 * An item whose session was folded away (50 per game cap) has at least 50 newer sessions, so it is a bloom.
 */
function stagesOf(store: Store, profile: string, game: string, items: GardenItem[]): GardenStage[] {
  const mine = store.sessions.filter(s => s.profile === profile && s.game === game);
  const after = new Map<string, number>(); // session id -> counting sessions after it
  let n = 0;
  for (let i = mine.length - 1; i >= 0; i--) { after.set(mine[i].id, n); if (countsForGrowth(mine[i])) n++; }
  return items.map(it => {
    const k = after.get(it.session);
    return (k === undefined ? 2 : Math.min(2, k)) as GardenStage;
  });
}

/**
 * The garden as the game sees it. `nextStage` is what each stage becomes if this coming session counts: the website
 * owns the growth rule, the kit only animates stage to nextStage. Items are newest first (the kit shows the start).
 * Returns undefined when the stored garden has a newer schema than this code knows.
 */
export function gardenView(store: Store, profile: string, game: string): GardenView | undefined {
  const g = store.gardens[profile]?.[game];
  if (g === undefined) return { total: 0, items: [] };
  if (!isGardenV1(g)) return undefined;
  const stages = stagesOf(store, profile, game, g.items);
  const meadow: Record<string, number> = { ...(isObj(g.meadow) ? g.meadow : {}) };
  const cut = Math.max(0, g.items.length - GARDEN_VIEW_ITEMS);
  // Older than the newest 30: summed into the meadow band so the plot stays readable.
  for (const it of g.items.slice(0, cut)) meadow[it.species] = (meadow[it.species] ?? 0) + 1;
  const items = g.items.slice(cut).map((it, i) => {
    const stage = stages[cut + i];
    return { id: it.id, species: it.species, stage, nextStage: Math.min(2, stage + 1) as GardenStage };
  }).reverse();
  const total = g.items.length + Object.values(isObj(g.meadow) ? g.meadow : {}).reduce((a, b) => a + (Number(b) || 0), 0);
  return Object.keys(meadow).length ? { total, items, meadow } : { total, items };
}

/**
 * An old tab (code from before gardens) saves sessions with `rewards` still inside. On the next load, move them
 * into the garden so those seeds are not lost, and strip them from the session like a fresh save would.
 */
function harvestStrayRewards(store: Store) {
  for (const s of store.sessions as (StoredSession & { rewards?: unknown })[]) {
    if (!isObj(s) || !('rewards' in s)) continue;
    const rewards = validRewards(s.rewards).slice(0, Math.max(0, s.questions));
    const words = validWordRewards(s.rewards).slice(0, Math.max(0, s.questions));
    const patches = validPatchRewards(s.rewards).slice(0, Math.max(0, s.questions));
    delete s.rewards;
    if (!store.profiles[s.profile]) continue;
    if (rewards.length) { s.seeds = rewards.length; plant(store, s.profile, s.game, s.id, rewards); }
    if (words.length) pinWords(store, s.profile, s.game, s.id, words);
    if (patches.length) stitch(store, s.profile, s.game, s.id, patches);
  }
}

// ---------- Word wall (facts: which words, first earned when; the game draws the shelf) ----------

export const WALL_V = 1;
/**
 * Cards kept per child per game. A word game's bank is small (Letter Workshop has about 40 words) and a word counts
 * once, so a real child never gets near this. It only bounds storage if a buggy game sends made-up ids.
 * About 70 bytes a card, so 200 is about 14 KB.
 */
export const WALL_MAX_WORDS = 200;

/** Item ids like "w-cat". Strict on purpose: ids go back to the game and may be shown on a parent page later. */
const WORD_ID_RE = /^[A-Za-z0-9][A-Za-z0-9_-]{0,47}$/;
const validWordRewards = (list: unknown): WordReward[] => {
  if (!Array.isArray(list)) return [];
  const seen = new Set<string>();
  return list.filter((r): r is WordReward => isObj(r) && r.kind === 'word' && typeof r.id === 'string' && r.id.length > 0 &&
    r.id.length <= 64 && typeof r.wordId === 'string' && WORD_ID_RE.test(r.wordId) && typeof r.at === 'string' &&
    r.at.length <= 40 && !seen.has(r.id) && !!seen.add(r.id));
};

const isWallV1 = (w: unknown): w is Wall => isObj(w) && w.v === WALL_V && Array.isArray(w.words);
const isWallWord = (x: unknown): x is WallWord => isObj(x) && typeof x.wordId === 'string' && WORD_ID_RE.test(x.wordId);

/** The wall to write to, or null when a newer wall schema is stored (then we leave it alone). */
function wallFor(store: Store, profile: string, game: string): Wall | null {
  if (!isObj(store.walls[profile])) store.walls[profile] = {}; // missing or corrupt; versions live one level down
  const byGame = store.walls[profile];
  // Missing or corrupt (not an object, or no `v` at all): start a fresh wall. Anything with a `v` this code does not
  // know is real data from newer code, so it is left alone.
  const cur: unknown = byGame[game];
  if (!isObj(cur) || !('v' in cur)) byGame[game] = { v: WALL_V, words: [] };
  const w = byGame[game];
  return isWallV1(w) ? w : null;
}

/**
 * Adds cards in the order they were earned. A word already on the wall is skipped, so its first time stays
 * (merge = union by wordId, which also keeps a future sync simple). Order is the order of saving on this device,
 * never the reward clock, so a wrong device clock cannot reshuffle the shelf. Past the cap, new words are not added:
 * cards a child earned are never dropped to make room.
 */
function pinWords(store: Store, profile: string, game: string, session: string, rewards: WordReward[]) {
  const w = wallFor(store, profile, game);
  if (!w) return;
  const have = new Set(w.words.filter(isWallWord).map(x => x.wordId));
  for (const r of rewards) {
    if (have.has(r.wordId)) continue;
    if (w.words.length >= WALL_MAX_WORDS) break;
    w.words.push({ wordId: r.wordId, at: r.at, session });
    have.add(r.wordId);
  }
}

/** The wall as the game sees it (HostInit.wall), oldest first. Undefined when the stored wall has a newer schema. */
export function wallView(store: Store, profile: string, game: string): WallView | undefined {
  const byGame = store.walls[profile];
  const w = isObj(byGame) ? byGame[game] : undefined;
  if (w === undefined) return { words: [] };
  if (!isWallV1(w)) return undefined;
  return { words: w.words.filter(isWallWord).map(x => x.wordId) };
}

// ---------- Quilt (facts: which patch, when; the game draws the quilt) ----------

export const QUILT_V = 1;
/**
 * Patches kept per child per game. One patch per finished board and about 5 boards a session, so 200 is about 40
 * sessions. About 90 bytes a patch, so 200 is about 18 KB. Past the cap the OLDEST fold into `folded` (a count), because
 * the game continues its pattern from the newest patch: freezing the quilt at the cap would freeze the pattern too.
 */
export const QUILT_MAX_PATCHES = 200;
/** Newest patches sent to the game (the kit design recommends at most 64). The mini quilt shows 9, the end screen 16. */
export const QUILT_VIEW_PATCHES = 64;

/** Pattern slugs like "gingham-red". Strict on purpose: slugs go back to the game and may be shown on a parent page. */
const PATCH_RE = /^[a-z][a-z0-9-]{0,31}$/;
const validPatchRewards = (list: unknown): PatchReward[] => {
  if (!Array.isArray(list)) return [];
  const seen = new Set<string>();
  return list.filter((r): r is PatchReward => isObj(r) && r.kind === 'patch' && typeof r.id === 'string' && r.id.length > 0 &&
    r.id.length <= 64 && typeof r.patch === 'string' && PATCH_RE.test(r.patch) && typeof r.at === 'string' &&
    r.at.length <= 40 && !seen.has(r.id) && !!seen.add(r.id));
};

const isQuiltV1 = (q: unknown): q is Quilt => isObj(q) && q.v === QUILT_V && Array.isArray(q.patches);
const isQuiltPatch = (x: unknown): x is QuiltPatch => isObj(x) && typeof x.patch === 'string' && PATCH_RE.test(x.patch);

/** The quilt to write to, or null when a newer quilt schema is stored (then we leave it alone). */
function quiltFor(store: Store, profile: string, game: string): Quilt | null {
  if (!isObj(store.quilts[profile])) store.quilts[profile] = {}; // missing or corrupt; versions live one level down
  const byGame = store.quilts[profile];
  // Missing or corrupt (not an object, or no `v` at all): start a fresh quilt. Anything with a `v` this code does not
  // know is real data from newer code, so it is left alone.
  const cur: unknown = byGame[game];
  if (!isObj(cur) || !('v' in cur)) byGame[game] = { v: QUILT_V, patches: [] };
  const q = byGame[game];
  return isQuiltV1(q) ? q : null;
}

/**
 * Adds patches in the order they were earned. A reward id already on the quilt is skipped (merge = union by id, so a
 * repeated session or a future sync never doubles a patch), but a repeated PATTERN is normal and always kept. Order is
 * the order of saving on this device, never the reward clock, so a wrong device clock cannot reshuffle the quilt.
 */
function stitch(store: Store, profile: string, game: string, session: string, rewards: PatchReward[]) {
  const q = quiltFor(store, profile, game);
  if (!q) return;
  const have = new Set(q.patches.filter(isQuiltPatch).map(x => x.id));
  for (const r of rewards) {
    if (have.has(r.id)) continue;
    q.patches.push({ id: r.id, patch: r.patch, at: r.at, session });
    have.add(r.id);
  }
  const extra = q.patches.length - QUILT_MAX_PATCHES;
  if (extra > 0) {
    q.patches.splice(0, extra);
    q.folded = (Number.isFinite(q.folded) ? q.folded! : 0) + extra;
  }
}

/** The quilt as the game sees it (HostInit.quilt): newest 64 at most, oldest first. Undefined when the stored quilt has a newer schema. */
export function quiltView(store: Store, profile: string, game: string): QuiltView | undefined {
  const byGame = store.quilts[profile];
  const q = isObj(byGame) ? byGame[game] : undefined;
  if (q === undefined) return { patches: [] };
  if (!isQuiltV1(q)) return undefined;
  return { patches: q.patches.filter(isQuiltPatch).map(x => x.patch).slice(-QUILT_VIEW_PATCHES) };
}

// ---------- HostInit (the website side of the contract, kept pure so it can be unit tested) ----------

/**
 * Everything HostInit carries apart from `type` and `protocol`. The catalog `reward` decides the extras:
 * "garden" adds the garden view, "wall" adds the word wall, "quilt" adds the quilt, anything else (Pond Hop's "lights")
 * adds nothing.
 * Never a profile id: the game only learns the avatar and color.
 */
export function hostInitFor(store: Store, p: Profile, game: string, reward: string) {
  const garden = reward === 'garden' ? gardenView(store, p.id, game) : undefined;
  const wall = reward === 'wall' ? wallView(store, p.id, game) : undefined;
  const quilt = reward === 'quilt' ? quiltView(store, p.id, game) : undefined;
  return {
    avatar: avatarOf(p).id, color: p.color,
    startLevel: startLevel(store, p.id, game), practiceItems: practiceItems(store, p.id, game), settings: store.settings,
    ...(garden ? { garden } : {}),
    ...(wall ? { wall } : {}),
    ...(quilt ? { quilt } : {}),
  } as { avatar: string; color: string; startLevel: number; practiceItems: string[]; settings: Settings;
    garden?: GardenView; wall?: WallView; quilt?: QuiltView };
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

/** The wrong-operation tip depends on the topic: in subtraction the slip is adding instead of taking away. */
const WRONG_OPERATION_TIPS = {
  default: 'Sometimes subtracts instead of adding. Point at the + sign and say "plus means put together".',
  subtraction: 'Sometimes adds instead of taking away. Point at the minus sign and say "minus means take away", then count what is left.',
};

/**
 * Word games (kit v0.4.0). Written for a parent of a 5 to 7 year old: these slips are normal at this age, so each tip
 * says what is happening in plain words and gives one thing to try together. Never blames the child.
 */
const LETTER_TIPS: Record<LetterMistake, string> = {
  'letter-order': 'Knows the letters, and sometimes puts them in a different order. Say the word slowly together and point left to right.',
  'wrong-vowel': 'Sometimes mixes up the middle sound, like cut for cat. Stretch the word, "c-a-a-t", and listen for the vowel together.',
  'look-alike': 'Sometimes swaps letters that look alike, like b and d. Very common at this age. Trace the letter and say its sound.',
  'wrong-letter': 'Sometimes picks a letter that is not in the word. Say the word one sound at a time and find each sound together.',
};

/** Plain words for parents: which mistake shows up most for this skill, if any shows up often. */
export function mistakeTip(store: Store, profile: string, skill: string): string | null {
  const counts: Record<string, number> = {};
  for (const s of sessionsOf(store, profile, x => x.skill === skill).slice(-5))
    for (const [k, n] of Object.entries(isObj(s.mistakes) ? s.mistakes : {})) counts[k] = (counts[k] ?? 0) + (Number(n) || 0);
  const [kind, n] = Object.entries(counts).sort((a, b) => b[1] - a[1])[0] ?? [];
  if (!kind || n < 3) return null;
  if (kind === 'wrong-operation' && skill.startsWith('math.subtraction.')) return WRONG_OPERATION_TIPS.subtraction;
  const tips: Record<string, string> = {
    'off-by-one': 'Often lands one away from the answer. Counting on fingers or dots, slowly, helps.',
    'off-by-two': 'Sometimes lands two away from the answer. Practice counting on from the bigger number.',
    'wrong-operation': WRONG_OPERATION_TIPS.default,
    ...LETTER_TIPS,
  };
  // A kind this code does not know yet (a newer game) gets no tip rather than a wrong one.
  return Object.prototype.hasOwnProperty.call(tips, kind) ? tips[kind] : null;
}

// ---------- Persistence ----------

let memory: Store | null = null; // used when storage is blocked (private mode, full, disabled)

export function load(): Store {
  if (memory) return memory;
  try { return parseStore(localStorage.getItem(KEY)); } catch { return (memory = emptyStore()); }
}

export function save(store: Store) {
  // Newer data on disk: keep this tab's changes in memory only, never overwrite what newer code wrote.
  if (store.readOnly) { memory = store; return; }
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
