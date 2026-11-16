# Builds index.html for the Bead Parlor art preview (Color pattern repeat, Kindergarten).
# Run from this folder: python3 build.py
# Hazel is copied from brand/mascot/owl.svg (source of truth), never redrawn.
# No external requests: fonts fall back to system rounded fonts.
import re, math

INK = '#3B2A20'
FONT = "Fredoka, 'Baloo 2', 'Trebuchet MS', 'Segoe UI', system-ui, sans-serif"

owl = open('../mascot/owl.svg').read()
owl_inner = re.sub(r'^<svg[^>]*>', '', owl.strip())
owl_inner = owl_inner[:owl_inner.rindex('</svg>')]
owl_inner = re.sub(r'<title>.*?</title>', '', owl_inner, flags=re.S)
owl_inner = re.sub(r'<!--.*?-->', '', owl_inner, flags=re.S)

def hazel(prefix, x, y, w):
    inner = owl_inner
    for i in re.findall(r'id="([^"]+)"', inner):
        inner = inner.replace(f'id="{i}"', f'id="{prefix}-{i}"').replace(f'url(#{i})', f'url(#{prefix}-{i})')
    inner = inner.replace(f'id="{prefix}-eye-left" class="part"', f'id="{prefix}-eye-left" class="part hz-blink"')
    inner = inner.replace(f'id="{prefix}-eye-right" class="part"', f'id="{prefix}-eye-right" class="part hz-blink"')
    h = w * 262 / 240
    return f'<svg x="{x}" y="{y}" width="{w}" height="{h:.0f}" viewBox="0 0 240 262">{inner}</svg>'

# ---------------------------------------------------------------- beads: color AND shape
def star(cx, cy, ro, ri):
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        r = ro if k % 2 == 0 else ri
        pts.append(f'{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}')
    return ' '.join(pts)

EMBLEM = {
 'circle':   '<circle cx="50" cy="50" r="14"/>',
 'square':   '<rect x="36" y="36" width="28" height="28" rx="6"/>',
 'triangle': '<path d="M50 34 L66 63 H34 Z"/>',
 'star':     f'<polygon points="{star(50, 52, 19, 8.5)}"/>',
 'diamond':  '<path d="M50 32 L68 50 L50 68 L32 50 Z"/>',
 'heart':    '<path d="M50 67 C27 52 32 35 43 36 C47 36 50 40 50 44 C50 40 53 36 57 36 C68 35 73 52 50 67 Z"/>',
}
BEADS = [  # id, name, color, shape, note
 ('red',    'Red',    '#E8504A', 'circle',   'C'),
 ('blue',   'Blue',   '#3A78D8', 'square',   'D'),
 ('yellow', 'Yellow', '#FFC83D', 'triangle', 'E'),
 ('green',  'Green',  '#2FCB86', 'star',     'G'),
 ('purple', 'Purple', '#9B6BE0', 'diamond',  'A'),
 ('orange', 'Orange', '#FF8A3D', 'heart',    'C2'),
]
BCOL = {b[0]: b[2] for b in BEADS}

symbols = []
for bid, name, col, shape, note in BEADS:
    symbols.append(f'''<symbol id="b-{bid}" viewBox="0 0 100 100"><g stroke="{INK}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round">
<rect x="8" y="8" width="84" height="84" rx="38" fill="{col}"/>
<path d="M22 38 Q24 22 40 19" fill="none" stroke="#fff" stroke-width="5" opacity=".55"/>
<g fill="#fff">{EMBLEM[shape]}</g></g></symbol>''')

# gap slot, tray dish, spider
symbols.append(f'''<symbol id="gap" viewBox="0 0 100 100"><rect x="8" y="8" width="84" height="84" rx="38" fill="#fff" fill-opacity=".55" stroke="{INK}" stroke-opacity=".55" stroke-width="3" stroke-dasharray="7 8"/></symbol>''')

