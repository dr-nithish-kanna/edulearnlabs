"""Letter Station art preview (game 6). Static art only: no game logic, no kit code.
Run from this folder:  python3 build.py   ->  index.html
Fonts: Andika and Fredoka come from the website's self-hosted subsets (../../src/assets/fonts) and are embedded
as data URIs so the preview looks right offline and in screenshots."""
import re, math, base64

INK = '#3B2A20'

# ------------------------------------------------------------------ shared pieces
owl = open('../mascot/owl.svg').read()
owl_inner = re.sub(r'^<svg[^>]*>', '', owl.strip())
owl_inner = owl_inner[:owl_inner.rindex('</svg>')]
owl_inner = re.sub(r'<title>.*?</title>', '', owl_inner, flags=re.S)
owl_inner = re.sub(r'<!--.*?-->', '', owl_inner, flags=re.S)


def b64(path):
    return base64.b64encode(open(path, 'rb').read()).decode()


FONTS = (f"@font-face{{font-family:Andika;font-weight:400;src:url(data:font/woff2;base64,{b64('../../src/assets/fonts/andika-400.woff2')}) format('woff2')}}"
         f"@font-face{{font-family:Fredoka;font-weight:400 700;src:url(data:font/woff2;base64,{b64('../../src/assets/fonts/fredoka-600.woff2')}) format('woff2')}}")


def eyes_round(pts, r=8, gaze=(0, 0)):
    out = ''
    for (x, y) in pts:
        x += gaze[0]
        y += gaze[1]
        out += (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{INK}"/>'
                f'<circle cx="{x - r * .32:.1f}" cy="{y - r * .38:.1f}" r="{r * .38:.1f}" fill="#fff"/>'
                f'<circle cx="{x + r * .36:.1f}" cy="{y + r * .4:.1f}" r="{r * .17:.1f}" fill="#fff" opacity=".8"/>')
    return out


def eyes_happy(pts, r=8):
    out = ''
    for (x, y) in pts:
        out += (f'<path d="M{x - r - 1} {y + 3} Q{x} {y - r - 3} {x + r + 1} {y + 3}" fill="none" stroke="{INK}" '
                f'stroke-width="4.6" stroke-linecap="round"/>')
    return out


def sparkle_star(x, y, s, fill='#FFC83D'):
    return (f'<path d="M{x} {y - s} L{x + s * .28} {y - s * .28} L{x + s} {y} L{x + s * .28} {y + s * .28} '
            f'L{x} {y + s} L{x - s * .28} {y + s * .28} L{x - s} {y} L{x - s * .28} {y - s * .28}Z" fill="{fill}" '
            f'stroke="{fill}" stroke-width="2" stroke-linejoin="round"/>')


def star5(cx, cy, R, r, fill, stroke):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        k = R if i % 2 == 0 else r
        pts.append(f'{cx + k * math.cos(a):.1f},{cy + k * math.sin(a):.1f}')
    return f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="{stroke}" stroke-width="2" stroke-linejoin="round"/>'


# ------------------------------------------------------------------ the fox station master
O, OD, CR, DK = '#F28C38', '#C96A1E', '#FFF1D6', '#6E3B22'
TEAL, TD = '#0F857D', '#0A625C'


def fox(pose):
    """viewBox 0 0 180 200. pose: n (asking), h (happy), t (thinking). Faces the viewer, like Hazel."""
    happy, think = pose == 'h', pose == 't'
    # tail: bushy, cream tip, on the viewer's left. Raised when happy.
    tail_rot = ' transform="rotate(-14 70 156)"' if happy else ''
    tail = (f'<g{tail_rot}><path d="M72 160 C30 172 6 142 14 100 C16 90 24 86 28 96 C34 116 48 130 76 138Z" fill="{O}" stroke="{OD}" stroke-width="3" stroke-linejoin="round"/>'
            f'<path d="M14 100 C16 90 24 86 28 96 C30 104 33 110 36 115 C24 118 14 112 14 100Z" fill="#fff" stroke="#E9D9BF" stroke-width="2.5" stroke-linejoin="round"/></g>')
    feet = (f'<ellipse cx="66" cy="189" rx="15" ry="8" fill="{DK}"/><ellipse cx="114" cy="189" rx="15" ry="8" fill="{DK}"/>')
    shadow = '<ellipse cx="90" cy="193" rx="62" ry="6" fill="#2b3a67" opacity=".15"/>'
    body = (f'<ellipse cx="90" cy="150" rx="40" ry="36" fill="{O}" stroke="{OD}" stroke-width="3"/>'
            f'<path d="M52 146 Q54 116 90 114 Q126 116 128 146 Q130 184 90 187 Q50 184 52 146Z" fill="{TEAL}" stroke="{TD}" stroke-width="3" stroke-linejoin="round"/>'
            f'<path d="M62 140 Q62 126 74 120" fill="none" stroke="#14A39A" stroke-width="4" stroke-linecap="round" opacity=".8"/>'
            f'<path d="M78 117 L90 142 L102 117Z" fill="{CR}" stroke="#E6C9A0" stroke-width="2" stroke-linejoin="round"/>'
            f'<path d="M80 119 L100 119 L90 136Z" fill="#FFC83D" stroke="#D99E12" stroke-width="2" stroke-linejoin="round"/>'
            f'<circle cx="90" cy="156" r="4.2" fill="#FFC83D" stroke="#D99E12" stroke-width="2"/><circle cx="90" cy="172" r="4.2" fill="#FFC83D" stroke="#D99E12" stroke-width="2"/>')

    def arm(cx, cy, rot, paw):
        return (f'<ellipse cx="{cx}" cy="{cy}" rx="12" ry="26" transform="rotate({rot} {cx} {cy})" fill="{TEAL}" stroke="{TD}" stroke-width="3"/>'
                f'<circle cx="{paw[0]}" cy="{paw[1]}" r="9.5" fill="{DK}"/>')
    paddle_disk = lambda x, y: (f'<circle cx="{x}" cy="{y}" r="17" fill="#2FCB86" stroke="#1FA56A" stroke-width="3"/>'
                                f'<path d="M{x - 9} {y - 5} Q{x - 6} {y - 11} {x + 1} {y - 12}" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" opacity=".7"/>')
    if happy:
        arms = (arm(38, 130, -34, (24, 106)) + arm(142, 130, 34, (156, 106)) +
                f'<path d="M156 104 L159 58" stroke="#C8996A" stroke-width="5" stroke-linecap="round"/>' + paddle_disk(159, 44))
    elif think:
        arms = (arm(50, 152, 8, (46, 174)) + arm(119, 132, -24, (109, 109)))
    else:
        arms = (arm(50, 152, 8, (46, 174)) + arm(134, 148, -12, (141, 168)) +
                f'<path d="M141 170 L152 102" stroke="#C8996A" stroke-width="5" stroke-linecap="round"/>' + paddle_disk(153, 86))
    # head
    ear_o = f'<path d="M52 62 L38 14 L84 48Z" fill="{O}" stroke="{OD}" stroke-width="3.2" stroke-linejoin="round"/>'
    ear_t = f'<path d="M38 14 L42.9 30.8 L54.1 25.9Z" fill="{DK}" stroke="{DK}" stroke-width="3.2" stroke-linejoin="round"/>'
    ear_i = '<path d="M55 56 L47 29 L71 46Z" fill="#FFB3DA" stroke="#FFB3DA" stroke-width="3" stroke-linejoin="round"/>'
    ears = f'<g>{ear_o}{ear_i}{ear_t}</g><g transform="translate(180 0) scale(-1 1)">{ear_o}{ear_i}{ear_t}</g>'
    face = (f'<ellipse cx="90" cy="82" rx="46" ry="37" fill="{O}" stroke="{OD}" stroke-width="3"/>'
            f'<path d="M48 90 Q62 82 90 100 Q118 82 132 90 Q132 117 90 120 Q48 117 48 90Z" fill="{CR}"/>'
            f'<ellipse cx="59" cy="99" rx="7.5" ry="4.8" fill="#FF6FB5" opacity="{.8 if happy else .6}"/><ellipse cx="121" cy="99" rx="7.5" ry="4.8" fill="#FF6FB5" opacity="{.8 if happy else .6}"/>'
            f'<path d="M81 93 Q90 88 99 93 Q97 104 90 106 Q83 104 81 93Z" fill="{DK}" stroke="{DK}" stroke-width="2.5" stroke-linejoin="round"/>'
            f'<ellipse cx="87" cy="92" rx="3" ry="1.6" fill="#fff" opacity=".7"/>')
    if happy:
        face += (eyes_happy([(68, 80), (112, 80)], 8) +
                 f'<path d="M78 108 Q90 130 102 108Z" fill="{DK}" stroke="{DK}" stroke-width="3" stroke-linejoin="round"/>'
                 '<path d="M84 117 Q90 124 96 117 Q90 113 84 117Z" fill="#FF6FB5"/>')
    elif think:
        face += (eyes_round([(68, 80), (112, 80)], 8.5, gaze=(-3, -3)) +
                 f'<path d="M84 111 Q90 113 96 111" fill="none" stroke="{DK}" stroke-width="3.4" stroke-linecap="round"/>' +
                 f'<path d="M58 66 Q68 60 78 64" fill="none" stroke="{DK}" stroke-width="3.6" stroke-linecap="round"/>'
                 f'<path d="M102 60 Q114 54 124 62" fill="none" stroke="{DK}" stroke-width="3.6" stroke-linecap="round"/>')
    else:
        face += (eyes_round([(68, 80), (112, 80)], 8.5) +
                 f'<path d="M81 109 Q85.5 116 90 109 Q94.5 116 99 109" fill="none" stroke="{DK}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')
    cap = (f'<path d="M60 54 L64 30 Q90 18 116 30 L120 54Z" fill="{TEAL}" stroke="{TD}" stroke-width="3" stroke-linejoin="round"/>'
           f'<path d="M70 32 Q90 25 110 32" fill="none" stroke="#14A39A" stroke-width="4" stroke-linecap="round" opacity=".85"/>'
           f'<rect x="58" y="46" width="64" height="11" rx="5" fill="#FFC83D" stroke="#D99E12" stroke-width="2.5"/>'
           f'<path d="M64 58 Q90 70 116 58 Q90 62 64 58Z" fill="{TD}" stroke="{TD}" stroke-width="3" stroke-linejoin="round"/>'
           + star5(90, 38, 8.5, 3.8, '#FFC83D', '#D99E12'))
    head = ears + face + cap
    if think:
        head = f'<g transform="rotate(-7 90 118)">{head}</g>'
    extra = ''
    if happy:
        extra = sparkle_star(16, 40, 9) + sparkle_star(176, 118, 7, '#FF6FB5') + sparkle_star(112, 8, 6, '#2FB5EC')
    if think:
        extra = ('<circle cx="146" cy="58" r="3.6" fill="#fff" stroke="#9CC7E6" stroke-width="2"/>'
                 '<circle cx="155" cy="44" r="5.4" fill="#fff" stroke="#9CC7E6" stroke-width="2"/>'
                 '<circle cx="166" cy="26" r="8" fill="#fff" stroke="#9CC7E6" stroke-width="2"/>')
    if think:  # the paw sits on the cheek, in front of the face
        return shadow + tail + feet + body + arms[:arms.index('<ellipse', 10)] + head + arms[arms.index('<ellipse', 10):] + extra
    return shadow + tail + feet + body + (arms if not happy else arms) + head + extra


# ------------------------------------------------------------------ the picture set (A to Z), viewBox 0 0 100 100
def wedge(cx, cy, r, a1, a2, fill):
    x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
    x2, y2 = cx + r * math.cos(math.radians(a2)), cy + r * math.sin(math.radians(a2))
    return f'<path d="M{cx} {cy} L{x1:.1f} {y1:.1f} A{r} {r} 0 0 1 {x2:.1f} {y2:.1f}Z" fill="{fill}"/>'


def eye(x, y, r=3.4):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{INK}"/><circle cx="{x - r * .3:.1f}" cy="{y - r * .35:.1f}" r="{r * .36:.1f}" fill="#fff"/>'


def blush(x, y, rx=5, ry=3.2, o=.6):
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#FF6FB5" opacity="{o}"/>'


ground = '<ellipse cx="50" cy="90" rx="30" ry="4.5" fill="#2b3a67" opacity=".14"/>'

PICS = {}
PICS['A'] = ('apple', ground +
             '<path d="M50 31 C38 22 15 28 15 54 C15 77 33 91 50 85 C67 91 85 77 85 54 C85 28 62 22 50 31Z" fill="#EF5B45" stroke="#C9402E" stroke-width="2.5" stroke-linejoin="round"/>'
             '<path d="M50 31 Q49 19 56 12" fill="none" stroke="#6E432A" stroke-width="4" stroke-linecap="round"/>'
             '<path d="M54 21 Q66 8 81 16 Q71 31 54 21Z" fill="#2FCB86" stroke="#1FA56A" stroke-width="2.5" stroke-linejoin="round"/>'
             '<ellipse cx="29" cy="50" rx="5" ry="10" transform="rotate(14 29 50)" fill="#fff" opacity=".45"/>')
