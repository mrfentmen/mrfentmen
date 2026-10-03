#!/usr/bin/env python3
"""Regenerate snake.svg from this account's contribution graph.

Self-hosted: reads the GitHub GraphQL API directly with GITHUB_TOKEN and
writes an animated SVG. No third-party rendering service.

    GITHUB_TOKEN=... python3 snake.py
"""
import json
import os
import urllib.request

DUR = 24.0        # seconds per loop
CELL = 11         # px per day cell
PAD = 8
BG = '#0d1117'
SNAKE = '#00ff9d'
# GitHub's dark-theme contribution ramp
LEVELS = ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353']
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'snake.svg')

QUERY = '''
query { viewer { login contributionsCollection { contributionCalendar {
  totalContributions
  weeks { contributionDays { date contributionCount } }
} } } }
'''


def fetch_contributions():
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        raise SystemExit('GITHUB_TOKEN is required')
    req = urllib.request.Request(
        'https://api.github.com/graphql',
        data=json.dumps({'query': QUERY}).encode(),
        headers={
            'Authorization': f'bearer {token}',
            'Content-Type': 'application/json',
            'User-Agent': 'profile-snake',
        },
    )
    with urllib.request.urlopen(req) as r:
        payload = json.load(r)
    if 'errors' in payload:
        raise SystemExit(f'GraphQL error: {payload["errors"]}')
    return payload['data']['viewer']['login'], \
        payload['data']['viewer']['contributionsCollection']['contributionCalendar']


def level(count):
    if count == 0:
        return 0
    if count <= 3:
        return 1
    if count <= 7:
        return 2
    if count <= 12:
        return 3
    return 4


def build_svg(grid, cols, rows):
    # serpentine route covering every cell
    route = []
    for c in range(cols):
        order = range(rows) if c % 2 == 0 else range(rows - 1, -1, -1)
        for r in order:
            route.append((c, r))

    n = len(route)
    width = PAD * 2 + cols * CELL
    height = PAD * 2 + rows * CELL

    def cx(c):
        return PAD + c * CELL + CELL / 2

    def cy(r):
        return PAD + r * CELL + CELL / 2

    d = 'M' + ' L'.join(f'{cx(c):.1f} {cy(r):.1f}' for c, r in route)
    trail = n * CELL

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="contribution snake">',
        f'<rect width="{width}" height="{height}" fill="{BG}" rx="6"/>',
    ]

    # Grid structure (dim empty squares) is always visible so the chart reads as a
    # chart. Contribution squares stay hidden until the snake reaches them.
    pos = {p: i for i, p in enumerate(route)}

    for c in range(cols):
        for r in range(rows):
            count = grid[c][r]
            x = PAD + c * CELL
            y = PAD + r * CELL
            if count == 0:
                out.append(f'<rect x="{x}" y="{y}" width="{CELL - 1}" height="{CELL - 1}" '
                           f'rx="2" fill="{LEVELS[0]}"/>')
                continue
            t0 = pos[(c, r)] / n
            t1 = min(1.0, (pos[(c, r)] + 1) / n)
            out.append(
                f'<rect x="{x}" y="{y}" width="{CELL - 1}" height="{CELL - 1}" rx="2" '
                f'fill="{LEVELS[level(count)]}" opacity="0">'
                f'<animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite" '
                f'values="0;0;1;1" keyTimes="0;{t0:.5f};{t1:.5f};1"/></rect>'
            )

    # body draws itself along the route, leaving a trail
    out.append(
        f'<path id="route" d="{d}" fill="none" stroke="{SNAKE}" stroke-width="2.5" '
        f'stroke-linecap="round" stroke-linejoin="round" opacity="0.95" '
        f'stroke-dasharray="{trail} {trail}">'
        f'<animate attributeName="stroke-dashoffset" from="{trail}" to="0" '
        f'dur="{DUR}s" repeatCount="indefinite"/></path>'
    )

    out.append(
        f'<circle r="3.2" fill="#eafff5">'
        f'<animateMotion dur="{DUR}s" repeatCount="indefinite" rotate="auto">'
        f'<mpath href="#route" xlink:href="#route"/></animateMotion></circle>'
    )
    out.append('</svg>')
    return ''.join(out)


def main():
    login, calendar = fetch_contributions()
    weeks = calendar['weeks']
    cols = len(weeks)
    rows = 7
    grid = [[0] * rows for _ in range(cols)]
    for c, week in enumerate(weeks):
        for r, day in enumerate(week['contributionDays'][:rows]):
            grid[c][r] = day['contributionCount']

    svg = build_svg(grid, cols, rows)
    with open(OUT, 'w') as fh:
        fh.write(svg)

    active = sum(1 for c in range(cols) for r in range(rows) if grid[c][r] > 0)
    print(f'{login}: {calendar["totalContributions"]} contributions, '
          f'{active} active days, {cols} weeks -> {OUT} ({len(svg)} bytes)')


if __name__ == '__main__':
    main()