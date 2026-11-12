# Builds index.html for the Pond Hop art preview. Run from this folder: python3 build.py
# Why a script: Hazel's art is reused from brand/mascot/owl.svg (source of truth). The script inlines it in four poses
# without redrawing her, so the preview and the owl file cannot drift apart.
import re

# ------------------------------------------------------------------ Hazel (reused, not redrawn)
owl = open('../mascot/owl.svg').read().strip()
owl = re.sub(r'^<svg[^>]*>', '', owl)
owl = owl[:owl.rindex('</svg>')]
owl = re.sub(r'<title>.*?</title>', '', owl, flags=re.S)
owl = re.sub(r'<!--.*?-->', '', owl, flags=re.S)
owl_defs = re.search(r'<defs>(.*?)</defs>', owl, flags=re.S).group(1)
owl_body = re.sub(r'<defs>.*?</defs>', '', owl, flags=re.S)
owl_defs = owl_defs.replace('id="g-', 'id="ell-pond-hz-g-')
owl_body = owl_body.replace('url(#g-', 'url(#ell-pond-hz-g-')


def hazel_variant(name, keeper=False, cheer=False, point=False):
    b = owl_body
    if keeper:
        b = b.replace('<g id="wing-right" class="part" style="transform-origin:172px 178px">', '<g transform="rotate(-60 172 178)">')
    if point:
        b = b.replace('<g id="wing-right" class="part" style="transform-origin:172px 178px">', '<g transform="rotate(-75 172 178)">')
    if cheer:
        b = b.replace('<g id="wing-right" class="part" style="transform-origin:172px 178px">', '<g transform="rotate(-75 172 178)">')
        b = b.replace('<g id="wing-left" class="part" style="transform-origin:68px 178px">', '<g transform="rotate(75 68 178)">')
        b = b.replace('<g id="eyes-happy" opacity="0"', '<g id="eyes-happy" opacity="1"')
        b = b.replace('id="eye-left" class="part"', 'opacity="0"').replace('id="eye-right" class="part"', 'opacity="0"')
        # open beak, a cheer
        b = b.replace('<path id="beak-lower" class="part" style="transform-origin:120px 138px"', '<path transform="translate(0 3)"')
    b = re.sub(r' id="[^"]*"', '', b)
    b = re.sub(r' class="(part|look|pupil)"', '', b)
    b = re.sub(r' style="transform-origin:[^"]*"', '', b)
    return f'<symbol id="ell-pond-hazel{name}" viewBox="0 0 240 262">{b}</symbol>'


hazel_symbols = (hazel_variant('') + hazel_variant('-keeper', keeper=True) + hazel_variant('-cheer', cheer=True)
                 + hazel_variant('-point', point=True))

# ------------------------------------------------------------------ palette
PAL = [
    ('Sky top (night)', '#070F33', 'backdrop'), ('Sky dusk blue', '#1B3A7A', 'backdrop'), ('Sky horizon teal', '#2B8DAA', 'backdrop'),
    ('Far hills', '#1D4F7C', 'backdrop'), ('Near hills', '#12335E', 'backdrop'),
    ('Water light', '#1D7AA3', 'water'), ('Water deep', '#0C3560', 'water'), ('Ripple', '#BFF0FF', 'water'),
    ('Pad', '#1FAE74', 'lily pad'), ('Pad rim', '#0E7A52', 'lily pad'), ('Pad highlight', '#35C98B', 'lily pad'),
    ('Frog', '#9BE564', 'frog'), ('Frog outline', '#3C9A33', 'frog'), ('Frog belly', '#E8FBB8', 'frog'),
    ('Firefly glow', '#FFD43B', 'firefly'), ('Firefly core', '#FFF3B0', 'firefly'), ('Firefly dim', '#6D7FB5', 'firefly'),
    ('Lantern brass', '#D9A93F', 'lantern'), ('Lantern light', '#FFC83D', 'lantern'),
    ('Teal (brand)', '#0F857D', 'UI'), ('Teal dark', '#0A625C', 'UI'), ('Ink', '#3B2A20', 'text on white'), ('White', '#FFFFFF', 'text on dusk, bubbles'),
    ('Duckling', '#FFD84A', 'cast'), ('Turtle shell', '#C8996A', 'cast'), ('Turtle skin', '#8FD6A0', 'cast'),
    ('Dragonfly', '#FF6FB5', 'cast'), ('Fish', '#FF9F43', 'cast'), ('Cheek pink', '#FF92C8', 'cast'),
]

# ------------------------------------------------------------------ shared drawing bits
LINE = 2.5  # one outline weight for the whole cast, same as the garden cast


def eyes_open(cx1, cx2, cy, rx=8, ry=9, px=1.5, py=1.5):
    out = ''
    for cx in (cx1, cx2):
        out += (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#fff"/>'
                f'<circle cx="{cx + px}" cy="{cy + py}" r="{rx * 0.62:.1f}" fill="#3B2A20"/>'
                f'<circle cx="{cx + px + 2}" cy="{cy + py - 2}" r="2" fill="#fff"/>')
    return out


def eyes_happy(cx1, cx2, cy, w=8):
    return (f'<path d="M{cx1 - w} {cy + 2} Q{cx1} {cy - 9} {cx1 + w} {cy + 2}" stroke="#3B2A20" stroke-width="3.2" fill="none" stroke-linecap="round"/>'
            f'<path d="M{cx2 - w} {cy + 2} Q{cx2} {cy - 9} {cx2 + w} {cy + 2}" stroke="#3B2A20" stroke-width="3.2" fill="none" stroke-linecap="round"/>')


def cheeks(x1, x2, y, rx=6, ry=4):
    return f'<ellipse cx="{x1}" cy="{y}" rx="{rx}" ry="{ry}" fill="#FF92C8" opacity=".75"/><ellipse cx="{x2}" cy="{y}" rx="{rx}" ry="{ry}" fill="#FF92C8" opacity=".75"/>'


def smile(x, y, w=6):
    return f'<path d="M{x - w} {y} Q{x} {y + 6} {x + w} {y}" stroke="#3B2A20" stroke-width="2.5" fill="none" stroke-linecap="round"/>'


def sparkle(x, y, s=1.0, fill='#FFE066'):
    return (f'<path transform="translate({x} {y}) scale({s})" d="M0 -9 L2.6 -2.6 L9 0 L2.6 2.6 L0 9 L-2.6 2.6 L-9 0 L-2.6 -2.6Z" fill="{fill}" stroke="#E0A91C" stroke-width="1" stroke-linejoin="round"/>')


def waterline(cx, cy, rx):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="5" fill="none" stroke="#BFF0FF" stroke-width="3" opacity=".5"/>'


# ------------------------------------------------------------------ frog family
FB, FO, FBL, FS = '#9BE564', '#3C9A33', '#E8FBB8', '#78CF4A'


def frog_sit():
    return f'''<symbol id="ell-pond-frog" viewBox="0 -8 100 100">
<ellipse cx="50" cy="88" rx="38" ry="5" fill="#06223F" opacity=".28"/>
<ellipse cx="20" cy="70" rx="15" ry="17" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/><ellipse cx="80" cy="70" rx="15" ry="17" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/>
<ellipse cx="15" cy="84" rx="14" ry="6" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/><ellipse cx="85" cy="84" rx="14" ry="6" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/>
<ellipse cx="50" cy="60" rx="34" ry="28" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/>
<ellipse cx="50" cy="69" rx="22" ry="17" fill="{FBL}"/>
<ellipse cx="36" cy="86" rx="9" ry="5" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/><ellipse cx="64" cy="86" rx="9" ry="5" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/>
<g fill="{FS}"><circle cx="50" cy="40" r="3.5"/><circle cx="62" cy="44" r="2.6"/><circle cx="38" cy="44" r="2.6"/></g>
<circle cx="30" cy="26" r="15" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/><circle cx="70" cy="26" r="15" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/>
{eyes_open(30, 70, 26, 10, 10.5, 1, 2)}
<path d="M30 52 Q50 66 70 52" stroke="#3B2A20" stroke-width="2.8" fill="none" stroke-linecap="round"/>
{cheeks(24, 76, 50, 6, 4)}
</symbol>'''


def frog_lift():
    return f'''<symbol id="ell-pond-frog-lifted" viewBox="0 -8 100 128">
<ellipse cx="32" cy="88" rx="10" ry="19" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/><ellipse cx="68" cy="88" rx="10" ry="19" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/>
<ellipse cx="29" cy="110" rx="13" ry="5.5" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/><ellipse cx="71" cy="110" rx="13" ry="5.5" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/>
<ellipse cx="14" cy="62" rx="7" ry="12" transform="rotate(20 14 62)" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/><ellipse cx="86" cy="62" rx="7" ry="12" transform="rotate(-20 86 62)" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/>
<ellipse cx="50" cy="60" rx="33" ry="31" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/>
<ellipse cx="50" cy="72" rx="21" ry="17" fill="{FBL}"/>
<g fill="{FS}"><circle cx="50" cy="38" r="3.5"/><circle cx="62" cy="43" r="2.6"/><circle cx="38" cy="43" r="2.6"/></g>
<circle cx="30" cy="26" r="15" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/><circle cx="70" cy="26" r="15" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/>
{eyes_open(30, 70, 26, 10, 10.5, 0, -1)}
<path d="M34 52 Q50 74 66 52 Z" fill="#5A2A2A" stroke="#3B2A20" stroke-width="2.5" stroke-linejoin="round"/><path d="M42 62 Q50 68 58 62 Q50 58 42 62Z" fill="#FF92C8"/>
{cheeks(24, 76, 50, 6, 4)}
</symbol>'''


