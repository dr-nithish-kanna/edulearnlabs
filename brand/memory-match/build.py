# Builds index.html for the Quilt Picnic art preview (Memory Match for Pre-K and Kindergarten).
# Run from this folder: python3 build.py
# Hazel is copied from brand/mascot/owl.svg (source of truth), never redrawn.
# No external requests: fonts fall back to system rounded fonts (the real game ships subset Fredoka and Andika).
import re, math

INK = '#3B2A20'
FONT = "Fredoka, 'Baloo 2', 'Trebuchet MS', 'Segoe UI', system-ui, sans-serif"

# ---------------------------------------------------------------- Hazel (reused)
owl = open('../mascot/owl.svg').read()
owl_inner = re.sub(r'^<svg[^>]*>', '', owl.strip())
owl_inner = owl_inner[:owl_inner.rindex('</svg>')]
owl_inner = re.sub(r'<title>.*?</title>', '', owl_inner, flags=re.S)
owl_inner = re.sub(r'<!--.*?-->', '', owl_inner, flags=re.S)

def hazel(prefix, x, y, w):
    inner = owl_inner
    ids = re.findall(r'id="([^"]+)"', inner)
    for i in ids:
        inner = inner.replace(f'id="{i}"', f'id="{prefix}-{i}"').replace(f'url(#{i})', f'url(#{prefix}-{i})')
    inner = inner.replace(f'id="{prefix}-wing-right" class="part"', f'id="{prefix}-wing-right" class="part hz-wave"')
    inner = inner.replace(f'id="{prefix}-body-group" class="part"', f'id="{prefix}-body-group" class="part hz-bob"')
    inner = inner.replace(f'id="{prefix}-eye-left" class="part"', f'id="{prefix}-eye-left" class="part hz-blink"')
    inner = inner.replace(f'id="{prefix}-eye-right" class="part"', f'id="{prefix}-eye-right" class="part hz-blink"')
    h = w * 262 / 240
    return (f'<svg x="{x}" y="{y}" width="{w}" height="{h:.0f}" viewBox="0 0 240 262" class="hazel" '
            f'style="overflow:visible">{inner}</svg>')

# ---------------------------------------------------------------- friend pictures (100 x 100 boxes, content inside 8..92)
G = f'stroke="{INK}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"'

def star_pts(cx, cy, ro, ri, n=5, rot=-90):
    pts = []
    for i in range(n * 2):
        r = ro if i % 2 == 0 else ri
        a = math.radians(rot + i * 180 / n)
        pts.append(f'{cx + r * math.cos(a):.1f} {cy + r * math.sin(a):.1f}')
    return 'M' + ' L'.join(pts) + 'Z'

def hedgehog_path():
    cx, cy, rx, ry = 50, 62, 40, 30
    pts = []
    n = 15
    for i in range(n + 1):
        th = math.radians(180 + i * 180 / n)
        rr = 1.0 if i % 2 == 0 else 1.2
        if i == 0 or i == n:
            rr = 1.0
        pts.append(f'{cx + rx * rr * math.cos(th):.1f} {cy + ry * rr * math.sin(th):.1f}')
    return 'M' + ' L'.join(pts) + ' Q93 82 80 86 H20 Q7 82 10 62Z'

def wedge(cx, cy, r, a0, a1, col):
    x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
    x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
    return f'<path d="M{cx} {cy} L{x0:.1f} {y0:.1f} A{r} {r} 0 0 1 {x1:.1f} {y1:.1f}Z" fill="{col}" stroke="none"/>'

def petals():
    out = ''
    for i in range(6):
        out += f'<ellipse cx="50" cy="23" rx="11" ry="15" transform="rotate({i * 60} 50 42)" fill="#FF8DC0"/>'
    return out

PICS = {}
PICS['ladybug'] = f'''<g {G}>
<path d="M43 22 Q40 11 33 10 M57 22 Q60 11 67 10" fill="none"/>
<circle cx="33" cy="10" r="3" fill="{INK}"/><circle cx="67" cy="10" r="3" fill="{INK}"/>
<circle cx="50" cy="60" r="30" fill="#E8504A"/>
<path d="M50 40 V90" stroke-width="2.5" fill="none"/>
<g fill="{INK}" stroke="none"><circle cx="34" cy="58" r="5.5"/><circle cx="66" cy="58" r="5.5"/><circle cx="36" cy="76" r="5"/><circle cx="64" cy="76" r="5"/></g>
<path d="M33 40 Q33 20 50 20 Q67 20 67 40 Q50 46 33 40Z" fill="{INK}"/>
<g fill="#fff" stroke="none"><circle cx="44" cy="32" r="3.2"/><circle cx="56" cy="32" r="3.2"/></g>
<path d="M28 52 Q30 44 37 41" fill="none" stroke="#fff" stroke-width="3" opacity=".7"/>
</g>'''

PICS['snail'] = f'''<g {G}>
<path d="M15 39 Q12 28 14 21 M26 39 Q28 28 28 21" fill="none"/>
<circle cx="14" cy="19" r="4.5" fill="#CFE8A9"/><circle cx="28" cy="19" r="4.5" fill="#CFE8A9"/>
<path d="M8 86 Q5 76 11 62 Q13 52 12 45 Q12 37 20 37 Q28 37 28 47 Q28 57 34 70 H86 Q98 70 94 82 Q92 88 84 88 H14 Q9 88 8 86Z" fill="#CFE8A9"/>
<circle cx="14" cy="19" r="1.6" fill="{INK}" stroke="none"/><circle cx="28" cy="19" r="1.6" fill="{INK}" stroke="none"/>
<path d="M13 54 Q18 59 23 54" fill="none" stroke-width="2.5"/>
<circle cx="62" cy="48" r="26" fill="#E8A33D"/>
<circle cx="62" cy="48" r="17" fill="none" stroke-width="2.5"/><circle cx="62" cy="48" r="8" fill="#F5C26B" stroke-width="2.5"/>
</g>'''

PICS['bee'] = f'''<g {G}>
<ellipse cx="48" cy="30" rx="11" ry="17" transform="rotate(-18 48 30)" fill="#DDF2FF"/>
<ellipse cx="66" cy="32" rx="11" ry="17" transform="rotate(14 66 32)" fill="#DDF2FF"/>
<clipPath id="bee-clip"><ellipse cx="56" cy="58" rx="28" ry="22"/></clipPath>
<ellipse cx="56" cy="58" rx="28" ry="22" fill="#FFC83D"/>
<g clip-path="url(#bee-clip)" stroke="none" fill="{INK}"><rect x="50" y="30" width="9" height="60"/><rect x="68" y="30" width="9" height="60"/></g>
<ellipse cx="56" cy="58" rx="28" ry="22" fill="none"/>
<path d="M83 58 L94 58 L84 65Z" fill="{INK}"/>
<path d="M22 43 Q18 31 11 28 M31 42 Q32 30 39 26" fill="none"/>
<circle cx="11" cy="28" r="2.8" fill="{INK}"/><circle cx="39" cy="26" r="2.8" fill="{INK}"/>
<circle cx="26" cy="57" r="15" fill="#FFC83D"/>
<circle cx="21" cy="54" r="3" fill="{INK}" stroke="none"/><circle cx="30" cy="66" r="4" fill="#FF8DA1" stroke="none" opacity=".6"/>
<path d="M19 62 Q25 67 31 62" fill="none" stroke-width="2.5"/>
</g>'''