symbols.append(f'''<symbol id="spider" viewBox="0 0 240 220"><g stroke="{INK}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">
<g fill="none" stroke="#4B3470" stroke-width="9">
<path d="M92 118 Q50 92 30 118 Q22 132 34 150"/><path d="M92 128 Q50 118 30 150 Q24 166 38 182"/>
<path d="M98 140 Q64 150 56 182 Q54 196 66 204"/><path d="M110 150 Q92 176 92 200"/>
<path d="M148 118 Q190 92 210 118 Q218 132 206 150"/><path d="M148 128 Q190 118 210 150 Q216 166 202 182"/>
<path d="M142 140 Q176 150 184 182 Q186 196 174 204"/><path d="M130 150 Q148 176 148 200"/></g>
<ellipse cx="120" cy="150" rx="46" ry="42" fill="#6A4C93"/>
<ellipse cx="120" cy="156" rx="30" ry="28" fill="#D9C8F0" stroke="none"/>
<circle cx="120" cy="82" r="46" fill="#6A4C93"/>
<g stroke="none"><ellipse cx="98" cy="84" rx="15" ry="18" fill="#fff"/><ellipse cx="142" cy="84" rx="15" ry="18" fill="#fff"/>
<circle cx="101" cy="87" r="8" fill="{INK}"/><circle cx="139" cy="87" r="8" fill="{INK}"/>
<circle cx="104" cy="83" r="3" fill="#fff"/><circle cx="142" cy="83" r="3" fill="#fff"/>
<ellipse cx="82" cy="106" rx="9" ry="6" fill="#FF6FB5" opacity=".6"/><ellipse cx="158" cy="106" rx="9" ry="6" fill="#FF6FB5" opacity=".6"/></g>
<path d="M104 112 Q120 126 136 112" fill="none" stroke-width="4"/>
<path d="M92 52 Q96 40 104 46 M148 52 Q144 40 136 46" fill="none" stroke="#fff" stroke-width="5" opacity=".35" stroke-linecap="round"/>
</g></symbol>''')

def bead(bid, x, y, s=104, cls=''):
    return f'<use class="{cls}" href="#b-{bid}" x="{x}" y="{y}" width="{s}" height="{s}"/>'

def string_row(cells, y, start_label=None, s=104, gapw=14, cls_for={}):
    """cells: list of bead ids or None (gap). Returns svg markup and the x list. Centered on 480."""
    n = len(cells)
    total = n * s + (n - 1) * gapw
    x0 = 480 - total / 2
    out = [f'<path d="M{x0-26:.0f} {y+s/2} H{x0+total+26:.0f}" stroke="#8B5A3C" stroke-width="7" stroke-linecap="round" fill="none"/>']
    for i, c in enumerate(cells):
        x = x0 + i * (s + gapw)
        if c is None:
            out.append(f'<use class="{cls_for.get(i, "")}" href="#gap" x="{x:.0f}" y="{y}" width="{s}" height="{s}"/>')
        else:
            out.append(bead(c, f'{x:.0f}', y, s, cls_for.get(i, '')))
    return '\n'.join(out), x0

def tray(beads_, y, s=104, gapw=14, cls_for={}):
    n = len(beads_)
    total = n * s + (n - 1) * gapw
    x0 = 480 - total / 2
    out = [f'<rect x="{x0-22:.0f}" y="{y-14}" width="{total+44:.0f}" height="{s+28}" rx="38" fill="#C8996A"/><rect x="{x0-14:.0f}" y="{y-8}" width="{total+28:.0f}" height="{s+16}" rx="32" fill="#E9C99A"/>']
    for i, b in enumerate(beads_):
        x = x0 + i * (s + gapw)
        out.append(bead(b, f'{x:.0f}', y, s, cls_for.get(i, '')))
    return '\n'.join(out), x0

def bracelet(cx, cy, r, seq, bs=15):
    n = len(seq)
    out = [f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r*0.8:.0f}" fill="none" stroke="#8B5A3C" stroke-width="3"/>']
    for i, b in enumerate(seq):
        a = 2 * math.pi * i / n - math.pi / 2
        out.append(bead(b, f'{cx + r*math.cos(a) - bs/2:.1f}', f'{cy + r*0.8*math.sin(a) - bs/2:.1f}', bs))
    return '\n'.join(out)

