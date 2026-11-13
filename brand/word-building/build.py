# Builds scene.ts, index.html and fit.html for the Letter Workshop art preview.
# Run from this folder: python3 build.py
# Why a script: Hazel is reused from brand/mascot/owl.svg (source of truth), and the same strings feed both the
# preview page and the scene.ts module the game skin will import, so the two cannot drift apart.
import json
import re

OUT = '#6B4129'   # one outline colour for the whole cast
LINE = 2.5        # one outline weight for the whole cast (same as garden and pond)
INK = '#3B2A20'

# ------------------------------------------------------------------ Hazel (reused, not redrawn)
owl = open('../mascot/owl.svg').read().strip()
owl = re.sub(r'^<svg[^>]*>', '', owl)
owl = owl[:owl.rindex('</svg>')]
owl = re.sub(r'<title>.*?</title>', '', owl, flags=re.S)
owl = re.sub(r'<!--.*?-->', '', owl, flags=re.S)
owl_defs = re.search(r'<defs>(.*?)</defs>', owl, flags=re.S).group(1).replace('id="g-', 'id="ell-wb-hz-g-')
owl_body = re.sub(r'<defs>.*?</defs>', '', owl, flags=re.S).replace('url(#g-', 'url(#ell-wb-hz-g-')
owl_body = owl_body.replace('<ellipse id="shadow" cx="120" cy="254" rx="62" ry="7" fill="#3B2A20" opacity=".12"/>', '')


def hazel_variant(point=False, cheer=False):
    b = owl_body
    if point:  # left wing (viewer's left) raised toward the easel, head tilted, gaze to the picture
        b = b.replace('<g id="wing-left" class="part" style="transform-origin:68px 178px">', '<g transform="rotate(62 68 178)">')
        b = b.replace('<g id="head" class="part" style="transform-origin:120px 168px">', '<g transform="rotate(-4 120 168)">')
        b = b.replace('<g class="look">', '<g transform="translate(-6 1)">')
    if cheer:
        b = b.replace('<g id="wing-right" class="part" style="transform-origin:172px 178px">', '<g transform="rotate(-75 172 178)">')
        b = b.replace('<g id="wing-left" class="part" style="transform-origin:68px 178px">', '<g transform="rotate(75 68 178)">')
        b = b.replace('<g id="eyes-happy" opacity="0"', '<g id="eyes-happy" opacity="1"')
        b = b.replace('id="eye-left" class="part"', 'opacity="0"').replace('id="eye-right" class="part"', 'opacity="0"')
        b = b.replace('<path id="beak-lower" class="part" style="transform-origin:120px 138px"', '<path transform="translate(0 3)"')
    b = re.sub(r' id="[^"]*"', '', b)
    b = re.sub(r' class="(part|look|pupil)"', '', b)
    b = re.sub(r' style="transform-origin:[^"]*"', '', b)
    b = re.sub(r'\s*\n\s*', '', b)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-20 -16 280 290" overflow="visible" style="overflow:visible" '
            f'role="img" aria-label="Hazel the owl"><defs>{owl_defs}</defs>{b}</svg>')


HAZEL = {'neutral': hazel_variant(), 'point': hazel_variant(point=True), 'cheer': hazel_variant(cheer=True)}
HAZEL_VB = (-20, -16, 280, 290)
HAZEL_ANCHOR = (120, 252)

# ------------------------------------------------------------------ palette (name, hex, use)
PAL = [
    ('Wall paper top', '#F8E6C6', 'backdrop'), ('Wall paper low', '#EBCB98', 'backdrop'), ('Floor light', '#A9744A', 'backdrop'),
    ('Floor dark', '#7A4E2E', 'backdrop'), ('Bench maple', '#E4B079', 'bench'), ('Bench maple low', '#D3995C', 'bench'),
    ('Bench back rail', '#B9804C', 'bench'), ('Tray inside', '#A8703F', 'tray'), ('Tray rim', '#E0A765', 'tray'),
    ('Slot recess', '#7E4D2B', 'slot'), ('Slot shadow', '#5E3820', 'slot'), ('Slot hint gold', '#FFD45C', 'slot'),
    ('Tile face', '#FFF3D6', 'tile'), ('Tile edge', '#D9A464', 'tile'), ('Tile lit', '#FFF1A8', 'tile'),
    ('Tile lit rim', '#2FCB86', 'tile'), ('Tile wobble rim', '#FF9F43', 'tile'), ('Letter ink', '#3B2A20', 'letters'),
    ('Lamp shade', '#FFD98A', 'lamp'), ('Brass', '#D9A93F', 'lamp'), ('Walnut', '#8A5A35', 'easel, shelves'),
    ('Frame caramel', '#C8996A', 'easel frame'), ('Mouse fur', '#CDBFD9', 'cast'), ('Hedgehog spikes', '#8A5B3C', 'cast'),
    ('Bunny fur', '#FFFDF9', 'cast'), ('Robin brown', '#8A6A55', 'cast'), ('Robin breast', '#F0743E', 'cast'),
    ('Cheek pink', '#FF92C8', 'cast'), ('Teal (brand)', '#0F857D', 'UI'), ('Sun', '#FFC83D', 'glow, sparkles'),
]

# ------------------------------------------------------------------ shared drawing bits
def eyes_open(cx1, cx2, cy, rx=8, ry=9, px=0, py=1.5):
    out = ''
    for cx in (cx1, cx2):
        out += (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#fff" stroke="{OUT}" stroke-width="1.5"/>'
                f'<circle cx="{cx + px}" cy="{cy + py}" r="{rx * 0.62:.1f}" fill="{INK}"/>'
                f'<circle cx="{cx + px + 2}" cy="{cy + py - 2}" r="2" fill="#fff"/>')
    return out


def eyes_happy(cx1, cx2, cy, w=8):
    return ''.join(f'<path d="M{c - w} {cy + 2} Q{c} {cy - 9} {c + w} {cy + 2}" stroke="{INK}" stroke-width="3.2" fill="none" stroke-linecap="round"/>' for c in (cx1, cx2))


def cheeks(x1, x2, y, rx=7, ry=4.5):
    return ''.join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#FF92C8" opacity=".7"/>' for x in (x1, x2))


def smile(x, y, w=7):
    return f'<path d="M{x - w} {y} Q{x} {y + 7} {x + w} {y}" stroke="{INK}" stroke-width="2.6" fill="none" stroke-linecap="round"/>'


def open_mouth(x, y, w=11):
    return (f'<path d="M{x - w} {y} Q{x} {y + 22} {x + w} {y} Z" fill="#8F3B34" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>'
            f'<path d="M{x - w + 4} {y + 9} Q{x} {y + 15} {x + w - 4} {y + 9} Q{x} {y + 5} {x - w + 4} {y + 9}Z" fill="#F58AA8"/>')


def sparkle(x, y, s=1.0, fill='#FFE066'):
    return (f'<g transform="translate({x} {y}) scale({s})"><path class="wb-sparkle" d="M0 -9 L2.6 -2.6 L9 0 L2.6 2.6 L0 9 L-2.6 2.6 L-9 0 L-2.6 -2.6Z" '
            f'fill="{fill}" stroke="#E0A91C" stroke-width="1" stroke-linejoin="round"/></g>')


def tube(d, w, col):
    return (f'<path d="{d}" fill="none" stroke="{OUT}" stroke-width="{w + 2 * LINE}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')


def paw(cx, cy, r, col):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{col}" stroke="{OUT}" stroke-width="{LINE}"/>'


def picture_card_inner(w=48, h=58):
    """Paper card with a tiny placeholder picture. Origin top left."""
    return (f'<rect x="0" y="0" width="{w}" height="{h}" rx="7" fill="#FFFFFF" stroke="#C8996A" stroke-width="2.5"/>'
            f'<rect x="5" y="5" width="{w - 10}" height="{h - 14}" rx="4" fill="#CBEBF6"/>'
            f'<path d="M5 {h - 18} Q{w * .35:.0f} {h - 32} {w * .6:.0f} {h - 20} Q{w * .8:.0f} {h - 26} {w - 5} {h - 20} V{h - 9} Q{w - 5} {h - 9} {w - 9} {h - 9} H9 Q5 {h - 9} 5 {h - 13}Z" fill="#7BD39A"/>'
            f'<circle cx="{w * .7:.0f}" cy="17" r="6" fill="#FFC83D"/>')


def card_at(cx, cy, w=48, h=58, rot=0):
    return (f'<g transform="translate({cx} {cy}) rotate({rot}) translate({-w / 2} {-h / 2})">'
            f'<rect x="1" y="3" width="{w}" height="{h}" rx="7" fill="#3B2A20" opacity=".12"/>{picture_card_inner(w, h)}</g>')


PICTURE_CARD = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-6 -6 60 70" overflow="visible" style="overflow:visible" role="img" aria-label="Picture card">'
                f'{picture_card_inner()}</svg>')