def tube(d, w_out, w_in, col=FB, out=FO):
    return f'<path d="{d}" stroke="{out}" stroke-width="{w_out}" fill="none" stroke-linecap="round"/><path d="{d}" stroke="{col}" stroke-width="{w_in}" fill="none" stroke-linecap="round"/>'


def frog_leap():
    return f'''<symbol id="ell-pond-frog-leap" viewBox="-8 -10 158 124">
<g transform="rotate(-14 75 50)">
{tube('M56 62 Q30 72 12 80', 19, 14)}<ellipse cx="9" cy="82" rx="10" ry="5" transform="rotate(-20 9 82)" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/>
<ellipse cx="74" cy="56" rx="38" ry="24" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/>
<ellipse cx="76" cy="68" rx="26" ry="11" fill="{FBL}"/>
<g fill="{FS}"><circle cx="60" cy="48" r="3.4"/><circle cx="74" cy="44" r="2.6"/><circle cx="50" cy="54" r="2.4"/></g>
{tube('M98 64 Q118 62 136 50', 15, 10)}<ellipse cx="138" cy="48" rx="7" ry="6" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/>
<circle cx="84" cy="30" r="12" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/><circle cx="106" cy="34" r="14" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/>
{eyes_open(84, 106, 31, 8, 8.5, 2.5, 0)}
<path d="M96 56 Q112 66 124 54" stroke="#3B2A20" stroke-width="2.8" fill="none" stroke-linecap="round"/>
<ellipse cx="96" cy="58" rx="6" ry="4" fill="#FF92C8" opacity=".75"/>
</g>
</symbol>'''


def frog_swim():
    return f'''<symbol id="ell-pond-frog-swim" viewBox="0 0 100 64">
<ellipse cx="50" cy="40" rx="34" ry="20" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/>
<circle cx="30" cy="22" r="15" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/><circle cx="70" cy="22" r="15" fill="{FB}" stroke="{FO}" stroke-width="{LINE}"/>
{eyes_open(30, 70, 22, 10, 10.5, 1, 1)}
<path d="M38 44 Q50 54 62 44" stroke="#3B2A20" stroke-width="2.8" fill="none" stroke-linecap="round"/>
<path d="M8 50 Q16 44 28 50 T50 50 T72 50 T92 50 Q98 58 90 63 H10 Q2 58 8 50Z" fill="url(#ell-pond-swim-fade)"/>
<path d="M8 50 Q16 44 28 50 T50 50 T72 50 T92 50" stroke="#BFF0FF" stroke-width="3" fill="none" stroke-linecap="round" opacity=".75"/>
</symbol>'''


# ------------------------------------------------------------------ fireflies, lantern, pad, ripple
def firefly(lit=True):
    if lit:
        return '''<symbol id="ell-pond-firefly" viewBox="0 0 64 64">
<circle cx="32" cy="34" r="30" fill="url(#ell-pond-glow)"/>
<ellipse cx="19" cy="25" rx="8" ry="14" transform="rotate(-35 19 25)" fill="#E8F6FF" opacity=".8" stroke="#BFE9FA" stroke-width="1.5"/><ellipse cx="45" cy="25" rx="8" ry="14" transform="rotate(35 45 25)" fill="#E8F6FF" opacity=".8" stroke="#BFE9FA" stroke-width="1.5"/>
<path d="M27 14 Q24 7 19 6 M37 14 Q40 7 45 6" stroke="#2B3A75" stroke-width="2.5" fill="none" stroke-linecap="round"/><circle cx="19" cy="6" r="2.4" fill="#2B3A75"/><circle cx="45" cy="6" r="2.4" fill="#2B3A75"/>
<ellipse cx="32" cy="40" rx="12" ry="14" fill="#FFD43B" stroke="#E0A91C" stroke-width="2.5"/>
<ellipse cx="32" cy="45" rx="8.5" ry="8" fill="#FFF3B0"/>
<circle cx="32" cy="22" r="9.5" fill="#2B3A75" stroke="#1B2550" stroke-width="2"/>
<circle cx="28.5" cy="21" r="2.6" fill="#fff"/><circle cx="35.5" cy="21" r="2.6" fill="#fff"/><circle cx="29" cy="21.4" r="1.2" fill="#1B2550"/><circle cx="36" cy="21.4" r="1.2" fill="#1B2550"/>
<path d="M29 26.5 Q32 29 35 26.5" stroke="#FFD1E8" stroke-width="1.8" fill="none" stroke-linecap="round"/>
</symbol>'''
    return '''<symbol id="ell-pond-firefly-dim" viewBox="0 0 64 64">
<ellipse cx="19" cy="25" rx="8" ry="14" transform="rotate(-35 19 25)" fill="#9DB3E0" opacity=".35" stroke="#7F95C8" stroke-width="1.5"/><ellipse cx="45" cy="25" rx="8" ry="14" transform="rotate(35 45 25)" fill="#9DB3E0" opacity=".35" stroke="#7F95C8" stroke-width="1.5"/>
<path d="M27 14 Q24 7 19 6 M37 14 Q40 7 45 6" stroke="#5B6FA8" stroke-width="2.5" fill="none" stroke-linecap="round"/><circle cx="19" cy="6" r="2.4" fill="#5B6FA8"/><circle cx="45" cy="6" r="2.4" fill="#5B6FA8"/>
<ellipse cx="32" cy="40" rx="12" ry="14" fill="#6D7FB5" stroke="#4A5A94" stroke-width="2.5"/>
<ellipse cx="32" cy="45" rx="8.5" ry="8" fill="#8FA0CF"/>
<circle cx="32" cy="22" r="9.5" fill="#46568F" stroke="#34417A" stroke-width="2"/>
<path d="M26.5 21.5 Q28.5 23.5 30.5 21.5 M33.5 21.5 Q35.5 23.5 37.5 21.5" stroke="#C9D5F5" stroke-width="1.8" fill="none" stroke-linecap="round"/>
<path d="M29.5 27 Q32 28.6 34.5 27" stroke="#C9D5F5" stroke-width="1.6" fill="none" stroke-linecap="round"/>
</symbol>'''


NOTCH = 'M280 100 L530.3 133 A270 88 0 1 0 480.7 158.9 Z'


def pad_symbol():
    veins = ''.join(f'<path d="M280 100 L{280 + 262 * __import__("math").cos(a):.0f} {100 + 80 * __import__("math").sin(a):.0f}"/>' for a in
                    [x * 3.14159 / 180 for x in (-170, -135, -100, -62, -25, 75, 105, 140, 175)])
    return f'''<symbol id="ell-pond-pad" viewBox="0 0 560 200">
<ellipse cx="280" cy="118" rx="272" ry="80" fill="#06223F" opacity=".34"/>
<ellipse cx="280" cy="112" rx="276" ry="84" fill="none" stroke="#BFF0FF" stroke-width="3" opacity=".28"/>
<path d="{NOTCH}" fill="#1FAE74" stroke="#0E7A52" stroke-width="4" stroke-linejoin="round"/>
<path d="{NOTCH}" transform="translate(280 98) scale(.9 .84) translate(-280 -100)" fill="#35C98B" opacity=".75"/>
<g stroke="#0E7A52" stroke-width="3" stroke-linecap="round" opacity=".3">{veins}</g>
<path d="M60 60 Q110 28 200 24" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round" opacity=".28"/>
<g transform="translate(46 60)"><g fill="#FF92C8" stroke="#E04C98" stroke-width="2" stroke-linejoin="round"><ellipse cx="-14" cy="6" rx="9" ry="15" transform="rotate(-50 -14 6)"/><ellipse cx="14" cy="6" rx="9" ry="15" transform="rotate(50 14 6)"/><ellipse cx="0" cy="-2" rx="9" ry="17"/></g><circle cx="0" cy="8" r="5" fill="#FFC83D"/></g>
</symbol>'''


def ripple_symbol():
    return '''<symbol id="ell-pond-ripple" viewBox="0 0 200 60">
<ellipse cx="100" cy="30" rx="94" ry="26" fill="none" stroke="#BFF0FF" stroke-width="3" opacity=".4"/>
<ellipse cx="100" cy="30" rx="68" ry="19" fill="none" stroke="#BFF0FF" stroke-width="3.5" opacity=".65"/>
<ellipse cx="100" cy="30" rx="42" ry="12" fill="none" stroke="#fff" stroke-width="4" opacity=".9"/>
</symbol>'''