PICS['rabbit'] = f'''<g {G}>
<ellipse cx="36" cy="30" rx="10" ry="20" transform="rotate(-8 36 30)" fill="#EADCCB"/>
<ellipse cx="64" cy="30" rx="10" ry="20" transform="rotate(8 64 30)" fill="#EADCCB"/>
<ellipse cx="36" cy="32" rx="4.5" ry="13" transform="rotate(-8 36 32)" fill="#F4A9B8" stroke="none"/>
<ellipse cx="64" cy="32" rx="4.5" ry="13" transform="rotate(8 64 32)" fill="#F4A9B8" stroke="none"/>
<ellipse cx="50" cy="66" rx="31" ry="24" fill="#EADCCB"/>
<g fill="{INK}" stroke="none"><circle cx="39" cy="62" r="3.6"/><circle cx="61" cy="62" r="3.6"/></g>
<circle cx="31" cy="73" r="5" fill="#F9B8B0" stroke="none" opacity=".7"/><circle cx="69" cy="73" r="5" fill="#F9B8B0" stroke="none" opacity=".7"/>
<ellipse cx="50" cy="70" rx="4.5" ry="3.2" fill="#F2849E" stroke-width="2"/>
<path d="M50 73 V77 M50 77 Q45 82 41 78 M50 77 Q55 82 59 78" fill="none" stroke-width="2.5"/>
</g>'''

PICS['fox'] = f'''<g {G}>
<path d="M12 42 L18 10 L38 28 Q50 24 62 28 L82 10 L88 42 Q90 68 50 90 Q10 68 12 42Z" fill="#EE8A33"/>
<path d="M21 24 L23 36 L32 30Z M79 24 L77 36 L68 30Z" fill="#5A3520" stroke="none"/>
<path d="M50 90 Q22 72 24 58 Q38 64 50 58 Q62 64 76 58 Q78 72 50 90Z" fill="#FFF4E0" stroke-width="2.5"/>
<ellipse cx="36" cy="50" rx="3.6" ry="4.6" fill="{INK}" stroke="none"/><ellipse cx="64" cy="50" rx="3.6" ry="4.6" fill="{INK}" stroke="none"/>
<ellipse cx="50" cy="76" rx="5.5" ry="4" fill="{INK}" stroke="none"/>
<path d="M50 80 Q45 86 40 83 M50 80 Q55 86 60 83" fill="none" stroke-width="2.5"/>
</g>'''

PICS['duck'] = f'''<g {G}>
<path d="M15 60 Q6 52 10 46 Q21 49 22 60Z" fill="#FFD84D"/>
<circle cx="64" cy="32" r="18" fill="#FFD84D"/>
<ellipse cx="44" cy="64" rx="32" ry="20" fill="#FFD84D"/>
<path d="M26 62 Q40 48 58 62 Q44 78 26 62Z" fill="#F2B01E"/>
<path d="M78 30 Q94 28 94 36 Q90 42 78 40Z" fill="#F28C28"/>
<circle cx="68" cy="26" r="3.2" fill="{INK}" stroke="none"/>
<circle cx="71" cy="38" r="4" fill="#FFA98A" stroke="none" opacity=".7"/>
<path d="M36 84 V90 M52 84 V90" fill="none"/>
<ellipse cx="36" cy="92" rx="6" ry="2.8" fill="#F28C28" stroke-width="2.5"/><ellipse cx="52" cy="92" rx="6" ry="2.8" fill="#F28C28" stroke-width="2.5"/>
</g>'''

PICS['hedgehog'] = f'''<g {G}>
<path d="{hedgehog_path()}" fill="#8B5A3C"/>
<ellipse cx="30" cy="88" rx="8" ry="4.5" fill="#C8996A" stroke-width="2.5"/><ellipse cx="68" cy="88" rx="8" ry="4.5" fill="#C8996A" stroke-width="2.5"/>
<ellipse cx="28" cy="70" rx="22" ry="17" fill="#F2D3A8"/>
<circle cx="8" cy="71" r="4.5" fill="{INK}" stroke="none"/>
<circle cx="24" cy="62" r="3.2" fill="{INK}" stroke="none"/>
<path d="M18 78 Q26 83 34 77" fill="none" stroke-width="2.5"/>
<circle cx="38" cy="72" r="4" fill="#F9B8B0" stroke="none" opacity=".7"/>
</g>'''

PICS['mouse'] = f'''<g {G}>
<circle cx="24" cy="30" r="15" fill="#C9CDD6"/><circle cx="76" cy="30" r="15" fill="#C9CDD6"/>
<circle cx="24" cy="30" r="8" fill="#F6B3C4" stroke="none"/><circle cx="76" cy="30" r="8" fill="#F6B3C4" stroke="none"/>
<ellipse cx="50" cy="62" rx="32" ry="28" fill="#C9CDD6"/>
<ellipse cx="50" cy="73" rx="16" ry="11" fill="#EDEFF3" stroke="none"/>
<g fill="{INK}" stroke="none"><circle cx="39" cy="57" r="3.6"/><circle cx="61" cy="57" r="3.6"/></g>
<circle cx="50" cy="67" r="4.5" fill="#F28FA5" stroke-width="2"/>
<path d="M50 71 Q45 78 40 75 M50 71 Q55 78 60 75" fill="none" stroke-width="2.5"/>
<path d="M18 64 H32 M18 72 L32 70 M82 64 H68 M82 72 L68 70" fill="none" stroke-width="2"/>
</g>'''

PICS['apple'] = f'''<g {G}>
<path d="M50 30 Q30 18 16 36 Q6 58 22 80 Q36 94 50 86 Q64 94 78 80 Q94 58 84 36 Q70 18 50 30Z" fill="#E8504A"/>
<path d="M50 30 Q50 20 56 11" fill="none" stroke-width="5" stroke="#6E432A"/>
<path d="M54 22 Q70 8 84 16 Q74 32 54 22Z" fill="#6FCB72"/>
<path d="M24 44 Q26 38 32 35" fill="none" stroke="#fff" stroke-width="4" opacity=".7"/>
</g>'''

ball_cols = ['#F26B5B', '#FFC83D', '#2FB5EC'] * 2
PICS['ball'] = f'''<g {G}>
<ellipse cx="50" cy="90" rx="26" ry="4" fill="{INK}" opacity=".15" stroke="none"/>
{''.join(wedge(50, 52, 36, -90 + i * 60, -30 + i * 60, ball_cols[i]) for i in range(6))}
<circle cx="50" cy="52" r="36" fill="none"/>
<circle cx="50" cy="52" r="6" fill="#fff" stroke-width="2.5"/>
<path d="M28 34 Q32 28 39 25" fill="none" stroke="#fff" stroke-width="4" opacity=".75"/>
</g>'''

