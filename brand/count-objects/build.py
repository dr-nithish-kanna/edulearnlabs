import re, math

# Hazel (source of truth: brand/mascot/owl.svg), embedded once as a symbol
owl = open('../mascot/owl.svg').read()
owl_inner = re.sub(r'^<svg[^>]*>', '', owl.strip())
owl_inner = owl_inner[:owl_inner.rindex('</svg>')]
owl_inner = re.sub(r'<title>.*?</title>', '', owl_inner, flags=re.S)
owl_inner = re.sub(r'<!--.*?-->', '', owl_inner, flags=re.S)

INK = '#3B2A20'


def spikes(cx, cy, rx, ry, n, inner, rot=0.0):
    pts = []
    for i in range(2 * n):
        a = math.pi * i / n + rot
        f = 1 if i % 2 == 0 else inner
        pts.append(f'{cx + rx * f * math.cos(a):.1f},{cy + ry * f * math.sin(a):.1f}')
    return ' '.join(pts)


# ---------------------------------------------------------------- cast
def eyes_round(pts, r=8):
    out = ''
    for (x, y) in pts:
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


def hedgehog(happy):
    body = spikes(70, 84, 58, 52, 13, .80, 0.1)
    body2 = spikes(70, 84, 50, 44, 13, .78, 0.1 + math.pi / 13)
    if happy:
        eyes = eyes_happy([(108, 84), (130, 84)], 7.5)
        mouth = (f'<path d="M144 105 Q153 126 165 105 Z" fill="{INK}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
                 '<path d="M149 114 Q154 121 160 114 Q154 111 149 114Z" fill="#FF6FB5"/>')
        paws = ''
        extra = sparkle_star(26, 28, 9) + sparkle_star(160, 30, 7, '#FF6FB5')
        cheek = .75
    else:
        eyes = eyes_round([(108, 84), (130, 84)], 8)
        mouth = f'<path d="M146 108 Q153 116 161 108" fill="none" stroke="{INK}" stroke-width="3.2" stroke-linecap="round"/>'
        paws = ('<ellipse cx="96" cy="124" rx="11" ry="9" fill="#F6DDB8" stroke="#C8996A" stroke-width="2.5"/>')
        extra = ''
        cheek = .55
    return f'''
<ellipse cx="84" cy="142" rx="64" ry="6" fill="#2b3a67" opacity=".15"/>
<ellipse cx="62" cy="136" rx="14" ry="8" fill="#C8996A" stroke="#A97A4C" stroke-width="2.5"/>
<ellipse cx="112" cy="136" rx="14" ry="8" fill="#C8996A" stroke="#A97A4C" stroke-width="2.5"/>
<polygon points="{body}" fill="#6E432A" stroke="#6E432A" stroke-width="9" stroke-linejoin="round"/>
<polygon points="{body2}" fill="#8B5A3C" stroke="#8B5A3C" stroke-width="8" stroke-linejoin="round"/>
<g fill="none" stroke="#B07A52" stroke-width="3.5" stroke-linecap="round" opacity=".8"><path d="M32 78 Q38 54 58 44"/><path d="M44 92 Q44 76 54 66"/></g>
<ellipse cx="96" cy="104" rx="30" ry="26" fill="#F6DDB8"/>
<ellipse cx="118" cy="92" rx="38" ry="34" fill="#F6DDB8" stroke="#C8996A" stroke-width="2.5"/>
<ellipse cx="146" cy="100" rx="19" ry="14" fill="#F6DDB8" stroke="#C8996A" stroke-width="2.5"/>
<ellipse cx="118" cy="92" rx="35" ry="31" fill="#F6DDB8"/>
<circle cx="104" cy="58" r="13" fill="#F6DDB8" stroke="#C8996A" stroke-width="2.5"/><circle cx="104" cy="59" r="7" fill="#FFB3DA"/>
<circle cx="136" cy="62" r="11" fill="#F6DDB8" stroke="#C8996A" stroke-width="2.5"/><circle cx="136" cy="63" r="5.5" fill="#FFB3DA"/>
<ellipse cx="102" cy="100" rx="7" ry="4.5" fill="#FF6FB5" opacity="{cheek}"/><ellipse cx="132" cy="102" rx="6" ry="4" fill="#FF6FB5" opacity="{cheek}"/>
{eyes}
<ellipse cx="160" cy="96" rx="8.5" ry="7" fill="{INK}"/><ellipse cx="157.5" cy="93.5" rx="2.6" ry="1.8" fill="#fff" opacity=".8"/>
{mouth}{paws}{extra}'''


def duck(happy):
    wing_l = '<ellipse cx="30" cy="106" rx="14" ry="24" transform="rotate(14 30 106)" fill="#F5B52A" stroke="#D99E12" stroke-width="2.5"/>'
    wing_r = '<ellipse cx="120" cy="106" rx="14" ry="24" transform="rotate(-14 120 106)" fill="#F5B52A" stroke="#D99E12" stroke-width="2.5"/>'
    if happy:
        wing_l = '<ellipse cx="26" cy="86" rx="13" ry="24" transform="rotate(-38 26 86)" fill="#F5B52A" stroke="#D99E12" stroke-width="2.5"/>'
        wing_r = '<ellipse cx="124" cy="86" rx="13" ry="24" transform="rotate(38 124 86)" fill="#F5B52A" stroke="#D99E12" stroke-width="2.5"/>'
        eyes = eyes_happy([(60, 56), (90, 56)], 7)
        mouth = '<path d="M66 80 Q75 96 84 80Z" fill="#7A3B20" stroke="#7A3B20" stroke-width="2.5" stroke-linejoin="round"/>'
        extra = sparkle_star(18, 30, 9) + sparkle_star(134, 34, 7, '#FF6FB5')
        cheek = .8
    else:
        eyes = eyes_round([(60, 56), (90, 56)], 7.5)
        mouth = ''
        extra = ''
        cheek = .6
    return f'''
<ellipse cx="75" cy="152" rx="50" ry="6" fill="#2b3a67" opacity=".15"/>
<path d="M50 148 Q40 156 52 154 L66 152 Q62 146 50 148Z" fill="#FF9F43" stroke="#D9792A" stroke-width="2.5" stroke-linejoin="round"/>
<path d="M100 148 Q110 156 98 154 L84 152 Q88 146 100 148Z" fill="#FF9F43" stroke="#D9792A" stroke-width="2.5" stroke-linejoin="round"/>
{wing_l}{wing_r}
<ellipse cx="75" cy="112" rx="46" ry="40" fill="#FFC83D" stroke="#E0A91C" stroke-width="2.5"/>
<ellipse cx="75" cy="122" rx="30" ry="26" fill="#FFE08A"/>
<path d="M64 88 L75 98 L86 88 L98 96 L90 106 L75 100 L60 106 L52 96Z" fill="#2FB5EC" stroke="#1E8FC0" stroke-width="2.5" stroke-linejoin="round"/>
<circle cx="75" cy="64" r="37" fill="#FFC83D" stroke="#E0A91C" stroke-width="2.5"/>
<path d="M66 28 Q62 14 72 12 M76 28 Q78 12 88 14" fill="none" stroke="#E0A91C" stroke-width="4" stroke-linecap="round"/>
<ellipse cx="44" cy="70" rx="7.5" ry="5" fill="#FF6FB5" opacity="{cheek}"/><ellipse cx="106" cy="70" rx="7.5" ry="5" fill="#FF6FB5" opacity="{cheek}"/>
{eyes}
<ellipse cx="75" cy="72" rx="21" ry="11" fill="#FF9F43" stroke="#D9792A" stroke-width="2.5"/>
<ellipse cx="75" cy="68" rx="14" ry="5" fill="#FFBE7A" opacity=".8"/>
<circle cx="68" cy="68" r="1.8" fill="#B8601E"/><circle cx="82" cy="68" r="1.8" fill="#B8601E"/>
{mouth}{extra}'''


