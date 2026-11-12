import re
owl=open('../mascot/owl.svg').read()
owl_inner=re.sub(r'^<svg[^>]*>','',owl.strip()); owl_inner=owl_inner[:owl_inner.rindex('</svg>')]
owl_inner=re.sub(r'<title>.*?</title>','',owl_inner,flags=re.S)
def hazel(x,y,w): 
    h=w*262/240
    return f'<svg x="{x}" y="{y}" width="{w}" height="{h:.0f}" viewBox="0 0 240 262" class="hazel">{owl_inner}</svg>'

defs='''
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<symbol id="daisy" viewBox="0 0 60 90">
  <path d="M30 40 C30 60 28 75 30 88" stroke="#2FA866" stroke-width="5" fill="none" stroke-linecap="round"/>
  <path d="M30 70 C42 64 50 66 52 58 C44 56 34 60 30 70Z" fill="#46C47E"/>
  <g fill="#fff" stroke="#E4DCCB" stroke-width="1.5">
    <ellipse cx="30" cy="14" rx="7" ry="13"/><ellipse cx="30" cy="14" rx="7" ry="13" transform="rotate(45 30 30)"/>
    <ellipse cx="30" cy="14" rx="7" ry="13" transform="rotate(90 30 30)"/><ellipse cx="30" cy="14" rx="7" ry="13" transform="rotate(135 30 30)"/>
    <ellipse cx="30" cy="14" rx="7" ry="13" transform="rotate(180 30 30)"/><ellipse cx="30" cy="14" rx="7" ry="13" transform="rotate(225 30 30)"/>
    <ellipse cx="30" cy="14" rx="7" ry="13" transform="rotate(270 30 30)"/><ellipse cx="30" cy="14" rx="7" ry="13" transform="rotate(315 30 30)"/>
  </g>
  <circle cx="30" cy="30" r="9" fill="#FFC83D" stroke="#E0A91C" stroke-width="1.5"/>
  <circle cx="27" cy="27" r="2.4" fill="#FFE9A0"/>
</symbol>
<symbol id="tulip" viewBox="0 0 60 90">
  <path d="M30 38 C30 60 31 75 30 88" stroke="#2FA866" stroke-width="5" fill="none" stroke-linecap="round"/>
  <path d="M30 80 C14 76 8 62 10 52 C20 58 28 66 30 80Z" fill="#46C47E"/>
  <path d="M12 14 C12 36 20 46 30 46 C40 46 48 36 48 14 L39 22 L30 8 L21 22Z" fill="#FF6FB5" stroke="#E04C98" stroke-width="2" stroke-linejoin="round"/>
  <path d="M30 8 L21 22 C24 34 26 40 30 46 C34 40 36 34 39 22Z" fill="#FF92C8"/>
  <ellipse cx="20" cy="30" rx="3" ry="6" fill="#FFB3DA" opacity=".8"/>
</symbol>
<symbol id="ladybug" viewBox="0 0 120 110">
  <ellipse cx="60" cy="104" rx="38" ry="5" fill="#2b3a67" opacity=".15"/>
  <path d="M38 96 l-6 10 M60 98 l0 10 M82 96 l6 10" stroke="#3B2A20" stroke-width="5" stroke-linecap="round"/>
  <path d="M18 88 C14 44 36 22 60 22 C84 22 106 44 102 88 C92 98 28 98 18 88Z" fill="#E8503A" stroke="#B8341F" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M60 24 L60 94" stroke="#B8341F" stroke-width="2.5"/>
  <g fill="#3B2A20"><circle cx="38" cy="58" r="7"/><circle cx="82" cy="58" r="7"/><circle cx="44" cy="82" r="5.5"/><circle cx="76" cy="82" r="5.5"/></g>
  <path d="M30 40 C32 20 88 20 90 40 C80 30 40 30 30 40Z" fill="#3B2A20"/>
  <path d="M46 24 C42 10 34 8 30 10 M74 24 C78 10 86 8 90 10" stroke="#3B2A20" stroke-width="3.5" fill="none" stroke-linecap="round"/>
  <circle cx="30" cy="10" r="4" fill="#3B2A20"/><circle cx="90" cy="10" r="4" fill="#3B2A20"/>
  <ellipse cx="46" cy="42" rx="9" ry="10" fill="#fff"/><ellipse cx="74" cy="42" rx="9" ry="10" fill="#fff"/>
  <circle cx="48" cy="44" r="5.5" fill="#3B2A20"/><circle cx="72" cy="44" r="5.5" fill="#3B2A20"/>
  <circle cx="50" cy="42" r="2" fill="#fff"/><circle cx="74" cy="42" r="2" fill="#fff"/>
  <ellipse cx="36" cy="54" rx="6" ry="4" fill="#FF92C8" opacity=".7"/><ellipse cx="84" cy="54" rx="6" ry="4" fill="#FF92C8" opacity=".7"/>
  <path d="M54 56 Q60 62 66 56" stroke="#3B2A20" stroke-width="2.5" fill="none" stroke-linecap="round"/>
</symbol>
<symbol id="snail" viewBox="0 0 140 110">
  <ellipse cx="70" cy="104" rx="56" ry="5" fill="#2b3a67" opacity=".15"/>
  <path d="M10 98 C10 84 30 78 70 80 C100 80 112 84 112 92 C112 100 100 102 70 102 L24 102 C14 102 10 100 10 98Z" fill="#CDEFD6" stroke="#8FCBA2" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M96 84 C92 60 100 40 108 30" stroke="#8FCBA2" stroke-width="12" fill="none" stroke-linecap="round"/>
  <path d="M110 30 L108 12 M118 32 L126 16" stroke="#8FCBA2" stroke-width="4" stroke-linecap="round"/>
  <circle cx="108" cy="11" r="6" fill="#fff" stroke="#8FCBA2" stroke-width="2"/><circle cx="127" cy="14" r="6" fill="#fff" stroke="#8FCBA2" stroke-width="2"/>
  <circle cx="109" cy="12" r="3" fill="#3B2A20"/><circle cx="128" cy="15" r="3" fill="#3B2A20"/>
  <circle cx="58" cy="60" r="34" fill="#C8996A" stroke="#A97A4C" stroke-width="3"/>
  <circle cx="58" cy="60" r="23" fill="none" stroke="#A97A4C" stroke-width="3.5"/>
  <circle cx="58" cy="60" r="12" fill="none" stroke="#A97A4C" stroke-width="3.5"/>
  <circle cx="58" cy="60" r="3" fill="#A97A4C"/>
  <path d="M40 40 C48 34 56 33 62 34" stroke="#E6C9A0" stroke-width="4" fill="none" stroke-linecap="round"/>
  <ellipse cx="104" cy="82" rx="5" ry="3.5" fill="#FF92C8" opacity=".7"/>
</symbol>
<symbol id="bee" viewBox="0 0 120 110">
  <ellipse cx="60" cy="104" rx="30" ry="4" fill="#2b3a67" opacity=".12"/>
  <ellipse cx="40" cy="38" rx="20" ry="26" transform="rotate(-25 40 38)" fill="#BFE9FA" stroke="#7CCBEB" stroke-width="2.5" opacity=".9"/>
  <ellipse cx="78" cy="36" rx="20" ry="26" transform="rotate(25 78 36)" fill="#BFE9FA" stroke="#7CCBEB" stroke-width="2.5" opacity=".9"/>
  <ellipse cx="60" cy="68" rx="38" ry="32" fill="#FFC83D" stroke="#D99E12" stroke-width="2.5"/>
  <path d="M34 52 C32 70 34 84 40 92 L52 94 C46 84 44 70 46 48Z" fill="#3B2A20"/>
  <path d="M72 48 C76 70 74 84 68 94 L80 92 C86 84 88 70 84 52Z" fill="#3B2A20"/>
  <path d="M50 40 C46 26 40 22 36 22 M70 40 C74 26 80 22 84 22" stroke="#3B2A20" stroke-width="3.5" fill="none" stroke-linecap="round"/>
  <circle cx="36" cy="22" r="4" fill="#3B2A20"/><circle cx="84" cy="22" r="4" fill="#3B2A20"/>
  <ellipse cx="50" cy="58" rx="8.5" ry="9.5" fill="#fff"/><ellipse cx="70" cy="58" rx="8.5" ry="9.5" fill="#fff"/>
  <circle cx="51.5" cy="60" r="5" fill="#3B2A20"/><circle cx="68.5" cy="60" r="5" fill="#3B2A20"/>
  <circle cx="53" cy="58" r="1.8" fill="#fff"/><circle cx="70" cy="58" r="1.8" fill="#fff"/>
  <ellipse cx="40" cy="70" rx="5.5" ry="3.5" fill="#FF92C8" opacity=".8"/><ellipse cx="80" cy="70" rx="5.5" ry="3.5" fill="#FF92C8" opacity=".8"/>
  <path d="M55 72 Q60 77 65 72" stroke="#3B2A20" stroke-width="2.5" fill="none" stroke-linecap="round"/>
</symbol>
<symbol id="rabbit" viewBox="0 0 120 150">
  <ellipse cx="60" cy="144" rx="38" ry="5" fill="#2b3a67" opacity=".15"/>
  <ellipse cx="40" cy="30" rx="12" ry="32" transform="rotate(-8 40 30)" fill="#F4ECE0" stroke="#CDBFAA" stroke-width="2.5"/>
  <ellipse cx="80" cy="30" rx="12" ry="32" transform="rotate(8 80 30)" fill="#F4ECE0" stroke="#CDBFAA" stroke-width="2.5"/>
  <ellipse cx="40" cy="32" rx="5.5" ry="22" transform="rotate(-8 40 32)" fill="#FFB3DA"/>
  <ellipse cx="80" cy="32" rx="5.5" ry="22" transform="rotate(8 80 32)" fill="#FFB3DA"/>
  <ellipse cx="60" cy="116" rx="34" ry="26" fill="#F4ECE0" stroke="#CDBFAA" stroke-width="2.5"/>
  <ellipse cx="40" cy="138" rx="12" ry="7" fill="#F4ECE0" stroke="#CDBFAA" stroke-width="2.5"/><ellipse cx="80" cy="138" rx="12" ry="7" fill="#F4ECE0" stroke="#CDBFAA" stroke-width="2.5"/>
  <circle cx="60" cy="74" r="34" fill="#F4ECE0" stroke="#CDBFAA" stroke-width="2.5"/>
  <ellipse cx="46" cy="72" rx="8" ry="9" fill="#fff"/><ellipse cx="74" cy="72" rx="8" ry="9" fill="#fff"/>
  <circle cx="47.5" cy="74" r="5" fill="#3B2A20"/><circle cx="72.5" cy="74" r="5" fill="#3B2A20"/>
  <circle cx="49" cy="72" r="1.8" fill="#fff"/><circle cx="74" cy="72" r="1.8" fill="#fff"/>
  <ellipse cx="38" cy="86" rx="7" ry="4.5" fill="#FF92C8" opacity=".7"/><ellipse cx="82" cy="86" rx="7" ry="4.5" fill="#FF92C8" opacity=".7"/>
  <path d="M55 84 Q60 88 60 84 Q60 88 65 84" stroke="#3B2A20" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <ellipse cx="60" cy="81" rx="4" ry="3" fill="#FF92C8"/>
  <rect x="55" y="88" width="10" height="7" rx="2" fill="#fff" stroke="#CDBFAA" stroke-width="1.5"/>
</symbol>
<symbol id="sprout" viewBox="0 0 60 80">
  <path d="M30 76 C30 60 30 50 30 42" stroke="#2FA866" stroke-width="5" fill="none" stroke-linecap="round"/>
  <path d="M30 50 C14 52 8 40 10 30 C24 30 30 40 30 50Z" fill="#46C47E" stroke="#2FA866" stroke-width="2" stroke-linejoin="round"/>
  <path d="M30 44 C44 44 52 34 50 24 C36 24 30 34 30 44Z" fill="#7FE0AF" stroke="#2FA866" stroke-width="2" stroke-linejoin="round"/>
</symbol>
<symbol id="seed" viewBox="0 0 60 60">
  <ellipse cx="30" cy="34" rx="12" ry="16" transform="rotate(20 30 34)" fill="#C8996A" stroke="#8B5A3C" stroke-width="2.5"/>
  <path d="M26 26 C28 30 28 36 26 42" stroke="#E6C9A0" stroke-width="3" fill="none" stroke-linecap="round"/>
</symbol>
<symbol id="pot" viewBox="0 0 100 60">
  <path d="M10 8 H90 L82 54 C81 57 78 58 75 58 H25 C22 58 19 57 18 54Z" fill="#E39B6B" stroke="#B9703F" stroke-width="3" stroke-linejoin="round"/>
  <rect x="6" y="4" width="88" height="14" rx="7" fill="#F0B287" stroke="#B9703F" stroke-width="3"/>
</symbol>
</defs></svg>'''

