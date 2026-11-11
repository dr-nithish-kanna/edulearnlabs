# <GAME NAME> (EduLearnLabs game)

One educational mini-game for EduLearnLabs. Product rules live in the main repo (dr-nithish-kanna/edu-learn-labs):
`CLAUDE.md`, `planning/decisions.md` and `planning/framework-spec.md`.
Universal game rules are in `GAME_RULES.md` in this repo. Follow every one of them.

## Game card (fill in, must match game.json)
- Game ID (URL slug, never changes):
- Friendly title (on screen):
- Keyword title (website URL and H1, for example "Addition for Grade 1"):
- Grade:
- Subject:
- Topic:
- Skill ID (from main repo `content/skills.json`):
- Mechanic:
- Difficulty levels (1 to 5):
- Session end rule (maxQuestions, maxSeconds):

## How to work with me (owner)
- Teach as you build. Explain why, not only what. No blind building.
- Critique my ideas and suggest better options.
- Recommend Opus before architecture choices, hard performance work, or anything costly to undo.
  Sonnet is fine for routine work: content JSON, styling, small fixes.
- No em dashes in docs or copy. Do not commit or push unless I ask.

## Tech
- Stack: plain TypeScript with DOM, CSS and SVG, built with Vite. No game engine.
- Shared library: ell-kit, pinned to a tag in package.json (for example `github:<owner>/edulearnlabs-kit#v1.0.0`).
  Upgrade it on purpose, never with a loose version range. Do not copy kit code into this repo; fix the kit instead.
- A canvas effects layer, Lottie or Rive only after Play, and only with measured size written in the README.
- Visual style: follow the EduLearnLabs style guide and use the shared mascot. Game colors go in `src/theme.css`.

## Repo layout
```
game.json                  taxonomy, session rules, levels (content)
src/main.ts                starts ell-kit with the mechanic and theme
src/theme.css              colors for this game (from the style guide)
assets/img/                sprite atlases, 512 px max per sprite
assets/audio/              voice lines (from "say" fields) and one sound sprite
public/poster.webp         poster for the website game page
scripts/check-size.mjs     fails the build if over budget
tests/smoke.spec.ts        Playwright: plays one full session on the throttled profile
README.md                  game card, size and load table, any budget exception with reason
```
Build output: `dist/` with the game and `asset-manifest.json` (files the website preloads).
SEO text for the game page lives in the website repo, not here.

## Commands (fill in when the repo is set up)
- Dev: `npm run dev` (runs with the ell-kit fake host, messages logged to the console)
- Build: `npm run build`
- Size check: `npm run size`
- Smoke test: `npm run test:e2e -- --trace off`

## Done means
- Plays a full session with no console errors in dev mode and inside the website iframe.
- Content validates against the mechanic's JSON Schema.
- Size check passes, or the README explains the exception.
- Smoke test passes on the throttled profile. Size and load time recorded in the README.
- Checked against every rule in GAME_RULES.md, including the "Never" list.

## Release
Tag a version (for example `v1.0.0`). The GitHub Action builds and attaches `dist` to the release.
The website pins that version in its `content/games.json`.

## Daily log in Notion (applies to all my repos)
If Notion tools are connected, log my work and learning in "Nithish Kanna's Dashboard" without being asked.
Never put card text, book content or secrets in Notion. If Notion isn't connected, say so in one line and carry on.
- "Plan my day" (or first session of a day): ask me 3-4 short questions, then add today's tasks to my Notion Tasks
  database. Fetch the database schema first and use its exact property names.
- "End of day": check which of today's tasks are done, show my progress warmly and honestly, log anything unplanned,
  and carry unfinished tasks to tomorrow.
- Never mark a task Done for me. I do that.