PICS['B'] = ('ball', ground +
             '<circle cx="50" cy="50" r="38" fill="#fff"/>' +
             wedge(50, 50, 38, -90, -30, '#FF6FB5') + wedge(50, 50, 38, -30, 30, '#fff') + wedge(50, 50, 38, 30, 90, '#FFC83D') +
             wedge(50, 50, 38, 90, 150, '#fff') + wedge(50, 50, 38, 150, 210, '#2FB5EC') + wedge(50, 50, 38, 210, 270, '#fff') +
             '<circle cx="50" cy="50" r="38" fill="none" stroke="#3B2A20" stroke-opacity=".25" stroke-width="2.5"/>'
             '<circle cx="50" cy="50" r="6" fill="#fff" stroke="#3B2A20" stroke-opacity=".25" stroke-width="2"/>'
             '<ellipse cx="33" cy="30" rx="8" ry="4.5" transform="rotate(-35 33 30)" fill="#fff" opacity=".7"/>')
PICS['C'] = ('cat', ground +
             '<path d="M20 52 L18 14 L44 30Z" fill="#A9B7C6" stroke="#8394A6" stroke-width="3" stroke-linejoin="round"/><path d="M24 40 L23 24 L35 32Z" fill="#FFB3DA" stroke="#FFB3DA" stroke-width="3" stroke-linejoin="round"/>'
             '<path d="M80 52 L82 14 L56 30Z" fill="#A9B7C6" stroke="#8394A6" stroke-width="3" stroke-linejoin="round"/><path d="M76 40 L77 24 L65 32Z" fill="#FFB3DA" stroke="#FFB3DA" stroke-width="3" stroke-linejoin="round"/>'
             '<ellipse cx="50" cy="56" rx="35" ry="29" fill="#A9B7C6" stroke="#8394A6" stroke-width="3"/>'
             '<path d="M44 30 V40 M50 28 V40 M56 30 V40" stroke="#8394A6" stroke-width="3.4" stroke-linecap="round"/>'
             '<ellipse cx="50" cy="66" rx="19" ry="14" fill="#F4F1EA"/>' + eye(36, 54, 4.6) + eye(64, 54, 4.6) +
             '<path d="M45 61 Q50 58 55 61 Q53 66 50 67 Q47 66 45 61Z" fill="#FF8FB8" stroke="#FF8FB8" stroke-width="2" stroke-linejoin="round"/>'
             '<path d="M50 67 V70 M42 71 Q46 75 50 70 Q54 75 58 71" fill="none" stroke="#3B2A20" stroke-width="2.4" stroke-linecap="round"/>'
             '<g stroke="#8394A6" stroke-width="2" stroke-linecap="round"><path d="M10 62 L28 64 M10 72 L28 68 M90 62 L72 64 M90 72 L72 68"/></g>' + blush(28, 68, 5, 3) + blush(72, 68, 5, 3))
PICS['D'] = ('dog', ground +
             '<path d="M22 28 Q4 30 6 60 Q8 78 22 74 Q26 52 28 34Z" fill="#8B5A3C" stroke="#6E432A" stroke-width="3" stroke-linejoin="round"/>'
             '<path d="M78 28 Q96 30 94 60 Q92 78 78 74 Q74 52 72 34Z" fill="#8B5A3C" stroke="#6E432A" stroke-width="3" stroke-linejoin="round"/>'
             '<ellipse cx="50" cy="48" rx="31" ry="30" fill="#E8B77A" stroke="#C48D4F" stroke-width="3"/>'
             '<ellipse cx="50" cy="66" rx="19" ry="15" fill="#FFF1D6"/>' + eye(37, 44, 4.6) + eye(63, 44, 4.6) +
             '<path d="M42 58 Q50 53 58 58 Q56 67 50 68 Q44 67 42 58Z" fill="#3B2A20" stroke="#3B2A20" stroke-width="2" stroke-linejoin="round"/>'
             '<ellipse cx="46" cy="58" rx="2.6" ry="1.4" fill="#fff" opacity=".7"/>'
             '<path d="M50 68 V72" stroke="#3B2A20" stroke-width="2.6" stroke-linecap="round"/><path d="M42 76 Q50 90 58 76Z" fill="#FF6FB5" stroke="#3B2A20" stroke-width="2.6" stroke-linejoin="round"/>'
             '<path d="M33 35 Q38 31 43 33 M57 33 Q62 31 67 35" fill="none" stroke="#C48D4F" stroke-width="3" stroke-linecap="round"/>')
PICS['E'] = ('egg', '<ellipse cx="50" cy="90" rx="28" ry="4.5" fill="#2b3a67" opacity=".14"/>'
             '<path d="M50 8 C68 8 78 34 78 48 C78 62 66 70 50 70 C34 70 22 62 22 48 C22 34 32 8 50 8Z" fill="#FFF6E5" stroke="#D9BE92" stroke-width="3" stroke-linejoin="round"/>'
             '<ellipse cx="37" cy="30" rx="5" ry="10" transform="rotate(18 37 30)" fill="#fff" opacity=".9"/>'
             '<g fill="#E3C79A"><circle cx="62" cy="44" r="2.2"/><circle cx="52" cy="58" r="2"/><circle cx="66" cy="58" r="1.8"/><circle cx="46" cy="40" r="1.8"/></g>'
             '<path d="M26 62 H74 Q76 86 64 90 H36 Q24 86 26 62Z" fill="#14A39A" stroke="#0F857D" stroke-width="3" stroke-linejoin="round"/>'
             '<path d="M24 64 H76" stroke="#0F857D" stroke-width="6" stroke-linecap="round"/><path d="M30 78 Q50 84 70 78" fill="none" stroke="#FFC83D" stroke-width="3" stroke-linecap="round" stroke-dasharray="1 7"/>')
PICS['F'] = ('fish', '<ellipse cx="50" cy="90" rx="30" ry="4" fill="#2b3a67" opacity=".1"/>'
             '<path d="M72 50 L94 30 Q98 50 94 70Z" fill="#1E8FC0" stroke="#1E8FC0" stroke-width="3" stroke-linejoin="round"/>'
             '<path d="M40 28 Q52 12 62 30Z" fill="#1E8FC0" stroke="#1E8FC0" stroke-width="3" stroke-linejoin="round"/>'
             '<path d="M42 72 Q50 88 62 72Z" fill="#1E8FC0" stroke="#1E8FC0" stroke-width="3" stroke-linejoin="round"/>'
             '<ellipse cx="46" cy="50" rx="36" ry="25" fill="#2FB5EC" stroke="#1E8FC0" stroke-width="3"/>'
             '<path d="M44 34 Q52 50 44 66 M58 32 Q66 50 58 68" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".5"/>'
             '<path d="M20 58 Q14 66 24 66" fill="#FFF" opacity="0"/>' + eye(26, 46, 4.6) + blush(28, 58, 4.5, 3) +
             '<path d="M14 54 Q20 62 28 58" fill="none" stroke="#3B2A20" stroke-width="2.6" stroke-linecap="round"/>'
             '<circle cx="12" cy="28" r="4" fill="none" stroke="#2FB5EC" stroke-width="2.4"/><circle cx="20" cy="16" r="2.6" fill="none" stroke="#2FB5EC" stroke-width="2.2"/>')
grapes = ''
for (gx, gy) in [(34, 40), (50, 38), (66, 40), (42, 54), (58, 54), (34, 62)[:0] or (50, 68)]:
    grapes += f'<circle cx="{gx}" cy="{gy}" r="11" fill="#8E5BD6" stroke="#6E3FB5" stroke-width="2.5"/><ellipse cx="{gx - 3.5}" cy="{gy - 4}" rx="3" ry="2" fill="#fff" opacity=".55"/>'
PICS['G'] = ('grapes', ground +
             '<path d="M50 28 Q50 16 58 10" fill="none" stroke="#6E432A" stroke-width="4" stroke-linecap="round"/>'
             '<path d="M54 18 Q68 6 82 14 Q72 30 54 18Z" fill="#2FCB86" stroke="#1FA56A" stroke-width="2.5" stroke-linejoin="round"/>' + grapes +
             '<circle cx="32" cy="58" r="11" fill="#8E5BD6" stroke="#6E3FB5" stroke-width="2.5"/><circle cx="68" cy="58" r="11" fill="#8E5BD6" stroke="#6E3FB5" stroke-width="2.5"/>'
             '<ellipse cx="28.5" cy="54" rx="3" ry="2" fill="#fff" opacity=".55"/><ellipse cx="64.5" cy="54" rx="3" ry="2" fill="#fff" opacity=".55"/>')
PICS['H'] = ('house', ground +
             '<rect x="20" y="44" width="60" height="44" rx="6" fill="#FFE2B0" stroke="#E0B070" stroke-width="3"/>'
             '<path d="M10 48 L50 12 L90 48Z" fill="#EF5B45" stroke="#C9402E" stroke-width="3.2" stroke-linejoin="round"/>'
             '<rect x="62" y="16" width="10" height="18" rx="2" fill="#C9402E"/>'
             '<rect x="42" y="62" width="16" height="26" rx="7" fill="#0F857D" stroke="#0A625C" stroke-width="2.5"/><circle cx="53" cy="76" r="1.8" fill="#FFC83D"/>'
             '<rect x="26" y="54" width="13" height="13" rx="3" fill="#BFE9FA" stroke="#2FB5EC" stroke-width="2.5"/><rect x="61" y="54" width="13" height="13" rx="3" fill="#BFE9FA" stroke="#2FB5EC" stroke-width="2.5"/>')
blocks = ''.join(f'<path d="{d}" fill="none" stroke="#6FA8D6" stroke-width="2.4" stroke-linecap="round"/>' for d in
                 ['M16 66 H84', 'M24 52 H76', 'M36 66 V80', 'M64 66 V80', 'M50 44 V52', 'M32 52 V66', 'M68 52 V66'])
PICS['I'] = ('igloo', '<ellipse cx="50" cy="86" rx="44" ry="6" fill="#CFE6F7"/><path d="M12 82 A38 38 0 0 1 88 82Z" fill="#fff" stroke="#4F97C8" stroke-width="3.4" stroke-linejoin="round"/>' + blocks +
             '<path d="M38 82 V70 A12 12 0 0 1 62 70 V82Z" fill="#3E6A8F" stroke="#2F5577" stroke-width="2.5" stroke-linejoin="round"/>')
PICS['J'] = ('jam', ground +
             '<rect x="22" y="38" width="56" height="50" rx="14" fill="#F4EEFB" stroke="#B9A6E8" stroke-width="3"/>'
             '<path d="M28 52 H72 V76 Q72 84 64 84 H36 Q28 84 28 76Z" fill="#B0306E" stroke="#8A2255" stroke-width="2"/>'
             '<ellipse cx="42" cy="62" rx="4" ry="7" transform="rotate(12 42 62)" fill="#fff" opacity=".4"/>'
             '<rect x="26" y="24" width="48" height="16" rx="7" fill="#0F857D" stroke="#0A625C" stroke-width="3"/>'
             '<path d="M34 28 H66" stroke="#14A39A" stroke-width="3" stroke-linecap="round"/>'
             '<rect x="36" y="56" width="28" height="18" rx="5" fill="#FFF7E8" opacity=".0"/>')
PICS['K'] = ('kite', '<path d="M50 78 Q38 86 50 90 Q62 94 56 99" fill="none" stroke="#C8996A" stroke-width="2.6" stroke-linecap="round"/>'
             '<path d="M50 6 L80 36 L50 78 L20 36Z" fill="#FF6FB5" stroke="#D94E94" stroke-width="3" stroke-linejoin="round"/>'
             '<path d="M50 6 L80 36 L50 36Z" fill="#FFC83D"/><path d="M50 78 L20 36 L50 36Z" fill="#2FB5EC"/>'
             '<path d="M50 6 L80 36 L50 78 L20 36Z" fill="none" stroke="#D94E94" stroke-width="3" stroke-linejoin="round"/>'
             '<path d="M50 6 V78 M20 36 H80" stroke="#fff" stroke-width="2.2" opacity=".7"/>'
             '<g fill="#2FCB86" stroke="#1FA56A" stroke-width="2" stroke-linejoin="round"><path d="M44 84 L38 80 L38 90Z"/><path d="M50 82 L56 86 L56 78Z" fill="#FFC83D" stroke="#D99E12"/></g>')