def mouse(happy):
    BODY, EDGE = '#D9D2E3', '#B3A8C9'
    if happy:
        arms = (f'<ellipse cx="36" cy="92" rx="8" ry="15" transform="rotate(-32 36 92)" fill="{BODY}" stroke="{EDGE}" stroke-width="2.5"/>'
                f'<ellipse cx="114" cy="92" rx="8" ry="15" transform="rotate(32 114 92)" fill="{BODY}" stroke="{EDGE}" stroke-width="2.5"/>')
        eyes = eyes_happy([(61, 62), (89, 62)], 7)
        mouth = '<path d="M64 84 Q75 102 86 84Z" fill="#7A3B20" stroke="#7A3B20" stroke-width="2.5" stroke-linejoin="round"/><path d="M69 92 Q75 98 81 92 Q75 89 69 92Z" fill="#FF6FB5"/>'
        extra = sparkle_star(16, 40, 9) + sparkle_star(136, 28, 7, '#FF6FB5')
        cheek = .85
    else:
        arms = (f'<ellipse cx="40" cy="116" rx="8" ry="15" transform="rotate(14 40 116)" fill="{BODY}" stroke="{EDGE}" stroke-width="2.5"/>'
                f'<ellipse cx="110" cy="116" rx="8" ry="15" transform="rotate(-14 110 116)" fill="{BODY}" stroke="{EDGE}" stroke-width="2.5"/>')
        eyes = eyes_round([(61, 62), (89, 62)], 7.5)
        mouth = '<path d="M69 88 Q75 93 81 88" fill="none" stroke="#3B2A20" stroke-width="3" stroke-linecap="round"/><rect x="71" y="88" width="8" height="7" rx="2.5" fill="#fff" stroke="#B3A8C9" stroke-width="1.6"/>'
        extra = ''
        cheek = .6
    return f'''
<ellipse cx="75" cy="152" rx="46" ry="6" fill="#2b3a67" opacity=".15"/>
<path d="M108 136 C132 140 146 124 138 104 C134 94 142 90 144 84" fill="none" stroke="#F3B6D2" stroke-width="7" stroke-linecap="round"/>
<ellipse cx="58" cy="148" rx="12" ry="7" fill="#FFB3DA" stroke="#E08AB8" stroke-width="2.2"/><ellipse cx="92" cy="148" rx="12" ry="7" fill="#FFB3DA" stroke="#E08AB8" stroke-width="2.2"/>
<ellipse cx="75" cy="116" rx="36" ry="34" fill="{BODY}" stroke="{EDGE}" stroke-width="2.5"/>
<ellipse cx="75" cy="124" rx="22" ry="22" fill="#F4EEF8"/>
{arms}
<circle cx="42" cy="36" r="21" fill="{BODY}" stroke="{EDGE}" stroke-width="2.5"/><circle cx="42" cy="37" r="12.5" fill="#FFB3DA"/>
<circle cx="108" cy="36" r="21" fill="{BODY}" stroke="{EDGE}" stroke-width="2.5"/><circle cx="108" cy="37" r="12.5" fill="#FFB3DA"/>
<circle cx="75" cy="66" r="35" fill="{BODY}" stroke="{EDGE}" stroke-width="2.5"/>
<ellipse cx="75" cy="76" rx="20" ry="15" fill="#F4EEF8"/>
<ellipse cx="46" cy="76" rx="7" ry="4.5" fill="#FF6FB5" opacity="{cheek}"/><ellipse cx="104" cy="76" rx="7" ry="4.5" fill="#FF6FB5" opacity="{cheek}"/>
<g stroke="{EDGE}" stroke-width="2.4" stroke-linecap="round" fill="none"><path d="M54 78 L34 74"/><path d="M54 82 L35 86"/><path d="M96 78 L116 74"/><path d="M96 82 L115 86"/></g>
{eyes}
<ellipse cx="75" cy="77" rx="6.5" ry="5" fill="#FF6FB5"/><ellipse cx="73" cy="75.4" rx="2" ry="1.4" fill="#fff" opacity=".8"/>
{mouth}{extra}'''


# ------------------------------------------------------------ objects
APPLE = '''
<ellipse cx="52" cy="99" rx="34" ry="4.5" fill="#2b3a67" opacity=".16"/>
<path d="M52 32 C42 20 14 24 12 54 C10 80 30 98 44 94 C48 93 50 92 52 92 C54 92 56 93 60 94 C74 98 94 80 92 54 C90 24 62 20 52 32Z" fill="#EF5B45" stroke="#C23B2B" stroke-width="3" stroke-linejoin="round"/>
<path d="M84 52 C86 76 72 92 58 93 C74 96 92 80 90 54 Z" fill="#D9442F" opacity=".55"/>
<ellipse cx="29" cy="50" rx="6.5" ry="11" transform="rotate(18 29 50)" fill="#fff" opacity=".5"/>
<path d="M52 32 C52 24 54 18 59 13" fill="none" stroke="#6E432A" stroke-width="5" stroke-linecap="round"/>
<path d="M58 22 C64 8 82 8 88 16 C82 28 66 28 58 22Z" fill="#46C47E" stroke="#2FA866" stroke-width="2.5" stroke-linejoin="round"/>
<path d="M62 21 C70 17 78 17 84 16" fill="none" stroke="#2FA866" stroke-width="1.8" stroke-linecap="round"/>'''

PEBBLE_A = '''
<ellipse cx="52" cy="95" rx="40" ry="4.5" fill="#2b3a67" opacity=".16"/>
<path d="M8 66 C6 44 26 30 54 30 C82 30 100 44 96 66 C94 84 74 93 50 93 C24 93 10 84 8 66Z" fill="#A9B7C9" stroke="#7B8BA3" stroke-width="3" stroke-linejoin="round"/>
<path d="M12 72 C16 86 34 91 52 91 C74 91 92 84 94 68 C86 82 66 86 48 86 C30 86 18 80 12 72Z" fill="#8E9DB5" opacity=".6"/>
<path d="M24 56 C38 46 60 44 78 50" fill="none" stroke="#E8EEF6" stroke-width="5" stroke-linecap="round" opacity=".75"/>
<g fill="#7B8BA3" opacity=".75"><circle cx="34" cy="68" r="2.8"/><circle cx="60" cy="72" r="3.2"/><circle cx="78" cy="66" r="2.4"/><circle cx="48" cy="78" r="2.2"/></g>'''

PEBBLE_B = '''
<ellipse cx="52" cy="95" rx="38" ry="4.5" fill="#2b3a67" opacity=".16"/>
<path d="M12 70 C8 50 22 36 42 32 C66 28 94 40 94 64 C94 84 72 93 48 93 C28 93 14 86 12 70Z" fill="#B3C0D1" stroke="#7B8BA3" stroke-width="3" stroke-linejoin="round"/>
<path d="M16 76 C22 88 40 91 54 90 C74 89 90 82 92 66 C84 80 66 84 50 84 C34 84 22 82 16 76Z" fill="#8E9DB5" opacity=".6"/>
<path d="M22 60 C30 46 52 40 70 42" fill="none" stroke="#EEF2F8" stroke-width="5" stroke-linecap="round" opacity=".8"/>
<g fill="#7B8BA3" opacity=".75"><circle cx="30" cy="72" r="2.6"/><circle cx="74" cy="70" r="3"/><circle cx="82" cy="56" r="2.2"/></g>'''

ACORN = '''
<ellipse cx="52" cy="101" rx="26" ry="3.6" fill="#2b3a67" opacity=".16"/>
<path d="M20 44 H84 C86 68 72 90 52 98 C32 90 18 68 20 44Z" fill="#D9A25F" stroke="#A5703F" stroke-width="3" stroke-linejoin="round"/>
<path d="M32 52 C32 66 38 80 46 88" fill="none" stroke="#F3CE96" stroke-width="5" stroke-linecap="round"/>
<path d="M14 44 C12 22 32 10 52 10 C72 10 92 22 90 44Z" fill="#8B5A3C" stroke="#6E432A" stroke-width="3" stroke-linejoin="round"/>
<g stroke="#6E432A" stroke-width="2.2" opacity=".55" stroke-linecap="round" fill="none"><path d="M26 18 L40 42"/><path d="M40 12 L54 42"/><path d="M58 12 L48 42"/><path d="M74 14 L58 42"/><path d="M84 24 L68 42"/><path d="M20 34 H84"/></g>
<path d="M24 24 C28 18 36 14 44 13" fill="none" stroke="#B07A52" stroke-width="4.5" stroke-linecap="round"/>
<rect x="10" y="40" width="84" height="13" rx="6.5" fill="#A8734D" stroke="#6E432A" stroke-width="3"/>
<path d="M52 10 C52 6 54 3 58 2" fill="none" stroke="#6E432A" stroke-width="5" stroke-linecap="round"/>'''

# ------------------------------------------------------------ baby farm animals (viewBox 0 0 100 100)
def eye(x, y, r=4.4):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{INK}"/><circle cx="{x - r * .3:.1f}" cy="{y - r * .35:.1f}" r="{r * .38:.1f}" fill="#fff"/>')


SH = '<ellipse cx="50" cy="95" rx="30" ry="4" fill="#2b3a67" opacity=".15"/>'

CHICK = SH + f'''
<path d="M40 90 L36 97 M40 90 L42 97 M60 90 L58 97 M60 90 L64 97" stroke="#E5532E" stroke-width="3.2" stroke-linecap="round" fill="none"/>
<ellipse cx="20" cy="62" rx="9" ry="14" transform="rotate(20 20 62)" fill="#FFB36B" stroke="#D9822B" stroke-width="2.5"/>
<ellipse cx="80" cy="62" rx="9" ry="14" transform="rotate(-20 80 62)" fill="#FFB36B" stroke="#D9822B" stroke-width="2.5"/>
<circle cx="50" cy="58" r="31" fill="#FFCB94" stroke="#D9822B" stroke-width="2.5"/>
<path d="M44 28 Q42 16 50 14 Q52 22 50 28 M52 28 Q58 16 66 20 Q62 26 56 30" fill="#FFCB94" stroke="#D9822B" stroke-width="2.5" stroke-linejoin="round"/>
<ellipse cx="34" cy="64" rx="5.5" ry="3.6" fill="#FF6FB5" opacity=".6"/><ellipse cx="66" cy="64" rx="5.5" ry="3.6" fill="#FF6FB5" opacity=".6"/>
{eye(39, 52)}{eye(61, 52)}
<path d="M43 60 Q50 57 57 60 Q55 69 50 70 Q45 69 43 60Z" fill="#E5532E" stroke="#B8401F" stroke-width="2" stroke-linejoin="round"/>'''

LAMB = SH + f'''
<rect x="38" y="82" width="8" height="12" rx="4" fill="#6E432A"/><rect x="54" y="82" width="8" height="12" rx="4" fill="#6E432A"/>
<g fill="#FFFDF6" stroke="#DDD3C0" stroke-width="2.5">
<circle cx="26" cy="58" r="17"/><circle cx="74" cy="58" r="17"/><circle cx="32" cy="76" r="15"/><circle cx="68" cy="76" r="15"/><circle cx="50" cy="80" r="14"/><circle cx="36" cy="40" r="15"/><circle cx="64" cy="40" r="15"/><circle cx="50" cy="32" r="16"/></g>
<g fill="#FFFDF6"><circle cx="26" cy="58" r="15"/><circle cx="74" cy="58" r="15"/><circle cx="36" cy="40" r="13"/><circle cx="64" cy="40" r="13"/><circle cx="50" cy="32" r="14"/><circle cx="50" cy="62" r="24"/></g>
<ellipse cx="22" cy="54" rx="8" ry="13" transform="rotate(34 22 54)" fill="#6E432A"/><ellipse cx="78" cy="54" rx="8" ry="13" transform="rotate(-34 78 54)" fill="#6E432A"/>
<ellipse cx="50" cy="62" rx="19" ry="21" fill="#7A4B30" stroke="#6E432A" stroke-width="2"/>
<circle cx="50" cy="38" r="9" fill="#FFFDF6" stroke="#DDD3C0" stroke-width="2"/>
<circle cx="41" cy="58" r="5.6" fill="#fff"/><circle cx="59" cy="58" r="5.6" fill="#fff"/>
<circle cx="41.5" cy="58.5" r="3.4" fill="{INK}"/><circle cx="58.5" cy="58.5" r="3.4" fill="{INK}"/>
<ellipse cx="50" cy="70" rx="5.5" ry="4" fill="#FFB3DA"/>'''