def pot(x,y,kind):
    plant={'bloom':'<use href="#daisy" x="-6" y="-70" width="62" height="93"/>','sprout':'<use href="#sprout" x="2" y="-44" width="46" height="62"/>','seed':'<use href="#seed" x="8" y="-6" width="34" height="34"/>','empty':''}[kind]
    op=' opacity=".45"' if kind=='empty' else ''
    q='<text x="25" y="42" text-anchor="middle" class="fred" font-size="28" fill="#B9703F" opacity=".6">?</text>' if kind=='empty' else ''
    return f'<g transform="translate({x} {y})"{op}><g transform="translate(25 8)">{plant}</g><use href="#pot" x="0" y="14" width="76" height="46"/>{q.replace("x=\"25\"","x=\"38\"").replace("y=\"42\"","y=\"52\"")}</g>'

def sky():
    return '''<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#BFE9FA"/><stop offset="1" stop-color="#FFF7E8"/></linearGradient>
<linearGradient id="hill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8DE6B8"/><stop offset="1" stop-color="#5CCB93"/></linearGradient>
<linearGradient id="wood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D9AA77"/><stop offset="1" stop-color="#B98254"/></linearGradient>
<filter id="soft" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="6" stdDeviation="7" flood-color="#2b3a67" flood-opacity=".18"/></filter>
</defs>
<rect width="960" height="600" fill="url(#sky)"/>
<circle cx="860" cy="70" r="38" fill="#FFC83D" opacity=".9"/><circle cx="860" cy="70" r="52" fill="#FFC83D" opacity=".18"/>
<g fill="#fff" opacity=".9"><ellipse cx="200" cy="74" rx="50" ry="16"/><ellipse cx="232" cy="62" rx="32" ry="18"/><ellipse cx="640" cy="52" rx="44" ry="13"/><ellipse cx="666" cy="42" rx="26" ry="14"/></g>
<ellipse cx="300" cy="470" rx="520" ry="120" fill="#BDEFD3"/>
<path d="M0 430 C160 395 330 400 520 425 C720 450 840 420 960 405 V600 H0Z" fill="url(#hill)"/>
<path d="M0 520 C120 470 220 440 330 440 L350 600 H0Z" fill="#F3DDB4" opacity=".0"/>'''