PICS['L'] = ('lemon', ground +
             '<g transform="rotate(-18 50 52)"><path d="M10 52 Q18 44 25 44 C32 24 68 24 75 44 Q82 44 90 52 Q82 60 75 60 C68 80 32 80 25 60 Q18 60 10 52Z" fill="#FFD93D" stroke="#E0A91C" stroke-width="3" stroke-linejoin="round"/>'
             '<ellipse cx="38" cy="42" rx="9" ry="4.5" transform="rotate(-20 38 42)" fill="#fff" opacity=".55"/></g>'
             '<path d="M64 26 Q74 10 90 16 Q84 32 64 26Z" fill="#2FCB86" stroke="#1FA56A" stroke-width="2.5" stroke-linejoin="round"/>')
PICS['M'] = ('moon', '<path d="M62 12 A40 40 0 1 0 90 62 A32 32 0 0 1 62 12Z" fill="#FFC83D" stroke="#E0A91C" stroke-width="3" stroke-linejoin="round"/>'
             '<path d="M32 50 Q36 46 40 50" fill="none" stroke="#3B2A20" stroke-width="3" stroke-linecap="round"/>'
             '<path d="M30 62 Q36 68 42 62" fill="none" stroke="#3B2A20" stroke-width="2.6" stroke-linecap="round"/>' + blush(28, 58, 4.5, 3, .55) +
             sparkle_star(82, 26, 6, '#2FB5EC') + sparkle_star(88, 44, 4, '#FF6FB5'))
PICS['N'] = ('nest', '<ellipse cx="50" cy="88" rx="38" ry="5" fill="#2b3a67" opacity=".14"/>'
             '<ellipse cx="38" cy="44" rx="12" ry="15" fill="#9ADCF5" stroke="#4FB6E0" stroke-width="2.6"/><ellipse cx="62" cy="44" rx="12" ry="15" fill="#9ADCF5" stroke="#4FB6E0" stroke-width="2.6"/><ellipse cx="50" cy="38" rx="12" ry="15" fill="#9ADCF5" stroke="#4FB6E0" stroke-width="2.6"/>'
             '<g fill="#4FB6E0" opacity=".6"><circle cx="34" cy="48" r="1.8"/><circle cx="66" cy="42" r="1.8"/><circle cx="52" cy="32" r="1.8"/></g>'
             '<path d="M10 56 Q50 44 90 56 Q92 82 50 86 Q8 82 10 56Z" fill="#C8996A" stroke="#A5703F" stroke-width="3" stroke-linejoin="round"/>'
             '<g fill="none" stroke="#8B5A3C" stroke-width="2.6" stroke-linecap="round" opacity=".7"><path d="M16 62 Q50 52 84 62"/><path d="M14 70 Q50 62 86 70"/><path d="M20 78 Q50 72 80 78"/><path d="M30 58 L40 80 M50 56 L56 82 M68 58 L62 80"/></g>')
PICS['O'] = ('octopus', '<ellipse cx="50" cy="92" rx="34" ry="4" fill="#2b3a67" opacity=".1"/>'
             '<g fill="none" stroke="#E5627A" stroke-width="9" stroke-linecap="round"><path d="M28 64 Q16 74 22 86"/><path d="M40 70 Q36 84 44 90"/><path d="M60 70 Q64 84 56 90"/><path d="M72 64 Q84 74 78 86"/></g>'
             '<g fill="none" stroke="#FF7A8A" stroke-width="5" stroke-linecap="round"><path d="M28 64 Q16 74 22 86"/><path d="M40 70 Q36 84 44 90"/><path d="M60 70 Q64 84 56 90"/><path d="M72 64 Q84 74 78 86"/></g>'
             '<path d="M20 48 C20 18 80 18 80 48 C80 70 70 76 50 76 C30 76 20 70 20 48Z" fill="#FF7A8A" stroke="#E5627A" stroke-width="3" stroke-linejoin="round"/>'
             '<g fill="#FFB3BE"><circle cx="34" cy="30" r="3.6"/><circle cx="50" cy="24" r="3"/><circle cx="66" cy="30" r="3.6"/></g>' + eye(38, 52, 5) + eye(62, 52, 5) +
             '<path d="M44 62 Q50 68 56 62" fill="none" stroke="#3B2A20" stroke-width="2.8" stroke-linecap="round"/>' + blush(28, 60, 5, 3.2, .7) + blush(72, 60, 5, 3.2, .7))
PICS['P'] = ('pig', ground +
             '<path d="M22 34 L16 10 L40 22Z" fill="#FF9CC8" stroke="#E5589F" stroke-width="3" stroke-linejoin="round"/><path d="M78 34 L84 10 L60 22Z" fill="#FF9CC8" stroke="#E5589F" stroke-width="3" stroke-linejoin="round"/>'
             '<ellipse cx="50" cy="54" rx="37" ry="33" fill="#FFB3DA" stroke="#E5589F" stroke-width="3"/>'
             '<ellipse cx="50" cy="64" rx="17" ry="13" fill="#FF8FC0" stroke="#E5589F" stroke-width="2.6"/><ellipse cx="44" cy="64" rx="3.2" ry="4.6" fill="#B03A78"/><ellipse cx="56" cy="64" rx="3.2" ry="4.6" fill="#B03A78"/>' +
             eye(34, 46, 4.6) + eye(66, 46, 4.6) + blush(24, 62, 5.5, 3.4, .7) + blush(76, 62, 5.5, 3.4, .7))
patch = ''
cols = ['#FF6FB5', '#FFF7E8', '#2FB5EC', '#FFC83D', '#FFF7E8', '#2FCB86', '#B69CF0', '#FF9F43', '#FFF7E8']
for i, c in enumerate(cols):
    gx, gy = 14 + (i % 3) * 24, 18 + (i // 3) * 24
    patch += f'<rect x="{gx}" y="{gy}" width="24" height="24" fill="{c}"/>'
    patch += f'<rect x="{gx + 3}" y="{gy + 3}" width="18" height="18" fill="none" stroke="#fff" stroke-width="1.8" stroke-dasharray="3 3" opacity=".9"/>'
PICS['Q'] = ('quilt', '<rect x="10" y="14" width="80" height="78" rx="12" fill="#2b3a67" opacity=".1"/><g>' +
             '<clipPath id="qc"><rect x="14" y="18" width="72" height="72" rx="9"/></clipPath><g clip-path="url(#qc)">' + patch + '</g>'
             '<rect x="14" y="18" width="72" height="72" rx="9" fill="none" stroke="#0F857D" stroke-width="4"/></g>'
             '<path d="M70 18 Q76 28 86 30 L86 18Z" fill="#E4F3F1" opacity="0"/>')
PICS['R'] = ('rainbow', '<g fill="none" stroke-linecap="round" stroke-width="9">'
             '<path d="M10 74 A40 40 0 0 1 90 74" stroke="#EF5B45"/><path d="M19 74 A31 31 0 0 1 81 74" stroke="#FFC83D"/>'
             '<path d="M28 74 A22 22 0 0 1 72 74" stroke="#2FCB86"/><path d="M37 74 A13 13 0 0 1 63 74" stroke="#2FB5EC"/></g>'
             '<g fill="#fff" stroke="#9CC7E6" stroke-width="2.6" stroke-linejoin="round"><path d="M2 80 Q2 70 12 71 Q16 62 26 68 Q36 66 36 78 Q36 88 26 88 H10 Q2 88 2 80Z"/>'
             '<path d="M64 80 Q64 70 74 71 Q78 62 88 68 Q98 66 98 78 Q98 88 88 88 H72 Q64 88 64 80Z"/></g>')
rays = ''.join(f'<path d="M{50 + 30 * math.cos(math.radians(a)):.1f} {50 + 30 * math.sin(math.radians(a)):.1f} L{50 + 41 * math.cos(math.radians(a)):.1f} {50 + 41 * math.sin(math.radians(a)):.1f}" />' for a in range(0, 360, 45))
PICS['S'] = ('sun', f'<g stroke="#F5A623" stroke-width="7" stroke-linecap="round" fill="none">{rays}</g>'
             '<circle cx="50" cy="50" r="25" fill="#FFC83D" stroke="#E0A91C" stroke-width="3"/>'
             '<path d="M38 46 Q41 42 44 46 M56 46 Q59 42 62 46" fill="none" stroke="#3B2A20" stroke-width="3" stroke-linecap="round"/>'
             '<path d="M42 56 Q50 66 58 56Z" fill="#7A3B20" stroke="#7A3B20" stroke-width="2" stroke-linejoin="round"/>' + blush(35, 55, 4.5, 3, .6) + blush(65, 55, 4.5, 3, .6))
shell = ''.join(f'<path d="{d}" fill="none" stroke="#168553" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>' for d in
                ['M50 28 L38 40 L38 56 L50 64 L62 56 L62 40Z', 'M38 40 L28 36 M62 40 L72 36 M38 56 L28 62 M62 56 L72 62 M50 28 V16 M50 64 V74'])
PICS['T'] = ('turtle', ground +
                          '<ellipse cx="30" cy="80" rx="10" ry="7" fill="#8FDDB0" stroke="#1FA56A" stroke-width="3"/><ellipse cx="68" cy="80" rx="10" ry="7" fill="#8FDDB0" stroke="#1FA56A" stroke-width="3"/>'
             '<path d="M12 64 Q4 66 8 72 Q16 70 18 66Z" fill="#8FDDB0" stroke="#1FA56A" stroke-width="2.5" stroke-linejoin="round"/>'
             '<path d="M14 70 Q14 28 50 26 Q86 28 86 70 Q86 80 76 80 H24 Q14 80 14 70Z" fill="#2FCB86" stroke="#1FA56A" stroke-width="3" stroke-linejoin="round"/>' + shell.replace('M50 28', 'M50 40') .replace('V16', 'V30')[:0] +
             '<g fill="none" stroke="#168553" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M40 46 L50 40 L60 46 L60 58 L50 64 L40 58Z"/><path d="M50 40 V30 M40 46 L30 42 M60 46 L70 42 M40 58 L30 64 M60 58 L70 64 M50 64 V74"/></g>'
             '<ellipse cx="32" cy="42" rx="6" ry="3.4" transform="rotate(-30 32 42)" fill="#fff" opacity=".4"/>'
             '<ellipse cx="86" cy="58" rx="12" ry="11" fill="#8FDDB0" stroke="#1FA56A" stroke-width="3"/>' + eye(89, 55, 2.8) +
             '<path d="M85 63 Q89 66 93 63" fill="none" stroke="#3B2A20" stroke-width="2" stroke-linecap="round"/>' + blush(81, 62, 2.6, 1.8, .7))
PICS['U'] = ('umbrella', '<path d="M50 40 V78 Q50 88 40 88 Q32 88 32 80" fill="none" stroke="#6E432A" stroke-width="4.5" stroke-linecap="round"/>'
             '<path d="M8 50 Q10 14 50 12 Q90 14 92 50 Q82 42 71 50 Q61 42 50 50 Q39 42 29 50 Q18 42 8 50Z" fill="#FF6FB5" stroke="#D94E94" stroke-width="3" stroke-linejoin="round"/>'
             '<path d="M50 12 Q40 30 39 47 M50 12 Q60 30 61 47 M50 12 V47" fill="none" stroke="#D94E94" stroke-width="2.4" stroke-linecap="round" opacity=".8"/>'
             '<path d="M30 24 Q38 18 44 18" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".6"/><circle cx="50" cy="10" r="3.4" fill="#FFC83D" stroke="#D99E12" stroke-width="2"/>')
PICS['V'] = ('vase', ground +
             '<g fill="none" stroke="#2FCB86" stroke-width="3.4" stroke-linecap="round"><path d="M50 56 Q46 40 36 26"/><path d="M50 56 Q52 38 54 18"/><path d="M50 56 Q58 42 70 30"/></g>'
             '<g><circle cx="36" cy="22" r="8" fill="#FF6FB5" stroke="#D94E94" stroke-width="2.4"/><circle cx="36" cy="22" r="3.4" fill="#FFC83D"/>'
             '<circle cx="54" cy="14" r="8" fill="#FFC83D" stroke="#E0A91C" stroke-width="2.4"/><circle cx="54" cy="14" r="3.4" fill="#EF5B45"/>'
             '<circle cx="71" cy="27" r="8" fill="#B69CF0" stroke="#8E72D0" stroke-width="2.4"/><circle cx="71" cy="27" r="3.4" fill="#FFC83D"/></g>'
             '<path d="M38 52 H62 Q60 60 70 72 Q72 88 50 88 Q28 88 30 72 Q40 60 38 52Z" fill="#14A39A" stroke="#0F857D" stroke-width="3" stroke-linejoin="round"/>'
             '<path d="M36 50 H64" stroke="#0F857D" stroke-width="5" stroke-linecap="round"/><ellipse cx="40" cy="74" rx="3.4" ry="8" fill="#fff" opacity=".35"/>'
             '<path d="M33 70 Q50 78 67 70" fill="none" stroke="#FFC83D" stroke-width="3" stroke-linecap="round" stroke-dasharray="1 7"/>')
PICS['W'] = ('worm', '<ellipse cx="50" cy="88" rx="38" ry="7" fill="#8B5A3C"/><ellipse cx="50" cy="86" rx="34" ry="5" fill="#A5703F"/>'
             + ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" stroke="#6BAF2E" stroke-width="2.6"/>' for x, y, r, c in
                       [(22, 80, 8, '#A6E36A'), (32, 70, 9, '#8FD650'), (44, 66, 9, '#A6E36A'), (56, 62, 9.5, '#8FD650'), (66, 52, 10, '#A6E36A'), (68, 38, 11, '#8FD650')]) +
             '<circle cx="62" cy="22" r="14" fill="#B8EE7F" stroke="#6BAF2E" stroke-width="2.8"/>' + eye(57, 20, 3.6) + eye(69, 20, 3.6) +
             '<path d="M56 28 Q62 34 68 28" fill="none" stroke="#3B2A20" stroke-width="2.6" stroke-linecap="round"/>' + blush(52, 27, 3.8, 2.6, .6) + blush(72, 27, 3.8, 2.6, .6) +
             '<path d="M56 9 Q54 2 49 4 M68 9 Q72 2 77 4" fill="none" stroke="#6BAF2E" stroke-width="2.6" stroke-linecap="round"/>')