CALF = SH + f'''
<rect x="34" y="84" width="9" height="11" rx="4" fill="#5A3F32"/><rect x="57" y="84" width="9" height="11" rx="4" fill="#5A3F32"/>
<ellipse cx="50" cy="82" rx="24" ry="13" fill="#fff" stroke="#D4CABB" stroke-width="2.5"/>
<path d="M30 80 C32 74 42 74 42 82 C40 90 30 90 30 80Z" fill="#8B5A3C"/>
<ellipse cx="19" cy="48" rx="13" ry="7.5" transform="rotate(-18 19 48)" fill="#8B5A3C" stroke="#6E432A" stroke-width="2.2"/>
<ellipse cx="81" cy="48" rx="13" ry="7.5" transform="rotate(18 81 48)" fill="#fff" stroke="#D4CABB" stroke-width="2.2"/>
<ellipse cx="19" cy="48" rx="6" ry="3.4" transform="rotate(-18 19 48)" fill="#FFB3DA" opacity=".8"/>
<ellipse cx="81" cy="48" rx="6" ry="3.4" transform="rotate(18 81 48)" fill="#FFB3DA" opacity=".8"/>
<path d="M36 30 C34 22 38 18 42 22" fill="none" stroke="#E9C98F" stroke-width="5.5" stroke-linecap="round"/>
<path d="M64 30 C66 22 62 18 58 22" fill="none" stroke="#E9C98F" stroke-width="5.5" stroke-linecap="round"/>
<ellipse cx="50" cy="52" rx="28" ry="27" fill="#fff" stroke="#D4CABB" stroke-width="2.5"/>
<path d="M30 36 C34 26 50 24 54 28 C52 38 44 44 36 46 C32 44 30 40 30 36Z" fill="#8B5A3C"/>
<ellipse cx="50" cy="66" rx="17" ry="12" fill="#FFB3DA" stroke="#E08AB8" stroke-width="2.2"/>
<ellipse cx="44" cy="66" rx="2.6" ry="3.4" fill="#B5527F"/><ellipse cx="56" cy="66" rx="2.6" ry="3.4" fill="#B5527F"/>
{eye(39, 50)}{eye(61, 50)}'''

PIGLET = SH + f'''
<ellipse cx="40" cy="92" rx="7" ry="4.5" fill="#FF92C8" stroke="#E87AB0" stroke-width="2"/><ellipse cx="60" cy="92" rx="7" ry="4.5" fill="#FF92C8" stroke="#E87AB0" stroke-width="2"/>
<ellipse cx="50" cy="82" rx="22" ry="13" fill="#FFB3DA" stroke="#E87AB0" stroke-width="2.5"/>
<path d="M20 38 C14 22 22 16 34 24 C38 30 36 38 30 42Z" fill="#FF92C8" stroke="#E87AB0" stroke-width="2.5" stroke-linejoin="round"/>
<path d="M80 38 C86 22 78 16 66 24 C62 30 64 38 70 42Z" fill="#FF92C8" stroke="#E87AB0" stroke-width="2.5" stroke-linejoin="round"/>
<circle cx="50" cy="56" r="30" fill="#FFB3DA" stroke="#E87AB0" stroke-width="2.5"/>
<ellipse cx="31" cy="68" rx="6" ry="4" fill="#FF6FB5" opacity=".55"/><ellipse cx="69" cy="68" rx="6" ry="4" fill="#FF6FB5" opacity=".55"/>
{eye(38, 50)}{eye(62, 50)}
<ellipse cx="50" cy="66" rx="14" ry="10.5" fill="#FF92C8" stroke="#E87AB0" stroke-width="2.5"/>
<ellipse cx="45" cy="66" rx="2.6" ry="3.6" fill="#B5527F"/><ellipse cx="55" cy="66" rx="2.6" ry="3.6" fill="#B5527F"/>'''

BUNNY = SH + f'''
<ellipse cx="38" cy="92" rx="8" ry="4.5" fill="#E9D0AE" stroke="#B89466" stroke-width="2"/><ellipse cx="62" cy="92" rx="8" ry="4.5" fill="#E9D0AE" stroke="#B89466" stroke-width="2"/>
<ellipse cx="50" cy="82" rx="22" ry="13" fill="#E9D0AE" stroke="#B89466" stroke-width="2.5"/>
<ellipse cx="35" cy="28" rx="9.5" ry="21" transform="rotate(-8 35 28)" fill="#E9D0AE" stroke="#B89466" stroke-width="2.5"/>
<ellipse cx="65" cy="28" rx="9.5" ry="21" transform="rotate(8 65 28)" fill="#E9D0AE" stroke="#B89466" stroke-width="2.5"/>
<ellipse cx="35" cy="31" rx="4.6" ry="14" transform="rotate(-8 35 31)" fill="#FFB3DA"/><ellipse cx="65" cy="31" rx="4.6" ry="14" transform="rotate(8 65 31)" fill="#FFB3DA"/>
<circle cx="50" cy="60" r="28" fill="#E9D0AE" stroke="#B89466" stroke-width="2.5"/>
<ellipse cx="50" cy="68" rx="15" ry="11" fill="#FFF3DF"/>
<ellipse cx="32" cy="68" rx="5.5" ry="3.6" fill="#FF6FB5" opacity=".55"/><ellipse cx="68" cy="68" rx="5.5" ry="3.6" fill="#FF6FB5" opacity=".55"/>
{eye(39, 56)}{eye(61, 56)}
<ellipse cx="50" cy="64" rx="4.6" ry="3.4" fill="#FF6FB5"/>
<path d="M50 67 V71 M44 73 Q50 77 50 71 Q50 77 56 73" fill="none" stroke="{INK}" stroke-width="2.2" stroke-linecap="round"/>'''

GOAT = SH + f'''
<rect x="36" y="84" width="8" height="11" rx="4" fill="#8B5A3C"/><rect x="56" y="84" width="8" height="11" rx="4" fill="#8B5A3C"/>
<ellipse cx="50" cy="82" rx="21" ry="13" fill="#F5E6CF" stroke="#CDB58F" stroke-width="2.5"/>
<path d="M38 30 C32 18 36 10 44 12 C42 18 42 24 44 30Z" fill="#8B5A3C" stroke="#6E432A" stroke-width="2" stroke-linejoin="round"/>
<path d="M62 30 C68 18 64 10 56 12 C58 18 58 24 56 30Z" fill="#8B5A3C" stroke="#6E432A" stroke-width="2" stroke-linejoin="round"/>
<ellipse cx="21" cy="52" rx="13" ry="7" transform="rotate(24 21 52)" fill="#C8996A" stroke="#A97A4C" stroke-width="2.2"/>
<ellipse cx="79" cy="52" rx="13" ry="7" transform="rotate(-24 79 52)" fill="#C8996A" stroke="#A97A4C" stroke-width="2.2"/>
<ellipse cx="50" cy="52" rx="25" ry="28" fill="#F5E6CF" stroke="#CDB58F" stroke-width="2.5"/>
<ellipse cx="50" cy="66" rx="14" ry="10" fill="#FFF3DF"/>
<ellipse cx="44" cy="63" rx="2" ry="2.6" fill="#A97A4C"/><ellipse cx="56" cy="63" rx="2" ry="2.6" fill="#A97A4C"/>
<path d="M44 70 Q50 74 56 70" fill="none" stroke="{INK}" stroke-width="2.2" stroke-linecap="round"/>
<path d="M45 76 Q50 90 55 76 Q50 80 45 76Z" fill="#C8996A" stroke="#A97A4C" stroke-width="2" stroke-linejoin="round"/>
{eye(39, 50)}{eye(61, 50)}
<ellipse cx="33" cy="60" rx="4.6" ry="3" fill="#FF6FB5" opacity=".5"/><ellipse cx="67" cy="60" rx="4.6" ry="3" fill="#FF6FB5" opacity=".5"/>'''

ANIMALS = [('chick', 'Chick', CHICK), ('lamb', 'Lamb', LAMB), ('calf', 'Calf', CALF),
           ('piglet', 'Piglet', PIGLET), ('bunny', 'Bunny', BUNNY), ('goat', 'Kid goat', GOAT)]

BELL = '''
<path d="M50 14 C30 14 22 32 22 52 C22 66 18 70 12 76 H88 C82 70 78 66 78 52 C78 32 70 14 50 14Z" fill="#FFC83D" stroke="#D99E12" stroke-width="4" stroke-linejoin="round"/>
<path d="M32 36 C32 28 38 22 44 20" fill="none" stroke="#FFF1B0" stroke-width="5" stroke-linecap="round"/>
<circle cx="50" cy="12" r="6" fill="#FFC83D" stroke="#D99E12" stroke-width="3.5"/>
<path d="M12 76 H88" stroke="#D99E12" stroke-width="5" stroke-linecap="round"/>
<ellipse cx="50" cy="84" rx="9" ry="8" fill="#D99E12"/>'''