def hud(filled):
    dots=''.join(f'<circle cx="{410+i*15}" cy="38" r="5.5" fill="{"#2FCB86" if i<filled else "#fff"}" stroke="#0F857D" stroke-width="2" opacity="{1 if i<filled else .8}"/>' for i in range(10))
    return f'''<g class="fred">
<g><rect x="24" y="22" width="112" height="46" rx="23" fill="#0A625C"/><rect x="24" y="16" width="112" height="46" rx="23" fill="#0F857D"/><text x="80" y="47" text-anchor="middle" fill="#fff" font-size="21" font-weight="600">‹ Back</text></g>
{dots}
<g><circle cx="920" cy="44" r="25" fill="#fff" filter="url(#soft)"/><path d="M908 38 h6 l9 -7 v26 l-9 -7 h-6z" fill="#0F857D"/><path d="M928 36 q6 8 0 16" stroke="#0F857D" stroke-width="3.2" fill="none" stroke-linecap="round"/></g></g>'''

def stall(awn_y=150):
    stripes=''
    for i in range(9):
        c='#0F857D' if i%2==0 else '#fff'
        x=270+i*72
        stripes+=f'<path d="M{x} 96 h72 v{awn_y-96} a36 26 0 0 1 -72 0Z" fill="{c}" stroke="#0A625C" stroke-width="2" stroke-linejoin="round"/>'
    return f'''<g filter="url(#soft)">
<rect x="280" y="150" width="14" height="300" rx="6" fill="url(#wood)"/><rect x="896" y="150" width="14" height="300" rx="6" fill="url(#wood)"/>
<rect x="296" y="150" width="598" height="290" fill="#FFF1D6" opacity=".75"/>
<g>{stripes}</g>
<rect x="262" y="84" width="664" height="20" rx="10" fill="#0A625C"/>
</g>'''

