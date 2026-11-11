# EduLearnLabs

Free, browser-based educational mini-games for kids (Pre-K to Grade 12 planned, MVP is Pre-K to Grade 2).
Subjects: language, math, science, logic and memory. Brand name is **EduLearnLabs** (not "EdLearnLabs").

This repo holds the **website** (Astro, static) and the **planning docs**. Each game lives in its own repo
and is built from the template in `templates/game-repo/`.

Not to be confused with the Nifty Games Studios site (the owner's indie studio, separate repo and brand).

## How to work with me (owner)

- Teach as you build. Explain why, not only what. No blind building. Short explanations, concrete examples.
- Critique my ideas and propose better options. I am open to learning new things.
- Tell me when a task is better done on Opus (see Model guidance).
- I am not strong at marketing. Make sensible marketing, pricing and SEO choices and explain them simply.
- Do not use em dashes in any docs or copy.
- Do not commit or push unless I ask.

## Model guidance

- Sonnet is fine for routine work: new games from the template, question JSON, Astro pages, CSS, SEO copy, small fixes.
- Recommend switching to Opus before: engine choice, shared framework or data schema design, login, subscription
  or child-privacy design, hard performance or build-size debugging, and a review pass before locking any major decision.

## Product decisions (locked)

- Audience: parents and home users first, schools later. Child plays, parent pays.
- Games are 2 to 5 minutes, one micro-skill per game, fully free to play, no login.
- Monetization order: free with no ads at launch, then website-level ads (non-personalized, child-safe)
  at roughly 5k to 10k monthly visitors, then a family subscription that removes ads. Price TBD
  (rough idea: $3.99/month or $29/year, check India pricing and payment providers later).
- Ads and prices live on the website only. Games never render ads, prices or upsells.
  Site reserves ad slots and keeps an ad on/off flag from day one so ads can be enabled with no game changes.
- Progress, stars and mastery badges are stored locally (no login). Use a schema that can sync to a backend later.
- Rewards are light: stars, badges, progress bars. No streaks, leaderboards, loot boxes or failure screens.
- Safety: no chat, no external links in games, no data collected from children, COPPA and GDPR-K friendly.
  No parent gate at MVP (no pricing or external links yet). Add a simple parent gate before pricing, subscription
  or any external link ships. Deleting profiles or data uses hold-to-confirm.
- MVP: 20 games for Pre-K to Grade 2 (8 math, 8 language, 4 logic and memory). See `planning/mvp-games.md`.
  Taxonomy supports all grades from day one. Science comes right after MVP. Grades 3 to 12 stay on the roadmap.

## Engine decision (final, 2026-11-11)

Plain TypeScript with DOM, CSS and SVG for all MVP games, built with Vite, plus one small shared runtime library.
No game engine, no Unity. A canvas library only for games with a real game loop or many moving objects, loaded
after Play. Budgets: before Play 100 KB or less (firm), after Play about 1.5 MB preloaded in the background (can
grow when a game needs it, justified in its README). First load under 5 seconds on an old Chromebook.
Visual direction is "juicy but fair": rich color, motion and audio, no manipulative retention tricks.
Full reasoning, per-mechanic stacks and the yes/no engagement lists are in `planning/decisions.md`.

## Website rules (SEO)

- One page per game with a clean keyword URL, for example `/math-games/addition-for-grade-1`.
- Each game page: one H1, title tag (keyword + age or grade + benefit), meta description, 300 to 600 words of
  real text (what it is, what kids learn, who it is for, how to play, why it helps).
- Category pages (500 to 1000 words) list games and learning goals. Parent and teacher articles link to 2 or 3 games.
- Game loads after the text, with a poster image and lazy loading. No single-page-app, no login wall, no canvas-only pages.
- Must have sitemap.xml, robots.txt, HTTPS, mobile friendly, Core Web Vitals in range (LCP under 2.5s, CLS 0).
- Navigation: max 2 clicks to play, big cards, always a visible back button, audio toggle.

## Game taxonomy

Every game is tagged with: grade, subject, topic, micro-skill, mechanic, difficulty. Reuse mechanics, change content
and difficulty. Do not build new mechanics per grade. Questions are data (JSON), never hardcoded.
Universal game rules are in `templates/game-repo/GAME_RULES.md`.

## Repo layout

- `CLAUDE.md` this file
- `planning/` decisions, framework spec, style guide, MVP list
- `brand/` Hazel the owl (`brand/mascot/owl.svg` is the source of truth) and style previews
- `templates/game-repo/` CLAUDE.md and rules to copy into every new game repo
- Website (Astro 7, static): `src/pages/` pages, `src/layouts/`, `src/components/`, `src/scripts/progress.ts`
  (local progress store), `src/scripts/player.ts` (website side of the game contract), `src/data/` catalog
- `public/play/<game-id>/` built games, copied in with `npm run sync-game -- ../<game-repo>` (pinned by commit)
- `tests/` progress store unit tests (`node --test tests/progress.test.ts`) and the site smoke test
  (`npm run build && npm run test:e2e`)

## Hosting

- Live at `niftygamesstudios.in/edulearnlabs/` as a GitHub Pages project site under the Nifty Games Studios user site.
  `.github/workflows/pages.yml` deploys on every push to `main`. The base path comes from GitHub, so a repo rename
  or a move to our own domain needs no code change.
- Games are served from the same domain at `/play/<game-id>/` (required by the postMessage contract).

## Daily log in Notion (applies to all my repos)

If Notion tools are connected, log my work and learning in "Nithish Kanna's Dashboard" without being asked.
Never put card text, book content or secrets in Notion. If Notion isn't connected, say so in one line and carry on.
- "Plan my day" (or first session of a day): ask me 3-4 short questions, then add today's tasks to my Notion Tasks
  database. Fetch the database schema first and use its exact property names.
- "End of day": check which of today's tasks are done, show my progress warmly and honestly, log anything unplanned,
  and carry unfinished tasks to tomorrow.
- Never mark a task Done for me. I do that.
