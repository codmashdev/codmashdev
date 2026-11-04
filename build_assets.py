"""Build self-contained SVG panels for the CodMash GitHub profile README.

All graphics are SVG code, not AI-generated images. Run:
    python3 build_assets.py
"""

from html import escape
from pathlib import Path

OUT = Path(__file__).parent / "assets"
OUT.mkdir(exist_ok=True)
ORANGE = "#ff8a2b"
CYAN = "#39c5ff"
WHITE = "#f7f8fc"
MUTED = "#a0aabc"


def t(x, y, s, size=24, color=WHITE, weight=500, anchor="start", opacity=1, spacing=0):
    return (
        f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial,Helvetica,sans-serif" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" '
        f'opacity="{opacity}" letter-spacing="{spacing}">{escape(str(s))}</text>'
    )


def rect(x, y, w, h, fill, rx=12, stroke="none", sw=1, opacity=1):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}"/>'
    )


def line(x1, y1, x2, y2, color="#273142", sw=1, opacity=1):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}" opacity="{opacity}"/>'


def pill(x, y, w, title, accent=ORANGE, fill="#1c2636"):
    return (
        rect(x, y, w, 39, fill, 12, "#394457")
        + f'<circle cx="{x+20}" cy="{y+19}" r="6" fill="{accent}"/>'
        + t(x+36, y+26, title, 16, WHITE, 700)
    )


def common_defs():
    return """
    <defs>
      <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#0c1019"/>
        <stop offset="60%" stop-color="#171d2c"/>
        <stop offset="100%" stop-color="#0e1420"/>
      </linearGradient>
      <linearGradient id="orange" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#ffd178"/>
        <stop offset="58%" stop-color="#ff8a2b"/>
        <stop offset="100%" stop-color="#d85113"/>
      </linearGradient>
      <linearGradient id="coat" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#ffab4f"/>
        <stop offset="55%" stop-color="#ee7222"/>
        <stop offset="100%" stop-color="#b33b14"/>
      </linearGradient>
      <linearGradient id="blue" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#5dd6ff"/>
        <stop offset="100%" stop-color="#105ca9"/>
      </linearGradient>
      <radialGradient id="halo">
        <stop offset="0%" stop-color="#ff8a2b" stop-opacity=".28"/>
        <stop offset="100%" stop-color="#ff8a2b" stop-opacity="0"/>
      </radialGradient>
      <radialGradient id="cyanHalo">
        <stop offset="0%" stop-color="#37b8f7" stop-opacity=".16"/>
        <stop offset="100%" stop-color="#37b8f7" stop-opacity="0"/>
      </radialGradient>
      <pattern id="dots" width="32" height="32" patternUnits="userSpaceOnUse">
        <circle cx="2" cy="2" r="1" fill="#9da9bd" opacity=".13"/>
      </pattern>
      <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="16"/>
      </filter>
    </defs>
    """


def frame(w, h, content, label):
    grid = "".join(
        line(x, 0, x, h, "#71809b", .5, .07)
        for x in range(60, w, 80)
    )
    grid += "".join(
        line(0, y, w, y, "#71809b", .5, .06)
        for y in range(40, h, 80)
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">'
        + common_defs()
        + rect(1, 1, w-2, h-2, "url(#bg)", 24, "#3b4355", 2)
        + f'<ellipse cx="{w*.74}" cy="{h*.5}" rx="{w*.3}" ry="{h*.85}" fill="url(#halo)"/>'
        + grid
        + content
        + "</svg>"
    )


def corners(w, h):
    return (
        f'<path d="M42 88V43H96 M{w-96} 43H{w-42}V88 M42 {h-88}V{h-43}H96 '
        f'M{w-96} {h-43}H{w-42}V{h-88}" fill="none" stroke="{ORANGE}" '
        f'stroke-width="3" opacity=".7"/>'
    )


