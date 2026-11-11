# Decisions log

## Revenue (decided 2026-11-11)
- Launch free, no ads. Build SEO traffic first.
- Turn on website-level, non-personalized ads at about 5k to 10k monthly visitors.
- Family subscription later, removes ads. Price TBD.
- Why changed from "ads from day 1": a new site has almost no traffic so ads earn about nothing, AdSense needs
  content and traffic to approve, and child-directed content limits ad earnings.

## Scope
- All grades in the taxonomy. MVP is 20 games, Pre-K to Grade 2.

## Name
- EduLearnLabs.

## Engine test (to run before committing)
Build one game, Addition for Grade 1, twice:
1. TypeScript + Phaser (4.2.1)
2. Plain HTML, CSS, TypeScript
Optionally compare against an existing Unity build.
Measure: gzipped build size, first load time on throttled network and slow CPU, frames per second on a low-end
device, and how fast Claude Code can build and change it. Pick the lightest option that feels good.
Use Opus for the final decision.

## Open items
- Subscription price and payment provider (India, tax handling).
- Final engine choice after the test.
- Logo and visual style guide.
- Asset plan: Kenney packs, one itch.io pack, AI-generated icons, recolor and reuse, shared asset bank.

## Engine test results (2026-11-11, Addition Grade 1, 10 questions, 3 choices, star result)
Both versions built with Vite and played end to end with no console errors.
Load test: headless Chrome, CPU slowed 4x, network about 1.6 Mbps with 150 ms latency.

| | Plain HTML/CSS/TS | Phaser 4.2.1 |
|---|---|---|
| Raw size | 2.6 KB | 1337.7 KB |
| Gzip | 1.5 KB | 348.4 KB |
| Brotli | 1.2 KB | 277.0 KB |
| Load time (throttled) | about 0.8 s | about 8.2 s |
| FPS (4x CPU) | 62 | 62 |

Notes:
- Phaser's cost is a fixed engine size (about 280 KB brotli), paid by every game page. Unity is typically larger still.
- Not measured: Unity build, audio and sprite assets, drag and drop or animation heavy games.
- Phaser text defaults to a monospace font unless a font is set.
- Test code was throwaway and is not in this repo.

Leaning: plain TypeScript with DOM and CSS (plus SVG or small canvas helpers) for quiz, match, sort, order and memory games.
Add a lighter canvas library only for games that need real animation or dragging. Final decision to be made on Opus.
