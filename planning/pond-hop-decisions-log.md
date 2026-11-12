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