# ------------------------------------------------------------------ cast
# Each character is drawn in a "-20 -20 240 270" box (content inside 0..200 x 8..232, so ears and spikes have headroom).
CAST_VB = (-20, -20, 240, 270)
CAST_FEET = 228


def cast_wrap(inner, name, state, happy=False):
    hop = '<g class="wb-hop" transform="translate(0 -9)">' if happy else '<g>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-20 -20 240 270" overflow="visible" style="overflow:visible" role="img" aria-label="{name}, {state}">'
            f'<ellipse cx="100" cy="229" rx="52" ry="7" fill="{INK}" opacity=".16"/>{hop}{inner}</g></svg>')


def arms(state, col, paw_col=None, wing=False):
    """Arms and paws for the three states, plus the card. Anchors are shared so every character holds the card the same way."""
    pc = paw_col or col
    w = 15
    r = 9.5
    if state == 'idle':
        card = card_at(100, 192, 48, 58)
        a = tube('M64 158 Q54 184 80 192', w, col) + tube('M136 158 Q146 184 120 192', w, col) + paw(80, 192, r, pc) + paw(120, 192, r, pc)
        return card + a
    if state == 'happy':
        a = tube('M64 160 Q26 160 30 118', w, col) + tube('M136 160 Q174 160 170 118', w, col) + paw(30, 116, r, pc) + paw(170, 116, r, pc)
        return a
    # wave: viewer's left arm holds the card low, right arm up and waving
    card = card_at(50, 194, 40, 48, -10)
    a = tube('M64 160 Q46 186 64 198', w, col) + paw(64, 198, r, pc)
    a += tube('M138 160 Q172 150 170 108', w, col) + paw(170, 104, r, pc)
    a += (f'<path d="M186 88 Q198 100 188 118" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round" opacity=".55"/>'
          f'<path d="M192 78 Q210 98 194 126" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round" opacity=".35"/>')
    return card + a


def face_expr(state, ex1, ex2, ey, mouth_x, mouth_y, cheek_y, open_w=11):
    if state == 'happy':
        return eyes_happy(ex1, ex2, ey, 8) + open_mouth(mouth_x, mouth_y, open_w) + cheeks(ex1 - 14, ex2 + 14, cheek_y)
    return eyes_open(ex1, ex2, ey, 8, 9, 0, 1.5) + smile(mouth_x, mouth_y, 7) + cheeks(ex1 - 14, ex2 + 14, cheek_y)


def mouse(state):
    M, MB, P = '#CDBFD9', '#F1E8F4', '#F7A7C4'
    tail = f'<path d="M134 206 Q184 214 176 168 Q172 146 190 138" fill="none" stroke="{OUT}" stroke-width="10.5" stroke-linecap="round"/><path d="M134 206 Q184 214 176 168 Q172 146 190 138" fill="none" stroke="#F5A9BE" stroke-width="5.5" stroke-linecap="round"/>'
    feet = f'<ellipse cx="80" cy="224" rx="18" ry="9" fill="{M}" stroke="{OUT}" stroke-width="{LINE}"/><ellipse cx="120" cy="224" rx="18" ry="9" fill="{M}" stroke="{OUT}" stroke-width="{LINE}"/>'
    body = (f'<ellipse cx="100" cy="182" rx="40" ry="46" fill="{M}" stroke="{OUT}" stroke-width="{LINE}"/>'
            f'<ellipse cx="100" cy="190" rx="26" ry="34" fill="{MB}"/>')
    ears = ''.join(f'<circle cx="{x}" cy="64" r="26" fill="{M}" stroke="{OUT}" stroke-width="{LINE}"/><circle cx="{x}" cy="64" r="15" fill="{P}"/>' for x in (54, 146))
    head = f'<circle cx="100" cy="106" r="52" fill="{M}" stroke="{OUT}" stroke-width="{LINE}"/>'
    whisk = ''.join(f'<path d="M{x0} {y0} L{x1} {y1}" stroke="{OUT}" stroke-width="1.8" stroke-linecap="round" opacity=".7"/>'
                    for x0, y0, x1, y1 in [(78, 116, 44, 108), (78, 122, 44, 126), (122, 116, 156, 108), (122, 122, 156, 126)])
    nose = f'<ellipse cx="100" cy="112" rx="7" ry="5" fill="#F27FA8" stroke="{OUT}" stroke-width="1.8"/>'
    teeth = '' if state == 'happy' else f'<rect x="95" y="128" width="10" height="8" rx="2.5" fill="#fff" stroke="{OUT}" stroke-width="1.5"/>'
    face = whisk + nose + face_expr(state, 78, 122, 96, 100, 122, 120) + teeth
    inner = tail + feet + body + ears + head + face + arms(state, M, M)
    if state == 'happy':
        inner += sparkle(8, 70, 1.0) + sparkle(194, 52, .8) + sparkle(172, 20, .6)
    return cast_wrap(inner, 'Mouse', state, state == 'happy')


def hedgehog(state):
    SP, SPL, FACE, SK = '#8A5B3C', '#B07A52', '#F2D6B0', '#EBC9A0'
    # spike ring behind everything: 24 rounded triangles around (100,130)
    import math
    cx, cy, r0, r1, n = 100, 132, 66, 86, 26
    pts = []
    for i in range(n * 2):
        a = math.pi * 2 * i / (n * 2) - math.pi / 2
        r = r1 if i % 2 == 0 else r0
        pts.append(f'{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}')
    spikes = f'<polygon points="{" ".join(pts)}" fill="{SP}" stroke="{OUT}" stroke-width="{LINE}" stroke-linejoin="round"/>'
    spikes += f'<circle cx="{cx}" cy="{cy}" r="{r0 - 2}" fill="#7A4D32"/>'
    # a few lighter spike tips for texture
    tips = ''.join(f'<path d="M{x} {y} l3 -9" stroke="{SPL}" stroke-width="3" stroke-linecap="round" opacity=".8"/>' for x, y in [(52, 74), (78, 58), (122, 58), (148, 74), (30, 112), (170, 112)])
    feet = f'<ellipse cx="80" cy="224" rx="18" ry="9" fill="{SK}" stroke="{OUT}" stroke-width="{LINE}"/><ellipse cx="120" cy="224" rx="18" ry="9" fill="{SK}" stroke="{OUT}" stroke-width="{LINE}"/>'
    body = (f'<ellipse cx="100" cy="184" rx="38" ry="44" fill="{SK}" stroke="{OUT}" stroke-width="{LINE}"/>'
            f'<ellipse cx="100" cy="192" rx="25" ry="32" fill="#FFF0D6"/>')
    head = (f'<circle cx="100" cy="116" r="48" fill="{SP}" stroke="{OUT}" stroke-width="{LINE}"/>'
            f'<circle cx="100" cy="124" r="39" fill="{FACE}"/>')
    ears = ''.join(f'<circle cx="{x}" cy="88" r="13" fill="{SK}" stroke="{OUT}" stroke-width="{LINE}"/><circle cx="{x}" cy="89" r="7" fill="#F7A7C4"/>' for x in (58, 142))
    muzzle = f'<ellipse cx="100" cy="132" rx="19" ry="14" fill="#FFEBD0"/><ellipse cx="100" cy="126" rx="7.5" ry="5.5" fill="{INK}"/><circle cx="98" cy="124" r="1.8" fill="#fff"/>'
    face = muzzle + face_expr(state, 78, 122, 112, 100, 138, 130, 9)
    inner = spikes + tips + feet + body + head + ears + face + arms(state, SK, SK)
    if state == 'happy':
        inner += sparkle(4, 80, 1.0) + sparkle(196, 70, .8) + sparkle(168, 22, .6)
    return cast_wrap(inner, 'Hedgehog', state, state == 'happy')


def bunny(state):
    F, FB, PI = '#FFFDF9', '#FFE9DA', '#FFB3CF'
    lean = 22 if state == 'happy' else 8
    ears = ''
    for sgn, x in ((-1, 76), (1, 124)):
        ears += (f'<g transform="rotate({sgn * lean} {x} 74)"><ellipse cx="{x}" cy="34" rx="17" ry="45" fill="{F}" stroke="{OUT}" stroke-width="{LINE}"/>'
                 f'<ellipse cx="{x}" cy="38" rx="8" ry="32" fill="{PI}"/></g>')
    tail = f'<circle cx="150" cy="212" r="14" fill="{F}" stroke="{OUT}" stroke-width="{LINE}"/>'
    feet = (f'<ellipse cx="78" cy="224" rx="22" ry="9" fill="{F}" stroke="{OUT}" stroke-width="{LINE}"/><ellipse cx="122" cy="224" rx="22" ry="9" fill="{F}" stroke="{OUT}" stroke-width="{LINE}"/>')
    body = (f'<ellipse cx="100" cy="184" rx="40" ry="44" fill="{F}" stroke="{OUT}" stroke-width="{LINE}"/>'
            f'<ellipse cx="100" cy="192" rx="26" ry="32" fill="{FB}"/>')
    head = f'<circle cx="100" cy="108" r="50" fill="{F}" stroke="{OUT}" stroke-width="{LINE}"/>'
    nose = f'<path d="M93 112 Q100 107 107 112 Q104 119 100 119 Q96 119 93 112Z" fill="#F27FA8" stroke="{OUT}" stroke-width="1.8" stroke-linejoin="round"/>'
    if state == 'happy':
        mouth = open_mouth(100, 124, 10)
    else:
        mouth = (f'<path d="M100 119 V124 M100 124 Q93 131 86 125 M100 124 Q107 131 114 125" fill="none" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/>'
                 f'<rect x="95.5" y="127" width="9" height="9" rx="2.5" fill="#fff" stroke="{OUT}" stroke-width="1.5"/>')
    eyes = eyes_happy(78, 122, 98, 8) if state == 'happy' else eyes_open(78, 122, 98, 8, 9.5, 0, 1.5)
    face = nose + mouth + eyes + cheeks(62, 138, 118)
    inner = ears + tail + feet + body + head + face + arms(state, F, F)
    if state == 'happy':
        inner += sparkle(6, 96, 1.0) + sparkle(196, 90, .8) + sparkle(24, 150, .6)
    return cast_wrap(inner, 'Bunny', state, state == 'happy')