def lantern_symbol():
    return '''<symbol id="ell-pond-lantern" viewBox="0 0 60 90">
<path d="M18 14 Q30 -6 42 14" stroke="#D9A93F" stroke-width="4" fill="none" stroke-linecap="round"/>
<path d="M14 24 L46 24 L40 14 L20 14Z" fill="#D9A93F" stroke="#A97A1E" stroke-width="2" stroke-linejoin="round"/>
<path d="M12 28 C6 44 6 64 16 76 H44 C54 64 54 44 48 28Z" fill="#FFE9A0" stroke="#D9A93F" stroke-width="3" stroke-linejoin="round" opacity=".96"/>
<ellipse cx="30" cy="54" rx="11" ry="16" fill="#FFC83D"/><ellipse cx="30" cy="58" rx="6" ry="9" fill="#FFF7D6"/>
<path d="M17 36 Q14 50 18 62" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round" opacity=".7"/>
<rect x="14" y="76" width="32" height="9" rx="4" fill="#D9A93F" stroke="#A97A1E" stroke-width="2"/>
<path d="M30 24 V30" stroke="#D9A93F" stroke-width="3"/>
</symbol>'''


def jar_symbol():
    body = 'M100 86 L100 106 C100 114 60 118 44 146 C30 170 28 196 28 226 V400 C28 450 60 470 110 470 H330 C380 470 412 450 412 400 V226 C412 196 410 170 396 146 C380 118 340 114 340 106 V86 Z'
    return f'''<symbol id="ell-pond-jar" viewBox="0 0 440 500">
<ellipse cx="220" cy="486" rx="200" ry="10" fill="#06122F" opacity=".4"/>
<ellipse cx="220" cy="300" rx="260" ry="240" fill="url(#ell-pond-glow-warm)" opacity=".55"/>
<path d="{body}" fill="#BFE9FA" fill-opacity=".13" stroke="#DFF4FF" stroke-opacity=".9" stroke-width="5" stroke-linejoin="round"/>
<path d="M54 170 Q42 200 44 280 M60 150 Q70 138 86 130" stroke="#fff" stroke-width="7" fill="none" stroke-linecap="round" opacity=".38"/>
<path d="M392 200 Q398 240 394 300" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round" opacity=".22"/>
<rect x="88" y="62" width="264" height="30" rx="15" fill="#D9A93F" stroke="#A97A1E" stroke-width="3"/>
<path d="M118 66 C118 14 322 14 322 66" stroke="#D9A93F" stroke-width="7" fill="none" stroke-linecap="round"/>
<path d="M118 66 C118 14 322 14 322 66" stroke="#FFE9A0" stroke-width="2" fill="none" stroke-linecap="round" opacity=".6"/>
</symbol>'''


def star_symbol():
    return '''<symbol id="ell-pond-star" viewBox="0 0 64 64">
<path d="M32 4 L40 24 L61 25 L45 39 L50 60 L32 48 L14 60 L19 39 L3 25 L24 24Z" fill="#FFC83D" stroke="#E0A91C" stroke-width="3" stroke-linejoin="round"/>
<path d="M32 12 L37 25 L24 27Z" fill="#FFE9A0"/>
</symbol>'''


# ------------------------------------------------------------------ cast
def duckling(happy=False):
    Y, YO = '#FFD84A', '#E0A91C'
    if happy:
        wings = (f'<ellipse cx="22" cy="68" rx="11" ry="19" transform="rotate(-38 22 68)" fill="#F5C026" stroke="{YO}" stroke-width="{LINE}"/>'
                 f'<ellipse cx="98" cy="68" rx="11" ry="19" transform="rotate(38 98 68)" fill="#F5C026" stroke="{YO}" stroke-width="{LINE}"/>')
        eyes = eyes_happy(49, 71, 37, 7)
        beak = f'<path d="M50 46 Q60 41 70 46 Q68 58 60 59 Q52 58 50 46Z" fill="#FF9F43" stroke="#D9701F" stroke-width="2"/><path d="M53 50 Q60 55 67 50" stroke="#8A3A12" stroke-width="2" fill="none" stroke-linecap="round"/>'
        extra = sparkle(96, 16, 1.1) + sparkle(18, 28, .8)
    else:
        wings = (f'<ellipse cx="22" cy="84" rx="11" ry="19" transform="rotate(18 22 84)" fill="#F5C026" stroke="{YO}" stroke-width="{LINE}"/>'
                 f'<ellipse cx="98" cy="84" rx="11" ry="19" transform="rotate(-18 98 84)" fill="#F5C026" stroke="{YO}" stroke-width="{LINE}"/>')
        eyes = eyes_open(49, 71, 37, 7, 8.5, 0, 1)
        beak = '<path d="M50 46 Q60 41 70 46 Q68 56 60 57 Q52 56 50 46Z" fill="#FF9F43" stroke="#D9701F" stroke-width="2"/>'
        extra = ''
    sid = 'ell-pond-duckling-happy' if happy else 'ell-pond-duckling'
    return f'''<symbol id="{sid}" viewBox="0 -8 120 128">
<ellipse cx="60" cy="114" rx="52" ry="6" fill="#BFF0FF" opacity=".3"/>
<ellipse cx="44" cy="112" rx="11" ry="4" fill="#FF9F43"/><ellipse cx="76" cy="112" rx="11" ry="4" fill="#FF9F43"/>
<ellipse cx="60" cy="84" rx="41" ry="28" fill="{Y}" stroke="{YO}" stroke-width="{LINE}"/>
{wings}
<path d="M58 14 Q54 4 60 1 M64 14 Q68 4 74 6" stroke="{YO}" stroke-width="3" fill="none" stroke-linecap="round"/>
<circle cx="60" cy="38" r="27" fill="{Y}" stroke="{YO}" stroke-width="{LINE}"/>
{eyes}{beak}{cheeks(38, 82, 50, 6, 4)}{extra}
</symbol>'''


def turtle(happy=False):
    SH, SHO, SK, SKO = '#C8996A', '#A97A4C', '#8FD6A0', '#4FA86E'
    hy = 44 if happy else 62
    neck = f'<path d="M112 80 Q120 {hy + 16} 128 {hy + 14}" stroke="{SKO}" stroke-width="30" fill="none" stroke-linecap="round"/><path d="M112 80 Q120 {hy + 16} 128 {hy + 14}" stroke="{SK}" stroke-width="25" fill="none" stroke-linecap="round"/>'
    if happy:
        eyes = eyes_happy(121, 136, hy - 2, 6)
        extra = sparkle(146, 14, 1.1) + sparkle(18, 30, .8)
        legs = (f'<ellipse cx="44" cy="96" rx="12" ry="9" fill="{SK}" stroke="{SKO}" stroke-width="{LINE}"/><ellipse cx="112" cy="96" rx="12" ry="9" fill="{SK}" stroke="{SKO}" stroke-width="{LINE}"/>')
    else:
        eyes = eyes_open(121, 136, hy - 2, 6, 7, 1, 1)
        extra = ''
        legs = (f'<ellipse cx="44" cy="96" rx="12" ry="9" fill="{SK}" stroke="{SKO}" stroke-width="{LINE}"/><ellipse cx="108" cy="90" rx="12" ry="9" transform="rotate(-25 108 90)" fill="{SK}" stroke="{SKO}" stroke-width="{LINE}"/>')
    sid = 'ell-pond-turtle-happy' if happy else 'ell-pond-turtle'
    return f'''<symbol id="{sid}" viewBox="0 -8 160 124">
<ellipse cx="78" cy="112" rx="64" ry="6" fill="#BFF0FF" opacity=".3"/>
<ellipse cx="14" cy="88" rx="10" ry="6" fill="{SK}" stroke="{SKO}" stroke-width="{LINE}"/>
{legs}
{neck}
<path d="M18 88 C18 44 46 26 74 26 C102 26 126 44 126 88 Z" fill="{SH}" stroke="{SHO}" stroke-width="3" stroke-linejoin="round"/>
<path d="M74 26 V62 M74 62 L46 82 M74 62 L102 82" stroke="{SHO}" stroke-width="3" fill="none" stroke-linecap="round"/>
<ellipse cx="74" cy="45" rx="15" ry="11" fill="#E6C9A0" opacity=".7"/><ellipse cx="48" cy="70" rx="12" ry="9" fill="#E6C9A0" opacity=".55"/><ellipse cx="100" cy="70" rx="12" ry="9" fill="#E6C9A0" opacity=".55"/>
<ellipse cx="72" cy="90" rx="58" ry="10" fill="{SHO}"/><ellipse cx="72" cy="87" rx="54" ry="7" fill="#D9AE82"/>
<circle cx="128" cy="{hy}" r="20" fill="{SK}" stroke="{SKO}" stroke-width="{LINE}"/>
{eyes}{smile(128, hy + 8, 6)}{cheeks(114, 142, hy + 6, 4.5, 3)}{extra}
</symbol>'''


