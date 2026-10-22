#!/usr/bin/env python3
"""Build the "Historic shots" dataset embedded in index.html.

    python3 tools/build_historic.py

Reads the PCN game files in data/, picks the positions listed in PICKS, and rewrites the block between the
HISTORIC:START / HISTORIC:END markers in index.html. To add a game, drop its .pcn file (it needs layer-3 `@` board
lines) into data/, add an entry to GAMES with the positions to feature, and re-run.
"""
import json, math, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import pcn  # noqa: E402

R = pcn.R
TEAM = ['Red', 'Yellow']
HANDLE = {'>': 'clockwise handle (curls right)', '<': 'counter-clockwise handle (curls left)', None: 'handle not recorded'}
GRADE = ['0% (missed)', '25%', '50%', '75%', '100% (made)']

# (end, stone) -> the puzzle's text. `setup` and `prompt` are shown before the pro's call is revealed, `notes` after.
# Everything here is read off the recorded board and call; nothing about intent or tactics beyond the position.
GAMES = [{
    'file': 'og2018-women-bronze-gbr-jpn.pcn',
    'id': 'og2018-w-bronze',
    'attribution': 'Positions and calls from the PCN conversion of the World Curling / CURLIT Shot by Shot results book '
                   '(PyeongChang 2018), by Shintaro Inagaki. Stone positions were read from the published diagrams and are '
                   'accurate to a few centimetres.',
    'source': 'https://github.com/shinagaki/pcn',
    'picks': {
        (1, 12): dict(
            title='Take control of the first end', tag='Hammer',
            setup='Scoreless in the first end. Red has the hammer and throws its sixth stone. Yellow’s only stone in play is lying shot '
                  'on the right side of the house, 1.55 m from the pin, and Red has a single guard out front on the right.',
            prompt='Red wants the shot rock back. What does it take to remove Yellow’s stone and still lie shot?',
            notes='Yellow’s stone was removed and the shooter finished 1.09 m from the pin, leaving Red lying one in the house with a guard still out front.'),
        (2, 4): dict(
            title='Red sits on the pin', tag='Early end',
            setup='Red leads 1–0 and Yellow has the hammer. Red holds the button (4 cm) with a second stone just in front at 42 cm. '
                  'Yellow has a lone guard on the left in the guard zone and is throwing its second stone.',
            prompt='Two Red stones are stacked up the middle. Can one stone clear them?',
            notes='One Red stone was removed and the other rolled out to the right at 1.54 m. Yellow’s shooter stopped at 0.67 m and lay shot, so the pin stone was replaced by a Yellow one.'),
        (2, 16): dict(
            title='Hammer, down one', tag='Last stone',
            setup='Red leads 1–0 and Yellow has the last stone. Red lies shot at 1.54 m on the right behind the tee line, with two more Red stones '
                  'around the edge of the house. Yellow has two stones in play, both outside the house.',
            prompt='One stone to score. Where does it need to finish?',
            notes='A draw to 1.32 m, 22 cm closer than Red’s shot stone. Yellow scored one and levelled the game at 1–1.'),
        (5, 9): dict(
            title='Red lies shot behind a Yellow guard', tag='Middle of the end',
            setup='Tied 2–2, Red with the hammer. Red’s shot stone sits on the left, 1.59 m from the pin, with a Yellow guard directly in line in front of it at 3.41 m. '
                  'Yellow throws its fifth stone.',
            prompt='Yellow’s own stone is lined up with the shot rock. Can it be put to work?',
            notes='The shooter stopped as a guard at 3.69 m while the Yellow guard was driven 1.9 m down the ice into Red’s shot stone, taking it out and finishing at 1.51 m. '
                  'Yellow went from nothing in the house to lying shot.'),
        (5, 16): dict(
            title='Twelve stones, last rock', tag='Last stone',
            setup='Tied 2–2 in a packed house. Yellow lies shot at 0.77 m, Red is second at 0.84 m, then Yellow at 0.98 m and Red at 1.13 m. Red has the last stone.',
            prompt='Red needs to climb over Yellow’s shot stone without giving up the rest of the house.',
            notes='Yellow’s shot stone was nudged back and Red’s shooter finished at 0.61 m, lying shot. Yellow’s next stone was 0.81 m away, so Red scored one and led 3–2.'),
        (7, 16): dict(
            title='Score one or keep the hammer?', tag='Last stone',
            setup='Red leads 3–2 with three ends still to play and Yellow has the last stone. Red lies shot at 1.80 m on the right behind the tee line, '
                  'Yellow is second at 2.07 m, and there is a Red guard outside the house.',
            prompt='Yellow could draw in to score one and tie, or try to leave nothing in the house. What do you call?',
            notes='Yellow cleared both house stones, leaving only the Red guard, which does not count. The end was blanked and Yellow kept the hammer for the eighth, where it scored one.'),
        (8, 16): dict(
            title='A guard in the way', tag='Last stone',
            setup='Red leads 3–2 and Yellow has the last stone. Three Red stones sit around the back and sides of the house. Yellow has a guard on the front edge of the house just right of the centre line and another at 3.70 m on the left, with the button open behind them.',
            prompt='Yellow needs one to tie. The button is open but the guard is in the way. What are the options?',
            notes='The shooter came to rest as a guard at 2.23 m and drove Yellow’s front guard back to 0.39 m from the pin. Red’s nearest stone was 1.89 m away, so Yellow scored one and tied at 3–3.'),
        (9, 16): dict(
            title='Tied, last stone, no shot rock', tag='Last stone',
            setup='Tied 3–3 in the ninth end. Red has the hammer but nothing in the house. Yellow lies shot at 1.15 m on the left, with two Red guards in front of the house, 3.5 m and 5.5 m from the tee line.',
            prompt='If Red does nothing, Yellow steals. What is Red’s best way to deal with Yellow’s stone?',
            notes='The shot missed: Yellow’s stone did not move, and Red’s guards ended at 3.74 m and 5.46 m. Yellow stole one and led 4–3 going into the last end.'),
        (10, 12): dict(
            title='Red needs the shot rock', tag='Final end',
            setup='Final end, Red trails 3–4 and has the hammer. Yellow lies shot at 0.97 m and has a guard on the centre line at 3.96 m, with a Red guard on the left at 3.17 m. Red throws its sixth stone.',
            prompt='Yellow’s guard blocks the middle. How do you get on top of the shot rock?',
            notes='A draw to 0.43 m, behind the Yellow guard, taking shot rock from Yellow’s 0.97 m.'),
        (10, 16): dict(
            title='The last stone of the bronze medal game', tag='Final end',
            setup='Final end, Red trails 3–4 and has the last stone. Red lies shot at 0.47 m, but Yellow holds the next two at 0.54 m and 0.56 m, with Red fourth at 0.68 m. '
                  'One point ties the game and sends it to an extra end, two win it.',
            prompt='Red is counting one right now. What do you call to get a second point?',
            notes='The shot missed. Yellow ended up lying shot at 0.21 m with Red’s nearest stone at 0.68 m, and Yellow stole one to win 5–3.'),
    },
}]


