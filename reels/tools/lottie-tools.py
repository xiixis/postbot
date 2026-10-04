"""Две правки Lottie для роликов: перекраска в цвета бренда и сдвиг начала.

  python3 lottie-tools.py recolor in.json out.json '#00FFC8=#C7E24B' '#F5B401=#56690C'
  python3 lottie-tools.py shift   in.json out.json 2.0     # анимация начнётся на 2-й секунде
"""
import json, sys

def hex2rgb(h):
    h = h.lstrip('#'); return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]

def recolor(d, pairs):
    m = {k.upper(): hex2rgb(v) for k, v in pairs}
    n = 0
    def walk(o):
        nonlocal n
        if isinstance(o, dict):
            c = o.get('c') if o.get('ty') in ('fl', 'st', 'gf', 'gs') else None
            if isinstance(c, dict) and isinstance(c.get('k'), list) and c['k'] and not isinstance(c['k'][0], dict):
                key = '#%02X%02X%02X' % tuple(round(x * 255) for x in c['k'][:3])
                if key in m:
                    c['k'][:3] = m[key]; n += 1
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(d); return n

def shift(d, sec):
    off = round(sec * d['fr'])
    d['op'] += off
    for layer in d['layers']:
        for k in ('ip', 'op', 'st'):
            if k in layer: layer[k] += off
    return off

cmd, src, dst, *args = sys.argv[1:]
d = json.load(open(src))
if cmd == 'recolor':
    print('перекрашено мест:', recolor(d, [a.split('=') for a in args]))
elif cmd == 'shift':
    print('сдвиг кадров:', shift(d, float(args[0])))
json.dump(d, open(dst, 'w'), separators=(',', ':'))