def dragonfly(happy=False):
    P, PO = '#FF6FB5', '#E04C98'
    if happy:
        tail = 'M98 66 Q132 74 148 52 Q156 40 150 26'
        eyes = eyes_happy(33, 51, 58, 6.5)
        extra = sparkle(150, 6, 1.0) + sparkle(14, 20, .8)
    else:
        tail = 'M98 66 Q134 74 160 62'
        eyes = eyes_open(33, 51, 58, 8.5, 9.5, 1, 1)
        extra = ''
    sid = 'ell-pond-dragonfly-happy' if happy else 'ell-pond-dragonfly'
    wing = 'fill="#CDEFFF" fill-opacity=".72" stroke="#7CCBEB" stroke-width="2.5"'
    return f'''<symbol id="{sid}" viewBox="0 -14 170 122">
<ellipse cx="66" cy="30" rx="34" ry="10" transform="rotate(-128 66 30)" {wing}/><ellipse cx="82" cy="24" rx="36" ry="10" transform="rotate(-100 82 24)" {wing}/>
<ellipse cx="98" cy="28" rx="34" ry="10" transform="rotate(-68 98 28)" {wing}/><ellipse cx="112" cy="38" rx="30" ry="9" transform="rotate(-36 112 38)" {wing}/>
<path d="{tail}" stroke="{PO}" stroke-width="14" fill="none" stroke-linecap="round"/><path d="{tail}" stroke="{P}" stroke-width="10" fill="none" stroke-linecap="round"/>
<path d="{tail}" stroke="#FFD1E8" stroke-width="10" fill="none" stroke-dasharray="3 11" stroke-dashoffset="-4"/>
<ellipse cx="84" cy="64" rx="26" ry="19" fill="{P}" stroke="{PO}" stroke-width="{LINE}"/><path d="M70 56 Q84 50 98 56" stroke="#FFD1E8" stroke-width="4" fill="none" stroke-linecap="round"/>
<circle cx="42" cy="62" r="24" fill="{P}" stroke="{PO}" stroke-width="{LINE}"/>
<circle cx="32" cy="46" r="3" fill="{PO}" opacity="0"/>
{eyes}{smile(42, 74, 6)}{cheeks(24, 60, 70, 5, 3.4)}{extra}
</symbol>'''


def fish(happy=False):
    O, OO = '#FF9F43', '#D9701F'
    if happy:
        g0, g1 = '<g transform="rotate(-24 70 50)">', '</g>'
        eye = f'<path d="M92 44 Q100 33 108 44" stroke="#3B2A20" stroke-width="3.4" fill="none" stroke-linecap="round"/>'
        extra = ('<g fill="#BFF0FF" opacity=".9"><circle cx="20" cy="92" r="4"/><circle cx="34" cy="100" r="3"/><circle cx="116" cy="96" r="3.4"/><circle cx="128" cy="86" r="2.4"/></g>' + sparkle(132, 12, 1.0) + sparkle(14, 20, .8))
        mouth = '<path d="M112 54 Q118 62 124 54" stroke="#8A3A12" stroke-width="2.6" fill="none" stroke-linecap="round"/>'
    else:
        g0, g1 = '<g>', '</g>'
        eye = f'<ellipse cx="100" cy="42" rx="10" ry="11" fill="#fff"/><circle cx="102" cy="44" r="6.2" fill="#3B2A20"/><circle cx="104.5" cy="41.5" r="2.2" fill="#fff"/>'
        extra = '<g fill="none" stroke="#BFF0FF" stroke-width="2.5" opacity=".85"><circle cx="138" cy="30" r="5"/><circle cx="130" cy="14" r="3.4"/></g>'
        mouth = '<path d="M112 56 Q118 62 124 55" stroke="#8A3A12" stroke-width="2.6" fill="none" stroke-linecap="round"/>'
    sid = 'ell-pond-fish-happy' if happy else 'ell-pond-fish'
    return f'''<symbol id="{sid}" viewBox="0 -8 150 116">
{g0}
<path d="M30 50 L4 26 Q12 50 4 74Z" fill="#FF8A2A" stroke="{OO}" stroke-width="{LINE}" stroke-linejoin="round"/>
<path d="M52 24 Q72 2 94 24Z" fill="#FF8A2A" stroke="{OO}" stroke-width="{LINE}" stroke-linejoin="round"/>
<ellipse cx="72" cy="52" rx="46" ry="32" fill="{O}" stroke="{OO}" stroke-width="{LINE}"/>
<ellipse cx="72" cy="66" rx="34" ry="15" fill="#FFD8A8"/>
<g fill="none" stroke="{OO}" stroke-width="2.2" stroke-linecap="round" opacity=".5"><path d="M44 42 q6 5 12 0 M58 42 q6 5 12 0 M51 52 q6 5 12 0"/></g>
<path d="M84 34 Q80 52 86 70" stroke="{OO}" stroke-width="2.5" fill="none" stroke-linecap="round" opacity=".5"/>
<path d="M62 62 Q52 76 66 80 Q70 70 68 62Z" fill="#FF8A2A" stroke="{OO}" stroke-width="2" stroke-linejoin="round"/>
{eye}{mouth}<ellipse cx="104" cy="58" rx="5.5" ry="3.6" fill="#FF92C8" opacity=".75"/>
{g1}{extra}
</symbol>'''


# ------------------------------------------------------------------ backdrops (960 x 600 scene, overflow visible)
def stars(pts, cls='twinkle'):
    return f'<g class="{cls}" fill="#fff">' + ''.join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in pts) + '</g>'


def reeds(x, y, n=4, col='#1E7A58', dark=False):
    out = ''
    cat = '#6B4129' if not dark else '#2B1E1A'
    for i in range(n):
        dx = i * 16 - n * 8
        lean = (i - n / 2) * 4
        h = 70 + (i * 37 % 40)
        out += f'<path d="M{x + dx} {y} Q{x + dx + lean} {y - h / 2} {x + dx + lean * 2} {y - h}" stroke="{col}" stroke-width="5" fill="none" stroke-linecap="round"/>'
        if i % 2 == 0:
            out += f'<ellipse cx="{x + dx + lean * 2}" cy="{y - h - 10}" rx="6" ry="15" fill="{cat}"/>'
    return out


def backdrop_dusk():
    return f'''<symbol id="ell-pond-backdrop" viewBox="0 0 960 600" overflow="visible" style="overflow:visible">
<rect x="-3000" y="-3000" width="6960" height="3400" fill="url(#ell-pond-sky)"/>
{stars([(120, 130, 2), (250, 190, 1.6), (330, 100, 2.2), (470, 150, 1.5), (560, 108, 2), (650, 190, 1.6), (720, 110, 2.2), (880, 160, 1.8), (60, 220, 1.5), (-120, 150, 2), (1060, 130, 2), (-260, 90, 1.6), (1200, 210, 1.8)])}
<path d="M-3000 340 H0 C80 292 160 262 250 280 C340 296 400 330 520 322 C640 314 720 276 810 270 C880 266 930 290 960 300 H3960 V345 H-3000Z" fill="#1D4F7C"/>
<path d="M-3000 352 H0 C90 330 190 318 300 330 C420 344 560 346 700 330 C800 318 900 322 960 334 H3960 V356 H-3000Z" fill="#12335E"/>
<rect x="-3000" y="334" width="6960" height="3400" fill="url(#ell-pond-water)"/>
<path d="M-3000 346 H3960" stroke="#7FD6E8" stroke-width="3" opacity=".35"/>
<g stroke="#BFF0FF" stroke-width="3" stroke-linecap="round" opacity=".16"><path d="M60 372 H170 M210 392 H330 M120 560 H260 M700 580 H840 M20 470 H110 M880 396 H960 M-200 400 H-90 M1040 480 H1160"/></g>
<ellipse cx="800" cy="372" rx="90" ry="9" fill="#FFE9A0" opacity=".14"/>
<g>{reeds(70, 345, 5)}{reeds(640, 342, 3)}{reeds(944, 345, 3)}{reeds(-80, 345, 4)}{reeds(1090, 345, 4)}</g>
</symbol>'''


def backdrop_night():
    pts = [(60, 100, 2.2), (150, 190, 1.6), (240, 120, 2), (330, 220, 1.4), (420, 110, 2.2), (560, 100, 1.8), (640, 200, 1.6), (720, 90, 2.4),
           (790, 230, 1.6), (880, 120, 2), (930, 210, 1.6), (500, 220, 1.4), (190, 280, 1.4), (-100, 120, 2), (-220, 210, 1.6), (1060, 100, 2.2), (1180, 200, 1.6)]
    return f'''<symbol id="ell-pond-backdrop-night" viewBox="0 0 960 600" overflow="visible" style="overflow:visible">
<rect x="-3000" y="-3000" width="6960" height="3400" fill="url(#ell-pond-sky-night)"/>
{stars(pts)}
<circle cx="150" cy="150" r="70" fill="url(#ell-pond-glow-warm)" opacity=".8"/><path d="M168 122 A34 34 0 1 0 168 178 A28 28 0 1 1 168 122Z" fill="#FFF1C2"/>
<path d="M-3000 360 H0 C100 322 190 300 290 318 C400 338 470 360 600 340 C720 320 800 290 900 300 C930 304 950 310 960 314 H3960 V366 H-3000Z" fill="#0E2A5E"/>
<path d="M-3000 374 H0 C120 350 260 346 400 360 C560 376 700 362 960 350 H3960 V380 H-3000Z" fill="#091C46"/>
<rect x="-3000" y="360" width="6960" height="3400" fill="url(#ell-pond-water-night)"/>
<path d="M-3000 372 H3960" stroke="#7FA8F0" stroke-width="3" opacity=".3"/>
<g fill="#fff" opacity=".35"><circle cx="150" cy="450" r="2"/><circle cx="620" cy="560" r="2"/><circle cx="800" cy="440" r="2"/><circle cx="60" cy="560" r="2"/><circle cx="900" cy="570" r="2"/></g>
<ellipse cx="150" cy="420" rx="40" ry="7" fill="#FFF1C2" opacity=".16"/>
<g>{reeds(40, 372, 4, '#14513F', True)}{reeds(930, 372, 4, '#14513F', True)}{reeds(-90, 372, 4, '#14513F', True)}{reeds(1070, 372, 4, '#14513F', True)}</g>
</symbol>'''