def counter():
    return '''<g filter="url(#soft)"><rect x="262" y="408" width="664" height="30" rx="15" fill="#E6BE8D"/><rect x="274" y="436" width="640" height="76" rx="10" fill="url(#wood)"/>
<g stroke="#A5703F" stroke-width="2" opacity=".35"><path d="M300 460 H890"/><path d="M300 486 H890"/></g>
<rect x="470" y="446" width="196" height="40" rx="14" fill="#FFF7E8" stroke="#A5703F" stroke-width="2.5"/>
<text x="568" y="474" text-anchor="middle" class="fred" font-size="22" font-weight="600" fill="#0F857D">Seed Stall</text></g>'''

def bin_(x,label,flower,n,color):
    inner=''.join(f'<use href="#{flower}" x="{x+14+ (i%4)*30}" y="{300+(i//4)*0 - (i%2)*10}" width="42" height="63"/>' for i in range(n))
    return f'''<g><use href="#{flower}" x="0" y="0" width="0" height="0"/>
{inner}
<path d="M{x} 348 H{x+148} L{x+138} 408 H{x+10}Z" fill="{color}" stroke="#3B2A20" stroke-opacity=".25" stroke-width="2.5" stroke-linejoin="round"/>
<path d="M{x-4} 346 H{x+152}" stroke="#fff" stroke-width="10" stroke-linecap="round" opacity=".9"/>
<rect x="{x+34}" y="368" width="80" height="26" rx="13" fill="#fff"/><text x="{x+74}" y="387" text-anchor="middle" class="fred" font-size="17" font-weight="600" fill="#3B2A20">{label}</text></g>'''