PICS['star'] = f'''<g {G}>
<path d="{star_pts(50, 53, 42, 20)}" fill="#FFC83D" stroke-width="3.5"/>
<g fill="{INK}" stroke="none"><circle cx="42" cy="52" r="3.2"/><circle cx="58" cy="52" r="3.2"/></g>
<path d="M44 61 Q50 67 56 61" fill="none" stroke-width="2.5"/>
<circle cx="37" cy="60" r="3.5" fill="#FF8DA1" stroke="none" opacity=".6"/><circle cx="63" cy="60" r="3.5" fill="#FF8DA1" stroke="none" opacity=".6"/>
</g>'''

PICS['cup'] = f'''<g {G}>
<path d="M38 27 Q32 19 38 12 M54 27 Q48 19 54 12" fill="none" stroke="#8FA3C7"/>
<path d="M72 46 Q94 44 90 58 Q86 70 68 66" fill="none" stroke-width="9"/>
<path d="M72 46 Q94 44 90 58 Q86 70 68 66" fill="none" stroke="#FFB3D4" stroke-width="3.5"/>
<ellipse cx="46" cy="85" rx="37" ry="7" fill="#fff"/>
<path d="M18 36 H74 Q74 78 46 78 Q18 78 18 36Z" fill="#FF8DC0"/>
<ellipse cx="46" cy="36" rx="28" ry="6" fill="#FFE3F0"/>
<ellipse cx="46" cy="36" rx="23" ry="3.6" fill="#B87A4B" stroke="none"/>
<g fill="#fff" stroke="none" opacity=".9"><circle cx="32" cy="52" r="3"/><circle cx="46" cy="62" r="3"/><circle cx="60" cy="50" r="3"/><circle cx="38" cy="70" r="2.5"/></g>
</g>'''

wing_up = '<ellipse cx="28" cy="34" rx="20" ry="26" transform="rotate(-30 28 34)" fill="#B58CE8"/>'
wing_lo = '<ellipse cx="33" cy="68" rx="14" ry="16" transform="rotate(20 33 68)" fill="#FF8DC0"/>'
wing_dots = '<circle cx="24" cy="30" r="5" fill="#fff" stroke="none" opacity=".85"/><circle cx="32" cy="70" r="3.5" fill="#fff" stroke="none" opacity=".85"/>'
PICS['butterfly'] = f'''<g {G}>
<g>{wing_up}{wing_lo}{wing_dots}</g>
<g transform="translate(100 0) scale(-1 1)">{wing_up}{wing_lo}{wing_dots}</g>
<path d="M47 22 Q44 12 36 10 M53 22 Q56 12 64 10" fill="none"/>
<circle cx="36" cy="10" r="2.8" fill="{INK}"/><circle cx="64" cy="10" r="2.8" fill="{INK}"/>
<ellipse cx="50" cy="56" rx="5" ry="26" fill="{INK}"/><circle cx="50" cy="28" r="7" fill="{INK}"/>
</g>'''

PICS['fish'] = f'''<g {G}>
<circle cx="16" cy="32" r="3" fill="#DDF2FF" stroke-width="2"/><circle cx="10" cy="20" r="2" fill="#DDF2FF" stroke-width="2"/>
<path d="M68 52 L90 32 Q95 52 90 72Z" fill="#1E8FC0"/>
<path d="M34 32 Q46 14 58 33Z" fill="#1E8FC0"/>
<ellipse cx="44" cy="54" rx="32" ry="24" fill="#2FB5EC"/>
<path d="M48 40 q5 4 0 8 M56 50 q5 4 0 8 M46 58 q5 4 0 8" fill="none" stroke-width="2" opacity=".55"/>
<circle cx="27" cy="48" r="6.5" fill="#fff"/><circle cx="26" cy="49" r="3" fill="{INK}" stroke="none"/>
<path d="M14 60 Q20 65 25 61" fill="none" stroke-width="2.5"/>
</g>'''

PICS['flower'] = f'''<g {G}>
<path d="M50 56 Q54 76 49 92" fill="none" stroke="#3E8F4A" stroke-width="5"/>
<path d="M50 78 Q70 66 80 74 Q68 88 50 78Z" fill="#6FCB72"/>
{petals()}
<circle cx="50" cy="42" r="11" fill="#FFC83D"/>
<circle cx="46" cy="38" r="2.5" fill="#FFF0B0" stroke="none"/>
</g>'''

PICS['kite'] = f'''<g {G}>
<path d="M50 77 Q38 83 47 87 Q57 91 50 94" fill="none" stroke-width="2.5"/>
<circle cx="44" cy="84" r="3" fill="#F26B5B" stroke-width="2"/><circle cx="53" cy="90" r="3" fill="#2FB5EC" stroke-width="2"/>
<path d="M50 10 L50 42 L82 42Z" fill="#2FB5EC"/><path d="M50 10 L50 42 L18 42Z" fill="#FFC83D"/>
<path d="M50 77 L50 42 L82 42Z" fill="#F26B5B"/><path d="M50 77 L50 42 L18 42Z" fill="#FF8DC0"/>
<path d="M50 10 L82 42 L50 77 L18 42Z" fill="none"/>
</g>'''

PIC_IDS = list(PICS.keys())
assert len(PIC_IDS) == 16

def symbols():
    return ''.join(f'<symbol id="p-{k}" viewBox="0 0 100 100">{v}</symbol>' for k, v in PICS.items())

# ---------------------------------------------------------------- flap fabrics
FABRIC = [  # fill, edge, name
    ('#C95F83', '#9E3F61', 'berry'), ('#E7AE3C', '#B9851C', 'mustard'), ('#8FB07A', '#5F8550', 'sage'),
    ('#A594D6', '#7A68B0', 'lavender'), ('#EE9262', '#C2663A', 'terracotta'), ('#6DB7B0', '#3F8782', 'teal'),
]
PATS = ['dots', 'stripes', 'checks']

def sp(x, y, r):
    return f'M{x} {y - r} Q{x} {y} {x + r} {y} Q{x} {y} {x} {y + r} Q{x} {y} {x - r} {y} Q{x} {y} {x} {y - r}Z'

def sparkles(items):
    return ''.join(f'<path class="sparkle" d="{sp(x, y, r)}" fill="#FFD65C" stroke="#fff" stroke-width="1.5" stroke-linejoin="round" style="animation-delay:{d}s"/>'
                   for x, y, r, d in items)

def base_shadow():
    return f'<rect x="0" y="5" width="120" height="120" rx="18" fill="{INK}" opacity=".16"/>'

def closed(ci, pat):
    f, e, _ = FABRIC[ci]
    return (f'{base_shadow()}<rect width="120" height="120" rx="18" fill="{f}" stroke="{e}" stroke-width="3"/>'
            f'<rect width="120" height="120" rx="18" fill="url(#pat-{pat})"/>'
            f'<rect x="7" y="7" width="106" height="106" rx="13" fill="none" stroke="#fff" stroke-width="2.5" stroke-dasharray="6 5" opacity=".85"/>'
            f'<path d="M12 22 Q12 12 22 12 H46" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".45"/>'
            f'<circle cx="60" cy="60" r="12" fill="#FFF4DC" stroke="{e}" stroke-width="3"/>'
            f'<g fill="{e}"><circle cx="56" cy="56" r="2"/><circle cx="64" cy="56" r="2"/><circle cx="56" cy="64" r="2"/><circle cx="64" cy="64" r="2"/></g>')