def bank_symbol():
    return '''<symbol id="ell-pond-bank" viewBox="0 0 260 70">
<ellipse cx="130" cy="58" rx="126" ry="12" fill="#06223F" opacity=".35"/>
<path d="M4 56 C14 28 70 14 130 14 C190 14 246 28 256 56 C230 66 30 66 4 56Z" fill="#2E8F5B" stroke="#1F6E45" stroke-width="3" stroke-linejoin="round"/>
<path d="M30 40 C60 26 110 22 150 24" stroke="#6FD39A" stroke-width="5" fill="none" stroke-linecap="round" opacity=".6"/>
<g stroke="#46C47E" stroke-width="3.5" stroke-linecap="round" fill="none"><path d="M60 24 l-3 -9 M66 22 l2 -10 M190 24 l3 -9 M198 26 l6 -8 M120 16 l-2 -8"/></g>
<g fill="#C8996A"><ellipse cx="44" cy="46" rx="8" ry="5"/><ellipse cx="214" cy="46" rx="7" ry="4.5"/></g>
</symbol>'''


GRADS = '''
<linearGradient id="ell-pond-sky" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="340"><stop offset="0" stop-color="#070F33"/><stop offset=".45" stop-color="#1B3A7A"/><stop offset=".85" stop-color="#2B8DAA"/><stop offset="1" stop-color="#4FB8C4"/></linearGradient>
<linearGradient id="ell-pond-water" gradientUnits="userSpaceOnUse" x1="0" y1="334" x2="0" y2="600"><stop offset="0" stop-color="#1D7AA3"/><stop offset="1" stop-color="#0C3560"/></linearGradient>
<linearGradient id="ell-pond-sky-night" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="370"><stop offset="0" stop-color="#050B26"/><stop offset=".6" stop-color="#0F2468"/><stop offset="1" stop-color="#1D4F9A"/></linearGradient>
<linearGradient id="ell-pond-water-night" gradientUnits="userSpaceOnUse" x1="0" y1="360" x2="0" y2="600"><stop offset="0" stop-color="#143A7C"/><stop offset="1" stop-color="#071940"/></linearGradient>
<linearGradient id="ell-pond-wood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D9AA77"/><stop offset="1" stop-color="#B98254"/></linearGradient>
<radialGradient id="ell-pond-glow"><stop offset="0" stop-color="#FFE066" stop-opacity=".95"/><stop offset=".45" stop-color="#FFD43B" stop-opacity=".38"/><stop offset="1" stop-color="#FFD43B" stop-opacity="0"/></radialGradient>
<radialGradient id="ell-pond-glow-warm"><stop offset="0" stop-color="#FFC83D" stop-opacity=".55"/><stop offset=".5" stop-color="#FFC83D" stop-opacity=".18"/><stop offset="1" stop-color="#FFC83D" stop-opacity="0"/></radialGradient>
<linearGradient id="ell-pond-swim-fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1B72A0" stop-opacity=".95"/><stop offset=".55" stop-color="#1B72A0" stop-opacity=".7"/><stop offset="1" stop-color="#1B72A0" stop-opacity="0"/></linearGradient>
<filter id="ell-pond-soft" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="6" stdDeviation="7" flood-color="#030A24" flood-opacity=".35"/></filter>
<filter id="ell-pond-text-glow" x="-20%" y="-30%" width="140%" height="180%"><feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#FFD43B" flood-opacity=".55"/></filter>'''

DEFS = (f'<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>{GRADS}{owl_defs}'
        + hazel_symbols + backdrop_dusk() + backdrop_night() + bank_symbol() + pad_symbol() + ripple_symbol()
        + frog_sit() + frog_lift() + frog_leap() + frog_swim() + firefly(True) + firefly(False)
        + lantern_symbol() + jar_symbol() + star_symbol()
        + duckling() + duckling(True) + turtle() + turtle(True) + dragonfly() + dragonfly(True) + fish() + fish(True)
        + '</defs></svg>')


# ------------------------------------------------------------------ scene parts
def use(sym, x, y, w, h, extra=''):
    return f'<use href="#{sym}" x="{x}" y="{y}" width="{w}" height="{h}" {extra}/>'


def hud(filled):
    dots = ''.join(
        f'<circle cx="{480 - 99 + i * 22}" cy="44" r="8" fill="{"#FFD43B" if i < filled else "#16306A"}" stroke="{"#E0A91C" if i < filled else "#7CA6E0"}" stroke-width="2.5"/>'
        for i in range(10))
    glow = ''.join(f'<circle cx="{480 - 99 + i * 22}" cy="44" r="15" fill="url(#ell-pond-glow)"/>' for i in range(filled))
    return f'''<g class="fred">
<rect x="16" y="18" width="128" height="64" rx="32" fill="#0A625C"/><rect x="16" y="12" width="128" height="64" rx="32" fill="#0F857D"/>
<text x="80" y="53" text-anchor="middle" fill="#fff" font-size="26" font-weight="600">&#8249; Back</text>
{glow}{dots}
<circle cx="920" cy="44" r="32" fill="#fff" filter="url(#ell-pond-soft)"/><path d="M905 37 h8 l12 -9 v32 l-12 -9 h-8z" fill="#0F857D"/><path d="M932 35 q8 9 0 18" stroke="#0F857D" stroke-width="3.6" fill="none" stroke-linecap="round"/></g>'''


def bubble(x, y, w, h, tailx, inner):
    return (f'<g filter="url(#ell-pond-soft)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="32" fill="#fff"/>'
            f'<path d="M{tailx - 18} {y + h - 2} l10 36 l26 -36Z" fill="#fff"/></g>{inner}')


def hint(x, w, text, y=92):
    return (f'<g class="fred"><rect x="{x}" y="{y}" width="{w}" height="40" rx="20" fill="#fff" filter="url(#ell-pond-soft)"/>'
            f'<text x="{x + w / 2}" y="{y + 27}" text-anchor="middle" font-size="20" font-weight="600" fill="#3B2A20">{text}</text></g>')


def hazel_keeper(x0, y0, w):
    s = w / 240
    return (f'<g transform="translate({x0} {y0}) scale({s:.4f})">'
            '<path d="M236 196 L270 62" stroke="#8B5A3C" stroke-width="8" stroke-linecap="round"/><path d="M236 196 L270 62" stroke="#C8996A" stroke-width="3" stroke-linecap="round"/>'
            '<circle cx="270" cy="120" r="80" fill="url(#ell-pond-glow-warm)"/>'
            + use('ell-pond-hazel-keeper', 0, 0, 240, 262)
            + use('ell-pond-lantern', 242, 50, 56, 84)
            + '</g>')


FROG_SLOTS_BACK = [168, 258, 348, 438]
FROG_SLOTS_FRONT = [123, 213, 303, 393]


def pad_group(x0, y0, s, back, front, extra=''):
    fr = ''.join(use('ell-pond-frog', cx - 42, 18, 84, 84, 'class="bob"') for cx in back)
    fr += ''.join(use('ell-pond-frog', cx - 42, 84, 84, 84, 'class="bob"') for cx in front)
    return f'<g transform="translate({x0} {y0}) scale({s})">{use("ell-pond-pad", 0, 0, 560, 200)}{fr}{extra}</g>'


def dest(cx, cy, rx=108, ry=56):
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#BFF0FF" opacity=".12"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="#BFF0FF" stroke-width="4" stroke-dasharray="14 12" stroke-linecap="round" opacity=".7"/>')


def order_pad(icon_sym, text1, text2, n, iw, icon_h):
    icons = ''.join(use(icon_sym, 150 + i * (iw + 6), 168, iw, icon_h) for i in range(n))
    return bubble(24, 96, 290, 168, 110,
                  '<g class="fred" font-weight="600" fill="#3B2A20">'
                  f'<text x="169" y="136" text-anchor="middle" font-size="22">{text1}</text><text x="169" y="164" text-anchor="middle" font-size="22">{text2}</text>'
                  f'<text x="106" y="236" text-anchor="middle" font-size="64" font-weight="700" fill="#0F857D">{n}</text></g>' + icons)


def friend(sym, x, y, w, h, ripple=True, bob=True):
    r = use('ell-pond-ripple', x - 10, y + h - 24, w + 20, 36, 'class="rip"') if ripple else ''
    return f'{r}<g class="{"bob" if bob else ""}">{use(sym, x, y, w, h)}</g>'


def choice(cx, n, state='idle'):
    fill = {'idle': '#fff', 'pick': '#fff'}[state]
    return (f'<g class="fred"><rect x="{cx - 88}" y="478" width="176" height="96" rx="28" fill="#0F857D"/>'
            f'<rect x="{cx - 88}" y="470" width="176" height="96" rx="28" fill="{fill}" stroke="#0F857D" stroke-width="4"/>'
            f'<text x="{cx}" y="535" text-anchor="middle" font-size="64" font-weight="700" fill="#0F857D">{n}</text></g>')