def backdrop():
    return f'''<defs>
<linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FDE7D2"/><stop offset="1" stop-color="#F9D2B2"/></linearGradient>
<linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C8996A"/><stop offset="1" stop-color="#A9784B"/></linearGradient>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9FD9F5"/><stop offset="1" stop-color="#E4F5FC"/></linearGradient>
<radialGradient id="lamp" cx=".5" cy=".5"><stop offset="0" stop-color="#FFD65C" stop-opacity=".6"/><stop offset="1" stop-color="#FFD65C" stop-opacity="0"/></radialGradient></defs>
<rect x="-400" y="-200" width="1760" height="840" fill="url(#wall)"/>
<g stroke="#fff" stroke-opacity=".35" stroke-width="3">{''.join(f'<path d="M{x} -200 V560"/>' for x in range(-380, 1360, 70))}</g>
<rect x="-400" y="540" width="1760" height="200" fill="url(#floor)"/>
<rect x="-400" y="532" width="1760" height="12" fill="#8B5A3C"/>
<g><rect x="700" y="86" width="190" height="150" rx="18" fill="url(#sky)" stroke="#8B5A3C" stroke-width="9"/><path d="M795 86 V236 M700 161 H890" stroke="#8B5A3C" stroke-width="6"/>
<path d="M735 214 q15 -22 34 -8 q16 -22 36 -4 q16 -12 30 4 z" fill="#fff" opacity=".8"/>
<path d="M684 78 Q724 120 696 244 H676 V78Z M906 78 Q866 120 894 244 H914 V78Z" fill="#FF6FB5" opacity=".75"/></g>
<g stroke="#8B5A3C" stroke-width="3" fill="none"><path d="M24 40 Q480 90 936 40"/></g>
{''.join(f'<g transform="translate({x} {40 + 50*math.sin(x/960*math.pi)*0.96:.0f})"><circle r="15" fill="{c}" stroke="{INK}" stroke-width="3"/><path d="M-9 -3 Q0 6 9 -3 M-9 5 Q0 14 9 5" fill="none" stroke="#fff" stroke-width="3" opacity=".7"/></g>' for x, c in [(110,'#FF8A3D'),(250,'#2FB5EC'),(390,'#FF6FB5'),(570,'#2FCB86'),(710,'#FFC83D'),(850,'#9B6BE0')])}
<ellipse cx="480" cy="330" rx="440" ry="230" fill="url(#lamp)"/>'''

def board(title, bracelets_list):
    parts = [f'<rect x="24" y="116" width="200" height="184" rx="28" fill="#A9784B"/><rect x="32" y="124" width="184" height="168" rx="22" fill="#FFF1D6"/>',
             f'<text x="124" y="152" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="600" fill="#0A625C">{title}</text>']
    cells = [(70, 195), (124, 195), (178, 195), (70, 255), (124, 255), (178, 255)]
    for (cx, cy), seq in zip(cells, bracelets_list):
        parts.append(bracelet(cx, cy - 18, 20, seq, 11))
    return '\n'.join(parts)

SPIDER_BODY_H = 180

def scene(sid, inner, label):
    return f'''<svg class="scene" viewBox="0 0 960 600" role="img" aria-label="{label}" id="{sid}">{backdrop()}{inner}</svg>'''

# --- scene 1: Level 2, continue AB (1 gap at the end, 1 spare) ---
row1, x0 = string_row(['red', 'blue', 'red', 'blue', 'red', None], 318, cls_for={5: 'glow-gap'})
tray1, _ = tray(['blue', 'yellow', 'red'], 470, cls_for={})
s1 = f'''<path d="M300 40 V150" stroke="#E9E4F0" stroke-width="3"/>
<use href="#spider" x="215" y="118" width="170" height="156" class="hz-bob2"/>
{board('My bracelets', [['red','blue']*3, ['red','blue','yellow']*2, ['green','purple']*3])}
{hazel('h1', 770, 104, 150)}
{row1}{tray1}'''

