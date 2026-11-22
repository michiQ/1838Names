#!/usr/bin/env python3
"""One-time prep for the ads map (2026-11-22): turn a Philadelphia address-point file (newline-delimited GeoJSON
in the OpenAddresses layout: properties.number, properties.street, Point geometry; supplied by Michiko) into the
compact pipeline/ads_map_geo.json used by build_ads_map.py:
  - 'pts': street -> [[house number, x, y], ...] for the map area, in metres, rotated so the street grid is square
           to the page (x grows EAST, y grows SOUTH);
  - 'streets': fitted centre lines, split into runs where a street is interrupted.
Usage: python3 -I ads_map_prep.py /path/to/source.geojson
"""
import json, math, os, re, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
LAT0, LON0 = 39.9440, -75.1560
BOX = (39.928, 39.968, -75.178, -75.136)

def main(src):
    raw = []
    with open(src) as f:
        for line in f:
            i = line.find('"coordinates": [')
            if i < 0: continue
            try:
                lon, lat = map(float, line[i + 16:line.index(']', i)].split(','))
            except Exception:
                continue
            if BOX[0] < lat < BOX[1] and BOX[2] < lon < BOX[3]:
                p = json.loads(line)['properties']
                m = re.match(r'\d+', p.get('number') or '')
                if m and p.get('street'):
                    raw.append((int(m.group(0)), p['street'].upper().strip(), lon, lat))
    kx = 111320 * math.cos(math.radians(LAT0)); ky = 110540
    E = [((lon - LON0) * kx, (lat - LAT0) * ky) for _, _, lon, lat in raw]      # east, north (metres)
    # grid angle from Market Street
    ths = []
    for nm in ('PINE ST', 'LOMBARD ST', 'SPRUCE ST', 'CHRISTIAN ST'):          # long rowhouse streets give a steady angle
        for par in (0, 1):
            mk = [E[i] for i, r in enumerate(raw) if r[1] == nm and r[0] % 2 == par]
            mx = sum(p[0] for p in mk) / len(mk); my = sum(p[1] for p in mk) / len(mk)
            ths.append(math.atan2(sum((p[0] - mx) * (p[1] - my) for p in mk), sum((p[0] - mx) ** 2 for p in mk)))
    th = sorted(ths)[len(ths) // 2]
    c, s = math.cos(-th), math.sin(-th)
    pts = collections.defaultdict(list)
    for (n, st, _, _), (e, nn) in zip(raw, E):
        u = e * c - nn * s; v = e * s + nn * c
        pts[st].append([n, round(u, 1), round(-v, 1)])          # x east, y south
    def base(st): return re.sub(r'^[NS] (?=(\d+(ST|ND|RD|TH)|FRONT|BROAD|JUNIPER|HUTCHINSON|WARNOCK) )', '', st)
    groups = collections.defaultdict(list)
    for st, L in pts.items():
        if re.search(r' (ST|AVE|PL)$', st): groups[base(st)] += L
    def med(a): a = sorted(a); return a[len(a) // 2]
    streets = []
    for name, L in groups.items():
        if len(L) < 10: continue
        xs = [p[1] for p in L]; ys = [p[2] for p in L]
        sx = sorted(xs); sy = sorted(ys); q = len(L) // 20
        o = 'h' if (sx[-1 - q] - sx[q]) > (sy[-1 - q] - sy[q]) else 'v'
        A, C = (1, 2) if o == 'h' else (2, 1)                  # along index, cross index
        along = sorted(L, key=lambda p: p[A]); runs = [[along[0]]]
        for p in along[1:]:
            (runs[-1].append(p) if p[A] - runs[-1][-1][A] < 190 else runs.append([p]))
        for R in runs:
            if len(R) < 5 or R[-1][A] - R[0][A] < 40: continue
            odd = [p[C] for p in R if p[0] % 2]; even = [p[C] for p in R if not p[0] % 2]
            a0, b0 = R[0][A] - 15, R[-1][A] + 15
            # the grid is square to the page, so a run's centre line is a constant: midway between the medians of
            # its two sides (odd numbers: north side of E-W streets, east side of N-S streets)
            so = 14 if o == 'h' else -14
            cc = (med(odd) + med(even)) / 2 if len(odd) >= 3 and len(even) >= 3 else (med(odd) + so if len(odd) >= len(even) else med(even) - so)
            cen = lambda t: cc
            streets.append({'n': name, 'o': o, 'a': round(a0, 1), 'b': round(b0, 1), 'ca': round(cen(a0), 1), 'cb': round(cen(b0), 1)})
    out = {'_doc': __doc__, 'lat0': LAT0, 'lon0': LON0, 'theta': th, 'streets': streets,
           'pts': {st: sorted(L) for st, L in pts.items()}}
    json.dump(out, open(os.path.join(HERE, 'ads_map_geo.json'), 'w'), separators=(',', ':'))
    print(len(raw), 'points;', len(streets), 'street runs; grid angle', round(math.degrees(th), 2), 'deg')

if __name__ == '__main__':
    main(sys.argv[1])