# ------------------------------------------------------------------ scenes
def scene1_body():
    return f'''{use("ell-pond-backdrop", 0, 0, 960, 600)}
<ellipse cx="820" cy="300" rx="190" ry="120" fill="url(#ell-pond-glow-warm)"/>
{use("ell-pond-bank", 740, 288, 200, 54)}{hazel_keeper(762, 138, 150)}
<ellipse cx="840" cy="350" rx="150" ry="14" fill="#FFC83D" opacity=".12"/>
{dest(846, 474)}
{pad_group(170, 352, 1, FROG_SLOTS_BACK, FROG_SLOTS_FRONT)}
{friend("ell-pond-duckling", 38, 330, 130, 139)}
{order_pad("ell-pond-frog", "3 frogs are going", "for a swim!", 3, 40, 40)}
{hint(380, 330, "Drag frogs into the water")}'''


def scene1():
    return f'<svg viewBox="0 0 960 600" class="scene" role="img" aria-label="Pad scene: the duckling asks for 3 frogs to go for a swim. Eight frogs sit on a lily pad.">{scene1_body()}{hud(3)}</svg>'


def scene1_wide():
    return (f'<svg viewBox="-330 0 1620 600" class="scene" role="img" aria-label="Same pad scene on a very wide screen: the backdrop continues without a seam.">'
            f'<rect x="-330" y="0" width="1620" height="600" fill="none"/>{scene1_body()}</svg>')


def scene2():
    back = FROG_SLOTS_BACK[:3]
    front = FROG_SLOTS_FRONT[1:3]
    lifted = ('<g class="lift">'
              '<ellipse cx="702" cy="420" rx="40" ry="10" fill="#06223F" opacity=".38"/>'
              + use('ell-pond-frog-lifted', 654, 270, 96, 122, 'transform="rotate(-8 702 330)"') + '</g>')
    leap = (use('ell-pond-ripple', 758, 470, 150, 44, 'class="rip"')
            + '<g class="hop">' + use('ell-pond-frog-leap', 766, 344, 140, 110) + '</g>')
    swim = (use('ell-pond-ripple', 840, 498, 120, 36, 'class="rip2"') + '<g class="bob">' + use('ell-pond-frog-swim', 868, 494, 70, 45) + '</g>')
    order = bubble(24, 96, 290, 168, 110,
                   '<g class="fred" font-weight="600" fill="#3B2A20">'
                   '<text x="169" y="136" text-anchor="middle" font-size="22">3 frogs are going</text><text x="169" y="164" text-anchor="middle" font-size="22">for a swim!</text>'
                   '<text x="106" y="236" text-anchor="middle" font-size="64" font-weight="700" fill="#0F857D">3</text></g>'
                   + use('ell-pond-frog', 150, 168, 40, 40) + use('ell-pond-frog', 196, 168, 40, 40, 'opacity=".4"') + use('ell-pond-frog', 242, 168, 40, 40, 'opacity=".4"'))
    return f'''<svg viewBox="0 0 960 600" class="scene" role="img" aria-label="Mid action: one frog is lifted, one leaps over the water, one already swims. Five frogs are left on the pad.">
{use("ell-pond-backdrop", 0, 0, 960, 600)}
<ellipse cx="820" cy="300" rx="190" ry="120" fill="url(#ell-pond-glow-warm)"/>
{use("ell-pond-bank", 740, 288, 200, 54)}{hazel_keeper(762, 138, 150)}
{dest(846, 474)}
{pad_group(170, 352, 1, back, front)}
{lifted}{leap}{swim}
{friend("ell-pond-duckling", 38, 330, 130, 139)}
{order}
{hint(380, 330, "One more to go!")}
{hud(4)}</svg>'''


def scene3():
    frogs_back = FROG_SLOTS_BACK[:3]
    frogs_front = FROG_SLOTS_FRONT[1:3]
    card = ('<g class="fred" filter="url(#ell-pond-soft)"><rect x="200" y="92" width="560" height="104" rx="32" fill="#fff"/></g>'
            '<g class="fred" font-weight="600" fill="#3B2A20" text-anchor="middle"><text x="480" y="134" font-size="32">How many frogs are</text><text x="480" y="174" font-size="32">still on the pad?</text></g>')
    return f'''<svg viewBox="0 0 960 600" class="scene" role="img" aria-label="Question step: five frogs on the pad, three big number choices 6, 5 and 11.">
{use("ell-pond-backdrop", 0, 0, 960, 600)}
<ellipse cx="820" cy="300" rx="190" ry="120" fill="url(#ell-pond-glow-warm)"/>
{use("ell-pond-bank", 740, 288, 200, 54)}{hazel_keeper(762, 138, 150)}
{pad_group(214, 258, .95, frogs_back, frogs_front)}
{friend("ell-pond-duckling", 38, 310, 130, 139)}
{card}
{choice(260, 6)}{choice(480, 5)}{choice(700, 11)}
{hud(4)}</svg>'''


def frame(x, y, lit, ghost):
    cells = ''
    for r in range(2):
        for c in range(5):
            i = r * 5 + c
            cx, cy = x + c * 64 + 32, y + r * 64 + 32
            cells += f'<rect x="{x + c * 64 + 3}" y="{y + r * 64 + 3}" width="58" height="58" rx="10" fill="{"#17357A" if i in lit else "#0B1D4B"}" stroke="#35599F" stroke-width="2"/>'
            if i in lit:
                cells += use('ell-pond-firefly', cx - 30, cy - 30, 60, 60, 'class="tw%d"' % (i % 3))
            elif i in ghost:
                cells += use('ell-pond-firefly-dim', cx - 26, cy - 26, 52, 52, 'opacity=".55"')
    return f'<rect x="{x - 6}" y="{y - 6}" width="332" height="140" rx="16" fill="#08183F" stroke="#7CA6E0" stroke-width="3"/>{cells}'


def trail(d):
    return f'<path d="{d}" stroke="#FFE066" stroke-width="4" fill="none" stroke-dasharray="2 13" stroke-linecap="round" opacity=".6"/>'


def scene4():
    jx, jy = 260, 76
    frames = frame(jx + 60, jy + 150, set(range(10)), set()) + frame(jx + 60, jy + 302, set(), {0, 1, 2})
    flies = (trail('M480 160 C560 110 640 120 720 150') + trail('M480 170 C580 200 700 130 800 120') + trail('M480 170 C540 250 640 260 760 240')
             + '<g class="float1">' + use('ell-pond-firefly', 690, 108, 84, 84) + '</g>'
             + '<g class="float2">' + use('ell-pond-firefly', 770, 70, 84, 84) + '</g>'
             + '<g class="float3">' + use('ell-pond-firefly', 730, 214, 84, 84) + '</g>')
    cork = ('<g class="cork"><rect x="0" y="0" width="70" height="30" rx="12" fill="#C8996A" stroke="#A97A4C" stroke-width="3" transform="translate(610 516) rotate(-6 35 15)"/></g>')
    dock = '<rect x="266" y="544" width="428" height="34" rx="12" fill="url(#ell-pond-wood)" stroke="#8B5A3C" stroke-width="3"/><path d="M262 562 H700" stroke="#8B5A3C" stroke-width="2" opacity=".4"/>'
    order = bubble(24, 96, 258, 168, 110,
                   '<g class="fred" font-weight="600" fill="#3B2A20">'
                   '<text x="153" y="136" text-anchor="middle" font-size="22">3 fireflies are</text><text x="153" y="164" text-anchor="middle" font-size="22">flying home!</text>'
                   '<text x="86" y="236" text-anchor="middle" font-size="64" font-weight="700" fill="#0F857D">3</text></g>'
                   + ''.join(use('ell-pond-firefly', 128 + i * 46, 182, 48, 48) for i in range(3)))
    token = ('<g filter="url(#ell-pond-soft)"><rect x="24" y="406" width="226" height="166" rx="24" fill="#0C1F4F" stroke="#7CA6E0" stroke-width="3"/></g>'
             '<g class="fred"><text x="137" y="438" text-anchor="middle" font-size="22" font-weight="600" fill="#fff">Break ten</text></g>'
             '<g transform="translate(40 456)"><rect x="-4" y="-4" width="108" height="48" rx="8" fill="#08183F" stroke="#7CA6E0" stroke-width="2"/>'
             + ''.join(f'<circle cx="{10 + (i % 5) * 21}" cy="{10 + (i // 5) * 24}" r="8" fill="#FFD43B" stroke="#E0A91C" stroke-width="1.5"/>' for i in range(10))
             + '</g><path d="M152 478 H172 M164 470 L174 478 L164 486" stroke="#FFE066" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
             '<g class="glowpulse"><circle cx="212" cy="478" r="44" fill="url(#ell-pond-glow)"/></g>'
             '<rect x="184" y="452" width="56" height="52" rx="14" fill="#FFD43B" stroke="#E0A91C" stroke-width="3"/>'
             '<g class="fred"><text x="212" y="490" text-anchor="middle" font-size="34" font-weight="700" fill="#3B2A20">10</text>'
             '<text x="137" y="534" text-anchor="middle" font-size="17" font-weight="500" fill="#DDE8FF">A full frame folds</text><text x="137" y="556" text-anchor="middle" font-size="17" font-weight="500" fill="#DDE8FF">into one 10 token.</text></g>')
    return f'''<svg viewBox="0 0 960 600" class="scene" role="img" aria-label="Lantern scene: a glass jar holds two ten-frames. Ten fireflies glow in the first frame, three have flown out into the night sky. A frame folds into a ten token.">
{use("ell-pond-backdrop-night", 0, 0, 960, 600)}
{use("ell-pond-bank", 730, 520, 230, 62)}
{dock}
<g transform="translate({jx} {jy})">{use("ell-pond-jar", 0, 0, 440, 500)}</g>
{frames}{cork}{flies}
{use("ell-pond-hazel-point", 770, 392, 140, 152)}
{friend("ell-pond-dragonfly", 28, 276, 170, 122, False)}
{order}{token}
{hud(6)}</svg>'''