symbols = f'''<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<symbol id="hog-n" viewBox="0 0 180 150">{hedgehog(False)}</symbol>
<symbol id="hog-h" viewBox="0 0 180 150">{hedgehog(True)}</symbol>
<symbol id="duck-n" viewBox="0 0 150 160">{duck(False)}</symbol>
<symbol id="duck-h" viewBox="0 0 150 160">{duck(True)}</symbol>
<symbol id="mouse-n" viewBox="0 0 150 160">{mouse(False)}</symbol>
<symbol id="mouse-h" viewBox="0 0 150 160">{mouse(True)}</symbol>
<symbol id="apple" viewBox="0 0 104 104">{APPLE}</symbol>
<symbol id="pebble-a" viewBox="0 0 104 104">{PEBBLE_A}</symbol>
<symbol id="pebble-b" viewBox="0 0 104 104">{PEBBLE_B}</symbol>
<symbol id="acorn" viewBox="0 0 104 104">{ACORN}</symbol>
{''.join(f'<symbol id="a-{k}" viewBox="0 0 100 100">{art}</symbol>' for k, _, art in ANIMALS)}
<symbol id="bell" viewBox="0 0 100 96">{BELL}</symbol>
<symbol id="hazel-sym" viewBox="0 0 240 262">{owl_inner}</symbol>
</defs></svg>'''


# ------------------------------------------------------------ scene pieces
SIZE = 104  # object size in scene px


def defs_scene():
    return '''<defs>
<linearGradient id="sky" gradientUnits="userSpaceOnUse" x1="0" y1="-20" x2="0" y2="200"><stop offset="0" stop-color="#BFE9FA"/><stop offset="1" stop-color="#FFF7E8"/></linearGradient>
<linearGradient id="grass" gradientUnits="userSpaceOnUse" x1="0" y1="120" x2="0" y2="620"><stop offset="0" stop-color="#9CEBC1"/><stop offset="1" stop-color="#5CCB93"/></linearGradient>
<linearGradient id="wood" gradientUnits="userSpaceOnUse" x1="0" y1="300" x2="0" y2="520"><stop offset="0" stop-color="#D9AA77"/><stop offset="1" stop-color="#B98254"/></linearGradient>
<linearGradient id="path" gradientUnits="userSpaceOnUse" x1="0" y1="400" x2="0" y2="600"><stop offset="0" stop-color="#F7E6C2"/><stop offset="1" stop-color="#EBCF9B"/></linearGradient>
<pattern id="gingham" patternUnits="userSpaceOnUse" width="48" height="48" x="0" y="0">
<rect width="48" height="48" fill="#FFFFFF"/><rect width="24" height="48" fill="#BFE6E1" opacity=".8"/><rect width="48" height="24" fill="#BFE6E1" opacity=".8"/></pattern>
<filter id="soft" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="6" stdDeviation="7" flood-color="#2b3a67" flood-opacity=".18"/></filter>
</defs>'''


def backdrop(horizon=130):
    return f'''<rect x="-60" y="-40" width="1080" height="700" fill="url(#sky)"/>
<circle cx="730" cy="86" r="30" fill="#FFC83D" opacity=".9"/><circle cx="730" cy="86" r="42" fill="#FFC83D" opacity=".18"/>
<g fill="#fff" opacity=".9"><ellipse cx="520" cy="84" rx="46" ry="14"/><ellipse cx="550" cy="73" rx="28" ry="16"/><ellipse cx="900" cy="124" rx="40" ry="11"/></g>
<path d="M-60 {horizon + 20} C80 {horizon - 24} 200 {horizon - 20} 330 {horizon + 8} C470 {horizon + 30} 600 {horizon - 14} 740 {horizon - 4} C860 {horizon + 6} 940 {horizon - 18} 1020 {horizon - 2} V660 H-60Z" fill="#BDEFD3"/>
<path d="M-60 {horizon + 54} C100 {horizon + 20} 300 {horizon + 30} 480 {horizon + 44} C700 {horizon + 62} 840 {horizon + 30} 1020 {horizon + 40} V660 H-60Z" fill="url(#grass)"/>
<g fill="#7FD9A8"><circle cx="40" cy="{horizon + 8}" r="26"/><circle cx="76" cy="{horizon + 20}" r="20"/><circle cx="920" cy="{horizon + 10}" r="28"/><circle cx="890" cy="{horizon + 22}" r="18"/></g>'''


def hud(filled, total=6):
    x0 = 480 - (total - 1) * 11
    dots = ''.join(
        f'<circle cx="{x0 + i * 22}" cy="42" r="6.5" fill="{"#2FCB86" if i < filled else "#fff"}" stroke="#0F857D" stroke-width="2.2" opacity="{1 if i < filled else .85}"/>'
        for i in range(total))
    return f'''<g class="fred">
<g><rect x="24" y="22" width="124" height="56" rx="28" fill="#0A625C"/><rect x="24" y="16" width="124" height="56" rx="28" fill="#0F857D"/><text x="86" y="52" text-anchor="middle" fill="#fff" font-size="24" font-weight="600">&#8249; Back</text></g>
{dots}
<g><circle cx="900" cy="46" r="30" fill="#fff" filter="url(#soft)"/><path d="M886 40 h8 l11 -8 v30 l-11 -8 h-8z" fill="#0F857D"/><path d="M912 38 q7 9 0 18" stroke="#0F857D" stroke-width="3.6" fill="none" stroke-linecap="round"/></g></g>'''


def blanket(top=(352, 902, 168), bottom=(312, 944, 470), shadow=True):
    (tl, tr, ty), (bl, br, by) = top, bottom
    f = ' filter="url(#soft)"' if shadow else ''
    return (f'<g{f}><path d="M{tl} {ty} L{tr} {ty} L{br} {by} L{bl} {by}Z" fill="url(#gingham)" stroke="#FFFFFF" stroke-width="12" stroke-linejoin="round"/></g>'
            f'<path d="M{tl} {ty} L{tr} {ty} L{br} {by} L{bl} {by}Z" fill="none" stroke="#9FD6D0" stroke-width="3" stroke-linejoin="round"/>')


def hazel_helper(x=800, y=36, w=62):
    h = w * 262 / 240
    return (f'<g filter="url(#soft)"><rect x="{x - 6}" y="{y + h - 8}" width="{w + 12}" height="22" rx="11" fill="#C8996A"/>'
            f'<rect x="{x - 6}" y="{y + h - 8}" width="{w + 12}" height="9" rx="4.5" fill="#E6C9A0"/></g>'
            f'<use href="#hazel-sym" x="{x}" y="{y}" width="{w}" height="{h:.0f}"/>')


def strip_parade(animals, x=30, y=500, w=900, h=84, label=True):
    out = (f'<g filter="url(#soft)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="26" fill="#FFF1D6" stroke="#E6BE8D" stroke-width="3"/></g>')
    if label:
        out += f'<text x="{x + 28}" y="{y + 50}" class="fred" font-size="20" font-weight="600" fill="#0F857D">My parade</text>'
    for i, k in enumerate(animals):
        ax = x + 190 + i * 84
        out += f'<g class="march" style="animation-delay:{i * .35}s"><use href="#a-{k}" x="{ax}" y="{y + 8}" width="68" height="68"/></g>'
    return out


def bubble(x, y, w, h, tail_x, inner):
    return (f'<g filter="url(#soft)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="32" fill="#fff"/>'
            f'<path d="M{tail_x - 16} {y + h - 2} l10 32 l22 -32Z" fill="#fff"/></g>{inner}')


def order_bubble(x, y, kind_sym, word, tail_x):
    w = 268
    inner = (f'<g class="fred" font-weight="600" fill="{INK}"><text x="{x + 134}" y="{y + 42}" text-anchor="middle" font-size="24">Count the</text>'
             f'<use href="#{kind_sym}" x="{x + 20}" y="{y + 52}" width="64" height="64"/>'
             f'<text x="{x + 92}" y="{y + 98}" font-size="34" font-weight="700" fill="#0F857D">{word}</text></g>')
    return bubble(x, y, w, 132, tail_x, inner)


def badge(cx, cy, n, cls='pop'):
    return (f'<g class="{cls}" filter="url(#soft)"><circle cx="{cx}" cy="{cy}" r="42" fill="#FFC83D" stroke="#fff" stroke-width="6"/>'
            f'<text x="{cx}" y="{cy + 21}" text-anchor="middle" class="fred" font-size="60" font-weight="700" fill="{INK}">{n}</text></g>')


def ring(cx, cy, cls=''):
    return (f'<ellipse class="{cls}" cx="{cx}" cy="{cy + 44}" rx="56" ry="15" fill="#FFE7A3" fill-opacity=".6" stroke="#F5A623" stroke-width="6"/>')


def obj(sym, cx, cy, state='idle', rot=0, size=SIZE):
    """returns (behind_layer, object_layer). state: idle, counted, hop, glow"""
    s = size / 2
    u = f'<use href="#{sym}" x="{cx - s}" y="{cy - s}" width="{size}" height="{size}"/>'
    rt = f' transform="rotate({rot} {cx} {cy})"' if rot else ''
    if state == 'idle':
        return '', f'<g{rt}>{u}</g>'
    if state == 'counted':
        return ring(cx, cy), f'<g{rt}>{u}</g>'
    if state == 'hop':
        return ring(cx, cy), (f'<ellipse cx="{cx}" cy="{cy + 48}" rx="30" ry="6" fill="#2b3a67" opacity=".22"/>'
                              f'<g transform="translate(0 -16)"><g class="hop"{rt.replace("rotate(", "rotate(")}>{u}</g></g>')
    if state == 'glow':
        return (f'<circle class="glow" cx="{cx}" cy="{cy}" r="70" fill="#FFE27A" opacity=".55"/>'), (
            f'<g{rt}>{u}</g>' + f'<g class="twinkle">{sparkle_star(cx + 50, cy - 46, 11)}{sparkle_star(cx - 54, cy - 34, 8, "#fff")}</g>')
    if state == 'light':
        return (f'<circle class="glow" cx="{cx}" cy="{cy - 6}" r="72" fill="#FFE27A" opacity=".6"/>' + ring(cx, cy)), (
            f'<ellipse cx="{cx}" cy="{cy + 48}" rx="30" ry="6" fill="#2b3a67" opacity=".22"/><g transform="translate(0 -14)"><g class="lit"{rt}>{u}</g></g>')
    raise ValueError(state)