def basket(x,y,flowers,count):
    fl=''.join(f'<use href="#{f}" x="{x+fx}" y="{y+fy}" width="{w}" height="{int(w*1.5)}" transform="rotate({r} {x+fx+w/2} {y+fy+w})"/>' for f,fx,fy,w,r in flowers)
    badge=f'<g class="pop"><circle cx="{x+148}" cy="{y+4}" r="26" fill="#FFC83D" stroke="#D99E12" stroke-width="3"/><text x="{x+148}" y="{y+14}" text-anchor="middle" class="fred" font-size="30" font-weight="700" fill="#3B2A20">{count}</text></g>' if count is not None else ''
    return f'''<g>
{fl}
<path d="M{x+8} {y+56} H{x+142} L{x+128} {y+104} C{x+126} {y+110} {x+120} {y+112} {x+112} {y+112} H{x+38} C{x+30} {y+112} {x+24} {y+110} {x+22} {y+104}Z" fill="#D9A25F" stroke="#A5703F" stroke-width="3" stroke-linejoin="round"/>
<g stroke="#A5703F" stroke-width="2.5" opacity=".55" stroke-linecap="round"><path d="M{x+16} {y+72} H{x+134}"/><path d="M{x+20} {y+88} H{x+130}"/><path d="M{x+52} {y+58} V{y+110}"/><path d="M{x+75} {y+58} V{y+112}"/><path d="M{x+98} {y+58} V{y+110}"/></g>
<rect x="{x+2}" y="{y+50}" width="146" height="14" rx="7" fill="#E9B979" stroke="#A5703F" stroke-width="3"/>
<path d="M{x+14} {y+52} C{x+10} {y+0} {x+140} {y+0} {x+136} {y+52}" fill="none" stroke="#A5703F" stroke-width="5" stroke-linecap="round" opacity="0"/>
{badge}</g>'''

