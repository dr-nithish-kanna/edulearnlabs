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
- ~~Final engine choice after the test.~~ Decided 2026-11-11, see "Engine decision (final)" below.
- ~~Visual style guide.~~ Done 2026-11-11, see `planning/style-guide.md` (Hazel the owl). Logo still open.
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

## Engine decision (final, 2026-11-11)

**Decision: plain TypeScript with DOM, CSS and SVG for every MVP game. No game engine. No Unity.**
One shared runtime library (the framework spec in step 2) is bundled into each game. Vite builds each game.

### What the test showed, and what it did not
The test proves one thing clearly: Phaser costs about 280 KB brotli of fixed engine code before a single
question is drawn. On a slow CPU that code has to be parsed and run, which is why Phaser took about 8 s while
the transfer alone (277 KB at 1.6 Mbps) should take under 2 s. The cost is CPU, not only network, and old
Chromebooks are slow at exactly that.

Gaps in the test (none of them change the decision, but we should know them):
1. **No assets.** The 1.2 KB plain build had no audio, images or fonts. A real game will weigh 50 to 200 KB
   once it has sounds and sprites. The test compared engine overhead, not real game weight.
2. **No real device.** Headless Chrome with 4x CPU slowdown is an estimate. GPU, memory (4 GB Chromebooks)
   and touch were not tested. Run the first real game on a real low-end device or a cheap Android tablet.
3. **One run each.** No variance. Fine for a 10x gap, not fine for small comparisons later.
4. **No drag and drop.** The hardest mechanic for DOM (dragging on touch screens) was not tested.
5. **No audio latency test.** Feedback must land within 0.3 s. Browsers block audio until the first tap.
6. **Cached repeat visits not measured.** If every game shared one cached Phaser file, the 2nd game would be
   cheaper. This does not save Phaser: most visitors arrive from Google on one game page, so the first,
   uncached load is the one that counts for Core Web Vitals and for whether a parent stays.
7. **Unity skipped.** Correctly. Unity WebGL builds start in the megabytes. Not worth measuring.

### Stack per mechanic
| Mechanic | Stack | Notes |
|---|---|---|
| Quiz (tap the answer) | DOM buttons + CSS | Real buttons give keyboard, focus and screen reader support for free. |
| Match (pair items) | DOM + CSS | Tap one, tap the other. Optional drag on top. |
| Sort (into groups) | DOM + Pointer Events | Tap item, tap bin is the default. Drag is an extra, never required. |
| Order (put in sequence) | DOM + Pointer Events | Tap to place in the next slot, tap a slot to remove. |
| Memory (flip cards) | DOM + CSS 3D transform | CSS flip animation runs on the GPU, no JS loop needed. |
| Drag and drop | DOM + Pointer Events + shared drag helper (about 1 to 2 KB) | Do not use the HTML5 drag and drop API: it does not work on touch screens. Always offer tap-tap as well. |
| Number lines, shapes, patterns | Inline SVG | Sharp at any size, tiny, styleable with CSS. |

Animation: CSS transitions and transforms first, Web Animations API second. Both run off the main thread
where possible. Respect `prefers-reduced-motion`.

### When a canvas library is justified
Only when a game needs one of these, and DOM has been tried first:
- many moving objects at once (roughly 50 or more), or a continuous game loop (things fall, fly, collide)
- particle effects that are the point of the game, not decoration
- pixel-level drawing (for example a tracing or painting game)

Order of preference: plain Canvas 2D with a small helper in the shared library, then a renderer-only library
(measure candidates such as PixiJS at that time), then Phaser. Any library must be loaded only after the child
presses Play, so the page text and poster still load fast and the SEO page is unaffected. A game that needs a
library must state its brotli size in its README and justify it.

### When Unity is justified
For this catalog, effectively never. The only case worth revisiting: a later science simulation that needs real
3D and cannot be done with SVG, CSS 3D or a small WebGL library. Even then, try three.js first, and the
5 second first-load rule still applies.

### Budgets (defaults, updated later the same day)
- Before Play (page text, poster, game shell): 100 KB or less. **Firm.** This protects SEO, Core Web Vitals and
  the parent's first impression.
- After Play (art, audio, animation, effects): about 1.5 MB by default, preloaded in the background while the
  parent reads the page, so Play feels instant.
- The after-Play budget **can grow when a game needs it and it is worth it.** The game README must then say what
  the extra weight buys, its size, and the measured load time. Load-time target stays: under 5 s on the throttled profile.

### Why this is the right call (in one line)
Our games are tap-based with 2 to 4 choices. That is what the DOM was built for. An engine would make every
game 100 times heavier to solve a problem these games do not have.

## Visual and engagement direction: "juicy but fair" (approved 2026-11-11)
Visuals, motion and audio are the product for ages 4 to 7. Engagement must also be good for learning and fair to
children and parents.

**Yes:**
- Bright, saturated colors on characters, rewards and celebrations. Calm area around the question itself.
- Juice: springy squash and stretch buttons, character reactions (idle, happy, "hmm, try again"), particle bursts,
  animated end celebration. Respect `prefers-reduced-motion`.
- Smooth drag and drop: item lifts with a shadow, magnetic snap to targets. Tap-tap always available too.
- Audio: every question spoken, sound on every tap, rising pitch on correct answers in a row, soft music, mute toggle.
- Adaptive difficulty that keeps the child in the "just right" zone (the strongest engagement lever).
- Sticker book earned by mastering skills, a companion character that unlocks outfits through learning, varied
  praise lines, surprise celebrations at milestones, a garden that grows when you play and never wilts.
- Clear, happy endings ("Great job, see you next time!").

**No (manipulative design, see Radesky et al. 2022, UK Children's Code standard 13, FTC Epic Games 2022):**
- Streaks or anything that wilts, decays or is lost when a child stops playing.
- Random or variable rewards, loot boxes, mystery boxes.
- Fake timers and countdowns.
- Characters that guilt a child into staying ("Ollie will be sad if you go").
- Autoplay into the next game, endless levels.
- Leaderboards or comparisons between children.

**Why both lists:** busy visuals around the task cut learning (Fisher et al. 2014: 55% vs 42% correct in kindergarten),
and decorative extras hurt most in short lessons (seductive details meta-analysis, 2020). Parents are the buyers,
and one "this app is manipulative" review costs more than any retention trick earns.

**Tech impact:** still DOM, SVG and CSS with small spring, particle and drag helpers in the shared library. A canvas
effects layer, and character animation tools such as Lottie or Rive, are allowed after Play once their size is measured.