def place(items):
    behind, front = '', ''
    for it in items:
        b, f = obj(*it)
        behind += b
        front += f
    return behind, front


def host(sym, x, y, w, cls='bob', delay=0):
    vb = {'hog': (180, 150), 'duck': (150, 160), 'mouse': (150, 160)}[sym.split('-')[0]]
    h = w * vb[1] / vb[0]
    return f'<g class="{cls}" style="animation-delay:{delay}s"><use href="#{sym}" x="{x}" y="{y}" width="{w}" height="{h:.0f}"/></g>'


def done_bell(cx, cy, wobble=False, label=True):
    cls = 'wob' if wobble else ''
    return (f'<g filter="url(#soft)"><circle cx="{cx}" cy="{cy + 8}" r="52" fill="#D99E12"/><circle cx="{cx}" cy="{cy}" r="52" fill="#FFF7E8" stroke="#FFC83D" stroke-width="6"/></g>'
            f'<g class="{cls}"><use href="#bell" x="{cx - 34}" y="{cy - 34}" width="68" height="65"/></g>')


def choice(x, y, n, state='idle'):
    fill = {'idle': '#fff', 'dim': '#F1EADC'}[state]
    tcol = {'idle': INK, 'dim': '#BDB19D'}[state]
    edge = {'idle': '#E6BE8D', 'dim': '#E4DAC5'}[state]
    return (f'<g class="fred"><rect x="{x}" y="{y + 8}" width="132" height="104" rx="24" fill="{edge}"/>'
            f'<rect x="{x}" y="{y}" width="132" height="104" rx="24" fill="{fill}" stroke="{edge}" stroke-width="4"/>'
            f'<text x="{x + 66}" y="{y + 76}" text-anchor="middle" font-size="76" font-weight="700" fill="{tcol}">{n}</text></g>')


def scene(label, body, filled=0, clsname='scene', horizon=130, total=6):
    return (f'<svg viewBox="0 0 960 600" class="{clsname}" role="img" aria-label="{label}">{defs_scene()}'
            f'{backdrop(horizon)}{body}{hud(filled, total)}</svg>')


# ------------------------------------------------------------ scene builders
def sceneL1():
    items = [('apple', 372 + i * 118, 312, 'counted') for i in range(2)] + [('apple', 372 + 2 * 118, 312, 'hop')] + \
            [('apple', 372 + i * 118, 312, 'idle') for i in (3, 4)]
    b, f = place(items)
    tops = badge(372 + 2 * 118, 312 - 16, 3)
    body = (blanket() + b + f + tops + order_bubble(40, 92, 'apple', 'apples', 130) + host('hog-n', 28, 256, 176) +
            hazel_helper() + strip_parade(['chick', 'lamb', 'calf']))
    return scene('Level 1: the hedgehog asks the child to count five apples in a neat row. Three have been tapped.', body, 1)


def sceneL2():
    rows = []
    items = []
    for r, cy in enumerate((246, 358)):
        for i in range(5):
            idx = r * 5 + i
            st = 'hop' if idx == 6 else ('counted' if idx < 6 else 'idle')
            items.append(('pebble-a' if (idx % 2 == 0) else 'pebble-b', 372 + i * 118, cy, st))
    b, f = place(items)
    tops = badge(372 + 1 * 118, 358 - 16, 7)
    body = (blanket(top=(352, 902, 160), bottom=(312, 944, 450)) + b + f + tops +
            order_bubble(40, 92, 'pebble-a', 'pebbles', 130) + host('duck-n', 36, 262, 160) +
            hazel_helper() + strip_parade(['chick', 'lamb', 'calf', 'piglet']))
    return scene('Level 2: the duck asks for pebbles, two neat rows of five. Seven have been tapped.', body, 2)


SCATTER = [(392, 232, -6), (552, 206, 8), (716, 262, -4), (868, 222, 5), (430, 378, 7), (596, 344, -9), (740, 396, 3), (872, 356, -6)]


def sceneL3():
    items = [('acorn', x, y, 'idle', r) for x, y, r in SCATTER]
    b, f = place(items)
    body = (blanket(top=(352, 902, 160), bottom=(312, 944, 450)) + b + f +
            order_bubble(40, 92, 'acorn', 'acorns', 130) + host('mouse-n', 36, 262, 160) +
            done_bell(262, 424) + hazel_helper() + strip_parade(['chick', 'lamb', 'calf', 'piglet', 'bunny']))
    return scene('Level 3: the mouse asks for acorns scattered on the blanket with a Done bell.', body, 3)


def sceneBell():
    states = ['counted', 'counted', 'counted', 'glow', 'counted', 'glow', 'counted', 'counted']
    states[2] = 'counted'
    items = [('acorn', x, y, states[i], r) for i, (x, y, r) in enumerate(SCATTER)]
    # nothing is mid-hop: the last count has finished, so no badge. Two acorns still uncounted.
    b, f = place(items)
    bubble_txt = bubble(40, 92, 268, 104, 130,
                        f'<g class="fred" text-anchor="middle" font-weight="600" fill="{INK}"><text x="174" y="136" font-size="26">Did we count</text><text x="174" y="170" font-size="26">them all?</text></g>')
    body = (blanket(top=(352, 902, 160), bottom=(312, 944, 450)) + b + f + bubble_txt + host('mouse-n', 44, 270, 150) +
            done_bell(262, 424, True) + hazel_helper() + strip_parade(['chick', 'lamb', 'calf', 'piglet', 'bunny']))
    return scene('Done bell: six acorns are counted, two still twinkle, the bell wobbles.', body, 3)


def sceneMany(dim=False):
    items = [('apple', 372 + i * 118, 290, 'light' if (dim and i == 2) else 'counted') for i in range(5)]
    b, f = place(items)
    if dim:
        bub = bubble(40, 92, 268, 104, 130,
                     f'<g class="fred" text-anchor="middle" font-weight="600" fill="{INK}"><text x="174" y="152" font-size="30" font-weight="700" fill="#0F857D">Count with me!</text></g>')
        ch = choice(408, 468, 4, 'dim') + choice(562, 468, 5) + choice(716, 468, 6)
        hz = host('hog-n', 28, 256, 176, cls='tilt')
    else:
        bub = bubble(40, 92, 268, 132, 130,
                     f'<g class="fred" font-weight="600" fill="{INK}"><text x="174" y="134" text-anchor="middle" font-size="24">How many</text>'
                     f'<use href="#apple" x="52" y="142" width="64" height="64"/><text x="128" y="188" font-size="34" font-weight="700" fill="#0F857D">apples?</text></g>')
        ch = choice(408, 468, 4) + choice(562, 468, 5) + choice(716, 468, 6)
        hz = host('hog-n', 28, 256, 176)
    body = blanket(top=(352, 902, 150), bottom=(312, 944, 440)) + b + f + bub + hz + hazel_helper() + ch
    lab = 'How many step: one choice dimmed, the apples light one by one' if dim else 'How many step: three big number choices, the hedgehog waits'
    return scene(lab, body, 1)


def sceneL4():
    basket_apples = ''.join(
        f'<use href="#apple" x="{x}" y="{y}" width="78" height="78" transform="rotate({r} {x + 39} {y + 39})"/>'
        for x, y, r in [(724, 300, -8), (772, 292, 8), (746, 262, 2), (792, 256, -10)])
    basket = f'''<g>{basket_apples}
<path d="M708 362 H900 L880 440 C876 452 868 456 856 456 H752 C740 456 732 452 728 440Z" fill="#D9A25F" stroke="#A5703F" stroke-width="3.5" stroke-linejoin="round"/>
<g stroke="#A5703F" stroke-width="3" opacity=".55" stroke-linecap="round"><path d="M718 386 H890"/><path d="M724 412 H884"/><path d="M766 366 V454"/><path d="M804 366 V456"/><path d="M842 366 V454"/></g>
<rect x="700" y="352" width="208" height="20" rx="10" fill="#E9B979" stroke="#A5703F" stroke-width="3.5"/></g>'''
    bdg = badge(884, 352, 4)
    # crate of apples: back wall, two heaped rows, front wall covering the apple bottoms
    back_row = ''.join(f'<use href="#apple" x="{x}" y="{y}" width="104" height="104" transform="rotate({r} {x + 52} {y + 52})"/>'
                       for x, y, r in [(372, 252, -5), (506, 250, 4)])
    front_row = ''.join(f'<use href="#apple" x="{x}" y="{y}" width="104" height="104" transform="rotate({r} {x + 52} {y + 52})"/>'
                        for x, y, r in [(330, 282, -3), (440, 288, 3), (550, 282, -2)])
    crate = f"""<rect x="322" y="330" width="344" height="60" rx="10" fill="#9A6A42"/>
{back_row}{front_row}
<g filter="url(#soft)"><rect x="318" y="372" width="352" height="96" rx="14" fill="url(#wood)" stroke="#A5703F" stroke-width="3"/>
<g stroke="#A5703F" stroke-width="2.5" opacity=".45"><path d="M330 408 H658"/><path d="M330 440 H658"/></g>
<rect x="312" y="360" width="364" height="26" rx="13" fill="#E6BE8D" stroke="#A5703F" stroke-width="3"/></g>"""
    drag = (f'<g class="lift"><ellipse cx="696" cy="300" rx="30" ry="7" fill="#2b3a67" opacity=".22"/>'
            f'<use href="#apple" x="644" y="172" width="104" height="104" transform="rotate(-8 696 224)"/></g>')
    bub = bubble(40, 92, 268, 132, 130,
                 f'<g class="fred" font-weight="600" fill="{INK}"><text x="174" y="134" text-anchor="middle" font-size="24">Give me</text>'
                 f'<text x="124" y="198" text-anchor="middle" font-size="66" font-weight="700" fill="#0F857D">6</text>'
                 f'<use href="#apple" x="150" y="140" width="68" height="68"/></g>')
    body = (blanket(top=(352, 902, 150), bottom=(312, 944, 470)) + crate + basket + bdg + drag + bub + host('hog-n', 28, 256, 176) +
            done_bell(262, 424) + hazel_helper() + strip_parade(['chick', 'lamb', 'calf', 'piglet']))
    return scene('Level 4: give me six apples. Drag apples from the crate into the basket, then ring the Done bell.', body, 4)