def bubble(x,y,w,h,inner):
    return f'<g filter="url(#soft)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="32" fill="#fff"/><path d="M{x+w//2-18} {y+h-2} l12 34 l22 -34Z" fill="#fff"/></g>{inner}'

def sceneA():
    order=bubble(40,92,236,132,
        '<g class="fred" text-anchor="middle" font-weight="600" fill="#3B2A20"><text x="158" y="124" font-size="19">I would like</text>'
        '<use href="#daisy" x="62" y="134" width="34" height="51"/><text x="112" y="172" font-size="36" font-weight="700" fill="#0F857D">3</text>'
        '<text x="158" y="170" font-size="30">+</text>'
        '<use href="#tulip" x="180" y="134" width="34" height="51"/><text x="232" y="172" font-size="36" font-weight="700" fill="#C23B86">4</text></g>')
    cust=f'<g class="bob"><use href="#ladybug" x="76" y="298" width="150" height="138"/></g>'
    path='<path d="M0 456 C80 436 190 436 262 446 V600 H0Z" fill="#F3DDB4"/><path d="M0 470 C80 452 190 452 262 462" stroke="#E2C58E" stroke-width="4" fill="none" stroke-dasharray="2 18" stroke-linecap="round"/>'
    bins=bin_(290,'Daisies','daisy',6,'#FFFFFF')+bin_(446,'Tulips','tulip',6,'#FFD3EA')
    bsk=basket(622,330,[('daisy',20,-8,40,-10),('daisy',48,-18,40,6),('daisy',76,-6,40,14),('tulip',98,-14,40,-6)],4)
    shelf=f'''<g filter="url(#soft)"><rect x="30" y="500" width="900" height="84" rx="26" fill="#FFF1D6" stroke="#E6BE8D" stroke-width="3"/></g>
<text x="56" y="532" class="fred" font-size="20" font-weight="600" fill="#0F857D">My garden</text>
{pot(260,512,'bloom')}{pot(352,512,'bloom')}{pot(444,512,'sprout')}{pot(536,512,'sprout')}{pot(628,512,'seed')}{pot(720,512,'empty')}{pot(812,512,'empty')}'''
    # dragging flower with shadow
    drag='<g class="lift"><ellipse cx="586" cy="372" rx="26" ry="7" fill="#2b3a67" opacity=".22"/><use href="#tulip" x="556" y="262" width="60" height="90" transform="rotate(-8 586 307)"/></g>'
    return f'''<svg viewBox="0 0 960 600" class="scene" role="img" aria-label="Seed Stall screen: the ladybug orders 3 daisies and 4 tulips">
{sky()}{path}{stall()}{hazel(776,236,150)}
<g class="fred"><rect x="800" y="154" width="116" height="30" rx="15" fill="#fff" opacity="0"/></g>
{counter()}{bins}{bsk}{cust}{order}{drag}{shelf}{hud(3)}
<g class="fred"><g><rect x="338" y="116" width="270" height="36" rx="18" fill="#fff"/><text x="473" y="141" text-anchor="middle" font-size="19" font-weight="600" fill="#3B2A20">Drag flowers into the basket</text></g></g>
</svg>'''