PICS['X'] = ('box', ground +
             '<path d="M14 36 L8 16 L36 26Z" fill="#E7C08C" stroke="#A5703F" stroke-width="3" stroke-linejoin="round"/><path d="M86 36 L92 16 L64 26Z" fill="#E7C08C" stroke="#A5703F" stroke-width="3" stroke-linejoin="round"/>'
             '<path d="M14 34 L50 44 L86 34 L86 78 L50 90 L14 78Z" fill="#D9AA77" stroke="#A5703F" stroke-width="3" stroke-linejoin="round"/>'
             '<path d="M14 34 L50 44 L86 34 L50 26Z" fill="#B98254" stroke="#A5703F" stroke-width="3" stroke-linejoin="round"/>'
             '<path d="M50 44 V90" stroke="#A5703F" stroke-width="3"/><rect x="42" y="44" width="16" height="30" fill="#F7E6C2" opacity=".9"/>'
             '<path d="M20 50 V70 M80 50 V70" stroke="#A5703F" stroke-width="2.4" stroke-linecap="round" opacity=".5"/>')
PICS['Y'] = ('yarn', ground +
             '<path d="M64 80 Q80 84 86 74 Q92 66 84 62" fill="none" stroke="#FF6FB5" stroke-width="4" stroke-linecap="round"/>'
             '<circle cx="44" cy="50" r="34" fill="#FF9F43" stroke="#D9792A" stroke-width="3"/>'
             '<g fill="none" stroke="#FFC37A" stroke-width="3.4" stroke-linecap="round"><path d="M16 42 Q44 60 72 30"/><path d="M14 54 Q44 72 74 44"/><path d="M20 66 Q44 80 70 62"/><path d="M26 28 Q40 40 58 20"/></g>'
             '<ellipse cx="30" cy="34" rx="6" ry="3.4" transform="rotate(-35 30 34)" fill="#fff" opacity=".45"/>')
PICS['Z'] = ('zebra', ground +
             '<path d="M26 30 L22 8 L42 22Z" fill="#fff" stroke="#3B2A20" stroke-width="3" stroke-linejoin="round"/><path d="M74 30 L78 8 L58 22Z" fill="#fff" stroke="#3B2A20" stroke-width="3" stroke-linejoin="round"/>'
             '<path d="M26 22 L25 14 L33 20Z" fill="#FFB3DA" stroke="#FFB3DA" stroke-width="2" stroke-linejoin="round"/><path d="M74 22 L75 14 L67 20Z" fill="#FFB3DA" stroke="#FFB3DA" stroke-width="2" stroke-linejoin="round"/>'
             '<path d="M28 24 Q50 10 72 24 Q80 52 70 76 Q60 90 50 90 Q40 90 30 76 Q20 52 28 24Z" fill="#fff" stroke="#3B2A20" stroke-width="3" stroke-linejoin="round"/>'
             '<path d="M50 14 V30 M38 18 Q42 28 40 36 M62 18 Q58 28 60 36 M25 40 Q34 44 36 52 M75 40 Q66 44 64 52" fill="none" stroke="#3B2A20" stroke-width="4.4" stroke-linecap="round"/>'
             '<ellipse cx="50" cy="72" rx="18" ry="15" fill="#6B5B52" stroke="#3B2A20" stroke-width="2.6"/><ellipse cx="43" cy="72" rx="2.6" ry="3.6" fill="#1f1510"/><ellipse cx="57" cy="72" rx="2.6" ry="3.6" fill="#1f1510"/>' +
             eye(38, 50, 4) + eye(62, 50, 4))

WORDS = {k: v[0] for k, v in PICS.items()}
assert len(PICS) == 26 and ''.join(sorted(PICS)) == 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


# ------------------------------------------------------------------ parcels (letter carriers)
CARRIER = {  # body, edge, handle
    'sky': ('#2FB5EC', '#1E8FC0', '#16709A'),
    'pink': ('#FF6FB5', '#D94E94', '#B03A78'),
    'sun': ('#FFC83D', '#E0A91C', '#B88408'),
    'leaf': ('#2FCB86', '#1FA56A', '#168553'),
    'orange': ('#FF9F43', '#D9792A', '#B35E18'),
    'lilac': ('#B69CF0', '#8E72D0', '#6E55B0'),
    'teal': ('#14A39A', '#0F857D', '#0A625C'),
}
CKEYS = list(CARRIER)
DIM = ('#F1EADC', '#E4DAC5', '#D6CBB3')
GLYPH_PX = 82  # Andika font size giving a cap height of about 58 scene px (checked in the browser)
SIZE = 104
_clip = [0]


def ring(cx, cy, cls=''):
    return (f'<ellipse class="{cls}" cx="{cx}" cy="{cy + 50}" rx="58" ry="15" fill="#FFE7A3" fill-opacity=".6" stroke="#F5A623" stroke-width="6"/>')


def parcel(letter, cx, cy, ck='sky', state='idle', tilt=0, sx=-10, delay=0.0):
    """One carrier. The body (and label) may tilt by a few degrees; the letter is always drawn upright on top.
    state: idle, shimmer, dim, found, lit (kept lit when the board narrows)."""
    dim = state == 'dim'
    body, edge, handle = DIM if dim else CARRIER[ck]
    lab = '#F8F2E6' if dim else '#FFFDF6'
    ink = '#BDB19D' if dim else INK
    _clip[0] += 1
    cid = f'pc{_clip[0]}'
    y0 = cy - 40
    shape = (f'<rect x="{cx - 18}" y="{cy - 53}" width="36" height="18" rx="8" fill="{handle}"/>'
             f'<rect x="{cx - 52}" y="{y0 + 7}" width="104" height="88" rx="24" fill="{edge}"/>'
             f'<rect x="{cx - 52}" y="{y0}" width="104" height="88" rx="24" fill="{body}"/>'
             f'<rect x="{cx - 38}" y="{y0 + 4}" width="76" height="7" rx="3.5" fill="#fff" opacity="{.12 if dim else .35}"/>'
             f'<rect x="{cx - 39}" y="{cy - 33}" width="78" height="70" rx="16" fill="{lab}"/>'
             f'<g fill="{handle}" opacity="{.5 if dim else .9}"><circle cx="{cx - 46}" cy="{cy - 30}" r="3.4"/><circle cx="{cx + 46}" cy="{cy - 30}" r="3.4"/>'
             f'<circle cx="{cx - 46}" cy="{cy + 32}" r="3.4"/><circle cx="{cx + 46}" cy="{cy + 32}" r="3.4"/></g>')
    sheen = ''
    if state in ('shimmer',):
        sheen = (f'<clipPath id="{cid}"><rect x="{cx - 52}" y="{y0}" width="104" height="88" rx="24"/></clipPath>'
                 f'<g clip-path="url(#{cid})"><g transform="skewX(-18)"><rect class="sheen" style="--sx:{sx}px;animation-delay:{delay}s" '
                 f'x="{cx - 72 + cy * .32:.0f}" y="{y0 - 6}" width="26" height="110" fill="#fff" opacity=".7"/></g></g>')
    rt = f' transform="rotate({tilt} {cx} {cy})"' if tilt else ''
    glyph = (f'<text x="{cx}" y="{cy + 3 + 29}" text-anchor="middle" font-family="Andika,sans-serif" font-size="{GLYPH_PX}" fill="{ink}">{letter}</text>')
    art = f'<g{rt}>{shape}{sheen}</g>{glyph}'
    sh = f'<ellipse cx="{cx}" cy="{cy + 55}" rx="46" ry="7" fill="#2b3a67" opacity="{.10 if dim else .2}"/>'
    if state == 'found':
        return (f'<circle class="glow" cx="{cx}" cy="{cy - 6}" r="80" fill="#FFE27A" opacity=".6"/>' + ring(cx, cy) +
                f'<ellipse cx="{cx}" cy="{cy + 56}" rx="34" ry="6" fill="#2b3a67" opacity=".22"/><g transform="translate(0 -18)"><g class="hopf">{art}</g></g>'
                f'<g class="twinkle">{sparkle_star(cx + 62, cy - 56, 12)}{sparkle_star(cx - 66, cy - 40, 9, "#fff")}{sparkle_star(cx + 70, cy + 8, 7, "#FF6FB5")}{sparkle_star(cx - 60, cy + 20, 6, "#2FB5EC")}</g>')
    if state == 'lit':
        return f'<circle class="glow" cx="{cx}" cy="{cy}" r="72" fill="#FFE27A" opacity=".35"/>{sh}{art}'
    return sh + art


# ------------------------------------------------------------------ train
CAR_COLS = ['sky', 'pink', 'sun', 'leaf', 'orange', 'lilac', 'teal']


def car(x, y, ck, letter=None, w=92, label_font=34, empty_dash=True, word=None):
    """a wagon, 92 x 86 scene px at x,y (top-left). letter None = empty car waiting for its letter."""
    body, edge, handle = CARRIER[ck]
    s = f'<rect x="{x}" y="{y + 22}" width="{w}" height="50" rx="12" fill="{edge}"/><rect x="{x}" y="{y + 16}" width="{w}" height="50" rx="12" fill="{body}"/>'
    if letter is None:
        s += (f'<rect x="{x + 8}" y="{y + 24}" width="{w - 16}" height="34" rx="9" fill="#FFFDF6" opacity=".55"/>'
              f'<rect x="{x + 8}" y="{y + 24}" width="{w - 16}" height="34" rx="9" fill="none" stroke="#fff" stroke-width="2.4" stroke-dasharray="5 5"/>')
    else:
        pw = 34
        s += (f'<rect x="{x + 6}" y="{y + 20}" width="{w - 12}" height="42" rx="10" fill="#FFFDF6"/>'
              f'<text x="{x + 24}" y="{y + 52}" text-anchor="middle" font-family="Andika,sans-serif" font-size="{label_font}" fill="{INK}">{letter}</text>'
              f'<use href="#p-{letter}" x="{x + w - 6 - pw - 3}" y="{y + 22}" width="{pw + 2}" height="{pw + 2}"/>')
    s += (f'<rect x="{x + 6}" y="{y + 62}" width="{w - 12}" height="6" rx="3" fill="{handle}" opacity=".55"/>'
          f'<circle cx="{x + 24}" cy="{y + 72}" r="9" fill="#5C4B42"/><circle cx="{x + 24}" cy="{y + 72}" r="3.4" fill="#C8B9A8"/>'
          f'<circle cx="{x + w - 24}" cy="{y + 72}" r="9" fill="#5C4B42"/><circle cx="{x + w - 24}" cy="{y + 72}" r="3.4" fill="#C8B9A8"/>'
          f'<rect x="{x + w}" y="{y + 52}" width="10" height="6" rx="3" fill="#5C4B42"/>')
    return s