def robin(state):
    BR, BRL, OR, BK = '#8A6A55', '#A98770', '#F0743E', '#FFC03D'
    tail = (f'<ellipse cx="152" cy="212" rx="17" ry="8" transform="rotate(28 150 212)" fill="{BR}" stroke="{OUT}" stroke-width="{LINE}"/>'
            f'<ellipse cx="146" cy="218" rx="16" ry="7" transform="rotate(8 144 218)" fill="#7A5A47" stroke="{OUT}" stroke-width="{LINE}"/>')
    legs = ''.join(f'<path d="M{x} 218 V230 M{x - 8} 232 H{x + 8}" stroke="#E8973A" stroke-width="5" stroke-linecap="round" fill="none"/>' for x in (86, 114))
    body = (f'<ellipse cx="100" cy="176" rx="46" ry="50" fill="{BR}" stroke="{OUT}" stroke-width="{LINE}"/>'
            f'<ellipse cx="100" cy="186" rx="33" ry="38" fill="{OR}"/>'
            f'<path d="M80 200 q5 6 10 0 M96 204 q5 6 10 0 M112 200 q5 6 10 0" fill="none" stroke="#C9552A" stroke-width="2.6" stroke-linecap="round" opacity=".7"/>')
    crest = f'<path d="M92 56 Q90 40 98 36 Q98 46 104 54 Q108 42 118 42 Q112 50 112 58Z" fill="{BR}" stroke="{OUT}" stroke-width="{LINE}" stroke-linejoin="round"/>'
    head = (f'<circle cx="100" cy="102" r="52" fill="{BR}" stroke="{OUT}" stroke-width="{LINE}"/>'
            f'<ellipse cx="100" cy="116" rx="40" ry="34" fill="{OR}"/>'
            f'<ellipse cx="100" cy="116" rx="40" ry="34" fill="none" stroke="#E56430" stroke-width="1.5" opacity=".6"/>')
    if state == 'happy':
        beak = (f'<path d="M86 108 Q100 98 114 108 Q108 114 100 114 Q92 114 86 108Z" fill="{BK}" stroke="#C98A1E" stroke-width="2" stroke-linejoin="round"/>'
                f'<path d="M88 114 Q100 132 112 114 Q100 120 88 114Z" fill="#E8973A" stroke="#C98A1E" stroke-width="2" stroke-linejoin="round"/>')
        eyes = eyes_happy(78, 122, 92, 8)
    else:
        beak = f'<path d="M87 108 Q100 98 113 108 Q108 122 100 124 Q92 122 87 108Z" fill="{BK}" stroke="#C98A1E" stroke-width="2" stroke-linejoin="round"/><path d="M92 110 Q100 106 108 110" fill="none" stroke="#FFE49A" stroke-width="2.4" stroke-linecap="round"/>'
        eyes = eyes_open(78, 122, 94, 8, 9, 0, 1.5)
    face = beak + eyes + cheeks(58, 142, 118, 6, 4)
    inner = tail + legs + body + crest + head + face + arms(state, '#7A5A47', '#7A5A47')
    if state == 'happy':
        inner += sparkle(6, 78, 1.0) + sparkle(196, 66, .8) + sparkle(172, 20, .6)
    return cast_wrap(inner, 'Robin', state, state == 'happy')


CAST = {name: {s: fn(s) for s in ('idle', 'happy', 'wave')} for name, fn in
        (('mouse', mouse), ('hedgehog', hedgehog), ('bunny', bunny), ('robin', robin))}

# ------------------------------------------------------------------ letter glyphs (stroked, no font needed)
# Unit box: x-height top 22, baseline 58, ascender 4, descender 76 (stroke centrelines). Stroke width 8, round caps.
G = {
    'a': ('<circle cx="19" cy="40" r="17"/><path d="M36 22 V58"/>', 20),
    'b': ('<path d="M6 4 V58"/><circle cx="23" cy="40" r="17"/>', 20),
    'c': ('<path d="M34.7 29.7 A18 18 0 1 0 34.7 50.3"/>', 19),
    'd': ('<path d="M34 4 V58"/><circle cx="17" cy="40" r="17"/>', 20),
    'e': ('<path d="M3 40 H37 A17 17 0 1 0 33 50.9"/>', 20),
    'f': ('<path d="M18 58 V18 Q18 4 32 6 M6 24 H30"/>', 19),
    'g': ('<circle cx="19" cy="40" r="17"/><path d="M36 22 V62 Q36 76 20 76 Q10 76 6 70"/>', 20),
    'h': ('<path d="M6 4 V58 M6 38 Q6 22 20 22 Q34 22 34 38 V58"/>', 20),
    'i': ('<path d="M20 22 V58"/><circle cx="20" cy="6" r="4.5" fill="currentColor" stroke="none"/>', 20),
    'j': ('<path d="M24 22 V64 Q24 76 12 76 Q8 76 6 74"/><circle cx="24" cy="6" r="4.5" fill="currentColor" stroke="none"/>', 16),
    'k': ('<path d="M6 4 V58 M32 22 L8 42 M14 37 L34 58"/>', 20),
    'l': ('<path d="M18 4 V50 Q18 59 30 58"/>', 23),
    'm': ('<path d="M5 22 V58 M5 38 Q5 22 14 22 Q22 22 22 38 V58 M22 38 Q22 22 31 22 Q39 22 39 38 V58"/>', 22),
    'n': ('<path d="M6 22 V58 M6 38 Q6 22 20 22 Q34 22 34 38 V58"/>', 20),
    'o': ('<circle cx="20" cy="40" r="17"/>', 20),
    'p': ('<path d="M6 22 V78"/><circle cx="23" cy="40" r="17"/>', 20),
    'q': ('<path d="M34 22 V78"/><circle cx="17" cy="40" r="17"/>', 20),
    'r': ('<path d="M8 22 V58 M8 40 Q8 22 22 22 Q28 22 32 24"/>', 19),
    's': ('<path d="M33 28 Q28 22 20 22 Q8 22 8 31 Q8 39 20 40 Q32 42 32 50 Q32 58 20 58 Q11 58 6 52"/>', 20),
    't': ('<path d="M16 8 V50 Q16 58 28 58 Q31 58 33 57 M6 24 H28"/>', 20),
    'u': ('<path d="M6 22 V44 Q6 58 20 58 Q34 58 34 44 M34 22 V58"/>', 20),
    'v': ('<path d="M4 22 L20 58 L36 22"/>', 20),
    'w': ('<path d="M2 22 L11 58 L20 32 L29 58 L38 22"/>', 20),
    'x': ('<path d="M6 22 L34 58 M34 22 L6 58"/>', 20),
    'y': ('<path d="M5 22 L20 56 M35 22 L17 68 Q12 78 3 76"/>', 20),
    'z': ('<path d="M6 22 H34 L6 58 H34"/>', 20),
}
GS = 0.86  # glyph scale inside the 80 px tile


def glyph_markup(letter):
    d, cx = G[letter]
    return (f'<g transform="translate({40 - cx * GS:.1f} 3) scale({GS})" fill="none" stroke="{INK}" stroke-width="8.4" '
            f'stroke-linecap="round" stroke-linejoin="round" color="{INK}">{d}</g>')


# ------------------------------------------------------------------ tiles (80 x 80, viewBox -20 -20 120 130)
TILE_VB = (-20, -20, 120, 130)
FACE, EDGE = '#FFF3D6', '#D9A464'
TILE_DEFS = ('<defs><radialGradient id="ell-wb-tile-glow"><stop offset="0" stop-color="#FFE066" stop-opacity=".95"/>'
             '<stop offset=".5" stop-color="#FFC83D" stop-opacity=".4"/><stop offset="1" stop-color="#FFC83D" stop-opacity="0"/></radialGradient></defs>')