def scene5():
    # ten fireflies drifting toward the lantern, each with a short motion tail behind it
    pts = [(96, 290, 70), (200, 200, 62), (290, 330, 60), (150, 430, 64), (372, 350, 52), (650, 214, 60), (640, 316, 62), (810, 170, 56)]
    trails = ''
    for x, y, s in pts:
        p0 = (x + s / 2, y + s / 2); p2 = (480, 330); c = ((p0[0] + p2[0]) / 2, min(p0[1], p2[1]) - 50)
        def q(t):
            return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p2[1])
        a, m, e = q(0.18), q(0.34), q(0.5)
        trails += trail(f'M{a[0]:.0f} {a[1]:.0f} Q{m[0]:.0f} {m[1] - 6:.0f} {e[0]:.0f} {e[1]:.0f}')
    flies = ''.join(f'<g class="float{i % 3 + 1}">' + use('ell-pond-firefly', x, y, s, s) + '</g>' for i, (x, y, s) in enumerate(pts))
    stars3 = ''.join(use('ell-pond-star', 480 - 118 + i * 80, (212 if i != 1 else 196), 76, 76, 'class="pop"') for i in range(3))
    return f'''<svg viewBox="0 0 960 600" class="scene" role="img" aria-label="End screen: ten glowing fireflies drift toward the lantern, Hazel cheers, the text says The pond is glowing, three stars.">
{use("ell-pond-backdrop-night", 0, 0, 960, 600)}
{use("ell-pond-bank", 640, 452, 270, 72)}
<rect x="352" y="548" width="256" height="30" rx="12" fill="url(#ell-pond-wood)" stroke="#8B5A3C" stroke-width="3"/>
<g class="glowpulse"><circle cx="480" cy="420" r="200" fill="url(#ell-pond-glow-warm)"/></g>
{use("ell-pond-jar", 360, 296, 240, 273)}
{trails}
{use('ell-pond-firefly', 436, 410, 62, 62, 'class="tw1"')}{use('ell-pond-firefly', 488, 446, 56, 56, 'class="tw2"')}
<g class="fred" text-anchor="middle"><text x="480" y="160" font-size="56" font-weight="700" fill="#fff" filter="url(#ell-pond-text-glow)">The pond is glowing!</text></g>
{stars3}
{flies}
{use("ell-pond-hazel-cheer", 700, 296, 170, 185, 'class="bob"')}
<g class="fred"><rect x="740" y="524" width="184" height="64" rx="32" fill="#D99E12"/><rect x="740" y="518" width="184" height="64" rx="32" fill="#FFC83D"/><text x="832" y="560" text-anchor="middle" font-size="26" font-weight="600" fill="#3B2A20">Play again</text></g>
<g class="fred"><rect x="16" y="18" width="128" height="64" rx="32" fill="#0A625C"/><rect x="16" y="12" width="128" height="64" rx="32" fill="#0F857D"/><text x="80" y="53" text-anchor="middle" fill="#fff" font-size="26" font-weight="600">&#8249; Back</text></g>
</svg>'''


# ------------------------------------------------------------------ cast sheet and notes
def card(sym, w, h, label, sub, dw=None):
    dw = dw or 150
    dh = dw * h / w
    return (f'<figure class="cast"><svg viewBox="0 0 {w} {h}" width="{dw}" height="{dh:.0f}"><use href="#{sym}" width="{w}" height="{h}"/></svg>'
            f'<figcaption><b>{label}</b><br>{sub}</figcaption></figure>')


def cast():
    out = '<h3>The four friends (anonymous, each one asks one order)</h3><div class="row">'
    for name, sym, w, h, a_txt, h_txt in [('Duckling', 'duckling', 120, 128, 'arriving, paddles in', 'happy, wings up'),
                                           ('Turtle', 'turtle', 160, 124, 'arriving, walks in', 'happy, head up'),
                                           ('Dragonfly', 'dragonfly', 170, 122, 'arriving, hovers in', 'happy, tail curls'),
                                           ('Fish', 'fish', 150, 116, 'arriving, swims in', 'happy, jumps')]:
        out += card('ell-pond-' + sym, w, h, name, a_txt, 170) + card('ell-pond-' + sym + '-happy', w, h, name, h_txt, 170)
    out += '</div><h3>Frog (the item the child moves), four poses</h3><div class="row">'
    out += (card('ell-pond-frog', 100, 100, 'Sitting', 'on the pad', 130) + card('ell-pond-frog-lifted', 100, 128, 'Lifted', 'while dragged, soft shadow below', 130)
            + card('ell-pond-frog-leap', 158, 124, 'Leaping', 'mid-hop over the water', 190) + card('ell-pond-frog-swim', 100, 64, 'Swimming', 'after the splash', 130))
    out += '</div><h3>Firefly (the item in the lantern), lit and dim</h3><div class="row">'
    out += (card('ell-pond-firefly', 64, 64, 'Lit', 'in the frame or in the sky', 130) + card('ell-pond-firefly-dim', 64, 64, 'Dim', 'ghost of a firefly that flew out', 130)
            + card('ell-pond-star', 64, 64, 'Star', 'end screen reward', 110)
            + card('ell-pond-lantern', 60, 90, 'Hand lantern', "Hazel's pole lantern", 90) + card('ell-pond-ripple', 200, 60, 'Ripple', 'ring under every exit', 170)
            + '</div>')
    return out


def palette():
    groups = {}
    for n, h, u in PAL:
        groups.setdefault(u, []).append((n, h))
    out = ''
    for n, h, u in PAL:
        txt = '#fff' if n not in ('Frog', 'Frog belly', 'Firefly glow', 'Firefly core', 'Ripple', 'Lantern light', 'White', 'Duckling', 'Fish', 'Cheek pink', 'Dragonfly', 'Turtle skin', 'Pad highlight', 'Turtle shell') else '#3B2A20'
        out += f'<div class="sw"><span style="background:{h};color:{txt};border:1px solid rgba(0,0,0,.15)">{h}</span><b>{n}</b><i>{u}</i></div>'
    return out


CSS = '''
:root{--cream:#FFF7E8;--ink:#3B2A20;--teal:#0F857D}
body{margin:0;background:var(--cream);color:var(--ink);font-family:Andika,system-ui,sans-serif;padding:24px 16px 60px}
.fred{font-family:Fredoka,ui-rounded,"Arial Rounded MT Bold",system-ui,sans-serif}
main{max-width:980px;margin:0 auto}
h1{font-family:Fredoka,system-ui;color:var(--teal);margin:0 0 4px} h2{font-family:Fredoka,system-ui;margin:40px 0 8px} h3{font-family:Fredoka,system-ui;margin:24px 0 10px}
p{line-height:1.5;max-width:70ch} .scene{width:100%;height:auto;border-radius:32px;box-shadow:0 10px 30px rgba(43,58,103,.25);display:block;background:#0B1640}
.row{display:flex;flex-wrap:wrap;gap:16px;align-items:flex-end}
.cast{margin:0;text-align:center;background:linear-gradient(#1B3A7A,#12335E);color:#fff;border-radius:24px;padding:14px 18px 10px;box-shadow:0 6px 18px rgba(43,58,103,.2)}
.cast figcaption{font-size:15px;margin-top:6px;line-height:1.3}
.note{background:#fff;border-left:6px solid var(--teal);border-radius:12px;padding:10px 16px;max-width:70ch}
.sw{display:flex;align-items:center;gap:10px;margin:4px 0}.sw span{display:inline-block;width:92px;text-align:center;border-radius:8px;padding:6px 0;font:600 14px Andika,system-ui}.sw i{color:#6b5a4b;font-size:14px}
.pal{columns:2 360px}
table{border-collapse:collapse;width:100%;background:#fff;border-radius:12px;overflow:hidden;font-size:15px}
td,th{padding:8px 12px;border-bottom:1px solid #eadfca;text-align:left;vertical-align:top}th{background:#0F857D;color:#fff;font-family:Fredoka,system-ui}
code{background:#fff;padding:1px 6px;border-radius:6px;font-size:14px}
.ids{columns:2 380px;font-size:14px;line-height:1.6}
.bob,.lift,.float1,.float2,.float3,.pop,.rip,.rip2,.hop,.glowpulse,.cork{transform-box:fill-box;transform-origin:center}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}} .bob{animation:bob 3s ease-in-out infinite}
@keyframes lift{0%,100%{transform:translateY(0) rotate(0)}50%{transform:translateY(-5px) rotate(2deg)}} .lift{animation:lift 1.8s ease-in-out infinite}
@keyframes hop{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}} .hop{animation:hop 1.6s ease-in-out infinite}
@keyframes fl1{0%,100%{transform:translate(0,0)}50%{transform:translate(8px,-10px)}} .float1{animation:fl1 3.4s ease-in-out infinite}
@keyframes fl2{0%,100%{transform:translate(0,0)}50%{transform:translate(-8px,-12px)}} .float2{animation:fl2 4s ease-in-out infinite}
@keyframes fl3{0%,100%{transform:translate(0,0)}50%{transform:translate(6px,10px)}} .float3{animation:fl3 3.8s ease-in-out infinite}
@keyframes pop{0%,100%{transform:scale(1)}50%{transform:scale(1.08)}} .pop{animation:pop 2.2s ease-in-out infinite}
@keyframes rip{0%{transform:scale(.55);opacity:0}30%{opacity:1}100%{transform:scale(1.15);opacity:0}} .rip{animation:rip 2.4s ease-out infinite} .rip2{animation:rip 2.4s ease-out 1.1s infinite}
@keyframes tw{0%,100%{opacity:.7}50%{opacity:1}} .twinkle{animation:tw 3.2s ease-in-out infinite} .tw0{animation:tw 2.2s ease-in-out infinite}.tw1{animation:tw 2.7s ease-in-out infinite}.tw2{animation:tw 3.1s ease-in-out infinite}
@keyframes gp{0%,100%{opacity:.75}50%{opacity:1}} .glowpulse{animation:gp 2.8s ease-in-out infinite}
@media (prefers-reduced-motion:reduce){.bob,.lift,.hop,.float1,.float2,.float3,.pop,.rip,.rip2,.twinkle,.tw0,.tw1,.tw2,.glowpulse{animation:none}.rip,.rip2{opacity:.7}}
'''

