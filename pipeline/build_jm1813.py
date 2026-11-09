#!/usr/bin/env python3
"""Build extractions_jm1813.json from jm1813_rosters.json (added 2026-11-08).

Source: The Juvenile Magazine, No. 3 (Philadelphia: Arthur Donaldson, July 1, 1813), Internet
Archive scan; Michiko found it through the Bernice Dutrieuille Shelton papers at HSP.

Linking rules (Michiko, 2026-11-08):
  * Julie Winch made a record for most scholars with surnames A-G ("Attended Donaldson's school,
    1809-13"). Those scholars link to her record. Her notes stop around G, so later surnames are
    new records.
  * Every other scholar gets a NEW record ("new:jm1813"), never matched by name to a later adult.
  * Hand links Michiko confirmed: the Douglass children (Robert Jr., Sarah Mapps, George), the Appo
    children (Joseph, William, and Helen, who married Frank Johnson), and the Bogle children
    (printed Bogal / Bougal).
  * Night scholars are probably adults (Michiko); they are marked so, and still not auto-linked.
Run by hand after editing the rosters: python3 build_jm1813.py
"""
import json, os, re, sqlite3, unicodedata, difflib

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.environ.get("BM_DB", os.path.join(os.path.dirname(HERE), "black_metropolis.db"))

def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\b(jr|jun|sr)\b\.?", " ", s.replace("'", ""))
    return " ".join(re.sub(r"[^a-z ]", " ", s).split())

# Printed spellings of the same scholar in different lists -> one spelling (the first printed).
VAR = {
    "Manliff Nixon": "Manlif Nixon", "Cyrus Burton": "Cyrus R. Burten", "Henry Warters": "Henry Waters",
    "Eleven Baily": "Leven Bailey", "Silby Roads": "Selby Roads", "Sinclair Mitchell": "Sinclair Mitchel",
    "Isaiah Le Count": "Isaiah Lecount", "George Douglas": "George Douglass", "Robert Douglass": "Robert Douglass, jr.",
    "Robert Bogal": "Robert Bougal", "Alexander Pratus": "Alexander Pratos", "George Monzatus": "George Mongatus",
    "Mary Ann Nelson": "Maryann Nelson", "Elizabeth Smith": "Eliza Smith", "Elizabeth Dunken": "Elizabeth Duncan",
    "Mariah Williams": "Maria Williams", "Eliza Pancost": "Eliza Pancoast", "Juliann Mitchell": "Julian Mitchell",
    "Mariann Stotts": "Mary Ann Stotts", "Ann Wheelar": "Ann Wheeler", "Ann Moran": "Ann Morain",
    "Abigail Biot": "Abigail Biat", "Henrietta Warren": "Henrietta Warring", "Mariah Correl": "Maria Carrel",
    "Ann Mariah Bogal": "Ann Maria Bogal", "Caroline Waterford": "Carolina Waterford", "Catherine Thomas": "Catharine Thomas",
    "Joseph Johnston": "Joseph Johnson", "Jacob Johnston": "Jacob Johnson", "William Johnston": "William Johnson",
    "John Umphreys": "John Humphreys", "Robert C. Gordon": "Robert Gordon",
}
# Fixed links (record ids) confirmed by Michiko or by Winch's own notes under another spelling.
FIXED = {
    "Joseph Appo": 14195, "William Appo": 355075, "Helen Appo": 359990,
    "Robert Douglass, jr.": 899, "Sarah Douglass": 901, "George Douglass": 894,
    "Robert Bougal": 278, "Ann Maria Bogal": 274,
    "Famy Absalom": 1,          # Winch: Absalom, Fanny
    "Luner Brown": 392,         # Winch: Brown, Lunar Jr.
    "Maria Carrel": 538,        # Winch: Carroll, Maria ("Also Carrel or Correl")
    "Henrietta Gardner": 1102,  # Winch: Gardiner, Henrietta ("[Gardner] Attended Donaldson's school")
    "Robert Gordon": 1188,      # Winch: Gordon, Robert (the child, not Robert C. Gordon the grocer)
    "Cyrus R. Burten": 466,     # Winch: Burton, Cyrus R.
    "Catherine Gibbs": 1127,    # Winch: Gibbs, Catherina
    "Joseph Le Count": 1695,    # Winch: Lecount, Joseph (Michiko 2026-11-08: same man, uncle of Caroline R. Le Count)
}
# Winch notes for these scholars are buried inside another person's entry; do not link there.
NO_WINCH = {"Eleven Davis", "Jane Duffel"}