def tile_body(face=FACE, edge=EDGE, stroke='#C9985F', sw=2, extra=''):
    return (f'<rect x="0" y="6" width="80" height="74" rx="18" fill="{edge}"/>'
            f'<rect x="0" y="0" width="80" height="74" rx="18" fill="{face}" stroke="{stroke}" stroke-width="{sw}"/>'
            f'<rect x="8" y="5" width="64" height="9" rx="4.5" fill="#fff" opacity=".55"/>{extra}')


def tile_state(state):
    if state == 'resting':
        return f'<ellipse cx="40" cy="84" rx="36" ry="6" fill="{INK}" opacity=".18"/>' + tile_body() + '%G%'
    if state == 'lifted':
        return (f'<ellipse cx="40" cy="90" rx="30" ry="6" fill="{INK}" opacity=".2"/>'
                '<g class="wb-lift" transform="translate(40 40) rotate(-4) scale(1.1) translate(-40 -40) translate(0 -10)">'
                f'<rect x="-3" y="2" width="86" height="82" rx="20" fill="{INK}" opacity=".12"/>'
                + tile_body('#FFFAEA', '#E0AC6C') + '%G%</g>')
    if state == 'lit':
        return (TILE_DEFS + '<circle class="wb-glow" cx="40" cy="40" r="68" fill="url(#ell-wb-tile-glow)"/>'
                + tile_body('#FFF1A8', '#E5B230', '#2FCB86', 4) + '%G%' + sparkle(76, 4, .9) + sparkle(2, 70, .7))
    if state == 'wobble':
        arcs = ('<path d="M-9 28 Q-16 40 -9 52" fill="none" stroke="#FF9F43" stroke-width="4" stroke-linecap="round" opacity=".8"/>'
                '<path d="M-16 22 Q-26 40 -16 58" fill="none" stroke="#FF9F43" stroke-width="3" stroke-linecap="round" opacity=".45"/>'
                '<path d="M89 28 Q96 40 89 52" fill="none" stroke="#FF9F43" stroke-width="4" stroke-linecap="round" opacity=".8"/>'
                '<path d="M96 22 Q106 40 96 58" fill="none" stroke="#FF9F43" stroke-width="3" stroke-linecap="round" opacity=".45"/>')
        return (f'<ellipse cx="40" cy="84" rx="36" ry="6" fill="{INK}" opacity=".18"/>' + arcs
                + '<g class="wb-wobble" transform="rotate(-7 40 74)">' + tile_body('#FFF3D6', '#E8A860', '#FF9F43', 3.5) + '%G%</g>')
    raise ValueError(state)


TILE_STATES = ('resting', 'lifted', 'lit', 'wobble')
TILE_TPL = {s: tile_state(s) for s in TILE_STATES}


def tile_svg(letter, state='resting'):
    g = glyph_markup(letter) if letter in G else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-20 -20 120 130" overflow="visible" style="overflow:visible" role="img" aria-label="Letter tile {letter}">'
            + TILE_TPL[state].replace('%G%', g) + '</svg>')


# ------------------------------------------------------------------ slots (96 x 96, viewBox -24 -24 144 144)
SLOT_DEFS = ('<defs><linearGradient id="ell-wb-slot-g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5E3820"/><stop offset=".45" stop-color="#7E4D2B"/><stop offset="1" stop-color="#8E5A33"/></linearGradient>'
             '<radialGradient id="ell-wb-slot-glow"><stop offset="0" stop-color="#FFE066" stop-opacity=".9"/><stop offset=".55" stop-color="#FFC83D" stop-opacity=".35"/><stop offset="1" stop-color="#FFC83D" stop-opacity="0"/></radialGradient></defs>')


def slot_inner(state, letter=None):
    base = ('<rect x="-3" y="-1" width="102" height="102" rx="25" fill="#F6CD92" opacity=".9"/>'  # lit lip under the recess
            '<rect x="0" y="0" width="96" height="96" rx="22" fill="url(#ell-wb-slot-g)"/>'
            '<rect x="0" y="0" width="96" height="96" rx="22" fill="none" stroke="#5E3820" stroke-width="3"/>')
    if state == 'empty':
        return base + '<rect x="12" y="12" width="72" height="72" rx="16" fill="none" stroke="#E0A765" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round" opacity=".75"/>'
    if state == 'hint':
        return ('<circle class="wb-glow" cx="48" cy="48" r="84" fill="url(#ell-wb-slot-glow)"/>' + base
                + '<rect x="0" y="0" width="96" height="96" rx="22" fill="none" stroke="#FFD45C" stroke-width="5"/>'
                + '<rect x="12" y="12" width="72" height="72" rx="16" fill="#FFD45C" opacity=".16"/>'
                + '<rect x="12" y="12" width="72" height="72" rx="16" fill="none" stroke="#FFE9A0" stroke-width="3.5" stroke-dasharray="7 9" stroke-linecap="round"/>'
                + sparkle(92, 2, .9) + sparkle(2, 94, .7))
    if state == 'filled':
        g = glyph_markup(letter) if letter in G else ''
        return base + '<g transform="translate(8 8)">' + tile_body() + g + '</g>'
    raise ValueError(state)


def slot_svg(state='empty', letter=None):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-24 -24 144 144" overflow="visible" style="overflow:visible" role="img" aria-label="Slot, {state}">'
            + SLOT_DEFS + slot_inner(state, letter) + '</svg>')


# ------------------------------------------------------------------ scene layers (960 x 600 coordinates, overflow visible)
BIG = 3000


def layer(inner, defs=''):
    """A scene layer is a <g>. It can sit inside any <svg viewBox="0 0 960 600"> and carries its own gradients."""
    return f'<g>{("<defs>" + defs + "</defs>") if defs else ""}{inner}</g>'


BACKDROP = layer(
    f'<rect x="-{BIG}" y="-{BIG}" width="{960 + 2 * BIG}" height="{BIG + 452}" fill="url(#ell-wb-wall)"/>'
    f'<rect x="-{BIG}" y="-{BIG}" width="{960 + 2 * BIG}" height="{BIG + 452}" fill="url(#ell-wb-paper)"/>'
    # wainscot rail and baseboard
    f'<rect x="-{BIG}" y="338" width="{960 + 2 * BIG}" height="10" fill="#D9A464" opacity=".55"/>'
    f'<rect x="-{BIG}" y="442" width="{960 + 2 * BIG}" height="16" fill="#B9804C"/><rect x="-{BIG}" y="442" width="{960 + 2 * BIG}" height="4" fill="#D9A464"/>'
    # floor
    f'<rect x="-{BIG}" y="458" width="{960 + 2 * BIG}" height="{BIG}" fill="url(#ell-wb-floor)"/>'
    '<g stroke="#5E3820" stroke-width="2" opacity=".28"><path d="M-3000 492 H3960 M-3000 534 H3960 M-3000 582 H3960 M-3000 640 H3960"/>'
    '<path d="M40 458 V492 M-120 492 V534 M120 492 V534 M-60 534 V582 M200 534 V582 M10 582 V640 M-180 458 V492"/></g>',
    '<linearGradient id="ell-wb-wall" gradientUnits="userSpaceOnUse" x1="0" y1="-60" x2="0" y2="452"><stop offset="0" stop-color="#F8E6C6"/><stop offset="1" stop-color="#EBCB98"/></linearGradient>'
    '<pattern id="ell-wb-paper" patternUnits="userSpaceOnUse" x="0" y="0" width="72" height="72"><rect x="0" y="0" width="6" height="72" fill="#C8996A" opacity=".07"/>'
    '<circle cx="39" cy="36" r="2" fill="#C8996A" opacity=".1"/></pattern>'
    '<linearGradient id="ell-wb-floor" gradientUnits="userSpaceOnUse" x1="0" y1="458" x2="0" y2="620"><stop offset="0" stop-color="#A9744A"/><stop offset="1" stop-color="#7A4E2E"/></linearGradient>')


