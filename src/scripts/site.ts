// Shared site behavior: the "who's playing" picker, the header player chip, the sound toggle and progress widgets.
import {
  avatarOf, bestStars, createProfile, ensureProfile, load, mastery, MAX_PROFILES, STAGES, update,
  type Profile, type Store,
} from './progress';

const $ = <T extends Element>(sel: string, root: ParentNode = document) => root.querySelector<T>(sel);
const $$ = <T extends Element>(sel: string, root: ParentNode = document) => [...root.querySelectorAll<T>(sel)];

export function chip(p: Profile): string {
  const a = avatarOf(p);
  return `<span class="avatar avatar--${p.color}" aria-hidden="true">${a.emoji}</span>`;
}

/** Re-draws every element that shows progress. Safe to call any time (after a game, after switching player). */
export function renderProgress(store: Store = load()) {
  const p = store.activeProfile ? store.profiles[store.activeProfile] : null;
  for (const el of $$<HTMLElement>('[data-player-chip]')) {
    el.innerHTML = p ? `${chip(p)}<span class="sr-only">Playing as ${avatarOf(p).name}. Change player</span>` : '';
    // visibility, not display: the chip's space is reserved from the first paint, so nothing moves when it appears.
    el.style.visibility = p ? 'visible' : 'hidden';
  }
  for (const el of $$<HTMLElement>('[data-progress]')) {
    const { game = '', skill = '', top = '5' } = el.dataset;
    if (!p) { el.hidden = true; continue; }
    const stage = STAGES[mastery(store, p.id, skill, Number(top))];
    const stars = bestStars(store, p.id, game);
    el.hidden = false;
    el.innerHTML = `${chip(p)}<span class="progress-plant" title="${stage.label}">${stage.plant}</span>` +
      `<span><strong>${stage.label}</strong> <span class="muted">in this skill</span></span>` +
      `<span class="progress-stars" aria-label="Best: ${stars} of 3 stars">${'★'.repeat(stars)}<span class="muted">${'★'.repeat(3 - stars)}</span></span>`;
  }
  const sound = load().settings.audio;
  for (const b of $$<HTMLButtonElement>('[data-sound-toggle]')) {
    b.setAttribute('aria-pressed', String(sound));
    b.dataset.on = String(sound);
    b.title = sound ? 'Sound on' : 'Sound off';
  }
}

export function setSound(on: boolean) {
  update(s => { s.settings.audio = on; });
  renderProgress();
  document.dispatchEvent(new CustomEvent('ell:settings'));
}

/**
 * "Who's playing?" Shown before Play when there are 2 or more players. With one player it is skipped,
 * keeping "max 2 clicks to play". Resolves with the chosen profile, or null if closed.
 */
export function pickPlayer(force = false): Promise<Profile | null> {
  const me = update(ensureProfile);
  if (!force && Object.keys(load().profiles).length < 2) return Promise.resolve(me);
  const dlg = $<HTMLDialogElement>('#player-picker')!;
  const grid = $<HTMLElement>('[data-picker-grid]', dlg)!;
  return new Promise(resolve => {
    const draw = () => {
      const s = load();
      grid.innerHTML = Object.values(s.profiles).map(p =>
        `<button class="pick" data-id="${p.id}" aria-label="${avatarOf(p).name}">${chip(p)}</button>`).join('') +
        (Object.keys(s.profiles).length < MAX_PROFILES ? `<button class="pick pick--add" data-add aria-label="Add a player"><span class="avatar">+</span></button>` : '');
    };
    draw();
    const onClick = (e: Event) => {
      const t = (e.target as HTMLElement).closest('button');
      if (!t) return;
      if (t.hasAttribute('data-add')) { update(s => createProfile(s)); draw(); return; }
      if (t.dataset.id) { update(s => { s.activeProfile = t.dataset.id!; }); finish(load().profiles[t.dataset.id] ?? null); }
    };
    const finish = (p: Profile | null) => {
      grid.removeEventListener('click', onClick);
      dlg.removeEventListener('close', onClose);
      if (dlg.open) dlg.close();
      renderProgress();
      resolve(p);
    };
    const onClose = () => finish(null);
    grid.addEventListener('click', onClick);
    dlg.addEventListener('close', onClose);
    dlg.showModal();
  });
}

export function initSite() {
  renderProgress();
  for (const b of $$<HTMLButtonElement>('[data-sound-toggle]')) b.addEventListener('click', () => setSound(!load().settings.audio));
  for (const b of $$<HTMLButtonElement>('[data-player-chip]')) b.addEventListener('click', () => void pickPlayer(true));
  // Another tab changed progress: redraw.
  addEventListener('storage', e => { if (e.key === 'ell:v1') renderProgress(); });
}
