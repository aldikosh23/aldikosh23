import base64
import html
import json
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(REPO_ROOT, 'README.md')
OWNER = 'aldikosh23'
SELF_REPO = OWNER + '/aldikosh23'
START = '<!-- REPOS:START -->'
END = '<!-- REPOS:END -->'

LANG_COLORS = {
    'Swift': 'F05138',
    'TypeScript': '3178C6',
    'Python': '3572A5',
    'JavaScript': 'f1e05a',
    'Go': '00ADD8',
    'Rust': 'dea584',
    'C++': 'f34b7d',
    'C': '555555',
    'HTML': 'e34c26',
    'Shell': '89e051',
}


def repos():
    out = subprocess.check_output(
        ['gh', 'api', f'users/{OWNER}/repos?per_page=100&sort=updated'],
        env={**os.environ}, text=True)
    items = json.loads(out)
    keep = [r for r in items
            if not r['fork'] and not r['private'] and f"{OWNER}/{r['name']}" != SELF_REPO]
    return keep


def render(rs):
    cols = 3 if len(rs) >= 3 else max(len(rs), 1)
    rows = []
    for i in range(0, len(rs), cols):
        chunk = rs[i:i + cols]
        width = 100 // cols
        cells = []
        for r in chunk:
            name = html.escape(r['name'])
            url = html.escape(r['html_url'])
            desc = html.escape(r['description'] or '')
            parts = []
            if r['language']:
                color = LANG_COLORS.get(r['language'], '8b949e')
                lang = html.escape(r['language'])
                parts.append(
                    f'<img src="https://img.shields.io/badge/{lang.replace(" ", "_")}-{color}'
                    f'?style=flat-square" alt="{lang}"/>')
            stars = r['stargazers_count']
            if stars:
                parts.append(f'<img src="https://img.shields.io/badge/%E2%98%85-{stars}-0f5c43'
                             f'?style=flat-square" alt="stars"/>')
            if r['homepage']:
                parts.append(f'<a href="{html.escape(r["homepage"])}"><b>&#9654; live</b></a>')
            cells.append(
                f'<td width="{width}%" valign="top">'
                f'<h4><a href="{url}">{name}</a></h4>'
                f'{desc}<br/><br/>'
                f'<sub>{" ".join(parts)}</sub>'
                f'</td>')
        while len(cells) < cols:
            cells.append('<td></td>')
        rows.append('<tr>' + ''.join(cells) + '</tr>')
    return '<table>\n  ' + '\n  '.join(rows) + '\n</table>'


def main():
    rs = repos()
    block = f'{START}\n{render(rs)}\n{END}'
    text = open(README, encoding='utf-8').read()
    if START in text:
        import re
        new = re.sub(re.escape(START) + r'.*?' + re.escape(END), block, text, flags=re.S)
    else:
        anchor = '### Tools I build with'
        new = text.replace(anchor, f'### Repos\n\n{block}\n\n{anchor}', 1)
    if new == text:
        print('no changes')
        return
    open(README, 'w', encoding='utf-8').write(new)
    print('README updated:', len(rs), 'repos')


if __name__ == '__main__':
    sys.exit(main())