def pocket(pic, stroke='#E0C28E', sw=3, op=1):
    return (f'{base_shadow()}<rect width="120" height="120" rx="18" fill="#FFF4DC" stroke="{stroke}" stroke-width="{sw}"/>'
            f'<path d="M1.5 20 Q1.5 1.5 20 1.5 H100 Q118.5 1.5 118.5 20 V30 H1.5Z" fill="#E8CF9F" opacity=".5"/>'
            f'<use href="#p-{pic}" x="16" y="18" width="88" height="88" opacity="{op}"/>')

def sliver(ci):
    f, e, _ = FABRIC[ci]
    return (f'<path d="M12 0 L108 0 L103 -17 Q102 -20 98 -20 H22 Q18 -20 17 -17Z" fill="{f}" stroke="{e}" stroke-width="3" stroke-linejoin="round"/>'
            f'<path d="M28 -13 H92" stroke="#fff" stroke-width="2.2" stroke-dasharray="5 4" opacity=".8" stroke-linecap="round"/>'
            f'<circle cx="60" cy="-8" r="3" fill="#FFF4DC" stroke="{e}" stroke-width="2"/>')

def matched(pic, ci):
    return (f'<circle class="glow" cx="60" cy="60" r="88" fill="url(#g-glow)"/>'
            f'{pocket(pic, "#F2B632", 4.5)}'
            f'<ellipse cx="60" cy="108" rx="26" ry="4" fill="{INK}" opacity=".15"/>'
            + sliver(ci) +
            sparkles([(6, 8, 11, 0), (116, 14, 9, .5), (112, 110, 10, 1.0), (8, 104, 7, 1.4)]))

def hint(ci, pat):
    return (f'<circle class="glow" cx="60" cy="60" r="84" fill="url(#g-glow)"/>'
            + closed(ci, pat) + sparkles([(4, 6, 12, 0), (116, 10, 9, .6), (112, 112, 11, 1.1)]))

def cell_markup(state, r, c, pic):
    ci = (r * 2 + c) % 6
    pat = PATS[(r + c) % 3]
    if state == 'closed':
        return closed(ci, pat), ''
    if state == 'lifted':
        return pocket(pic), sliver(ci)
    if state == 'matched':
        return matched(pic, ci), ''
    if state == 'hint':
        return hint(ci, pat), ''
    raise ValueError(state)

def place(x, y, k, markup, cls=''):
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.4f})" class="{cls}">{markup}</g>'

# ---------------------------------------------------------------- scene
def clouds(p):
    def cloud(x, y, s, d):
        return (f'<g class="cloud" style="animation-delay:{d}s" transform="translate({x} {y}) scale({s})"><g fill="#FFF6E6" opacity=".92">'
                f'<ellipse cx="0" cy="0" rx="40" ry="13"/><ellipse cx="-18" cy="-8" rx="20" ry="14"/><ellipse cx="12" cy="-12" rx="24" ry="16"/></g></g>')
    return cloud(300, 44, 1, 0) + cloud(520, 24, .7, -6) + cloud(-260, 50, 1.1, -3) + cloud(1120, 40, 1, -9)

def tree(x, y, s):
    return (f'<g transform="translate({x} {y}) scale({s})"><rect x="-4" y="-26" width="8" height="30" rx="3" fill="#7A4E2E"/>'
            f'<circle cx="0" cy="-44" r="30" fill="#7FA05A"/><circle cx="-9" cy="-52" r="13" fill="#93B46C" opacity=".8"/></g>')

def wild(x, y, col, s=1):
    return (f'<g transform="translate({x} {y}) scale({s})"><path d="M0 0 V12" stroke="#5E7A3A" stroke-width="2" stroke-linecap="round"/>'
            f'<g fill="{col}"><circle cx="0" cy="-4" r="3.2"/><circle cx="4" cy="0" r="3.2"/><circle cx="0" cy="4" r="3.2"/><circle cx="-4" cy="0" r="3.2"/></g>'
            f'<circle cx="0" cy="0" r="2.4" fill="#FFF3C4"/></g>')

def basket(x, y):
    weave = ''.join(f'<path d="M{x + 6} {y + 18 + i * 10} H{x + 66}" stroke="#B9803F" stroke-width="2" opacity=".6"/>' for i in range(3))
    return (f'<ellipse cx="{x + 36}" cy="{y + 54}" rx="42" ry="7" fill="{INK}" opacity=".16"/>'
            f'<path d="M{x + 14} {y + 12} Q{x + 36} {y - 28} {x + 58} {y + 12}" fill="none" stroke="#B9803F" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="M{x + 2} {y + 8} H{x + 70} L{x + 62} {y + 50} Q{x + 36} {y + 56} {x + 10} {y + 50}Z" fill="#E2A957" stroke="#A8712F" stroke-width="3" stroke-linejoin="round"/>'
            + weave +
            f'<path d="M{x + 2} {y + 8} H{x + 70}" stroke="#A8712F" stroke-width="3" stroke-linecap="round"/>'
            f'<path d="M{x + 8} {y + 8} Q{x + 22} {y - 4} {x + 36} {y + 8} Q{x + 50} {y - 2} {x + 64} {y + 8}Z" fill="#F3D2DE" stroke="#C95F83" stroke-width="2" stroke-linejoin="round"/>'
            f'<circle cx="{x + 24}" cy="{y + 2}" r="8" fill="#E8504A" stroke="{INK}" stroke-width="2.5"/>'
            f'<path d="M{x + 24} {y - 5} q1 -5 4 -6" stroke="{INK}" stroke-width="2.5" fill="none" stroke-linecap="round"/>')

