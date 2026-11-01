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
    if r.get("to_name"):
        row = con.execute("SELECT id FROM people WHERE canonical_name=? AND source=?", (r["to_name"], r["to_source"])).fetchone()
        if not row: print("  no target record for", r["to_name"]); continue
    else: row = [r["to_id"]] if r.get("to_id") else con.execute("SELECT id FROM people WHERE canonical_name=?", (r["new_name"],)).fetchone()
    new = row[0] if row else con.execute("INSERT INTO people(canonical_name, norm_name, source) VALUES(?,?,?)",
                                         (r["new_name"], norm(r["new_name"]), r["from_source"])).lastrowid
    q = f"UPDATE appearances SET person_id=? WHERE person_id IN ({','.join('?'*len(src))}) AND context LIKE ?"
    n = con.execute(q, (new, *src, r["context_prefix"] + "%")).rowcount
    print(f"  {r['from_name']} -> {r.get('new_name') or r.get('to_name') or r.get('to_id')} (id {new}): moved {n} appearance(s)")
con.commit()

# renames: fix a mis-parsed display name by id
for r in json.load(open(os.path.join(HERE, "split_appearances.json"))).get("renames", []):
    n = con.execute("UPDATE people SET canonical_name=?, norm_name=?, aliases=COALESCE(NULLIF(aliases,''),?) WHERE id=?",
                    (r["name"], norm(r["name"]), r.get("aliases"), r["id"])).rowcount
    if r.get("life_dates"):
        con.execute("UPDATE people SET life_dates=? WHERE id=?", (r["life_dates"], r["id"]))
    print(f"  rename id {r['id']} -> {r['name']}: {n} row")
# move_refs: move Winch notes filed under the wrong record
for r in json.load(open(os.path.join(HERE, "split_appearances.json"))).get("move_refs", []):
    n = 0
    for pre in r["note_prefixes"]:
        n += con.execute("UPDATE winch_references SET person_id=? WHERE person_id=? AND note LIKE ?",
                         (r["to_id"], r["from_id"], pre + "%")).rowcount
    print(f"  moved {n} Winch note(s) from id {r['from_id']} to id {r['to_id']}")
con.commit()