# --- scene 2: Level 1, copy: pattern shown above, build below ---
ex_row, _ = string_row(['red', 'blue', 'red', 'blue'], 160, s=84, gapw=12)
row2, _ = string_row(['red', 'blue', None, None], 318)
tray2, _ = tray(['red', 'blue', 'yellow'], 470)
s2 = f'''<g opacity="1"><rect x="270" y="124" width="420" height="146" rx="30" fill="#fff" fill-opacity=".8"/>
<text x="480" y="150" text-anchor="middle" font-family="{FONT}" font-size="18" font-weight="600" fill="#0A625C">Make this one!</text></g>
{ex_row}
{hazel('h2', 790, 104, 120)}
{row2}{tray2}'''

# --- scene 3: done, bracelet tied, flies to the shelf ---
done, _ = string_row(['red', 'blue', 'red', 'blue', 'red', 'blue'], 318, cls_for={i: 'lit' for i in range(6)})
s3 = f'''{board('My bracelets', [['red','blue']*3, ['red','blue','yellow']*2, ['green','purple']*3, ['red','blue']*3])}
<path d="M595 40 V150" stroke="#E9E4F0" stroke-width="3"/><use href="#spider" x="520" y="116" width="150" height="138" class="hz-bob2"/>
{done}
<g transform="translate(480 470)"><circle r="72" fill="#FFC83D" opacity=".22"/>{bracelet(0, 0, 44, ['red','blue']*3, 24)}
<path d="M-22 -56 q22 -22 44 0" fill="none" stroke="#E8504A" stroke-width="7" stroke-linecap="round"/></g>
{hazel('h3', 770, 104, 150)}
<g fill="#FFC83D" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round">{''.join(f'<polygon transform="translate({x} {y}) scale({s})" points="{star(0,0,10,4.5)}"/>' for x, y, s in [(250,260,1.2),(740,420,1.5),(190,430,1),(820,290,1),(350,500,1.1)])}</g>'''

# --- bead sheet ---
def sheet(gray=False):
    cells = ''.join(f'<figure class="bd"><svg viewBox="0 0 100 100" width="96" height="96"><use href="#b-{b}"/></svg><figcaption>{n}<br><i>{sh}</i></figcaption></figure>' for b, n, c, sh, _ in BEADS)
    return f'<div class="beads{" gray" if gray else ""}">{cells}</div>'

def pattern_strip(units, gray=False):
    cells = ''.join(f'<svg viewBox="0 0 100 100" width="58" height="58"><use href="#b-{b}"/></svg>' for b in units)
    return f'<div class="strip{" gray" if gray else ""}">{cells}</div>'

