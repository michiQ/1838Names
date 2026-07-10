#!/usr/bin/env python3
"""Apply curated person merges from pipeline/merges.json. Idempotent.
Run AFTER import_census + match_names + load_extractions, BEFORE build_viewer."""
import sqlite3, json, re, unicodedata, os

DB = "/tmp/fj3/black_metropolis.db"
MERGES = "/sessions/funny-elegant-edison/mnt/Newspapers/1838 Names Database/pipeline/merges.json"

def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode()
    return re.sub(r"[^a-z ]", "", s.lower()).strip()

con = sqlite3.connect(DB)
try: con.execute("ALTER TABLE people ADD COLUMN aliases TEXT")
except sqlite3.OperationalError: pass

if not os.path.exists(MERGES):
    print("no merges.json"); raise SystemExit

groups = json.load(open(MERGES))
total_merged = 0
for g in groups:
    names = {norm(g["keep"])} | {norm(a) for a in g.get("aliases", [])}
    rows = [r for r in con.execute("SELECT id, canonical_name, source, winch_entry, aliases FROM people")
            if norm(r[1]) in names]
    if len(rows) < 2 and not any(norm(r[1]) == norm(g["keep"]) for r in rows):
        # nothing to merge but maybe rename a single alias row
        pass
    if not rows: continue
    # target: prefer winch, else lowest id
    rows.sort(key=lambda r: (0 if r[2]=="winch" else 1, r[0]))
    target = rows[0]; rest = rows[1:]
    tid = target[0]
    alias_set = set(filter(None, (target[4] or "").split(" | ")))
    entries = [target[3] or ""]
    for pid, cname, src, wentry, als in rest:
        for tbl, col in (("appearances","person_id"), ("winch_references","person_id"),
                          ("census_links","person_id"), ("newspaper_orgs","person_id")):
            try: con.execute(f"UPDATE {tbl} SET {col}=? WHERE {col}=?", (tid, pid))
            except sqlite3.OperationalError: pass
        if cname != g["keep"]: alias_set.add(cname)
        if als: alias_set.update(a for a in als.split(" | ") if a)
        if wentry: entries.append(wentry)
        con.execute("DELETE FROM people WHERE id=?", (pid,))
        total_merged += 1
    if target[1] != g["keep"]:
        alias_set.add(target[1])
    alias_set.discard(g["keep"])
    con.execute("UPDATE people SET canonical_name=?, norm_name=?, aliases=?, winch_entry=? WHERE id=?",
                (g["keep"], norm(g["keep"]), " | ".join(sorted(alias_set)) or None,
                 "\n".join(e for e in entries if e) or None, tid))
    # dedupe identical appearances created by multiple alias matches on the same span
    con.execute("""DELETE FROM appearances WHERE rowid NOT IN (
        SELECT MIN(rowid) FROM appearances GROUP BY person_id, role, context, issue_id, page)""")
con.commit()
print(f"merged {total_merged} duplicate records across {len(groups)} groups")
for g in groups:
    r = con.execute("SELECT id, canonical_name, aliases FROM people WHERE canonical_name=?", (g["keep"],)).fetchone()
    if r: print(" ", r[1], "| aka:", r[2])
