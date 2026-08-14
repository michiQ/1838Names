#!/usr/bin/env python3
"""Load the 1838 Mob Attack Statistics (Self-Defense & Resistance table) as a source.

Source: Michiko's live 'Self-Defense' Google Sheet (1838 Research folder), curated
into pipeline/mobstats.json (2026-08-14). Main source page:
https://www.1838blackmetropolis.com/attackstats

Each sheet row is one documented act of self-defense/resistance during the
Philadelphia anti-Black mob attacks (1834 Flying Horses, 1835 Red Row, 1842
Lombard Street, 1849 Boyer/California House, surrounding St. Mary's incidents).
Every individually-named defender/complainant is linked to a person record:
- confident unique matches attach to the EXISTING person (census/winch/storymap/...)
- unmatched names are created as source='mobstats' people
- ambiguous same-name collisions are NOT auto-linked -- a mobstats person is
  created so the record is preserved, and the candidates are written to
  pipeline/mobstats_matches.md for Michiko to fold via merges.json (same review
  flow as the blog/StoryMap layers; nothing is force-merged).

Rows with no named individual (collective/unnamed defenders) load into the
`mobstats` table only -- they carry no person link and don't surface on cards.

Runs AFTER load_blogs and BEFORE apply_merges pass 2 / find_merge_candidates /
build_viewer. Idempotent: `mobstats` and `mobstats_people` are rebuilt each run;
matches re-resolve against canonical names+aliases every time.

Matching mirrors load_blogs.py exactly (exact identity-token set incl. aliases,
else unique surname+first-given).
"""
import sqlite3, json, re, unicodedata, os

HERE = os.path.dirname(os.path.abspath(__file__))
DB  = os.environ.get("BM_DB", os.path.join(HERE, "..", "black_metropolis.db"))
SRC = os.environ.get("MOBSTATS_SRC", os.path.join(HERE, "mobstats.json"))

HON = {"mr","mrs","miss","ms","dr","rev","reverend","bishop","gen","general","capt",
       "captain","col","colonel","sir","hon","prof","professor","elder","deacon",
       "father","mother","sister","brother","aunt","uncle","st","madame","mme",
       "quaker","wm"}  # 'wm' kept OUT of identity? no -- see toks(): Wm expands below
SUFFIX = {"jr","sr","ii","iii","esq"}
# common given-name abbreviations in the sheet -> expand so "Wm Rice" matches "William Rice"
ABBREV = {"wm": "william", "jas": "james", "jno": "john", "thos": "thomas",
          "chas": "charles", "geo": "george", "saml": "samuel", "benj": "benjamin",
          "jos": "joseph", "robt": "robert", "and'w": "andrew", "andw": "andrew"}
HON = HON - {"wm"}

def strip_accents(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()

def toks(name):
    n = strip_accents(name).lower()
    n = re.sub(r"[^a-z ]", " ", n)
    return [ABBREV.get(t, t) for t in n.split() if t]

def content_toks(name):
    return [t for t in toks(name) if len(t) > 1 and t not in HON]

def okey(name):
    return frozenset(content_toks(name))

def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z ]", " ", strip_accents(s).lower())).strip()

con = sqlite3.connect(DB)
con.execute("""CREATE TABLE IF NOT EXISTS mobstats(
    id TEXT PRIMARY KEY, attack TEXT, location TEXT, type TEXT, category TEXT,
    description TEXT, means TEXT, outcome TEXT, defenders TEXT, sources TEXT)""")
con.execute("""CREATE TABLE IF NOT EXISTS mobstats_people(
    person_id INT, entry_id TEXT)""")
con.execute("DELETE FROM mobstats")
con.execute("DELETE FROM mobstats_people")

# ---- match index over EXISTING (non-mobstats) people ---------------------------
exact = {}
surn_first = {}
def parse_forms(name):
    # suffixes (Jr/Sr/III) are kept for exact-set identity but must NOT be taken as the
    # surname in "First ... Last Jr." forms -- strip them when picking (surname, given).
    if "," in name:
        sur, _, rest = name.partition(",")
        st = [t for t in content_toks(sur) if t not in SUFFIX]
        rt = [t for t in content_toks(rest) if t not in SUFFIX]
        if st and rt: yield (st[0], rt[0])
        if st: yield (st[0], st[0])
    else:
        t = [x for x in content_toks(name) if x not in SUFFIX]
        if len(t) >= 2:
            yield (t[-1], t[0])