def engine(x, y):
    """small friendly steam engine facing left, 118 x 96 scene px"""
    return (f'<g class="puff"><ellipse cx="{x + 34}" cy="{y - 14}" rx="12" ry="9" fill="#fff" opacity=".9"/><ellipse cx="{x + 46}" cy="{y - 28}" rx="9" ry="7" fill="#fff" opacity=".7"/></g>'
            f'<rect x="{x + 22}" y="{y + 6}" width="22" height="26" rx="6" fill="#FFC83D" stroke="#D99E12" stroke-width="3"/><rect x="{x + 16}" y="{y}" width="34" height="12" rx="6" fill="#FFC83D" stroke="#D99E12" stroke-width="3"/>'
            f'<rect x="{x}" y="{y + 38}" width="118" height="12" rx="6" fill="#0A625C"/>'
            f'<rect x="{x}" y="{y + 28}" width="86" height="44" rx="22" fill="#0A625C"/><rect x="{x}" y="{y + 22}" width="86" height="44" rx="22" fill="#0F857D"/>'
            f'<rect x="{x + 70}" y="{y + 8}" width="48" height="58" rx="10" fill="#FFC83D" stroke="#D99E12" stroke-width="3"/>'
            f'<rect x="{x + 80}" y="{y + 18}" width="28" height="24" rx="7" fill="#BFE9FA" stroke="#2FB5EC" stroke-width="2.6"/>'
            f'<rect x="{x + 64}" y="{y + 2}" width="60" height="10" rx="5" fill="#0A625C"/>'
            f'<path d="M{x + 12} {y + 64} L{x - 4} {y + 76} L{x + 24} {y + 76}Z" fill="#FF6FB5" stroke="#D94E94" stroke-width="3" stroke-linejoin="round"/>'
            f'<rect x="{x - 2}" y="{y + 36}" width="9" height="14" rx="4" fill="#FFF7E8" stroke="#E6BE8D" stroke-width="2"/>'
            f'<circle cx="{x + 30}" cy="{y + 76}" r="14" fill="#5C4B42"/><circle cx="{x + 30}" cy="{y + 76}" r="5" fill="#C8B9A8"/>'
            f'<circle cx="{x + 90}" cy="{y + 76}" r="14" fill="#5C4B42"/><circle cx="{x + 90}" cy="{y + 76}" r="5" fill="#C8B9A8"/>'
            f'<rect x="{x + 38}" y="{y + 75}" width="46" height="5" rx="2.5" fill="#5C4B42"/>')


# ------------------------------------------------------------------ station scenery (no letters, numerals or letter-shaped props)
def defs_scene():
    return '''<defs>
<linearGradient id="sky" gradientUnits="userSpaceOnUse" x1="0" y1="-20" x2="0" y2="260"><stop offset="0" stop-color="#BFE9FA"/><stop offset="1" stop-color="#FFF7E8"/></linearGradient>
<linearGradient id="plat" gradientUnits="userSpaceOnUse" x1="0" y1="262" x2="0" y2="620"><stop offset="0" stop-color="#F7E6C2"/><stop offset="1" stop-color="#EBCF9B"/></linearGradient>
<linearGradient id="bed" gradientUnits="userSpaceOnUse" x1="0" y1="232" x2="0" y2="266"><stop offset="0" stop-color="#C9B79C"/><stop offset="1" stop-color="#B5A184"/></linearGradient>
<filter id="soft" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="6" stdDeviation="7" flood-color="#2b3a67" flood-opacity=".18"/></filter>
</defs>'''


def bush(cx, cy, s=1.0, col='#7FD9A8'):
    return (f'<g fill="{col}"><ellipse cx="{cx}" cy="{cy}" rx="{30 * s}" ry="{20 * s}"/><ellipse cx="{cx - 24 * s}" cy="{cy + 6 * s}" rx="{20 * s}" ry="{15 * s}"/>'
            f'<ellipse cx="{cx + 26 * s}" cy="{cy + 6 * s}" rx="{22 * s}" ry="{15 * s}"/></g>')


def station_house(x=24, y=92):
    """flat-roofed station house, base at y+142. A plain blank signboard, no text, no clock."""
    return f'''<g filter="url(#soft)"><rect x="{x}" y="{y + 40}" width="270" height="102" rx="12" fill="#FFF1D6" stroke="#E6BE8D" stroke-width="3"/>
<rect x="{x - 12}" y="{y + 24}" width="294" height="22" rx="11" fill="#0F857D"/><rect x="{x - 12}" y="{y + 24}" width="294" height="9" rx="4.5" fill="#14A39A"/></g>
<rect x="{x + 70}" y="{y + 2}" width="130" height="30" rx="12" fill="#0A625C"/><rect x="{x + 76}" y="{y + 7}" width="118" height="20" rx="9" fill="#FFC83D" opacity=".9"/>
<rect x="{x + 100}" y="{y + 58}" width="70" height="84" rx="14" fill="#0A625C"/><rect x="{x + 106}" y="{y + 64}" width="26" height="78" rx="8" fill="#14A39A"/><rect x="{x + 138}" y="{y + 64}" width="26" height="78" rx="8" fill="#14A39A"/>
<circle cx="{x + 128}" cy="{y + 104}" r="2.6" fill="#FFC83D"/><circle cx="{x + 142}" cy="{y + 104}" r="2.6" fill="#FFC83D"/>
<rect x="{x + 22}" y="{y + 62}" width="54" height="46" rx="12" fill="#BFE9FA" stroke="#2FB5EC" stroke-width="3"/><path d="M{x + 49} {y + 62} V{y + 108}" stroke="#fff" stroke-width="3"/>
<rect x="{x + 194}" y="{y + 62}" width="54" height="46" rx="12" fill="#BFE9FA" stroke="#2FB5EC" stroke-width="3"/><path d="M{x + 221} {y + 62} V{y + 108}" stroke="#fff" stroke-width="3"/>
<rect x="{x + 16}" y="{y + 108}" width="66" height="12" rx="6" fill="#C8996A"/><rect x="{x + 188}" y="{y + 108}" width="66" height="12" rx="6" fill="#C8996A"/>
<g><circle cx="{x + 30}" cy="{y + 106}" r="6" fill="#FF6FB5"/><circle cx="{x + 46}" cy="{y + 104}" r="6" fill="#FFC83D"/><circle cx="{x + 62}" cy="{y + 106}" r="6" fill="#FF6FB5"/>
<circle cx="{x + 202}" cy="{y + 106}" r="6" fill="#FFC83D"/><circle cx="{x + 218}" cy="{y + 104}" r="6" fill="#FF6FB5"/><circle cx="{x + 234}" cy="{y + 106}" r="6" fill="#FFC83D"/></g>
<rect x="{x + 80}" y="{y + 70}" width="14" height="16" rx="4" fill="#FFE27A" stroke="#D99E12" stroke-width="2.4"/>'''


def backdrop(show_house=True):
    s = f'''<rect x="-60" y="-40" width="1080" height="320" fill="url(#sky)"/>
<circle cx="730" cy="70" r="26" fill="#FFC83D" opacity=".9"/><circle cx="730" cy="70" r="38" fill="#FFC83D" opacity=".18"/>
<g fill="#fff" opacity=".9"><ellipse cx="420" cy="62" rx="44" ry="13"/><ellipse cx="450" cy="52" rx="26" ry="15"/><ellipse cx="860" cy="98" rx="42" ry="11"/><ellipse cx="888" cy="88" rx="22" ry="12"/></g>
<path d="M-60 196 C60 150 200 150 320 186 C460 222 600 160 740 172 C860 182 940 150 1020 176 V300 H-60Z" fill="#BDEFD3"/>
<path d="M-60 226 C100 190 300 200 480 212 C700 228 840 196 1020 208 V300 H-60Z" fill="#9CEBC1"/>
{bush(930, 204, 1.0, '#7FD9A8')}{bush(330, 206, .8, '#7FD9A8')}
<rect x="-60" y="232" width="1080" height="34" fill="url(#bed)"/>
<rect x="-60" y="238" width="1080" height="7" fill="#8C98A8"/><rect x="-60" y="238" width="1080" height="3" fill="#B7C1CE"/>
''' + ''.join(f'<rect x="{x}" y="246" width="16" height="12" rx="3" fill="#8B5A3C" opacity=".7"/>' for x in range(-40, 1000, 30)) + f'''
<path d="M-60 262 H1020 V700 H-60Z" fill="url(#plat)"/>
<rect x="-60" y="262" width="1080" height="14" fill="#FFC83D"/><rect x="-60" y="262" width="1080" height="5" fill="#FFE27A"/>
<path d="M-60 276 H1020" stroke="#E6BE8D" stroke-width="3" opacity=".7"/>
<g fill="#E6BE8D" opacity=".45">''' + ''.join(f'<path d="M{x} 290 V600" stroke="#E6BE8D" stroke-width="2.4" opacity=".4"/>' for x in range(-20, 1000, 160)) + '</g>'
    if show_house:
        s = s + station_house()
    return s


def hud(filled, total=10, muted=False):
    x0 = 480 - (total - 1) * 11
    dots = ''.join(
        f'<circle cx="{x0 + i * 22}" cy="42" r="6.5" fill="{"#2FCB86" if i < filled else "#fff"}" stroke="#0F857D" stroke-width="2.2" opacity="{1 if i < filled else .85}"/>'
        for i in range(total))
    slash = '<path d="M884 30 L916 62" stroke="#0F857D" stroke-width="5" stroke-linecap="round"/><path d="M884 30 L916 62" stroke="#fff" stroke-width="1.5" stroke-linecap="round" opacity="0"/>' if muted else ''
    waves = '' if muted else '<path d="M912 38 q7 9 0 18" stroke="#0F857D" stroke-width="3.6" fill="none" stroke-linecap="round"/>'
    return f'''<g class="fred">
<g><rect x="24" y="22" width="124" height="56" rx="28" fill="#0A625C"/><rect x="24" y="16" width="124" height="56" rx="28" fill="#0F857D"/><text x="86" y="52" text-anchor="middle" fill="#fff" font-size="24" font-weight="600">&#8249; Back</text></g>
{dots}
<g><circle cx="900" cy="46" r="30" fill="#fff" filter="url(#soft)"/><path d="M886 40 h8 l11 -8 v30 l-11 -8 h-8z" fill="#0F857D"/>{waves}{slash}</g></g>'''


def hazel_helper(x=226, y=444, w=74, tilt=False):
    h = w * 262 / 240
    crate = (f'<g filter="url(#soft)"><rect x="{x - 8}" y="{y + h - 10}" width="{w + 16}" height="46" rx="12" fill="#C8996A"/>'
             f'<rect x="{x - 8}" y="{y + h - 10}" width="{w + 16}" height="12" rx="6" fill="#E6C9A0"/>'
             f'<path d="M{x + 4} {y + h + 12} H{x + w - 4}" stroke="#A5703F" stroke-width="3" stroke-linecap="round" opacity=".5"/></g>')
    rt = f' transform="rotate(-9 {x + w / 2} {y + h})"' if tilt else ''
    return crate + f'<g{rt}><use href="#hazel-sym" x="{x}" y="{y}" width="{w}" height="{h:.0f}"/></g>'


def bubble(x, y, w, h, tail_x, inner):
    return (f'<g filter="url(#soft)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="32" fill="#fff"/>'
            f'<path d="M{tail_x - 16} {y + h - 2} l10 30 l22 -30Z" fill="#fff"/></g>{inner}')


def speaker_bubble(pulse=True):
    """The request is spoken, never written: a big speaker, no letter. 104 scene px tap target."""
    x, y, w, h = 38, 268, 172, 132
    cx, cy = x + w / 2, y + h / 2
    inner = (f'<circle class="{"spk" if pulse else ""}" cx="{cx}" cy="{cy}" r="52" fill="none" stroke="#0F857D" stroke-width="4" opacity=".35"/>'
             f'<circle cx="{cx}" cy="{cy}" r="50" fill="#E4F3F1" stroke="#0F857D" stroke-width="4"/>'
             f'<path d="M{cx - 22} {cy - 9} h13 l18 -15 v48 l-18 -15 h-13z" fill="#0F857D" stroke="#0F857D" stroke-width="4" stroke-linejoin="round"/>'
             f'<path d="M{cx + 16} {cy - 14} q12 14 0 28" fill="none" stroke="#0F857D" stroke-width="5" stroke-linecap="round"/>'
             f'<path d="M{cx + 25} {cy - 24} q20 24 0 48" fill="none" stroke="#0F857D" stroke-width="5" stroke-linecap="round" opacity=".75"/>')
    return bubble(x, y, w, h, 120, inner)


def card_bubble(letter='M'):
    """muted hint: the letter card, shown only when asked (costed hint) or when the player is muted"""
    x, y, w, h = 30, 252, 270, 148
    inner = (f'<g filter="url(#soft)"><rect x="{x + 18}" y="{y + 18}" width="104" height="112" rx="18" fill="#fff" stroke="#2FB5EC" stroke-width="5"/></g>'
             f'<text x="{x + 70}" y="{y + 100}" text-anchor="middle" font-family="Andika,sans-serif" font-size="92" fill="{INK}">{letter}</text>'
             f'<g class="fred" font-weight="600" fill="#0F857D" font-size="26"><text x="{x + 138}" y="{y + 66}">It looks</text><text x="{x + 138}" y="{y + 98}">like this!</text></g>'
             f'<g transform="translate({x + 244} {y + 22})"><circle r="13" fill="#E4F3F1"/><path d="M-6 -3 h4 l6 -5 v16 l-6 -5 h-4z" fill="#0F857D"/><path d="M-9 -9 L9 9" stroke="#0F857D" stroke-width="2.6" stroke-linecap="round"/></g>')
    return bubble(x, y, w, h, 120, inner)


