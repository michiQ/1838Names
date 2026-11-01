#!/usr/bin/env python3
"""Move named appearances off a shared same-name record (see split_appearances.json).
Runs after load_extractions/split_swilliams and before apply_merges, so a later merge of the
shared record only carries the appearances that belong to that person."""
import json, os, re, sqlite3
DB = os.environ.get("BM_DB", "/tmp/black_metropolis.db")
HERE = os.path.dirname(os.path.abspath(__file__))
def norm(s): return re.sub(r"[^a-z ]", "", s.lower()).strip()
con = sqlite3.connect(DB)
for r in json.load(open(os.path.join(HERE, "split_appearances.json")))["rules"]:
    src = [x[0] for x in con.execute("SELECT id FROM people WHERE canonical_name=? AND source=?", (r["from_name"], r["from_source"]))]
    if not src: print("  no source record for", r["from_name"]); continue
    row = con.execute("SELECT id FROM people WHERE canonical_name=?", (r["new_name"],)).fetchone()
    new = row[0] if row else con.execute("INSERT INTO people(canonical_name, norm_name, source) VALUES(?,?,?)",
                                         (r["new_name"], norm(r["new_name"]), r["from_source"])).lastrowid
    q = f"UPDATE appearances SET person_id=? WHERE person_id IN ({','.join('?'*len(src))}) AND context LIKE ?"
    n = con.execute(q, (new, *src, r["context_prefix"] + "%")).rowcount
    print(f"  {r['from_name']} -> {r['new_name']} (id {new}): moved {n} appearance(s)")
con.commit()