def boy(x, y, scale=1, mirror=False, jacket=1):
    """Friendly young male coder in orange techwear; hand-drawn SVG geometry."""
    flip = "translate(310 0) scale(-1 1)" if mirror else ""
    return f'<g transform="translate({x} {y}) scale({scale})"><g transform="{flip}">' + f"""
      <ellipse cx="153" cy="349" rx="119" ry="22" fill="#fe7d22" opacity=".19" filter="url(#softGlow)"/>
      <path d="M116 262 L105 344 L143 344 L167 285 L180 343 L219 343 L218 257Z" fill="#181e2c" stroke="#313747" stroke-width="4"/>
      <path d="M103 336 L150 336 L149 356 L91 356 Q85 346 103 336Z" fill="#313644"/>
      <path d="M180 335 L226 335 L238 354 L176 356Z" fill="#313644"/>
      <path d="M80 163 Q98 134 128 136 L188 136 Q220 139 235 173 L261 264 Q250 288 219 275 L204 243 L218 283 Q159 302 91 275 L107 238 L89 274 Q62 279 53 255Z" fill="url(#coat)" stroke="#773318" stroke-width="5"/>
      <path d="M114 145 L151 179 L191 144 L187 266 Q150 281 112 264Z" fill="#222b38" stroke="#0d1727" stroke-width="4"/>
      <path d="M152 180L152 267" stroke="{ORANGE}" stroke-width="4"/>
      <path d="M111 156 L77 228 L91 259 L112 235" fill="#ff9c40" stroke="#803d1c" stroke-width="5"/>
      <path d="M198 155 L238 225 L222 266 L199 239" fill="#c6511b" stroke="#70301c" stroke-width="5"/>
      <path d="M95 228 L70 226 Q44 215 43 191 L34 156 Q30 141 42 134 Q56 125 64 145 L72 174 L111 193Z" fill="#dc742e" stroke="#773c22" stroke-width="4"/>
      <path d="M35 158 L25 134 Q24 122 35 122 L49 141 L49 113 Q52 102 61 112 L64 143 L76 134 Q91 131 84 146 L64 169Z" fill="#f1b37e" stroke="#8d593f" stroke-width="4"/>
      <path d="M127 120 L130 154 L180 154 L183 115Z" fill="#d99463" stroke="#a46840" stroke-width="3"/>
      <path d="M103 67 Q100 29 146 17 Q206 22 215 81 L210 113 Q195 139 163 143 Q126 141 110 120Z" fill="#efb486" stroke="#95654e" stroke-width="4"/>
      <path d="M98 82 Q88 50 109 26 L122 35 L136 8 L153 24 L178 6 L183 26 L212 18 L205 48 L225 47 L208 75 Q186 59 178 52 Q153 76 113 73 L110 96Z" fill="#1b1d29" stroke="#0a111d" stroke-width="5"/>
      <path d="M114 70 Q140 64 151 49 Q173 68 210 63" fill="none" stroke="#2d3040" stroke-width="6"/>
      <path d="M126 94 L146 92 M177 93 L196 95" stroke="#302d30" stroke-width="6" stroke-linecap="round"/>
      <ellipse cx="139" cy="100" rx="5" ry="8" fill="#202732"/>
      <ellipse cx="186" cy="100" rx="5" ry="8" fill="#202732"/>
      <path d="M159 102 Q154 114 164 116" fill="none" stroke="#b77d56" stroke-width="3"/>
      <path d="M149 125 Q163 135 179 122" fill="none" stroke="#743e3b" stroke-width="3" stroke-linecap="round"/>
      <path d="M109 88 Q99 78 91 90 Q94 109 108 109" fill="#e6a777" stroke="#9b674b" stroke-width="3"/>
      <path d="M212 88 Q223 79 229 92 Q228 109 209 111" fill="#e6a777" stroke="#9b674b" stroke-width="3"/>
      <path d="M111 167 L133 185 L123 202 M197 167L178 187L190 202" stroke="#ffc374" fill="none" stroke-width="5"/>
      <path d="M203 211 L233 214" stroke="{CYAN}" stroke-width="5" stroke-linecap="round"/>
      <circle cx="229" cy="214" r="5" fill="{CYAN}"/>
      <path d="M94 265 Q154 287 214 264" fill="none" stroke="#4c2419" stroke-width="4" opacity=".7"/>
    </g></g>"""