def scene(p, vb, rows=3, cols=4, cells=None, hud=True, hz=True):
    """960x600 design box. Sky, hills, meadow and cloth bleed far outside it so wide screens show no seam."""
    cells = cells or {}
    W = 6960
    X0 = -3000
    # cloth
    cx0, cy0, cw, ch = 56, 80, 576, 480
    # board geometry (cell size from the largest square that fits)
    avail_w, avail_h = 506, 392
    k_g = .12
    k_gy = .2
    cell = min((avail_w) / (cols + (cols - 1) * k_g), (avail_h) / (rows + (rows - 1) * k_gy), 150)
    gx, gy = cell * k_g, cell * k_gy
    bw, bh = cols * cell + (cols - 1) * gx, rows * cell + (rows - 1) * gy
    bx = cx0 + cw / 2 - bw / 2
    by = cy0 + ch / 2 - bh / 2 + 8
    k = cell / 120
    s = []
    s.append(f'''<defs>
<linearGradient id="{p}-sky" gradientUnits="userSpaceOnUse" x1="0" y1="-120" x2="0" y2="128"><stop offset="0" stop-color="#FFE6C2"/><stop offset="1" stop-color="#FFC6A0"/></linearGradient>
<radialGradient id="{p}-sun" gradientUnits="userSpaceOnUse" cx="140" cy="62" r="150"><stop offset="0" stop-color="#FFF0B8" stop-opacity=".95"/><stop offset=".35" stop-color="#FFE2A0" stop-opacity=".45"/><stop offset="1" stop-color="#FFE2A0" stop-opacity="0"/></radialGradient>
<linearGradient id="{p}-grass" gradientUnits="userSpaceOnUse" x1="0" y1="110" x2="0" y2="620"><stop offset="0" stop-color="#B2C26A"/><stop offset=".5" stop-color="#9DB45A"/><stop offset="1" stop-color="#86A24C"/></linearGradient>
<radialGradient id="{p}-warm" gradientUnits="userSpaceOnUse" cx="140" cy="62" r="900"><stop offset="0" stop-color="#FFE9B0" stop-opacity=".38"/><stop offset="1" stop-color="#FFE9B0" stop-opacity="0"/></radialGradient>
<pattern id="{p}-gingham" patternUnits="userSpaceOnUse" x="56" y="80" width="32" height="32"><rect width="32" height="32" fill="#FFF4DC"/><rect width="16" height="32" fill="#D98BA0" opacity=".28"/><rect width="32" height="16" fill="#D98BA0" opacity=".28"/></pattern>
<clipPath id="{p}-cloth-clip"><rect x="{cx0}" y="{cy0}" width="{cw}" height="{ch}" rx="24"/></clipPath>
</defs>''')
    # sky, sun, clouds
    s.append(f'<rect x="{X0}" y="-3000" width="{W}" height="3128" fill="url(#{p}-sky)"/>')
    s.append(f'<rect x="{X0}" y="-3000" width="{W}" height="3128" fill="url(#{p}-warm)"/>')
    s.append(f'<circle cx="140" cy="62" r="150" fill="url(#{p}-sun)"/><circle cx="140" cy="62" r="30" fill="#FFF3C4"/>')
    s.append(clouds(p))
    # far hills (mauve haze), mid hills (sage)
    s.append(f'<path d="M{X0} 700 V122 H-360 C-240 100 -120 72 20 82 C150 92 230 122 380 116 C520 110 640 74 790 80 C910 86 990 112 1120 122 H3960 V700Z" fill="#D5BBCB"/>')
    s.append(f'<path d="M{X0} 700 V134 H-300 C-170 126 -40 104 110 112 C260 120 330 140 470 136 C640 130 760 104 910 110 C1020 114 1090 128 1200 134 H3960 V700Z" fill="#B9C58C"/>')
    s.append(tree(-150, 128, 1) + tree(-60, 132, .7) + tree(1010, 126, 1) + tree(1100, 130, .8) + tree(848, 118, .62) + tree(884, 122, .45))
    # meadow
    s.append(f'<path d="M{X0} 3000 V150 H-300 C0 134 200 154 480 148 C760 142 900 128 1260 146 H3960 V3000Z" fill="url(#{p}-grass)"/>')
    # soft mowed bands, wide
    s.append(f'<path d="M{X0} 3000 V300 H3960 V3000Z" fill="#7C983F" opacity=".1"/>')
    # wildflowers, in and well outside the box
    wf = [(-260, 220, '#FF8DC0'), (-200, 300, '#FFD65C'), (-120, 190, '#fff'), (-90, 380, '#FF8DC0'), (-300, 430, '#fff'), (-180, 510, '#FFD65C'),
          (-40, 280, '#FFD65C'), (-30, 470, '#A594D6'), (-340, 330, '#A594D6'), (22, 580, '#FF8DC0'), (36, 166, '#fff'),
          (700, 560, '#FFD65C'), (668, 590, '#FF8DC0'), (940, 585, '#fff'), (990, 230, '#FF8DC0'), (1060, 300, '#FFD65C'), (1140, 200, '#fff'),
          (1180, 420, '#FF8DC0'), (1010, 520, '#A594D6'), (1250, 340, '#FFD65C'), (1100, 560, '#fff'), (1300, 250, '#A594D6'), (930, 170, '#FFD65C'),
          (338, 592, '#fff'), (210, 584, '#FFD65C'), (480, 590, '#A594D6')]
    s.append(''.join(wild(x, y, c, 1.15) for x, y, c in wf))
    # basket and Hazel
    if hz:
        s.append(basket(676, 470))
    # cloth: soft shadow, gingham, patchwork border, stitching
    s.append(f'<rect x="{cx0 + 4}" y="{cy0 + 12}" width="{cw}" height="{ch}" rx="24" fill="#4C6020" opacity=".22"/>')
    s.append(f'<rect x="{cx0}" y="{cy0}" width="{cw}" height="{ch}" rx="24" fill="url(#{p}-gingham)"/>')
    border = ''
    cols_b = [FABRIC[i][0] for i in (0, 1, 3, 4, 2, 5)]
    n_h, n_v = cw // 16, ch // 16
    for i in range(n_h):
        for row_y in (cy0, cy0 + ch - 16):
            border += f'<rect x="{cx0 + i * 16}" y="{row_y}" width="16" height="16" fill="{cols_b[(i + (row_y > cy0) * 3) % 6]}"/>'
    for j in range(1, n_v - 1):
        for col_x in (cx0, cx0 + cw - 16):
            border += f'<rect x="{col_x}" y="{cy0 + j * 16}" width="16" height="16" fill="{cols_b[(j + (col_x > cx0) * 2) % 6]}"/>'
    s.append(f'<g clip-path="url(#{p}-cloth-clip)">{border}<rect x="{cx0 + 16}" y="{cy0 + 16}" width="{cw - 32}" height="{ch - 32}" fill="none" stroke="#fff" stroke-width="2.5" stroke-dasharray="7 6" opacity=".9"/></g>')
    s.append(f'<rect x="{cx0}" y="{cy0}" width="{cw}" height="{ch}" rx="24" fill="none" stroke="#9E3F61" stroke-width="3" opacity=".5"/>')
    # cells: base layer then raised flaps on top
    tops = ''
    base = ''
    for r in range(rows):
        for c in range(cols):
            state, pic = cells.get((r, c), ('closed', None))
            m, top = cell_markup(state, r, c, pic)
            x, y = bx + c * (cell + gx), by + r * (cell + gy)
            cls = 'hopper' if state == 'matched' else ''
            if state == 'matched':
                # only the friend hops: keep it simple, hop the whole matched cell by a few px
                base += place(x, y, k, m, 'hopcell')
            else:
                base += place(x, y, k, m)
            if top:
                tops += place(x, y, k, top)
    s.append(base + tops)
    # Hazel and speech bubble
    if hz:
        s.append(hazel(p, 736, 322, 176))
        s.append(f'<g><path d="M790 254 L800 258 L806 322 Z" fill="#fff"/><rect x="700" y="196" width="230" height="62" rx="30" fill="#fff" stroke="#EADCC0" stroke-width="3"/>'
                 f'<path d="M788 255 L800 256 L806 318 Z" fill="#fff"/>'
                 f'<text x="815" y="234" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="600" fill="{INK}">Find two that match</text></g>')
    # HUD: back button (left), audio toggle (right)
    if hud:
        s.append(f'<g><circle cx="46" cy="42" r="22" fill="#0F857D"/><circle cx="46" cy="46" r="22" fill="#0A625C" opacity=".0"/>'
                 f'<path d="M52 30 L38 42 L52 54" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></g>')
        s.append(f'<g><circle cx="914" cy="42" r="22" fill="#fff" stroke="#EADCC0" stroke-width="3"/>'
                 f'<path d="M902 38 H908 L916 31 V53 L908 46 H902Z" fill="{INK}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
                 f'<path d="M921 36 Q927 42 921 48" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round"/></g>')
    return f'<svg viewBox="{vb}" class="scene" role="img" aria-label="Quilt Picnic scene">' + ''.join(s) + '</svg>'