def card_ph(x, y, kind, rot=0):
    """Small placeholder word card for the word wall (60 x 70). The real art swaps in later."""
    icons = {
        'star': '<path d="M30 14 L34 25 L46 26 L37 33 L40 45 L30 38 L20 45 L23 33 L14 26 L26 25Z" fill="#FFC83D" stroke="#E0A91C" stroke-width="1.6" stroke-linejoin="round"/>',
        'leaf': '<path d="M16 42 Q14 18 42 16 Q44 40 16 42Z" fill="#2FCB86" stroke="#0E7A52" stroke-width="1.6" stroke-linejoin="round"/><path d="M18 40 L36 22" stroke="#0E7A52" stroke-width="1.6" stroke-linecap="round"/>',
        'drop': '<path d="M30 14 Q46 34 40 40 Q30 50 20 40 Q14 34 30 14Z" fill="#2FB5EC" stroke="#1B86B8" stroke-width="1.6" stroke-linejoin="round"/>',
        'heart': '<path d="M30 44 Q12 32 16 22 Q22 14 30 24 Q38 14 44 22 Q48 32 30 44Z" fill="#FF6FB5" stroke="#D13F8A" stroke-width="1.6" stroke-linejoin="round"/>',
        'sun': '<circle cx="30" cy="30" r="10" fill="#FFC83D" stroke="#E0A91C" stroke-width="1.6"/><path d="M30 12 V16 M30 44 V48 M12 30 H16 M44 30 H48 M17 17 L20 20 M40 40 L43 43 M43 17 L40 20 M20 40 L17 43" stroke="#E0A91C" stroke-width="2" stroke-linecap="round"/>',
    }
    return (f'<g transform="translate({x} {y}) rotate({rot} 30 70)"><rect x="1" y="3" width="60" height="70" rx="9" fill="{INK}" opacity=".14"/>'
            f'<rect x="0" y="0" width="60" height="70" rx="9" fill="#FFFFFF" stroke="#C8996A" stroke-width="2.5"/>'
            f'<rect x="5" y="5" width="50" height="46" rx="6" fill="#FFF3D6"/>{icons[kind]}'
            f'<path d="M12 60 H48" stroke="#C8996A" stroke-width="3" stroke-linecap="round" opacity=".6"/></g>')


def card_ghost(x, y):
    return (f'<rect x="{x + 2}" y="{y + 2}" width="56" height="66" rx="9" fill="none" stroke="#B9804C" stroke-width="2.5" stroke-dasharray="6 8" '
            f'stroke-linecap="round" opacity=".5"/>')


WALL_CARD = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-6 -6 72 82" overflow="visible" style="overflow:visible" role="img" aria-label="Word card">'
             + card_ph(0, 0, 'star') + '</svg>')

WALL_SHELF = layer(
    # pennants
    '<path d="M410 20 Q670 54 930 20" fill="none" stroke="#B9804C" stroke-width="2.5"/>'
    + ''.join(f'<path d="M{x} {y} l13 0 l-6.5 20Z" fill="{c}" stroke="#fff" stroke-width="1.5" stroke-linejoin="round" opacity=".92"/>'
              for x, y, c in [(432, 23, '#2FB5EC'), (480, 33, '#FF6FB5'), (528, 40, '#FFC83D'), (576, 45, '#2FCB86'), (624, 47, '#2FB5EC'),
                              (672, 47, '#FF6FB5'), (720, 46, '#FFC83D'), (768, 42, '#2FCB86'), (816, 37, '#2FB5EC'), (864, 31, '#FF6FB5'), (906, 24, '#FFC83D')])
    # shelf plank and brackets
    + '<rect x="404" y="140" width="534" height="16" rx="6" fill="#8A5A35"/><rect x="404" y="140" width="534" height="5" rx="2.5" fill="#B9804C"/>'
      '<rect x="404" y="154" width="534" height="6" rx="3" fill="#000" opacity=".1"/>'
      '<path d="M430 156 V176 Q430 186 442 186 M912 156 V176 Q912 186 900 186" fill="none" stroke="#8A5A35" stroke-width="7" stroke-linecap="round"/>'
    + card_ph(424, 68, 'star', -3) + card_ph(504, 68, 'leaf', 2) + card_ph(584, 68, 'drop', -2) + card_ph(664, 68, 'sun', 3)
    + card_ghost(746, 68) + card_ghost(824, 68))

CRAFT_SHELF = layer(
    '<rect x="404" y="258" width="320" height="14" rx="6" fill="#8A5A35"/><rect x="404" y="258" width="320" height="5" rx="2.5" fill="#B9804C"/>'
    '<path d="M430 272 V292 Q430 302 442 302 M698 272 V292 Q698 302 686 302" fill="none" stroke="#8A5A35" stroke-width="7" stroke-linecap="round"/>'
    # pencil jar
    '<rect x="424" y="218" width="40" height="40" rx="9" fill="#BFE8F5" stroke="#6BA9C2" stroke-width="2.5"/>'
    '<path d="M434 220 L430 196 M444 220 L446 192 M454 220 L460 198" stroke="#FF6FB5" stroke-width="5" stroke-linecap="round"/>'
    '<path d="M444 220 L446 192" stroke="#FFC83D" stroke-width="5" stroke-linecap="round"/><path d="M454 220 L460 198" stroke="#2FB5EC" stroke-width="5" stroke-linecap="round"/>'
    # thread spools
    '<rect x="486" y="236" width="34" height="22" rx="5" fill="#2FB5EC" stroke="#1B86B8" stroke-width="2"/><rect x="482" y="232" width="42" height="6" rx="3" fill="#E0A765"/><rect x="482" y="256" width="42" height="4" rx="2" fill="#E0A765"/>'
    '<rect x="492" y="214" width="34" height="18" rx="5" fill="#FF6FB5" stroke="#D13F8A" stroke-width="2"/><rect x="488" y="210" width="42" height="5" rx="2.5" fill="#E0A765"/>'
    # paint pots
    '<rect x="548" y="236" width="32" height="22" rx="7" fill="#2FCB86" stroke="#0E7A52" stroke-width="2"/><rect x="544" y="232" width="40" height="7" rx="3.5" fill="#fff" stroke="#C8996A" stroke-width="1.5"/>'
    '<rect x="588" y="236" width="32" height="22" rx="7" fill="#FFC83D" stroke="#E0A91C" stroke-width="2"/><rect x="584" y="232" width="40" height="7" rx="3.5" fill="#fff" stroke="#C8996A" stroke-width="1.5"/>'
    # little plant
    '<path d="M664 258 L668 232 H694 L698 258Z" fill="#E8973A" stroke="#C97A1E" stroke-width="2" stroke-linejoin="round"/>'
    '<path d="M681 232 Q668 214 672 202 Q682 210 681 232 M681 232 Q696 216 694 204 Q684 212 681 232 M681 232 Q681 212 682 198" fill="#2FCB86" stroke="#0E7A52" stroke-width="2" stroke-linejoin="round"/>')

LAMP = layer(
    '<circle class="wb-glow" cx="330" cy="110" r="300" fill="url(#ell-wb-lamp-glow)"/>'
    f'<path d="M330 -{BIG} V40" stroke="#6B4129" stroke-width="4"/>'
    '<rect x="320" y="34" width="20" height="16" rx="5" fill="#D9A93F" stroke="#B8862A" stroke-width="2"/>'
    '<path d="M268 108 Q268 52 330 48 Q392 52 392 108 Z" fill="#FFD98A" stroke="#E0A91C" stroke-width="3" stroke-linejoin="round"/>'
    '<path d="M286 100 Q288 66 318 56" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".55"/>'
    '<path d="M300 108 Q304 70 330 50 M360 108 Q356 70 330 50" fill="none" stroke="#E8B73A" stroke-width="2" opacity=".6"/>'
    '<ellipse cx="330" cy="108" rx="62" ry="11" fill="#FFF3B8" stroke="#E0A91C" stroke-width="3"/><ellipse cx="330" cy="110" rx="44" ry="6" fill="#FFE066"/>',
    '<radialGradient id="ell-wb-lamp-glow"><stop offset="0" stop-color="#FFD98A" stop-opacity=".62"/><stop offset=".5" stop-color="#FFD98A" stop-opacity=".2"/><stop offset="1" stop-color="#FFD98A" stop-opacity="0"/></radialGradient>')

BENCH = layer(
    # tabletop, seen from slightly above. Left end rounded, runs off the right edge (and far past it).
    f'<path d="M278 330 Q250 330 250 358 V{BIG + 600} H{BIG + 960} V330 Z" fill="url(#ell-wb-bench)"/>'
    f'<path d="M250 358 Q250 330 278 330 H{BIG + 960} V342 H278 Q262 342 262 358 V{BIG + 600} H250Z" fill="#B27541" opacity=".55"/>'
    f'<rect x="262" y="330" width="{BIG + 700}" height="14" fill="#B9804C"/><rect x="262" y="344" width="{BIG + 700}" height="5" fill="#000" opacity=".1"/>'
    '<g fill="none" stroke="#B9804C" stroke-width="2.4" stroke-linecap="round" opacity=".38">'
    '<path d="M300 372 Q420 362 560 372 T900 370 M290 460 Q420 452 560 460 T930 456 M320 600 Q460 592 620 600"/>'
    '<path d="M980 380 Q1200 372 1400 382 M980 470 Q1200 462 1500 470"/></g>'
    '<ellipse cx="520" cy="430" rx="330" ry="90" fill="url(#ell-wb-pool)"/>',
    '<linearGradient id="ell-wb-bench" gradientUnits="userSpaceOnUse" x1="0" y1="330" x2="0" y2="600"><stop offset="0" stop-color="#E4B079"/><stop offset="1" stop-color="#D3995C"/></linearGradient>'
    '<radialGradient id="ell-wb-pool"><stop offset="0" stop-color="#FFE9A8" stop-opacity=".42"/><stop offset="1" stop-color="#FFE9A8" stop-opacity="0"/></radialGradient>')

