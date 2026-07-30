#!/usr/bin/env python3
"""Load the Institute for Colored Youth students/graduates named by Fanny Jackson
Coppin (Reminiscences of School Life, and Hints on Teaching, 1913 -- Part II,
"Some of the Graduates and Undergraduates of the I.C.Y.").

Every roster name is brought in as its own source='coppin' person -- NOTHING is
auto-linked to an existing record (Michiko's call, 2026-07-29). This avoids false
links across the generational gap between the 1838-era core data and this later ICY
roster (e.g. an 1890s ICY "Mary Smith" is not the 1838-census "Mary Smith"). Genuine
same-person matches -- including obvious ones like Octavius V. Catto -- are surfaced
by find_merge_candidates and confirmed by Michiko through the normal merge-review
workflow (merges.json), keeping a human in the loop for every identity decision.

build_viewer reads the coppin_students table, attaches the source to each person,
and makes every one a member of an "Institute for Colored Youth" organization node.

Idempotent: coppin_students is rebuilt each run, and new people are reused via
get_or_create(name, 'coppin'). Source file: pipeline/coppin_students.json.
"""
import sqlite3, json, re, unicodedata, os

HERE = os.path.dirname(os.path.abspath(__file__))
DB  = os.environ.get("BM_DB", os.path.join(HERE, "..", "black_metropolis.db"))
SRC = os.environ.get("COPPIN_SRC", os.path.join(HERE, "coppin_students.json"))

def norm(name):
    n = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z ]", " ", n.lower())).strip()

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
con.execute("CREATE TABLE IF NOT EXISTS coppin_students(person_id INT, note TEXT)")
con.execute("DELETE FROM coppin_students")

def get_or_create_coppin(name):
    r = con.execute("SELECT id FROM people WHERE canonical_name=? AND source='coppin'", (name,)).fetchone()
    if r:
        return r["id"]
    cur = con.execute("INSERT INTO people(canonical_name, norm_name, source) VALUES(?,?, 'coppin')",
                      (name, norm(name)))
    return cur.lastrowid

data = json.load(open(SRC, encoding="utf-8"))
for e in data:
    name = e["name"]
    note = e.get("note", "") or ""
    pid = get_or_create_coppin(name)   # never auto-link; merge review confirms identities
    con.execute("INSERT INTO coppin_students(person_id, note) VALUES(?,?)", (pid, note))

con.commit()
n_people = con.execute("SELECT COUNT(DISTINCT person_id) FROM coppin_students").fetchone()[0]

# Dedicated review aid: for each ICY roster name, list existing NON-coppin people who
# share the exact normalized name (candidate same-person matches for Michiko to confirm
# via merges.json). This is a COMPLETE list (unlike merge_candidates.md's top-N cut).
idx = {}
for pid, cname, source in con.execute("SELECT id, canonical_name, source FROM people WHERE source IS NOT 'coppin'"):
    idx.setdefault(norm(cname), []).append((cname, source))
matches = []
for e in data:
    cands = idx.get(norm(e["name"]), [])
    if cands:
        matches.append((e["name"], cands))
lines = ["# Institute for Colored Youth (Coppin) — name matches to confirm",
         "",
         "Each ICY roster name below shares an exact name with someone already in the",
         "database. NONE are auto-linked. To confirm a same-person match, add a group to",
         "`merges.json` (keep the existing record; alias the ICY one), e.g.:",
         '`{\"keep\": \"Catto, Octavius V.\", \"aliases\": [{\"name\": \"Catto, Octavius V.\", \"source\": \"coppin\"}]}`',
         "", f"{len(matches)} of {len(data)} ICY names have a same-name record:", ""]
for nm, cands in matches:
    tags = ", ".join(f"{cn} ({sr})" for cn, sr in cands)
    lines.append(f"- **{nm}** (coppin)  ↔  {tags}")
OUT_MD = os.path.join(HERE, "coppin_matches.md")
open(OUT_MD, "w", encoding="utf-8").write("\n".join(lines) + "\n")

print(f"coppin_students: {len(data)} roster names -> {n_people} coppin people "
      f"(no auto-linking; matches surfaced for review)")
print(f"coppin_matches.md: {len(matches)} ICY names share a name with an existing record (review to merge)")
