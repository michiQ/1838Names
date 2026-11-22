#!/usr/bin/env python3
"""Build ads_map.html: the business ads placed on a schematic street grid (Michiko, 2026-11-22).

Run AFTER build_viewer.py (which writes ads.html):  python3 build_ads_map.py   (from pipeline/)

Reads the ADS list baked into ../ads.html, so the map always shows exactly the ads on the ads page.
Placement is by rule, to the block, never by a geocoder:
  * Philadelphia renumbered its houses in 1857 (100 numbers to the block). For ads of 1857 and later, a house
    number on an east-west street gives the block between numbered streets (913 Lombard = 13/100 of the way
    from 9th to 10th); a number on a north-south street gives the block south or north of Market
    (427 S. 6th = between Pine and Lombard). Odd numbers are on the north and east sides, even on the south and west.
  * Ads before 1857 carry old house numbers: they are placed ONLY from a cross street the ad itself gives,
    through the SPECIAL table below; entries marked approx are shown with a dashed ring.
  * An address with no house number and no cross street, a street not located, or a place outside the grid is
    NOT placed: it is listed under the map with the reason.
The grid is schematic: blocks are drawn equal, not to scale.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# ---- grid: x = numbered street (Front=1 ... Broad=14 ... 18th), y = blocks south of Market (north is negative)
EW = {"market": 0, "chestnut": 1, "chesnut": 1, "walnut": 2, "spruce": 3, "pine": 4, "lombard": 5, "south": 6,
      "shippen": 7, "catharine": 8, "christian": 9, "carpenter": 10, "washington": 11,
      # small streets (between the main ones)
      "jayne": 0.5, "sansom": 1.5, "barley": 4.5, "addison": 4.5, "rodman": 5.5, "gaskill": 5.5,
      "cherry": -1.5, "wood": -3.4}
ORD = {"front": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9,
       "tenth": 10, "eleventh": 11, "twelfth": 12, "thirteenth": 13, "broad": 14}
for i in range(2, 19):
    ORD[f"{i}th"] = i
ORD.update({"2nd": 2, "3rd": 3, "2d": 2, "3d": 3})
SIDE = 0.13

# ---- hand placements: substring of the printed address -> (x, y, approx?, note)
SPECIAL = [
    ("300 Cherry Street, above Thirteenth", 13.1, -1.5 - SIDE, False, "placed by the cross street in the ad (old house number)"),
    ("189 South Sixth", 6 - SIDE, 4.45, True, "old (pre-1857) house number; placed below Pine by comparison with the 1827 ad for No. 182 South Sixth, 'below Pine'"),
    ("Broad and Willow", 14, -4.4, False, "coal yard at Broad and Willow"),
    ("157 North Second", 2 - SIDE, -2.3, False, "between Race and New, east side, as the ad says (old house number)"),
    ("137 Lombard Street, between Fifth and Sixth", 5.5, 5 - SIDE, False, "between Fifth and Sixth, as the ad says (old house number)"),
    ("218, South Sixth", 6 + SIDE, 4.85, True, "old (pre-1857) house number with no cross street; placed a little below No. 182 ('below Pine')"),
    ("122 North-Third", 3 + SIDE, -2.2, False, "above Race, as the ad says (old house number)"),
    ("Currant-alley", 10.5, 2.42, True, "Currant Alley, third door above Locust; the alley is placed between Tenth and Eleventh"),
    ("51 South Fourth", 4 - SIDE, 1.5, False, "between Chesnut and Walnut, as the ad says (old house number)"),
    ("64 Walnut", 3.1, 2 + SIDE, False, "three doors above Third, as the ad says (old house number)"),
    ("182, South Sixth", 6 + SIDE, 4.15, False, "below Pine, as the ad says (old house number)"),
    ("South-Fourth-St., above Lombard", 4, 4.85, False, "above Lombard, as the ad says"),
    ("Shippen St. between 8th and 9th, south side", 8.5, 7 + SIDE, False, "between 8th and 9th, south side, as the ad says"),
    ("South Sixth St., above Walnut", 6, 1.9, False, "above Walnut, as the ad says (no house number)"),
    ("South Seventh Street, below Pine", 7, 4.12, False, "below Pine, as the ad says (no house number)"),
    ("Lombard Street, between Fourth and Fifth", 4.5, 5, False, "between Fourth and Fifth, as the ad says (no house number)"),
    ("four doors above Eleventh, north side", 11.08, 6 - SIDE, False, "four doors above Eleventh, north side, as the ad says"),
    ("Juniper Street, between Spruce and Pine", 13.5, 3.5, False, "Juniper Street, between Spruce and Pine, as the ad says"),
    ("third door above Lombard", 7, 4.9, False, "third door above Lombard, as the ad says"),
    ("South Fifth Street above Walnut", 5, 1.9, False, "above Walnut, as the ad says (no house number)"),
    ("257 Raspberry", 9.5, 2.9, True, "Raspberry Street, second door above Spruce; the street is placed between Ninth and Tenth"),
    ("1216, 1218 & 1220 Washington", 12.18, 11 + SIDE, False, "above Twelfth, south side, as the ad says"),
    ("52 & 54 North Sixth", 6 + SIDE, -0.53, False, ""),
    ("1230 Wood St.", 12.30, -3.4 + SIDE, False, "placed at the Wood Street address; the ad also gives 1618 North 11th St., which is north of this map"),
]
# addresses we deliberately do not place, with the reason shown to the reader
NOPLACE = [
    ("Helmuth", "street not located on this grid"), ("Russell", "street not located on this grid"),
    ("Minster", "street not located on this grid"), ("Union Street", "no house number"),
    ("Frankford", "outside the map area"), ("Newtown", "outside the map area"),
    ("abv. Poplar", "outside the map area"), ("Franklin Hall", "a concert notice, not a business address"),
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


NS_RE = re.compile(r"(\d+)(?:\s*1/2)?,?\s+(South|North|S\.|N\.)[ -]+([A-Za-z0-9]+)", re.I)
EW_RE = re.compile(r"(\d+)(?:\s*1/2)?,?\s+([A-Z][a-z]+)[ -]+(?:St\b|st\b|Street|street|Avenue)")


def place_one(addr, iso):
    """-> (x, y, approx, note) or (None, reason)"""
    for key, why in NOPLACE:
        if key in addr:
            return None, why
    for key, x, y, approx, note in SPECIAL:
        if key in addr:
            on_ew = any(abs(abs(y - v) - d) < 0.006 for v in EW.values() for d in (0, SIDE))
            return (x, y, approx, note, "h" if on_ew else "v"), None
    if iso < "1857":
        return None, "old (pre-1857) house number and no cross street in the ad"
    m = NS_RE.search(addr)
    if m and m.group(3).lower() in ORD:
        n = int(m.group(1)); x = ORD[m.group(3).lower()]
        y = n / 100.0 * (-1 if m.group(2)[0] in "Nn" else 1)
        return (x + (-SIDE if n % 2 else SIDE), y, False, "", "v"), None
    m = EW_RE.search(addr)
    if m and m.group(2).lower() in EW:
        n = int(m.group(1)); y = EW[m.group(2).lower()]
        return (n / 100.0, y + (-SIDE if n % 2 else SIDE), False, "", "h"), None
    if re.search(r"\d", addr):
        return None, "street not located on this grid"
    return None, "no house number"


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
        if got and -4.9 <= got[1] <= 11.9 and 0.6 <= got[0] <= 18.4:
            key = (round(got[0], 2), round(got[1], 2))
            pl = places.setdefault(key, {"x": key[0], "y": key[1], "approx": got[2], "note": got[3], "o": got[4], "ads": []})
            pl["ads"].append(rec); n_on += 1
        else:
            rec["why"] = reason or "outside the map area"; off.append(rec)
    P = sorted(places.values(), key=lambda p: (p["y"], p["x"]))
    for p in P:
        p["ads"].sort(key=lambda r: r["iso"])
    off.sort(key=lambda r: r["iso"])
    legend = []
    seen = set()
    for p in P:
        for r in p["ads"]:
            if r["lab"] not in seen:
                seen.add(r["lab"]); legend.append([r["emo"], r["col"], r["lab"]])
    legend.sort(key=lambda t: t[2])
    tpl = open(os.path.join(HERE, "ads_map_template.html"), encoding="utf-8").read()
    out = (tpl.replace("/*PLACES*/[]", json.dumps(P, ensure_ascii=False, separators=(",", ":")))
              .replace("/*OFF*/[]", json.dumps(off, ensure_ascii=False, separators=(",", ":")))
              .replace("{{N_ON}}", str(n_on)).replace("{{N_PLACES}}", str(len(P))).replace("{{N_OFF}}", str(len(off))))
    open(os.path.join(ROOT, "ads_map.html"), "w", encoding="utf-8").write(out)
    print(f"ads map: {n_on} ads at {len(P)} places; {len(off)} not placed; {len(out)} bytes")
    for r in off:
        print(f"   not placed: {r['iso'][:4]} {r['t'][:50]:50} | {' ; '.join(r['addr'])[:50]:50} | {r['why']}")


if __name__ == "__main__":
    main()
