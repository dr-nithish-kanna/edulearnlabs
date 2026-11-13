// Website side of the game contract (planning/framework-spec.md, section 6).
// The website owns all child data. The game gets an avatar, a color, a start level and practice items,
// never a profile id. Only messages from our own iframe on our own origin are trusted.
// Protocol rule: unknown fields are ignored on both sides, so website and games can upgrade in any order.
import { addSession, hostInitFor, load, update } from './progress';
import { pickPlayer, renderProgress } from './site';

const PROTOCOL = 1;

export function initPlayer(root: HTMLElement) {
  const { game = '', src = '', manifest = '', reward = '' } = root.dataset;
  const playBtn = root.querySelector<HTMLButtonElement>('[data-play]')!;
  const overlay = root.querySelector<HTMLElement>('[data-overlay]')!;
  const frameBox = root.querySelector<HTMLElement>('[data-frame]')!;
  let frame: HTMLIFrameElement | null = null;
  let profileId: string | null = null;

  // Preload: once the page is idle, warm the browser cache with the game files so Play feels instant.
  const prefetch = async () => {
    try {
      const res = await fetch(manifest);
      const m = await res.json() as { files: string[] };
      const base = new URL('.', new URL(manifest, location.href));
      for (const f of m.files) {
        const l = document.createElement('link');
        l.rel = 'prefetch';
        l.href = new URL(f, base).href;
        document.head.append(l);
      }
    } catch { /* preloading is a bonus, never an error */ }
  };
  const idle = (cb: () => void) => ('requestIdleCallback' in window ? requestIdleCallback(cb, { timeout: 3000 }) : setTimeout(cb, 1500));
  if (document.readyState === 'complete') idle(prefetch); else addEventListener('load', () => idle(prefetch), { once: true });

  const send = (msg: object) => frame?.contentWindow?.postMessage(msg, location.origin);

  const close = () => {
    frame?.remove();
    frame = null;
    overlay.hidden = true;
    document.documentElement.classList.remove('is-playing');
    renderProgress();
    playBtn.focus();
  };

  const open = async () => {
    const p = await pickPlayer();
    if (!p) return;
    profileId = p.id;
    overlay.hidden = false;
    document.documentElement.classList.add('is-playing');
    frame = document.createElement('iframe');
    frame.src = src;
    frame.title = root.dataset.title ?? 'Game';
    // No popups, no navigating the page: enforces "no external links in games".
    frame.setAttribute('sandbox', 'allow-scripts allow-same-origin');
    frame.allow = 'autoplay; fullscreen';
    frameBox.append(frame);
    frame.focus();
  };

  addEventListener('message', (e: MessageEvent) => {
    if (!frame || e.origin !== location.origin || e.source !== frame.contentWindow) return;
    const m = e.data as { type?: string; session?: unknown; protocol?: number };
    switch (m?.type) {
      case 'GameReady': {
        const s = load();
        const p = profileId ? s.profiles[profileId] : null;
        if (!p) return close();
        // The catalog `reward` decides the extras: "garden" adds the garden view, "wall" adds the word wall
        // (word ids, oldest first). Built by a pure function in progress.ts so it is unit tested. Never the profile id.
        send({ type: 'HostInit', protocol: PROTOCOL, ...hostInitFor(s, p, game, reward) });
        break;
      }
      case 'GameCompleted':
        // addSession keeps known fields only, stores `hints`, plants one seed per solved order (garden rewards) and
        // puts one card per new word on the wall (word rewards), under the profile WE chose. The game never says whose
        // rewards they are.
        if (profileId) update(s => addSession(s, profileId!, m.session));
        renderProgress();
        break;
      case 'GameExit':
        close();
        break;
      case 'GameError':
        close();
        root.querySelector<HTMLElement>('[data-error]')!.hidden = false;
        break;
    }
  });

  document.addEventListener('ell:settings', () => send({ type: 'HostSettings', settings: load().settings }));
  playBtn.addEventListener('click', () => void open());
}