def found_bubble(letter='M', word='moon'):
    x, y, w, h = 30, 252, 270, 148
    inner = (f'<use href="#p-{letter}" x="{x + 18}" y="{y + 26}" width="92" height="92"/>'
             f'<g font-family="Andika,sans-serif" fill="{INK}"><text x="{x + 122}" y="{y + 70}" font-size="34">{letter} is for</text>'
             f'<text x="{x + 122}" y="{y + 112}" font-size="40" fill="#0F857D">{word}</text></g>')
    return bubble(x, y, w, h, 120, inner)


def fox_use(pose, x=22, y=394, w=170, cls='bob', delay=0):
    h = w * 200 / 180
    return f'<g class="{cls}" style="animation-delay:{delay}s"><use href="#fox-{pose}" x="{x}" y="{y}" width="{w}" height="{h:.0f}"/></g>'


def train(cars):
    """engine plus five wagons on the top track. cars = list of letters filled so far (rest empty)."""
    out = engine(330, 140)
    for i in range(5):
        ck = CAR_COLS[i % len(CAR_COLS)]
        out += car(444 + i * 102, 150, ck, cars[i] if i < len(cars) else None)
    return out


def scene(label, parcels=(), fox_pose='n', bub=None, filled=0, cars=(), muted=False, tilt_hazel=False, cls='scene'):
    p = ''
    for it in parcels:
        p += parcel(it[0], it[1], it[2], **it[3])
    b = {'ask': speaker_bubble, 'card': card_bubble, 'found': found_bubble, None: lambda: ''}[bub]()
    return (f'<svg viewBox="0 0 960 600" class="{cls}" role="img" aria-label="{label}">{defs_scene()}'
            f'{backdrop()}{train(cars)}{p}{b}{fox_use(fox_pose)}{hazel_helper(tilt=tilt_hazel)}{hud(filled, 10, muted)}</svg>')


# parcel spec: (letter, cx, cy, kwargs)
def P(letter, cx, cy, ck, state='idle', tilt=0, **kw):
    return (letter, cx, cy, dict(ck=ck, state=state, tilt=tilt, **kw))


L1 = [('S', 470, 420, 'sky'), ('A', 640, 408, 'pink'), ('M', 810, 424, 'sun')]
# level 4: M W E F O Q + H S (three look-alike pairs on one board), 3 rows (3, 3, 2). Reading order matters, no alphabet runs.
L4 = [('M', 430, 338, 'sky', -3), ('H', 604, 330, 'leaf', 4), ('E', 776, 342, 'orange', -5),
      ('O', 518, 436, 'lilac', 5), ('W', 690, 428, 'pink', -4), ('F', 862, 438, 'teal', 3),
      ('S', 440, 530, 'sun', -3), ('Q', 640, 532, 'sky', 4)]


def check_layout(items, name, bounds=(330, 1000)):
    """no overlap, spacing >= 112, in bounds (scene px, centre to centre)"""
    mind = 1e9
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            d = math.hypot(items[i][1] - items[j][1], items[i][2] - items[j][2])
            mind = min(mind, d)
    for it in items:
        assert 330 <= it[1] - 52 and it[1] + 52 <= 960 and it[2] - 54 >= 266 and it[2] + 56 <= 600, (name, it)
    assert mind >= 112, (name, mind)
    return mind


MIN1 = check_layout(L1, 'L1')
MIN4 = check_layout(L4, 'L4')
print('min spacing L1', round(MIN1, 1), 'L4', round(MIN4, 1))


def spec(items, state_of=lambda l: 'idle', **kw):
    out = []
    for i, it in enumerate(items):
        l, cx, cy, ck = it[:4]
        tilt = it[4] if len(it) > 4 else 0
        st = state_of(l)
        extra = dict(kw)
        if st == 'shimmer':
            extra.update(sx=20 + (i * 37) % 90, delay=round(i * .22, 2))
        out.append(P(l, cx, cy, ck, st, tilt, **extra))
    return out


# ------------------------------------------------------------------ page pieces
def symbols():
    s = '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
    for p in 'nht':
        s += f'<symbol id="fox-{p}" viewBox="0 0 180 200" overflow="visible">{fox(p)}</symbol>'
    for k, (w, art) in PICS.items():
        s += f'<symbol id="p-{k}" viewBox="0 0 100 100" overflow="visible">{art}</symbol>'
    s += f'<symbol id="hazel-sym" viewBox="0 0 240 262">{owl_inner}</symbol>'
    s += '</defs></svg>'
    return s


def card_svg(w, h, inner, label, scale=1.0, cls='stage'):
    return (f'<svg viewBox="0 0 {w} {h}" width="{w * scale:.0f}" height="{h * scale:.0f}" class="{cls}" role="img" aria-label="{label}" overflow="visible">'
            f'<defs><filter id="softc" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="6" stdDeviation="7" flood-color="#2b3a67" flood-opacity=".18"/></filter></defs>{inner}</svg>')


def cast_cards():
    items = [('n', 'Fox station master, neutral', 'asks for the letter, waits with a gentle bob, flag at his side'),
             ('h', 'Fox, happy', 'cheers on a found letter: closed smiling eyes, both arms up, tail up'),
             ('t', 'Fox, thinking', 'plays after a miss and on a hint: head tilted, one brow up, paw on cheek')]
    out = ''
    for k, name, d in items:
        out += (f'<figure class="cast"><svg viewBox="-6 0 192 204" width="{192 * 1.3:.0f}" height="{204 * 1.3:.0f}" role="img" aria-label="{name}">'
                f'<use href="#fox-{k}" width="180" height="200"/></svg><figcaption><b>{name}</b><br>{d}</figcaption></figure>')
    out += ('<figure class="cast"><svg viewBox="0 0 240 262" width="190" height="207" role="img" aria-label="Hazel the owl">'
            '<use href="#hazel-sym" width="240" height="262"/></svg><figcaption><b>Hazel (unchanged)</b><br>host and hint helper. Sits on a crate by the platform. Tap her for a hint.</figcaption></figure>')
    return out


def fox_small():
    out = '<div class="row small-row">'
    for w, lab in ((64, '64 px (the smallest it can be)'), (106, '106 px (as drawn on a 667 x 375 phone)'), (170, '170 px (scene size)')):
        h = w * 200 / 180
        out += (f'<figure class="cast"><svg viewBox="-6 0 192 204" width="{w * 192 / 180:.0f}" height="{h * 204 / 200:.0f}" role="img" aria-label="Fox at {w} pixels">'
                f'<use href="#fox-n" width="180" height="200"/></svg><figcaption>{lab}</figcaption></figure>')
        out += (f'<figure class="cast"><svg viewBox="-6 0 192 204" width="{w * 192 / 180:.0f}" height="{h * 204 / 200:.0f}" role="img" aria-label="Fox happy at {w} pixels">'
                f'<use href="#fox-h" width="180" height="200"/></svg><figcaption>happy, same size</figcaption></figure>') if w == 64 else ''
    return out + '</div>'


def carrier_cards():
    out = ''
    for i, ck in enumerate(CKEYS):
        letter = 'ABCDEMS'[i]
        inner = f'<rect width="220" height="190" fill="#F7E6C2"/>' + parcel(letter, 110, 94, ck, 'idle', 0)
        out += f'<figure class="cast statecard">{card_svg(220, 190, inner, ck + " parcel", 1.0, "stage sc")}<figcaption><b>{ck}</b></figcaption></figure>'
    return out


def carrier_anatomy():
    inner = '<rect width="560" height="230" fill="#F7E6C2"/>'
    inner += parcel('M', 150, 118, 'sky', 'idle', 0)
    inner += '<circle cx="150" cy="118" r="52" fill="none" stroke="#FF6FB5" stroke-width="3" stroke-dasharray="7 6"/>'
    inner += parcel('M', 330, 118, 'sky', 'idle', 6)
    inner += ('<g font-family="Fredoka,system-ui,sans-serif" font-size="17" font-weight="600" fill="#3B2A20">'
              '<text x="150" y="206" text-anchor="middle">104 px hit circle</text><text x="330" y="206" text-anchor="middle">tilted 6 deg (the most a pile does)</text></g>')
    inner += ('<g font-family="Fredoka,system-ui,sans-serif" font-size="15" font-weight="600" fill="#0F857D">'
              '<text x="420" y="60">flat label face, letter on top</text><text x="420" y="82">upright. Only the box tilts.</text>'
              '<text x="420" y="116" fill="#3B2A20" font-weight="400">handle and rivets give the</text><text x="420" y="136" fill="#3B2A20" font-weight="400">"suitcase" read without any</text><text x="420" y="156" fill="#3B2A20" font-weight="400">shape near the letter</text></g>')
    return card_svg(560, 230, inner, 'Carrier anatomy', 1.0, 'stage sc wide2')


def state_tiles():
    W, H = 220, 200
    cx, cy = 110, 112
    plat = f'<rect width="{W}" height="{H}" fill="#F7E6C2"/>'
    tiles = []
    tiles.append(('1. Idle', 'Plain parcel, letter upright. Nothing moves. 104 scene px, 65 px on a phone.', plat + parcel('M', cx, cy, 'sky')))
    tiles.append(('2. Idle shimmer', 'After 7 s still: a soft sheen sweeps across EVERY letter, left to right, once. It points at nothing, so it never gives the answer away.',
                  plat + parcel('M', cx, cy, 'sky', 'shimmer', sx=18)))
    tiles.append(('3. Wrong tap', 'That parcel dims (still visible, not tappable) and says its own name softly. No red, no X, no shake.', plat + parcel('W', cx, cy, 'pink', 'dim')))
    tiles.append(('4. Re-tap a dimmed one', 'Soft click and one ring pulse. No name, no cost.',
                  plat + f'<ellipse class="pulse" cx="{cx}" cy="{cy + 50}" rx="58" ry="15" fill="none" stroke="#F5A623" stroke-width="5"/>' + parcel('W', cx, cy, 'pink', 'dim')))
    tiles.append(('5. Found', 'Hops, glows, sparkles. The note plays at the tap, then the voice says "M! M is for moon."', plat + parcel('M', cx, cy, 'sky', 'found')))
    out = ''
    for t, d, inner in tiles:
        out += f'<figure class="cast statecard">{card_svg(W, H, inner, t, 1.0, "stage sc")}<figcaption><b>{t}</b><br>{d}</figcaption></figure>'
    return out


def pic_cards():
    out = ''
    for k in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        w = WORDS[k]
        word = (f'bo<b class="xl">x</b>' if k == 'X' else f'<b class="fl">{w[0]}</b>{w[1:]}')
        out += (f'<figure class="pic"><svg viewBox="0 0 100 100" width="100" height="100" role="img" aria-label="{w}"><use href="#p-{k}" width="100" height="100"/></svg>'
                f'<figcaption><span class="big">{k}</span> {word}</figcaption></figure>')
    return out


def alphabet_cars():
    out = ''
    for i, k in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        ck = CAR_COLS[i % 7]
        inner = '<rect width="120" height="100" fill="#fff"/>' + car(10, 6, ck, k)
        out += f'<figure class="carcard">{card_svg(120, 100, inner, "Car " + k + " " + WORDS[k], 1.0, "stage")}</figure>'
    return out


def train_strip():
    """end-screen strip: the engine then 8 cars at about 0.78 scale, newest marked new"""
    letters = 'MSABOEWF'
    inner = '<rect width="960" height="210" rx="32" fill="#FFF1D6" stroke="#E6BE8D" stroke-width="3"/>'
    inner += '<path d="M14 166 H946" stroke="#8C98A8" stroke-width="7" stroke-linecap="round"/>' + ''.join(f'<rect x="{x}" y="171" width="16" height="10" rx="3" fill="#8B5A3C" opacity=".6"/>' for x in range(20, 940, 30))
    inner += '<g transform="translate(26 96) scale(.78)">' + engine(0, 0) + '</g>'
    for i, k in enumerate(letters):
        x = 138 + i * 100
        inner += f'<g class="{"arrive" if i == 7 else ""}" transform="translate({x} 92) scale(.9)">' + car(0, 0, CAR_COLS[i % 7], k) + '</g>'
    inner += sparkle_star(910, 58, 11) + sparkle_star(930, 98, 7, '#FF6FB5')
    inner += '<text x="40" y="38" class="fred" font-size="24" font-weight="600" fill="#0F857D">Your train is growing!</text>'
    return card_svg(960, 210, inner, 'Alphabet train, engine and eight cars', 1.0, 'scene wide')


