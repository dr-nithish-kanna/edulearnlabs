# EduLearnLabs style guide (v3, 2026-11-11)

Status: **v3, approved by owner 2026-11-11.** Preview: `brand/style-preview.html`. Mascot poses: `brand/hazel-demo.html`.
Mascot source: `brand/mascot/owl.svg`. Rules here become CSS tokens in ell-kit.

## 1. Feel in one line
Rounded, bright and friendly at the edges. Calm and clear where the child thinks.

## 2. Mascot: Hazel the owl
- **Shape:** "chibi" proportions. A big round head on a small body, huge amber eyes, round cheeks, a feather cowlick
  on top and pointed ear tufts. Big head plus big eyes is the "baby schema" (Konrad Lorenz): the features people
  read as cute and friendly.
- **Look:** brown body and head, light brown heart-shaped face and belly, feather brows, round brass reading
  glasses, and **one** beaded chain hanging on one side (Hazel's left, viewer's right) ending in a gold star charm.
  The other side is empty. The one-sided charm makes it a personal, quirky accessory.
- **Why it works:** brown and brass say "wise, warm, bookish". The glasses and the star charm make Hazel
  recognisably ours. The star links to the stars children earn.
- **Built for animation.** `brand/mascot/owl.svg` is layered SVG (about 8 KB). Every movable part is a named group
  with its pivot point already set, so a pose or animation is a few lines of CSS:

  | Part | Moves | Pivot |
  |---|---|---|
  | `#hazel` | hop, squash and stretch | feet |
  | `#body-group` | breathe, bob | feet |
  | `#head` | tilt, nod | neck |
  | `#wing-left`, `#wing-right` | wave, flap, cheer | shoulder |
  | `#foot-left`, `#foot-right` | tap, hop | heel |
  | `#tuft-left`, `#tuft-right`, `#cowlick` | wiggle, bounce | base |
  | `#brow-left`, `#brow-right` | raise (thinking, surprised) | center |
  | `#eye-left`, `#eye-right` | blink (scaleY); `.look` inside = gaze direction | eye center |
  | `#eyes-happy` | closed smiling eyes (swap in with opacity) | |
  | `#beak-lower` | open for talking | beak hinge |
  | `#glasses` | push up | |
  | `#charm` | sway | hinge on glasses |

  Demo of idle, happy, thinking, talking and "try again": `brand/hazel-demo.html` (serve the `brand` folder over
  http, for example `npx serve brand`).
- **Poses still to add:** cheering end-screen pose, sleepy goodbye, wave hello.
- **Personality:** curious, warm, a little silly professor. Celebrates effort and learning. Never sad because a
  child leaves, never disappointed in a wrong answer.
- **Outfits and charms** (unlocked by mastery, carried across games): swap the star charm (acorn, book, music note),
  add a scarf, bow tie, lab coat or graduation cap. Each is a small SVG layer.

## 3. Colors

| Token | Hex | Use | Text on it |
|---|---|---|---|
| teal | #0F857D | brand, primary button, titles | white (4.5:1) |
| teal-dark | #0A625C | button "press" edge | white |
| teal-bright | #14A39A | decoration only | ink |
| sun | #FFC83D | stars, Play again | ink (8.8:1) |
| leaf | #2FCB86 | correct answer, progress, garden | ink or large white |
| sky | #2FB5EC | counters, info | ink |
| pink | #FF6FB5 | counters, cheeks, stickers | ink |
| cocoa | #8B5A3C | owl body | white |
| caramel | #C8996A | owl face rim, warm accents | ink |
| ink | #3B2A20 | all text (warm dark brown, never pure black) | |
| cream | #FFF7E8 | page and game background | |
| card | #FFFFFF | question card, choices | |

Rules:
- **Teal is the opposite of warm brown on the color wheel,** so buttons and titles stand out and make the owl pop.
- **Bright colors carry dark ink text,** not white. Only teal and cocoa are dark enough for white text. (Checked
  with the WCAG contrast formula: white on bright yellow is 1.5:1, unreadable; ink on yellow is 8.8:1.)
- **The question card is always white on cream.** Color lives on the owl, rewards, counters and celebrations.
- **No red anywhere in feedback.** Correct is leaf green. "Try again" is a soft orange glow plus the owl's kind nod.
- Counting objects use 2 clearly different colors per group (sky and pink) so groups are easy to see.

## 4. Shapes and depth
- Corner radius: 16 px (small), 24 px (choices), 32 px (cards and screens), pill (buttons).
- No sharp corners anywhere, including icons and star points (rounded joins).
- **"Pressable" buttons:** a solid darker edge under each button (6 px). On press the button moves down 4 px and
  the edge shrinks, so it feels like a real button being pushed.
- Soft shadows only (large blur, low opacity, tinted navy, never grey-black).
- Backgrounds: soft gradients and one rounded hill. No busy patterns behind the question.

## 5. Type
- **Fredoka** (rounded, Google Fonts, free OFL license) for numbers, titles and buttons. Bold and friendly.
- **Andika** (SIL, free OFL license) for any reading text. It was designed for early readers: single-story "a" and
  "g", clear "I l 1" shapes. This matters for ages 4 to 7, who are learning letter shapes.
- Sizes on the play area: numbers 64 to 96 px, choices 48 px, any word at least 28 px.
- Fonts are self-hosted and subset (only the characters we use) to keep them around 15 to 25 KB each.

## 6. Motion
- Spring easing for anything a child touches: `cubic-bezier(.34, 1.56, .64, 1)` (slight overshoot, feels bouncy).
- Timing: taps respond in under 100 ms, feedback finishes within 300 ms, celebrations under 1.5 s.
- Correct: chosen card pops (scale 1.08, small tilt), turns leaf green, confetti burst, the owl hops.
- Wrong: card does a gentle wobble (not a shake), the owl tilts its head, hint appears.
- Idle: the owl blinks every 3 to 6 s and bobs slowly. Nothing else moves while a question is waiting.
- Reduced motion: replace pops, hops and confetti with simple fades and color changes.

## 7. Sound
- Soft, rounded sounds (marimba, xylophone, soft pops). No buzzers.
- Correct-answer notes climb a scale for answers in a row; resets gently after a miss.
- One warm, clear voice for all spoken lines. Music is quiet and drops lower whenever the voice speaks.

## 8. Asset sources and licenses
- **Free assets:** only CC0 (public domain) or clearly free-for-commercial-use packs (for example Kenney, CC0).
  Keep a `CREDITS.md` with source and license for every asset, even CC0.
- **AI-generated assets:** fine for backgrounds, props and sticker designs. Clean up and recolor to this palette.
  **Not for the mascot.** The owl stays hand-built SVG. Reasons: AI art cannot be animated part by part, it drifts
  between images (the owl would look slightly different each time), and in the US purely AI-made images may not be
  protected by copyright, so we could not stop someone copying our brand character.
- Fonts: Google Fonts and SIL fonts under OFL. Free for commercial use.
- Sound effects: CC0 packs (Kenney audio, freesound CC0 only). Voice: text-to-speech at build time, reviewed by ear.

## 9. Decisions and open questions
- **Name: Hazel** (owner, 2026-11-11). Hazel is a light brown, which matches the owl. Still to do: a quick trademark
  check (USPTO and India IP office) for "Hazel" plus "education" or "games" before launch.
- **Glasses chain:** one short earring-style chain on one side only (Hazel's left, viewer's right) with a gold star
  charm. The other side is empty. The asymmetry makes it feel like a personal, quirky accessory. The charm can later
  be swapped (star, acorn, book) as an earned mastery reward.