def sceneParade():
    bunting = ''
    cols = ['#0F857D', '#FFC83D', '#FF6FB5', '#2FB5EC']
    for i in range(14):
        x = 40 + i * 64
        yy = 118 + 12 * math.sin(i / 13 * math.pi)
        bunting += f'<path d="M{x} {yy:.0f} L{x + 38} {yy:.0f} L{x + 19} {yy + 38:.0f}Z" fill="{cols[i % 4]}" stroke="#fff" stroke-width="3" stroke-linejoin="round"/>'
    bunting = f'<path d="M20 112 Q480 168 940 112" fill="none" stroke="#C8996A" stroke-width="4" stroke-linecap="round"/>' + bunting
    fence = ''.join(f'<rect x="{40 + i * 52}" y="250" width="30" height="86" rx="10" fill="#fff" stroke="#E6D9C0" stroke-width="3"/>' for i in range(18))
    fence = f'<g opacity=".95">{fence}<rect x="20" y="272" width="930" height="12" rx="6" fill="#fff" stroke="#E6D9C0" stroke-width="3"/><rect x="20" y="304" width="930" height="12" rx="6" fill="#fff" stroke="#E6D9C0" stroke-width="3"/></g>'
    path = '<path d="M-60 430 C120 400 360 410 560 428 C760 446 880 424 1020 410 V560 C860 580 700 572 520 574 C320 576 140 586 -60 570Z" fill="url(#path)"/>'
    path += '<path d="M-20 548 C160 536 360 540 520 546 C700 552 860 544 980 538" fill="none" stroke="#E2C58E" stroke-width="4" stroke-dasharray="2 20" stroke-linecap="round"/>'
    crowd = ''
    xs = [215, 365, 515, 665]
    for i, (k, _, _) in enumerate(ANIMALS[:4]):
        crowd += f'<g class="march" style="animation-delay:{i * .3}s"><use href="#a-{k}" x="{xs[i]}" y="372" width="146" height="146"/></g>'
    # arriving animal: hopping in from the right, trail dots, burst
    arrive = ('<g class="arrive"><use href="#a-bunny" x="800" y="340" width="146" height="146"/></g>'
              '<g fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" stroke-dasharray="1 14" opacity=".9"><path d="M958 300 Q900 250 860 334"/></g>'
              f'<g class="twinkle">{sparkle_star(786, 350, 14)}{sparkle_star(930, 338, 12, "#FF6FB5")}{sparkle_star(850, 322, 10, "#fff")}{sparkle_star(790, 420, 9, "#2FB5EC")}</g>')
    bub = bubble(40, 186, 200, 106, 108,
                 f'<g class="fred" font-weight="700" fill="#0F857D"><text x="96" y="262" text-anchor="middle" font-size="72">5</text></g>'
                 f'<use href="#apple" x="132" y="214" width="64" height="64"/>')
    body = (path + fence + bunting + bub + host('hog-h', 24, 330, 160, cls='hop2') + crowd + arrive +
            f'<g filter="url(#soft)"><rect x="20" y="326" width="0" height="0"/></g>' + hazel_helper())
    return scene('Parade: four baby animals march along the path and a fifth, the bunny, hops in. The hedgehog cheers from the grass.', body, 5, horizon=150)


# ------------------------------------------------------------ small cards
def card_svg(w, h, inner, label, scale=1.0, cls='stage'):
    return (f'<svg viewBox="0 0 {w} {h}" width="{w * scale:.0f}" height="{h * scale:.0f}" class="{cls}" role="img" aria-label="{label}">'
            f'<defs><filter id="softc" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="6" stdDeviation="7" flood-color="#2b3a67" flood-opacity=".18"/></filter></defs>{inner}</svg>')


def badge_c(cx, cy, n, cls='pop'):
    return (f'<g class="{cls}" filter="url(#softc)"><circle cx="{cx}" cy="{cy}" r="42" fill="#FFC83D" stroke="#fff" stroke-width="6"/>'
            f'<text x="{cx}" y="{cy + 21}" text-anchor="middle" class="fred" font-size="60" font-weight="700" fill="{INK}">{n}</text></g>')


def state_cards():
    W, H = 220, 190
    cx, cy = 110, 110
    u = f'<use href="#apple" x="{cx - 52}" y="{cy - 52}" width="104" height="104"/>'
    cards = []
    # uncounted
    cards.append(('1. Uncounted', 'Plain object. Idle. Nothing moves. 104 scene px, 65 px on a phone.',
                  f'<rect width="{W}" height="{H}" fill="url(#gingham)"/>{u}'))
    # just tapped
    cards.append(('2. Just tapped', 'Hops, ring appears, the one 84 px badge sits ON the object with a 60 px numeral. Note plays, voice says the number.',
                  f'<rect width="{W}" height="{H}" fill="url(#gingham)"/>' + ring(cx, cy) +
                  f'<ellipse cx="{cx}" cy="{cy + 48}" rx="30" ry="6" fill="#2b3a67" opacity=".22"/><g transform="translate(0 -16)"><g class="hop">{u}</g></g>' +
                  badge_c(cx, cy - 16, 4)))
    cards.append(('3. Counted', 'Badge has moved on. A warm ring stays under the object. No tick (a tick would mean "right").',
                  f'<rect width="{W}" height="{H}" fill="url(#gingham)"/>' + ring(cx, cy) + u))
    cards.append(('4. Tapped again', 'Soft click, the ring pulses once. No number, no badge, no error. The count does not change.',
                  f'<rect width="{W}" height="{H}" fill="url(#gingham)"/><ellipse class="pulse" cx="{cx}" cy="{cy + 44}" rx="56" ry="15" fill="none" stroke="#F5A623" stroke-width="5"/>' +
                  ring(cx, cy) + u))
    out = ''
    for t, d, inner in cards:
        out += (f'<figure class="cast statecard">{card_svg(W, H, inner, t, 1.0, "stage sc")}<figcaption><b>{t}</b><br>{d}</figcaption></figure>')
    return out


def cast_cards():
    items = [('hog', 'Hedgehog (main host)', 'asks for apples', 180, 150),
             ('duck', 'Duck', 'asks for pebbles', 150, 160),
             ('mouse', 'Mouse', 'asks for acorns', 150, 160)]
    out = ''
    for k, name, how, w, h in items:
        for pose, lab in (('n', 'neutral'), ('h', 'happy')):
            out += (f'<figure class="cast"><svg viewBox="0 0 {w} {h}" width="{w * 1.3:.0f}" height="{h * 1.3:.0f}" role="img" aria-label="{name}, {lab}">'
                    f'<use href="#{k}-{pose}" width="{w}" height="{h}"/></svg><figcaption><b>{name}</b><br>{lab}, {how if pose == "n" else "cheers on a solved round"}</figcaption></figure>')
    return out


def object_cards():
    items = [('apple', 'Apple', 'round, red, stem and leaf'), ('pebble-a', 'Pebble', 'flat, wide, grey blue, speckled'),
             ('acorn', 'Acorn', 'tall, pointed, cap on top')]
    out = ''
    for sym, name, d in items:
        out += (f'<figure class="cast objcard"><div class="trio">'
                f'<div><svg viewBox="0 0 104 104" width="104" height="104" class="box"><use href="#{sym}" width="104" height="104"/></svg><small>colour, 104 px</small></div>'
                f'<div><svg viewBox="0 0 104 104" width="104" height="104" class="box sil"><use href="#{sym}" width="104" height="104"/></svg><small>silhouette</small></div>'
                f'<div><svg viewBox="0 0 104 104" width="104" height="104" class="box gray"><use href="#{sym}" width="104" height="104"/></svg><small>greyscale</small></div>'
                f'</div><figcaption><b>{name}</b>: {d}</figcaption></figure>')
    return out


def animal_cards():
    out = ''
    for i, (k, name, _) in enumerate(ANIMALS):
        out += (f'<figure class="cast"><svg viewBox="0 0 100 100" width="120" height="120" role="img" aria-label="{name}"><use href="#a-{k}" width="100" height="100"/></svg>'
                f'<figcaption><b>{i + 1}. {name}</b></figcaption></figure>')
    return out


def parade_strip_demo():
    # a parade of 4 plus the next one arriving, shown as a standalone row at strip scale
    inner = ''
    inner += '<rect width="900" height="130" rx="26" fill="#FFF1D6" stroke="#E6BE8D" stroke-width="3"/>'
    for i in range(4):
        k = ANIMALS[i][0]
        inner += f'<g class="march" style="animation-delay:{i * .35}s"><use href="#a-{k}" x="{30 + i * 100}" y="30" width="86" height="86"/></g>'
    inner += '<g class="arrive2"><use href="#a-bunny" x="460" y="26" width="92" height="92"/></g>'
    inner += f'<g class="twinkle">{sparkle_star(580, 40, 12)}{sparkle_star(448, 30, 9, "#FF6FB5")}</g>'
    inner += '<path d="M660 104 Q610 70 575 100" fill="none" stroke="#C8996A" stroke-width="5" stroke-dasharray="1 12" stroke-linecap="round"/>'
    inner += f'<text x="880" y="72" text-anchor="end" class="fred" font-size="24" font-weight="600" fill="#0F857D">the next friend hops in</text>'
    return f'<svg viewBox="0 0 900 130" class="scene wide" role="img" aria-label="Parade strip with four animals and a fifth arriving"><defs></defs>{inner}</svg>'