TRAY = layer(
    '<rect x="276" y="472" width="668" height="124" rx="30" fill="#E0A765"/>'
    '<rect x="276" y="472" width="668" height="124" rx="30" fill="none" stroke="#8A5A35" stroke-width="3"/>'
    '<rect x="288" y="484" width="644" height="100" rx="22" fill="url(#ell-wb-tray)"/>'
    '<path d="M300 486 H920" stroke="#5E3820" stroke-width="3" stroke-linecap="round" opacity=".35"/>'
    '<rect x="288" y="484" width="644" height="100" rx="22" fill="none" stroke="#7A4A28" stroke-width="2.5"/>',
    '<linearGradient id="ell-wb-tray" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8E5A33"/><stop offset=".4" stop-color="#A8703F"/><stop offset="1" stop-color="#B27A47"/></linearGradient>')

# Easel: picture window is x 70..214, y 108..252 (144 x 144), exported as PICTURE_RECT so the game can overlay real art.
PICTURE_RECT = {'x': 70, 'y': 108, 'w': 144, 'h': 144}
EASEL = layer(
    # legs and ledge
    '<path d="M70 262 L48 552 M214 262 L238 552 M142 140 L142 556" fill="none" stroke="#6B4129" stroke-width="11" stroke-linecap="round"/>'
    '<path d="M70 262 L48 552 M214 262 L238 552 M142 140 L142 556" fill="none" stroke="#8A5A35" stroke-width="7" stroke-linecap="round"/>'
    '<ellipse cx="143" cy="560" rx="112" ry="12" fill="#3B2A20" opacity=".16"/>'
    '<rect x="50" y="306" width="184" height="16" rx="7" fill="#8A5A35" stroke="#6B4129" stroke-width="2.5"/>'
    # frame
    '<rect x="50" y="88" width="184" height="190" rx="22" fill="#000" opacity=".12" transform="translate(4 6)"/>'
    '<rect x="50" y="88" width="184" height="190" rx="22" fill="#C8996A" stroke="#8A5A35" stroke-width="3"/>'
    '<rect x="58" y="96" width="168" height="174" rx="16" fill="#FFF7E8"/>'
    '<g id="ell-wb-picture">'
    '<rect x="70" y="108" width="144" height="144" rx="10" fill="url(#ell-wb-sky)"/>'
    '<circle cx="180" cy="144" r="16" fill="#FFC83D" stroke="#E0A91C" stroke-width="2"/>'
    '<path d="M70 226 Q110 176 160 214 Q190 198 214 220 V242 Q214 252 204 252 H80 Q70 252 70 242Z" fill="#7BD39A" stroke="#3C9A33" stroke-width="2" stroke-linejoin="round"/>'
    '<path d="M96 156 q10 -12 22 -2 q12 -8 18 4 q-20 8 -40 -2Z" fill="#fff"/></g>'
    '<rect x="70" y="108" width="144" height="144" rx="10" fill="none" stroke="#C8996A" stroke-width="2.5"/>'
    # name plate under the picture
    '<rect x="102" y="256" width="80" height="12" rx="6" fill="#FFFFFF" stroke="#C8996A" stroke-width="2"/>'
    '<circle cx="142" cy="92" r="4.5" fill="#D9A93F" stroke="#B8862A" stroke-width="1.5"/>',
    '<linearGradient id="ell-wb-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#BFE8F5"/><stop offset="1" stop-color="#EAF8FC"/></linearGradient>')

# ------------------------------------------------------------------ composing helpers (preview only; the game does its own layout)
def place(svg, x, y, w, h, extra=''):
    return svg.replace('<svg ', f'<svg x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" {extra}', 1)


def sprite(svg, vb, ax, ay, tx, ty, k):
    """Place a sprite so that its anchor (ax, ay) lands at (tx, ty), scaled by k."""
    vx, vy, vw, vh = vb
    return place(svg, tx - (ax - vx) * k, ty - (ay - vy) * k, vw * k, vh * k)


def tile_at(letter, state, X, Y, k=1.0):
    return place(tile_svg(letter, state), X - 20 * k, Y - 20 * k, 120 * k, 130 * k)


def slot_at(state, X, Y, letter=None):
    return place(slot_svg(state, letter), X - 24, Y - 24, 144, 144)


def friend(name, state, cx=836, feet=348, k=0.78):
    return sprite(CAST[name][state], CAST_VB, 100, CAST_FEET, cx, feet, k)


def hazel_at(pose, cx=326, feet=348, k=0.66):
    return sprite(HAZEL[pose], HAZEL_VB, HAZEL_ANCHOR[0], HAZEL_ANCHOR[1], cx, feet, k)


def slot_xs(n, cx=610, w=96, gap=12):
    total = n * w + (n - 1) * gap
    x0 = cx - total / 2
    return [x0 + i * (w + gap) for i in range(n)]


def tray_pitch(n):
    return min(88, 640 / n)


def tray_xs(n, cx=610, w=80):
    pitch = tray_pitch(n)
    k = min(1, (pitch - 4) / 80)
    w = 80 * k
    total = (n - 1) * pitch + w
    x0 = cx - total / 2
    return [x0 + i * pitch for i in range(n)]


def tray_k(n):
    return min(1, (tray_pitch(n) - 4) / 80)


SLOT_Y = 352
TRAY_Y = 492


def scene_body(who='mouse', fstate='idle', hpose='point', word='frog', tray='frog' + 'sit', placed=0, hint=0, lit=False,
               lifted=None, wobble=None, wall_new=False):
    """placed: how many letters already in the slots. hint: slot index that glows (or -1). lit: all letters lit."""
    out = BACKDROP + LAMP + WALL_SHELF + CRAFT_SHELF
    out += BENCH
    out += '<ellipse cx="326" cy="348" rx="62" ry="8" fill="#3B2A20" opacity=".18"/>' + hazel_at(hpose) + friend(who, fstate)
    out += TRAY
    sx = slot_xs(len(word))
    for i, x in enumerate(sx):
        if lit:
            out += slot_at('empty', x, SLOT_Y) + tile_at(word[i], 'lit', x + 8, SLOT_Y + 8)
        elif i < placed:
            out += slot_at('filled', x, SLOT_Y, word[i])
        elif i == hint:
            out += slot_at('hint', x, SLOT_Y)
        else:
            out += slot_at('empty', x, SLOT_Y)
    used = list(word[:placed]) if not lit else list(word)
    if lifted:
        used.append(lifted[0])
    tx = tray_xs(len(tray))
    # keep the tray positions stable: used tiles leave a gap
    avail = list(tray)
    for i, ch in enumerate(avail):
        if ch in used:
            used.remove(ch)
            continue
        st = 'resting'
        if wobble is not None and i == wobble:
            st = 'wobble'
        out += tile_at(ch, st, tx[i], TRAY_Y, tray_k(len(tray)))
    if lifted:
        ch, X, Y = lifted
        out += tile_at(ch, 'lifted', X, Y)
    out += EASEL
    if hpose == 'point':
        pass
    if wall_new:
        out += card_ph(746, 68, 'heart', -4) + sparkle(776, 62, 1.2) + sparkle(820, 90, .9) + sparkle(736, 120, .8)
    return out


def scene_svg(body, wide=False, cls='scene', label=''):
    vb = '-320 0 1600 600' if wide else '0 0 960 600'
    return (f'<svg viewBox="{vb}" class="{cls}" role="img" aria-label="{label}">{body}</svg>')


# ------------------------------------------------------------------ scene.ts
def ts_const(name, value, doc=''):
    return (f'/** {doc} */\n' if doc else '') + f'export const {name} = {json.dumps(value, ensure_ascii=False)};\n'