def sceneB():
    order=bubble(40,92,236,100,'<g class="fred" text-anchor="middle" font-weight="600" fill="#3B2A20"><text x="158" y="136" font-size="22">How many flowers</text><text x="158" y="166" font-size="22">do I have?</text></g>')
    cust=f'<g class="bob"><use href="#ladybug" x="76" y="298" width="150" height="138"/></g>'
    path='<path d="M0 456 C80 436 190 436 262 446 V600 H0Z" fill="#F3DDB4"/>'
    bouquet=''.join(f'<use href="#{f}" x="{x}" y="{y}" width="{w}" height="{int(w*1.5)}" transform="rotate({r} {x+w/2} {y+w*1.2})"/>' for f,x,y,w,r in [('daisy',560,240,64,-18),('daisy',600,214,64,-4),('daisy',644,232,64,12),('tulip',684,250,64,22),('tulip',520,268,64,-30),('tulip',724,282,64,32),('tulip',600,262,64,6)])
    wrap='<path d="M560 340 L760 340 L700 440 L620 440Z" fill="#FFF7E8" stroke="#E6BE8D" stroke-width="3" stroke-linejoin="round"/><path d="M596 340 L660 440 L724 340" fill="#FFD3EA" opacity=".6"/><path d="M638 392 L682 392 L674 408 L646 408Z" fill="#FFC83D"/>'
    def choice(x,n,state):
        fill={'idle':'#fff','dim':'#F1EADC','pick':'#fff'}[state]; tcol={'idle':'#3B2A20','dim':'#B9AD99','pick':'#3B2A20'}[state]
        edge={'idle':'#E6BE8D','dim':'#E4DAC5','pick':'#2FCB86'}[state]; sw=4 if state!='pick' else 6
        return f'<g class="fred"><rect x="{x}" y="478" width="150" height="86" rx="24" fill="{edge}"/><rect x="{x}" y="470" width="150" height="86" rx="24" fill="{fill}" stroke="{edge}" stroke-width="{sw}"/><text x="{x+75}" y="528" text-anchor="middle" font-size="52" font-weight="700" fill="{tcol}">{n}</text></g>'
    choices=choice(290,6,'dim')+choice(480,7,'idle')+choice(670,8,'idle')
    hz=bubble(730,176,176,52,'<g class="fred" text-anchor="middle" font-weight="600" fill="#3B2A20"><text x="818" y="210" font-size="19">Count them!</text></g>')
    return f'''<svg viewBox="0 0 960 600" class="scene" role="img" aria-label="How many step: three number choices, one dimmed as a hint">
{sky()}{path}{stall()}{hazel(776,236,150)}
<g filter="url(#soft)"><rect x="262" y="408" width="664" height="30" rx="15" fill="#E6BE8D"/></g>
{wrap}{bouquet}
<g class="sparkle" fill="#FFC83D"><path d="M520 220 l5 12 l12 5 l-12 5 l-5 12 l-5 -12 l-12 -5 l12 -5Z"/><path d="M770 220 l4 9 l9 4 l-9 4 l-4 9 l-4 -9 l-9 -4 l9 -4Z"/></g>
{cust}{order}{hz}{choices}
{hud(3)}
<g class="fred"><rect x="300" y="116" width="300" height="36" rx="18" fill="#fff"/><text x="450" y="141" text-anchor="middle" font-size="19" font-weight="600" fill="#3B2A20">Hint: the 6 is dimmed</text></g>
</svg>'''

def cast():
    items=[('ladybug','Ladybug','flutters in',120,110),('snail','Snail','slides in slowly',140,110),('bee','Bee','zig-zags in',120,110),('rabbit','Rabbit','hops in',120,150)]
    out=''
    for sid,name,how,w,h in items:
        out+=f'<figure class="cast"><svg viewBox="0 0 {w} {h}" width="{w*1.3:.0f}" height="{h*1.3:.0f}"><use href="#{sid}" width="{w}" height="{h}"/></svg><figcaption><b>{name}</b><br>{how}</figcaption></figure>'
    return out

def stages():
    out=''
    for lab,sym,w,h in [('Seed','seed',60,60),('Sprout','sprout',60,80),('Bloom','daisy',60,90)]:
        out+=f'<figure class="cast"><svg viewBox="0 0 90 110" width="110" height="134"><use href="#{sym}" x="{(90-w)/2}" y="{110-h-18}" width="{w}" height="{h}"/><use href="#pot" x="5" y="78" width="80" height="48"/></svg><figcaption><b>{lab}</b></figcaption></figure>'
    return out

