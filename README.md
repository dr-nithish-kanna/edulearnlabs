# EduLearnLabs website

Free, short learning games for kids, Pre-K to Grade 2. Live at https://niftygamesstudios.in/edulearnlabs/

Static Astro site. Games are separate repos built on ell-kit and copied into `public/play/`.
Planning and rules: `CLAUDE.md` and `planning/`.

## Run

```bash
npm install
npm run dev                         # http://localhost:4321/edulearnlabs/
npm run build                       # static site in dist/
node --test tests/progress.test.ts  # progress store unit tests
npm run test:e2e                    # full family journey on a throttled profile (after build)
```

## Add or update a game

```bash
npm run sync-game -- ../addition-grade-1   # builds the committed game and copies it to public/play/<id>/
```

Then add the game to `src/data/games.json` (if new) and give it a page in `src/pages/<category>/`.

## Deploy

Push to `main`. `.github/workflows/pages.yml` builds and publishes to GitHub Pages.
One-time setup: repo Settings, Pages, Source: GitHub Actions.

## Measured (2026-11-11, throttled: 4x CPU, 1.6 Mbps, 150 ms)

| Page | Load | LCP | CLS |
|---|---|---|---|
| Home | 0.75 s | 0.74 s | 0 |
| Math games | 0.75 s | 0.97 s | 0 |
| Addition for Grade 1 | 0.78 s | 0.76 s | 0 |