MAIN_CELLS = {
    (0, 0): ('matched', 'ladybug'), (0, 1): ('closed', None), (0, 2): ('lifted', 'fox'), (0, 3): ('closed', None),
    (1, 0): ('closed', None), (1, 1): ('matched', 'ladybug'), (1, 2): ('matched', 'bee'), (1, 3): ('closed', None),
    (2, 0): ('closed', None), (2, 1): ('matched', 'bee'), (2, 2): ('closed', None), (2, 3): ('hint', None),
}

# ---------------------------------------------------------------- small figures
def tile(markup_base, markup_top='', label='', w=160, h=190, extra_defs=''):
    return (f'<figure class="fig"><svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" style="overflow:visible" role="img" aria-label="{label}">'
            f'{markup_base}{markup_top}</svg><figcaption>{label}</figcaption></figure>')

def state_tiles():
    out = []
    out.append(tile(place(20, 40, 1, closed(0, 'dots')), '', '<b>Closed</b><br>a stitched fabric flap with a button'))
    m, t = cell_markup('lifted', 0, 1, 'fox')
    out.append(tile(place(20, 40, 1, pocket('fox')), place(20, 40, 1, sliver(1)), '<b>Lifted</b><br>the flap folds up, a friend shows'))
    out.append(tile(place(20, 40, 1, matched('bee', 2), 'hopcell'), '', '<b>Matched pair</b><br>warm glow, sparkles, friend hops, flap stays up'))
    out.append(tile(place(20, 40, 1, hint(4, 'stripes')), '', '<b>Sparkle hint</b><br>one flap of an unfound pair twinkles'))
    # peek: 2x2 mini board, all flaps lifted together
    pk = ''
    tp = ''
    k = .56
    pics = ['apple', 'duck', 'duck', 'apple']
    for i in range(4):
        r, c = divmod(i, 2)
        x, y = 8 + c * (120 * k + 10), 34 + r * (120 * k + 20)
        pk += place(x, y, k, pocket(pics[i], '#B9A8E8', 3))
        tp += place(x, y, k, sliver((r * 2 + c) % 6))
    ring = '<rect x="0" y="12" width="156" height="170" rx="22" fill="#A594D6" opacity=".16"/><rect x="0" y="12" width="156" height="170" rx="22" fill="none" stroke="#A594D6" stroke-width="3" stroke-dasharray="3 7" stroke-linecap="round" class="glow"/>'
    out.append(tile(ring + pk, tp, '<b>Peek hint</b><br>after 3 misses every flap lifts together for 1.5 seconds'))
    return ''.join(out)

def mismatch_frames():
    k = .85
    def pair(stateA, stateB, label, extra=''):
        x1, x2 = 12, 140
        a = b = ''
        topa = topb = ''
        if stateA == 'lifted':
            a, topa = pocket('fox'), sliver(0)
            b, topb = pocket('apple'), sliver(1)
        elif stateA == 'closing':
            half = lambda pic, ci: (pocket(pic, op=.55) +
                                    f'<g style="transform:scaleY(.55);transform-origin:0 0">{closed(ci, PATS[ci % 3])}</g>')
            a, b = half('fox', 0), half('apple', 1)
        else:
            a, b = closed(0, 'dots'), closed(1, 'stripes')
        body = place(x1, 34, k, a) + place(x2, 34, k, b) + place(x1, 34, k, topa) + place(x2, 34, k, topb)
        return (f'<figure class="fig"><svg viewBox="0 0 260 150" width="260" height="150" style="overflow:visible" role="img" aria-label="{label}">{body}</svg>'
                f'<figcaption>{label}</figcaption></figure>')
    chev = '<svg class="chev" viewBox="0 0 24 40" width="24" height="40" aria-hidden="true"><path d="M5 5 L19 20 L5 35" fill="none" stroke="#0F857D" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    anim = (f'<figure class="fig"><svg viewBox="0 0 260 150" width="260" height="150" style="overflow:visible" role="img" aria-label="Looping demo of the gentle closing">'
            + place(12, 34, k, f'{base_shadow()}<rect width="120" height="120" rx="18" fill="#FFF4DC" stroke="#E0C28E" stroke-width="3"/><g class="pic-fade"><use href="#p-fox" x="16" y="18" width="88" height="88"/></g><g class="flap-close">{closed(0, "dots")}</g>')
            + place(140, 34, k, f'{base_shadow()}<rect width="120" height="120" rx="18" fill="#FFF4DC" stroke="#E0C28E" stroke-width="3"/><g class="pic-fade"><use href="#p-apple" x="16" y="18" width="88" height="88"/></g><g class="flap-close">{closed(1, "stripes")}</g>')
            + '</svg><figcaption><b>Looping demo</b><br>fade and settle, transform and opacity only</figcaption></figure>')
    return (pair('lifted', 'lifted', '<b>1. Two flaps up</b><br>two different friends')
            + chev + pair('closing', 'closing', '<b>2. A short pause, then they close</b><br>slow and soft, no sound, no colour change')
            + chev + pair('closed', 'closed', '<b>3. Closed again</b><br>nothing is counted or shown') + anim)

def reward_strip():
    cols = [0, 1, 2, 3, 4, 5, 0, 2]
    pics = ['ladybug', 'bee', 'rabbit', 'fox', 'apple', 'star', 'duck', 'snail']
    out = [f'<rect x="4" y="4" width="952" height="132" rx="30" fill="#FFF1D6" stroke="#E6BE8D" stroke-width="3"/>',
           f'<text x="32" y="58" font-family="{FONT}" font-size="26" font-weight="600" fill="#0F857D">Your Quilt</text>',
           f'<text x="32" y="86" font-family="{FONT}" font-size="15" fill="#6b5a4b">One patch per board</text>',
           f'<text x="32" y="108" font-family="{FONT}" font-size="15" fill="#6b5a4b">8 patches sewn</text>']
    for i in range(10):
        x = 226 + i * 72
        y = 34
        if i < 8:
            f, e, _ = FABRIC[cols[i]]
            out.append(f'<g transform="translate({x} {y})"><rect x="0" y="4" width="64" height="64" rx="10" fill="{INK}" opacity=".13"/>'
                       f'<rect width="64" height="64" rx="10" fill="{f}" stroke="{e}" stroke-width="3"/>'
                       f'<rect x="5" y="5" width="54" height="54" rx="7" fill="none" stroke="#fff" stroke-width="2" stroke-dasharray="5 4" opacity=".85"/>'
                       f'<rect x="13" y="13" width="38" height="38" rx="9" fill="#FFF4DC"/>'
                       f'<use href="#p-{pics[i]}" x="14" y="14" width="36" height="36"/>'
                       f'</g>')
        else:
            out.append(f'<g transform="translate({x} {y})" opacity=".5"><rect width="64" height="64" rx="10" fill="none" stroke="#B9703F" stroke-width="3" stroke-dasharray="7 6"/>'
                       f'<text x="32" y="44" text-anchor="middle" font-family="{FONT}" font-size="28" fill="#B9703F" opacity=".7">?</text></g>')
    return f'<svg viewBox="0 0 960 140" class="strip" role="img" aria-label="Your Quilt reward strip with eight sewn patches">{"".join(out)}</svg>'