def glow_points(w, h):
    pts = [(130,115),(265,76),(442,335),(746,81),(870,330),(1074,112),(1120,314)]
    return "".join(f'<path d="M{x-6} {y}H{x+6} M{x} {y-6}V{y+6}" stroke="{CYAN if i%2 else ORANGE}" opacity=".36" stroke-width="2"/>' for i,(x,y) in enumerate(pts))


def hero():
    w,h = 1200,440
    c = corners(w,h)+glow_points(w,h)
    c += t(68,100,"< CODMASH / DIGITAL EXPERIENCE STUDIO >",18,CYAN,700,spacing=2)
    c += t(68,166,"Hi, we're",26,WHITE,600)
    c += t(68,239,"CodMash",73,ORANGE,800)
    c += t(68,279,"WE DESIGN. WE DEVELOP. WE AUTOMATE.",20,WHITE,700,spacing=1.5)
    c += t(68,314,"Crafting standout web experiences and intelligent products.",18,MUTED)
    c += pill(68,343,145,"WEBSITES")+pill(228,343,146,"SOFTWARE",CYAN)+pill(389,343,142,"AI + UX","#5ce5a2")
    c += f'<ellipse cx="943" cy="218" rx="226" ry="194" fill="url(#cyanHalo)"/>'
    c += boy(747,49,1.04)
    c += t(1128,396,"BUILD WHAT'S NEXT.",14,ORANGE,800,"end",.9,1.1)
    return frame(w,h,c,"CodMash hero with male software developer mascot")


def team():
    w,h=660,178
    c = t(330,22,"THE PEOPLE BEHIND THE PIXELS",14,"#4c596b",800,"middle",1,2)
    for x,caption in ((118,"DESIGN"),(263,"BUILD"),(408,"AUTOMATE")):
        c += f'<circle cx="{x+67}" cy="80" r="65" fill="#f5f7fa" stroke="#e3e7ec" stroke-width="2"/>'
        c += boy(x,26,.36,mirror=x==263)
        c += t(x+56,163,caption,13,"#253041",800,"middle",1,1)
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'+common_defs()+c+'</svg>'


def mission():
    w,h=1200,370
    c=t(595,77,"// OUR PHILOSOPHY",17,ORANGE,800,spacing=2)
    c+=t(595,129,"Believe in the build.",38,WHITE,800)
    c+=t(595,157,"Technology should be powerful, human, and beautifully simple.",17,MUTED)
    rows=[
        ("01","Interfaces that feel alive","Thoughtful UI, motion, and memorable experiences.",ORANGE),
        ("02","Solutions that solve real problems","Custom platforms, portals, and business automation.",CYAN),
        ("03","Engineering for the long run","Maintainable code, performance, and dependable delivery.","#5ee5a2"),
    ]
    for i,(n,a,b,col) in enumerate(rows):
        y=203+i*53
        c+=rect(590,y-21,560,48,"#202735",10,"#31384a")
        c+=t(607,y+11,n,18,col,800)
        c+=t(650,y+2,a,18,WHITE,700)
        c+=t(650,y+21,b,12,MUTED)
    c+=f'<ellipse cx="285" cy="200" rx="220" ry="190" fill="url(#halo)"/>'
    c+=boy(42,8,.96)
    c+=boy(237,55,.70,mirror=True)
    return frame(w,h,c,"CodMash philosophy dark orange cinematic panel")


def tech():
    w,h=390,150
    return w,h