def build_ts():
    o = ['// Letter Workshop scene art as plain SVG strings, generated by brand/word-building/build.py. Do not edit by hand.\n'
         '// Port of the approved art preview (index.html). Every string is self-contained: scene layers carry their own gradients,\n'
         '// so they can be dropped into any <svg viewBox="0 0 960 600" style="overflow:visible"> in the order\n'
         '// backdrop, lamp, wallShelf, craftShelf, (Hazel and the friend), bench, tray, slots, tiles, easelFrame.\n'
         '// Sprites (hazel, cast, tiles, slots, cards) are standalone <svg> strings with a viewBox that includes headroom;\n'
         '// size and place them with x / y / width / height (see the SPRITE_* constants for the viewBox and anchors).\n'
         '// Classes you may animate (transform and opacity only): wb-glow, wb-sparkle, wb-hop, wb-lift, wb-wobble.\n\n']
    o.append(ts_const('backdrop', BACKDROP, 'Wall, paper, rail, baseboard, floor. Extends 3000 units past every edge, no seam on wide screens.'))
    o.append(ts_const('lamp', LAMP, 'Hanging lamp with a soft warm glow (cord runs off the top). Centred at x 330.'))
    o.append(ts_const('wallShelf', WALL_SHELF, 'Word wall: pennants, shelf, 4 placeholder cards and 2 empty ghost slots. Next card goes at x 746, y 68.'))
    o.append(ts_const('craftShelf', CRAFT_SHELF, 'Craft shelf: pencil jar, spools, paint pots, plant.'))
    o.append(ts_const('bench', BENCH, 'Workbench top, runs off the right edge. Slots sit at y 352, tray below.'))
    o.append(ts_const('tray', TRAY, 'Letter tray. Tiles sit at y 492, 80 wide, pitch 88.'))
    o.append(ts_const('easelFrame', EASEL, 'Easel and picture frame. Picture window is PICTURE_RECT; the placeholder is <g id="ell-wb-picture">.'))
    o.append('export const PICTURE_RECT = ' + json.dumps(PICTURE_RECT) + ' as const;\n')
    o.append('export const SLOT = { size: 96, y: 352, gap: 12, centerX: 610 } as const;\n')
    o.append('export const TILE = { size: 80, trayY: 492, pitch: 88, centerX: 610, trayInnerWidth: 640 } as const;\n// Tray layout rule used in the preview: pitch = min(88, 640 / count), tile scale = min(1, (pitch - 4) / 80). Eight tiles gives pitch 80, scale 0.95.\n')
    o.append('/** viewBox (x y w h) and anchor of each sprite family: place so the anchor lands where you want it. */\n')
    o.append('export const SPRITE_VB = ' + json.dumps({
        'hazel': {'viewBox': list(HAZEL_VB), 'anchor': list(HAZEL_ANCHOR), 'note': 'anchor is her feet'},
        'cast': {'viewBox': list(CAST_VB), 'anchor': [100, CAST_FEET], 'note': 'anchor is the feet'},
        'tile': {'viewBox': list(TILE_VB), 'anchor': [0, 0], 'note': 'anchor is the top left of the 80 x 80 tile'},
        'slot': {'viewBox': [-24, -24, 144, 144], 'anchor': [0, 0], 'note': 'anchor is the top left of the 96 x 96 slot'},
    }) + ' as const;\n\n')
    o.append(ts_const('hazel', HAZEL, 'Hazel the shop owner: neutral, point (left wing toward the easel), cheer (both wings up, happy eyes).'))
    o.append(ts_const('cast', CAST, 'Friends by name and state: idle (holding the picture card), happy, wave.'))
    o.append(ts_const('pictureCard', PICTURE_CARD, 'The paper card a friend holds up.'))
    o.append(ts_const('wallCard', WALL_CARD, 'A word card for the word wall (placeholder picture).'))
    o.append('export type TileState = ' + ' | '.join(f"'{s}'" for s in TILE_STATES) + ';\n')
    o.append("export type SlotState = 'empty' | 'hint' | 'filled';\n")
    o.append('export const TILE_STATES: readonly TileState[] = ' + json.dumps(list(TILE_STATES)) + ';\n')
    o.append('const GLYPHS: Record<string, string> = ' + json.dumps({k: glyph_markup(k) for k in G}, ensure_ascii=False) + ';\n')
    o.append('const TILE_TPL: Record<TileState, string> = ' + json.dumps(TILE_TPL, ensure_ascii=False) + ';\n')
    o.append('const TILE_OPEN = ' + json.dumps('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-20 -20 120 130" overflow="visible" style="overflow:visible" role="img" aria-label="Letter tile %L%">') + ';\n')
    o.append('''/** A letter tile in one of its states. Letters a to z (lowercase); anything else gives a blank tile. */
export function tileSvg(letter: string, state: TileState = 'resting'): string {
  const l = letter.toLowerCase();
  return TILE_OPEN.replace('%L%', l) + TILE_TPL[state].replace('%G%', GLYPHS[l] ?? '') + '</svg>';
}

''')
    sd = {s: slot_inner(s, None) for s in ('empty', 'hint')}
    o.append('const SLOT_DEFS = ' + json.dumps(SLOT_DEFS) + ';\n')
    o.append('const SLOT_PART: Record<\'empty\' | \'hint\', string> = ' + json.dumps(sd, ensure_ascii=False) + ';\n')
    base = slot_inner('filled', 'a').split('<g transform="translate(8 8)">')[0]
    o.append('const SLOT_FILLED_BASE = ' + json.dumps(base) + ';\n')
    o.append('const TILE_RESTING_BODY = ' + json.dumps(tile_body()) + ';\n')
    o.append('''/** A slot. 'filled' seats a resting tile showing `letter` (blank tile when omitted). */
export function slotSvg(state: SlotState = 'empty', letter?: string): string {
  const open = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-24 -24 144 144" overflow="visible" style="overflow:visible" role="img" aria-label="Slot, ' + state + '">' + SLOT_DEFS;
  if (state === 'filled') {
    const g = letter ? GLYPHS[letter.toLowerCase()] ?? '' : '';
    return open + SLOT_FILLED_BASE + '<g transform="translate(8 8)">' + TILE_RESTING_BODY + g + '</g></svg>';
  }
  return open + SLOT_PART[state] + '</svg>';
}
''')
    open('scene.ts', 'w').write(''.join(o))


# ------------------------------------------------------------------ preview page
CSS = '''
:root{--cream:#FFF7E8;--ink:#3B2A20;--teal:#0F857D}
*{box-sizing:border-box}
body{margin:0;background:var(--cream);color:var(--ink);font-family:Andika,system-ui,sans-serif;padding:24px 16px 60px}
main{max-width:980px;margin:0 auto}
h1{font-family:Fredoka,system-ui,sans-serif;color:var(--teal);margin:0 0 4px} h2{font-family:Fredoka,system-ui,sans-serif;margin:40px 0 8px} h3{font-family:Fredoka,system-ui,sans-serif;margin:24px 0 10px}
p{line-height:1.5;max-width:70ch}
.scene{width:100%;height:auto;border-radius:32px;box-shadow:0 10px 30px rgba(90,50,20,.28);display:block;background:#EBCB98}
.wide{overflow:hidden;border-radius:32px;box-shadow:0 10px 30px rgba(90,50,20,.28)} .wide .scene{border-radius:0;box-shadow:none}
.row{display:flex;flex-wrap:wrap;gap:16px;align-items:flex-end}
.fig{margin:0;text-align:center;background:linear-gradient(#F8E6C6,#EBCB98);border-radius:24px;padding:14px 18px 10px;box-shadow:0 6px 18px rgba(90,50,20,.16)}
.fig svg{display:block;margin:0 auto}
.fig figcaption{font-size:15px;margin-top:6px;line-height:1.3}
.bench{background:linear-gradient(#E4B079,#D3995C)}
.dark{background:#A8703F}
.note{background:#fff;border-left:6px solid var(--teal);border-radius:12px;padding:10px 16px;max-width:70ch}
.sw{display:flex;align-items:center;gap:10px;margin:4px 0}.sw span{display:inline-block;width:92px;text-align:center;border-radius:8px;padding:6px 0;font:600 14px Andika,system-ui;border:1px solid #0002}.sw i{color:#6b5a4b;font-size:14px}
.pal{columns:2 360px}
table{border-collapse:collapse;width:100%;background:#fff;border-radius:12px;overflow:hidden;font-size:15px}
td,th{padding:8px 12px;border-bottom:1px solid #eadfca;text-align:left;vertical-align:top}th{background:#0F857D;color:#fff;font-family:Fredoka,system-ui}
code{background:#fff;padding:1px 6px;border-radius:6px;font-size:14px}
.wb-glow,.wb-sparkle,.wb-hop,.wb-lift,.wb-wobble{transform-box:fill-box;transform-origin:center}
@keyframes gp{0%,100%{opacity:.7}50%{opacity:1}} .wb-glow{animation:gp 2.6s ease-in-out infinite}
@keyframes sp{0%,100%{opacity:.6;transform:scale(.85)}50%{opacity:1;transform:scale(1.1)}} .wb-sparkle{animation:sp 2s ease-in-out infinite}
@keyframes hop{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}} .wb-hop{animation:hop 1.1s ease-in-out infinite}
@media (prefers-reduced-motion:reduce){.wb-glow,.wb-sparkle,.wb-hop{animation:none}}
'''


def fig(svg, w, cap, cls=''):
    return f'<figure class="fig {cls}">{place(svg, 0, 0, w[0], w[1]).replace("<svg x=\"0.0\" y=\"0.0\"", "<svg")}<figcaption>{cap}</figcaption></figure>'


def fig_sized(svg, w, h, cap, cls=''):
    s = svg.replace('<svg ', f'<svg width="{w}" height="{h}" ', 1)
    return f'<figure class="fig {cls}">{s}<figcaption>{cap}</figcaption></figure>'


