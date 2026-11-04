"""Build the self-contained Codmash README images (Python standard library only).

python3 build_assets.py             # Rebuild from the checked-in public snapshot
python3 build_assets.py --refresh   # Refresh public GitHub data, then rebuild
python3 build_assets.py --preview   # Also create .preview/index.html
"""
from __future__ import annotations

import argparse
import base64
from datetime import date, datetime, timezone
from html import escape
from html.parser import HTMLParser
import json
import math
import os
from pathlib import Path
import re
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
DATA = ROOT / 'data' / 'github.json'
USERNAME = 'codmashdev'
ORANGE, BLUE, GOLD, GREEN = '#ff7a1a', '#4aa8ff', '#ffb52e', '#2fd48a'
WHITE, MUTED = '#eef1f7', '#8b93a7'


class ContributionParser(HTMLParser):
    """Read dates, levels and counts from GitHub's public contribution calendar."""
    def __init__(self):
        super().__init__()
        self.days = {}
        self.tooltips = {}
        self.tooltip_id = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'td' and 'data-date' in attrs:
            self.days[attrs['id']] = {
                'date': attrs['data-date'], 'level': int(attrs['data-level'])
            }
        elif tag == 'tool-tip' and 'for' in attrs:
            self.tooltip_id = attrs['for']

    def handle_data(self, text):
        if self.tooltip_id:
            self.tooltips[self.tooltip_id] = self.tooltips.get(self.tooltip_id, '') + text

    def handle_endtag(self, tag):
        if tag == 'tool-tip':
            self.tooltip_id = None

    def result(self):
        result = []
        for key, day in self.days.items():
            tooltip = self.tooltips.get(key, '').strip()
            match = re.match(r'([\d,]+) contribution', tooltip)
            if match:
                count = int(match[1].replace(',', ''))
            elif tooltip.startswith('No contributions'):
                count = 0
            else:
                raise ValueError(f'Missing contribution count for {day["date"]}')
            date.fromisoformat(day['date'])
            if not 0 <= day['level'] <= 4:
                raise ValueError('Invalid contribution level')
            result.append({**day, 'count': count})
        if len(result) < 350:
            raise ValueError('Incomplete GitHub calendar; retaining existing snapshot')
        return sorted(result, key=lambda day: day['date'])


def fetch(url):
    headers = {'User-Agent': 'codmash-profile', 'Accept': 'application/vnd.github+json'}
    if url.startswith('https://api.github.com/') and os.environ.get('GITHUB_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    with urlopen(Request(url, headers=headers), timeout=30) as response:
        return response.read().decode('utf-8')


def snapshot(user, repos, calendar):
    if user.get('login', '').lower() != USERNAME:
        raise ValueError('Unexpected GitHub account')
    parser = ContributionParser()
    parser.feed(calendar)
    days = parser.result()
    return {
        'username': USERNAME,
        'updated': datetime.now(timezone.utc).date().isoformat(),
        'repos': user['public_repos'], 'followers': user['followers'],
        'stars': sum(r['stargazers_count'] for r in repos),
        'forks': sum(r['forks_count'] for r in repos),
        'contributions': sum(d['count'] for d in days),
        'repositories': [{'name': r['name'], 'language': r['language'] or 'Other',
                          'url': r['html_url']} for r in repos],
        'days': days,
    }


def refresh():
    user = json.loads(fetch(f'https://api.github.com/users/{USERNAME}'))
    repos = []
    page = 1
    while True:
        batch = json.loads(fetch(f'https://api.github.com/users/{USERNAME}/repos?type=owner&per_page=100&page={page}'))
        if not isinstance(batch, list):
            raise ValueError('Invalid GitHub repository response')
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    result = snapshot(user, repos, fetch(f'https://github.com/users/{USERNAME}/contributions'))
    # Replace only after every source passes validation.
    DATA.write_text(json.dumps(result, indent=2) + '\n')


def t(x, y, text, size=14, color=WHITE, cls='jb', extra=''):
    return f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}" fill="{color}" {extra}>{escape(str(text))}</text>'


def rect(x, y, w, h, color='#ffffff', opacity='.03', radius=15, stroke='#272e42'):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{color}" fill-opacity="{opacity}" stroke="{stroke}"/>'


def font_css():
    return '\n'.join(
        "@font-face{font-family:'" + p.stem + "';src:url(data:font/woff2;base64," +
        base64.b64encode(p.read_bytes()).decode() + ") format('woff2')}"
        for p in sorted((ASSETS / 'fonts').glob('*.woff2'))
    )