def main():
    R = json.load(open(os.path.join(HERE, "jm1813_rosters.json"), encoding="utf-8"))
    con = sqlite3.connect(DB)
    widx = {}
    for pid, cn, we in con.execute("SELECT id, canonical_name, winch_entry FROM people WHERE source='winch' AND winch_entry LIKE '%Donaldson%'"):
        if "," not in cn: continue
        sur, given = [x.strip() for x in cn.split(",", 1)]
        given = re.sub(r"\(.*?\)", "", given).strip()
        widx.setdefault(norm(f"{given} {sur}"), []).append(pid)

    kids = {}   # key -> {"name", "roles": [], "night": bool}
    order = []
    for lid, L in R["lists"].items():
        seen_here = {}
        for nm in L["names"]:
            base = VAR.get(nm, nm)
            k = base
            seen_here[base] = seen_here.get(base, 0) + 1
            if seen_here[base] > 1: k = f"{base}#{seen_here[base]}"
            if k not in kids:
                kids[k] = {"name": base, "roles": [], "night": False, "lists": set()}; order.append(k)
            kids[k]["roles"].append(L["label"]); kids[k]["lists"].add(lid)
            if L.get("night"): kids[k]["night"] = True
    # second Mary Sammons / Mary Johnson on the girls' roll are the later entrants (H2)
    for base in ("Mary Sammons", "Mary Johnson"):
        a, b = kids.get(base), kids.get(base + "#2")
        if a and b is None and "H2" in a["lists"] and "H" in a["lists"]:
            kids[base + "#2"] = {"name": base, "roles": [r for r in a["roles"] if "May-July" in r], "night": False, "lists": {"H2"}}
            a["roles"] = [r for r in a["roles"] if "May-July" not in r]; order.append(base + "#2")
    cls_seen = {}
    for nm, cl in R["classes"]["entries"]:
        base = VAR.get(nm, nm)
        if nm == "Mary Johnston": base = "Mary Johnson#2"
        cls_seen[base] = cls_seen.get(base, 0) + 1
        if base in ("Mary Sammons",) and cls_seen[base] > 1: base = "Mary Sammons#2"
        if nm == "William Thomas" and cl == "does not yet write": base = "William Thomas, jun."
        if base not in kids:   # on the class lists only (Caroline and Susan Butler)
            print("   on the class list only:", nm)
            kids[base] = {"name": base, "roles": ["in the May 1813 class lists only"], "night": False, "lists": set()}; order.append(base)
        kids[base]["roles"].append("class: " + cl)

    att, report = [], {"winch": [], "fixed": [], "new": [], "fuzzy": []}
    n_new = {}
    merged = {}   # winch id -> attendee index (two printed people collapsing onto one Winch record)
    for k in order:
        kd = kids[k]; nm = kd["name"]
        role = "; ".join(dict.fromkeys(kd["roles"]))
        pid = FIXED.get(nm)
        if pid is None and nm not in NO_WINCH:
            c = widx.get(norm(nm), [])
            if len(set(c)) == 1: pid = c[0]; report["winch"].append(nm)
            elif not c:
                # same given name, surname spelled a little differently (Burten/Burton, Fosset/Fossett)
                g, s = norm(nm).split()[0], norm(nm).split()[-1]
                hits = [(key, ids) for key, ids in widx.items() if key.split()[0] == g and difflib.SequenceMatcher(None, key.split()[-1], s).ratio() >= 0.8]
                if len(hits) == 1 and len(set(hits[0][1])) == 1:
                    pid = hits[0][1][0]; report["fuzzy"].append(f"{nm} -> {hits[0][0]}")
        elif pid is not None: report["fixed"].append(nm)
        if pid is not None:
            if pid in merged:
                a = att[merged[pid]]; a[1] += " | listed twice: " + role; continue
            merged[pid] = len(att); att.append([nm, role, pid])
        else:
            report["new"].append(nm + (" (night)" if kd["night"] else ""))
            n_new[nm] = n_new.get(nm, 0) + 1
            disp = re.sub(r",\s*(?:jun|jr)\.?$", " Jr.", nm, flags=re.I)   # "Thomas Lewis, Jr." would flip to "Jr. Thomas Lewis"
            att.append([disp, role, "new:jm1813" + ("" if n_new[nm] == 1 else "bcdef"[n_new[nm] - 2])])
    out = json.load(open(os.path.join(HERE, "jm1813_events.json"), encoding="utf-8"))
    out["events"][0]["attendees"] = att
    json.dump(out, open(os.path.join(HERE, "extractions_jm1813.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("scholars:", len(order), "| attendees:", len(att), "| winch exact:", len(report["winch"]),
          "| winch fuzzy:", len(report["fuzzy"]), "| fixed:", len(report["fixed"]), "| new:", len(report["new"]))
    for f in report["fuzzy"]: print("   fuzzy:", f)
    json.dump(report, open(os.path.join(HERE, "jm1813_match_report.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