def phone_box(inner_scene, label, ref=(0, 0)):
    # 667 x 375 viewport, scene letterboxed at 0.625 (600 x 375)
    return (f'<div class="phonewrap"><div class="phone" style="width:667px;height:375px"><div class="phone-in">{inner_scene}</div>'
            f'<div class="ref64" style="left:{ref[0]}px;top:{ref[1]}px" aria-hidden="true"><span>64 px</span></div></div><p class="cap">{label}</p></div>')


def mini_demo():
    return f'''<div class="demo" id="demo"><svg viewBox="0 0 240 200" width="240" height="200" role="img" aria-label="Tap the apple to see the hop and badge">
<defs><filter id="softd" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="6" stdDeviation="7" flood-color="#2b3a67" flood-opacity=".18"/></filter></defs>
<rect width="240" height="200" fill="url(#gingham)"/>
<ellipse class="demoring" cx="120" cy="152" rx="56" ry="15" fill="#FFE7A3" fill-opacity=".6" stroke="#F5A623" stroke-width="6"/>
<g class="demoapple"><use href="#apple" x="68" y="48" width="104" height="104"/></g>
<g class="demobadge" filter="url(#softd)"><circle cx="120" cy="92" r="42" fill="#FFC83D" stroke="#fff" stroke-width="6"/><text x="120" y="113" text-anchor="middle" class="fred" font-size="60" font-weight="700" fill="{INK}">1</text></g>
</svg>
<div class="democtl"><button id="tapbtn" type="button">Tap the apple</button>
<label><input type="checkbox" id="rmtoggle"> Pretend reduced motion</label>
<p class="small" id="demotxt">Normal: the apple hops, the badge pops in with a spring.</p></div></div>'''


css = '''
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
.chip{display:inline-block;background:#fff;border-radius:999px;padding:6px 14px;margin:4px;box-shadow:0 3px 10px rgba(43,58,103,.1);font-family:Fredoka,"Arial Rounded MT Bold",system-ui,sans-serif;font-weight:600}
.note{background:#fff;border-left:6px solid var(--teal);border-radius:12px;padding:10px 16px;max-width:70ch}
.decide{background:#fff;border:3px solid var(--teal);border-radius:24px;padding:8px 24px 18px;margin-top:20px}
.decide li{margin:8px 0}
table{border-collapse:collapse;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 14px rgba(43,58,103,.1);max-width:100%}
td,th{padding:8px 14px;text-align:left;border-bottom:1px solid #F0E6D2;font-size:15px}th{background:#E4F3F1;font-family:Fredoka,system-ui,sans-serif}
.tablewrap{overflow-x:auto;max-width:100%}
.trio{display:flex;gap:10px;justify-content:center;align-items:flex-end}.trio div{display:flex;flex-direction:column;align-items:center}.trio small{font-size:12px;margin-top:4px}
.box{border:2px dashed #C8996A;border-radius:12px;background:#fff7e8}
.sil{filter:brightness(0);background:transparent;border-color:transparent}.gray{filter:grayscale(1)}
.cap{font-size:14px;margin:6px 0 0}.small{font-size:14px}
.phonewrap{overflow-x:auto;max-width:100%;padding-bottom:6px}
.phone{position:relative;background:#3B2A20;border-radius:20px;overflow:hidden;flex:none}
.phone-in{position:absolute;left:33.5px;top:0;width:600px;height:375px}
.phone-in .scene{border-radius:0;box-shadow:none;width:600px;height:375px}
.ref64{position:absolute;width:64px;height:64px;border:3px dashed #FF6FB5;border-radius:10px;display:flex;align-items:flex-end;justify-content:center;pointer-events:none}
.ref64 span{font:700 11px/1 system-ui,sans-serif;color:#fff;background:#FF6FB5;padding:2px 5px;border-radius:6px;transform:translateY(8px)}
.demo{display:flex;flex-wrap:wrap;gap:18px;align-items:center;background:#fff;border-radius:24px;padding:14px;box-shadow:0 6px 18px rgba(43,58,103,.12);max-width:640px}
.demo svg{border-radius:16px}
.demo button{font:600 20px Fredoka,"Arial Rounded MT Bold",system-ui,sans-serif;color:#fff;background:var(--teal);border:0;border-radius:999px;padding:12px 24px;box-shadow:0 6px 0 var(--teal-dark);cursor:pointer;margin-bottom:10px;min-height:48px}
.demo button:active{transform:translateY(4px);box-shadow:0 2px 0 var(--teal-dark)}
.demo label{display:block;margin:6px 0}
.wide{border-radius:26px}
/* motion: transform and opacity only */
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
.bob{animation:bob 2.8s ease-in-out infinite}
@keyframes tilt{0%,100%{transform:rotate(0)}50%{transform:rotate(-3deg)}}
.tilt{transform-box:fill-box;transform-origin:50% 100%;animation:tilt 2.4s ease-in-out infinite}
@keyframes hop2{0%,100%{transform:translateY(0)}40%{transform:translateY(-18px)}}
.hop2{animation:hop2 1.1s var(--spring) infinite}
@keyframes hop{0%,100%{transform:translateY(0) scale(1,1)}45%{transform:translateY(-8px) scale(.97,1.04)}}
.hop{transform-box:fill-box;transform-origin:50% 100%;animation:hop 1.3s var(--spring) infinite}
@keyframes pop{0%,100%{transform:scale(1)}50%{transform:scale(1.06)}}
.pop{transform-box:fill-box;transform-origin:center;animation:pop 1.6s ease-in-out infinite}
@keyframes tw{0%,100%{opacity:.25}50%{opacity:1}}
.twinkle{animation:tw 1.5s ease-in-out infinite}
.glow{animation:tw 1.5s ease-in-out infinite}
@keyframes lift{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
.lift{animation:lift 1.6s ease-in-out infinite}
@keyframes wob{0%,100%{transform:rotate(0)}25%{transform:rotate(-9deg)}75%{transform:rotate(9deg)}}
.wob{transform-box:fill-box;transform-origin:50% 12%;animation:wob 1.2s ease-in-out infinite}
@keyframes march{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
.march{animation:march 1s ease-in-out infinite}
@keyframes pulse{0%{transform:scale(1);opacity:.9}100%{transform:scale(1.35);opacity:0}}
.pulse{transform-box:fill-box;transform-origin:center;animation:pulse 1.6s ease-out infinite}
@keyframes lit{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
.lit{animation:lit 1.4s var(--spring) infinite}
@keyframes arrive{0%,100%{transform:translateY(0)}50%{transform:translateY(-26px)}}
.arrive,.arrive2{animation:arrive 1.1s var(--spring) infinite}
/* demo */
.demoapple,.demobadge,.demoring{transform-box:fill-box;transform-origin:center}
.demobadge{opacity:0}.demoring{opacity:0}
.demo.go .demoring{animation:fadein .3s ease-out forwards}
.demo.go .demoapple{animation:dhop .5s var(--spring)}
.demo.go .demobadge{animation:bpop .45s var(--spring) forwards}
@keyframes fadein{to{opacity:1}}
@keyframes dhop{0%{transform:translateY(0)}40%{transform:translateY(-22px) scale(.97,1.04)}100%{transform:translateY(0)}}
@keyframes bpop{0%{opacity:0;transform:scale(.4)}100%{opacity:1;transform:scale(1)}}
.demo.rm.go .demoapple{animation:none}
.demo.rm.go .demobadge{animation:bfade .25s linear forwards}
@keyframes bfade{from{opacity:0}to{opacity:1}}
@media (prefers-reduced-motion:reduce){
 .bob,.tilt,.hop2,.hop,.pop,.twinkle,.glow,.lift,.wob,.march,.arrive,.arrive2,.lit{animation:none}
 .twinkle{opacity:.85}.glow{opacity:.5}.pulse{animation:none;opacity:.5}
 .demo.go .demoapple{animation:none}.demo.go .demobadge{animation:bfade .25s linear forwards}
}
@media (max-width:640px){.cast figcaption{max-width:24ch}}
'''

js = '''
(function(){
  var d=document.getElementById('demo'),b=document.getElementById('tapbtn'),c=document.getElementById('rmtoggle'),t=document.getElementById('demotxt');
  function say(){t.textContent=d.classList.contains('rm')?'Reduced motion: no hop. The badge just fades in and the ring appears. Same information.':'Normal: the apple hops, the badge pops in with a spring.';}
  b.addEventListener('click',function(){d.classList.remove('go');void d.offsetWidth;d.classList.add('go');});
  c.addEventListener('change',function(){d.classList.toggle('rm',c.checked);d.classList.remove('go');say();});
})();
'''

L1, L2, L3, LB, M1, M2, L4, PA = sceneL1(), sceneL2(), sceneL3(), sceneBell(), sceneMany(False), sceneMany(True), sceneL4(), sceneParade()

html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hedgehog Picnic art preview</title>
<style>{css}</style></head><body>{symbols}<main>
<h1>Hedgehog Picnic: art direction preview</h1>
<p>Static prototype for approval. Nothing here is the final game. It shows the cast, the counting objects, the four level layouts, the counting moment, the How many? step, the Done bell and the Parade reward, so we can agree on the art before any development.
Gentle motion only (bobbing, hop, twinkle), all transform and opacity, with a reduced-motion version. It follows the v3 style guide: cream and teal, Fredoka numbers, rounded shapes, soft tinted shadows, no red in feedback. This page uses a rounded system font where the real game self-hosts Fredoka, so numeral widths are close but not exact.</p>

