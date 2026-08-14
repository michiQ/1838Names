#!/usr/bin/env python3
"""Load the curated 'Northern Liberties Tour Sources' profiles (pipeline/nolibs_profiles.json)
onto the matching people: a short biography + a page-anchored citation to the tour PDF.
Runs AFTER apply_merges (so renames/unifications are final) and BEFORE build_viewer.
Idempotent: rebuilds the nolibs_profiles table from scratch every run. Creates the two
people the tour documents who are absent from the source data (Rebecca McCormick, James
Julius Jr.) and splits Hetty Burr out of the 'Burr, David T.' Winch record."""
import sqlite3, json, re, unicodedata, os

DB = "/tmp/black_metropolis.db"
SRC = "/tmp/repo/pipeline/nolibs_profiles.json"
PDF_URL = "Northern_Liberties_Tour_Sources.pdf"   # served alongside index.html (repo root / Drive folder)

def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z ]", "", s.lower()).strip()

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
con.execute("CREATE TABLE IF NOT EXISTS nolibs_profiles(person_id INT, story TEXT, cite TEXT, url TEXT)")
con.execute("DELETE FROM nolibs_profiles")

def get_or_create(name, source):
    r = con.execute("SELECT id FROM people WHERE canonical_name=? AND source=?", (name, source)).fetchone()
    if r: return r["id"]
    cur = con.execute("INSERT INTO people(canonical_name, norm_name, source) VALUES(?,?,?)",
                      (name, norm(name), source))
    return cur.lastrowid

def resolve_census(year, last, first, addr):
    if year == 1838:
        q = ("SELECT rowid_ FROM census_1838 WHERE last_name_of_head_of_family LIKE ? "
             "AND first_name_of_head_of_family LIKE ?")
        params = [f"%{last}%", f"%{first}%"]
        if addr: q += " AND address LIKE ?"; params.append(f"%{addr}%")
    else:
        q = ("SELECT rowid_ FROM census_1847 WHERE last_name LIKE ? AND first_name LIKE ?")
        params = [f"%{last}%", f"%{first}%"]
        if addr: q += " AND residence_street_name LIKE ?"; params.append(f"%{addr}%")
    rows = con.execute(q, params).fetchall()
    pids = []
    for r in rows:
        lk = con.execute("SELECT person_id FROM census_links WHERE census=? AND row_id=?",
                         (str(year), r["rowid_"])).fetchone()
        if lk: pids.append(lk["person_id"])
    return list(dict.fromkeys(pids))  # dedupe, keep order

def resolve(find):
    if "create" in find:
        return [get_or_create(find["create"]["name"], find["create"]["source"])]
    if "census" in find:
        return resolve_census(find["census"], find["last"], find["first"], find.get("addr"))
    if "newspaper" in find:
        r = con.execute("SELECT id FROM people WHERE canonical_name=? AND source='newspaper'", (find["newspaper"],)).fetchone()
        return [r["id"]] if r else []
    if "name" in find:
        rs = con.execute("SELECT id FROM people WHERE canonical_name=?", (find["name"],)).fetchall()
        return [r["id"] for r in rs]
    return []

data = json.load(open(SRC, encoding="utf-8"))
ok = amb = miss = 0
for p in data["profiles"]:
    pids = resolve(p["find"])
    label = json.dumps(p["find"])
    if not pids:
        print("  MISS:", label); miss += 1; continue
    if len(pids) > 1:
        print(f"  AMBIG ({len(pids)}): {label} -> pids {pids} (using first)"); amb += 1
    pid = pids[0]
    if "page" in p:
        cite = f"Northern Liberties Tour Sources (1838 Black Metropolis, 2025), p. {p['page']}"
        url = f"{PDF_URL}#page={p['page']}"
    else:
        cite = p.get("cite", {}).get("text", "1838 Black Metropolis research")
        url = None
    con.execute("INSERT INTO nolibs_profiles(person_id, story, cite, url) VALUES(?,?,?,?)",
                (pid, p["story"], cite, url))
    ok += 1

# --- Hetty Burr: trim her sketch out of David T. Burr's Winch entry (idempotent) ---
dt = con.execute("SELECT id, winch_entry FROM people WHERE canonical_name='Burr, David T.'").fetchone()
if dt and dt["winch_entry"] and "Burr, Hetty" in dt["winch_entry"]:
    trimmed = dt["winch_entry"].split("Burr, Hetty")[0].rstrip()
    con.execute("UPDATE people SET winch_entry=? WHERE id=?", (trimmed or None, dt["id"]))
    print("  trimmed Hetty Burr's sketch out of 'Burr, David T.'")

con.commit()
print(f"nolibs_profiles: {ok} loaded, {amb} ambiguous, {miss} unresolved")