for pid, cn, src, al in con.execute(
        "SELECT id, canonical_name, source, aliases FROM people WHERE source IS NOT 'mobstats'"):
    forms = [cn] + ([a for a in al.split(" | ") if a.strip()] if al else [])
    for f in forms:
        k = okey(f)
        if len(k) >= 2:
            exact.setdefault(k, []).append((pid, cn))
        for sf in parse_forms(f):
            surn_first.setdefault(sf, []).append((pid, cn))

def dedup(cands):
    seen = set(); out = []
    for pid, nm in cands:
        if pid not in seen:
            seen.add(pid); out.append((pid, nm))
    return out

def match(name):
    k = okey(name)
    if len(k) >= 2:
        c = dedup(exact.get(k, []))
        if len(c) == 1: return ("one", c[0][0])
        if len(c) > 1:  return ("many", c)
    cand = []
    for sf in parse_forms(name):
        cand += surn_first.get(sf, [])
    c = dedup(cand)
    if len(c) == 1: return ("one", c[0][0])
    if len(c) > 1:  return ("many", c)
    return ("none", None)

def get_or_create_mob(name):
    r = con.execute("SELECT id FROM people WHERE canonical_name=? AND source='mobstats'",
                    (name,)).fetchone()
    if r: return r[0]
    cur = con.execute("INSERT INTO people(canonical_name, norm_name, source) VALUES(?,?, 'mobstats')",
                      (name, norm(name)))
    return cur.lastrowid

data = json.load(open(SRC, encoding="utf-8"))
uniq_names = sorted({n for e in data["entries"] for n in e["names"]})
resolved, ambiguous, created, linked = {}, [], [], []
for nm in uniq_names:
    kind, val = match(nm)
    if kind == "one":
        resolved[nm] = val; linked.append(nm)
    elif kind == "many":
        resolved[nm] = get_or_create_mob(nm); ambiguous.append((nm, val))
    else:
        resolved[nm] = get_or_create_mob(nm); created.append(nm)

n_link = 0
for e in data["entries"]:
    con.execute("INSERT OR REPLACE INTO mobstats(id,attack,location,type,category,description,means,outcome,defenders,sources) VALUES(?,?,?,?,?,?,?,?,?,?)",
                (e["id"], e["attack"], e.get("location",""), e.get("type",""), e.get("category",""),
                 e.get("description",""), e.get("means",""), e.get("outcome",""),
                 e.get("defenders",""), json.dumps(e.get("sources", []), ensure_ascii=False)))
    seen = set()
    for nm in e["names"]:
        pid = resolved.get(nm)
        if pid is None or pid in seen: continue
        seen.add(pid)
        con.execute("INSERT INTO mobstats_people(person_id, entry_id) VALUES(?,?)", (pid, e["id"]))
        n_link += 1
# drop orphaned mobstats people from earlier runs (names since removed from the sheet)
con.execute("DELETE FROM people WHERE source='mobstats' AND id NOT IN (SELECT person_id FROM mobstats_people)")
con.commit()

lines = ["# 1838 Mob Attack Statistics -- name matches to confirm", "",
         f"{len(data['entries'])} sheet rows loaded. Of {len(uniq_names)} unique named defenders: "
         f"{len(linked)} linked to existing people, {len(created)} created as new mobstats people, "
         f"{len(ambiguous)} held as ambiguous (NOT linked -- confirm below).", "",
         "## Ambiguous (same name as MORE THAN ONE existing record -- not auto-linked)",
         "Add a group to merges.json to attach the mob-stats record to the right person:", ""]
for nm, cands in ambiguous:
    lines.append(f"- **{nm}** (mobstats)  <->  " + ", ".join(f"{cn}#{pid}" for pid, cn in cands))
lines += ["", "## Linked automatically (unique match -- spot-check these)", ""]
for nm in linked:
    pid = resolved[nm]
    cn = con.execute("SELECT canonical_name, source FROM people WHERE id=?", (pid,)).fetchone()
    lines.append(f"- {nm} -> {cn[0]} [{cn[1]}] #{pid}")
lines += ["", "## Newly created as mobstats-only people", ""]
for nm in created:
    lines.append(f"- {nm}")
open(os.path.join(HERE, "mobstats_matches.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")

print(f"mobstats: {len(data['entries'])} rows, {n_link} person links | "
      f"{len(linked)} linked to existing, {len(created)} new mobstats people, "
      f"{len(ambiguous)} ambiguous held -> mobstats_matches.md")