<h2>1. The cast: hedgehog, duck, mouse</h2>
<p>Hedgehog is the host and asks for apples. Duck asks for pebbles. Mouse asks for acorns. Each has a neutral pose (waiting, gentle bob) and a happy pose (closed smiling eyes, open mouth, arms or wings up) that plays when a round is solved. Same chibi proportions as Hazel: big head, big eyes, round cheeks, soft outlines in a darker shade of the body colour.</p>
<div class="row">{cast_cards()}</div>

<h2>2. The countable objects</h2>
<p>Drawn at 104 scene px, which is 65 px on a 667 x 375 phone, just above the 64 px hit target. The three silhouettes differ on purpose: the apple is round with a leaf, the pebble is flat and wide, the acorn is tall and pointed. The silhouette and greyscale versions are there to prove they still read for a child who cannot tell the colours apart.</p>
<div class="row">{object_cards()}</div>

<h2>3. Level layouts</h2>
<h3>Level 1: one neat row of 5 (hedgehog and apples)</h3>
<p>Count phase, three apples tapped. The order bubble has a picture and two short words, "Count the apples". The gingham picnic blanket is the table: pale so the objects pop. Hazel sits on a stump in the corner as the hint helper (tap her for a hint). The bottom shelf shows the parade so far.</p>
{L1}
<h3>Level 2: two neat rows, 5 + 5 (duck and pebbles)</h3>
<p>Rows are 112 scene px apart and objects are 118 px apart across, so the badge and rings never reach a neighbour. Seven pebbles are counted, the badge sits on number 7.</p>
{L2}
<h3>Level 3: a scatter of 8 (mouse and acorns)</h3>
<p>Eight acorns thrown loosely across the blanket with slight tilts. It is a scatter, not a heap: every centre is at least 130 scene px from every other, and objects are 104 px, so nothing touches or hides another. Skipping one is easy, which is the point. A Done bell (104 px) waits beside the mouse.</p>
{L3}

<h2>4. The counting moment</h2>
<p>One badge for the whole round, always on top, never blocking a tap. It is <b>84 scene px</b> across with a <b>60 px</b> numeral (52 px and 38 px on a phone), sun yellow with a white rim. It sits centred on the object that was just tapped. A tapped object hops, then keeps a warm ring under it. Counting is not right or wrong, so there is never a tick.</p>
<div class="row states">{state_cards()}</div>
<p class="note">Muted players still get everything: the badge pop is the visual twin of the count note and the spoken number, and the ring is the visual twin of "that one is done".</p>

<h2>5. The "How many?" step</h2>
<p>When the last object is counted, the badge fades, the friend asks, and three big choices bounce into the shelf slot where the parade was. Each choice is 132 x 104 scene px (82 x 65 on a phone) with a 76 px numeral. The friend waits with a slow bob.</p>
{M1}
<p>After a first wrong choice that choice dims (it stays visible, not tappable). No red, no X, no buzzer. The friend tilts their head, and the apples light up one after another, each lifting a little, in the order the child counted. This is a silent count-along. Here the third apple is mid-light.</p>
{M2}

<h2>6. Level 3 Done bell and "find the rest"</h2>
<p>Level 3 has no automatic finish: the child rings the bell when they think they have counted everything. If objects are left, the uncounted ones twinkle (soft yellow glow plus sparkles, opacity only), the bell gives a little wobble and the mouse asks "Did we count them all?". Here six acorns are counted and two still twinkle.</p>
{LB}

<h2>7. Level 4: "give me N"</h2>
<p>Uses the existing drag-and-drop fill mechanic. The bubble shows the number and a picture, "Give me 6". The crate holds the apples (each 104 px, big enough to grab), the basket on the right shows a count badge, one apple is lifting mid-drag, and the Done bell (104 px) appears after the first apple goes in. The numeral stays on screen because it is the request, not the answer.</p>
{L4}

<h2>8. Reward: Parade of animals</h2>
<p>Six baby farm animals, one new animal joins the parade per solved round, in a fixed order that repeats. Hedgehog, duck and mouse are never in the parade: they are the hosts, the animals are the reward. The six, in cycle order:</p>
<div class="row">{animal_cards()}</div>
<h3>A parade of 4 and the fifth arriving (the shelf strip)</h3>
<p>This is how the parade looks on the shelf during play, and the arrival of the next animal (bunny) at the right end.</p>
{parade_strip_demo()}
<h3>The parade on the end screen</h3>
<p>Four animals are already marching along the path, the bunny hops in, bunting and sparkles celebrate and the hedgehog cheers from the grass.</p>
{PA}

<h2>9. Phone size check (667 x 375)</h2>
<p>A 667 x 375 landscape phone shows the 960 x 600 scene at 0.625 scale (600 x 375, with dark bars at the sides). The dashed pink square is a real 64 px square for comparison. Real pixel sizes on this phone:</p>
<div class="tablewrap"><table><tr><th>Element</th><th>Scene px</th><th>Phone px</th></tr>
<tr><td>Counting object (hit target)</td><td>104 x 104</td><td>65 x 65</td></tr>
<tr><td>Number badge</td><td>84 across</td><td>52.5</td></tr>
<tr><td>Badge numeral</td><td>60</td><td>37.5</td></tr>
<tr><td>How many? choice</td><td>132 x 104</td><td>82.5 x 65</td></tr>
<tr><td>Choice numeral</td><td>76</td><td>47.5</td></tr>
<tr><td>Done bell</td><td>104 across</td><td>65</td></tr>
<tr><td>Spacing between neat-row centres</td><td>118 across, 112 down</td><td>74 across, 70 down</td></tr>
<tr><td>Scatter, closest centres</td><td>130</td><td>81</td></tr>
<tr><td>Parade animal on the shelf</td><td>68</td><td>42.5</td></tr>
<tr><td>Back button</td><td>124 x 56</td><td>77.5 x 35</td></tr>
<tr><td>Audio toggle</td><td>60 across</td><td>37.5</td></tr></table></div>
<p class="note">The Back button and audio toggle are only 35 and 37.5 px tall on this phone. The game targets are fine, but these two should get an invisible hit area padded out to at least 48 px when built (see the decisions below).</p>
<h3>Level 3 scatter on a phone</h3>
{phone_box(sceneL3(), 'Count phase, level 3. The pink square is a real 64 px. The acorn hit area (65 px) is a touch bigger than it; the drawn acorn inside it is about 52 px, so spacing, not art size, keeps taps apart.', (246.5, 116.8))}
<h3>How many? on a phone</h3>
{phone_box(sceneMany(False), 'The three choices are 82 x 65 px each, all bigger than the pink 64 px square.', (394, 293))}

<h2>10. Reduced motion and muted play</h2>
<p><b>Reduced motion.</b> Every motion on this page is transform or opacity only. When the device asks for reduced motion, the hop, bob, bell wobble, parade march and sparkle pulse stop. The state still shows: a counted object gets its ring instantly, the badge simply fades in (no spring), a twinkle is a steady soft glow, the animal appears in the parade with a fade. Try it:</p>
{mini_demo()}
<h3>Every sound has a visual twin</h3>
<div class="tablewrap"><table><tr><th>Sound</th><th>Visual twin (shows even when muted)</th></tr>
<tr><td>Count note and spoken number on a tap</td><td>Badge with the number on the object, ring under it</td></tr>
<tr><td>Soft click on a re-tap</td><td>Ring pulses once</td></tr>
<tr><td>Spoken "Count the apples"</td><td>Bubble with the picture and the two words</td></tr>
<tr><td>Spoken "How many?"</td><td>Three big number choices appear</td></tr>
<tr><td>Count-along notes after a wrong choice</td><td>Apples lift and light one after another, wrong choice dims</td></tr>
<tr><td>Done bell sound</td><td>Bell wobble, uncounted objects twinkle</td></tr>
<tr><td>Parade fanfare</td><td>New animal hops in with sparkles</td></tr></table></div>

<h2>11. Decisions for the owner</h2>
<div class="decide"><ul>
<li><b>Palette.</b> The page uses the v3 tokens. Two additions to approve: a soft warm grey-lilac for the mouse (#D9D2E3), and a pale teal gingham for the blanket (#BFE6E1 on white). Apples are red (#EF5B45). The style guide bans red in feedback, not in objects, and the ladybug already set that precedent. Say if you want green apples instead.</li>
<li><b>Cast likeness.</b> Hedgehog has a cream face and a layered brown spiky back. Duck is sun yellow with a sky blue bow (and the chick is a warm peach so it never looks like the duck). Mouse is lilac grey with big pink ears. All three share Hazel's chibi look. Hedgehog brown is close to Hazel's brown, so Hazel stays on her stump in the corner as a different shape.</li>
<li><b>Parade species.</b> Chick, lamb, calf, piglet, bunny, kid goat. Each has a different silhouette: round ball, cloud wool, horns and spots, floppy pink ears, tall ears, small horns and beard. The chick is peach with a red beak so it cannot be mistaken for the sun yellow duck.</li>
<li><b>Front view.</b> All animals face the viewer (like Hazel) so they march in place with a bob. A side view would need new art per animal.</li>
<li><b>Crate stock.</b> The level 4 crate shows only five apples. The real stock depends on the fill mechanic. If it is bigger than what fits, the crate needs a heaped look or the apples need to refill.</li>
<li><b>Words in bubbles.</b> "Count the apples", "How many apples?", "Count with me!", "Did we count them all?" and "Give me 6". All short, all spoken as well.</li>
<li><b>Small buttons.</b> Back and audio need a padded hit area (about 48 px) when built.</li>
</ul></div>
</main><script>{js}</script></body></html>'''

open('index.html', 'w').write(html)
print(len(html))