def cast_sheet():
    out = ''
    for n, label in (('mouse', 'Mouse'), ('hedgehog', 'Hedgehog'), ('bunny', 'Bunny'), ('robin', 'Robin')):
        out += f'<h3>{label}</h3><div class="row">'
        for s, cap in (('idle', 'idle, holding the card'), ('happy', 'happy'), ('wave', 'waving')):
            out += fig_sized(CAST[n][s], 216, 243, cap)
        out += '</div>'
    return out


def hazel_sheet():
    out = '<div class="row">'
    for p, cap in (('neutral', 'neutral'), ('point', 'pointing at the picture'), ('cheer', 'cheering')):
        out += fig_sized(HAZEL[p], 168, 174, cap)
    return out + '</div>'


def tile_sheet():
    out = '<div class="row">'
    caps = {'resting': 'resting', 'lifted': 'lifted (dragging)', 'lit': 'lit (correct, glow)', 'wobble': 'wobble (not this one)'}
    for s in TILE_STATES:
        out += fig_sized(tile_svg('g', s), 180, 195, caps[s])
    out += '</div><h3>Same tiles on the tray wood</h3><div class="row">'
    for s in TILE_STATES:
        out += fig_sized(tile_svg('m', s), 120, 130, s, 'dark')
    return out + '</div>'


def slot_sheet():
    out = '<div class="row">'
    for s, cap in (('empty', 'empty'), ('hint', 'glowing hint'), ('filled', 'filled (tile seated)')):
        out += fig_sized(slot_svg(s, 'o'), 216, 216, cap, 'bench')
    return out + '</div>'


def alphabet_sheet():
    out = '<div class="row" style="gap:8px">'
    for ch in G:
        out += f'<div style="text-align:center">{tile_svg(ch).replace("<svg ", "<svg width=\"96\" height=\"104\" ", 1)}</div>'
    return out + '</div>'


def palette():
    return ''.join(f'<div class="sw"><span style="background:{h};color:{"#fff" if h in ("#0F857D","#8A5A35","#7E4D2B","#5E3820","#7A4E2E","#A8703F","#3B2A20","#B9804C") else "#3B2A20"}">{h}</span>{n} <i>{u}</i></div>' for n, h, u in PAL)


NOTES = '''
<h2>8. Palette and notes</h2>
<div class="pal">%PAL%</div>
<p class="note">Letters are always ink (#3B2A20) on a light tile face (#FFF3D6, #FFF1A8 when lit): contrast about 12:1 and 11:1.
The lit state never relies on color alone: it adds a gold halo, a thicker green rim and sparkles. Wobble is a soft orange rim plus motion arcs, never red.</p>
<h3>Hand-off to the game skin</h3>
<p>Everything above is in <code>scene.ts</code> as plain strings (generated by <code>build.py</code>, so this page and the module cannot drift).
Scene layers (<code>backdrop</code>, <code>lamp</code>, <code>wallShelf</code>, <code>craftShelf</code>, <code>bench</code>, <code>tray</code>, <code>easelFrame</code>) are <code>&lt;g&gt;</code> fragments
for a 960 x 600 scene, each with its own gradients. Sprites (<code>hazel</code>, <code>cast</code>, <code>tileSvg</code>, <code>slotSvg</code>, <code>pictureCard</code>, <code>wallCard</code>) are standalone
<code>&lt;svg&gt;</code> strings with headroom in the viewBox; <code>SPRITE_VB</code> lists each viewBox and anchor.
Letters are stroked paths (single-story a and g), so the tiles need no font and render the same everywhere.</p>
<h3>What animates (transform and opacity only) and its reduced-motion version</h3>
<table><tr><th>Part</th><th>Normal motion</th><th>Reduced motion</th></tr>
<tr><td>Tile drag (<code>lifted</code>)</td><td>Follows the finger, small tilt, bigger shadow</td><td>Same (it is direct manipulation, not decoration)</td></tr>
<tr><td>Tile click-in</td><td>Spring settle into the slot (scale 1.08 to 1)</td><td>Instant swap to resting</td></tr>
<tr><td>Wrong tile (<code>wobble</code>)</td><td>Gentle wobble, then hops back to the tray</td><td>Soft orange rim fades in and out, tile slides back</td></tr>
<tr><td>Lit (<code>wb-glow</code>, <code>wb-sparkle</code>)</td><td>Letters light left to right, halo pulses</td><td>Halo shown steady, no pulse</td></tr>
<tr><td>Friend (<code>wb-hop</code>)</td><td>Hop while happy, idle bob</td><td>Swap to the happy pose with no hop</td></tr>
<tr><td>Hint slot</td><td>Halo pulses</td><td>Halo steady</td></tr></table>
'''


def build_html():
    s1 = scene_svg(scene_body('mouse', 'idle', 'point', 'frog', 'frogsit', placed=0, hint=0), label='Workshop: the mouse holds a picture card, slots are empty and the first one glows.')
    s1w = scene_svg(scene_body('mouse', 'idle', 'point', 'frog', 'frogsit', placed=0, hint=0), wide=True, label='The same scene on a very wide screen, no seam.')
    s2 = scene_svg(scene_body('hedgehog', 'wave', 'neutral', 'frog', 'frogsit', placed=2, hint=-1, lifted=('o', 618, 392), wobble=5),
                   label='Mid word: two letters seated, one tile lifted over the bench, one tile wobbling in the tray.')
    s3 = scene_svg(scene_body('bunny', 'happy', 'cheer', 'frog', 'frogsit', lit=True, wall_new=True),
                   label='Word complete: all four letters lit, the bunny is happy, a new card joins the word wall.')
    s4 = scene_svg(scene_body('robin', 'idle', 'neutral', 'truck', 'truckbia', placed=3, hint=3),
                   label='A five letter word with the robin.')
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Letter Workshop art preview</title>
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Andika:wght@400;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body><main>
<h1>Letter Workshop: art direction preview</h1>
<p>Static prototype for approval. Nothing here is the final game. It shows the cozy craft room, the four friends, Hazel as the shop owner, the letter tiles and slots, and the word wall for Word Building for Grade 1.
Same bones as the garden and the pond (rounded shapes, one outline weight, ink on light, teal for UI), in a third mood: indoors, warm wood, paper and lamplight.
Gentle idle motion only. Scenes are 960 x 600. The picture on the easel is a placeholder; the 36 word pictures are drawn separately.</p>
<h2>1. The workshop at the start of a round</h2>
<p>The mouse holds up a picture card, Hazel points at the easel, the word is four letters so there are four slots, and the first slot glows (the "Letter" hint). The tray holds the letters plus distractors.</p>
{s1}
<p>Wide screen check: the same scene on a 1600 wide canvas. Wall, floor, paper and bench continue past the 960 scene edges with no seam.</p>
<div class="wide">{s1w}</div>
<h2>2. Mid word</h2>
<p>Two letters are seated, a third tile is lifted with a soft shadow, and one tile in the tray wobbles (wrong letter, no red mark). The hedgehog waves and Hazel is neutral.</p>
{s2}
<h2>3. Word complete: the letters light up</h2>
<p>All four tiles are lit (gold halo, green rim). The bunny hops, Hazel cheers, and a new card joins the word wall with sparkles.</p>
{s3}
<h2>4. A five letter word</h2>
<p>Level 5 uses five slots and a longer tray. Three letters are seated and the next slot glows. The robin waits.</p>
{s4}
<h2>5. Letter tiles</h2>
<p>Tiles are 80 x 80 (never smaller than 64 at display size), a rounded paper-maple block with a solid darker edge like our pressable buttons. Letters are ink, lowercase, with single-story a and g.</p>
{tile_sheet()}
<h2>6. Slots</h2>
<p>A slot is a recess with a dashed "drop here" outline. The hint state adds a gold ring and glow. Filled shows the tile seated.</p>
{slot_sheet()}
<h2>7. The cast</h2>
<p>Each friend in three states. Every character has headroom in its box so ears, spikes, beak and crest never clip.</p>
{cast_sheet()}
<h3>Hazel, the shop owner</h3>
{hazel_sheet()}
<h2>7b. Alphabet check</h2>
<p>All 26 lowercase tiles, so every letter can be checked once.</p>
{alphabet_sheet()}
<h2>7c. Word wall</h2>
<p>The word wall shelf with four placeholder cards and two empty ghost places. A new card lands in the next ghost.</p>
<svg viewBox="390 0 560 200" class="scene">{BACKDROP}{WALL_SHELF}</svg>
{NOTES.replace('%PAL%', palette())}
</main></body></html>'''
    open('index.html', 'w').write(html)


def build_fit():
    body = scene_body('mouse', 'idle', 'point', 'frog', 'frogsit', placed=0, hint=0)
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Letter Workshop fit check</title><style>{CSS}html,body{{margin:0;padding:0;height:100%;background:#EBCB98;overflow:hidden}}
svg.fit{{display:block;width:100vw;height:100vh}}</style></head><body>
<svg class="fit" viewBox="0 0 960 600" preserveAspectRatio="xMidYMid meet">{body}</svg></body></html>'''
    open('fit.html', 'w').write(html)


build_ts()
build_html()
build_fit()
print('ok')