NOTES = '''
<h2>7. Palette and notes</h2>
<h3>Palette</h3>
<div class="pal">%PAL%</div>
<p class="note">Text rules: white (#FFFFFF) on the dusk and night sky (contrast about 15:1 against #0F2468), ink (#3B2A20) on white bubbles and number buttons,
teal (#0F857D) numerals on white (4.5:1, large text). The teal Back button keeps white text (4.5:1) as in the garden.</p>
<h3>What animates (transform and opacity only) and its reduced-motion version</h3>
<table>
<tr><th>Part</th><th>Normal motion</th><th>Reduced motion</th></tr>
<tr><td>Frog leaving the pad (<code>ell-pond-frog-lifted</code> then <code>ell-pond-frog-leap</code>)</td><td>Lift (translate, small rotate), arc over the water (translate), land (scale squash)</td><td>The frog fades out in place (opacity) and a calm frog fades in at the water</td></tr>
<tr><td>Ripple ring (<code>ell-pond-ripple</code>)</td><td>Scale from .55 to 1.15 while opacity goes 0, 1, 0</td><td>No scaling: the ring becomes a soft glow that fades in and out (opacity only)</td></tr>
<tr><td>Pad frogs that stay</td><td>Tiny bob (translateY 3 px), one bounce on a right answer (scale)</td><td>No bob. Right answer: a soft glow behind them (opacity)</td></tr>
<tr><td>Frog that hops back (taken too many)</td><td>Hop onto the pad with a small wobble (translate, rotate)</td><td>Fades out of the water, fades in on the pad</td></tr>
<tr><td>Firefly leaving the frame (<code>ell-pond-firefly</code>)</td><td>Drift up along an arc (translate), blink (opacity)</td><td>Fades out in the frame, fades in in the sky, no drift</td></tr>
<tr><td>Firefly glow</td><td>Opacity pulse .7 to 1, each firefly on its own rhythm (2.2 to 3.1 s)</td><td>Steady glow, no pulse</td></tr>
<tr><td>Ten token fold</td><td>Frame scales down (scale) into the token, token pops (scale)</td><td>Frame fades out, token fades in</td></tr>
<tr><td>Friend arriving (duckling, turtle, dragonfly, fish)</td><td>Enter by translate (paddle, walk, hover, swim), idle bob 3 px</td><td>Plain fade in, no bob</td></tr>
<tr><td>Stars at the end, lantern glow</td><td>Stars pop one by one (scale), lantern glow pulses (opacity), fireflies drift (translate)</td><td>Stars appear with a fade, glow steady, fireflies sit still</td></tr>
<tr><td>Hazel</td><td>Existing kit poses (wings, blink) on the part ids in the owl art</td><td>Kit already swaps to a still pose</td></tr>
</table>
<p>Not animated and never recolored for feedback: the backdrop, hills, water and the lily pad. No red anywhere in feedback. A wrong "How many left?" tap dims that choice, as in the garden.</p>
<h3>Symbols to import into the game skin</h3>
<p class="ids"><code>ell-pond-backdrop</code> (pad levels) and <code>ell-pond-backdrop-night</code> (lantern levels), both 960 x 600 with overflow visible and userSpaceOnUse gradients,
<code>ell-pond-bank</code>, <code>ell-pond-pad</code>, <code>ell-pond-frog</code>, <code>ell-pond-frog-lifted</code>, <code>ell-pond-frog-leap</code>, <code>ell-pond-frog-swim</code>,
<code>ell-pond-ripple</code>, <code>ell-pond-firefly</code>, <code>ell-pond-firefly-dim</code>, <code>ell-pond-lantern</code> (hand lantern), <code>ell-pond-jar</code> (big glass jar, frames are drawn by the game),
<code>ell-pond-star</code>, <code>ell-pond-duckling</code>, <code>ell-pond-turtle</code>, <code>ell-pond-dragonfly</code>, <code>ell-pond-fish</code> (each with a <code>-happy</code> twin),
and the Hazel poses <code>ell-pond-hazel</code>, <code>-keeper</code>, <code>-cheer</code>, <code>-point</code> (preview only: the game uses the kit's Hazel).
Gradients and filters used by the symbols: <code>ell-pond-sky</code>, <code>-water</code>, <code>-sky-night</code>, <code>-water-night</code>, <code>-wood</code>, <code>-glow</code>, <code>-glow-warm</code>, <code>-soft</code>.
Port like the garden: one string per symbol, items map <code>frog: 'ell-pond-frog'</code>, <code>firefly: 'ell-pond-firefly'</code>, customers list for the four friends, backdrop per layout.</p>
<p class="note">Open questions for review: (1) the duckling, turtle, dragonfly and fish are all friendly and bright; the dragonfly is the only pink one, as the ladybug was the only red one in the garden. (2) Frogs are lime green on a teal-green pad: they separate by value and outline, not by hue alone. (3) The preview uses Fredoka and Andika from Google Fonts. Offline, the page falls back to a rounded system font.</p>
'''


def build():
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pond Hop art preview</title>
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Andika:wght@400;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>{DEFS}<main>
<h1>Pond Hop: art direction preview</h1>
<p>Static prototype for approval. Nothing here is the final game. It shows the dusk pond look, the cast and the glowing sky reward for Subtraction for Grade 1, so we can agree on the art before any development.
Same bones as Addition Garden (rounded shapes, one outline weight, Fredoka numbers, teal buttons) in a different mood: evening, lantern light, things leaving instead of arriving.
Gentle idle motion only. All scenes are 960 x 600.</p>
<h2>1. Pad scene (levels 1 to 3)</h2>
<p>The duckling asks for 3 frogs to go for a swim. Eight frogs sit on the lily pad, the dashed patch of water is where they go. Hazel is the lantern keeper on the far bank.</p>
{scene1()}
<p>Wide screen check: the same scene on a 1620 wide canvas. The sky, hills, water and reeds continue past the 960 scene edges with no seam.</p>
{scene1_wide()}
<h2>2. Same scene, mid-action</h2>
<p>One frog is lifted with a soft shadow, one leaps over the water above a ripple ring, one already swims. Five frogs are left on the pad. The bubble shows the order with the frogs still to send dimmed.</p>
{scene2()}
<h2>3. The "How many are still on the pad?" step</h2>
<p>The pad calms down with the 5 remaining frogs. Three big choices, each 176 by 96 px: an off by one answer, the right answer and the wrong operation (8 + 3).</p>
{scene3()}
<h2>4. Lantern scene (levels 4 and 5)</h2>
<p>Thirteen fireflies: a full ten-frame, plus three that were in the second frame and have flown out into the night sky (their empty cells show a dim ghost). The card at the bottom left shows the "10" token idea for level 5: a full frame folds into one glowing 10.</p>
{scene4()}
<h2>5. The cast</h2>
<p>Same line weight, cheeks and eyes as the garden cast. Every character has headroom in its box so ears, eyestalks and antennae never clip.</p>
{cast()}
<h2>6. End screen: the pond is glowing</h2>
<p>Ten fireflies, one per solved order, drift together toward the lantern. Nothing is saved to the website and nothing is lost if the child stops. Stars still go to the website as today.</p>
{scene5()}
{NOTES.replace('%PAL%', palette())}
</main></body></html>'''
    open('index.html', 'w').write(html)


build()