def stack():
    w,h=1200,385
    c=boy(24,21,1.02)
    c+=f'<path d="M250 203 Q340 170 425 234" fill="none" stroke="{ORANGE}" stroke-width="4" stroke-dasharray="12 16" opacity=".9"/>'
    c+=f'<circle cx="420" cy="231" r="8" fill="{ORANGE}"/>'
    c+=t(440,75,"// OUR TECH ARSENAL",17,ORANGE,800,spacing=2)
    c+=t(440,119,"Tools we build with.",36,WHITE,800)
    c+=t(440,146,"Solid foundations. Modern workflows. Purposeful innovation.",16,MUTED)
    badges=[
        ("PHP","#7467bf"),("Laravel","#d54538"),("JavaScript","#ad8a14"),("TypeScript","#2d79b7"),
        ("React","#1a7da8"),("WordPress","#277f9d"),("Joomla","#c65c37"),("Shopify","#509b38"),
        ("Python","#467faf"),("AI & APIs","#8849bb"),("WooCommerce","#8e5ba6"),("Figma","#bc483f")
    ]
    for i,(name,col) in enumerate(badges):
        col_i=i%4
        row_i=i//4
        x=442+col_i*177
        y=174+row_i*61
        c+=rect(x,y,162,47,col,12,opacity=.23)
        c+=rect(x+1,y+1,160,45,"#20293b",11,"#384355")
        c+=f'<circle cx="{x+19}" cy="{y+23}" r="7" fill="{col}"/>'
        c+=t(x+34,y+30,name,17,WHITE,700)
    return frame(w,h,c,"CodMash technical skills panel with male mascot")


def identity():
    w,h=1200,460
    c=t(478,69,"// THE CODMASH IDENTITY",17,ORANGE,800,spacing=2)
    c+=t(478,110,"Our work, in focus.",35,WHITE,800)
    c+=rect(52,36,355,387,"#222a38",18,"#ae642e",2)
    c+=rect(69,53,321,42,"#cb591b",10)
    c+=t(88,81,"CODMASH  /  DIGITAL STUDIO",18,WHITE,800,spacing=1.3)
    c+=f'<circle cx="230" cy="205" r="92" fill="#132437" stroke="#e58a39" stroke-width="3"/>'
    c+=boy(130,100,.55)
    c+=t(230,329,"CODMASH",32,ORANGE,800,"middle")
    c+=t(230,357,"IDEAS INTO IMPACT",15,WHITE,700,"middle",1,2)
    c+=line(89,374,372,374,"#4d596a",2)
    c+=t(94,403,"WEB  •  SOFTWARE  •  AUTOMATION",13,CYAN,700)
    metrics=[
        ("250+","PROJECTS DELIVERED",ORANGE),
        ("12+","YEARS EXPERIENCE",CYAN),
        ("100+","HAPPY CLIENTS","#a98bfd"),
        ("GLOBAL","PARTNER MINDSET","#66d6a1")
    ]
    for i,(v,label,col) in enumerate(metrics):
        x=482+(i%4)*168
        c+=rect(x,145,154,92,"#20293a",13,"#353f51")
        c+=t(x+17,186,v,30,col,800)
        c+=t(x+17,211,label,12,MUTED,700)
    c+=rect(478,262,658,157,"#1b2433",14,"#344052")
    c+=t(500,290,"FROM IDEA TO IMPACT",14,WHITE,800,spacing=2)
    for i,(label,percent,col) in enumerate([
        ("Discover",.82,ORANGE),("Design",.94,CYAN),("Develop",.90,"#72d6a2"),("Deliver",.86,"#ad8bf5")
    ]):
        y=314+i*27
        c+=t(500,y,label,14,MUTED,700)
        c+=rect(609,y-12,477,11,"#313c4c",5)
        c+=rect(609,y-12,int(477*percent),11,col,5)
    c+=t(1138,435,"CAPABILITIES  /  NOT LIVE GITHUB STATS",11,"#6f7b8d",600,"end")
    return frame(w,h,c,"CodMash identity badge and published company highlights")