def phone_box(inner_scene, label, ref=None):
    r = f'<div class="ref64" style="left:{ref[0]}px;top:{ref[1]}px" aria-hidden="true"><span>64 px</span></div>' if ref else ''
    return (f'<div class="phonewrap"><div class="phone" style="width:667px;height:375px"><div class="phone-in">{inner_scene}</div>{r}</div><p class="cap">{label}</p></div>')


def desktop_box(inner_scene, label):
    return (f'<div class="deskwrap"><div class="desk" id="desk"><div class="desk-in">{inner_scene}</div></div><p class="cap">{label}</p></div>')


def mini_demo():
    return f'''<div class="demo" id="demo"><svg viewBox="0 0 240 220" width="240" height="220" role="img" aria-label="Tap the parcel to see the hop and glow" overflow="visible">
<defs><filter id="softd" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="6" stdDeviation="7" flood-color="#2b3a67" flood-opacity=".18"/></filter></defs>
<rect width="240" height="220" fill="#F7E6C2"/>
<ellipse class="demoring" cx="120" cy="170" rx="58" ry="15" fill="#FFE7A3" fill-opacity=".6" stroke="#F5A623" stroke-width="6"/>
<circle class="demoglow" cx="120" cy="106" r="80" fill="#FFE27A" opacity=".6"/>
<g class="demoparcel">{parcel('M', 120, 112, 'sky')}</g>
<g class="demospark">{sparkle_star(184, 52, 12)}{sparkle_star(52, 66, 9, '#FF6FB5')}</g>
</svg>
<div class="democtl"><button id="tapbtn" type="button">Tap the parcel</button>
<label><input type="checkbox" id="rmtoggle"> Pretend reduced motion</label>
<p class="small" id="demotxt">Normal: the parcel hops with a spring, a glow and sparkles appear.</p></div></div>'''


# ------------------------------------------------------------------ css and js
css = FONTS + '''
:root{--cream:#FFF7E8;--ink:#3B2A20;--teal:#0F857D;--teal-dark:#0A625C;--card:#fff;--spring:cubic-bezier(.34,1.56,.64,1)}
*{box-sizing:border-box}
body{margin:0;background:var(--cream);color:var(--ink);font-family:Andika,"Atkinson Hyperlegible",system-ui,sans-serif;padding:24px 16px 80px}
.fred{font-family:Fredoka,"Arial Rounded MT Bold","Nunito","Varela Round",ui-rounded,system-ui,sans-serif}
main{max-width:980px;margin:0 auto}
h1,h2,h3{font-family:Fredoka,"Arial Rounded MT Bold",ui-rounded,system-ui,sans-serif}
h1{color:var(--teal);margin:0 0 4px} h2{margin:44px 0 8px} h3{margin:22px 0 6px}
p,li{line-height:1.5} p{max-width:70ch}
.scene{width:100%;height:auto;border-radius:32px;box-shadow:0 10px 30px rgba(43,58,103,.18);display:block;background:#fff}
.row{display:flex;flex-wrap:wrap;gap:18px;align-items:flex-end}
.cast{margin:0;text-align:center;background:#fff;border-radius:24px;padding:14px 18px;box-shadow:0 6px 18px rgba(43,58,103,.12)}
.cast figcaption{font-size:15px;margin-top:6px;max-width:30ch}
.states{align-items:stretch}.statecard{padding:0 0 12px;overflow:hidden;width:220px}.statecard figcaption{padding:0 12px;max-width:none;font-size:14px}.statecard svg{display:block;margin-bottom:8px}
.wide2{width:100%;max-width:560px}
.chip{display:inline-block;background:#fff;border-radius:999px;padding:6px 14px;margin:4px;box-shadow:0 3px 10px rgba(43,58,103,.1);font-family:Fredoka,"Arial Rounded MT Bold",system-ui,sans-serif;font-weight:600}
.chip.look{background:#E4F3F1}
.note{background:#fff;border-left:6px solid var(--teal);border-radius:12px;padding:10px 16px;max-width:70ch}
.decide{background:#fff;border:3px solid var(--teal);border-radius:24px;padding:8px 24px 18px;margin-top:20px}
.decide li{margin:8px 0}
table{border-collapse:collapse;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 14px rgba(43,58,103,.1);max-width:100%}
td,th{padding:8px 14px;text-align:left;border-bottom:1px solid #F0E6D2;font-size:15px}th{background:#E4F3F1;font-family:Fredoka,system-ui,sans-serif}
.tablewrap{overflow-x:auto;max-width:100%}
.cap{font-size:14px;margin:6px 0 0}.small{font-size:14px}
.phonewrap{overflow-x:auto;max-width:100%;padding-bottom:6px}
.phone{position:relative;background:#3B2A20;border-radius:20px;overflow:hidden;flex:none}
.phone-in{position:absolute;left:33.5px;top:0;width:600px;height:375px}
.phone-in .scene{border-radius:0;box-shadow:none;width:600px;height:375px}
.ref64{position:absolute;width:64px;height:64px;border:3px dashed #FF6FB5;border-radius:10px;display:flex;align-items:flex-end;justify-content:center;pointer-events:none}
.ref64 span{font:700 11px/1 system-ui,sans-serif;color:#fff;background:#FF6FB5;padding:2px 5px;border-radius:6px;transform:translateY(8px)}
.deskwrap{overflow-x:auto;max-width:100%}
.desk{position:relative;width:1280px;height:720px;background:var(--cream);border-radius:12px;overflow:hidden;box-shadow:0 10px 30px rgba(43,58,103,.18)}
.desk-in{position:absolute;left:64px;top:0;width:1152px;height:720px}
.desk-in .scene{border-radius:0;box-shadow:none;width:1152px;height:720px}
.pics{display:grid;grid-template-columns:repeat(auto-fill,minmax(132px,1fr));gap:12px}
.pic{margin:0;background:#fff;border-radius:20px;padding:10px 6px 8px;text-align:center;box-shadow:0 4px 14px rgba(43,58,103,.1)}
.pic svg{display:block;margin:0 auto 4px}
.pic figcaption{font-size:18px}.pic .big{font-family:Andika,sans-serif;font-size:26px;color:var(--teal);margin-right:4px}
.fl{color:var(--teal)}.xl{color:#D94E94}
.cars{display:grid;grid-template-columns:repeat(auto-fill,minmax(128px,1fr));gap:8px}
.carcard{margin:0;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 3px 10px rgba(43,58,103,.1);display:flex;justify-content:center}
.demo{display:flex;flex-wrap:wrap;gap:18px;align-items:center;background:#fff;border-radius:24px;padding:14px;box-shadow:0 6px 18px rgba(43,58,103,.12);max-width:640px}
.demo svg{border-radius:16px}
.demo button{font:600 20px Fredoka,"Arial Rounded MT Bold",system-ui,sans-serif;color:#fff;background:var(--teal);border:0;border-radius:999px;padding:12px 24px;box-shadow:0 6px 0 var(--teal-dark);cursor:pointer;margin-bottom:10px;min-height:48px}
.demo button:active{transform:translateY(4px);box-shadow:0 2px 0 var(--teal-dark)}
.demo label{display:block;margin:6px 0}
.wide{border-radius:26px}
.small-row{align-items:flex-end}
/* motion: transform and opacity only */
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
.bob{animation:bob 2.8s ease-in-out infinite}
@keyframes hopf{0%,100%{transform:translateY(0) scale(1,1)}45%{transform:translateY(-8px) scale(.97,1.04)}}
.hopf{transform-box:fill-box;transform-origin:50% 100%;animation:hopf 1.3s var(--spring) infinite}
@keyframes tw{0%,100%{opacity:.25}50%{opacity:1}}
.twinkle{animation:tw 1.5s ease-in-out infinite}
.glow{animation:tw 1.5s ease-in-out infinite}
@keyframes sheen{0%{transform:translateX(-40px);opacity:0}15%{opacity:.7}60%{transform:translateX(150px);opacity:.7}70%,100%{transform:translateX(170px);opacity:0}}
.sheen{transform:translateX(var(--sx,0px));animation:sheen 3.2s ease-in-out infinite}
@keyframes pulse{0%{transform:scale(1);opacity:.9}100%{transform:scale(1.35);opacity:0}}
.pulse{transform-box:fill-box;transform-origin:center;animation:pulse 1.6s ease-out infinite}
.spk{transform-box:fill-box;transform-origin:center;animation:pulse 2s ease-out infinite}
@keyframes puff{0%,100%{transform:translateY(0);opacity:.9}50%{transform:translateY(-8px);opacity:.5}}
.puff{animation:puff 3s ease-in-out infinite}
@keyframes arrive{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
/* demo */
.demoparcel,.demoring,.demoglow,.demospark{transform-box:fill-box;transform-origin:50% 100%}
.demoring,.demoglow,.demospark{opacity:0}
.demo.go .demoring,.demo.go .demoglow,.demo.go .demospark{animation:fadein .3s ease-out forwards}
.demo.go .demoparcel{animation:dhop .55s var(--spring)}
@keyframes fadein{to{opacity:1}}
@keyframes dhop{0%{transform:translateY(0)}40%{transform:translateY(-24px) scale(.97,1.04)}100%{transform:translateY(-18px)}}
.demo.rm.go .demoparcel{animation:none}
.demo.rm.go .demoring,.demo.rm.go .demoglow,.demo.rm.go .demospark{animation:fadein .25s linear forwards}
@media (prefers-reduced-motion:reduce){
 .bob,.hopf,.twinkle,.glow,.sheen,.pulse,.spk,.puff,.arrive{animation:none}
 .twinkle{opacity:.85}.glow{opacity:.5}.sheen{opacity:.6}.pulse,.spk{opacity:.45}
 .demo.go .demoparcel{animation:none}
}
@media (max-width:640px){.cast figcaption{max-width:24ch}}
'''

js = '''
(function(){
  var d=document.getElementById('demo'),b=document.getElementById('tapbtn'),c=document.getElementById('rmtoggle'),t=document.getElementById('demotxt');
  function say(){t.textContent=d.classList.contains('rm')?'Reduced motion: no hop, no spring. The glow and sparkles just fade in. Same information.':'Normal: the parcel hops with a spring, a glow and sparkles appear.';}
  b.addEventListener('click',function(){d.classList.remove('go');void d.offsetWidth;d.classList.add('go');});
  c.addEventListener('change',function(){d.classList.toggle('rm',c.checked);d.classList.remove('go');say();});
})();
'''

# ------------------------------------------------------------------ scenes
S_EMPTY = scene('The station with no letters: a small railway station, a platform, and a train of empty cars waiting on the top track', [], 'n', None)
S_ASK1 = scene('Level 1: the fox asks the child to find a letter. Three parcels in a row. The bubble shows only a speaker.', spec(L1), 'n', 'ask', 0)
S_ASK4 = scene('Level 4: eight parcels in a pile, three look-alike pairs on the board. Every letter shimmers once after a wait.',
               spec(L4, lambda l: 'shimmer'), 'n', 'ask', 3, ['S', 'A', 'B'])
S_WRONG = scene('Wrong tap: W is dimmed and the fox thinks. Nothing else changes.',
                spec(L4, lambda l: 'dim' if l == 'W' else 'idle'), 't', 'ask', 3, ['S', 'A', 'B'], tilt_hazel=True)
S_NARROW = scene('Narrowed to two: after the second miss only M and its look-alike W stay lit.',
                 spec(L4, lambda l: 'idle' if l in 'MW' else 'dim'), 't', 'ask', 3, ['S', 'A', 'B'], tilt_hazel=True)
S_FOUND = scene('Found: the M parcel hops and glows, the fox is happy, the car fills with M and a moon.',
                spec(L4, lambda l: 'found' if l == 'M' else ('dim' if l in 'EFOQWHS' else 'idle')), 'h', 'found', 4, ['S', 'A', 'B', 'M'])
S_MUTED = scene('Muted play: the letter card shows from the start because the child cannot hear the request.',
                spec(L1), 'n', 'card', 0, muted=True)

# phone views (scene letterboxed at 0.625)
PH1 = phone_box(scene('Level 1 on a phone', spec(L1), 'n', 'ask', 0), 'Level 1 on a 667 x 375 phone. The dashed pink square is a real 64 px square; the parcel hit area (65 px) is just bigger than it.', (295, 230))
PH4 = phone_box(scene('Level 4 on a phone', spec(L4, lambda l: 'idle'), 'n', 'ask', 3, ['S', 'A', 'B']), 'Level 4 on the same phone: eight parcels, closest centres 112+ scene px (70 px on the phone). No parcel overlaps another.', (270, 182))
DESK = desktop_box(scene('Level 4 on desktop', spec(L4, lambda l: 'idle'), 'n', 'ask', 3, ['S', 'A', 'B']), 'Desktop (1280 x 720): the same scene, scaled to height, cream bars at the sides.')