def tech_chips():
    icons = json.loads((ASSETS / 'tech-icons.json').read_text())
    colors = ['#E34F26', '#a080bf', '#F7DF1E', '#3178C6', '#61DAFB',
              '#eef1f7', '#9293ca', '#ff6055', '#62a0ce', '#5ab5d3',
              '#95BF47', '#ff9d3a', '#b68be5', '#f77c66', '#F05032']
    chips = []
    for i, ((name, icon), color) in enumerate(zip(icons.items(), colors)):
        x, y = 462 + (i % 5) * 161, 136 + (i // 5) * 112
        icon = re.sub(r'color="#[a-fA-F0-9]+"', f'color="{color}"', icon)
        size = 10.3 if name == 'WooCommerce' else 12.5
        chips.append(f'''<g class="chip" style="animation-delay:{.45 + i * .11:.2f}s">
{rect(x, y, 152, 56, color, '.09', 14, color)}
<rect x="{x+.6}" y="{y+.6}" width="150.8" height="54.8" rx="13.4" fill="none" stroke="{color}" stroke-opacity=".25">
<animate attributeName="stroke-opacity" values=".25;.95;.25;.25" keyTimes="0;.08;.25;1" dur="6.3s" begin="{i*.3}s" repeatCount="indefinite"/></rect>
<g transform="translate({x+30},{y+28})" color="{color}" fill="{color}">{icon}</g>
{t(x+50, y+32.5, name, size)}</g>''')
    return '\n'.join(chips)


def dashboard(data):
    content = []
    for i, (key, label, color) in enumerate([
        ('repos', 'PUBLIC REPOS', ORANGE), ('stars', 'STARS EARNED', GOLD),
        ('forks', 'FORKS', BLUE), ('followers', 'FOLLOWERS', GREEN)
    ]):
        x = 420 + i * 208.5
        content.append(f'<g class="tile" style="animation-delay:{.7 + i*.1}s">' +
                       rect(x, 134, 194, 94) + rect(x+18, 148, 25, 3, color, '1', 1.5, 'none') +
                       t(x+18, 196, data[key], 33, WHITE, 'sg') +
                       t(x+18, 215, label, 9.8, MUTED, extra='letter-spacing="1.5"') + '</g>')
    content.append('<g class="tile" style="animation-delay:1.1s">' + rect(420, 248, 456, 300))
    content.append(t(442, 278, 'PUBLIC MISSIONS', 10.5, MUTED, 'jbb', 'letter-spacing="1.7"'))
    for i, repo in enumerate(data['repositories'][:5]):
        y = 318 + i * 41
        content.append(f'<circle cx="448" cy="{y-4}" r="4" fill="{ORANGE}"/>')
        content.append(t(464, y, repo['name'][:29], 13, WHITE, 'sgm'))
        content.append(t(850, y, repo['language'][:14], 10.5, BLUE, extra='text-anchor="end"'))
    content.append(t(442, 513, f"{data['contributions']} contributions in the last year", 13, ORANGE, 'sgm'))
    content.append(t(442, 535, f"github.com/{USERNAME}", 10.5, MUTED) + '</g>')
    content.append('<g class="tile" style="animation-delay:1.3s">' + rect(896, 276, 322, 230))
    content.append(t(918, 306, 'OUR SPECIALTIES', 10.5, MUTED, 'jbb', 'letter-spacing="1.7"'))
    for i, (label, detail, color) in enumerate([
        ('DESIGN', 'Web, mobile & intuitive UX', ORANGE),
        ('DEVELOP', 'Software, APIs & eCommerce', BLUE),
        ('AUTOMATE', 'AI assistants & workflows', GOLD),
    ]):
        y = 340 + i*51
        content.append(f'<circle cx="922" cy="{y}" r="3.6" fill="{color}"><animate attributeName="opacity" values="1;.3;1" dur="{2.4+i*.4}s" repeatCount="indefinite"/></circle>')
        content.append(t(936, y+4, label, 10, color, 'jbb', 'letter-spacing="1.5"'))
        content.append(t(936, y+23, detail, 13, WHITE, 'sgm'))
    content.append('</g>')
    return '\n'.join(content)


def contact_cards():
    cards = []
    for i, (name, detail, icon, color) in enumerate([
        ('Website', 'codmash.com', '&lt;/&gt;', ORANGE),
        ('Email', 'support@codmash.com', '@', '#e2383f'),
        ('GitHub', '@codmashdev', 'git', '#c77dff'),
        ('LinkedIn', 'codmashian', 'in', BLUE),
    ]):
        x, y = 690 + i%2*282, 150 + i//2*106
        cards.append(f'<g class="card" style="animation-delay:{.8+i*.12}s">' + rect(x,y,268,92))
        cards.append(f'<rect x="{x}" y="{y}" width="268" height="92" rx="16" fill="none" stroke="{color}" stroke-opacity="0"><animate attributeName="stroke-opacity" values="0;.7;0;0" keyTimes="0;.06;.2;1" dur="7.2s" begin="{i*1.1}s" repeatCount="indefinite"/></rect>')
        cards.append(rect(x+16, y+22, 46, 46, color, '.13', 13, 'none'))
        cards.append(f'<text class="jbb" x="{x+39}" y="{y+52}" font-size="18" fill="{color}" text-anchor="middle">{icon}</text>')
        cards.append(t(x+76,y+42,name,16,WHITE,'sg'))
        cards.append(t(x+76,y+63,detail,10.1,MUTED))
        cards.append(f'<g transform="translate({x+242},{y+46})"><g class="arrow" style="animation-delay:{i*.2}s"><path d="M-6 0h12M2-5l5 5-5 5" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></g></g></g>')
    return '\n'.join(cards)


def city(data, fonts):
    content = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="640" viewBox="0 0 1280 640" role="img" aria-label="Codmash contribution village">
<title>Codmash contribution village</title><desc>Each building represents a real day of public GitHub contributions. Taller buildings represent more contributions.</desc>
<defs><style>{fonts}
text{{font-family:JBM,monospace}}.sg{{font-family:SG,Arial,sans-serif;font-weight:700}}
@keyframes beacon{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}.beacon{{animation:beacon 3s ease-in-out infinite}}
@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style><linearGradient id="sky" x2="1" y2="1"><stop stop-color="#0b101b"/><stop offset="1" stop-color="#181c30"/></linearGradient>
<linearGradient id="tower" x2="0" y2="1"><stop stop-color="#ffb52e"/><stop offset="1" stop-color="#a84416"/></linearGradient></defs>
<rect width="1280" height="640" rx="24" fill="url(#sky)" stroke="#2b3249"/>
''']
    for i in range(75):
        x, y = (i * 167 + 39) % 1240 + 20, (i * 61 + 30) % 410 + 20
        content.append(f'<circle cx="{x}" cy="{y}" r="{.6+(i%3)*.3}" fill="#abc2ef" opacity=".25"/>')
    content += [t(52,55,'// OUR CONTRIBUTION VILLAGE',12,ORANGE,'jb','letter-spacing="2"'),
                t(52,108,'Every commit builds something.',32,WHITE,'sg'),
                t(52,142,f"{data['contributions']} contributions · {len(data['days'])} days · @{USERNAME}",14,MUTED),
                t(1228,55,f"UPDATED {data['updated']}",11,MUTED,extra='text-anchor="end"')]
    first = date.fromisoformat(data['days'][0]['date'])
    for day in data['days']:
        offset = (date.fromisoformat(day['date']) - first).days
        week, weekday = divmod(offset,7)
        x, y = 168 + week*18 - weekday*15, 223 + week*4.8 + weekday*9
        h = 3 if day['count'] == 0 else 12 + math.log2(day['count']+1)*24
        top = '#273349' if day['count']==0 else [GOLD,ORANGE,BLUE,GREEN][day['level']-1]
        left = '#1c273b' if day['count']==0 else '#8e451d'
        right = '#24324b' if day['count']==0 else 'url(#tower)'
        content.append(f'<g><title>{day["date"]}: {day["count"]} contributions</title>')
        content.append(f'<path d="M{x-8} {y}l8 4v{-h}l-8 -4Z" fill="{left}"/>')
        content.append(f'<path d="M{x} {y+4}l8 -4v{-h}l-8 4Z" fill="{right}"/>')
        content.append(f'<path d="M{x} {y-h-4}l8 4 -8 4 -8 -4Z" fill="{top}"/>')
        if day['count']:
            for window in range(1,int(h/11)):
                content.append(f'<path d="M{x+2} {y-h+10+window*8}l3 -1.5v3l-3 1.5Z" fill="#ffe8ac" opacity=".8"/>')
            content.append(f'<circle class="beacon" cx="{x}" cy="{y-h-7}" r="2" fill="{top}" style="animation-delay:{weekday*.35}s"/>')
        content.append('</g>')
    content += [t(52,592,'REAL ACTIVITY. REAL PROGRESS.',12,MUTED,extra='letter-spacing="1.5"'),
                t(1228,592,'One building = one day of contributions',12,MUTED,extra='text-anchor="end"'),'</svg>']
    return '\n'.join(content)


def badge(label, color, width):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="32" viewBox="0 0 {width} 32" role="img" aria-label="{escape(label)}"><rect width="{width}" height="32" rx="5" fill="{color}"/><text x="{width/2}" y="21" font-family="Arial,Helvetica,sans-serif" font-size="11" font-weight="700" fill="#ffffff" text-anchor="middle" letter-spacing="1">{escape(label)}</text></svg>'


def validate(name, svg):
    root = ET.fromstring(svg)
    assert '{{' not in svg, f'Unresolved template token in {name}'
    ids = [e.attrib['id'] for e in root.iter() if 'id' in e.attrib]
    assert len(ids) == len(set(ids)), f'Duplicate SVG ID in {name}'
    for e in root.iter():
        assert e.tag.split('}')[-1] not in ('script', 'foreignObject')
        for attr,value in e.attrib.items():
            if attr.endswith('href'):
                assert value.startswith(('data:', '#')), f'External SVG dependency in {name}'
    assert not re.search(r'Megha|Wiley|0920|meghamittal', svg, re.I), name


def build():
    data = json.loads(DATA.read_text())
    fonts = font_css()
    values = {'FONTS': fonts, 'TECH_CHIPS': tech_chips(), 'DASHBOARD': dashboard(data),
              'CONTACT_CARDS': contact_cards(), 'UPDATED': 'SYNC ' + data['updated']}
    values.update({key.upper():str(data[key]) for key in ['repos','stars','followers']})
    for token,filename in [('ART_NINJA','codmash-ninja.webp'),('ART_SQUAD','codmash-squad.webp'),('ART_TORCH','codmash-torch.webp')]:
        values[token]='data:image/webp;base64,'+base64.b64encode((ASSETS/filename).read_bytes()).decode()
    for template in sorted((ROOT/'templates').glob('*.svg')):
        svg = re.sub(r'\{\{(\w+)\}\}',lambda m:values[m[1]],template.read_text())
        validate(template.name,svg)
        (ASSETS/template.name).write_text(svg)
    contribution=city(data,fonts)
    validate('contribution.svg',contribution)
    (ASSETS/'contribution.svg').write_text(contribution)
    for label,color,width in [('WEBSITE', '#b6500e',110),('PORTFOLIO','#324b76',125),('EMAIL','#b52e35',90),('GITHUB','#673d9e',100),('LINKEDIN','#2169a4',115)]:
        (ASSETS/('badge-'+label.lower()+'.svg')).write_text(badge(label,color,width))
    (ASSETS/'badge-codmash.svg').write_text(badge('WELCOME TO CODMASH', '#b6500e',205))
    print(f"Built five animated panels, contribution village and local badges from {data['updated']} data.")


def preview():
    content = (ROOT/'README.md').read_text()
    content = re.sub(r'^## (.+)$',r'<h2>\1</h2>',content,flags=re.M)
    content = re.sub(r'^### (.+)$',r'<h3>\1</h3>',content,flags=re.M)
    content = content.replace('./assets/', '../assets/')
    folder = ROOT/'.preview'
    folder.mkdir(exist_ok=True)
    (folder/'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Codmash · README preview</title><style>
*{box-sizing:border-box}body{margin:0;background:#f6f8fa;color:#1f2328;font:16px/1.5 -apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif}article{max-width:1012px;margin:30px auto;padding:32px;background:#fff;border:1px solid #d1d9e0;border-radius:8px}img{max-width:100%;height:auto;vertical-align:middle}h2{padding-bottom:8px;border-bottom:1px solid #d1d9e0}a{color:#0969da;text-decoration:none}table{display:block;max-width:100%;overflow:auto;border-collapse:collapse;margin:16px 0}td,th{border:1px solid #d1d9e0;padding:7px 13px;text-align:left}tr:nth-child(2n){background:#f6f8fa}code{font:12px ui-monospace,monospace;background:#eff1f3;padding:3px 5px;border-radius:4px}p{margin:0 0 16px}@media(max-width:600px){article{margin:0;padding:16px;border:0}table{font-size:13px}td,th{padding:6px 9px}}@media(prefers-color-scheme:dark){body,article{background:#0d1117;color:#e6edf3}article,td,th{border-color:#30363d}tr:nth-child(2n){background:#161b22}code{background:#262c36}a{color:#58a6ff}}
</style><article>''' + content + '</article></html>')
    print('Preview: .preview/index.html')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh',action='store_true')
    parser.add_argument('--preview',action='store_true')
    args=parser.parse_args()
    if args.refresh:
        refresh()
    build()
    if args.preview:
        preview()