html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bead Parlor art preview</title>
<style>
:root{{--cream:#FFF7E8;--ink:#3B2A20;--teal:#0F857D}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--cream);color:var(--ink);font-family:Andika,"Trebuchet MS","Segoe UI",system-ui,sans-serif;padding:24px 16px 60px}}
main{{max-width:980px;margin:0 auto}}
h1,h2{{font-family:{FONT}}} h1{{color:var(--teal);margin:0 0 4px}} h2{{margin:44px 0 8px}}
p,li{{line-height:1.5;max-width:72ch}}
.scene{{width:100%;height:auto;border-radius:32px;box-shadow:0 10px 30px rgba(90,50,20,.28);display:block;background:#F9D2B2}}
.note{{background:#fff;border-left:6px solid var(--teal);border-radius:12px;padding:10px 16px;max-width:72ch}}
.beads{{display:flex;flex-wrap:wrap;gap:14px;background:#fff;border-radius:24px;padding:16px}}
.bd{{margin:0;text-align:center;font-size:14px}} .bd i{{color:#6b5a4b}}
.gray{{filter:grayscale(1)}}
.strip{{display:flex;gap:6px;background:#fff;border-radius:20px;padding:10px;margin:8px 0;width:max-content;max-width:100%;flex-wrap:wrap}}
.cols{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}}
code{{background:#fff;padding:1px 6px;border-radius:6px;font-size:14px}}
.hz-bob2,.glow-gap,.lit,.hz-blink{{transform-box:fill-box;transform-origin:center}}
@keyframes bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-4px)}}}} .hz-bob2{{animation:bob 3.4s ease-in-out infinite}}
@keyframes gp{{0%,100%{{opacity:.6;transform:scale(1)}}50%{{opacity:1;transform:scale(1.06)}}}} .glow-gap{{animation:gp 1.6s ease-in-out infinite}}
@keyframes lit{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-8px)}}}} .lit{{animation:lit 1.8s ease-in-out infinite}}
.lit:nth-of-type(2){{animation-delay:.28s}}
@keyframes blink{{0%,94%,100%{{transform:scaleY(1)}}97%{{transform:scaleY(.1)}}}} .hz-blink{{animation:blink 5s linear infinite}}
@media (prefers-reduced-motion:reduce){{.hz-bob2,.glow-gap,.lit,.hz-blink{{animation:none}}}}
</style></head><body><svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>{''.join(symbols)}</defs></svg>
<main>
<h1>Bead Parlor</h1>
<p>Art preview for <strong>Color pattern repeat</strong> (Kindergarten, logic). Status: for owner approval. Scene is 960 x 600, same as the other games. Beads, cast and layout are a proposal, nothing is built yet.</p>

<h2>1. Playing: continue the pattern (level 2)</h2>
{scene('sc1', s1, 'Craft room. A spider hangs by a thread. A bead string shows red, blue, red, blue, red and one empty gap. Three beads wait in a tray.')}
<p>The spider hangs from a thread beside the "My bracelets" board. The string has one dashed gap at the end, and it pulses softly (that is hint 2, "Gap"). The tray holds the right bead plus spares. Hazel waits at the top right as the host and hint button.</p>

<h2>2. Level 1: copy the pattern</h2>
{scene('sc2', s2, 'The pattern red, blue, red, blue is shown in a card above. Below it the child builds the same string, two beads placed and two gaps.')}
<p>The card above is the pattern to copy. The child builds it below, left to right. It is the easiest level, so it never counts as "reading" a pattern, only as matching one.</p>

<h2>3. Done: the bracelet is tied</h2>
{scene('sc3', s3, 'All six beads on the string are lit. A finished bracelet with a bow sits below, and stars sparkle. The shelf on the left shows four bracelets.')}
<p>Each bead lights left to right with its note, so the pattern plays as a tune. The bracelet is tied with a bow and flies to the "My bracelets" shelf (website-owned reward). In reduced motion the lift and fly become a fade.</p>

<h2>4. The six beads: color and shape</h2>
<p>Every bead has its own color and its own shape. The pattern can be read by shape alone. Levels 1 to 3 use only red circle, blue square and yellow triangle.</p>
{sheet()}
<h2>5. Color-blind check (grayscale)</h2>
<div class="note">Same beads with all color removed. If you can still tell all six apart, a child who cannot see the colors can still solve the game. Red and green are the usual trouble pair, so they are never both in levels 1 to 3.</div>
<p></p>
{sheet(True)}
<div class="cols"><div><p><strong>In color</strong></p>{pattern_strip(['red','blue','yellow','red','blue','yellow'])}</div>
<div><p><strong>In grayscale</strong></p>{pattern_strip(['red','blue','yellow','red','blue','yellow'], True)}</div></div>

<h2>6. What I need you to check</h2>
<ul>
<li><strong>The spider.</strong> Friendly or a bit much for 5 year olds? Some children fear spiders. The alternative is a caterpillar or a ladybug stringing the beads. I drew a big-eyed, smiling, plum spider on purpose, and it is your call.</li>
<li><strong>The six beads.</strong> Shapes read clearly in grayscale? Any shape you want swapped?</li>
<li><strong>The craft room.</strong> Peach wall, wood floor, window, hanging yarn garland. New look compared to the garden (sunny), pond (dusk), workshop (wood) and meadow (picnic).</li>
<li><strong>Layout.</strong> Bead tiles are 104 px in the 960 x 600 scene (65 px on a 667 x 375 phone), seven beads at most per string.</li>
</ul>
<p>Sound and motion are not shown in a static page. Motion is transform and opacity only, with a reduced-motion version of every animation. Fonts fall back to system fonts here, the game ships Fredoka and Andika.</p>
</main></body></html>'''
open('index.html', 'w').write(html)
print('wrote index.html', len(html))