LOOK = ('M W', 'E F', 'O Q')

html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Letter Station art preview</title>
<style>{css}</style></head><body>{symbols()}<main>
<h1>Letter Station: art direction preview</h1>
<p>Static prototype for approval (game 6, Letter tap, Pre-K). Nothing here is the final game and there is no game logic. It shows the cast, the station, the letter carriers, every state, the Alphabet train reward, and the phone and desktop views, so we can agree on the art before any development.
It follows the v3 style guide: cream and teal, rounded shapes, soft tinted shadows, no red in feedback. Letters are set in <b>Andika</b>, the kit's early-reader font, and titles in Fredoka (both embedded from the website's self-hosted copies, so what you see is what the game will show). Motion is gentle, all transform and opacity, with a reduced-motion version.</p>

<h2>1. The cast: the fox station master and Hazel</h2>
<p>A fox runs the station. He is orange with a cream face and chest, big ears with dark tips, a bushy tail, and a teal jacket with a sun-yellow scarf, buttons and a station master's cap with a star badge (the star links to the stars children earn, like Hazel's charm). He has the same chibi proportions as Hazel: big head, big eyes, round cheeks, soft outlines in a darker shade of his own colour. He carries a plain green "go" paddle, so there is no letter or numeral on him anywhere. Hazel stays as the host and hint helper, exactly as drawn in <code>brand/mascot/owl.svg</code>.</p>
<div class="row">{cast_cards()}</div>
<h3>Readable at phone size</h3>
<p>The fox is drawn 170 scene px wide, which is 106 px on a 667 x 375 phone. Below he is shown at 64 px, the smallest size we allow, next to his happy pose. The cap, ears, eyes and tail still read at 64 px, and happy versus neutral is clear from the open mouth and raised arms alone.</p>
{fox_small()}

<h2>2. The station scene (no letters anywhere)</h2>
<p>A small railway station with a flat teal canopy roof, a blank signboard, a door, two windows with flower boxes, a platform with a yellow safety stripe, and a train of <b>five empty cars</b> waiting on the top track behind the platform. Each solved letter fills one car (the dashed windows are where the letter and its picture land). The Back button, ten progress dots and audio toggle follow the same HUD as the other games.</p>
{S_EMPTY}
<div class="note"><b>Rule check (F9): no letters, numerals or letter-shaped props.</b> What is in the scene: a house with a flat roof (not a gable, which reads as A), a blank signboard (no text, no clock face), a lantern in a rounded box (not a hanging lamp), round-topped bushes, flat horizontal rails and sleepers. What was left out on purpose: a station clock (an O and numerals), lamp posts and telegraph poles (I and T), pointed mountains (A), a signal arm (T or Y), a horseshoe (U) and railings (a row of I). The only circles are the solid train wheels and the flower dots, which no child will read as the letter O.</div>

<h2>3. The letter carriers (parcels)</h2>
<p>One flat shape for every letter: a suitcase-style parcel with a handle and four rivets, a white label face and a big upright letter in Andika. Seven colours from the style guide, used in rotation by the planner so neighbours differ. The ink letter always sits on the light label (8:1 contrast or better), never white on a bright colour. The colour of a parcel carries no meaning, so a child cannot learn "the pink one is M".</p>
<div class="row states">{carrier_cards()}</div>
<h3>Anatomy</h3>
{carrier_anatomy()}
<p>The box may tilt up to about 6 degrees in a pile (the planner's rotation times 0.3). The letter is a separate layer drawn on top and is <b>never rotated</b>, so an N never reads as Z and an M never reads as W.</p>

<h3>Level 1: a row of 3 (S, A, M)</h3>
<p>Big, spread out, easy. The fox asks and the bubble shows only a speaker (the request is spoken, never written, so the child matches a name to a shape, not a shape to a shape). Centres are 170 scene px apart. No look-alikes at this level, from the locked pool A B C D E M O S.</p>
{S_ASK1}

<h3>Level 4: a pile of 8 with three look-alike pairs</h3>
<p>Eight parcels in three loose rows with tiny tilts. The board holds the look-alike pairs <b>M and W</b>, <b>E and F</b>, <b>O and Q</b>, plus H and S. Every centre is at least 112 scene px from every other (closest here: {MIN4:.0f}), parcels are 104 px, so nothing touches or covers another. The letters are never rotated. Here the board is waiting at the idle shimmer: the sheen sweeps over all eight in reading order, so it points at nothing. Three cars are already filled.</p>
<p><span class="chip look">M and W</span><span class="chip look">E and F</span><span class="chip look">O and Q</span></p>
{S_ASK4}

<h2>4. The states</h2>
<div class="row states">{state_tiles()}</div>
<p class="note">Muted players still get everything: the speaker pulse is the visual twin of the spoken request, the dim is the twin of "That's W.", and the hop and glow are the twin of the note and the voice.</p>

<h3>Asking: a speaker bubble, no letter shown</h3>
<p>The speaker disc is 104 scene px (65 px on a phone) and taps to hear the request again, free. It pulses softly while the voice speaks. See levels 1 and 4 above.</p>

<h3>Wrong tap: the letter dims, the fox thinks</h3>
<p>The tapped W dims and keeps its letter visible. The fox plays the thinking pose and Hazel tilts her head (in the game only her head moves; here the whole owl leans a little because the preview uses her fixed art). The voice says "That's W. Find M!". No red, no cross, no counter.</p>
{S_WRONG}

<h3>Narrowed to two</h3>
<p>After the second miss every parcel dims except the answer and one planned rival, here the look-alike W. "M or W?" is the exact discrimination the top level exists to teach. After a third miss only the answer stays lit, and the child still makes the last tap.</p>
{S_NARROW}

<h3>Found: hop and glow</h3>
<p>The M parcel hops at the tap, glows with sparkles and a warm ring, the fox goes happy, and the bubble now shows the picture and "M is for moon" (the letter may be shown now that it is solved). The newest car at the top fills with M and a moon. The other parcels dim so the eye stays on the winner.</p>
{S_FOUND}

<h3>Muted: the card hint</h3>
<p>If the player has audio off, they cannot hear the request, so the bubble shows the letter card ("It looks like this!") from the start, and the audio toggle shows a slash. The same card appears when a child taps Hazel for help while audio is on. Showing it costs one hint.</p>
{S_MUTED}

<h2>5. Reward: the Alphabet train</h2>
<p>One car per solved round, with the letter and a picture. The fox's train grows by rounds solved, never by time. Cars are coloured in rotation, the letter is in Andika, and the picture is a simple flat SVG in the same style as the rest of the art. The word is never shown on the car (reading load stays minimal); it is written below for the owner only.</p>
<h3>The train on the end screen (engine plus the 8 newest cars)</h3>
{train_strip()}
<h3>The 26 pictures</h3>
<p>One picturable word per letter. Each starts with its plain letter and that letter's common first sound. <b>X is "box"</b>, with the x at the end of the word (shown in pink below); the box picture has no cross or X-shaped tape on it, on purpose. The teal letter is the one the word starts with. Words to look at twice: <b>Q "quilt"</b> (starts with "kw", which is Q's normal sound), <b>I "igloo"</b> and <b>O "octopus"</b> (short vowel sounds, not "ice" or "owl"), <b>U "umbrella"</b> (short u), <b>J "jam"</b> (a jam jar) and <b>E "egg"</b>.</p>
<div class="pics">{pic_cards()}</div>
<h3>All 26 cars</h3>
<div class="cars">{alphabet_cars()}</div>

<h2>6. Phone and desktop views</h2>
<p>A 667 x 375 landscape phone shows the 960 x 600 scene at 0.625 scale (600 x 375 with dark bars). Real pixel sizes on this phone:</p>
<div class="tablewrap"><table><tr><th>Element</th><th>Scene px</th><th>Phone px</th></tr>
<tr><td>Parcel (hit target, 104 round)</td><td>104 x 104</td><td>65 x 65</td></tr>
<tr><td>Letter cap height</td><td>about 58</td><td>about 36</td></tr>
<tr><td>Spacing between parcel centres, level 1 row</td><td>170</td><td>106</td></tr>
<tr><td>Spacing between parcel centres, level 4 pile, closest</td><td>{MIN4:.0f}</td><td>{MIN4 * .625:.0f}</td></tr>
<tr><td>Speaker bubble disc (hit target)</td><td>104</td><td>65</td></tr>
<tr><td>Fox</td><td>170 wide</td><td>106 wide</td></tr>
<tr><td>Hazel (hint helper, with crate)</td><td>90 x 130</td><td>56 x 81</td></tr>
<tr><td>Train car (decoration, not a target)</td><td>92 x 86</td><td>58 x 54</td></tr>
<tr><td>Back button</td><td>124 x 56</td><td>77.5 x 35</td></tr>
<tr><td>Audio toggle</td><td>60 across</td><td>37.5</td></tr></table></div>
<p class="note">Same two flags as the earlier games: Back and audio are only 35 and 37.5 px tall on this phone and need a padded hit area of about 48 px when built. Hazel's hit area should also be padded to 64 px.</p>
<h3>Phone, level 1</h3>
{PH1}
<h3>Phone, level 4</h3>
{PH4}
<h3>Desktop</h3>
{DESK}

<h2>7. Reduced motion and muted play</h2>
<p><b>Reduced motion.</b> Every motion on this page is transform or opacity only. When the device asks for reduced motion: the parcel pop-in becomes a fade, the hop becomes a glow (opacity), the shimmer becomes a steady soft sheen (opacity only), the speaker pulse becomes a still ring, the fox's bob stops, the new car fades in place instead of rolling in, and confetti is off. The state still shows: a found parcel is still lit and glowing, a wrong one is still dimmed. Try it:</p>
{mini_demo()}
<h3>Every sound has a visual twin</h3>
<div class="tablewrap"><table><tr><th>Sound</th><th>Visual twin (shows even when muted)</th></tr>
<tr><td>Spoken "Find M!"</td><td>Speaker icon pulses in the bubble; the fox waits. When muted, the letter card shows instead.</td></tr>
<tr><td>Note at a right tap, then "M! M is for moon."</td><td>Hop, glow, sparkles, happy fox, the bubble shows the moon and the words</td></tr>
<tr><td>"That's W." after a wrong tap</td><td>The W parcel dims, the fox thinks</td></tr>
<tr><td>Soft click on a dimmed parcel</td><td>Ring pulse, nothing else</td></tr>
<tr><td>Repeat of the request after a wait</td><td>Every letter shimmers once in reading order, the fox bobs</td></tr>
<tr><td>Rising run and chord, then the car</td><td>The parcel slides up to the train and fills the next car</td></tr></table></div>

<h2>8. Decisions for the owner</h2>
<div class="decide"><ul>
<li><b>Carrier (decision 18).</b> One flat suitcase-style parcel in seven colours, letter on a white label, only the box tilts. Say yes, or ask for a plain card or a different object (a crate, a gift box).</li>
<li><b>Fox likeness.</b> Orange fox, cream face, teal jacket, sun scarf, station master cap with a star. His teal jacket is the same teal as the Back button so the brand colour sits on a new friend. Hazel's brown and the fox's orange are different enough that they never blur, and Hazel stays in her corner on a crate.</li>
<li><b>Reward words (decision 19).</b> A apple, B ball, C cat, D dog, E egg, F fish, G grapes, H house, I igloo, J jam, K kite, L lemon, M moon, N nest, O octopus, P pig, Q quilt, R rainbow, S sun, T turtle, U umbrella, V vase, W worm, X box, Y yarn, Z zebra. Swap any you dislike; each is one small SVG.</li>
<li><b>Train placement.</b> The scene shows the train of empty cars on a top track so the goal is visible while playing. The design doc described a bottom strip with the newest 8 cars; this preview puts the five-car train at the top instead (the end screen shows the 8-car strip). Either works; the top track keeps the bottom free for the pile.</li>
<li><b>Words on cars.</b> The cars show the letter and the picture only, no word. The word is spoken ("M is for moon"). Say if you want the word printed on the car too.</li>
<li><b>Palette.</b> No new colours. The fox orange (#F28C38) and dark tail brown (#6E3B22) are new tints near the existing caramel and cocoa; the parcel colours reuse sky, pink, sun, leaf and teal plus an orange (#FF9F43) and a lilac (#B69CF0) already used for the duck feet and mouse.</li>
<li><b>Small hit areas.</b> Back and audio need a padded hit area (about 48 px); Hazel needs about 64 px.</li>
</ul></div>
</main><script>{js}</script></body></html>'''

open('index.html', 'w').write(html)
for ch in (chr(0x2014), chr(0x2013)):
    assert ch not in html, 'dash found'
print(len(html))
