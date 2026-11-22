#!/usr/bin/env python3
"""Build ads_map.html: the business ads placed on a schematic street grid (Michiko, 2026-11-22).

Run AFTER build_viewer.py (which writes ads.html):  python3 build_ads_map.py   (from pipeline/)

Reads the ADS list baked into ../ads.html, so the map always shows exactly the ads on the ads page.
Streets and spots come from pipeline/ads_map_geo.json (real geometry from a modern Philadelphia address-point file;
see ads_map_prep.py), so the map is to scale.
  * Philadelphia renumbered its houses in 1857 and those numbers still stand. An ad of 1857 or later is placed at
    today's address point for its house number (or between the nearest neighbours on the same side; or, failing
    that, by the 100-to-the-block rule). Period street names are translated in EW_NAME / NS_NAME.
  * Ads before 1857 carry old house numbers: they are placed ONLY from a cross street the ad itself gives,
    through the SPECIAL table; entries marked approx are shown with a dashed ring.
  * An address with no house number and no cross street, a street not located, or a place outside the map is
    NOT placed: it is listed under the map with the reason.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# ---- real street geometry (pipeline/ads_map_geo.json, made once by ads_map_prep.py from a modern Philadelphia
#      address-point file). Coordinates are metres: x grows east, y grows south, grid square to the page.
GEO = json.load(open(os.path.join(HERE, "ads_map_geo.json")))
PTS = GEO["pts"]
RUNS = {}
for _s in GEO["streets"]:
    RUNS.setdefault(_s["n"], []).append(_s)
SIDE = 14.0                                             # metres from the centre line when only the side of the street is known

def centre(name, at=None):
    """centre-line coordinate of a street: the run containing `at` (position along it), else the longest run"""
    runs = RUNS[name]
    if at is not None:
        for r in runs:
            if r["a"] <= at <= r["b"]:
                return r["ca"]
    return max(runs, key=lambda r: r["b"] - r["a"])["ca"]

# period street name -> today's name in the address file
EW_NAME = {"market": "MARKET ST", "chestnut": "CHESTNUT ST", "chesnut": "CHESTNUT ST", "walnut": "WALNUT ST", "spruce": "SPRUCE ST",
           "pine": "PINE ST", "lombard": "LOMBARD ST", "south": "SOUTH ST", "shippen": "BAINBRIDGE ST", "catharine": "CATHARINE ST",
           "christian": "CHRISTIAN ST", "carpenter": "CARPENTER ST", "washington": "WASHINGTON AVE", "arch": "ARCH ST", "race": "RACE ST",
           "vine": "VINE ST", "callowhill": "CALLOWHILL ST", "locust": "LOCUST ST",
           "jayne": "RANSTEAD ST", "sansom": "SANSOM ST", "barley": "WAVERLY ST", "addison": "ADDISON ST", "rodman": "RODMAN ST",
           "gaskill": "GASKILL ST", "cherry": "CHERRY ST", "wood": "WOOD ST"}
NS_NAME = {"front": "FRONT ST", "second": "2ND ST", "third": "3RD ST", "fourth": "4TH ST", "fifth": "5TH ST", "sixth": "6TH ST",
           "seventh": "7TH ST", "eighth": "8TH ST", "ninth": "9TH ST", "tenth": "10TH ST", "eleventh": "11TH ST", "twelfth": "12TH ST",
           "thirteenth": "13TH ST", "broad": "BROAD ST", "2d": "2ND ST", "3d": "3RD ST", "2nd": "2ND ST", "3rd": "3RD ST",
           "raspberry": "HUTCHINSON ST", "currant": "WARNOCK ST", "juniper": "JUNIPER ST"}
for _i in range(4, 19):
    NS_NAME[f"{_i}th"] = "BROAD ST" if _i == 14 else f"{_i}TH ST"
# the regular grid, for house numbers the address file cannot answer: numbered streets by index, hundred-blocks by street
GRID_X = [(1, "FRONT ST"), (2, "2ND ST"), (3, "3RD ST")] + [(i, f"{i}TH ST") for i in range(4, 14)] + [(14, "BROAD ST")] + [(i, f"{i}TH ST") for i in range(15, 19)]
GRID_Y = [(-4, "CALLOWHILL ST"), (-3, "VINE ST"), (-2, "RACE ST"), (-1, "ARCH ST"), (0, "MARKET ST"), (1, "CHESTNUT ST"), (2, "WALNUT ST"),
          (3, "SPRUCE ST"), (4, "PINE ST"), (5, "LOMBARD ST"), (6, "SOUTH ST"), (7, "BAINBRIDGE ST"), (8, "CATHARINE ST"),
          (9, "CHRISTIAN ST"), (10, "CARPENTER ST"), (11, "WASHINGTON AVE")]

def interp(table, t):
    pts = [(i, centre(n)) for i, n in table]
    for (i0, c0), (i1, c1) in zip(pts, pts[1:]):
        if t <= i1 or (i1, c1) == pts[-1]:
            if t >= i0 or (i0, c0) == pts[0]:
                return c0 + (c1 - c0) * (t - i0) / (i1 - i0)
    return pts[-1][1]

def geocode(num, street, prefix=""):
    """modern address point for a house number: exact, or between the nearest same-side neighbours. -> (x, y, how) or None"""
    L = PTS.get((prefix + " " if prefix else "") + street) or []
    same = [p for p in L if p[0] % 2 == num % 2]
    ex = [p for p in same if p[0] == num]
    if ex:
        return sum(p[1] for p in ex) / len(ex), sum(p[2] for p in ex) / len(ex), "exact"
    lo = [p for p in same if p[0] < num]; hi = [p for p in same if p[0] > num]
    lo = max(lo, key=lambda p: p[0]) if lo else None; hi = min(hi, key=lambda p: p[0]) if hi else None
    if lo and hi and hi[0] - lo[0] <= 40:
        f = (num - lo[0]) / (hi[0] - lo[0])
        return lo[1] + (hi[1] - lo[1]) * f, lo[2] + (hi[2] - lo[2]) * f, "near"
    for nb in (lo, hi):
        if nb and abs(nb[0] - num) <= 6:
            return nb[1], nb[2], "near"
    return None

HOW = {"exact": "Placed at today's address point for this house number.",
       "near": "Placed between today's nearest house numbers on the same side of the street.",
       "block": "Placed by house number on its block and side of the street (no matching address point today)."}

def on_ns(ns, ew, along=0.0, side=None):
    """a spot on north-south street `ns`, `along` metres NORTH (+) or south (-) of east-west street `ew`"""
    y = centre(ew) - along; x = centre(ns, y)
    return x + (SIDE if side == "E" else -SIDE if side == "W" else 0), y, "v"

def on_ew(ew, ns, along=0.0, side=None):
    """a spot on east-west street `ew`, `along` metres WEST (+, 'above') or east (-) of north-south street `ns`"""
    x = centre(ns) - along; y = centre(ew, x)
    return x, y + (SIDE if side == "S" else -SIDE if side == "N" else 0), "h"

def mid_ew(ew, ns1, ns2, side=None):
    x = (centre(ns1) + centre(ns2)) / 2; y = centre(ew, x)
    return x, y + (SIDE if side == "S" else -SIDE if side == "N" else 0), "h"

def mid_ns(ns, ew1, ew2, side=None):
    y = (centre(ew1) + centre(ew2)) / 2; x = centre(ns, y)
    return x + (SIDE if side == "E" else -SIDE if side == "W" else 0), y, "v"

# ---- hand placements: substring of the printed address -> (spot, approx?, note). Used for old (pre-1857) house
#      numbers and for ads that give a cross street instead of a number.
SPECIAL = [
    ("300 Cherry Street, above Thirteenth", lambda: on_ew("CHERRY ST", "13TH ST", 25), False, "Cherry Street just above Thirteenth, as the ad says (old house number)."),
    ("189 South Sixth", lambda: on_ns("6TH ST", "PINE ST", -55), True, "Old (pre-1857) house number. Placed on Sixth below Pine by comparison with the 1827 ad for No. 182 South Sixth, 'below Pine'."),
    ("Broad and Willow", lambda: on_ns("BROAD ST", "CALLOWHILL ST", 70), True, "Coal yard at Broad and Willow. Willow Street ran just above Callowhill."),
    ("157 North Second", lambda: on_ns("2ND ST", "RACE ST", 60, "E"), False, "North Second between Race and New, east side, as the ad says (old house number)."),
    ("137 Lombard Street, between Fifth and Sixth", lambda: mid_ew("LOMBARD ST", "5TH ST", "6TH ST"), False, "Lombard between Fifth and Sixth, as the ad says (old house number)."),
    ("218, South Sixth", lambda: on_ns("6TH ST", "LOMBARD ST", 20), True, "Old (pre-1857) house number with no cross street. Placed a little below No. 182 ('below Pine')."),
    ("122 North-Third", lambda: on_ns("3RD ST", "RACE ST", 40), False, "North Third above Race, as the ad says (old house number)."),
    ("Currant-alley", lambda: on_ns("WARNOCK ST", "LOCUST ST", 18), True, "Currant Alley, third door above Locust. The alley is taken to be today's Warnock Street."),
    ("51 South Fourth", lambda: mid_ns("4TH ST", "CHESTNUT ST", "WALNUT ST"), False, "South Fourth between Chesnut and Walnut, as the ad says (old house number)."),
    ("64 Walnut", lambda: on_ew("WALNUT ST", "3RD ST", 25), False, "Walnut, three doors above Third, as the ad says (old house number)."),
    ("182, South Sixth", lambda: on_ns("6TH ST", "PINE ST", -20), False, "South Sixth below Pine, as the ad says (old house number)."),
    ("South-Fourth-St., above Lombard", lambda: on_ns("4TH ST", "LOMBARD ST", 22), False, "South Fourth above Lombard, as the ad says."),
    ("Shippen St. between 8th and 9th, south side", lambda: mid_ew("BAINBRIDGE ST", "8TH ST", "9TH ST", "S"), False, "Shippen (today Bainbridge) between 8th and 9th, south side, as the ad says."),
    ("South Sixth St., above Walnut", lambda: on_ns("6TH ST", "WALNUT ST", 22), False, "South Sixth above Walnut, as the ad says (no house number)."),
    ("South Seventh Street, below Pine", lambda: on_ns("7TH ST", "PINE ST", -22), False, "South Seventh below Pine, as the ad says (no house number)."),
    ("Lombard Street, between Fourth and Fifth", lambda: mid_ew("LOMBARD ST", "4TH ST", "5TH ST"), False, "Lombard between Fourth and Fifth, as the ad says (no house number)."),
    ("four doors above Eleventh, north side", lambda: on_ew("SOUTH ST", "11TH ST", 30, "N"), False, "South Street, four doors above Eleventh, north side, as the ad says."),
    ("Juniper Street, between Spruce and Pine", lambda: mid_ns("JUNIPER ST", "SPRUCE ST", "PINE ST"), False, "Juniper between Spruce and Pine, as the ad says."),
    ("third door above Lombard", lambda: on_ns("7TH ST", "LOMBARD ST", 20), False, "South Seventh, third door above Lombard, as the ad says."),
    ("South Fifth Street above Walnut", lambda: on_ns("5TH ST", "WALNUT ST", 22), False, "South Fifth above Walnut, as the ad says (no house number)."),
    ("257 Raspberry", lambda: on_ns("HUTCHINSON ST", "SPRUCE ST", 15), True, "Raspberry Street, second door above Spruce. The street is taken to be today's Hutchinson Street."),
    ("1216, 1218 & 1220 Washington", lambda: geocode(1218, "WASHINGTON AVE")[:2] + ("h",) if geocode(1218, "WASHINGTON AVE") else on_ew("WASHINGTON AVE", "12TH ST", 30, "S"), False, "Washington Avenue above Twelfth, south side, as the ad says."),
]
SPECIAL.append(("615 Jayne Street", lambda: (interp(GRID_X, 6.15), (centre("MARKET ST") + centre("CHESTNUT ST")) / 2 - SIDE, "h"), False,
                "Jayne Street (today Ranstead) ran between Market and Chestnut; placed between Sixth and Seventh, as the ad says."))
SPECIAL.append(("1230 Wood St.", lambda: (geocode(1230, "WOOD ST") or by_block(1230, "WOOD ST", "h"))[:2] + ("h",), False,
                "Placed at the Wood Street address. The ad also gives 1618 North 11th St., which is north of this map."))
# addresses we deliberately do not place, with the reason shown to the reader
NOPLACE = [
    ("Helmuth", "street not yet located"), ("Russell", "street not yet located"),
    ("Minster", "street not yet located"), ("Union Street", "no house number"),
    ("Frankford", "outside the map area"), ("Newtown", "outside the map area"),
    ("abv. Poplar", "outside the map area"), ("Franklin Hall", "a concert notice, not a business address"),
]

# ---- addresses the ad itself does not print (or prints without a number), supplied by Michiko from her research.
#      title substring -> address to place it at. The pop-up says the address is not from the ad.
OWNER_PLACED = [
    ("Organs for Sale, church organs built by Joseph H. Carter", "1249 South Street"),
    ("Mrs. H. T. O'Donnell, boarding house", "913 Lombard Street"),
    ("Mrs. H. S. Duterte, General Undertaker", "634 Lombard Street"),
    ("Lodging (Mrs. Julia A. Brown)", "610 South 8th Street"),
    # Michiko 2026-11-22: Thomas J. Bowers was at 634 Lombard. His 1864 ad was read as "631 Lombard Street, above Sixth".
    ("Coal Yard (Thos. J. Bowers)", "634 Lombard Street",
     "The house number in this 1864 ad was read as 631. Thomas J. Bowers's yard was at 634 Lombard, as his 1865 ads print, and it is placed there."),
]

# ---- business type -> (emoji, ring colour, label); first match on the ad title wins
TYPES = [
    (r"dentist", "🦷", "#2f7fb8", "Dentist"),
    (r"cupping|leech|bleeding", "🩸", "#b3261e", "Cupping and leeching"),
    (r"undertaker", "⚰️", "#4a3f35", "Undertaker"),
    (r"shroud|laying out|^Miss Jane Johnson$", "🕯️", "#6b5b95", "Shrouding and laying out"),
    (r"physician|doctress|\bM\. ?D\b|\bDr\.|tonic", "🩺", "#b3261e", "Physician or remedy"),
    (r"dress-?mak|cutting system", "👗", "#b5488f", "Dressmaking"),
    (r"coal|stove", "🔥", "#d2691e", "Coal and stoves"),
    (r"ice cream|bakery|confection", "🍦", "#d6478f", "Ice cream, cakes"),
    (r"oyster|restaurant|eating saloon", "🍽️", "#c0392b", "Restaurant"),
    (r"grocer|flour|provision", "🛒", "#2e8b57", "Grocery"),
    (r"shoe|boot", "👞", "#8b5a2b", "Boots and shoes"),
    (r"tailor", "✂️", "#34618f", "Tailor"),
    (r"dye|scouring|sponging", "🧺", "#1f8a8a", "Dyeing and scouring"),
    (r"clothing", "👔", "#34618f", "Clothing"),
    (r"wig|hair|dressing-room|barber", "💈", "#c2185b", "Hair and wigs"),
    (r"dry goods|trimming|hosiery|notion|fancy goods|goods|removed to|Shorter Hawkins", "🧵", "#8e44ad", "Dry goods and trimmings"),
    (r"china|queensware|glass", "🫖", "#2a9d8f", "China and glass"),
    (r"book depository|book-store|periodical|printing", "📚", "#7b5e2a", "Books and printing"),
    (r"piano|music|organ", "🎹", "#33415c", "Music"),
    (r"school|teacher|lessons|navigation|military instruction", "🎓", "#1e6f5c", "Schools and lessons"),
    (r"boarding|lodg|hotel|travelling public|house of application", "🛏️", "#5c7c2f", "Boarding and lodging"),
    (r"intelligence|employment|help wanted", "💼", "#46627f", "Employment office"),
    (r"claim|agency|insurance", "🎖️", "#946b00", "Soldiers' claims"),
    (r"oil", "🛢️", "#555555", "Oil"),
    (r"room to rent", "🔑", "#777777", "Rooms"),
]
DEFAULT_TYPE = ("📌", "#8a6418", "Other")


def ad_type(title):
    for pat, emo, col, lab in TYPES:
        if re.search(pat, title, re.I):
            return emo, col, lab
    return DEFAULT_TYPE


NS_RE = re.compile(r"(\d+)(?:\s*1/2)?(?: & \d+)?,?\s+(South|North|S\.|N\.)[ -]+([A-Za-z0-9]+)", re.I)
EW_RE = re.compile(r"(\d+)(?:\s*1/2)?,?\s+([A-Z][a-z]+)[ -]+(?:St\b|st\b|Street|street|Avenue)")


def by_block(n, name, o, north=False):
    """the regular grid: 100 numbers to the block; odd = north / east side"""
    if o == "v":
        y = interp(GRID_Y, n / 100.0 * (-1 if north else 1)); x = centre(name, y)
        return x + (SIDE if n % 2 else -SIDE), y
    x = interp(GRID_X, n / 100.0); y = centre(name, x)
    return x, y + (-SIDE if n % 2 else SIDE)


def place_one(addr, iso):
    """-> ((x, y, approx, note, orientation), None) or (None, reason)"""
    for key, why in NOPLACE:
        if key in addr:
            return None, why
    for key, fn, approx, note in SPECIAL:
        if key in addr:
            x, y, o = fn()
            return (x, y, approx, note, o), None
    if iso < "1857":
        return None, "old (pre-1857) house number and no cross street in the ad"
    m = NS_RE.search(addr)
    if m and m.group(3).lower() in NS_NAME:
        n = int(m.group(1)); name = NS_NAME[m.group(3).lower()]; north = m.group(2)[0] in "Nn"
        g = geocode(n, name, "N" if north else "S")
        if g:
            return (g[0], g[1], False, HOW[g[2]], "v"), None
        x, y = by_block(n, name, "v", north)
        return (x, y, False, HOW["block"], "v"), None
    m = EW_RE.search(addr)
    if m and m.group(2).lower() in EW_NAME:
        n = int(m.group(1)); name = EW_NAME[m.group(2).lower()]
        g = geocode(n, name)
        if g:
            return (g[0], g[1], False, HOW[g[2]], "h"), None
        if name in RUNS:
            x, y = by_block(n, name, "h")
            return (x, y, False, HOW["block"], "h"), None
        return None, "street not yet located"
    if re.search(r"\d", addr):
        return None, "street not yet located"
    return None, "no house number"


# ---- what the page draws
X_MIN, X_MAX = centre("18TH ST") - 170, centre("FRONT ST") + 330
Y_MIN, Y_MAX = centre("CALLOWHILL ST") - 190, centre("WASHINGTON AVE") + 190
LABEL = {"BAINBRIDGE ST": "Shippen (now Bainbridge)", "WAVERLY ST": "Barley (now Waverly)", "RANSTEAD ST": "Jayne (now Ranstead)",
         "HUTCHINSON ST": "Raspberry (now Hutchinson)", "WARNOCK ST": "Currant Alley (now Warnock)", "WASHINGTON AVE": "Washington Av."}
MINOR_LABELLED = {"RODMAN ST", "WAVERLY ST", "ADDISON ST", "GASKILL ST", "CHERRY ST", "SANSOM ST", "RANSTEAD ST", "WOOD ST",
                  "HUTCHINSON ST", "WARNOCK ST", "JUNIPER ST", "LOCUST ST"}


def nice(n):
    if n in LABEL: return LABEL[n]
    w = n.rsplit(" ", 1)[0].title()
    return re.sub(r"(\d+)(St|Nd|Rd|Th)", lambda m: m.group(1) + m.group(2).lower(), w)


def street_list():
    main = {n for _, n in GRID_X} | {n for _, n in GRID_Y} | {"LOCUST ST"}
    out = []
    for n in sorted(main - {"LOCUST ST"}):                 # the main grid: one clean line across the map
        r = max(RUNS[n], key=lambda r: r["b"] - r["a"])
        lo, hi = (X_MIN, X_MAX - 250) if r["o"] == "h" else (Y_MIN, Y_MAX)
        out.append({"o": r["o"], "c": r["ca"], "a": round(lo, 1), "b": round(hi, 1), "m": 1, "l": nice(n)})
    for n, runs in RUNS.items():
        if n in main - {"LOCUST ST"}: continue
        for r in runs:
            lo, hi = (X_MIN, X_MAX - 250) if r["o"] == "h" else (Y_MIN, Y_MAX)
            a, b = max(r["a"], lo), min(r["b"], hi)
            if b - a < 40 or not ((Y_MIN if r["o"] == "h" else X_MIN) < r["ca"] < (Y_MAX if r["o"] == "h" else X_MAX - 250)): continue
            out.append({"o": r["o"], "c": r["ca"], "a": round(a, 1), "b": round(b, 1), "m": 0, "l": nice(n) if n in MINOR_LABELLED else ""})
    return out


def main():
    h = open(os.path.join(ROOT, "ads.html"), encoding="utf-8").read()
    ADS = json.loads(re.search(r"const ADS\s*=\s*(\[.*?\]);\s*const e=", h, re.S).group(1))
    places = {}; off = []; n_on = 0
    for a in ADS:
        emo, col, lab = ad_type(a["title"])
        rec = {"t": a["title"], "img": a["img"], "paper": a["paper"], "date": a["date"], "iso": a["iso"], "issue": a["issue"],
               "page": a["page"], "people": a["people"], "addr": a["addr"], "emo": emo, "col": col, "lab": lab}
        got = None; reason = "no address in the ad" if not a["addr"] else None
        for ad in a["addr"]:
            p, why = place_one(ad, a["iso"])
            if p:
                got = p; break
            reason = reason or why
        for entry in OWNER_PLACED:                          # Michiko's placements come first
            if entry[0] in a["title"]:
                p, why = place_one(entry[1], "1860")
                if p:
                    got = p
                    rec["own"] = entry[2] if len(entry) > 2 else f"This ad does not print a house number. It is placed at {entry[1]} from 1838 Black Metropolis research."
        if got and Y_MIN <= got[1] <= Y_MAX and X_MIN <= got[0] <= X_MAX:
            key = (round(got[0], 1), round(got[1], 1))
            pl = places.setdefault(key, {"x": key[0], "y": key[1], "approx": got[2], "note": got[3], "o": got[4], "ads": []})
            pl["ads"].append(rec); n_on += 1
        else:
            rec["why"] = reason or "outside the map area"; off.append(rec)
    P = sorted(places.values(), key=lambda p: (p["y"], p["x"]))
    for p in P:
        p["ads"].sort(key=lambda r: r["iso"])
        labs = [r["lab"] for r in p["ads"]]                 # the place's icon: its commonest business type (ties: the earliest ad)
        top = max(p["ads"], key=lambda r: (labs.count(r["lab"]), -labs.index(r["lab"])))
        p["emo"], p["col"], p["lab"] = top["emo"], top["col"], top["lab"]
    off.sort(key=lambda r: r["iso"])
    legend = []
    seen = set()
    for p in P:
        for r in p["ads"]:
            if r["lab"] not in seen:
                seen.add(r["lab"]); legend.append([r["emo"], r["col"], r["lab"]])
    legend.sort(key=lambda t: t[2])
    tpl = open(os.path.join(HERE, "ads_map_template.html"), encoding="utf-8").read()
    gx = sorted(centre(n) for _, n in GRID_X); gy = sorted(centre(n) for _, n in GRID_Y)
    view = {"x0": round(X_MIN), "x1": round(X_MAX), "y0": round(Y_MIN), "y1": round(Y_MAX), "river": round(centre("FRONT ST") + 150),
            "gx": gx, "gy": gy, "core": [centre("12TH ST") - 60, centre("3RD ST") + 60, centre("WALNUT ST") - 60, centre("CATHARINE ST") + 40]}
    out = (tpl.replace("/*PLACES*/[]", json.dumps(P, ensure_ascii=False, separators=(",", ":")))
              .replace("/*STREETS*/[]", json.dumps(street_list(), separators=(",", ":")))
              .replace("/*VIEW*/{}", json.dumps(view, separators=(",", ":")))
              .replace("/*OFF*/[]", json.dumps(off, ensure_ascii=False, separators=(",", ":")))
              .replace("{{N_ON}}", str(n_on)).replace("{{N_PLACES}}", str(len(P))).replace("{{N_OFF}}", str(len(off))))
    open(os.path.join(ROOT, "ads_map.html"), "w", encoding="utf-8").write(out)
    import collections
    print("placement:", dict(collections.Counter(("approx" if p["approx"] else "exact point" if p["note"] == HOW["exact"] else "between neighbours" if p["note"] == HOW["near"] else "block rule" if p["note"] == HOW["block"] else "cross street") for p in P)))
    print(f"ads map: {n_on} ads at {len(P)} places; {len(off)} not placed; {len(out)} bytes")
    for r in off:
        print(f"   not placed: {r['iso'][:4]} {r['t'][:50]:50} | {' ; '.join(r['addr'])[:50]:50} | {r['why']}")


if __name__ == "__main__":
    main()
