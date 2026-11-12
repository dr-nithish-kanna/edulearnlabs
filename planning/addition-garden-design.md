# Addition Garden: creative design plan (draft for review)

Status: DRAFT. Nothing is built from this yet. Decisions below are what we agreed on 2026-11-12.
Open questions are at the end. Please critique before we start production.

## 1. Why we are redesigning

The first build was a 3-choice quiz with dots. It works, but it is a worksheet in a costume.
Goal now: the child adds by doing (moving things, seeing groups merge), and the game feels satisfying.
Rule for every future game: each game gets its own hands-on mechanic and its own reward feel.

## 2. Agreed decisions

- Core loop: **Seed Stall** (combine two groups in a basket). Levels 1 to 3.
- Level 4 to 5: **Stepping Stones** (make ten on a ten-frame). Shares the drag-into-container interaction.
- Reward: **Your Own Garden**. Each solved order gives a seed or sprout. Stored locally. Lives only inside Addition Garden.
- Framing: **tiny stories**. Each round is a short scene (a customer arrives with an order).
- Sound: **number pitch**. Each number has a note, adding plays a rising chord.
- Sandbox: **optional**. A "decorate my garden" button on the title screen and end screen. Never forced.
- Budget: ignored for now. Visual quality and satisfaction come first. We measure and trim later.
- Still true: no timers pressure, no failure screens, no streaks, no leaderboards, no ads, no external links.

## 3. A round, step by step (Seed Stall, levels 1 to 3)

1. A customer walks up to the stall (ladybug, snail, bee, rabbit; Hazel is the shopkeeper).
2. The customer says the order out loud and shows it as a thought bubble: "I would like 7 flowers, please."
   The spoken line comes from the `say` field. The number is also shown as a numeral.
3. Two bins sit on the counter: a red-flower bin and a blue-flower bin, each with a visible stock of items.
   The order is built so that the bins hold exactly the two parts (for example 3 and 4).
4. The child drags flowers from the bins into a basket. Each drop plays a note (number pitch).
   The basket shows a running count so the child can see the total form.
5. When the basket count equals the order, the flowers merge and bloom, the chord resolves,
   the customer is happy, and a seed drops into the child's garden shelf.
6. Overfilling is gentle: extra flowers pop back to the bin with a soft wobble. No buzzer, no red X.
7. Stuck for a few seconds: Hazel points at the bins (hint). After a second stuck round she shows the
   counting aid, such as numbers lighting up on each flower.

Question data stays JSON: `{ "order": 7, "red": 3, "blue": 4 }`. The generator still produces a and b
from `game.json` levels, so difficulty and adaptivity keep working.

## 4. Stepping Stones (levels 4 and 5)

- Hazel stands at the edge of a pond. A ten-frame of stones (2 rows of 5) is the path.
- Level 4 (teen plus small, 12 + 5): ten stones are already filled, the child places the extra 2 and 5 on a second frame.
- Level 5 (crossing ten, 8 + 5): the frame has 8 stones. The child drags 2 from the pile to complete the ten,
  the frame glows and "flips" into a single 10 token, then the remaining 3 go onto the next frame. Total: 13.
- This teaches the make-ten strategy (8 + 5 = 8 + 2 + 3), the key skill for crossing ten.
- Same drag, drop and note mechanics as Seed Stall, different container.

## 5. Your Own Garden (reward)

- Every correct order grants one item: seed first, then it grows over later sessions into a flower, bush or tree.
- Items are chosen from a small set of species. Rare species are never gated behind failure or streaks.
- Garden state is stored locally with the rest of the progress, in a schema that can sync later.
- Session end screen: shows the new items popping into the garden, with a calm "Come back and watch them grow".
  No "you lost" state, no streak language.
- Optional sandbox: the child can move, rotate and re-plant items, change the sky (day, sunset, night),
  and add small decorations unlocked by mastery badges. No timers, no purchases.

## 6. Sound design

- Each number 1 to 20 maps to a pitch on a pentatonic scale, so any combination sounds pleasant.
- Dropping flowers plays ascending notes. Completing the order plays the chord of the total.
- Voice lines (from `say` fields) come from the existing audio pipeline.
- Audio toggle stays visible. Every sound has a visual twin, because many children play muted.

## 7. Visual direction

- Warm, layered garden scene: sky, hills, stall, customer, Hazel. Parallax is subtle, transform and opacity only.
- Flowers have personality: squash and stretch on pick up, soft shadow while dragging, little pop on drop.
- Reduced-motion version of every animation (the kit already requires this).
- Customers are a cast of 4 animals (DECIDED): ladybug, snail, bee, rabbit. Drawn as SVG so they stay crisp and cheap.
  Each has its own entrance and reaction (ladybug flutters in, snail slides slowly, bee zig-zags, rabbit hops).
  They stay anonymous (no names) for now.

## 8. What changes in the code

- **Game repo (`addition-grade-1`)**: game.json gets a new mechanic id, new question shape, levels map to
  Seed Stall or Stepping Stones. New art, new scenes, new audio.
- **Kit (`edulearnlabs-kit`)**: a new reusable mechanic, working name `fill-container`
  (drag items into a container until a target count is reached). It will also serve counting,
  subtraction (take away) and make-ten games later. This changes shared schema and the message contract,
  so per CLAUDE.md it needs a **new minor kit tag and a README note**, and Opus is recommended for that design step.
- **Website**: the progress store gets a garden section (items, species, growth stage). Local only, versioned schema.
- **Pointer and touch**: use Pointer Events with a large drag hit area (at least 56 px), tap-to-pick then tap-to-place
  as an accessible fallback for children who struggle with dragging.

## 9. Build order (proposed, each step reviewed by you)

1. Opus: design `fill-container` mechanic, question schema, messages, garden data shape.
2. Paper prototype: one static Seed Stall screen (art direction approval).
3. Playable Seed Stall, levels 1 to 3, no garden yet.
4. Number pitch sound and voice lines.
5. Garden reward loop and storage.
6. Stepping Stones, levels 4 and 5.
7. Optional sandbox.
8. Measure size and speed on the throttled profile, then trim.

## 10. Questions

Decided on 2026-11-12:
1. Cast: ladybug, snail, bee, rabbit. No names for now.
2. Wrong totals: hints only, never the answer.
3. Garden species at launch: 6, each with 3 growth stages (seed, sprout, bloom).

Still open (default in brackets, tell me if you want it changed):
4. Does the garden grow only when the child plays, or also while away? [Default: only when they play, no pressure to return.]
5. Which 6 species? [Proposed: sunflower, tulip, daisy, lavender, strawberry plant, small tree.]
6. Are the two bins two different flower types from the species list (3 daisies + 4 tulips)? [Proposed: yes, it teaches "combine different things".]