def pictures_sheet():
    out = ''
    for k in PIC_IDS:
        out += (f'<figure class="pic"><svg viewBox="0 0 120 120" width="108" height="108" role="img" aria-label="{k}"><rect width="120" height="120" rx="18" fill="#FFF4DC" stroke="#E0C28E" stroke-width="3"/>'
                f'<use href="#p-{k}" x="10" y="10" width="100" height="100"/></svg><figcaption>{k}</figcaption></figure>')
    return out

def small_row(size):
    return ''.join(f'<svg viewBox="0 0 120 120" width="{size}" height="{size}" aria-label="{k}"><rect width="120" height="120" rx="18" fill="#FFF4DC" stroke="#E0C28E" stroke-width="3"/><use href="#p-{k}" x="10" y="10" width="100" height="100"/></svg>' for k in PIC_IDS)

def headroom_row():
    # pictures on a gridded box showing the 8..92 safe area, to prove nothing touches the edge
    out = ''
    for k in PIC_IDS:
        out += (f'<svg viewBox="0 0 100 100" width="84" height="84" role="img" aria-label="{k} with safe area"><rect width="100" height="100" fill="#fff" stroke="#E0C28E"/>'
                f'<rect x="6" y="6" width="88" height="88" fill="none" stroke="#2FB5EC" stroke-width=".8" stroke-dasharray="3 2"/><use href="#p-{k}" width="100" height="100"/></svg>')
    return out