def contribution():
    w,h=1200,525
    c=t(66,71,"ENGINEERING ACTIVITY  /  A CITY OF IDEAS",22,WHITE,800)
    c+=t(66,99,"A visual story of the things we build. GitHub's live activity appears below the README.",15,MUTED)
    # Isometric tiles: distinctive 3D-city visual, illustrative (not fabricated GitHub activity).
    c+=f'<path d="M80 245 L573 125 L1024 324 L532 452Z" fill="#0c1a32" stroke="#1c58a4" stroke-width="2"/>'
    for row in range(11):
        for col in range(23):
            x=106+col*20+row*18
            y=242-col*4.9+row*8.9
            strength=((col*13+row*7)%17)
            fill="#1b4980" if strength<10 else "#2165b2"
            if 10<col<18 and 3<row<9 and strength>8:
                fill="#279bd7"
            c+=f'<path d="M{x:.1f} {y:.1f}l18 -4.4 16 8 -18 4.4Z" fill="{fill}" stroke="#112845" stroke-width="1"/>'
            if 10<col<18 and 3<row<9 and strength>11:
                high=9+strength*1.7
                c+=f'<path d="M{x:.1f} {y:.1f}l18 -4.4v-{high:.1f}l-18 4.4Z" fill="#1598d8" opacity=".9"/>'
                c+=f'<path d="M{x:.1f} {y-high:.1f}l18 -4.4 16 8 -18 4.4Z" fill="#3ce2fa" opacity=".94"/>'
    # Donut / capability breakdown.
    c+=f'<circle cx="196" cy="398" r="68" stroke="#27384c" stroke-width="31" fill="none"/>'
    for dash,offset,col in ((95,0,ORANGE),(78,-104,CYAN),(75,-192,"#714cb1")):
        c+=f'<circle cx="196" cy="398" r="68" stroke="{col}" stroke-width="31" fill="none" stroke-dasharray="{dash} 427" stroke-dashoffset="{offset}" transform="rotate(-90 196 398)"/>'
    c+=t(196,404,"BUILD",20,WHITE,800,"middle")
    c+=t(313,385,"WEB / PRODUCT",16,ORANGE,700)
    c+=t(313,412,"DESIGN / UX",16,CYAN,700)
    c+=t(313,439,"AI / AUTOMATION",16,"#a88afa",700)
    c+=rect(920,52,218,183,"#131d2d",15,"#2c4262")
    c+=t(944,82,"HOW WE WORK",16,WHITE,800)
    for i,(label,col) in enumerate((("Ideate",ORANGE),("Prototype",CYAN),("Build","#76e2b9"),("Launch","#a88afa"))):
        y=111+i*29
        c+=f'<circle cx="951" cy="{y-5}" r="6" fill="{col}"/>'+t(970,y,label,15,MUTED,700)
    return frame(w,h,c,"CodMash isometric development city visual")


def contact():
    w,h=1200,335
    c=t(565,80,"// JOIN THE BUILD",18,ORANGE,800,spacing=2)
    c+=t(565,127,"Let's create something",36,WHITE,800)
    c+=t(565,167,"remarkable.",42,ORANGE,800)
    c+=t(565,198,"Big ideas deserve thoughtful execution.",17,MUTED)
    tech_symbols=[("{}",CYAN,87,80),("</>",ORANGE,285,76),("AI","#a26ae8",153,218),("JS","#e1c440",344,228)]
    for sym,col,x,y in tech_symbols:
        c+=rect(x,y,114,101,"#202a3b",15,col,2)
        c+=t(x+57,y+68,sym,36,col,800,"middle")
    c+=pill(565,222,176,"WEBSITE",CYAN)
    c+=pill(757,222,185,"PORTFOLIO",ORANGE)
    c+=pill(959,222,176,"CONTACT","#75dfaa")
    c+=t(1135,300,"CODMASH.COM  /  LET'S BUILD",13,MUTED,700,"end",1,1)
    return frame(w,h,c,"CodMash contact banner")


def runner():
    w,h=300,150
    c=f'<ellipse cx="154" cy="136" rx="105" ry="9" fill="#fdad60" opacity=".28"/>'
    c+=boy(79,-5,.39)
    c+=f'<path d="M29 110h56 M17 121h62 M211 71h57" stroke="{ORANGE}" stroke-width="5" stroke-linecap="round" opacity=".7"/>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'+common_defs()+c+'</svg>'


FILES = {
    "hero.svg": hero(),
    "team.svg": team(),
    "mission.svg": mission(),
    "stack.svg": stack(),
    "identity.svg": identity(),
    "contribution.svg": contribution(),
    "contact.svg": contact(),
    "runner.svg": runner(),
}
for filename, content in FILES.items():
    (OUT / filename).write_text(content, encoding="utf-8")
    print(filename, len(content))
