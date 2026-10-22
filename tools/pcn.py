"""Minimal PCN (Portable Curling Notation, https://github.com/shinagaki/pcn) reader: layers 1-3 only.

Yields, for every shot of every end, the position before and after the stone, the call (task, rotation,
World Curling rating), the thrower, and the score entering the end.
"""
import math, re

R, HOUSE = 0.145, 1.829
TASKS = {'D': 'Draw', 'F': 'Front guard', 'G': 'Guard', 'R': 'Raise / tap back', 'W': 'Wick / soft peel', 'Z': 'Freeze',
         'T': 'Take-out', 'H': 'Hit and roll', 'C': 'Clearing', 'S': 'Double take-out', 'P': 'Promotion take-out'}

def parse_stones(line):
    out = []
    for tok in line[1:].split():
        m = re.fullmatch(r'([RY])(-?[\d.]+),(-?[\d.]+)(\*?)', tok)
        out.append((0 if m[1] == 'R' else 1, float(m[2]), float(m[3]), bool(m[4])))
    return out

def parse(text):
    meta, ends, end = {}, [], None
    for raw in text.splitlines():
        line = raw.split(' ;')[0].strip() if not raw.startswith(';') else ''
        if not line: continue
        if m := re.fullmatch(r'\[(\w+) "(.*)"\]', line): meta[m[1]] = m[2]
        elif m := re.match(r'End (\d+) hammer=([RY])', line):
            end = {'end': int(m[1]), 'hammer': 0 if m[2] == 'R' else 1, 'shots': []}; ends.append(end)
        elif m := re.match(r'Score (\d+)-(\d+)', line): end['score'] = (int(m[1]), int(m[2]))
        elif m := re.match(r'(\d+) ([RY]) (\S+)', line):
            code = m[3]
            end['shots'].append({'n': int(m[1]), 'team': 0 if m[2] == 'R' else 1, 'task': code[0],
                                 'turn': code[1] if len(code) > 1 else None, 'rating': int(code[2]) if len(code) > 2 and code[2].isdigit() else None})
        elif line.startswith('@'): end['shots'][-1]['after'] = parse_stones(line)
    return meta, ends

def positions(ends):
    """Attach before/after boards and the running score to every shot."""
    total = [0, 0]
    for e in ends:
        prev = []
        e['score_in'] = tuple(total)
        for s in e['shots']:
            s['before'] = prev
            prev = [(t, x, y, False) for t, x, y, _ in s['after']]
        total[0] += e['score'][0]; total[1] += e['score'][1]
    return ends

def count(stones):
    """(team, points) for the stones in the house, or (None, 0)."""
    h = sorted((math.hypot(x, y), t) for t, x, y, *_ in stones if math.hypot(x, y) - R <= HOUSE)
    if not h: return None, 0
    n = 0
    for _, t in h:
        if t != h[0][1]: break
        n += 1
    return h[0][1], n