def spread(stones):
    """Nudge overlapping stones apart (positions come from diagrams and can touch by a few mm)."""
    pts = [list(s) for s in stones]
    for _ in range(20):
        moved = False
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                dx, dy = pts[j][1] - pts[i][1], pts[j][2] - pts[i][2]
                d = math.hypot(dx, dy)
                if d < 2 * R + 0.004:
                    ux, uy = (dx / d, dy / d) if d > 1e-6 else (1.0, 0.0)
                    push = (2 * R + 0.004 - d) / 2
                    pts[i][1] -= ux * push; pts[i][2] -= uy * push
                    pts[j][1] += ux * push; pts[j][2] += uy * push
                    moved = True
        if not moved: break
    return pts


def board(stones):
    """[[team, x, y], ...] with a trailing 1 on the stone that was just thrown."""
    return [[t, round(x, 3), round(y, 3)] + ([1] if thrown else []) for t, x, y, thrown in spread(stones)]


def surname(name):
    parts = name.split()
    return f'{parts[-1]}. {parts[0].title()}' if len(parts) > 1 and len(parts[-1]) == 1 else name.title()


def thrower(shot, hammer, players):
    first = 1 - hammer
    k = (shot['n'] + 1) // 2 if shot['team'] == first else shot['n'] // 2  # this team's k-th stone of the end
    return surname(players[shot['team']][(k - 1) // 2])


def result_text(end, shot, after):
    team, pts = pcn.count(after)
    who = 'nobody is in the house' if team is None else f'{TEAM[team]} lying {pts}'
    if shot['n'] == 16:
        sc = end['score']
        scorer = 0 if sc[0] else 1 if sc[1] else None
        return ('Blank end, no score' if scorer is None else f'{TEAM[scorer]} scored {sc[scorer]}')
    return who[0].upper() + who[1:]


def build_game(g):
    meta, ends = pcn.parse((ROOT / 'data' / g['file']).read_text(encoding='utf-8'))
    pcn.positions(ends)
    players = [[p.strip() for p in meta['RedPlayers'].split(';')], [p.strip() for p in meta['YellowPlayers'].split(';')]]
    line = [[e['score'][0] for e in ends], [e['score'][1] for e in ends]]
    out = []
    for (en, n), txt in g['picks'].items():
        e = ends[en - 1]; s = e['shots'][n - 1]
        out.append({
            'id': f'{g["id"]}-e{en}-s{n}', 'end': en, 'n': n, 'team': s['team'], 'hammer': e['hammer'], 'scoreIn': list(e['score_in']),
            'title': txt['title'], 'tag': txt['tag'], 'setup': txt['setup'], 'prompt': txt['prompt'],
            'stones': board(s['before']),
            'pro': {
                'thrower': thrower(s, e['hammer'], players), 'task': pcn.TASKS.get(s['task'], s['task']), 'handle': HANDLE[s['turn']],
                'grade': s['rating'], 'gradeText': GRADE[s['rating']] if s['rating'] is not None else 'not graded',
                'after': board(s['after']), 'result': result_text(e, s, s['after']), 'notes': txt['notes'],
            },
        })
    short = lambda k: meta[k + 'Short']
    return {
        'id': g['id'], 'event': meta['Event'], 'stage': meta.get('Stage', ''), 'date': meta.get('Date', '').replace('.', '-'), 'site': meta.get('Site', ''),
        'teams': [{'name': meta['Red'], 'short': short('Red'), 'players': players[0]}, {'name': meta['Yellow'], 'short': short('Yellow'), 'players': players[1]}],
        'final': [int(x) for x in meta['Result'].split('-')], 'lineScore': line, 'nEnds': int(meta['Ends']),
        'attribution': g['attribution'], 'source': g['source'], 'positions': out,
    }


def main():
    data = [build_game(g) for g in GAMES]
    blob = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    new, n = re.subn(r'/\*HISTORIC:START\*/.*?/\*HISTORIC:END\*/', lambda m: '/*HISTORIC:START*/' + blob + '/*HISTORIC:END*/', html, flags=re.S)
    if n != 1: sys.exit('HISTORIC markers not found in index.html')
    (ROOT / 'index.html').write_text(new, encoding='utf-8')
    print(f'{sum(len(g["positions"]) for g in data)} positions from {len(data)} game(s), {len(blob)} bytes')


if __name__ == '__main__':
    main()