def thumb_cells(rows, cols):
    n = rows * cols
    seq = PIC_IDS[:n // 2] * 2
    cells = {}
    for i in range(n):
        r, c = divmod(i, cols)
        cells[(r, c)] = ('closed', None)
    # one lifted flap so the picture size can be judged
    cells[(0, 1)] = ('lifted', 'fox')
    return cells

def palette():
    sw = [('#FFE6C2', 'sky top'), ('#FFC6A0', 'sky horizon'), ('#D5BBCB', 'far hills'), ('#B9C58C', 'near hills'), ('#B2C26A', 'meadow'),
          ('#FFF4DC', 'quilt cloth'), ('#C95F83', 'berry flap'), ('#E7AE3C', 'mustard flap'), ('#8FB07A', 'sage flap'), ('#A594D6', 'lavender flap'),
          ('#EE9262', 'terracotta flap'), ('#6DB7B0', 'teal flap'), ('#FFD65C', 'match glow')]
    return ''.join(f'<div class="sw"><span style="background:{c}">{c}</span><i>{n}</i></div>' for c, n in sw)

CSS = '''
:root{--cream:#FFF7E8;--ink:#3B2A20;--teal:#0F857D}
*{box-sizing:border-box}
body{margin:0;background:var(--cream);color:var(--ink);font-family:Andika,"Trebuchet MS","Segoe UI",system-ui,sans-serif;padding:24px 16px 60px}
main{max-width:980px;margin:0 auto}
h1,h2,h3{font-family:Fredoka,"Baloo 2","Trebuchet MS","Segoe UI",system-ui,sans-serif}
h1{color:var(--teal);margin:0 0 4px} h2{margin:44px 0 8px} h3{margin:24px 0 10px}
p{line-height:1.5;max-width:72ch}
.scene{width:100%;height:auto;border-radius:32px;box-shadow:0 10px 30px rgba(90,50,20,.28);display:block;background:#FFD9B3}
.wide{overflow:hidden;border-radius:32px;box-shadow:0 10px 30px rgba(90,50,20,.28)} .wide .scene{border-radius:0;box-shadow:none}
.row{display:flex;flex-wrap:wrap;gap:16px;align-items:flex-end}
.fig{margin:0;text-align:center;background:linear-gradient(#FFF1D6,#F6E2B8);border-radius:24px;padding:10px 14px 12px;box-shadow:0 6px 18px rgba(90,50,20,.16)}
.fig svg{display:block;margin:0 auto;max-width:100%;height:auto}
.fig figcaption{font-size:14px;margin-top:6px;line-height:1.35;max-width:190px}
.row.three .fig figcaption{max-width:260px}
.pic{margin:0;text-align:center} .pic figcaption{font-size:13px;margin-top:2px}
.pics{display:grid;grid-template-columns:repeat(auto-fill,minmax(112px,1fr));gap:10px}
.chev{align-self:center}
.strip{width:100%;height:auto;display:block;filter:drop-shadow(0 6px 14px rgba(90,50,20,.16))}
.small{display:flex;flex-wrap:wrap;gap:6px;align-items:center;background:#fff;border-radius:16px;padding:10px}
.note{background:#fff;border-left:6px solid var(--teal);border-radius:12px;padding:10px 16px;max-width:72ch}
.sw{display:flex;align-items:center;gap:10px;margin:4px 0}.sw span{display:inline-block;width:92px;text-align:center;border-radius:8px;padding:6px 0;font:600 14px Andika,system-ui;border:1px solid #0002}.sw i{color:#6b5a4b;font-size:14px}
.pal{columns:2 320px}
.thumbs{display:flex;flex-wrap:wrap;gap:16px;align-items:flex-start}
.thumbs figure{margin:0;flex:1 1 280px;max-width:430px}.thumbs figcaption{font-size:14px;margin-top:6px;line-height:1.35}
.thumbs .scene{border-radius:16px}
code{background:#fff;padding:1px 6px;border-radius:6px;font-size:14px}
.glow,.sparkle,.hopcell,.cloud,.hz-wave,.hz-bob,.hz-blink,.pic-fade,.flap-close{transform-box:fill-box;transform-origin:center}
@keyframes gp{0%,100%{opacity:.55}50%{opacity:1}} .glow{animation:gp 2.6s ease-in-out infinite}
@keyframes sp{0%,100%{opacity:.5;transform:scale(.7)}50%{opacity:1;transform:scale(1.15)}} .sparkle{animation:sp 2s ease-in-out infinite}
@keyframes hop{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}} .hopcell{animation:hop 1.4s ease-in-out infinite}
@keyframes drift{from{transform:translateX(0)}to{transform:translateX(46px)}} .cloud{animation:drift 40s ease-in-out infinite alternate}
@keyframes wave{0%,60%,100%{transform:rotate(0)}70%{transform:rotate(-32deg)}80%{transform:rotate(-12deg)}90%{transform:rotate(-30deg)}} .hz-wave{animation:wave 6s ease-in-out infinite}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}} .hz-bob{animation:bob 3.4s ease-in-out infinite}
@keyframes blink{0%,94%,100%{transform:scaleY(1)}97%{transform:scaleY(.1)}} .hz-blink{animation:blink 5s linear infinite}
/* gentle closing demo: closed look is the base, the loop starts with the friend showing */
.pic-fade{opacity:0}.flap-close{opacity:1}
@keyframes pf{0%,40%{opacity:1}60%,92%{opacity:0}100%{opacity:1}}
@keyframes fc{0%,10%{opacity:0;transform:scaleY(.3)}22%{opacity:.0;transform:scaleY(.3)}30%{opacity:1;transform:scaleY(.3)}60%,92%{opacity:1;transform:scaleY(1)}100%{opacity:0;transform:scaleY(.3)}}
.pic-fade{animation:pf 6s ease-in-out infinite}.flap-close{transform-origin:50% 0;animation:fc 6s cubic-bezier(.34,1.2,.64,1) infinite}
@media (prefers-reduced-motion:reduce){.glow,.sparkle,.hopcell,.cloud,.hz-wave,.hz-bob,.hz-blink,.pic-fade,.flap-close{animation:none}
.glow{opacity:.85}.sparkle{opacity:1}}
'''

def build():
    defs = f'''<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<radialGradient id="g-glow"><stop offset="0" stop-color="#FFD65C" stop-opacity=".75"/><stop offset=".55" stop-color="#FFD65C" stop-opacity=".28"/><stop offset="1" stop-color="#FFD65C" stop-opacity="0"/></radialGradient>
<pattern id="pat-dots" patternUnits="userSpaceOnUse" width="18" height="18"><circle cx="9" cy="9" r="3" fill="#fff" opacity=".32"/></pattern>
<pattern id="pat-stripes" patternUnits="userSpaceOnUse" width="14" height="14" patternTransform="rotate(45)"><rect width="5" height="14" fill="#fff" opacity=".24"/></pattern>
<pattern id="pat-checks" patternUnits="userSpaceOnUse" width="24" height="24"><rect width="12" height="12" fill="#fff" opacity=".22"/><rect x="12" y="12" width="12" height="12" fill="#fff" opacity=".22"/></pattern>
{symbols()}</defs></svg>'''
    main_scene = scene('m', '0 0 960 600', 3, 4, MAIN_CELLS)
    wide_scene = scene('w', '-320 0 1600 600', 3, 4, MAIN_CELLS)
    t22 = scene('t22', '0 0 960 600', 2, 2, thumb_cells(2, 2))
    t34 = scene('t34', '0 0 960 600', 3, 4, thumb_cells(3, 4))
    t44 = scene('t44', '0 0 960 600', 4, 4, thumb_cells(4, 4))
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Quilt Picnic art preview</title>
<style>{CSS}</style></head><body>{defs}<main>
<h1>Quilt Picnic: art direction preview</h1>
<p>Static prototype for approval. Nothing here is the final game. It shows a cozy afternoon meadow with a patchwork quilt, the board of fabric flaps, the five flap states, sixteen friend pictures, the "Your Quilt" reward strip and the quiet way a mismatch closes. Hazel is the picnic host.
Same bones as the garden, the pond and the workshop (rounded shapes, one outline weight, ink on light, teal for UI), in a fourth mood: golden afternoon, apricot sky, mauve hills and olive grass. Scenes are 960 x 600. Everything on this page is a local file with no external requests, so headings use a system rounded font here (the real game ships subset Fredoka and Andika).</p>

<h2>1. The meadow mid-game (3 x 4 board, level 4)</h2>
<p>Four flaps are matched (two ladybugs, two bees, glowing with the friend hopping), one flap is up on its own (the fox), one closed flap twinkles as the sparkle hint, and six are still closed. The voice says "Find two that match", shown here as Hazel's bubble. The back button and audio toggle sit in the top corners.</p>
{main_scene}

<h2>1b. Same scene on a wide screen (1600 x 600 window)</h2>
<p>The sky, hills, grass, clouds, trees and flowers are drawn thousands of units past the 960 x 600 box, and every gradient is in <code>userSpaceOnUse</code>. A wide tablet or a desktop sees more meadow and no seam. The quilt, board and Hazel stay in the 960 box.</p>
<div class="wide">{wide_scene}</div>

<h2>2. Flap states</h2>
<p>The flap is one rounded fabric square. Closed: stitched border, a button, and a fabric pattern (dots, stripes, checks) so the board looks like a real patchwork. The six fabric colours rotate so no two neighbours match, which is a handy landmark for remembering where things are. Lifting folds the flap up and back (a small sliver stays above the pocket), so a 3D card flip is not needed.</p>
<div class="row">{state_tiles()}</div>

<h2>3. Friends (16 pictures)</h2>
<p>Hand-drawn SVG, one 3 px ink outline, flat fills, big eyes and cheeks where there is a face. Each viewBox is 100 x 100 and the art stays inside 8 to 92, so ears, antennae, spikes and stems keep headroom. Ladybug, snail, bee and rabbit link to earlier games. These ids become the game's item ids.</p>
<div class="pics">{pictures_sheet()}</div>
<h3>Small size check (48 px and 32 px)</h3>
<div class="small">{small_row(48)}</div>
<div class="small" style="margin-top:8px">{small_row(32)}</div>
<h3>Headroom check (dashed blue line is the 6 to 94 safe box)</h3>
<div class="small">{headroom_row()}</div>

<h2>4. Your Quilt (reward strip, owned by the website)</h2>
<p>One patch is sewn for each finished board and stored as facts on the child's profile. It appears on the website and at the start and end of a session. Nothing is lost, nothing resets, no streak. Unsewn slots are faded outlines.</p>
{reward_strip()}

<h2>5. A mismatch is quiet</h2>
<p>Two different friends: both flaps stay up for a short moment, then fold back down slowly. No buzzer, no red, no cross, no shake, no counter. The child is never told they missed. The last card is a live loop of the closing.</p>
<div class="row three">{mismatch_frames()}</div>

<h2>6. Board sizes (the whole scene, scaled down)</h2>
<p>The board area is fixed and the cell size is the biggest square that fits. At 960 x 600: 2 x 2 cells are 150 px (capped), 3 x 4 cells are 116 px, 4 x 4 cells are about 86 px. One flap is lifted in each so the picture size can be judged.</p>
<div class="thumbs">
<figure>{t22}<figcaption><b>2 x 2</b> (level 1): 2 pairs, 150 px cells</figcaption></figure>
<figure>{t34}<figcaption><b>3 x 4</b> (level 4): 6 pairs, 116 px cells</figcaption></figure>
<figure>{t44}<figcaption><b>4 x 4</b> (level 5): 8 pairs, about 86 px cells</figcaption></figure>
</div>

<h2>7. Palette and motion notes</h2>
<div class="pal">{palette()}</div>
<p class="note">Distinct from the earlier games: the garden is sunny blue and bright green, the pond is dusk navy and purple, the workshop is warm wood and paper. Quilt Picnic is apricot, mauve and olive with fabric colours (berry, mustard, sage, lavender, terracotta, teal). No red is used for feedback. The match glow is warm gold.</p>
<p class="note">Motion uses transform and opacity only: soft glow pulse, sparkle twinkle, the matched friend hop, slow clouds, Hazel's idle bob, blink and a small wave, and the gentle flap closing. With <code>prefers-reduced-motion</code> every loop stops and each state keeps a still version (glow stays lit, sparkles stay visible, the flap closing demo shows the closed state).</p>
</main></body></html>'''
    open('index.html', 'w').write(html)
    print(len(html), 'bytes')

build()