def species():
    names=['Sunflower','Tulip','Daisy','Lavender','Strawberry','Small tree']
    return ''.join(f'<span class="chip">{n}</span>' for n in names)

html=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Addition Garden art preview</title>
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Andika:wght@400;700&display=swap" rel="stylesheet">
<style>
:root{{--cream:#FFF7E8;--ink:#3B2A20;--teal:#0F857D;--card:#fff}}
body{{margin:0;background:var(--cream);color:var(--ink);font-family:Andika,system-ui,sans-serif;padding:24px 16px 60px}}
.fred{{font-family:Fredoka,ui-rounded,system-ui,sans-serif}}
main{{max-width:980px;margin:0 auto}}
h1{{font-family:Fredoka,system-ui;color:var(--teal);margin:0 0 4px}} h2{{font-family:Fredoka,system-ui;margin:36px 0 8px}}
p{{line-height:1.5;max-width:70ch}} .scene{{width:100%;height:auto;border-radius:32px;box-shadow:0 10px 30px rgba(43,58,103,.18);display:block;background:#fff}}
.row{{display:flex;flex-wrap:wrap;gap:18px;align-items:flex-end}} .cast{{margin:0;text-align:center;background:#fff;border-radius:24px;padding:14px 18px;box-shadow:0 6px 18px rgba(43,58,103,.12)}}
.cast figcaption{{font-size:15px;margin-top:6px}} .chip{{display:inline-block;background:#fff;border-radius:999px;padding:6px 14px;margin:4px;box-shadow:0 3px 10px rgba(43,58,103,.1);font-family:Fredoka,system-ui;font-weight:600}}
.note{{background:#fff;border-left:6px solid var(--teal);border-radius:12px;padding:10px 16px;max-width:70ch}}
@keyframes bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-6px)}}}} .bob{{animation:bob 2.6s ease-in-out infinite}}
@keyframes lift{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-4px)}}}} .lift{{animation:lift 1.8s ease-in-out infinite}}
@keyframes pop{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.08)}}}} .pop{{transform-box:fill-box;transform-origin:center;animation:pop 2s ease-in-out infinite}}
@keyframes tw{{0%,100%{{opacity:.35}}50%{{opacity:1}}}} .sparkle{{animation:tw 1.6s ease-in-out infinite}}
@media (prefers-reduced-motion:reduce){{.bob,.lift,.pop,.sparkle{{animation:none}}}}
</style></head><body>{defs}<main>
<h1>Addition Garden: art direction preview</h1>
<p>Static prototype for approval. Nothing here is the final game. It shows the look, the cast and the garden reward so we can agree on the art before any development.
Gentle idle motion only (bobbing, glowing count badge). It follows the v3 style guide: cream and teal, Fredoka numbers, rounded shapes, soft tinted shadows, no red in feedback.</p>
<h2>1. Seed Stall: filling the basket (levels 1 to 3)</h2>
<p>The ladybug orders 3 daisies and 4 tulips. The child drags flowers from the two bins into the basket. The yellow badge counts as they go. Hazel is the shopkeeper. Progress dots on top, My garden shelf at the bottom.</p>
{sceneA()}
<h2>2. The "How many?" step</h2>
<p>After both groups are in, they merge into a bouquet and the child taps the total. This is the step that makes them add. A wrong tap dims that choice (here the 6) and never shows the answer.</p>
{sceneB()}
<h2>3. The customers</h2>
<div class="row">{cast()}</div>
<p class="note">The ladybug is the only coral red thing in the game. It is a character color, not feedback, so it does not break the "no red in feedback" rule. Say if you want a different color.</p>
<h2>4. My garden: seed, sprout, bloom</h2>
<div class="row">{stages()}</div>
<p>Each solved order plants one seed. Plants grow as the child plays more sessions, never with time away. Six species, in a fixed cycle that matches the bin flowers:</p>
<div>{species()}</div>
<p>Only the daisy and the tulip are drawn in this preview. The other four would follow the same simple, rounded style.</p>
</main></body></html>'''
open('index.html','w').write(html)
