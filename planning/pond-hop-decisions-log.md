# Pond Hop: decisions made while the owner slept (2026-11-12 night)

The owner accepted every default in `planning/subtraction-pond-design.md` section 10 and asked me to build and
publish the whole game unattended. This log lists every judgment call, newest at the bottom, with the reason, so
you can overturn any of them in the morning. Each entry says how hard it is to change.

## Setup
1. **Game repo is `dr-nithish-kanna/subtraction-grade-1`**, created by you, empty (no `main` yet). My first push
   creates the branch `ccr-d39a02df-81y4w7`. You may want to set a default branch in GitHub later.
   Easy to change.
2. **Kit pinned by full commit SHA, not a tag**, because tag pushes are blocked in cloud sessions. The kit v0.2.0
   tag is still missing on GitHub. Easy to change (swap the SHA for a tag).
3. **Art preview approval replaced by my own screenshot review.** You normally approve the static preview before
   development. You were asleep, so I reviewed it myself against the garden preview. Please look at
   `brand/subtraction-pond/index.html` first thing. Art changes are cheap if you dislike it.
4. **Merge and deploy authorised** by "publish it". I only merge when website tests, the build and the game tests
   pass.

(More entries are added below as the build goes on.)
5. **Art preview accepted by me (Sonnet made it, I checked the screenshots).** `brand/subtraction-pond/index.html`
   (built by `build.py`). Looks consistent with the garden. Known weak spots, left as they are for v1: the dragonfly
   (wings read as a narrow fan, tail a bit worm-like), the turtle's neck is hidden, Hazel's pointing pose is close to
   her neutral pose. A redraw of the dragonfly is the first thing I would change if you dislike it. Easy to change.
6. **Kit design pass done by Opus** (`planning/fill-container-remove-design.md`, 14 decisions). The important ones:
   - Take-away reuses the same reducer run backwards. Addition Garden is protected by golden tests written first,
     on the v0.2.0 code, that must never change. A separate opt-in runner `fillTakeAway` means the garden ships none
     of the new code. Costs about 1 KB, chosen for safety of the live game.
   - Level 3 "keep": `q-8m5` reads "8 frogs, keep 5, how many hopped away? 3". The child always names `item.answer`,
     so choices and records need no new code.
   - Reward is `sessionReward: {type: "lights"}`, never stored, never sent to the website.
   - Break ten: the "10" token OPENS into ten fireflies (make-ten backwards). The game design said "folds into";
     the doc says why it is the other way round. No zero results, no spare items in this version.
   - Kit grows to about 21 KB brotli for this page (over the 15 KB target, like the garden).
   - Needs a website fix: the parent tip for "wrong-operation" must not say "subtracts instead of adding" for a
     subtraction game.
7. **Kit v0.3.0 built by Opus** (kit commit `0e03b6e308d8079ffca6ad82c3efaa34b69be410`, branch `ccr-d39a02df-81y4w7`).
   138 unit tests, 190 pond browser checks. I re-ran the unit tests and checked screenshots myself. Nothing was cut.
   Make the `v0.3.0` tag on GitHub at that commit when you like. Until then both Pond Hop and any upgrade pin the SHA.
8. **Addition Garden stays on kit v0.2.0 in production.** I did not re-pin the live game. I did prove the upgrade is
   safe: the real garden game rebuilt on the new kit with no code edits passed its full smoke test (71 of 71 checks).
   The 2 golden tests also guard the garden reducer and session record.
9. **Overtake never happens on screen (known limitation, your call).** With a single destination the take-away
   ends on the exact move that reaches the goal, so a child cannot send "one too many". The garden has the same
   shape (it ends the moment the goal is met), but there a wrong extra drop at least gets a hint. Here the game stops
   the child for them, so the child does not have to count to know when to stop. "How many?" still tests the skill.
   Fixing it means a new rule in the shared reducer (for example a "Done" tap), which needs an Opus pass and a kit
   release. Suggested follow-up, not done.
10. **Parent tips.** The wrong-operation tip is now topic aware (subtraction says "adds instead of taking away").
    Website tests cover it. A wrong "How many?" tap counts as a hint (hints 1), because the kit counts along. Fine
    for the parent page, noted so it is not a surprise.
11. **Pond Hop uses the kit's default portrait prompt** ("Turn your phone sideways"). Same limitation as Addition
    Garden. Real portrait layout is still future work. Not tested on real touch devices, only mouse and emulated phones.
12. **Game version 1.0.0**, 10 orders or 180 seconds like the garden. Size: game JS 27.9 KB brotli, before Play 68.6 KB
    of the 100 KB firm limit. The 15 KB kit and 15 KB game targets are exceeded, as accepted for the garden.
13. **Website:** catalog entry, skill `math.subtraction.within-20`, page at `/math-games/subtraction-for-grade-1/`
    (about 540 words), math category page mentions subtraction, home page counts "2 games ready, 6 on the way",
    "Subtraction basics" removed from coming soon. Site smoke test has new Pond Hop checks (all pass).
14. **Zero results, spare items and hand-written items are not in this version.** Easy follow-ups.
